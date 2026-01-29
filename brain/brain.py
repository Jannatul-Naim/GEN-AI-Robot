from plan import Planner
from memory import RobotMemory
from llm import LLM


class Brain:
    def __init__(self):
        self.memory = RobotMemory()
        self.planner = Planner()
        self.llm = LLM()

    def process(self, cmd, vision):
        if self.memory.safety_state == "stop":
            return {"intent": "stop", "plan": [], "reply": "Stopped"}

        objects = vision.get("objects", [])
        decision = self.llm.decide(cmd, objects, self.memory.snapshot())

        if not decision:
            return {"intent": "chat", "plan": [], "reply": "I did not understand"}

        if decision["intent"] == "stop":
            self.memory.stop()
            return {"intent": "stop", "plan": [], "reply": "Stopping"}

        if decision["intent"] == "chat":
            return {"intent": "chat", "plan": [], "reply": decision.get("reply", "")}

        plan = []

        for step in decision.get("steps", []):
            if step["action"] == "pick":
                if self.memory.holding:
                    return {"intent": "chat", "plan": [], "reply": "Already holding"}
                obj = self.planner.find(
                    step.get("target"),
                    objects,
                    mode=step.get("mode")
                )
                if not obj:
                    return {"intent": "chat", "plan": [], "reply": "Object not visible"}
                plan.append(self.planner.pick(obj))
                self.memory.holding = obj["name"]

            elif step["action"] == "place":
                if not self.memory.holding:
                    return {"intent": "chat", "plan": [], "reply": "Nothing to place"}
                relation = step.get("relation")
                if relation == "left":
                    x = -10
                    z = 25
                elif relation == "right":
                    x = 10
                    z = 25
                else:
                    x = 0
                    z = 25
                plan.append(self.planner.place(x, z))
                self.memory.holding = None

            elif step["action"] == "give":
                if not self.memory.holding:
                    return {"intent": "chat", "plan": [], "reply": "Nothing to give"}
                plan.append(self.planner.give())
                self.memory.holding = None

        return {"intent": "task", "plan": plan, "reply": decision.get("reply", "")}
