import json
import requests
import re
import config


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
            config.OLLAMA_URL,
            json={
                "model": config.OLLAMA_MODEL,
                "prompt": self.prompt(cmd, objects, memory),
                "stream": False,
                "options": {"temperature": 0}
            },
            timeout=config.LLM_TIMEOUT
        )
        return self.extract(r.json().get("response", ""))



