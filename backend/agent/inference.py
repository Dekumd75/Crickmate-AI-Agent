import json
import os


class CricketInferenceEngine:
    def __init__(self):
        self.shots_data = self._load_shots_data()
        self.fundamentals = self._load_fundamentals_data()
        self.roadmap = self._load_roadmap_data()

    def _load_shots_data(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        shots_path = os.path.join(base_path, "rules", "shots.json")

        with open(shots_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _load_fundamentals_data(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        f_path = os.path.join(base_path, "rules", "fundamentals.json")

        with open(f_path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def _load_roadmap_data(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        r_path = os.path.join(base_path, "rules", "roadmap.json")

        with open(r_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def process_query(self, user_query: str):
        
        query = user_query.lower()
        if self._detect_roadmap(query):
           return self._format_roadmap()

        # Detect fundamentals first
        fund_key = self._detect_fundamental(query)
        
        if fund_key:
            return self._format_fundamental(self.fundamentals[fund_key])

        # Shot processing
        intent = self._detect_intent(query)
        shot_key = self._detect_shot(query)

        if not shot_key:
            return "Sorry, I couldn't identify the shot you are asking about."

        shot = self.shots_data.get(shot_key)

        if not shot:
            return "Sorry, I don't have information about that shot yet."

        if intent == "DRILLS_ONLY":
            return self._format_drills_only(shot)

        return self._format_full_explanation(shot)

    def _detect_intent(self, query: str):
        drill_keywords = ["drill", "practice", "improve", "training"]

        for word in drill_keywords:
            if word in query:
                return "DRILLS_ONLY"

        return "FULL_EXPLANATION"

    def _detect_shot(self, query: str):
        shot_keywords = {
            "forward defence": "FORWARD_DEFENCE",
            "forward defense": "FORWARD_DEFENCE",
            "cut": "CUT_SHOT",
            "cut shot": "CUT_SHOT",
            "pull": "PULL_SHOT",
            "pull shot": "PULL_SHOT"
        }

        for keyword, shot_key in shot_keywords.items():
            if keyword in query:
                return shot_key

        return None

    def _detect_fundamental(self, query: str):
        for key, info in self.fundamentals.items():
            for kw in info["keywords"]:
                if kw in query:
                    return key
        return None
    
    def _detect_roadmap(self, query: str):
        data = self.roadmap["roadmap_beginner"]

        for kw in data["trigger_keywords"]:
                if kw in query:
                    return True

        return False

    
    def _format_full_explanation(self, shot):
        response = []
        response.append(f"🏏 {shot['name']}")
        response.append(f"\nPlayed to: {shot['played_to_length']}")
        response.append(f"\n{shot['description']}\n")

        response.append("🔹 How to play:")
        for step in shot["technique"]["steps"]:
            response.append(f"- {step}")

        response.append("\n🔹 Key coaching points:")
        for point in shot["technique"]["key_points"]:
            response.append(f"- {point}")

        response.append("\n❌ Common mistakes:")
        for mistake in shot["technique"]["common_mistakes"]:
            response.append(f"- {mistake}")

        return "\n".join(response)

    def _format_drills_only(self, shot):
        response = []
        response.append(f"🧪 Drills for {shot['name']}:\n")

        for drill in shot["drills"]:
            response.append(f"➡ {drill['name']}")
            for step in drill["how_to"]:
                response.append(f"  - {step}")
            response.append(f"  Reps/Sets: {drill['reps_sets']}")
            response.append(f"  Safety: {drill['safety']}\n")

        return "\n".join(response)

    def _format_fundamental(self, item):
        response = []
        response.append(f"🏏 {item['title']}\n")

        response.append("📌 What it is:")
        response.append(f"- {item['what']}\n")

        response.append("📝 How to do it:")
        for step in item["how_to"]:
            response.append(f"- {step}")

        response.append("\n❌ Common mistakes:")
        for m in item["mistakes"]:
            response.append(f"- {m}")

        response.append("\n🎯 Why it matters:")
        response.append(f"- {item['why_it_matters']}\n")

        response.append("🧪 Drills:")
        for d in item["drills"]:
            response.append(f"- {d}")

        return "\n".join(response)
    
    def _format_roadmap(self):
        data = self.roadmap["roadmap_beginner"]
        response = []

        response.append("🏏 Beginner Cricket Roadmap\n")

        response.append("📌 Batting Fundamentals:")
        for x in data["batting"]:
            response.append(f"- {x}")

        response.append("\n📌 Bowling Fundamentals:")
        for x in data["bowling"]:
            response.append(f"- {x}")

        response.append("\n📌 Fielding Fundamentals:")
        for x in data["fielding"]:
           response.append(f"- {x}")

        response.append("\n📌 Fitness Fundamentals:")
        for x in data["fitness"]:
         response.append(f"- {x}")

        return "\n".join(response)

