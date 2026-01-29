import config


class Planner:
    def find(self, name, objects, mode=None):
        candidates = [
            o for o in objects
            if o.get("name") == name and o.get("confidence", 0) >= config.MIN_CONFIDENCE
        ]
        if not candidates:
            return None
        if mode == "farthest":
            return max(candidates, key=lambda o: o.get("z_cm", 0))
        if mode == "nearest":
            return min(candidates, key=lambda o: o.get("z_cm", 0))
        return candidates[0]

    def pick(self, obj):
        return {
            "action": "pick",
            "object": obj["name"]
        }

    def place(self, x, z):
        return {
            "action": "place",
            "x": x,
            "z": z
        }

    def give(self):
        return {
            "action": "give"
        }

