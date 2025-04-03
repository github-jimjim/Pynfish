use byteorder::{LittleEndian, ReadBytesExt};
use chess::{BitBoard, Board, Color, Piece, Square};
use once_cell::sync::OnceCell;
use pyo3::prelude::*;
use std::fs::File;
use std::io::{BufReader, Read, Seek, SeekFrom};
const FEATURE_TRANSFORMER_HALF_DIMENSIONS: usize = 256;
const SQUARE_NB: usize = 64;
const FT_INPUT_DIM: usize = 41024;
const HL1_INPUT_DIM: usize = 512;
const HL1_OUTPUT_DIM: usize = 32;
const HL2_OUTPUT_DIM: usize = 32;
struct Model {
    ft_weights: Vec<i16>,
    ft_biases: Vec<i16>,
    hl1_weights: Vec<i8>,
    hl1_biases: Vec<i32>,
    hl2_weights: Vec<i8>,
    hl2_biases: Vec<i32>,
    out_weights: Vec<i8>,
    out_bias: i32,
}
static MODEL: OnceCell<Model> = OnceCell::new();
#[pyfunction]
fn init_nnue(nnue_path: &str) -> PyResult<()> {
    let file =
        File::open(nnue_path).map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let mut reader = BufReader::new(file);
    let version = reader
        .read_u32::<LittleEndian>()
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let hash_value = reader
        .read_u32::<LittleEndian>()
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let size = reader
        .read_u32::<LittleEndian>()
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))? as usize;
    let mut arch_bytes = vec![0u8; size];
    reader
        .read_exact(&mut arch_bytes)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let arch = String::from_utf8_lossy(&arch_bytes);
    println!("Version: {}", version);
    println!("Hash: {}", hash_value);
    let ft_header = reader
        .read_u32::<LittleEndian>()
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let associated_halfkp_king: u32 = 1;
    let output_dimensions = 2 * FEATURE_TRANSFORMER_HALF_DIMENSIONS as u32;
    let expected_hash = (0x5D69D5B9_u32 ^ associated_halfkp_king) ^ output_dimensions;
    if ft_header != expected_hash {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Header passt nicht zum erwarteten Hash!",
        ));
    }
    let mut ft_biases = vec![0i16; FEATURE_TRANSFORMER_HALF_DIMENSIONS];
    reader
        .read_i16_into::<LittleEndian>(&mut ft_biases)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let ft_weights_count = FEATURE_TRANSFORMER_HALF_DIMENSIONS * FT_INPUT_DIM;
    let mut ft_weights = vec![0i16; ft_weights_count];
    reader
        .read_i16_into::<LittleEndian>(&mut ft_weights)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let _header = reader
        .read_u32::<LittleEndian>()
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let mut hl1_biases = vec![0i32; HL1_OUTPUT_DIM];
    reader
        .read_i32_into::<LittleEndian>(&mut hl1_biases)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let hl1_weights_count = HL1_INPUT_DIM * HL1_OUTPUT_DIM;
    let mut hl1_weights = vec![0i8; hl1_weights_count];
    reader
        .read_exact(unsafe {
            std::slice::from_raw_parts_mut(
                hl1_weights.as_mut_ptr() as *mut u8,
                hl1_weights_count * std::mem::size_of::<i8>(),
            )
        })
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let mut hl2_biases = vec![0i32; HL2_OUTPUT_DIM];
    reader
        .read_i32_into::<LittleEndian>(&mut hl2_biases)
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let hl2_weights_count = HL2_OUTPUT_DIM * HL2_OUTPUT_DIM;
    let mut hl2_weights = vec![0i8; hl2_weights_count];
    reader
        .read_exact(unsafe {
            std::slice::from_raw_parts_mut(
                hl2_weights.as_mut_ptr() as *mut u8,
                hl2_weights_count * std::mem::size_of::<i8>(),
            )
        })
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let out_bias = reader
        .read_i32::<LittleEndian>()
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let mut out_weights = vec![0i8; HL2_OUTPUT_DIM];
    reader
        .read_exact(unsafe {
            std::slice::from_raw_parts_mut(
                out_weights.as_mut_ptr() as *mut u8,
                HL2_OUTPUT_DIM * std::mem::size_of::<i8>(),
            )
        })
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let current_pos = reader
        .seek(SeekFrom::Current(0))
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?;
    let end_pos = reader
        .get_ref()
        .metadata()
        .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?
        .len();
    if end_pos - current_pos != 0 {
        return Err(pyo3::exceptions::PyValueError::new_err(
            "Es wurden nicht alle Parameter gelesen!",
        ));
    }
    let model = Model {
        ft_weights,
        ft_biases,
        hl1_weights,
        hl1_biases,
        hl2_weights,
        hl2_biases,
        out_weights,
        out_bias,
    };
    MODEL
        .set(model)
        .map_err(|_| pyo3::exceptions::PyRuntimeError::new_err("Modell bereits initialisiert!"))?;
    Ok(())
}
#[pyfunction]
fn eval_nnue(fen: &str) -> PyResult<f32> {
    let model = MODEL.get().ok_or_else(|| {
        pyo3::exceptions::PyValueError::new_err(
            "Modell nicht initialisiert! Bitte zuerst init_nnue(nnue_path) aufrufen.",
        )
    })?;
    let board = Board::from_fen(fen.to_string())
        .ok_or_else(|| pyo3::exceptions::PyValueError::new_err("Ungültiger FEN-String"))?;
    let features_current = get_halfkp_indices(&board, board.side_to_move() == Color::White);
    let features_opponent = get_halfkp_indices(&board, board.side_to_move() == Color::Black);
    let ft_current = feature_transformer(&features_current, &model.ft_weights, &model.ft_biases);
    let ft_opponent = feature_transformer(&features_opponent, &model.ft_weights, &model.ft_biases);
    let mut concat_features = Vec::with_capacity(HL1_INPUT_DIM);
    concat_features.extend_from_slice(&ft_current);
    concat_features.extend_from_slice(&ft_opponent);
    let hl1_out = dense_layer(
        &concat_features,
        &model.hl1_weights,
        &model.hl1_biases,
        HL1_INPUT_DIM,
        HL1_OUTPUT_DIM,
    );
    let hl2_out = dense_layer(
        &hl1_out,
        &model.hl2_weights,
        &model.hl2_biases,
        HL2_OUTPUT_DIM,
        HL2_OUTPUT_DIM,
    );
    let out_value = dense_output(&hl2_out, &model.out_weights, model.out_bias);
    let centipawn = nn_value_to_centipawn(out_value);
    Ok(centipawn)
}
fn feature_transformer(indices: &[usize], ft_weights: &[i16], ft_biases: &[i16]) -> Vec<i32> {
    let mut out = vec![0i32; FEATURE_TRANSFORMER_HALF_DIMENSIONS];
    for i in 0..FEATURE_TRANSFORMER_HALF_DIMENSIONS {
        out[i] = ft_biases[i] as i32;
    }
    for &idx in indices {
        let base = idx * FEATURE_TRANSFORMER_HALF_DIMENSIONS;
        for i in 0..FEATURE_TRANSFORMER_HALF_DIMENSIONS {
            out[i] += ft_weights[base + i] as i32;
        }
    }
    for v in &mut out {
        if *v < 0 {
            *v = 0;
        }
        if *v > 127 {
            *v = 127;
        }
    }
    out
}
fn dense_layer(
    input: &[i32],
    weights: &[i8],
    biases: &[i32],
    in_dim: usize,
    out_dim: usize,
) -> Vec<i32> {
    let mut out = vec![0i32; out_dim];
    for j in 0..out_dim {
        let mut sum = biases[j];
        for i in 0..in_dim {
            sum += input[i] * (weights[i + j * in_dim] as i32);
        }
        out[j] = nnue_relu(sum);
    }
    out
}
fn dense_output(input: &[i32], weights: &[i8], bias: i32) -> i32 {
    let mut sum = bias;
    for i in 0..input.len() {
        sum += input[i] * (weights[i] as i32);
    }
    sum
}
fn nnue_relu(x: i32) -> i32 {
    let y = py_floor_div(x, 64);
    if y < 0 {
        0
    } else if y > 127 {
        127
    } else {
        y
    }
}
fn py_floor_div(a: i32, b: i32) -> i32 {
    (a as f64 / b as f64).floor() as i32
}
fn nn_value_to_centipawn(nn_value: i32) -> f32 {
    let v = py_floor_div(nn_value, 8);
    let v = py_floor_div(v * 100, 208);
    (v as f32) / 100.0
}
fn make_halfkp_index(
    is_white: bool,
    king_oriented: usize,
    sq: usize,
    piece: Piece,
    piece_color: Color,
) -> usize {
    orient(is_white, sq)
        + piece_square_from_piece(piece, piece_color, is_white)
        + 641 * king_oriented
}
fn orient(is_white: bool, sq: usize) -> usize {
    if is_white {
        sq
    } else {
        63 - sq
    }
}
fn piece_square_from_piece(piece: Piece, piece_color: Color, is_white: bool) -> usize {
    let use_white = (piece_color == Color::White) == is_white;
    match (piece, use_white) {
        (Piece::Pawn, true) => 1,
        (Piece::Knight, true) => 2 * SQUARE_NB + 1,
        (Piece::Bishop, true) => 4 * SQUARE_NB + 1,
        (Piece::Rook, true) => 6 * SQUARE_NB + 1,
        (Piece::Queen, true) => 8 * SQUARE_NB + 1,
        (Piece::King, true) => 10 * SQUARE_NB + 1,
        (Piece::Pawn, false) => 1 * SQUARE_NB + 1,
        (Piece::Knight, false) => 3 * SQUARE_NB + 1,
        (Piece::Bishop, false) => 5 * SQUARE_NB + 1,
        (Piece::Rook, false) => 7 * SQUARE_NB + 1,
        (Piece::Queen, false) => 9 * SQUARE_NB + 1,
        (Piece::King, false) => 11 * SQUARE_NB + 1,
    }
}
fn get_halfkp_indices(board: &Board, is_white_pov: bool) -> Vec<usize> {
    let mut indices = Vec::new();
    let king_sq = board.king_square(if is_white_pov {
        Color::White
    } else {
        Color::Black
    });
    let king_oriented = orient(is_white_pov, king_sq.to_index());
    for i in 0..64 {
        let sq = unsafe { Square::new(i as u8) };
        if let Some(piece) = board.piece_on(sq) {
            if piece == Piece::King {
                continue;
            }
            let piece_color = if board.color_combined(Color::White) & BitBoard::from_square(sq)
                != BitBoard::new(0)
            {
                Color::White
            } else {
                Color::Black
            };
            let idx = make_halfkp_index(
                is_white_pov,
                king_oriented,
                sq.to_index(),
                piece,
                piece_color,
            );
            indices.push(idx);
        }
    }
    indices
}
#[pymodule]
fn pynnue(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(init_nnue, m)?)?;
    m.add_function(wrap_pyfunction!(eval_nnue, m)?)?;
    Ok(())
}
