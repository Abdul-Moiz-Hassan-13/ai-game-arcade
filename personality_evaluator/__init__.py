from flask import Blueprint, request, jsonify, render_template
import joblib
import numpy as np

personality_evaluator = Blueprint('personality_evaluator', __name__, template_folder='templates')

trait_codes = ["EI", "SN", "TF", "JP"]
models = {}
for code in trait_codes:
    models[code] = joblib.load(f"personality_evaluator/personality_model_{code}.pkl")

recommendations = {
    "INTJ": {
        "careers": ["Strategist", "Scientist"],
        "traits": "Independent, insightful",
        "description": "INTJs are imaginative yet decisive, ambitious yet private. They are rational strategists with a love for complex challenges. They thrive in analytical or technical careers.",
        "full_form": "Introverted, Intuitive, Thinking, Judging"
    },
    "INTP": {
        "careers": ["Philosopher", "Programmer"],
        "traits": "Analytical, curious",
        "description": "INTPs are deep thinkers, curious and logical. They often prefer theory over practice and thrive in intellectually stimulating environments like academia or development.",
        "full_form": "Introverted, Intuitive, Thinking, Perceiving"
    },
    "ENTJ": {
        "careers": ["Executive", "Entrepreneur"],
        "traits": "Confident, organized",
        "description": "ENTJs are natural-born leaders, assertive and efficient. They excel in strategic planning and often drive businesses or projects to success.",
        "full_form": "Extraverted, Intuitive, Thinking, Judging"
    },
    "ENTP": {
        "careers": ["Inventor", "Marketer"],
        "traits": "Creative, energetic",
        "description": "ENTPs are quick-witted and love debate and innovation. They are entrepreneurial and thrive in fast-paced creative or business roles.",
        "full_form": "Extraverted, Intuitive, Thinking, Perceiving"
    },
    "INFJ": {
        "careers": ["Psychologist", "Writer"],
        "traits": "Empathetic, visionary",
        "description": "INFJs are insightful, altruistic, and principled. They often find fulfillment in helping others grow, and are drawn to meaningful, mission-driven work.",
        "full_form": "Introverted, Intuitive, Feeling, Judging"
    },
    "INFP": {
        "careers": ["Counselor", "Artist"],
        "traits": "Idealistic, sensitive",
        "description": "INFPs are introspective, compassionate, and imaginative. They seek harmony, authenticity, and creativity in all aspects of life.",
        "full_form": "Introverted, Intuitive, Feeling, Perceiving"
    },
    "ENFJ": {
        "careers": ["Teacher", "Leader"],
        "traits": "Charismatic, altruistic",
        "description": "ENFJs are passionate and inspiring communicators who value connection. They thrive in leadership and mentoring roles.",
        "full_form": "Extraverted, Intuitive, Feeling, Judging"
    },
    "ENFP": {
        "careers": ["Journalist", "Motivational Speaker"],
        "traits": "Enthusiastic, imaginative",
        "description": "ENFPs are free-spirited and warm. They are often imaginative people who enjoy exploring ideas and expressing themselves creatively.",
        "full_form": "Extraverted, Intuitive, Feeling, Perceiving"
    },
    "ISTJ": {
        "careers": ["Auditor", "Military Officer"],
        "traits": "Reliable, detail-oriented",
        "description": "ISTJs are dutiful and meticulous. They value tradition and order, often excelling in administrative, logistical, or structured environments.",
        "full_form": "Introverted, Sensing, Thinking, Judging"
    },
    "ISFJ": {
        "careers": ["Nurse", "Librarian"],
        "traits": "Supportive, meticulous",
        "description": "ISFJs are nurturing, dedicated, and practical. They enjoy helping others and often work behind the scenes to keep systems running.",
        "full_form": "Introverted, Sensing, Feeling, Judging"
    },
    "ESTJ": {
        "careers": ["Manager", "Lawyer"],
        "traits": "Practical, assertive",
        "description": "ESTJs are organizers who live by a strong sense of duty. They thrive in leadership positions and enforce structure.",
        "full_form": "Extraverted, Sensing, Thinking, Judging"
    },
    "ESFJ": {
        "careers": ["Social Worker", "Customer Service Rep"],
        "traits": "Loyal, cooperative",
        "description": "ESFJs are caring and social, always ready to help others. They shine in roles that require collaboration and attention to interpersonal needs.",
        "full_form": "Extraverted, Sensing, Feeling, Judging"
    },
    "ISTP": {
        "careers": ["Engineer", "Mechanic"],
        "traits": "Logical, hands-on",
        "description": "ISTPs are observant and adaptable, often excelling in practical problem solving and technical skills.",
        "full_form": "Introverted, Sensing, Thinking, Perceiving"
    },
    "ISFP": {
        "careers": ["Chef", "Musician"],
        "traits": "Artistic, quiet",
        "description": "ISFPs are gentle and spontaneous. They are artistically inclined and prefer expressing themselves through action over words.",
        "full_form": "Introverted, Sensing, Feeling, Perceiving"
    },
    "ESTP": {
        "careers": ["Salesperson", "Paramedic"],
        "traits": "Bold, active",
        "description": "ESTPs are energetic and perceptive. They thrive in dynamic environments and enjoy solving real-world problems quickly.",
        "full_form": "Extraverted, Sensing, Thinking, Perceiving"
    },
    "ESFP": {
        "careers": ["Actor", "Event Planner"],
        "traits": "Fun-loving, outgoing",
        "description": "ESFPs are entertainers who enjoy life to the fullest. They are spontaneous and enjoy making people happy.",
        "full_form": "Extraverted, Sensing, Feeling, Perceiving"
    }
}


@personality_evaluator.route('/personality-evaluator')
def home():
    return render_template("personalityEvaluator.html")

@personality_evaluator.route('/personality-evaluator/predict', methods=['POST'])
def predict():
    data = request.get_json()
    answers = data.get("answers")

    if not answers or len(answers) != 20:
        return jsonify({"error": "Please provide all the answers."}), 400

    result = ""
    confidence = []

    for i, code in enumerate(trait_codes):
        model = models[code]
        input_data = np.array([answers[i*5:(i+1)*5]])
        pred = model.predict(input_data)[0]
        prob = model.predict_proba(input_data)[0][pred]
        result += code[pred]
        confidence.append(round(prob * 100, 2))

    rec = recommendations.get(result, {
        "careers": ["N/A"],
        "traits": "Unique mix!",
        "description": "No specific description available.",
        "full_form": "No title available."
    })

    return jsonify({
        "mbti": result,
        "confidence": confidence,
        "careers": rec["careers"],
        "traits": rec["traits"],
        "description": rec["description"],
        "full_form": rec["full_form"]
    })
