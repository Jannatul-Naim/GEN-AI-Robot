import json
import requests
from . import config


class LLM:
    def extract(self, text):
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except:
            return None

    def prompt(self, cmd, objects, memory):
        return f"""Return ONLY valid JSON.

FORMAT:
{{
  "intent": "task|chat|stop",
  "steps": [
    {{
      "action": "pick|place|give",
      "position": [x_cm, z_cm]|null
    }}
  ],
  "reply": "short"
}}

World:
X negative=left, positive=right
Z front=25, larger=further

Visible objects:
{json.dumps(objects)}

Memory:
{json.dumps(memory)}

Command:
{cmd}
"""

    def decide(self, cmd, objects, memory):
        r = requests.post(
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
            raw = r.json().get("response", "")
        except:
            raw = r.text
        return self.extract(raw)

def test():
    llm = LLM()
    cmd = "Pick up the nearest bottle and pick up the cup."
    objects = [
        {"name": "bottle", "x_cm": -10, "z_cm": 30},
        {"name": "cup", "x_cm": 10, "z_cm": 30}
    ]
    memory = []
    decision = llm.decide(cmd, objects, memory)
    print(json.dumps(decision, indent=2))

