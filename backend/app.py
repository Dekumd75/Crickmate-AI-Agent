from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Core imports
from agent.inference import CricketInferenceEngine
from agent.user_manager import UserManager
from agent.user_profile import UserProfile
from agent.exercise_engine import ExerciseEngine
from agent.tech_engine import TechEngine
from agent.conversation_router import ConversationRouter

# Flask app
app = Flask(__name__)
CORS(app) # Allow the Frontend to talk to us

# Single instances
print("🚀 Starting CrickMate AI Engines...")
engine = CricketInferenceEngine()
user_manager = UserManager()
exercise_engine = ExerciseEngine()
tech_engine = TechEngine()

# INITIALIZE ROUTER (With RAG support if you have the file)
# If this fails, make sure conversation_router.py is also updated!
router = ConversationRouter(engine, tech_engine, exercise_engine)

print("✅ Engines Online!")

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# --- OLD ENDPOINTS (For Postman) ---
@app.route("/api/recommend-training", methods=["POST"])
def recommend_training():
    return jsonify({"training_plan": {"drills": ["Basic drills"], "intensity": "Medium"}})

@app.route("/api/ask", methods=["POST"])
def ask_agent():
    data = request.get_json()
    user_query = data["message"]
    response = engine.process_query(user_query)
    return jsonify({"user_input": user_query, "agent_response": response})

@app.route("/api/register-user", methods=["POST"])
def register_user():
    user_data = request.get_json()
    success, info = user_manager.register_user(user_data)
    if not success: return jsonify({"status": "error", "message": info}), 400
    return jsonify({"status": "success", "user_id": info, "message": "User registered successfully"})

@app.route("/api/get-user/<user_id>", methods=["GET"])
def get_user(user_id):
    success, info = user_manager.get_user(user_id)
    if not success: return jsonify({"status": "error", "message": info}), 404
    return jsonify({"status": "success", "profile": info})

@app.route("/api/get-batting-exercises", methods=["POST"])
def get_batting_exercises():
    data = request.get_json()
    user_id = data["user_id"]
    goal = data["goal"]
    success, user_dict = user_manager.get_user(user_id)
    if not success: return jsonify({"error": "User not found"}), 404
    user = UserProfile(
        age=user_dict["age"], height_cm=user_dict["height_cm"], weight_kg=user_dict["weight_kg"],
        skill_level=user_dict["skill_level"], playing_role=user_dict["playing_role"],
        weekly_days=user_dict.get("weekly_training_days", None)
    )
    result = exercise_engine.get_batting_exercises(user, goal)
    return jsonify(result), 200

@app.route("/api/get-exercise-details", methods=["POST"])
def get_exercise_details():
    data = request.get_json()
    user_id = data["user_id"]
    exercise_name = data["exercise_name"]
    success, user_dict = user_manager.get_user(user_id)
    if not success: return jsonify({"error": "User not found"}), 404
    user = UserProfile(
        age=user_dict["age"], height_cm=user_dict["height_cm"], weight_kg=user_dict["weight_kg"],
        skill_level=user_dict["skill_level"], playing_role=user_dict["playing_role"],
        weekly_days=user_dict.get("weekly_training_days", None)
    )
    result = exercise_engine.get_exercise_details(user, exercise_name)
    return jsonify(result), 200

@app.route("/api/get-technical-drills", methods=["POST"])
def get_technical_drills():
    data = request.get_json()
    user_id = data["user_id"]
    success, user_dict = user_manager.get_user(user_id)
    if not success: return jsonify({"error": "User not found"}), 404
    user = UserProfile(
        age=user_dict["age"], height_cm=user_dict["height_cm"], weight_kg=user_dict["weight_kg"],
        skill_level=user_dict["skill_level"], playing_role=user_dict["playing_role"],
        weekly_days=user_dict.get("weekly_training_days", None)
    )
    result = tech_engine.recommend_technical_areas(user)
    return jsonify(result), 200

@app.route("/api/ask-tech", methods=["POST"])
def ask_technical():
    data = request.get_json()
    user_id = data["user_id"]
    question = data["question"].lower()
    success, user_dict = user_manager.get_user(user_id)
    if not success: return jsonify({"error": "User not found"}), 404
    area = tech_engine.search_area_by_query(question)
    if not area: return jsonify({"response": "Sorry, I couldn't match that to a technical area."})
    result = tech_engine.format_area_output(area)
    return jsonify(result), 200

# --- 🚀 THE NEW CHAT ENDPOINT (THIS WAS MISSING!) ---
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()

    # 1. Validation
    if not data or "message" not in data:
        return jsonify({"error": "message required"}), 400
    
    # 2. Default User (If frontend doesn't send ID)
    user_id = data.get("user_id", "GUEST_WEB")
    
    # 3. Create a Guest User if ID not found
    success, user_dict = user_manager.get_user(user_id)
    if not success:
        # Create a temp profile for the guest
        user = UserProfile(
            name="Guest", age=20, height_cm=180, weight_kg=75,
            skill_level="Intermediate", playing_role="Top Order Batsman"
        )
    else:
        user = UserProfile(
            name=user_dict["name"], age=user_dict["age"], height_cm=user_dict["height_cm"],
            weight_kg=user_dict["weight_kg"], skill_level=user_dict["skill_level"],
            playing_role=user_dict["playing_role"],
        )

    # 4. Process Message
    text = data["message"]
    response = router.process(user_id, user, text)

    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)