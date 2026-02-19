import requests
import json
from . import config


def get_vision():
    try:
        r = requests.get(config.VISION_URL, timeout=1)
        return r.json()
    except requests.exceptions.RequestException:
        return {"objects": []}
    

def send_to_russparry(plan):
    print(json.dumps({"plan to send in : ": plan}, indent=2))

    if not plan:
        return
    try:
        requests.post(
            config.RUSSPARRY_URL,
            json={"plan": plan},
            timeout=10
        )
    except requests.exceptions.ConnectTimeout:
        print("❌ Russparry timeout: server unreachable")
    except requests.exceptions.RequestException as e:
        print("❌ Russparry error:", e)
