import json
import os

class TechEngine:

    def __init__(self):
        self.categories = self._load_data()

        # ===============================
        # CATEGORY KEYWORD ROUTING MAP
        # ===============================
        self.keyword_map = {

            # Category A – Decision & Ball Reading
            "decision": "A",
            "decision making": "A",
            "shot selection": "A",
            "innings building": "A",

            # Category B – Timing & Contact
            "timing": "B",
            "hand eye": "B",
            "late contact": "B",
            "middle bat": "B",

            # Category C – Footwork & Balance
            "footwork": "C",
            "front foot": "C",
            "back foot": "C",
            "trigger": "C",
            "balance": "C",

            # Category D – Pace / Swing / Short Ball
            "pace": "D",
            "fast bowling": "D",
            "swing": "D",
            "seam": "D",
            "short ball": "D",
            "bouncer": "D",

            # Category E – Spin Playing
            "spin": "E",
            "sweep": "E",
            "reverse sweep": "E",
            "slog sweep": "E",
            "offbreak": "E",
            "legbreak": "E",

            # Category F – Placement & Rotation
            "placement": "F",
            "rotation": "F",
            "strike rotation": "F",
            "singles": "F",

            # Category G – Running Between Wickets
            "running": "G",
            "between wickets": "G",
            "diving": "G",

            # Category H – Power & Finishing (Technical)
            "power hitting": "H",
            "finishing": "H",
            "death overs": "H",

            # Category I – Mental & Awareness
            "mental": "I",
            "mind": "I",
            "awareness": "I",
            "pressure": "I",
            "mindset": "I"
        }
            # ============================
    # ROLE PRIORITY TABLE
    # ============================

    ROLE_PRIORITY_MAP = {

        "top order batsman": {
            "priority":   ["A", "B", "C", "D"],
            "secondary":  ["F", "I"],
            "low":        ["E", "H", "G"]
        },

        "middle order batsman": {
            "priority":   ["E", "F", "I"],
            "secondary":  ["C", "B", "H"],
            "low":        ["A", "G", "D"]
        },

        "finisher": {
            "priority":   ["H", "F", "I"],
            "secondary":  ["B", "C"],
            "low":        ["D", "A", "E", "G"]
        },

        "all rounder": {
            "priority":   ["I", "B", "C"],
            "secondary":  ["E", "D", "F"],
            "low":        ["A", "H", "G"]
        },

        "wicket keeper batsman": {
            "priority":   ["B", "E", "F"],
            "secondary":  ["C", "I"],
            "low":        ["A", "D", "G", "H"]
        },

        # TAIL ENDERS GROUP
        "fast bowler": {
            "priority":   ["B", "F", "D"],
            "secondary":  ["C", "I"],
            "low":        ["A", "E", "H", "G"]
        },
        "medium bowler": {
            "priority":   ["B", "F", "D"],
            "secondary":  ["C", "I"],
            "low":        ["A", "E", "H", "G"]
        },
        "wrist spinner": {
            "priority":   ["B", "F", "D"],
            "secondary":  ["C", "I"],
            "low":        ["A", "E", "H", "G"]
        },
        "finger spinner": {
            "priority":   ["B", "F", "D"],
            "secondary":  ["C", "I"],
            "low":        ["A", "E", "H", "G"]
        }
    }


    def _load_data(self):
        base_path = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(base_path, "data", "technical", "technical_drills.json")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)["technical_categories"]


    # ---------------------------------------------------
    # KEYWORD → category object mapping
    # ---------------------------------------------------
    def keyword_to_category(self, text):

        text = text.lower()

        for key, cat_id in self.keyword_map.items():
            if key in text:
                return next((c for c in self.categories if c["category_id"] == cat_id), None)

        return None


    # ---------------------------------------------------
    # MAIN OUTPUT FUNCTION
    # ---------------------------------------------------
    def recommend_technical_areas(self, user):

        role = user.playing_role.lower()

        if role not in self.ROLE_PRIORITY_MAP:
            return {
                "priority": [],
                "secondary": [],
                "low": [],
                "structured": False
            }

        role_map = self.ROLE_PRIORITY_MAP[role]

        priority_ids   = role_map["priority"]
        secondary_ids  = role_map["secondary"]
        low_ids        = role_map["low"]

        # helper function to build lists
        def build(category_id_list):
            output = []

            for cid in category_id_list:
                for cat in self.categories:
                    if cat["category_id"] == cid:
                        output.append({
                            "category_id": cid,
                            "category_name": cat["category_name"]
                        })
            return output

        return {
            "priority": build(priority_ids),
            "secondary": build(secondary_ids),
            "low": build(low_ids),
            "structured": True
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
    # NATURAL SEARCH ENGINE (fallback)
    # ---------------------------------------------------
    def search_area_by_query(self, query: str):

        text = query.lower()

        stopwords = {
            "how","to","improve","fix","help","teach","train","practice",
            "get","the","my","in","on","for","batting","skills","area","i","want"
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
    # CATEGORY LOOKUP
    # ============================
    def find_category_from_query(self, text):

        text = text.lower()

        # 1️⃣ Keyword routing FIRST
        mapped = self.keyword_to_category(text)
        if mapped:
            return mapped

        # 2️⃣ Legacy text match
        for cat in self.categories:

            if cat["category_name"].lower() in text:
                return cat

            for word in cat["category_name"].lower().split():
                if word in text:
                    return cat

        return None
    
    def get_category_by_id(self, cat_id):
       for c in self.categories:
          if c["category_id"] == cat_id:
            return c
       return None



    # ============================
    # GET SUB AREAS BY CATEGORY
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
    # GET DRILLS PAGINATED
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
