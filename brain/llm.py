import json
import requests
from . import config


class LLM:
    def __init__(self):
        pass


    def extract(self, text):
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start == -1 or end == -1:
                return None
            return json.loads(text[start:end])
        except Exception:
            return None

    def prompt(self, cmd, objects, memory):
        return f"""You are a robot control brain.

Return ONLY valid JSON.
Do NOT explain anything.
Do NOT include markdown.
Do NOT include extra text.

FORMAT:
{{
  "intent": "task|chat|stop",
  "steps": [
    {{
      "action": "pick|place|give",
      "target": "object_name|null",
      "mode": "nearest|farthest|null",
      "relation": "left|right|front|null",
      "reference": "object_name|null"
    }}
  ],
  "reply": "short"
}}

Rules:
- For pick → use target and optional mode.
- For place → use relation and reference if needed.
- For give → no target needed.
- If just talking → intent = chat.
- If emergency stop → intent = stop.
- If object not visible → still return task with best guess.

World:
X negative = left
X positive = right
Z = 25 is front of robot
Larger Z = further away

Visible objects:
{json.dumps(objects)}

Memory:
{json.dumps(memory)}

Command:
{cmd}
"""


    def decide(self, cmd, objects, memory):
        try:
            response = requests.post(
                config.OLLAMA_URL,
                json={
                    "model": config.OLLAMA_MODEL,
                    "prompt": self.prompt(cmd, objects, memory),
                    "stream": False,
                    "options": {
                        "temperature": config.TEMPERATURE,
                        "num_predict": config.MAX_TOKENS
                    }
                },
                timeout=config.LLM_TIMEOUT
            )

            try:
                raw = response.json().get("response", "")
            except Exception:
                raw = response.text

            decision = self.extract(raw)


            return decision

        except requests.exceptions.RequestException as e:
            print("❌ LLM connection error:", e)
            return {
                "intent": "chat",
                "steps": [],
                "reply": "LLM unavailable"
            }

        except Exception as e:
            print("❌ LLM unexpected error:", e)
            return {
                "intent": "chat",
                "steps": [],
                "reply": "LLM error"
            }



def test():
    llm = LLM()

    cmd = "Pick up the nearest bottle and pick up the cup."

    objects = [
        {"name": "bottle", "x_cm": -10, "z_cm": 30},
        {"name": "cup", "x_cm": 10, "z_cm": 30}
    ]

    memory = {
        "holding": None,
        "safety_state": "normal",
        "last_objects": objects,
        "last_plan": [],
        "last_command": None
    }

    decision = llm.decide(cmd, objects, memory)
    print("Final decision:")
    print(json.dumps(decision, indent=2))


