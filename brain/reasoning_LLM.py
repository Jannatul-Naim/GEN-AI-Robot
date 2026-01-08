import json
import requests
import time
import re

# ===================== CONFIG =====================
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b"
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
    def safe_json_parse(self, text):
        if not text:
            return None
        try:
            match = re.search(r"\{[\s\S]*\}", text)
            if not match:
                return None
            return json.loads(match.group(0))
        except Exception as e:
            print("[LLM JSON ERROR]:", e)
            print("[RAW OUTPUT]:", text)
            return None

    def decide(self, text, objects, holding):
        prompt = f"""
You are an embodied robotic reasoning system controlling a physical robot arm.

CORE PRINCIPLES:
- You exist in the real world
- You can only act on objects you can see
- Vision data is ground truth
- You cannot invent objects, actions, or locations
- Physics and robot state cannot be violated

ROBOT STATE:
- Currently holding: {holding}

VISIBLE OBJECTS (ground truth):
{json.dumps(objects, indent=2)}

TASK:
Interpret the human command and decide the robot's next intent.

REASONING RULES:
- If command asks to see, describe, confirm, or list objects → intent = "chat"
- Chat replies MUST only reference visible objects
- If requested object is visible → confirm it
- If not visible → say you cannot see it
- If robot is already holding something → picking is forbidden
- If placing while holding nothing → chat
- If command is impossible or ambiguous → chat
- If command is "stop" → stop immediately

INTENT DEFINITIONS:
- pick  : grasp a visible object
- place : release the currently held object onto the table
- stop  : immediately stop all actions
- chat  : respond verbally using ONLY visible objects

OUTPUT FORMAT (STRICT):
Return ONLY valid JSON.

{{
  "intent": "pick | place | stop | chat",
  "target": null | string,
  "reply": string
}}

HUMAN COMMAND:
{text}
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
                        "stop": ["```"]
                    }
                },
                timeout=LLM_TIMEOUT
            )
            raw = r.json().get("response", "")
            return self.safe_json_parse(raw)

        except requests.exceptions.RequestException as e:
            print("[LLM ERROR]:", e)
            return None

# ===================== BRAIN =====================
class Brain:
    def __init__(self):
        self.memory = Memory()
        self.planner = Planner()
        self.llm = LLM()

    def deterministic_fallback(self, text):
        t = text.lower().strip()
        if t == "stop":
            return {"intent": "stop", "target": None, "reply": "Stopping."}
        return None

    def process(self, user_text, vision):
        # Filter vision by confidence
        objects = [
            o for o in vision.get("objects", [])
            if o["confidence"] >= MIN_CONFIDENCE
        ]

        decision = self.llm.decide(user_text, objects, self.memory.holding)
        if decision is None:
            decision = self.deterministic_fallback(user_text)

        if not decision:
            return {
                "intent": "chat",
                "reply": "I did not understand the command.",
                "plan": []
            }

        # ================= STOP =================
        if decision["intent"] == "stop":
            return {
                "intent": "stop",
                "reply": "Robot stopped.",
                "plan": []
            }

        # ================= PLACE =================
        if decision["intent"] == "place":
            if not self.memory.holding:
                return {
                    "intent": "chat",
                    "reply": "I am not holding anything.",
                    "plan": []
                }

            released = self.memory.holding
            self.memory.clear()

            return {
                "intent": "place",
                "reply": f"Placed the {released}.",
                "plan": [self.planner.place()]
            }

        # ================= PICK =================
        if decision["intent"] == "pick":
            if self.memory.holding:
                return {
                    "intent": "chat",
                    "reply": f"I am already holding {self.memory.holding}.",
                    "plan": []
                }

            target = decision.get("target")
            if not target or target == "it":
                return {
                    "intent": "chat",
                    "reply": "Please specify which object to pick.",
                    "plan": []
                }

            obj = self.planner.find_object(target, objects)
            if not obj:
                return {
                    "intent": "chat",
                    "reply": f"I cannot see a {target}.",
                    "plan": []
                }

            # NOTE: memory should ideally update AFTER motion success
            self.memory.set_holding(obj["name"])

            return {
                "intent": "pick",
                "reply": decision["reply"],
                "plan": [self.planner.pick(obj)]
            }

        # ================= CHAT =================
        if decision["intent"] == "chat":
            # Safety: grounding enforcement
            tgt = decision.get("target")
            if tgt:
                names = {o["name"] for o in objects}
                if tgt not in names:
                    decision["reply"] = f"I cannot see a {tgt}."

            return {
                "intent": "chat",
                "reply": decision["reply"],
                "plan": []
            }

        return {
            "intent": "chat",
            "reply": "Unhandled command.",
            "plan": []
        }

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
