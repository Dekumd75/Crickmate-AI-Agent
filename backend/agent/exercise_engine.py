import json
import os

class ExerciseEngine:

    GOAL_MAP = {
        "power": "POWER_HITTING",
        "strength": "POWER_HITTING",
        "power hitting": "POWER_HITTING",
        "batting power": "POWER_HITTING",

        "endurance": "ENDURANCE_FITNESS",
        "fitness": "ENDURANCE_FITNESS",
        "stamina": "ENDURANCE_FITNESS",
        "running": "ENDURANCE_FITNESS",

        "timing": "TIMING_CONTROL",
        "control": "TIMING_CONTROL",

        "footwork": "FOOTWORK_AGILITY",
        "agility": "FOOTWORK_AGILITY",
        "speed": "FOOTWORK_AGILITY",
    }


    def __init__(self):
        self.exercises = self._load_batting_exercises()


    def _load_batting_exercises(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base_path, "data", "exercises", "batting_exercises.json")

        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data["batting_exercises"]


    # --------------------------------------------------------
    # MAIN ENTRY
    # --------------------------------------------------------
    def get_batting_exercises(self, user, message_text):

        # 1️⃣ detect goal from message text
        detected_goal = self._detect_goal(message_text)

        if not detected_goal:
            return {
                "error": True,
                "message": "Goal not recognized. Try power / timing / endurance / footwork"
            }

        # 2️⃣ get all matching exercises
        matches = self._filter_by_goal(detected_goal)

        if not matches:
            return {
                "error": True,
                "message": "No exercises exist for this goal."
            }

        # 3️⃣ personalise every exercise found
        output = self._personalise_all(user, matches)

        # 4️⃣ safety warning
        warning = self._warning(user, detected_goal)

        return {
            "goal_detected": detected_goal,
            "total_exercises_found": len(matches),
            "warning": warning,
            "exercises": output
        }



    # --------------------------------------------------------
    # GOAL EXTRACTION
    # --------------------------------------------------------
    def _detect_goal(self, text):

        text = text.lower()

        for key, goal in self.GOAL_MAP.items():
            if key in text:
                return goal

        return "POWER_HITTING"  # safe default fallback



    # --------------------------------------------------------
    # GET EXERCISES BELONGING TO GOAL
    # --------------------------------------------------------
    def _filter_by_goal(self, goal):

        selected = []

        for ex in self.exercises:
            if goal in ex["goals"] or "ALL" in ex["goals"]:
                selected.append(ex)

        return selected



    # --------------------------------------------------------
    # PERSONALISE EVERY EXERCISE FOUND
    # --------------------------------------------------------
    def _personalise_all(self, user, exercise_list):

        output = []

        for ex in exercise_list:

            # pick right prescription
            pres = self._find_prescription(user, ex)

            entry = {
                "exercise_name": ex["name"],
                "exercise_type": ex["type"],
                "equipment": ex["equipment"],
                "benefits": ex["benefits"],
                "how_to_do": ex["how_to"],
                "safety_notes": ex["safety_notes"],
                "recommended_for_role": user.playing_role in ex["role_priority"]
            }

            # attach dosage if found
            if pres:
                entry["sets"] = pres["sets"]
                entry["reps"] = pres["reps"]
                entry["rest_seconds"] = pres["rest_seconds"]
                entry["notes"] = pres.get("notes", None)
            else:
                entry["dosage_warning"] = (
                    "Exercise exists but no matching dosage for your age/BMI profile."
                )

            output.append(entry)

        return output



    # --------------------------------------------------------
    # FIND USER SPECIFIC PRESCRIPTION
    # --------------------------------------------------------
    def _find_prescription(self, user, ex):

        for p in ex["prescriptions"]:

            if p["age_group"] != user.age_group:
                continue

            if "All" in p["bmi_groups"]:
                return p

            if user.bmi_group in p["bmi_groups"]:
                return p

        return None



    # --------------------------------------------------------
    # BMI + SKILL WARNINGS
    # --------------------------------------------------------
    def _warning(self, user, goal):

        if goal == "POWER_HITTING":

            if user.bmi_group == "Underweight":
                return "⚠️ You are underweight — avoid heavy overload training."

            if user.skill_level == "beginner":
                return "⚠️ Start with controlled movement before heavy resistance."

        return ""
