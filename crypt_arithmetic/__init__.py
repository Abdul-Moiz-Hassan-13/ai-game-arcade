from flask import Blueprint, request, jsonify, render_template
import random

crypt_arithmetic = Blueprint('crypt_arithmetic', __name__, template_folder='templates')

PUZZLES = {
    "easy": [
        ("TO", "GO", "OUT"),
        ("HI", "BY", "END"),
        ("BE", "ME", "SHE"),
        ("SO", "NO", "YES"),
        ("IT", "IS", "FUN")
    ],
    "medium": [
        ("SEND", "MORE", "MONEY"),
        ("BASE", "BALL", "GAMES"),
        ("SAFE", "ZONE", "RULES"),
        ("LOOK", "BACK", "AGAIN"),
        ("FAST", "FOOD", "MEALS")
    ],
    "hard": [
        ("TRUE", "LOVE", "HEART"),
        ("SING", "SONG", "MUSIC"),
        ("MARK", "TEST", "GRADE"),
        ("APPLE", "PEAR", "PLUMS"),
        ("LUCK", "LUCK", "MAGIC")
    ]
}

puzzle_index = {"easy": 0, "medium": 0, "hard": 0}
current_puzzle = {}


def solve_crypt(word1, word2, result):
    letters = sorted(set(word1 + word2 + result))
    if len(letters) > 10:
        return None

    first_letters = {word1[0], word2[0], result[0]}
    domains = {l: set(range(10)) for l in letters}
    for fl in first_letters:
        domains[fl].discard(0)

    def is_valid(assignment):
        if len(set(assignment.values())) < len(assignment):
            return False
        if len(assignment) < len(letters):
            return True
        def val(w): return int(''.join(str(assignment[c]) for c in w))
        return val(word1) + val(word2) == val(result)

    def forward_check(assignment):
        used = set(assignment.values())
        for var in letters:
            if var not in assignment:
                possible = domains[var] - used
                if not possible:
                    return False
        return True

    def backtrack(assignment):
        if len(assignment) == len(letters):
            return assignment if is_valid(assignment) else None

        var = next(v for v in letters if v not in assignment)
        for val in domains[var]:
            if val in assignment.values():
                continue
            assignment[var] = val
            if is_valid(assignment) and forward_check(assignment):
                result_assignment = backtrack(assignment)
                if result_assignment:
                    return result_assignment
            del assignment[var]
        return None

    return backtrack({})


@crypt_arithmetic.route('/crypt-arithmetic')
def game():
    return render_template('crypt.html', puzzles=PUZZLES)


@crypt_arithmetic.route('/crypt-arithmetic/get-puzzle', methods=['POST'])
def get_puzzle():
    global current_puzzle, puzzle_index
    difficulty = request.json.get("difficulty", "medium")
    puzzles = PUZZLES[difficulty]
    total = len(puzzles)

    for _ in range(total):
        idx = puzzle_index[difficulty]
        word1, word2, result = puzzles[idx]
        solution = solve_crypt(word1, word2, result)
        puzzle_index[difficulty] = (idx + 1) % total
        if solution:
            current_puzzle = {
                "word1": word1,
                "word2": word2,
                "result": result,
                "solution": solution,
                "user_entries": {}
            }
            return jsonify({
                "word1": word1,
                "word2": word2,
                "result": result,
                "letters": sorted(solution.keys())
            })
    return jsonify({"error": "No solvable puzzle found"}), 500


@crypt_arithmetic.route('/crypt-arithmetic/custom-check', methods=['POST'])
def custom_check():
    data = request.json
    word1 = data.get("word1", "").upper()
    word2 = data.get("word2", "").upper()
    result = data.get("result", "").upper()
    solution = solve_crypt(word1, word2, result)
    if solution:
        return jsonify({"solvable": True, "letters": sorted(solution.keys())})
    return jsonify({"solvable": False})


@crypt_arithmetic.route('/crypt-arithmetic/check-letter', methods=['POST'])
def check_letter():
    data = request.json
    letter = data['letter']
    digit = int(data['digit'])
    current_puzzle['user_entries'][letter] = digit

    for k, v in current_puzzle['user_entries'].items():
        if k != letter and v == digit:
            return jsonify({"correct": False, "conflict": True})

    correct = current_puzzle['solution'][letter] == digit
    return jsonify({"correct": correct, "conflict": False})


@crypt_arithmetic.route('/crypt-arithmetic/get-hint')
def get_hint():
    remaining = [l for l in current_puzzle['solution'] if
                 l not in current_puzzle['user_entries'] or
                 current_puzzle['user_entries'][l] != current_puzzle['solution'][l]]
    if not remaining:
        return jsonify({"done": True})
    letter = random.choice(remaining)
    digit = current_puzzle['solution'][letter]
    current_puzzle['user_entries'][letter] = digit
    return jsonify({"letter": letter, "digit": digit})

@crypt_arithmetic.route('/crypt-arithmetic/check-custom', methods=['POST'])
def check_custom():
    data = request.json
    word1 = data.get("word1", "").upper().strip()
    word2 = data.get("word2", "").upper().strip()
    result = data.get("result", "").upper().strip()
    
    if not word1 or not word2 or not result:
        return jsonify({"error": "All fields are required"}), 400
    
    if not word1.isalpha() or not word2.isalpha() or not result.isalpha():
        return jsonify({"error": "Only letters are allowed"}), 400
    
    solution = solve_crypt(word1, word2, result)
    if solution:
        return jsonify({
            "solvable": True,
            "solution": solution,
            "letters": sorted(solution.keys())
        })
    return jsonify({"solvable": False, "solution": None})

@crypt_arithmetic.route('/crypt-arithmetic/get-puzzle-by-index', methods=['POST'])
def get_puzzle_by_index():
    global current_puzzle
    data = request.json
    difficulty = data.get("difficulty", "medium")
    index = data.get("index", 0)
    
    try:
        puzzles = PUZZLES[difficulty]
        index = int(index)
        if index < 0 or index >= len(puzzles):
            return jsonify({"error": "Invalid puzzle index"}), 400
            
        word1, word2, result = puzzles[index]
        solution = solve_crypt(word1, word2, result)
        if solution:
            current_puzzle = {
                "word1": word1,
                "word2": word2,
                "result": result,
                "solution": solution,
                "user_entries": {}
            }
            return jsonify({
                "word1": word1,
                "word2": word2,
                "result": result,
                "letters": sorted(solution.keys()),
                "total": len(puzzles)
            })
        return jsonify({"error": "Puzzle not solvable"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
