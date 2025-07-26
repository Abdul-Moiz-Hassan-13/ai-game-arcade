from flask import Blueprint, request, jsonify, render_template
import math, random

tic_tac_toe = Blueprint('tic_tac_toe', __name__, template_folder='templates')

def is_winner(board, player):
    wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    return any(all(board[i] == player for i in combo) for combo in wins)

def is_draw(board):
    return ' ' not in board

def get_available_moves(board):
    return [i for i, val in enumerate(board) if val == ' ']

def minimax(board, is_max, alpha, beta):
    if is_winner(board, 'O'):
        return 1
    if is_winner(board, 'X'):
        return -1
    if is_draw(board):
        return 0

    if is_max:
        best = -math.inf
        for i in get_available_moves(board):
            board[i] = 'O'
            score = minimax(board, False, alpha, beta)
            board[i] = ' '
            best = max(best, score)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = math.inf
        for i in get_available_moves(board):
            board[i] = 'X'
            score = minimax(board, True, alpha, beta)
            board[i] = ' '
            best = min(best, score)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best

def best_move(board, difficulty):
    available = get_available_moves(board)

    if difficulty == "easy":
        return random.choice(available)

    if difficulty == "medium":
        if random.random() < 0.5:
            return random.choice(available)

    best_score = -math.inf
    move = None
    for i in available:
        board[i] = 'O'
        score = minimax(board, False, alpha=-math.inf, beta=math.inf)
        board[i] = ' '
        if score > best_score:
            best_score = score
            move = i
    return move

@tic_tac_toe.route('/tic-tac-toe')
def game():
    return render_template('tictactoe.html')

@tic_tac_toe.route('/tic-tac-toe/ai-move', methods=['POST'])
def ai_move():
    data = request.json
    board = data['board']
    difficulty = data.get('difficulty', 'hard')
    move = best_move(board, difficulty)
    return jsonify({'move': move})
