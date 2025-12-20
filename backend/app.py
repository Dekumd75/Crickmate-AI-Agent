from flask import Flask, request, jsonify

# Core imports
from agent.inference import CricketInferenceEngine
from agent.user_manager import UserManager
from agent.user_profile import UserProfile
from agent.exercise_engine import ExerciseEngine
from agent.tech_engine import TechEngine
from agent.conversation_router import ConversationRouter

# Flask app
app = Flask(__name__)

# Single instances — IMPORTANT
engine = CricketInferenceEngine()
user_manager = UserManager()
exercise_engine = ExerciseEngine()
tech_engine = TechEngine()
router = ConversationRouter(engine, tech_engine, exercise_engine)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "message": "Crickmate AI Agent backend is live"
    })


@app.route("/api/recommend-training", methods=["POST"])
def recommend_training():
    return jsonify({
        "training_plan": {
            "drills": [
                "Basic conditioning drills",
                "Light skill practice"
            ],
            "intensity": "Medium",
            "frequency": "3 days per week"
        }
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



@app.route("/api/register-user", methods=["POST"])
def register_user():
    user_data = request.get_json()

    success, info = user_manager.register_user(user_data)

    if not success:
        return jsonify({"status": "error", "message": info}), 400

    return jsonify({
        "status": "success",
        "user_id": info,
        "message": "User registered successfully"
    })



@app.route("/api/get-user/<user_id>", methods=["GET"])
def get_user(user_id):
    success, info = user_manager.get_user(user_id)

    if not success:
        return jsonify({"status": "error", "message": info}), 404

    return jsonify({
        "status": "success",
        "profile": info
    })



@app.route("/api/get-batting-exercises", methods=["POST"])
def get_batting_exercises():

    data = request.get_json()

    if not data or "user_id" not in data or "goal" not in data:
        return jsonify({"error": "Missing user_id or goal"}), 400

    user_id = data["user_id"]
    goal = data["goal"]

    # retrieve saved raw dict
    success, user_dict = user_manager.get_user(user_id)

    if not success:
        return jsonify({"error": "User not found"}), 404

    # convert dict → UserProfile
    user = UserProfile(
        age=user_dict["age"],
        height_cm=user_dict["height_cm"],
        weight_kg=user_dict["weight_kg"],
        skill_level=user_dict["skill_level"],
        playing_role=user_dict["playing_role"],
        weekly_days=user_dict.get("weekly_training_days", None)
    )

    result = exercise_engine.get_batting_exercises(user, goal)

    return jsonify(result), 200

@app.route("/api/get-exercise-details", methods=["POST"])
def get_exercise_details():

    data = request.get_json()

    if "user_id" not in data or "exercise_name" not in data:
        return jsonify({"error": "Missing user_id or exercise_name"}), 400

    user_id = data["user_id"]
    exercise_name = data["exercise_name"]

    # get raw dict
    success, user_dict = user_manager.get_user(user_id)

    if not success:
        return jsonify({"error": "User not found"}), 404

    # convert into UserProfile object
    user = UserProfile(
        age=user_dict["age"],
        height_cm=user_dict["height_cm"],
        weight_kg=user_dict["weight_kg"],
        skill_level=user_dict["skill_level"],
        playing_role=user_dict["playing_role"],
        weekly_days=user_dict.get("weekly_training_days", None)
    )

    result = exercise_engine.get_exercise_details(user, exercise_name)

    return jsonify(result), 200





@app.route("/api/get-technical-drills", methods=["POST"])
def get_technical_drills():

    data = request.get_json()

    if not data or "user_id" not in data:
        return jsonify({"error": "Missing user_id"}), 400

    user_id = data["user_id"]

    # Load user from database
    success, user_dict = user_manager.get_user(user_id)

    if not success:
        return jsonify({"error": "User not found"}), 404

    # Create user object
    user = UserProfile(
        age=user_dict["age"],
        height_cm=user_dict["height_cm"],
        weight_kg=user_dict["weight_kg"],
        skill_level=user_dict["skill_level"],
        playing_role=user_dict["playing_role"],
        weekly_days=user_dict.get("weekly_training_days", None)
    )

    result = tech_engine.recommend_technical_areas(user)

    return jsonify(result), 200

@app.route("/api/ask-tech", methods=["POST"])
def ask_technical():

    data = request.get_json()

    if "user_id" not in data or "question" not in data:
        return jsonify({"error": "Missing user_id or question"}), 400

    user_id = data["user_id"]
    question = data["question"].lower()

    success, user_dict = user_manager.get_user(user_id)

    if not success:
        return jsonify({"error": "User not found"}), 404

    # Convert raw dict → profile object
    user = UserProfile(
        age=user_dict["age"],
        height_cm=user_dict["height_cm"],
        weight_kg=user_dict["weight_kg"],
        skill_level=user_dict["skill_level"],
        playing_role=user_dict["playing_role"],
        weekly_days=user_dict.get("weekly_training_days", None)
    )

    # search for area match
    area = tech_engine.search_area_by_query(question)

    if not area:
        return jsonify({
            "response": "Sorry, I couldn't match that to a technical area. Try asking more specific like 'improve timing' or 'fix footwork'."
        })

    result = tech_engine.format_area_output(area)

    return jsonify(result), 200

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if "user_id" not in data or "message" not in data:
        return jsonify({"error": "user_id & message required"}), 400

    success, user_dict = user_manager.get_user(data["user_id"])

    if not success:
        return jsonify({"error": "User not found"}), 404

    user = UserProfile(
        name=user_dict["name"],
        age=user_dict["age"],
        height_cm=user_dict["height_cm"],
        weight_kg=user_dict["weight_kg"],
        skill_level=user_dict["skill_level"],
        playing_role=user_dict["playing_role"],
    )

    text = data["message"]
    response = router.process(data["user_id"], user, text)

    return jsonify(response), 200


# END
if __name__ == "__main__":
    app.run(debug=True)
