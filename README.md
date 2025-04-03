# Pynfish v0.2.0

**Author:** Jimmy Luong

## Overview
Pynfish is a Python-based chess engine that achieves an approximate Elo rating of **1500**. This project has been relaunched because my Rust-based engine now includes all the features I wanted to integrate.

## Differences from Version 1.0
- Completely redesigned, as I was not satisfied with the previous structure – now it's easier to create new versions.
- It now uses Minimax and Alpha-Beta pruning for efficient search.
- Integrates Stockfish's old NNUE (2020 version), combining Stockfish's NNUE with the classic search method.
- stronger, faster, better

## Update
- Uses self made libary for NNUE-Probe. You have 2 options:
  1. compile it by yourself
  2. ```bash
     pip install nnue_parser
     ```

## Performance Comparison
| Engine          | Winrate % | Wins     | Looses   | Draws    |
|-----------------|-----------|----------|----------|----------|
| Pynfish 1       | 25%       | 3        | 9        | 0        |
| Pynfish 2 Beta  | 50%       | 6        | 6        | 0        |
| Pynfish 2 Alpha | 75%       | 9        | 3        | 0        |

- Each engine played 3 rounds (3 times Black and 3 times White) against each other engine.
[Download PGN file of a small tournament between Pynfish 1 vs Pynfish 2 Alpha/Beta](https://drive.google.com/file/d/1Sq6ptOuKYYrNAw8Y0393LpT-81ufu6aR/view?usp=sharing)


## Features
- Playable against Pynfish using:
  - `uci.py`: Can be compiled and used in chess arenas such as Lucas Chess or my self-developed one.

## Getting Started
1. Clone the repository:
   ```bash
   git clone https://github.com/github-jimjim/Pynfish.git
   cd pynfish
   ```
2. Compile `main.py` to use the engine in external chess arenas.
   ```bash
   pyinstaller --onefile --hidden-import=chess_engine --name=pynfish uci.py
   ```
3. IMPORTANT: Do not set a maximum thinking time for the engine or a maximum depth. It will automatically search depth 4 with nnue which can take 3-15 seconds per move.

## License
GPL-3.0 License

## External Links
- [Example Arena](https://github.com/github-jimjim/Arenmy)
---
Feel free to open issues or contribute improvements to Pynfish!
