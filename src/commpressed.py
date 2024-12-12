import sys
import chess
import argparse
from typing import Dict, List, Any



def talk():
    board = chess.Board()
    depth = get_depth()

    while True:
        msg = input()
        command(depth, board, msg)


def command(depth: int, board: chess.Board, msg: str):
    msg = msg.strip()
    tokens = msg.split(" ")
    while "" in tokens:
        tokens.remove("")

    if msg == "quit":
        sys.exit()

    if msg == "uci":
        print("id name Pynfish")
        print("id author Jimmy Luong")
        print("uciok")
        return

    if msg == "isready":
        print("readyok")
        return

    if msg == "ucinewgame":
        return

    if msg.startswith("position"):
        if len(tokens) < 2:
            return

        if tokens[1] == "startpos":
            board.reset()
            moves_start = 2
        elif tokens[1] == "fen":
            fen = " ".join(tokens[2:8])
            board.set_fen(fen)
            moves_start = 8
        else:
            return

        if len(tokens) <= moves_start or tokens[moves_start] != "moves":
            return

        for move in tokens[(moves_start+1):]:
            board.push_uci(move)

    if msg == "d":
        print(board)
        print(board.fen())

    if msg[0:2] == "go":
        _move = next_move(depth, board)
        print(f"bestmove {_move}")
        return


def get_depth() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", default=3, help="provide an integer (default: 3)")
    args = parser.parse_args()
    return max([1, int(args.depth)])


piece_value = {
    chess.PAWN: 100,
    chess.ROOK: 500,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.QUEEN: 900,
    chess.KING: 20000
}

pawnEvalWhite = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, -20, -20, 10, 10,  5,
    5, -5, -10,  0,  0, -10, -5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0
]
pawnEvalBlack = list(reversed(pawnEvalWhite))

knightEval = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50
]

bishopEvalWhite = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20
]
bishopEvalBlack = list(reversed(bishopEvalWhite))

rookEvalWhite = [
    0, 0, 0, 5, 5, 0, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0
]
rookEvalBlack = list(reversed(rookEvalWhite))

queenEval = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]

kingEvalWhite = [
    20, 30, 10, 0, 0, 10, 30, 20,
    20, 20, 0, 0, 0, 0, 20, 20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30
]
kingEvalBlack = list(reversed(kingEvalWhite))

kingEvalEndGameWhite = [
    50, -30, -30, -30, -30, -30, -30, -50,
    -30, -30,  0,  0,  0,  0, -30, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -20, -10,  0,  0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50
]
kingEvalEndGameBlack = list(reversed(kingEvalEndGameWhite))


def move_value(board: chess.Board, move: chess.Move, endgame: bool) -> float:
    if move.promotion is not None:
        return -float("inf") if board.turn == chess.BLACK else float("inf")

    _piece = board.piece_at(move.from_square)
    if _piece:
        _from_value = evaluate_piece(_piece, move.from_square, endgame)
        _to_value = evaluate_piece(_piece, move.to_square, endgame)
        position_change = _to_value - _from_value
    else:
        raise Exception(f"A piece was expected at {move.from_square}")

    capture_value = 0.0
    if board.is_capture(move):
        capture_value = evaluate_capture(board, move)

    current_move_value = capture_value + position_change
    if board.turn == chess.BLACK:
        current_move_value = -current_move_value

    return current_move_value


def evaluate_capture(board: chess.Board, move: chess.Move) -> float:
    if board.is_en_passant(move):
        return piece_value[chess.PAWN]
    _to = board.piece_at(move.to_square)
    _from = board.piece_at(move.from_square)
    if _to is None or _from is None:
        raise Exception(
            f"Pieces were expected at _both_ {move.to_square} and {move.from_square}"
        )
    return piece_value[_to.piece_type] - piece_value[_from.piece_type]


