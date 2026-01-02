import sys
import os
from dotenv import load_dotenv

# 1. Setup paths correctly to find the 'agent' folder
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 2. Point to the .env file (one folder up)
project_root = os.path.dirname(current_dir)
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

# 3. Import the Agent
try:
    from agent.intent_agent import IntentAgent
except ImportError:
    # Fallback if running from root
    sys.path.append(os.path.join(current_dir, 'backend'))
    from agent.intent_agent import IntentAgent

print(f"📂 Project Root: {project_root}")
key = os.getenv("GOOGLE_API_KEY")
print(f"🔑 API Key: {key[:5]}...{key[-5:] if key else 'NONE'}")

# 4. Run the Test
try:
    print("🧠 Initializing Intent Agent...")
    agent = IntentAgent()
    
    query = "power hitting drills"
    print(f"📨 Sending Query: '{query}'")
    
    result = agent.classify_intent(query)
    
    print("\n✅ SUCCESS! The Brain is working:")
    print(result)

except Exception as e:
    print("\n❌ FAILURE! Error details:")
    print(e)