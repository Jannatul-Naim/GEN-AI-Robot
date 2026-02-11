class Planner:
    def find(self, name, objects, mode=None):
        candidates = [o for o in objects if o.get("name") == name]
        if not candidates:
            return None
        if mode == "farthest":
            return max(candidates, key=lambda o: o.get("z_cm", 0))
        if mode == "nearest":
            return min(candidates, key=lambda o: o.get("z_cm", 0))
        return candidates[0]

    def resolve_relation(self, relation, reference, objects):
        ref = self.find(reference, objects)
        if not ref:
            return None
        rx = ref.get("x_cm", 0)
        rz = ref.get("z_cm", 25)
        if relation == "left":
            return rx - 10, rz
        if relation == "right":
            return rx + 10, rz
        if relation == "front":
            return rx, 25
        return rx, rz

    def pick(self, obj):
        return {
            "action": "pick",
            "x": obj.get("x_cm", 0),
            "z": obj.get("z_cm", 25)
        }

    def place(self, x, z):
        return {
            "action": "place",
            "x": x,
            "z": z
        }

    def give(self):
        return {"action": "give"}
