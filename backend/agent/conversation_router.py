import re
import google.generativeai as genai
from .intent_agent import IntentAgent


class ConversationRouter:

    # (We no longer need strict word lists because the AI handles this now)
    
    def __init__(self, inference_engine, tech_engine, exercise_engine):
        self.inference = inference_engine
        self.tech = tech_engine
        self.exercise = exercise_engine
        
        # 🧠 ADDED: The AI Brain
        self.intent_agent = IntentAgent()
        self.chat_model = genai.GenerativeModel('gemini-3-flash-preview')
        self.rag = None
        self.sessions = {}  

    def process(self, user_id, user, text):
        msg = text.strip()

        # ==========================
        # 1. INIT MEMORY (Kept Exact)
        # ==========================
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                "last_area": None,
                "tech_last_category": None,
                "tech_last_area": None,
                "tech_drill_index": 0
            }
        memory = self.sessions[user_id]

        # ============================================================
        # 2. HANDLE "MORE" & CODES (Kept Exact - Fast Path)
        # ============================================================
        
        # Check for "more"
        if msg.lower() == "more" and memory["tech_last_area"]:
            result = self.tech.get_area_drills(memory["tech_last_area"], start=memory["tech_drill_index"], count=2)
            memory["tech_drill_index"] += 2
            return {
                "chat": f"More drills for {memory['tech_last_area']} 👇",
                "technical_drills": {
                    "returned": result["returned"],
                    "remaining": result["remaining"]
                }
            }

        # Check for Direct IDs (A1, B2)
        match = re.match(r"([a-zA-Z]\d+)", msg)
        if match:
            area_id = match.group(1).upper()
            result = self.tech.get_area_drills(area_id, start=0, count=2)
            memory["tech_last_area"] = area_id
            memory["tech_drill_index"] = 2
            return {
                "chat": f"Sure! Here are the drills for {area_id}.",
                "technical_drills": {
                    "returned": result["returned"],
                    "remaining": result["remaining"]
                }
            }
            
        # Check for Category IDs (A, B, C...)
        if msg.upper() in ["A","B","C","D","E","F","G","H","I"]:
            category = self.tech.get_category_by_id(msg.upper())
            if category:
                subareas = self.tech.get_sub_areas(category["category_name"])
                memory["tech_last_category"] = category["category_id"]
                memory["tech_last_area"] = None
                return {
                    "type": "technical_category",
                    "category_id": category["category_id"],
                    "category_name": category["category_name"],
                    "instruction": "Choose sub-area ID (ex: A2)",
                    "sub_areas": subareas
                }

        # ============================================================
        # 3. ASK THE AI BRAIN (This replaces the SPLIT_KEYS loop)
        # ============================================================
        # The AI fixes typos ("powet" -> "power") and tells us the INTENT.
        ai_data = self.intent_agent.classify_intent(msg)
        intent = ai_data.get("intent", "UNKNOWN")
        
        # 'part' is now the Cleaned Subject from AI (e.g. "power hitting")
        part = ai_data.get("subject", msg) 
        if not part: part = msg # Safety fallback

        rag_keywords = [
            "rule", "law", "umpire", "signal", "run", "boundary", "catch", "out", 
            "lbw", "wide", "no ball", "fielding", "restriction", "history", "won", 
            "cup", "trophy", "origin", "who is", "what is"
        ]
        
        # If brain is unsure, but we see cricket keywords, FORCE RAG check
        if intent == "UNKNOWN" or intent == "TECHNICAL_DRILL":
             if any(k in msg.lower() for k in rag_keywords):
                 # Only force if it's NOT a drill found by tech engine
                 if not self.tech.search_area_by_query(part):
                     print(f"⚠️ Forcing RAG lookup for: {msg}")
                     intent = "GENERAL_KNOWLEDGE"




        ordered_output = []

        # ============================================================
        # 4. ROUTE USING YOUR ORIGINAL LOGIC
        # ============================================================

        # --- CASE: EXERCISES ---
        if intent == "EXERCISE":
            result = self.exercise.get_batting_exercises(user, part)
            memory["last_exercise_goal"] = part.upper()
            ordered_output.append({
                "type": "exercise",
                "input": part,
                "result": result
            })
            return {"chat": f"Here is a plan for {part}:", "ordered_responses": ordered_output}

        # --- CASE: TECHNICAL DRILLS (Your Original Flow) ---
        if intent == "TECHNICAL_DRILL":
            
            # A. CATEGORY REQUEST (Moved here from your original code)
            cat = self.tech.find_category_from_query(part)
            if cat:
                sub_list = self.tech.get_sub_areas(cat["category_name"])
                memory["tech_last_category"] = cat["category_id"]
                memory["tech_last_area"] = None
                
                ordered_output.append({
                    "type": "technical_category",
                    "category": cat["category_name"],
                    "instruction": "Choose one sub-area using ID (e.g. A3)",
                    "sub_areas": sub_list
                })
                return {"chat": f"I found the **{cat['category_name']}** category.", "ordered_responses": ordered_output}

            # B. DIRECT TECHNIQUE (Moved here from your original code)
            area = self.tech.search_area_by_query(part)
            if area:
                ordered_output.append({
                    "type": "technical_direct",
                    "result": self.tech.format_area_output(area)
                })
                return {"chat": f"Specific drills for **{area['name']}**:", "ordered_responses": ordered_output}
            
            # C. ROLE BASED FALLBACK (Moved here from your original code)
            mapping = self.tech.recommend_technical_areas(user)
            if mapping["structured"]:
                ordered_output.append({
                    "type": "batting_role_priority",
                    "chat": f"As a **{user.playing_role}**, here is your roadmap:",
                    "priority": mapping["priority"],
                    "secondary": mapping["secondary"],
                    "low": mapping["low"]
                })
                return {"chat": "I couldn't find that exact drill, but here is your priority list:", "ordered_responses": ordered_output}

        # --- CASE: FUNDAMENTALS / SHOTS ---
        if intent in ["FUNDAMENTAL_INFO", "SHOT_INFO"]:
            # Try Shot detection first
            shot_key = self.inference._detect_shot(part)
            if shot_key:
                data = self.inference.process_query(part)
                ordered_output.append({ "type": "shot", "input": part, "result": data })
                return {"chat": "Here is the shot analysis:", "ordered_responses": ordered_output}
            
            # Try Fundamental detection
            fund = self.inference._detect_fundamental(part)
            if fund:
                ordered_output.append({
                    "type": "fundamental",
                    "result": self.inference._format_fundamental(self.inference.fundamentals[fund])
                })
                return {"chat": "Here is the fundamental info:", "ordered_responses": ordered_output}
            
            # Fallback for general questions
            data = self.inference.process_query(part)
            ordered_output.append({ "type": "fundamental", "result": data })
            return {"chat": "Here is what I found:", "ordered_responses": ordered_output}

        if intent == "GENERAL_KNOWLEDGE":
             
             # Check if RAG engine is connected
             if self.rag:
                 # 1. Search the Library
                 context = self.rag.search(part)
                 
                 if context:
                     # 2. Ask Gemini to Summarize
                     prompt = f"""
                     You are an expert Cricket Coach. Answer the question using ONLY the context below.
                     
                     CONTEXT FROM OFFICIAL BOOKS:
                     {context}
                     
                     USER QUESTION: {part}
                     
                     Keep the answer short, professional, and helpful.
                     """
                     try:
                         response = self.intent_agent.model.generate_content(prompt)
                         return { "chat": response.text }
                     except:
                         return { "chat": "I found the info in the books, but I'm having trouble summarizing it right now."}
                 else:
                     return { "chat": "Please ask Something Related to Cricket" }
             else:
                 return { "chat": "My library is currently offline. Please restart the system." }

        # --- CASE: UNKNOWN (Your Original Fallback) ---
        ordered_output.append({
            "type": "unknown",
            "input": part,
            "result": "Try something related to Cricket"
        })
        
        return {
            "chat": "I'm here to help!",
            "ordered_responses": ordered_output
        }