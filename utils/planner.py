def plan(plan_steps):
    print("\n🛠️ EXECUTION PLAN")

    for step in plan_steps:
        action = step["action"]
        x = step["x"]
        z = step["z"]

        if action == "pick":
           print("🖐️ Picking up object")
           return True, x,3, z

        elif action == "place":
           print("📦 Placing object at target location")
           return False, x,3, z

        elif action == "give":
            print("🤝 Giving object to human")
            return False, 0,10, 15
        else:
            print(f"⚠️ Unknown action: {action}")


