import json
import os

class UserProfile:
    def __init__(self, age, height_cm, weight_kg, skill_level, playing_role, weekly_days=None):
        self.age = age
        self.height_cm = height_cm
        self.weight_kg = weight_kg
        self.skill_level = skill_level
        self.playing_role = playing_role
        self.weekly_days = weekly_days

        self.age_group = self._compute_age_group()
        self.bmi = self._compute_bmi()
        self.bmi_group = self._compute_bmi_group()

    def _compute_age_group(self):
        if self.age <= 12:
            return "U13"
        elif self.age <= 14:
            return "U15"
        elif self.age <= 16:
            return "U17"
        elif self.age <= 18:
            return "U19"
        else:
            return "Adult"

    def _compute_bmi(self):
        height_m = self.height_cm / 100
        try:
            return round(self.weight_kg / (height_m ** 2), 2)
        except ZeroDivisionError:
            return None

    def _compute_bmi_group(self):
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 25:
            return "Athletic Ideal"
        elif self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    @staticmethod
    def validate_inputs(user_data):
        base_path = os.path.dirname(os.path.dirname(__file__))
        rules_path = os.path.join(base_path, "rules", "user_inputs.json")

        with open(rules_path, "r", encoding="utf-8") as f:
            rules = json.load(f)

        # check required fields
        for field in rules["required_fields"]:
            if field not in user_data:
                return False, f"Missing required field: {field}"

        # value validation
        for field, rule in rules["required_fields"].items():
            val = user_data[field]

            if rule["type"] == "int":
                if not isinstance(val, int):
                    return False, f"{field} must be an integer."
                if val < rule["min"] or val > rule["max"]:
                    return False, f"{field} outside valid range."

            if rule["type"] == "choice":
                if val not in rule["values"]:
                    return False, f"{field} not in valid value list."

        return True, "Valid Input"
