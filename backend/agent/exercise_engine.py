import json
import os

class ExerciseEngine:
    def __init__(self):
        self.exercises = self._load_batting_exercises()

    def _load_batting_exercises(self):
        # Robust path finding (works on Windows/Linux/Mac)
        base_path = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base_path, "data", "exercises", "batting_exercises.json")
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("batting_exercises", [])
        except Exception as e:
            print(f"Error loading exercises: {e}")
            return []

    def get_batting_exercises(self, user, query):
        """
        Main function to get sorted, filtered, and personalized exercises.
        """
        query = query.lower()
        
        # 1. DETECT GOALS (Allow multiple goals)
        target_goals = []
        if any(w in query for w in ["power", "strength", "hard", "six", "loft", "finish"]):
            target_goals.append("POWER_HITTING")
        if any(w in query for w in ["endurance", "stamina", "fitness", "run", "sprint"]):
            target_goals.append("ENDURANCE_FITNESS")
        if any(w in query for w in ["footwork", "agility", "speed", "move"]):
            target_goals.append("FOOTWORK_AGILITY")
        if any(w in query for w in ["timing", "control", "gap"]):
            target_goals.append("TIMING_CONTROL")
            
        # Default fallback
        if not target_goals:
            target_goals = ["ALL"]

        # 2. SCORE & FILTER
        scored_exercises = []
        
        for ex in self.exercises:
            score = 0
            
            # A. Goal Match (+5 points)
            if "ALL" in target_goals:
                score += 1
            elif any(g in ex["goals"] for g in target_goals):
                score += 5
            else:
                continue # Skip irrelevant exercises

            # B. Age Safety Check
            if user.age < ex.get("age_limit_min", 0):
                continue

            # C. Role Match (+2 points)
            # Check if user's role is in the priority list (case-insensitive)
            if user.playing_role.lower() in [r.lower() for r in ex.get("role_priority", [])]:
                score += 2
                
            # D. Get Personal Prescription (The "Smart" Calculation)
            prescription = self._calculate_prescription(user, ex.get("prescriptions", []))
            
            if prescription:
                scored_exercises.append({
                    "data": ex,
                    "score": score,
                    "prescription": prescription
                })

        # 3. SORT & LIMIT
        # Sort by score descending (Best match first)
        scored_exercises.sort(key=lambda x: x["score"], reverse=True)
        
        # Take Top 3
        top_picks = scored_exercises[:3]

        # 4. FORMAT FOR FRONTEND
        # Convert raw data into a clean "Card" format
        clean_results = []
        for item in top_picks:
            ex = item["data"]
            pres = item["prescription"]
            
            clean_results.append({
                "name": ex["name"],
                "goal": ", ".join([g.replace("_", " ").title() for g in ex["goals"]]),
                "your_plan": f"{pres['sets']} Sets x {pres['reps']}",
                "rest": f"{pres['rest_seconds']}s Rest",
                "key_benefit": ex["benefits"][0] if ex["benefits"] else "Improves Performance",
                "equipment": ex.get("equipment", "None")
            })

        return clean_results

    def _calculate_prescription(self, user, prescriptions_list):
        """
        Dynamically calculates Age Group and BMI Group to find the right row.
        """
        if not prescriptions_list:
            return None

        # 1. Calculate User Metrics
        # Handle cases where height might be missing or 0 to avoid crash
        h = (user.height_cm / 100) if user.height_cm else 1.75
        w = user.weight_kg if user.weight_kg else 70
        bmi = w / (h * h)

        bmi_category = "Athletic Ideal"
        if bmi < 18.5: bmi_category = "Underweight"
        elif bmi >= 25 and bmi < 30: bmi_category = "Overweight"
        elif bmi >= 30: bmi_category = "Obese"

        # 2. Find Best Age Group Match
        # We search specifically for the user's age bucket
        chosen_prescription = None
        
        # Priority 1: Exact Age Group Match (e.g., user is 16, find U17)
        for p in prescriptions_list:
            group = p["age_group"]
            is_age_match = False
            
            if group == "Adult" and user.age >= 20:
                is_age_match = True
            elif group.startswith("U"):
                # Extract number from "U15" -> 15
                try:
                    limit = int(group.replace("U", ""))
                    # Check if user fits in this bucket (e.g. 14 fits in U15)
                    # We assume the list is ordered or we pick the first valid upper bound
                    if user.age <= limit and user.age > (limit - 4): 
                        is_age_match = True
                except:
                    pass
            
            if is_age_match:
                # Priority 2: BMI Match within that age group
                if "All" in p["bmi_groups"] or bmi_category in p["bmi_groups"]:
                    return p # Perfect Match Found!
                
                # Soft Match: Age fits, but specific BMI not found (fallback to this if no better one)
                chosen_prescription = p

        # Fallback: If no age match found (e.g. data gap), take the first one or generic
        return chosen_prescription if chosen_prescription else prescriptions_list[0]