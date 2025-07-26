from flask import Blueprint, request, jsonify, render_template
import random, heapq

eight_puzzle = Blueprint('eight_puzzle', __name__, template_folder='templates')

goal_state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
tile_positions = {val: (i // 3, i % 3) for i, val in enumerate(goal_state)}

current_state = goal_state.copy()
solution_path = []
score = 0

def manhattan(state):
    return sum(abs((i // 3) - tile_positions[val][0]) + abs((i % 3) - tile_positions[val][1])
               for i, val in enumerate(state) if val != 0)

def get_neighbors(state):
    idx = state.index(0)
    x, y = idx // 3, idx % 3
    moves = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            nidx = nx * 3 + ny
            new_state = state.copy()
            new_state[idx], new_state[nidx] = new_state[nidx], new_state[idx]
            moves.append((new_state, new_state[idx]))
    return moves

def a_star(start):
    visited = set()
    heap = [(manhattan(start), 0, start, [])]
    while heap:
        f, g, state, path = heapq.heappop(heap)
        if state == goal_state:
            return path
        visited.add(tuple(state))
        for neighbor, tile_moved in get_neighbors(state):
            if tuple(neighbor) not in visited:
                heapq.heappush(heap, (g + 1 + manhattan(neighbor), g + 1, neighbor, path + [neighbor]))
    return []

def is_solvable(state):
    inv = 0
    for i in range(8):
        for j in range(i + 1, 9):
            if state[i] and state[j] and state[i] > state[j]:
                inv += 1
    return inv % 2 == 0

def shuffle_board():
    state = goal_state.copy()
    while True:
        random.shuffle(state)
        if is_solvable(state) and state != goal_state:
            return state

@eight_puzzle.route('/8-puzzle')
def index():
    return render_template('8puzzle.html')

@eight_puzzle.route('/8-puzzle/shuffle', methods=['POST'])
def shuffle():
    global current_state, solution_path, score
    current_state = shuffle_board()
    solution_path = a_star(current_state)
    score = 0
    return jsonify({"state": current_state, "score": score})

@eight_puzzle.route('/8-puzzle/move', methods=['POST'])
def move():
    global current_state, score
    data = request.json
    tile = data['tile']

    idx = current_state.index(0)
    tile_idx = current_state.index(tile)
    x1, y1 = idx // 3, idx % 3
    x2, y2 = tile_idx // 3, tile_idx % 3
    if abs(x1 - x2) + abs(y1 - y2) != 1:
        return jsonify({"valid": False})

    simulated = current_state.copy()
    simulated[idx], simulated[tile_idx] = simulated[tile_idx], simulated[idx]

    new_path = a_star(current_state)
    correct = new_path and simulated == new_path[0]

    current_state[idx], current_state[tile_idx] = current_state[tile_idx], current_state[idx]

    if correct:
        score += 5
    else:
        score = max(0, score - 5)

    return jsonify({"valid": True, "correct": correct, "state": current_state, "score": score})

@eight_puzzle.route('/8-puzzle/hint', methods=['GET'])
def hint():
    global current_state, score
    solution_path = a_star(current_state)
    if not solution_path:
        return jsonify({"done": True})
    current_state = solution_path[0]
    solution_path.pop(0)
    score = max(0, score - 2)
    return jsonify({"state": current_state, "score": score})