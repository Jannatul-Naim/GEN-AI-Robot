import json
import requests
import time

# ===================== CONFIG =====================
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b-instruct-q4_K_M"

MIN_CONFIDENCE = 0.6
LLM_TIMEOUT = 20

# ===================== MEMORY =====================
class Memory:
    def __init__(self):
        self.holding = None

    def set_holding(self, obj_name):
        self.holding = obj_name

    def clear(self):
        self.holding = None

# ===================== PLANNER =====================
class Planner:
    def find_object(self, name, objects):
        candidates = [
            o for o in objects
            if o["name"] == name and o["confidence"] >= MIN_CONFIDENCE
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda x: x["distance_cm"])

    def pick(self, obj):
        return {
            "action": "pick",
            "object": obj["name"],
            "grasp_center": obj["grasp_center"],
            "distance_cm": obj["distance_cm"]
        }

    def place(self):
        return {
            "action": "place",
            "target": "table",
            "place_pose": [0.45, 0.12, 0.0]
        }

# ===================== LLM =====================
class LLM:

    VALID_INTENTS = {"pick", "place", "stop", "chat"}

    def _extract_json(self, text):
        if not text:
            return None
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1:
                return None
            return json.loads(text[start:end + 1])
        except Exception:
            print("[BAD JSON]", text)
            return None

    def _sanitize(self, data):
        """
        Enforce strict schema and auto-repair common LLM failures.
        """
        if not isinstance(data, dict):
            return None

        intent = data.get("intent")
        reply = data.get("reply")
        target = data.get("target", None)

        if intent not in self.VALID_INTENTS:
            return None

        if not isinstance(reply, str):
            return None

        # Normalize empty target
        if target == "":
            target = None

        return {
            "intent": intent,
            "target": target,
            "reply": reply
        }

    def decide(self, user_text, objects, holding):
        prompt = f"""
You are a robotic decision engine controlling a REAL robot arm.

You must decide the robot intent using ONLY visible objects.

ROBOT STATE:
holding = {holding}

VISIBLE OBJECTS:
{json.dumps(objects, indent=2)}

INTENTS (choose exactly ONE):
- pick
- place
- stop
- chat

RULES:
- "see" or "what can you see" → chat
- "pick <object>" → pick IF visible AND holding is null
- "place" or "place it" → place IF holding is not null
- object not visible → chat
- "stop" → stop
- If unsure → chat

OUTPUT JSON ONLY (NO EXTRA TEXT):
{{"intent":"<intent>","target":null|string,"reply":"short clear sentence"}}

Command:
{user_text}
"""

        try:
            r = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0,
                        "top_k": 1,
                        "num_predict": 200
                    }
                },
                timeout=LLM_TIMEOUT
            )

            raw = r.json().get("response", "")
            print("[LLM RAW]:", raw)

            parsed = self._extract_json(raw)
            return self._sanitize(parsed)

        except Exception as e:
            print("[LLM ERROR]", e)
            return None

# ===================== BRAIN =====================
class Brain:
    def __init__(self):
        self.memory = Memory()
        self.planner = Planner()
        self.llm = LLM()

    def deterministic_fallback(self, text):
        t = text.strip().lower()
        if t == "stop":
            return {"intent": "stop", "target": None, "reply": "Stopping."}
        if t.startswith("pick"):
            return {"intent": "chat", "target": None, "reply": "Tell me which object to pick."}
        if "see" in t:
            return {"intent": "chat", "target": None, "reply": "I can see objects on the table."}
        return {"intent": "chat", "target": None, "reply": "Please give a clear command."}

    def process(self, user_text, vision):
        objects = [
            o for o in vision.get("objects", [])
            if o["confidence"] >= MIN_CONFIDENCE
        ]

        decision = self.llm.decide(user_text, objects, self.memory.holding)
        if decision is None:
            decision = self.deterministic_fallback(user_text)

        intent = decision["intent"]

        # STOP
        if intent == "stop":
            return {"intent": "stop", "reply": "Robot stopped.", "plan": []}

        # PLACE
        if intent == "place":
            if not self.memory.holding:
                return {"intent": "chat", "reply": "I am not holding anything.", "plan": []}

            released = self.memory.holding
            self.memory.clear()

            return {
                "intent": "place",
                "reply": f"Placed the {released}.",
                "plan": [self.planner.place()]
            }

        # PICK
        if intent == "pick":
            if self.memory.holding:
                return {
                    "intent": "chat",
                    "reply": f"I am already holding {self.memory.holding}.",
                    "plan": []
                }

            target = decision.get("target")
            if not target:
                return {"intent": "chat", "reply": "Specify the object to pick.", "plan": []}

            obj = self.planner.find_object(target, objects)
            if not obj:
                return {"intent": "chat", "reply": f"I cannot see a {target}.", "plan": []}

            self.memory.set_holding(obj["name"])

            return {
                "intent": "pick",
                "reply": decision["reply"],
                "plan": [self.planner.pick(obj)]
            }

        # CHAT
        return {"intent": "chat", "reply": decision["reply"], "plan": []}

# ===================== TEST =====================
if __name__ == "__main__":
    yolo_data = {
        "objects": [
            {
                "name": "bottle",
                "confidence": 0.72,
                "distance_cm": 29.4,
                "center": [476, 524],
                "grasp_center": [476, 544]
            },
            {
                "name": "cup",
                "confidence": 0.66,
                "distance_cm": 24.9,
                "center": [621, 590],
                "grasp_center": [621, 610]
            }
        ]
    }

    brain = Brain()

    tests = [
        "see the cup",
        "pick bottle",
        "pick cup",
        "place it",
        "what can you see",
        "pick book",
        "stop"
    ]

    for cmd in tests:
        print("\nUSER:", cmd)
        print(json.dumps(brain.process(cmd, yolo_data), indent=2))
        time.sleep(1)
