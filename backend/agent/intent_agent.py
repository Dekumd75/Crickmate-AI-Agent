import google.generativeai as genai
import os
import json
import pickle
from dotenv import load_dotenv
import PIL.Image

load_dotenv()

class IntentAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("No GOOGLE_API_KEY found in .env file")
            
        genai.configure(api_key=api_key)
        
        # 1. Cloud AI (Gemini - for complex text & fallbacks)
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
        
        # 2. Vision Model (Gemini - for Camera Feature)
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')

        # 3. LOAD YOUR CUSTOM TRAINED MODULE 🧠
        # This satisfies the "Original AI Module" requirement
        try:
            # Look for the .pkl file in the same folder as this script
            model_path = os.path.join(os.path.dirname(__file__), 'custom_model.pkl')
            
            with open(model_path, 'rb') as f:
                self.local_classifier = pickle.load(f)
            print("✅ Custom ML Module Loaded Successfully! (System is now Hybrid)")
        except Exception as e:
            print(f"⚠️ Custom Model not found: {e}")
            print("Running in Cloud-Only mode.")
            self.local_classifier = None

    def classify_intent(self, message):
        """
        Hybrid Logic:
        1. Ask Local Custom Model (Fast, Free, Original)
        2. If unsure or model missing, ask Google Gemini (Smart, Slow)
        """
        
        # --- LAYER 1: YOUR CUSTOM BRAIN (Scikit-Learn) ---
        if self.local_classifier:
            try:
                # The model predicts the Label (e.g., "TECHNICAL_DRILL")
                prediction = self.local_classifier.predict([message])[0]
                
                # We trust our model! Return immediately.
                print(f"🤖 Local Brain Predicted: {prediction}")
                
                # Return standard format expected by the app
                return {"intent": prediction, "subject": message}
                
            except Exception as e:
                print(f"Local inference failed (falling back to cloud): {e}")

        # --- LAYER 2: CLOUD FALLBACK (Gemini) ---
        # This runs only if the Local Brain fails or isn't loaded
        system_prompt = """
        You are the 'Brain' of a Cricket Coaching App. 
        Analyze the user's query and return a JSON object with:
        - "intent": One of [TECHNICAL_DRILL, EXERCISE, FUNDAMENTAL_INFO, SHOT_INFO, GENERAL_KNOWLEDGE, CODE_INPUT]
        - "subject": The specific cricket topic, corrected for typos.
        
        EXAMPLES:
        - "improve batting" -> {"intent": "TECHNICAL_DRILL", "subject": "batting"}
        - "fitness plan" -> {"intent": "EXERCISE", "subject": "fitness"}
        - "how to play cover drive" -> {"intent": "SHOT_INFO", "subject": "cover drive"}
        """
        try:
            response = self.model.generate_content(f"{system_prompt}\nUser Query: {message}")
            return json.loads(response.text)
        except Exception as e:
            print(f"Cloud Agent Failed: {e}")
            return {"intent": "UNKNOWN", "subject": message}

    def analyze_cricket_image(self, image_file):
        """
        Vision Logic for the Camera Feature 📷
        """
        try:
            img = PIL.Image.open(image_file)
            prompt = """
            Act as an Expert Cricket Coach. Analyze this image.
            
            1. **Identify**: What shot or stance is shown?
            2. **Technique**: Comment on head position, feet, and balance.
            3. **Fixes**: If you see errors, suggest a specific drill.
            
            Format with emojis and clear headings. Keep it short (under 100 words).
            """
            response = self.vision_model.generate_content([prompt, img])
            return response.text
        except Exception as e:
            print(f"Vision Error: {e}")
            return "I couldn't analyze that image. Please try uploading a clearer cricket photo."