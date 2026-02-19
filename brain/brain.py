from .plan import Planner
from .memory import RobotMemory
from .llm import LLM


class Brain:
    def __init__(self):
        self.memory = RobotMemory()
        self.planner = Planner()
        self.llm = LLM()

    def process(self, cmd, vision):
        if self.memory.safety_state == "stop":
            return {"intent": "stop", "plan": [], "reply": "Stopped"}

        objects = vision.get("objects", [])
        self.memory.update_scene(objects)

        decision = self.llm.decide(cmd, objects, self.memory.snapshot())

        if not isinstance(decision, dict):
            return {"intent": "chat", "plan": [], "reply": "I did not understand"}

        intent = decision.get("intent")
        if intent not in ("task", "chat", "stop"):
            return {"intent": "chat", "plan": [], "reply": "I did not understand"}

        if intent == "stop":
            self.memory.stop()
            return {"intent": "stop", "plan": [], "reply": "Stopping"}

        if intent == "chat":
            return {"intent": "chat", "plan": [], "reply": decision.get("reply", "")}

        plan = []

        for step in decision.get("steps", []):
            action = step.get("action")

            if action == "pick":
                if self.memory.holding:
                    return {"intent": "chat", "plan": [], "reply": "Already holding"}
                obj = self.planner.find(step.get("target"), objects, mode=step.get("mode"))
                if not obj:
                    return {"intent": "chat", "plan": [], "reply": "Object not visible"}
                plan.append(self.planner.pick(obj))
                self.memory.holding = obj["name"]

            elif action == "place":
                if not self.memory.holding:
                    return {"intent": "chat", "plan": [], "reply": "Nothing to place"}
                relation = step.get("relation")
                reference = step.get("reference")
                if relation and reference:
                    pos = self.planner.resolve_relation(relation, reference, objects)
                    if not pos:
                        return {"intent": "chat", "plan": [], "reply": "Reference object not visible"}
                    x, z = pos
                else:
                    x, z = 0, 25
                plan.append(self.planner.place(x, z))
                self.memory.holding = None

            elif action == "give":
                if not self.memory.holding:
                    return {"intent": "chat", "plan": [], "reply": "Nothing to give"}
                plan.append(self.planner.give())
                self.memory.holding = None

        self.memory.update_plan(plan, cmd)
        return {"intent": "task", "plan": plan, "reply": decision.get("reply", "")}

