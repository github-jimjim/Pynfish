import chess
import random
import signal
import time
import os
import nnue-probe

class Engine:
    
    def __init__(self, fen):
        self.board = chess.Board()
        self.MAX_DEPTH = 60
        self.piece_values = {
            1:100,
            2:310,
            3:300,
            4:500,
            5:900,
            6:99999
        }
        self.square_table = square_table = {
            1: [
                0, 0, 0, 0, 0, 0, 0, 0,
                50, 50, 50, 50, 50, 50, 50, 50,
                10, 10, 20, 30, 30, 20, 10, 10,
                5, 5, 10, 25, 25, 10, 5, 5,
                0, 0, 0, 20, 20, 0, 0, 0,
                5, -5, -10, 0, 0, -10, -5, 5,
                5, 10, 10, -20, -20, 10, 10, 5,
                0, 0, 0, 0, 0, 0, 0, 0
            ],
            2: [
                -50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20, 0, 0, 0, 0, -20, -40,
                -30, 0, 10, 15, 15, 10, 0, -30,
                -30, 5, 15, 20, 20, 15, 5, -30,
                -30, 0, 15, 20, 20, 15, 0, -30,
                -30, 5, 10, 15, 15, 10, 5, -30,
                -40, -20, 0, 5, 5, 0, -20, -40,
                -50, -40, -30, -30, -30, -30, -40, -50,
            ],
            3: [
                -20, -10, -10, -10, -10, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 0, 5, 10, 10, 5, 0, -10,
                -10, 5, 5, 10, 10, 5, 5, -10,
                -10, 0, 10, 10, 10, 10, 0, -10,
                -10, 10, 10, 10, 10, 10, 10, -10,
                -10, 5, 0, 0, 0, 0, 5, -10,
                -20, -10, -10, -10, -10, -10, -10, -20,
            ],
            4: [
                0, 0, 0, 0, 0, 0, 0, 0,
                5, 10, 10, 10, 10, 10, 10, 5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                0, 0, 0, 5, 5, 0, 0, 0
            ],
            5: [
                -20, -10, -10, -5, -5, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 0, 5, 5, 5, 5, 0, -10,
                -5, 0, 5, 5, 5, 5, 0, -5,
                0, 0, 5, 5, 5, 5, 0, -5,
                -10, 5, 5, 5, 5, 5, 0, -10,
                -10, 0, 5, 0, 0, 0, 0, -10,
                -20, -10, -10, -5, -5, -10, -10, -20
            ],
            6: [
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -20, -30, -30, -40, -40, -30, -30, -20,
                -10, -20, -20, -20, -20, -20, -20, -10,
                20, 20, 0, 0, 0, 0, 20, 20,
                20, 30, 10, 0, 0, 10, 30, 20
            ]
        }
        self.board.set_fen(fen)
        self.leaves_reached = 0
        
        nnue_parser.init_nnue_py("final.jnn")
        

    def random_response(self):
        response = random.choice(list(self.board.legal_moves))
        return str(response)


    def material_eval(self):
        score = 0
        for i in range(1, 7):
            score += len(self.board.pieces(i, chess.WHITE)) * self.piece_values[i]
            score -= len(self.board.pieces(i, chess.BLACK)) * self.piece_values[i]

        return score


    def position_eval(self):
        score = 0
        for i in range(1, 7):
            w_squares = self.board.pieces(i, chess.WHITE)
            score += len(w_squares) * self.piece_values[i]
            for square in w_squares:
                score += self.square_table[i][-square]

            b_squares = self.board.pieces(i, chess.BLACK)
            score -= len(b_squares) * self.piece_values[i]
            for square in b_squares:
                score -= self.square_table[i][square]

        fen = self.board.fen().encode()
        nnue_score = nnue_parser.eval_nnue_py(fen)
        
        # because the NNUE is very weak with black
        if self.board.turn == chess.WHITE:
            score = score * 0.25 + nnue_score * 0.75
        else:
            score = score * 0.95 + nnue_score * 0.05

        return score






    def minimax(self, depth, move, maximiser):
        if depth == 0:
            return move, self.position_eval()

        if maximiser:
            best_move = None
            best_score = -9999

            moves = list(self.board.legal_moves)

            for move in moves:
                self.leaves_reached += 1
                self.board.push(move)
                new_move, new_score = self.minimax(depth - 1, move, False)
                if new_score > best_score:
                    best_score, best_move = new_score, move
                self.board.pop()

            return best_move, best_score

        if not maximiser:
            best_move = None
            best_score = 9999

            moves = list(self.board.legal_moves)

            for move in moves:
                self.leaves_reached += 1
                self.board.push(move)
                new_move, new_score = self.minimax(depth - 1, move, True)
                if new_score < best_score:
                    best_score, best_move = new_score, move
                self.board.pop()

            return best_move, best_score


    def alpha_beta(self, depth_neg, depth_pos, move, alpha, beta, prev_moves, maximiser):

        move_sequence = []

        if depth_neg == 0:
            move_sequence.append(move)
            return move_sequence, self.position_eval()


        moves = list(self.board.legal_moves)
        
        if not moves:
            if self.board.is_checkmate():
                if self.board.result() == "1-0":
                    move_sequence.append(move)
                    return move_sequence, 1000000
                elif self.board.result() == "0-1":
                    move_sequence.append(move)
                    return move_sequence, -1000000
            else:
                move_sequence.append(move)
                return move_sequence, 0

        best_move = None
        best_score = -10000001 if maximiser else 10000001

        if prev_moves and len(prev_moves) >= depth_neg:
            if depth_neg == 4 and not self.board.turn:
                print(prev_moves[depth_neg - 1])
            if prev_moves[depth_neg - 1] in moves:
                moves.insert(0, prev_moves[depth_neg - 1])


        if maximiser:
            for move in moves:
                self.leaves_reached += 1

                self.board.push(move)
                new_sequence, new_score = self.alpha_beta(depth_neg - 1, depth_pos + 1, move, alpha, beta, prev_moves, False)
                self.board.pop()

                if new_score > best_score:
                    move_sequence = new_sequence
                    best_score, best_move = new_score, move
                if new_score >= beta:
                    move_sequence.append(best_move)
                    return move_sequence, best_score
                if new_score > alpha:
                    alpha = new_score
            move_sequence.append(best_move)
            return move_sequence, best_score

        if not maximiser:
            for move in moves:
                self.leaves_reached += 1

                self.board.push(move)
                new_sequence, new_score = self.alpha_beta(depth_neg - 1, depth_pos + 1, move, alpha, beta, prev_moves, True)
                self.board.pop()

                if new_score < best_score:
                    move_sequence = new_sequence
                    best_score, best_move = new_score, move

                if new_score <= alpha:
                    move_sequence.append(best_move)
                    return move_sequence, best_score

                if new_score < beta:
                    beta = new_score

            move_sequence.append(best_move)
            return move_sequence, best_score

    def calculate_minimax(self, depth):
        maximiser = self.board.turn

        best_move, best_score = self.minimax(depth, None, maximiser)

        return str(best_move)


    def calculate_ab(self, depth):
        maximiser = self.board.turn

        move_sequence, best_score = self.alpha_beta(depth, 0, None, -10000001, 10000001, None, maximiser)
        for i in range(1, len(move_sequence)):
            print("move", move_sequence[-i])
        return str(move_sequence[-1])


    def total_leaves(self):
        leaves = self.leaves_reached
        self.leaves_reached = 0
        return leaves


    def order_moves(self):
        moves = list(self.board.legal_moves)
        scores = []
        for move in moves:
            self.board.push(move)
            scores.append(self.material_eval())
            self.board.pop()
        sorted_indexes = sorted(range(len(scores)), key=lambda i: scores[i], reverse=False)
        return [moves[i] for i in sorted_indexes]


    def iterative_deepening(self, depth):
        move_list, score  = self.alpha_beta(1, 0, None, -10000001, 10000001, None, self.board.turn)
        for i in range(2, depth + 1):
            print("Iteration", i)
            move_list, score = self.alpha_beta(i, 0, None, -10000001, 10000001, move_list, self.board.turn)
        print("Depth calculated:", len(move_list))
        return str(move_list[-1])

if __name__=="__main__":

    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    newengine = Engine(fen)


    start_time = time.time()
    print(newengine.calculate_ab(4))
    print(newengine.total_leaves())
    print("Time taken:", time.time() - start_time)

    start_time = time.time()
    print(newengine.iterative_deepening(4))
    print(newengine.total_leaves())
    print("Time taken:", time.time() - start_time)
