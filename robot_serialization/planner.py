def execute_plan(plan):
    results = []

    for step in plan:
        action = step.get("action")

        if action == "pick":
            z, theta = handle_pick(step)
            results.append({
                "action": "pick",
                "z_cm": z,
                "degree": theta
            })

        elif action == "place":
            z, theta = handle_place(step)
            results.append({
                "action": "place",
                "z_cm": z,
                "degree": theta
            })
        
        elif action == "give":
            results.append({
                "action": "give"
            })

        else:
            raise ValueError(f"Unknown action: {action}")

    return results

def handle_pick(step):
    obj = step.get("object")
    grasp = step.get("grasp", {})

    if not obj:
        raise ValueError("Pick action missing object")

    return grasp.get("z_cm", 0), grasp.get("degree", 0)


def handle_place(step):
    target = step.get("target")
    ref = step.get("reference", {})

    if not target or "name" not in ref:
        raise ValueError("Place action missing target or reference")

    return ref.get("z_cm", 0), ref.get("degree", 0)




 

def test():
    data = [
    {
        "action": "pick",
        "object": "cup",
        "grasp": {"z_cm": 12, "degree": 20}
    },
    {
        "action": "place",
        "target": "beside",
        "reference": {"name": "bottle", "z_cm": 18, "degree": -5}
    }

]
    print(execute_plan(data))
if __name__ == "__main__":
    test()