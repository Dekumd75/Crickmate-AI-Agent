import json
import os

class ExerciseEngine:

    def __init__(self):
        self.exercises = self._load_batting_exercises()

    def _load_batting_exercises(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base_path, "data", "exercises", "batting_exercises.json")

        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data["batting_exercises"]

    # -------------------------------------------------------
    # MAIN CALL
    # -------------------------------------------------------
    def get_batting_exercises(self, user, goal):
        
        goal = goal.upper().replace(" ", "_")

        # Get all exercises matching goal
        goal_matches = [ex for ex in self.exercises if goal in ex["goals"] or "ALL" in ex["goals"]]

        if not goal_matches:
            return {"error": "No exercises found for this goal."}

        # personalised first 3
        personalised = self._personalised_section(user, goal_matches)

        # remaining exercises as simple names
        remaining = self._recommended_section(goal_matches, personalised)

        # warnings
        warning = self._warning(user, goal)

        return {
            "goal": goal,
            "top_recommendations": personalised,
            "other_recommended_exercises": remaining,
            "safety_warning": warning
        }

    # -------------------------------------------------------
    # 1️⃣ PERSONAL EXERCISE FILTER
    # -------------------------------------------------------
    def _personalised_section(self, user, exercises):

        selected = []

        for ex in exercises:

            if "age_limit_min" in ex and user.age < ex["age_limit_min"]:
                continue

            if user.playing_role not in ex["role_priority"]:
                continue

            p = self._find_prescription(user, ex)
            if not p:
                continue

            selected.append({
                "exercise_name": ex["name"],
                "how_to_do": ex["how_to"],
                "benefits": ex["benefits"],
                "sets": p["sets"],
                "reps": p["reps"],
                "rest_seconds": p["rest_seconds"],
                "notes": p.get("notes", "")
            })

        return selected[:3] if selected else []

    # -------------------------------------------------------
    # 2️⃣ REMAINING EXERCISE NAMES
    # -------------------------------------------------------
    def _recommended_section(self, full_list, personalised):

        used = [e["exercise_name"] for e in personalised]

        names = [ex["name"] for ex in full_list if ex["name"] not in used]

        return names[:10]

    # -------------------------------------------------------
    # 3️⃣ PRESCRIPTION PICKER
    # -------------------------------------------------------
    def _find_prescription(self, user, ex):

        for p in ex["prescriptions"]:

            if p["age_group"] != user.age_group:
                continue

            if "All" in p["bmi_groups"]:
                return p

            if user.bmi_group in p["bmi_groups"]:
                return p

        return None

    # -------------------------------------------------------
    # 4️⃣ WARNINGS SECTION (ONLY WHEN NEEDED)
    # -------------------------------------------------------
    def _warning(self, user, goal):

        if goal == "POWER_HITTING":

            if user.bmi_group == "Underweight":
                return "You are underweight — avoid heavy resistance and focus on technique."

            if user.skill_level == "beginner":
                return "You are a beginner — start with lighter controlled training."

        return ""
    
    def get_exercise_details(self, user, exercise_name):

        # find exercise by name
        ex = next((e for e in self.exercises if e["name"].lower() == exercise_name.lower()), None)

        if not ex:
            return {"error": "Exercise not found"}

        # find correct prescription for user
        prescription = self._find_prescription(user, ex)

        details = {
            "exercise_name": ex["name"],
            "type": ex["type"],
            "equipment": ex["equipment"],
            "benefits": ex["benefits"],
            "how_to": ex["how_to"],
            "safety_notes": ex["safety_notes"],
            "age_limit_min": ex.get("age_limit_min", None),
            "role_recommended": user.playing_role in ex["role_priority"]
        }

        # add personalised dosage if possible
        if prescription:
            details["sets"] = prescription["sets"]
            details["reps"] = prescription["reps"]
            details["rest_seconds"] = prescription["rest_seconds"]
            details["notes"] = prescription.get("notes", "")
        else:
            details["warning"] = "Exercise exists but no matching dosage for your profile."

        return details
