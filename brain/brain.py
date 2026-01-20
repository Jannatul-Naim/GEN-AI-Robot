import json
import requests
import re
from typing import Dict, List, Optional

# ===================== CONFIG =====================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"
LLM_TIMEOUT = 20
MIN_CONFIDENCE = 0.6
RUSSPARRY_URL = "http://10.221.100.204:9000/robot"


# ===================== MEMORY =====================

class RobotMemory:
    def __init__(self):
        self.holding = None
        self.last_command = None
        self.last_failed_action = None
        self.task_context = None
        self.user_preferences = {}
        self.safety_state = "normal"  # normal | stop | error

    def set_holding(self, obj):
        self.holding = obj

    def clear_holding(self):
        self.holding = None

    def set_last_command(self, cmd):
        self.last_command = cmd

    def set_failure(self, action):
        self.last_failed_action = action

    def clear_failure(self):
        self.last_failed_action = None

    def emergency_stop(self):
        self.safety_state = "stop"

    def reset_safety(self):
        self.safety_state = "normal"


# ===================== PLANNER =====================

class Planner:
    def find(self, name: str, objects: List[Dict]) -> Optional[Dict]:
        if not name:
            return None
        for o in objects:
            if o.get("name") == name and o.get("confidence", 0) >= MIN_CONFIDENCE:
                return o
        return None

    def _degree(self, obj):
        return obj["theta_deg"]

    def pick(self, o: Dict) -> Dict:
        return {
            "action": "pick",
            "object": o["name"],
            "grasp": {
                "z_cm": o.get("z_cm", 0),
                "degree": self._degree(o)
            }
        }

    def place_beside(self, ref: Dict) -> Dict:
        return {
            "action": "place",
            "target": "beside",
            "reference": {
                "name": ref["name"],
                "z_cm": ref.get("z_cm", 0),
                "degree": self._degree(ref)
            }
        }

    def give(self) -> Dict:
        return {"action": "give"}


# ===================== LLM =====================

class LLM:
    def parse(self, text: str) -> Optional[Dict]:
        try:
            m = re.search(r"\{[\s\S]*\}", text)
            return json.loads(m.group(0)) if m else None
        except:
            return None

    def build_prompt(self, command, objects, holding):
        return f"""
You are a robot action interpreter for a real physical robot arm.

CURRENT STATE:
Holding: {holding if holding else "nothing"}

VISIBLE OBJECTS:
{json.dumps(objects, indent=2)}

RULES:
- Use only visible objects
- Never invent objects
- One goal only
- One hand only
- If unsafe or unclear, intent=chat
- If object not visible, intent=chat
- No steps, no explanations
- Output JSON ONLY

INTENTS:
pick, place, give, chat, stop

OUTPUT FORMAT:
{{
  "intent": "pick|place|give|chat|stop",
  "target": null|string,
  "reference": null|string,
  "reply": string
}}

COMMAND:
{command}
"""

    def decide(self, command: str, objects: List[Dict], holding: Optional[str]) -> Optional[Dict]:
        try:
            r = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": self.build_prompt(command, objects, holding),
                    "stream": False,
                    "options": {"temperature": 0}
                },
                timeout=LLM_TIMEOUT
            )
            return self.parse(r.json().get("response", ""))
        except:
            return None


# ===================== BRAIN =====================

class Brain:
    def __init__(self):
        self.memory = RobotMemory()
        self.planner = Planner()
        self.llm = LLM()

    def process(self, text: str, vision: Dict) -> Dict:
        self.memory.set_last_command(text)

        if self.memory.safety_state == "stop":
            return {"intent": "stop", "reply": "Emergency stop active.", "plan": []}

        objects = vision.get("objects", [])
        decision = self.llm.decide(text, objects, self.memory.holding)

        if not decision:
            self.memory.set_failure("llm")
            return {"intent": "chat", "reply": "I did not understand.", "plan": []}

        self.memory.clear_failure()
        intent = decision["intent"]
        plan = []

        if intent == "stop":
            self.memory.emergency_stop()
            return {"intent": "stop", "reply": "Stopping robot.", "plan": []}

        if intent == "chat":
            return {"intent": "chat", "reply": decision.get("reply", ""), "plan": []}

        if intent == "give":
            if not self.memory.holding:
                obj = self.planner.find(decision["target"], objects)
                if not obj:
                    return {"intent": "chat", "reply": "I cannot see that.", "plan": []}
                plan.append(self.planner.pick(obj))
                self.memory.set_holding(obj["name"])
            plan.append(self.planner.give())
            self.memory.clear_holding()
            return {"intent": "give", "reply": decision["reply"], "plan": plan}

        if intent == "pick":
            if self.memory.holding:
                return {"intent": "chat", "reply": "I am already holding something.", "plan": []}
            obj = self.planner.find(decision["target"], objects)
            if not obj:
                return {"intent": "chat", "reply": "I cannot see that.", "plan": []}
            plan.append(self.planner.pick(obj))
            self.memory.set_holding(obj["name"])
            return {"intent": "pick", "reply": decision["reply"], "plan": plan}

        if intent == "place":
            if not self.memory.holding:
                obj = self.planner.find(decision["target"], objects)
                ref = self.planner.find(decision["reference"], objects)
                if not obj or not ref:
                    return {"intent": "chat", "reply": "Objects not visible.", "plan": []}
                plan.append(self.planner.pick(obj))
                self.memory.set_holding(obj["name"])
            ref = self.planner.find(decision["reference"], objects)
            if not ref:
                return {"intent": "chat", "reply": "Reference not visible.", "plan": []}
            plan.append(self.planner.place_beside(ref))
            self.memory.clear_holding()
            return {"intent": "place", "reply": decision["reply"], "plan": plan}

        return {"intent": "chat", "reply": "Command not executable.", "plan": []}


# ===================== RUSSPARRY =====================

def send_to_russparry(plan: List[Dict]):
    if not plan:
        return
    try:
        print("Sending to Russparry:", plan)
        requests.post(RUSSPARRY_URL, json={"plan": plan}, timeout=3)
    except:
        pass


# ===================== RUN =====================

if __name__ == "__main__":
    brain = Brain()

    vision_data = {
        "objects": [
            {"name": "bottle", "confidence": 0.67, "pixel": [527, 296], "theta_deg": 27.65, "z_cm": 63.85},
            {"name": "cup", "confidence": 0.74, "pixel": [310, 280], "theta_deg": 5.0, "z_cm": 62.0}
        ]
    }

    while True:
        cmd = input("USER> ")
        output = brain.process(cmd, vision_data)
        print("BRAIN OUTPUT:\n", json.dumps(output, indent=2))
        send_to_russparry(output["plan"])