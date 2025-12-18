from agent.tech_engine import TechEngine
from agent.user_profile import UserProfile

engine = TechEngine()

user = UserProfile(
    age=18,
    height_cm=175,
    weight_kg=68,
    skill_level="intermediate",
    playing_role="top order batsman"
)

result = engine.recommend_technical_areas(user)

print("----- TOP TECHNICAL AREAS -----\n")
for item in result["top_recommendations_full"]:
    print(item["area_name"])
    print(item["description"])
    print("Drills:")
    for d in item["drills"]:
        print("  -", d["drill_name"])
    print("\n")

print("----- OTHER AREAS -----\n")
for name in result["other_area_names"]:
    print("-", name)
