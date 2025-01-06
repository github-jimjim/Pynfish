
# Pynfish v0.2.0 BETA

**Author:** Jimmy Luong

## Overview
Pynfish is a Python-based chess engine that achieves an approximate Elo rating of **1500**. This project has been relaunched because my Rust-based engine now includes all the features I wanted to integrate.

## Differences from Version 1.0
- Completely redesigned, as I was not satisfied with the previous structure – now it's easier to create new versions.
- It now uses Minimax and Alpha-Beta pruning for efficient search.
- Integrates Stockfish's old NNUE (2020 version), combining Stockfish's NNUE with the classic search method.

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

## Notes
Pynfish is currently in Beta version, and the Alpha version will be released in a few days after this version has undergone some testing.

## Acknowledgements
A big thanks to [https://github.com/dshawul/nnue-probe](https://github.com/dshawul/nnue-probe) for providing resources that greatly helped me in developing this engine. Since I couldn't find another compatible NNUE version, I had to use the only available one, even though it is quite old. If anyone could develop or find a newer NNUE version for Rust or Python, I would greatly appreciate the help!

## License
GPL-3.0 License

## External Links
- [Example Arena](https://github.com/github-jimjim/Arenmy)
- [Demonstration games against JOMFISH 10 DEV (3200) with time pressure of 0.1 seconds per move](https://drive.google.com/file/d/1lfz2S88zeSJaAk8G1VvVkqoOQZck5dtf/view?usp=drive_link)

---
Feel free to open issues or contribute improvements to Pynfish!
