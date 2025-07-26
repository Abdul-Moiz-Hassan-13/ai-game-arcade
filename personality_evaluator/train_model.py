import random
import numpy as np
from sklearn.linear_model import LogisticRegression
import joblib

NUM_SAMPLES = 500

traits = {
    "EI": ("E", "I"),
    "SN": ("S", "N"),
    "TF": ("T", "F"),
    "JP": ("J", "P")
}

def generate_trait_data():
    data = {}
    for trait_code, (pos_label, neg_label) in traits.items():
        X, y = [], []
        for _ in range(NUM_SAMPLES):
            answers = [random.randint(0, 1) for _ in range(5)]
            X.append(answers)
            label = 1 if sum(answers) >= 2 else 0
            y.append(label)
        data[trait_code] = (np.array(X), np.array(y))
    return data

all_data = generate_trait_data()
for trait_code, (X, y) in all_data.items():
    model = LogisticRegression()
    model.fit(X, y)
    joblib.dump(model, f"personality_model_{trait_code}.pkl")
    print(f"Trained and saved model for {trait_code} ({traits[trait_code][0]}/{traits[trait_code][1]})")
