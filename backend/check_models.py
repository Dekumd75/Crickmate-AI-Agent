import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Load the API Key from your .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found. Please check your .env file.")
else:
    print(f"✅ API Key found! Checking available models...\n")
    
    # 2. Configure the library
    genai.configure(api_key=api_key)

    # 3. List all models that support 'generateContent' (Chat)
    try:
        print("--- Available Models ---")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model ID: {m.name}")
                print(f"Name:     {m.display_name}")
                print("------------------------")
    except Exception as e:
        print(f"❌ Error connecting to Google: {e}")