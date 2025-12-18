from agent.inference import CricketInferenceEngine

engine = CricketInferenceEngine()


print("\n---- Test stance ----\n")
print(engine.process_query("bowling grip"))
