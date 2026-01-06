import json
import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:3b"
MIN_CONFIDENCE = 0.6


class Memory:
    def __init__(self):
        self.holding = None

    def set_holding(self, obj_name):
        self.holding = obj_name

    def clear(self):
        self.holding = None


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


class LLM:
    def safe_json_parse(self, text):
        try:
            s = text.index("{")
            e = text.rindex("}") + 1
            return json.loads(text[s:e])
        except:
            return None

    def decide(self, text, objects, holding):
        prompt = f"""
Return ONLY valid JSON.
No explanation.

ROBOT STATE:
holding = {holding}

VISION OBJECTS:
{json.dumps(objects)}

USER COMMAND:
{text}

FORMAT:
{{
  "intent": "pick | place | stop | chat",
  "target": null | string,
  "reply": string
}}
"""
        r = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "stop": ["```", "\n\n"]
                }
            },
            timeout=60
        )

        raw = r.json().get("response", "")
        return self.safe_json_parse(raw)


class Brain:
    def __init__(self):
        self.memory = Memory()
        self.planner = Planner()
        self.llm = LLM()

    def deterministic_fallback(self, text):
        t = text.lower().strip()

        if t == "stop":
            return {"intent": "stop", "target": None, "reply": "Robot stopped."}

        if t.startswith("pick "):
            return {
                "intent": "pick",
                "target": t.split(" ", 1)[1],
                "reply": f"Picking {t.split(' ',1)[1]}"
            }

        if t.startswith("place"):
            return {"intent": "place", "target": None, "reply": "Placing object."}

        return None

    def process(self, user_text, vision):
        objects = vision.get("objects", [])

        decision = self.deterministic_fallback(user_text)
        if decision is None:
            decision = self.llm.decide(user_text, objects, self.memory.holding)

        if not decision:
            return {
                "intent": "chat",
                "reply": "I did not understand the command.",
                "plan": []
            }

        if decision["intent"] == "stop":
            return {
                "intent": "stop",
                "reply": "Robot stopped.",
                "plan": []
            }

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

        if decision["intent"] == "pick":
            if self.memory.holding:
                return {
                    "intent": "chat",
                    "reply": f"I am already holding {self.memory.holding}.",
                    "plan": []
                }

            obj = self.planner.find_object(decision["target"], objects)
            if not obj:
                return {
                    "intent": "chat",
                    "reply": f"I cannot see a {decision['target']}.",
                    "plan": []
                }

            self.memory.set_holding(obj["name"])

            return {
                "intent": "pick",
                "reply": decision["reply"],
                "plan": [self.planner.pick(obj)]
            }

        if "around" in user_text.lower():
            names = [o["name"] for o in objects]
            return {
                "intent": "chat",
                "reply": f"I can see: {', '.join(names)}.",
                "plan": []
            }

        return {
            "intent": "chat",
            "reply": decision.get("reply", ""),
            "plan": []
        }


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
        "pick bottle",
        "pick cup",
        "place it",
        "pick cup",
        "what is around me",
        "pick book",
        "stop"
    ]

    for cmd in tests:
        print("\nUSER:", cmd)
        print(json.dumps(brain.process(cmd, yolo_data), indent=2))
        time.sleep(1)
