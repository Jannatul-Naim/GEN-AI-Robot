import json
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# ===================== CONFIG =====================
MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
MIN_CONFIDENCE = 0.6
MAX_NEW_TOKENS = 120
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ===================== LOAD MODEL =====================
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto"
)
model.eval()

# ===================== MEMORY =====================
class Memory:
    def __init__(self):
        self.holding = None

    def set(self, obj):
        self.holding = obj

    def clear(self):
        self.holding = None

# ===================== PLANNER =====================
class Planner:
    def find_object(self, name, objects):
        objs = [
            o for o in objects
            if o["name"] == name and o["confidence"] >= MIN_CONFIDENCE
        ]
        if not objs:
            return None
        return min(objs, key=lambda x: x["distance_cm"])

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
    def _extract_json(self, text):
        m = re.search(r"\{[\s\S]*\}", text)
        return json.loads(m.group(0)) if m else None

    @torch.inference_mode()
    def decide(self, command, objects, holding):
        prompt = f"""
You are a robotic control AI.

RULES:
- Only use visible objects
- Never invent objects
- If holding something, you cannot pick
- If placing with empty hand → chat
- Output JSON only

ROBOT STATE:
Holding: {holding}

VISIBLE OBJECTS:
{json.dumps(objects, indent=2)}

COMMAND:
{command}

OUTPUT JSON:
{{
  "intent": "pick | place | stop | chat",
  "target": null | string,
  "reply": string
}}
"""
        inputs = tokenizer(prompt, return_tensors="pt").to(DEVICE)
        out = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=0.0,
            do_sample=False
        )
        text = tokenizer.decode(out[0], skip_special_tokens=True)
        return self._extract_json(text)

# ===================== BRAIN =====================
class Brain:
    def __init__(self):
        self.memory = Memory()
        self.planner = Planner()
        self.llm = LLM()

    def process(self, command, vision):
        objects = [
            o for o in vision["objects"]
            if o["confidence"] >= MIN_CONFIDENCE
        ]

        decision = self.llm.decide(command, objects, self.memory.holding)
        if not decision:
            return {"intent": "chat", "reply": "Invalid command.", "plan": []}

        intent = decision["intent"]

        if intent == "stop":
            return {"intent": "stop", "reply": "Stopping robot.", "plan": []}

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

        if intent == "pick":
            if self.memory.holding:
                return {
                    "intent": "chat",
                    "reply": f"I am already holding {self.memory.holding}.",
                    "plan": []
                }

            target = decision.get("target")
            obj = self.planner.find_object(target, objects)
            if not obj:
                return {
                    "intent": "chat",
                    "reply": f"I cannot see a {target}.",
                    "plan": []
                }

            self.memory.set(obj["name"])
            return {
                "intent": "pick",
                "reply": decision["reply"],
                "plan": [self.planner.pick(obj)]
            }

        return {"intent": "chat", "reply": decision["reply"], "plan": []}

# ===================== DUMMY VISION =====================
vision_data = {
    "objects": [
        {
            "name": "cup",
            "confidence": 0.66,
            "distance_cm": 24.9,
            "center": [621, 590],
            "grasp_center": [621, 610]
        }
    ]
}

# ===================== REALTIME COMMAND LOOP =====================
brain = Brain()

commands = [
    "what can you see",
    "pick cup",
    "pick cup",
    "place it",
    "stop"
]

for cmd in commands:
    print("\nUSER:", cmd)
    out = brain.process(cmd, vision_data)
    print(json.dumps(out, indent=2))
