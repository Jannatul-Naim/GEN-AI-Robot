import json
import requests
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b"
LLM_TIMEOUT = 20
MIN_CONFIDENCE = 0.6
RUSSPARRY_URL = "http://192.168.0.109:9000/robot"


class Memory:
    def __init__(self):
        self.holding = None

    def pick(self, name):
        self.holding = name

    def clear(self):
        self.holding = None


class Planner:
    def find(self, name, objects):
        for o in objects:
            if o["name"] == name and o["confidence"] >= MIN_CONFIDENCE:
                return o
        return None

    def pick(self, o):
        return {
            "action": "pick",
            "object": o["name"],
            "grasp": {"z_cm": o["z_cm"], "degree": o["degree"]}
        }

    def place_beside(self, ref):
        return {
            "action": "place",
            "target": "beside",
            "reference": {
                "name": ref["name"],
                "z_cm": ref["z_cm"],
                "degree": ref["degree"]
            }
        }

    def give(self):
        return {"action": "give"}


class LLM:
    def parse(self, text):
        try:
            m = re.search(r"\{[\s\S]*\}", text)
            return json.loads(m.group(0)) if m else None
        except:
            return None

    def decide(self, command, objects, holding):
        prompt = f"""
You control a real robot arm.

STATE:
Holding: {holding}

VISIBLE OBJECTS:
{json.dumps(objects)}

RULES:
- One goal only
- Never invent objects
- No steps
- One hand only
- If impossible, chat

INTENTS:
pick, place, give, chat, stop

OUTPUT JSON ONLY:
{{
  "intent": "pick|place|give|chat|stop",
  "target": null|string,
  "reference": null|string,
  "reply": string
}}

COMMAND:
{command}
"""
        try:
            r = requests.post(
                OLLAMA_URL,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0}
                },
                timeout=LLM_TIMEOUT
            )
            return self.parse(r.json().get("response", ""))
        except:
            return None


class Brain:
    def __init__(self):
        self.memory = Memory()
        self.planner = Planner()
        self.llm = LLM()

    def process(self, text, vision):
        objects = vision.get("objects", [])
        d = self.llm.decide(text, objects, self.memory.holding)

        if not d:
            return {"intent": "chat", "reply": "I did not understand.", "plan": []}

        if any(w in text.lower() for w in ["both", "all", "everything"]):
            return {"intent": "chat", "reply": "I can only handle one object.", "plan": []}

        plan = []
        intent = d["intent"]

        if intent == "stop":
            return {"intent": "stop", "reply": "Stopped.", "plan": []}

        if intent == "chat":
            return {"intent": "chat", "reply": d["reply"], "plan": []}

        if intent == "give":
            if not self.memory.holding:
                obj = self.planner.find(d["target"], objects)
                if not obj:
                    return {"intent": "chat", "reply": "I cannot see that.", "plan": []}
                plan.append(self.planner.pick(obj))
                self.memory.pick(obj["name"])
            plan.append(self.planner.give())
            self.memory.clear()
            return {"intent": "give", "reply": d["reply"], "plan": plan}

        if intent == "pick":
            if self.memory.holding:
                return {"intent": "chat", "reply": "I am already holding something.", "plan": []}
            obj = self.planner.find(d["target"], objects)
            if not obj:
                return {"intent": "chat", "reply": "I cannot see that.", "plan": []}
            plan.append(self.planner.pick(obj))
            self.memory.pick(obj["name"])
            if "place" in text.lower():
                ref = self.planner.find(d["reference"], objects)
                if ref:
                    plan.append(self.planner.place_beside(ref))
                    self.memory.clear()
                    return {"intent": "pick_place", "reply": d["reply"], "plan": plan}
            return {"intent": "pick", "reply": d["reply"], "plan": plan}

        if intent == "place":
            if not self.memory.holding:
                obj = self.planner.find(d["target"], objects)
                ref = self.planner.find(d["reference"], objects)
                if not obj or not ref:
                    return {"intent": "chat", "reply": "Objects not visible.", "plan": []}
                plan.append(self.planner.pick(obj))
                self.memory.pick(obj["name"])
            ref = self.planner.find(d["reference"], objects)
            if not ref:
                return {"intent": "chat", "reply": "Reference not visible.", "plan": []}
            plan.append(self.planner.place_beside(ref))
            self.memory.clear()
            return {"intent": "place", "reply": d["reply"], "plan": plan}

        return {"intent": "chat", "reply": "Command not executable.", "plan": []}


def send_to_russparry(plan):
    if plan:
        try:
            print("Sending to Russparry:", plan)
            requests.post(RUSSPARRY_URL, json={"plan": plan}, timeout=3)
        except:
            pass


def test():
    vision = {
        "objects": [
            {"name": "cup", "z_cm": 12, "degree": 20, "confidence": 0.9},
            {"name": "bottle", "z_cm": 18, "degree": -5, "confidence": 0.95}
        ]
    }

    brain = Brain()
    cmds = [
        "pick the cup and place it beside the bottle",
        "give me the bottle",
        "stop"
    ]

    for c in cmds:
        r = brain.process(c, vision)
        # print(json.dumps(r, indent=2))
        send_to_russparry(r["plan"])


if __name__ == "__main__":
    test()
