from flask import Flask, request, jsonify
from agent.inference import CricketInferenceEngine

app = Flask(__name__)

# Load inference engine once
engine = CricketInferenceEngine()

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "message": "Crickmate AI Agent backend is live"
    })

@app.route("/api/recommend-training", methods=["POST"])
def recommend_training():
    data = request.get_json()

    return jsonify({
        "training_plan": {
            "drills": [
                "Basic conditioning drills",
                "Light skill practice"
            ],
            "intensity": "Medium",
            "frequency": "3 days per week"
        },
        "explanation": [
            "This is a placeholder response",
            "AI rule engine will be added next"
        ]
    })

@app.route("/api/ask", methods=["POST"])
def ask_agent():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Missing message field"}), 400

    user_query = data["message"]
    response = engine.process_query(user_query)

    return jsonify({
        "user_input": user_query,
        "agent_response": response
    }), 200

if __name__ == "__main__":
    app.run(debug=True)
