import re

class ConversationRouter:

    EXERCISE_WORDS = [
        "exercise", "exercises", "workout", "gym", "physical",
        "strength", "fitness", "stamina", "endurance"
    ]

    SPLIT_KEYS = [" and ", " & ", " plus ", " also ", " with ", ",", ";"]


    def __init__(self, inference_engine, tech_engine, exercise_engine):
        self.inference = inference_engine
        self.tech = tech_engine
        self.exercise = exercise_engine

        self.sessions = {}  


    def process(self, user_id, user, text):

        msg = text.lower().strip()

        # ==========================
        # INIT MEMORY
        # ==========================
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "last_area": None,
                "last_exercise_goal": None,
                "last_shot": None,
                "last_fundamental": None,
                "tech_last_category": None,
                "tech_last_area": None,
                "tech_drill_index": 0
            }

        memory = self.sessions[user_id]


        # ============================================================
        # FOLLOW UP PAGINATION ("more" drill request)
        # ============================================================
        if msg == "more" and memory["tech_last_area"]:

            area_id = memory["tech_last_area"]

            result = self.tech.get_area_drills(
                area_id=area_id,
                start=memory["tech_drill_index"],
                count=2
            )

            memory["tech_drill_index"] += 2

            return {
                "chat": f"More drills for {area_id} 👇",
                "technical_drills": {
                    "returned": result["returned"],
                    "remaining": result["remaining"]
                }
            }


        # ============================================================
        # MULTIPLE REQUEST SPLITTING
        # ============================================================
        segments = [msg]

        for key in self.SPLIT_KEYS:
            new_segments = []
            for seg in segments:
                if key in seg:
                    new_segments.extend(seg.split(key))
                else:
                    new_segments.append(seg)
            segments = [s.strip() for s in new_segments]


        ordered_output = []


        # ============================================================
        # PROCESS EACH INPUT PART
        # ============================================================
        for part in segments:


            # =====================================================
            # 0️⃣ EXERCISE DETECTION (UNCHANGED)
            # =====================================================
            if any(w in part for w in self.EXERCISE_WORDS):

                result = self.exercise.get_batting_exercises(user, part)

                memory["last_exercise_goal"] = part.upper()

                ordered_output.append({
                    "type": "exercise",
                    "input": part,
                    "result": result
                })
                continue


            # =====================================================
            # 1️⃣ SHOT SYSTEM (MOVED UP BEFORE TECH)
            # =====================================================
            shot_key = self.inference._detect_shot(part)

            if shot_key:
                data = self.inference.process_query(part)
                memory["last_shot"] = part

                ordered_output.append({
                    "type": "shot",
                    "input": part,
                    "result": data
                })
                continue


            # =====================================================
            # 2️⃣ FUNDAMENTALS (MOVED BEFORE TECH)
            # =====================================================
            fund = self.inference._detect_fundamental(part)

            if fund:
                memory["last_fundamental"] = fund

                ordered_output.append({
                    "type": "fundamental",
                    "result": self.inference._format_fundamental(
                        self.inference.fundamentals[fund]
                    )
                })
                continue


            # =====================================================
            # 3️⃣ CATEGORY REQUEST (timing/footwork/swing)
            # =====================================================
            cat = self.tech.find_category_from_query(part)

            if cat:

                sub_list = self.tech.get_sub_areas(cat["category_name"])

                memory["tech_last_category"] = cat["category_id"]
                memory["tech_last_area"] = None
                memory["tech_drill_index"] = 0

                ordered_output.append({
                    "type": "technical_category",
                    "category": cat["category_name"],
                    "instruction": "Choose one sub-area using ID (e.g. A3)",
                    "sub_areas": sub_list
                })
                continue


            # =====================================================
            # 4️⃣ SUB AREA → FIRST DRILLS
            # =====================================================
            match = re.match(r"([a-zA-Z]\d+)", part)
            if match:

                area_id = match.group(1).upper()

                result = self.tech.get_area_drills(area_id, start=0, count=2)

                memory["tech_last_area"] = area_id
                memory["tech_drill_index"] = 2

                ordered_output.append({
                    "type": "technical_drills",
                    "area_id": area_id,
                    "drills": result["returned"],
                    "remaining": result["remaining"],
                    "instruction": "Type 'more' to load next drills"
                })
                continue


            # =====================================================
            # 5️⃣ DIRECT TECHNIC
            # =====================================================
            area = self.tech.search_area_by_query(part)

            if area:
                ordered_output.append({
                    "type": "technical_direct",
                    "result": self.tech.format_area_output(area)
                })
                continue


            # =====================================================
            # 6️⃣ GENERAL IMPROVE BATTING
            # =====================================================
            if "improve" in part and "batting" in part:

                result = self.tech.recommend_technical_areas(user)

                ordered_output.append({
                    "type": "batting_overview",
                    "input": part,
                    "result": {
                        "top_recommendations": result["top_recommendations_full"],
                        "other_areas": result["other_area_names"]
                    }
                })
                continue


            # =====================================================
            # 7️⃣ UNKNOWN
            # =====================================================
            ordered_output.append({
                "type": "unknown",
                "input": part,
                "result": (
                    "Try:\n"
                    "- timing category\n"
                    "- A2 drills\n"
                    "- improve batting\n"
                    "- pull shot drills\n"
                    "- exercises for power"
                )
            })


        return {
            "chat": "Here is your requested information 👇",
            "ordered_responses": ordered_output
        }
