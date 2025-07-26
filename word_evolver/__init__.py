from flask import Blueprint, request, jsonify, render_template, session
import random, string

word_evolver = Blueprint('word_evolver', __name__, template_folder='templates')

POPULATION_SIZE = 100
MUTATION_RATE = 0.01

def random_char():
    return random.choice(string.ascii_uppercase + ' ')

def random_individual(length):
    return ''.join(random_char() for _ in range(length))

def fitness(individual, target):
    return sum(1 for a, b in zip(individual, target) if a == b)

def mutate(individual, mutation_log):
    result = []
    for c in individual:
        if random.random() < MUTATION_RATE:
            new_char = random_char()
            mutation_log.append((c, new_char))
            result.append(new_char)
        else:
            result.append(c)
    return ''.join(result)

def crossover(parent1, parent2, crossover_log):
    split = random.randint(0, len(parent1) - 1)
    child = parent1[:split] + parent2[split:]
    crossover_log.append((parent1, parent2, child))
    return child

def evolve_population(population, target, debug_info):
    sorted_population = sorted(population, key=lambda x: fitness(x, target), reverse=True)
    new_generation = sorted_population[:10]
    crossover_log = []
    mutation_log = []
    fitness_calls = 0

    while len(new_generation) < POPULATION_SIZE:
        parent1 = tournament_selection(sorted_population, target)
        parent2 = tournament_selection(sorted_population, target)
        child = crossover(parent1, parent2, crossover_log)
        before_mutation = child
        child = mutate(child, mutation_log)
        new_generation.append(child)
        fitness_calls += 1

    debug_info['crossover_log'] = crossover_log
    debug_info['mutation_log'] = mutation_log
    debug_info['fitness_calls'] = fitness_calls + len(population)
    return new_generation

def tournament_selection(population, target, k=5):
    return max(random.sample(population, k), key=lambda x: fitness(x, target))

@word_evolver.route('/word-evolver')
def home():
    return render_template('wordEvolver.html')

@word_evolver.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    target = data.get("target", "").upper().strip()
    if not target:
        return jsonify({"error": "Target sentence required."}), 400

    session['target'] = target
    session['population'] = [random_individual(len(target)) for _ in range(POPULATION_SIZE)]
    session['generation'] = 0
    session['history'] = []
    return jsonify({"message": "Target set.", "length": len(target)})

@word_evolver.route('/next-generation')
def next_generation():
    if 'target' not in session:
        return jsonify({"error": "No target set. Please start first."}), 400

    target = session['target']
    population = session['population']
    generation = session['generation']
    history = session['history']

    generation += 1
    debug_info = {}
    population = evolve_population(population, target, debug_info)
    best = max(population, key=lambda x: fitness(x, target))
    fit = fitness(best, target)
    done = best == target

    explanation = f"Generation {generation}: Best string \"{best}\" has {fit}/{len(target)} matching characters."
    formula = f"Fitness = Number of matching characters between candidate and target (\"{target}\")"

    history.append({"generation": generation, "best": best, "fitness": fit})

    session['population'] = population
    session['generation'] = generation
    session['history'] = history

    return jsonify({
        "generation": generation,
        "best": best,
        "fitness": fit,
        "done": done,
        "history": history,
        "explanation": explanation,
        "calculations": {
            "crossover_log": debug_info['crossover_log'],
            "mutation_log": debug_info['mutation_log'],
            "fitnessCalls": debug_info['fitness_calls'],
            "formula": formula
        }
    })

@word_evolver.route('/reset', methods=['POST'])
def reset():
    session.clear()
    return jsonify({"message": "Reset complete."})
