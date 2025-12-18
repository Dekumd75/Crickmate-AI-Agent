from backend.agent.exercise_engine import ExerciseEngine
from backend.agent.user_profile import UserProfile

# Create sample user
user = UserProfile(
    age=15,
    height_cm=165,
    weight_kg=55,
    skill_level="intermediate",
    playing_role="middle order batsman",
)

engine = ExerciseEngine()

result = engine.get_batting_exercises(user, "power hitting")

print("\n--- TOP PERSONALISED EXERCISES ---\n")

for ex in result["top_recommendations"]:
    print(f"• {ex['exercise_name']}")
    print("  How to do:")
    for step in ex["how_to_do"]:
        print(f"   - {step}")
    print("  Benefits:")
    for b in ex["benefits"]:
        print(f"   - {b}")
    print(f"  Sets: {ex['sets']}")
    print(f"  Reps: {ex['reps']}")
    print(f"  Rest: {ex['rest_seconds']} seconds")
    if ex["notes"]:
        print(f"  Notes: {ex['notes']}")
    print("\n")

print("\n--- OTHER EXERCISE RECOMMENDATIONS ---")
for name in result["other_recommended_exercises"]:
    print(f"- {name}")

print("\n--- SAFETY WARNING ---")
print(result["safety_warning"])
