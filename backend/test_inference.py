from agent.inference import CricketInferenceEngine

engine = CricketInferenceEngine()




tests = [
    "teach me pull shot",
    "how to play cover drive?",
"explain sweep shot",
"give drills for hook shot",
"teach straight drive technique",
"cut shot drills",
"show pull shot",
"shadow drill for drive shot"
,
   
]

for t in tests:
    print("\n============================")
    print("User asked:", t)
    print("----------------------------")
    print(engine.process_query(t))

