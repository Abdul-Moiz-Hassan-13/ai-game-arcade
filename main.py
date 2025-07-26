from flask import Flask, send_file
from tic_tac_toe import tic_tac_toe
from crypt_arithmetic import crypt_arithmetic
from eight_puzzle import eight_puzzle
from personality_evaluator import personality_evaluator
from word_evolver import word_evolver

app = Flask(__name__)
app.secret_key = 'secret-key'

app.register_blueprint(tic_tac_toe)
app.register_blueprint(crypt_arithmetic)
app.register_blueprint(eight_puzzle)
app.register_blueprint(personality_evaluator)
app.register_blueprint(word_evolver)

@app.route('/')
def home():
    return send_file('index.html')

if __name__ == '__main__':
    app.run(debug=True)
