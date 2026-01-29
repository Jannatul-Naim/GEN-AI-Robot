import json
import requests
import re
from typing import Dict, List, Optional

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gpt-oss:120b-cloud"
LLM_TIMEOUT = 250
MIN_CONFIDENCE = 0.6
RUSSPARRY_URL = "http://10.237.216.204:9000/robot"


class RobotMemory:
    def __init__(self):
        self.holding = None
        self.safety_state = "normal"

    def snapshot(self):
        return {
            "holding": self.holding,
            "safety_state": self.safety_state
        }

    def stop(self):
        self.safety_state = "stop"

    def reset(self):
        self.holding = None
        self.safety_state = "normal"


class Planner:
    def find(self, name, objects, mode=None):
        candidates = [
            o for o in objects
            if o.get("name") == name and o.get("confidence", 0) >= MIN_CONFIDENCE
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


class LLM:
    def extract(self, text):
        try:
            m = re.search(r"\{[\s\S]*\}", text)
            if not m:
                return None
            return json.loads(m.group(0))
        except:
            return None

    def prompt(self, cmd, objects, memory):
        return f"""
You control a REAL robot arm.

X AXIS:
negative = left
positive = right

Z AXIS:
front = 25

RULES:
- Use only visible objects
- Never invent objects
- Max 2 steps
- If unsafe or unclear -> chat
- If multiple objects exist, resolve far / nearest
- If place without reference -> place front (z=25)
- Output JSON ONLY

VISIBLE OBJECTS:
{json.dumps(objects)}

MEMORY:
{json.dumps(memory)}

FORMAT:
{{
  "intent": "task|chat|stop",
  "steps": [
    {{
      "action": "pick|place|give",
      "target": string|null,
      "mode": "farthest|nearest|null",
      "relation": "left|right|front|null",
      "reference": string|null
    }}
  ],
  "reply": "short"
}}

COMMAND:
{cmd}
"""

    def decide(self, cmd, objects, memory):
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": self.prompt(cmd, objects, memory),
                "stream": False,
                "options": {"temperature": 0}
            },
            timeout=LLM_TIMEOUT
        )
        return self.extract(r.json().get("response", ""))


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


def send_to_russparry(plan):
    if not plan:
        return
    print(json.dumps({"plan": plan}, indent=2))
    try:
        requests.post(
            RUSSPARRY_URL,
            json={"plan": plan},
            timeout=30
        )
    except requests.exceptions.ConnectTimeout:
        print("❌ Russparry timeout: server unreachable")
    except requests.exceptions.ConnectionError:
        print("❌ Russparry connection error")

