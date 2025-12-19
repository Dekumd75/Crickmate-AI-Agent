import json
import os

class TechEngine:

    def __init__(self):
        self.categories = self._load_data()

    def _load_data(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base_path, "data", "technical", "technical_drills.json")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)["technical_categories"]

    # ---------------------------------------------------
    # MAIN OUTPUT FUNCTION
    # ---------------------------------------------------
    def recommend_technical_areas(self, user):

        flattened = []

        for cat in self.categories:
            for area in cat["areas"]:

                role_score = self._score(user.playing_role, area["role_priority"])

                flattened.append({
                    "area_id": area["area_id"],
                    "area_name": area["name"],
                    "category": cat["category_name"],
                    "description": area["description"],
                    "why_it_matters": area["why_it_matters"],
                    "drills": area["drills"],
                    "role_score": role_score
                })

        flattened.sort(key=lambda x: x["role_score"], reverse=True)

        top_three = []

        for area in flattened[:3]:

            full_drills = []

            for d in area["drills"]:
                full_drills.append({
                    "drill_name": d["name"],
                    "how_to": d["how_to"],
                    "equipment": d.get("equipment", "None"),
                    "coaching_points": d.get("coaching_points", []),
                    "mistakes": d.get("mistakes", []),
                    "reps_sets": d.get("reps_sets", ""),
                    "difficulty": d.get("difficulty", ""),
                    "safety": d.get("safety", "")
                })

            top_three.append({
                "area_name": area["area_name"],
                "category_name": area["category"],
                "description": area["description"],
                "why_it_matters": area["why_it_matters"],
                "drills": full_drills
            })

        other_area_names = [a["area_name"] for a in flattened[3:]]

        return {
            "top_recommendations_full": top_three,
            "other_area_names": other_area_names
        }

    # ---------------------------------------------------
    # PRIORITY SCORING SYSTEM
    # ---------------------------------------------------
    def _score(self, role, priority_map):

        if role not in priority_map:
            return 1

        val = priority_map[role]

        if val == "core":
            return 3
        elif val == "important":
            return 2
        elif val == "support":
            return 1
        else:
            return 1

    # ---------------------------------------------------
    # NATURAL SEARCH ENGINE
    # ---------------------------------------------------
    def search_area_by_query(self, query: str):

        text = query.lower()

        stopwords = {
            "how","to","improve","fix","help","teach","train","practice",
            "get","the","my","in","on","for","batting","skills","area"
        }

        cleaned_words = [w for w in text.split() if w not in stopwords]

        if len(cleaned_words) == 0:
            return None

        candidates = []

        for cat in self.categories:
            for area in cat["areas"]:

                area_name = area["name"].lower()

                if area_name in text:
                    candidates.append(area)
                    continue

                for word in cleaned_words:
                    if word in area_name:
                        candidates.append(area)
                        break

        if not candidates:
            return None

        candidates.sort(
            key=lambda a: 3 if a["role_priority"].get("top order batsman","")=="core" else 1,
            reverse=True
        )

        return candidates[0]

    # ---------------------------------------------------
    # FIXED function - details lookup by name
    # ---------------------------------------------------
    def get_area_details_by_name(self, name):

        for cat in self.categories:
            for area in cat["areas"]:
                if area["name"].lower() == name.lower():
                    return self.format_area_output(area)

        return None

    # ---------------------------------------------------
    # FORMAT ALL DETAILS FROM JSON
    # ---------------------------------------------------
    def format_area_output(self, area):

        drills_output = []

        for d in area["drills"]:

            drills_output.append({
                "drill_name": d["name"],
                "how_to": d["how_to"],
                "equipment": d.get("equipment", ""),
                "coaching_points": d.get("coaching_points", []),
                "mistakes": d.get("mistakes", []),
                "reps_sets": d.get("reps_sets", ""),
                "difficulty": d.get("difficulty", ""),
                "safety": d.get("safety", "")
            })

        return {
            "area_name": area["name"],
            "description": area["description"],
            "why_it_matters": area["why_it_matters"],
            "drills": drills_output
        }


        # ============================
    # NEW: CATEGORY LOOKUP
    # ============================
    def find_category_from_query(self, text):

        text = text.lower()

        for cat in self.categories:

            # full match
            if cat["category_name"].lower() in text:
                return cat

            # partial match
            for word in cat["category_name"].lower().split():
                if word in text:
                    return cat

        return None


    # ============================
    # NEW: GET SUB AREAS BY CATEGORY
    # ============================
    def get_sub_areas(self, category_name):

        for cat in self.categories:
            if cat["category_name"].lower() == category_name.lower():

                return [
                    {
                        "area_id": a["area_id"],
                        "name": a["name"],
                        "description": a["description"]
                    }
                    for a in cat["areas"]
                ]

        return []


    # ============================
    # NEW: GET DRILLS PAGINATED
    # ============================
    def get_area_drills(self, area_id, start=0, count=2):

        for cat in self.categories:
            for area in cat["areas"]:

                if area["area_id"] == area_id:

                    drills = area["drills"]

                    sliced = drills[start:start+count]

                    formatted = []

                    for d in sliced:
                        formatted.append({
                            "drill_name": d["name"],
                            "how_to": d["how_to"],
                            "equipment": d.get("equipment", ""),
                            "coaching_points": d.get("coaching_points", []),
                            "mistakes": d.get("mistakes", []),
                            "reps_sets": d.get("reps_sets", ""),
                            "difficulty": d.get("difficulty", ""),
                            "safety": d.get("safety", "")
                        })

                    return {
                        "returned": formatted,
                        "total": len(drills),
                        "remaining": max(0, len(drills) - (start + count))
                    }

        return {"returned": [], "total": 0, "remaining": 0}
