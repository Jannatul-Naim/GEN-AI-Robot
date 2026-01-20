import json
import requests
import re
from typing import Dict, List, Optional

# ===================== CONFIG =====================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b"
LLM_TIMEOUT = 20
MIN_CONFIDENCE = 0.6
RUSSPARRY_URL = "http://192.168.0.109:9000/robot"


# ===================== MEMORY =====================

class RobotMemory:
    def __init__(self):
        self.holding: Optional[str] = None
        self.last_command: Optional[str] = None
        self.last_failed_action: Optional[str] = None
        self.safety_state: str = "normal"  # normal | stop

    def snapshot(self) -> Dict:
        return {
            "holding": self.holding,
            "last_command": self.last_command,
            "last_failed_action": self.last_failed_action,
            "safety_state": self.safety_state
        }

    def emergency_stop(self):
        self.safety_state = "stop"

    def reset(self):
        self.holding = None
        self.last_failed_action = None
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

    def pick(self, obj: Dict) -> Dict:
        return {
            "action": "pick",
            "object": obj["name"],
            "grasp": {
                "z_cm": obj.get("z_cm", 0),
                "degree": obj.get("theta_deg", 0)
            }
        }

    def place_beside(self, ref: Dict) -> Dict:
        return {
            "action": "place",
            "target": "beside",
            "reference": {
                "name": ref["name"],
                "z_cm": ref.get("z_cm", 0),
                "degree": ref.get("theta_deg", 0)
            }
        }

    def give(self) -> Dict:
        return {"action": "give"}


# ===================== LLM =====================

class LLM:
    def _extract_json(self, text: str) -> Optional[Dict]:
        try:
            match = re.search(r"\{[\s\S]*\}", text)
            if not match:
                return None
            data = json.loads(match.group(0))
            data.setdefault("reply", "")
            data.setdefault("target", None)
            data.setdefault("reference", None)
            return data
        except Exception:
            return None

    def build_prompt(self, command: str, objects: List[Dict], memory: Dict) -> str:
        return f"""
You are a robot action interpreter for a REAL robot arm.
You must be STRICT and CONSERVATIVE.

ROBOT MEMORY:
{json.dumps(memory, indent=2)}

VISIBLE OBJECTS:
{json.dumps(objects, indent=2)}

RULES (ABSOLUTE):
- Use ONLY visible objects
- Never invent names
- One intent only
- One hand only
- If unclear or unsafe → intent=chat
- If object not visible → intent=chat
- If holding something and asked to pick → intent=chat
- Output JSON ONLY (no text)

VALID INTENTS:
pick, place, give, chat, stop

OUTPUT FORMAT:
{{
  "intent": "pick|place|give|chat|stop",
  "target": string|null,
  "reference": string|null,
  "reply": string
}}

USER COMMAND:
{command}
"""

    def decide(self, command: str, objects: List[Dict], memory: Dict) -> Optional[Dict]:
        try:
            r = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": self.build_prompt(command, objects, memory),
                    "stream": False,
                    "options": {"temperature": 0}
                },
                timeout=LLM_TIMEOUT
            )
            return self._extract_json(r.json().get("response", ""))
        except Exception:
            return None


# ===================== BRAIN =====================

class Brain:
    def __init__(self):
        self.memory = RobotMemory()
        self.planner = Planner()
        self.llm = LLM()

    def process(self, text: str, vision: Dict) -> Dict:
        self.memory.last_command = text

        if self.memory.safety_state == "stop":
            return {"intent": "stop", "reply": "Emergency stop active.", "plan": []}

        objects = vision.get("objects", [])
        decision = self.llm.decide(text, objects, self.memory.snapshot())

        if not decision:
            self.memory.last_failed_action = "llm_parse"
            return {"intent": "chat", "reply": "I did not understand.", "plan": []}

        intent = decision["intent"]
        plan: List[Dict] = []

        # ---------- STOP ----------
        if intent == "stop":
            self.memory.emergency_stop()
            return {"intent": "stop", "reply": "Stopping robot.", "plan": []}

        # ---------- CHAT ----------
        if intent == "chat":
            return {"intent": "chat", "reply": decision.get("reply", ""), "plan": []}

        # ---------- PICK ----------
        if intent == "pick":
            if self.memory.holding:
                return {"intent": "chat", "reply": "I am already holding something.", "plan": []}

            obj = self.planner.find(decision["target"], objects)
            if not obj:
                return {"intent": "chat", "reply": "I cannot see that.", "plan": []}

            plan.append(self.planner.pick(obj))
            self.memory.holding = obj["name"]

            return {"intent": "pick", "reply": decision.get("reply", ""), "plan": plan}

        # ---------- PLACE ----------
        if intent == "place":
            if not self.memory.holding:
                return {"intent": "chat", "reply": "I am not holding anything.", "plan": []}

            ref = self.planner.find(decision["reference"], objects)
            if not ref:
                return {"intent": "chat", "reply": "Reference not visible.", "plan": []}

            plan.append(self.planner.place_beside(ref))
            self.memory.holding = None

            return {"intent": "place", "reply": decision.get("reply", ""), "plan": plan}

        # ---------- GIVE ----------
        if intent == "give":
            if not self.memory.holding:
                return {"intent": "chat", "reply": "I am not holding anything.", "plan": []}

            plan.append(self.planner.give())
            self.memory.holding = None

            return {"intent": "give", "reply": decision.get("reply", ""), "plan": plan}

        return {"intent": "chat", "reply": "Command not executable.", "plan": []}


# ===================== RUSSPARRY =====================

def send_to_russparry(plan: List[Dict]):
    if not plan:
        return
    try:
        print("→ Sending to Russparry:", plan)
        requests.post(RUSSPARRY_URL, json={"plan": plan}, timeout=3)
    except Exception:
        print("⚠ Russparry not reachable")
