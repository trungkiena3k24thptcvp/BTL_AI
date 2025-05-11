"""
Handling the AI moves.
"""
import random
import time

TIME_LIMIT = 5
piece_score = {"K": 1000, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

knight_scores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawn_scores = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piece_position_scores = {"wN": knight_scores,
                         "bN": knight_scores[::-1],
                         "wB": bishop_scores,
                         "bB": bishop_scores[::-1],
                         "wQ": queen_scores,
                         "bQ": queen_scores[::-1],
                         "wR": rook_scores,
                         "bR": rook_scores[::-1],
                         "wp": pawn_scores,
                         "bp": pawn_scores[::-1]}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 4


def findBestMove(game_state, valid_moves, return_queue):
    """
    Find the best move using the iterative deepening search with negamax algorithm and alpha-beta pruning.
    """
    global next_move, stop_search
    next_move = None
    stop_search = False
    random.shuffle(valid_moves)

    start_time = time.time()

    # Iterative deepening loop
    for depth in range(1, DEPTH + 1):
        findMoveNegaMaxAlphaBeta(game_state, valid_moves, depth, -CHECKMATE, CHECKMATE,
                                 1 if game_state.whiteToMove else -1, start_time)

        # If we have exceeded the time limit, stop further searching
        if stop_search:
            break

    # Nếu hết thời gian mà chưa tìm được move tốt nhất, chọn random
    if next_move is None:
        next_move = findRandomMove(valid_moves)

    return_queue.put(next_move)


def findMoveNegaMaxAlphaBeta(game_state, valid_moves, depth, alpha, beta, turn_multiplier, start_time):
    """
    Negamax with alpha-beta pruning and time cutoff.
    """
    global next_move, stop_search

    # Ngắt sớm nếu vượt quá thời gian
    if time.time() - start_time > TIME_LIMIT:
        stop_search = True
        return 0  # Không tính gì nữa

    if depth == 0 or stop_search:
        return turn_multiplier * scoreBoard(game_state)

    valid_moves = orderMoves(game_state, valid_moves)
    max_score = -CHECKMATE

    for move in valid_moves:
        game_state.makeMove(move)
        next_moves = game_state.getAllValidMoves()
        score = -findMoveNegaMaxAlphaBeta(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier, start_time)
        game_state.undoMove()

        if stop_search:
            break

        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break

    return max_score


def orderMoves(game_state, moves):
    """
    Order moves based on a heuristic to prioritize better moves.
    """

    def moveScore(move):
        score = 0

        # Capture priority: Assign a high value to captures.
        if move.pieceCaptured != "--":
            score += 10 * piece_score[move.pieceCaptured[1]]  # Capturing higher-valued pieces is better.

        # Promotion bonus
        if move.isPawnPromotion:
            score += 1000  # Prioritize pawn promotions.

        # Castling: Assign a lower priority bonus for castling.
        if move.isCastleMove:
            score += 50

        # Optionally: Add checks, positional advantages, etc.
        return score

    # Sort moves by descending score (higher is better)
    moves.sort(key=moveScore, reverse=True)
    return moves


def scoreBoard(game_state):
    """
    Score the board. A positive score is good for white, and a negative score is good for black.
    """
    if game_state.checkmate:
        if game_state.whiteToMove:
            return -CHECKMATE  # Black wins
        else:
            return CHECKMATE  # White wins
    elif game_state.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            piece = game_state.board[row][col]
            if piece != "--":
                piece_position_score = 0
                if piece[1] != "K":  # King is not scored with positional advantages
                    piece_position_score = piece_position_scores[piece][row][col]
                if piece[0] == "w":
                    score += piece_score[piece[1]] + piece_position_score
                if piece[0] == "b":
                    score -= piece_score[piece[1]] + piece_position_score

    return score


def findRandomMove(valid_moves):
    """
    Picks and returns a random valid move.
    """
    return random.choice(valid_moves)