import json
import os
from .user_profile import UserProfile

class UserManager:

    def __init__(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        self.profile_path = os.path.join(base_path, "data", "user_profiles.json")

        if not os.path.exists(self.profile_path):
            with open(self.profile_path, "w") as f:
                json.dump({"users": []}, f)

    def _load_users(self):
        with open(self.profile_path, "r") as f:
            return json.load(f)

    def _save_users(self, data):
        with open(self.profile_path, "w") as f:
            json.dump(data, f, indent=4)

    def register_user(self, user_data):
        # validate base structure
        valid, msg = UserProfile.validate_inputs(user_data)
        if not valid:
            return False, msg

        # build new profile object
        user = UserProfile(**user_data)

        # create user_id
        users = self._load_users()
        new_id = "USER" + str(len(users["users"]) + 1).zfill(4)

        # store user
        users["users"].append({
            "user_id": new_id,
            "age": user.age,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "age_group": user.age_group,
            "bmi": user.bmi,
            "bmi_group": user.bmi_group,
            "skill_level": user.skill_level,
            "playing_role": user.playing_role,
            "weekly_days": user.weekly_days
        })

        self._save_users(users)

        return True, new_id

    def get_user(self, user_id):
        users = self._load_users()["users"]
        for u in users:
            if u["user_id"] == user_id:
                return True, u
        return False, "User not found"
