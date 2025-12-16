from flask import Flask, request, jsonify

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(debug=True)
