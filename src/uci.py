import chess
from chess_engine import Engine
import sys
import threading
import time

class UCIEngine:
    def __init__(self):
        self.engine = Engine("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.is_running = False
        self.stop_event = threading.Event()
        self.current_best_move = None

    def uci(self):
        print("id name Pynfish 2 DEV")
        print("id author Jimmy Luong")
        print("uciok")

    def isready(self):
        print("readyok")

    def position(self, command):
        parts = command.split(" ", 1)
        if parts[0] == "startpos":
            self.engine.board.set_fen(chess.STARTING_BOARD_FEN)
            if len(parts) > 1 and parts[1].startswith("moves"):
                self._apply_moves(parts[1][6:])
        elif parts[0] == "fen":
            fen_and_moves = parts[1].split(" moves ", 1)
            self.engine.board.set_fen(fen_and_moves[0])
            if len(fen_and_moves) > 1:
                self._apply_moves(fen_and_moves[1])

    def _apply_moves(self, moves):
        for move in moves.split():
            self.engine.board.push_uci(move)

    def go(self, command):
        depth = 4
        tokens = command.split()
        if "depth" in tokens:
            depth = int(tokens[tokens.index("depth") + 1])

        self.stop_event.clear()
        thread = threading.Thread(target=self._search_best_move, args=(depth,))
        thread.start()
        thread.join()
        
        if self.current_best_move:
            print(f"bestmove {self.current_best_move}")

    def _search_best_move(self, depth):
        self.current_best_move = self.engine.calculate_ab(depth)

    def stop(self):
        self.stop_event.set()

    def quit(self):
        self.is_running = False

    def main_loop(self):
        self.is_running = True
        while self.is_running:
            try:
                command = input().strip()
                if command == "uci":
                    self.uci()
                elif command == "isready":
                    self.isready()
                elif command.startswith("position"):
                    self.position(command[9:])
                elif command.startswith("go"):
                    self.go(command[3:])
                elif command == "stop":
                    self.stop()
                elif command == "quit":
                    self.quit()
            except EOFError:
                break

if __name__ == "__main__":
    uci_engine = UCIEngine()
    uci_engine.main_loop()
