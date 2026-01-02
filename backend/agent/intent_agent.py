import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

class IntentAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("No GOOGLE_API_KEY found in .env file")
            
        genai.configure(api_key=api_key)
        
        # We use Gemini 2.5 Flash as confirmed by your test
        self.model = genai.GenerativeModel(
            model_name= 'gemini-3-flash-preview',
            generation_config={"response_mime_type": "application/json"}
        )

    def classify_intent(self, message):
        """
        1. Corrects typos (e.g. 'powet' -> 'power').
        2. Identifies the Intent (Drill, Shot, Exercise, Rule, etc.).
        3. Extracts the clean Cricket Topic as 'subject'.
        """
        system_prompt = """
        You are the 'Brain' of a Cricket Coaching App. 
        Analyze the user's query and return a JSON object with:
        - "intent": One of [TECHNICAL_DRILL, EXERCISE, FUNDAMENTAL_INFO, SHOT_INFO, GENERAL_KNOWLEDGE, CODE_INPUT]
        - "subject": The specific cricket topic, corrected for typos.

        GUIDELINES:
        1. **TECHNICAL_DRILL**: User wants to improve/practice a skill (e.g., "batting", "bowling", "fielding", "footwork", "timing").
        2. **EXERCISE**: User wants fitness/gym work (e.g., "strength", "stamina", "warm up").
        3. **FUNDAMENTAL_INFO**: User asks "what is" or "how to hold" (Definitions).
        4. **GENERAL_KNOWLEDGE**: History, rules, or player facts.
        5. **CODE_INPUT**: Short codes like "A1", "B2" or "more".
        6. **SHOT_INFO**: User asks "how to play" or about a specific shot (e.g., "how to play cut shot", "cover drive technique", "pull shot").

        EXAMPLES:
        - "improve powet hitting" -> {"intent": "TECHNICAL_DRILL", "subject": "power hitting"}
        - "drils for foot wrk" -> {"intent": "TECHNICAL_DRILL", "subject": "footwork"}
        - "batting drills" -> {"intent": "TECHNICAL_DRILL", "subject": "batting"}
        - "fitness for batting" -> {"intent": "EXERCISE", "subject": "batting fitness"}
        - "who is sachin?" -> {"intent": "GENERAL_KNOWLEDGE", "subject": "Sachin Tendulkar"}
        - "A2" -> {"intent": "CODE_INPUT", "subject": "A2"}
        - "how to play cut shot" -> {"intent": "SHOT_INFO", "subject": "cut shot"}
        - "drills for cut shot" -> {"intent": "SHOT_INFO", "subject": "cut shot"}

        Return ONLY raw JSON.
        """

        try:
            response = self.model.generate_content(f"{system_prompt}\nUser Query: {message}")
            return json.loads(response.text)

        except Exception as e:
            print(f"[ERROR] Intent Agent Failed: {e}")
            # Fallback: Just return the original message as the subject
            return {"intent": "UNKNOWN", "subject": message}