def evaluate_piece(piece: chess.Piece, square: chess.Square, end_game: bool) -> int:
    piece_type = piece.piece_type
    mapping = []
    if piece_type == chess.PAWN:
        mapping = pawnEvalWhite if piece.color == chess.WHITE else pawnEvalBlack
    if piece_type == chess.KNIGHT:
        mapping = knightEval
    if piece_type == chess.BISHOP:
        mapping = bishopEvalWhite if piece.color == chess.WHITE else bishopEvalBlack
    if piece_type == chess.ROOK:
        mapping = rookEvalWhite if piece.color == chess.WHITE else rookEvalBlack
    if piece_type == chess.QUEEN:
        mapping = queenEval
    if piece_type == chess.KING:
        if end_game:
            mapping = (
                kingEvalEndGameWhite
                if piece.color == chess.WHITE
                else kingEvalEndGameBlack
            )
        else:
            mapping = kingEvalWhite if piece.color == chess.WHITE else kingEvalBlack

    return mapping[square]


def evaluate_board(board: chess.Board) -> float:
    total = 0
    end_game = check_end_game(board)

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue

        value = piece_value[piece.piece_type] + evaluate_piece(piece, square, end_game)
        total += value if piece.color == chess.WHITE else -value

    return total


def check_end_game(board: chess.Board) -> bool:
    queens = 0
    minors = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.QUEEN:
            queens += 1
        if piece and (
            piece.piece_type == chess.BISHOP or piece.piece_type == chess.KNIGHT
        ):
            minors += 1

    if queens == 0 or (queens == 2 and minors <= 1):
        return True

    return False



debug_info: Dict[str, Any] = {}


MATE_SCORE     = 1000000000
MATE_THRESHOLD =  999000000


def next_move(depth: int, board: chess.Board, debug=True) -> chess.Move:
    """
    What is the next best move?
    """
    debug_info.clear()
    debug_info["nodes"] = 0
    t0 = time.time()

    move = minimax_root(depth, board)

    debug_info["time"] = time.time() - t0
    if debug == True:
        print(f"info {debug_info}")
    return move


def get_ordered_moves(board: chess.Board) -> List[chess.Move]:
    end_game = check_end_game(board)

    def orderer(move):
        return move_value(board, move, end_game)

    in_order = sorted(
        board.legal_moves, key=orderer, reverse=(board.turn == chess.WHITE)
    )
    return list(in_order)


def minimax_root(depth: int, board: chess.Board) -> chess.Move:
    maximize = board.turn == chess.WHITE
    best_move = -float("inf")
    if not maximize:
        best_move = float("inf")

    moves = get_ordered_moves(board)
    best_move_found = moves[0]

    for move in moves:
        board.push(move)
        if board.can_claim_draw():
            value = 0.0
        else:
            value = minimax(depth - 1, board, -float("inf"), float("inf"), not maximize)
        board.pop()
        if maximize and value >= best_move:
            best_move = value
            best_move_found = move
        elif not maximize and value <= best_move:
            best_move = value
            best_move_found = move

    return best_move_found


def minimax(
    depth: int,
    board: chess.Board,
    alpha: float,
    beta: float,
    is_maximising_player: bool,
) -> float:
    debug_info["nodes"] += 1

    if board.is_checkmate():
        return -MATE_SCORE if is_maximising_player else MATE_SCORE
    elif board.is_game_over():
        return 0

    if depth == 0:
        return evaluate_board(board)

    if is_maximising_player:
        best_move = -float("inf")
        moves = get_ordered_moves(board)
        for move in moves:
            board.push(move)
            curr_move = minimax(depth - 1, board, alpha, beta, not is_maximising_player)
            if curr_move > MATE_THRESHOLD:
                curr_move -= 1
            elif curr_move < -MATE_THRESHOLD:
                curr_move += 1
            best_move = max(
                best_move,
                curr_move,
            )
            board.pop()
            alpha = max(alpha, best_move)
            if beta <= alpha:
                return best_move
        return best_move
    else:
        best_move = float("inf")
        moves = get_ordered_moves(board)
        for move in moves:
            board.push(move)
            curr_move = minimax(depth - 1, board, alpha, beta, not is_maximising_player)
            if curr_move > MATE_THRESHOLD:
                curr_move -= 1
            elif curr_move < -MATE_THRESHOLD:
                curr_move += 1
            best_move = min(
                best_move,
                curr_move,
            )
            board.pop()
            beta = min(beta, best_move)
            if beta <= alpha:
                return best_move
        return best_move



talk()
