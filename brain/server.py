import requests
import json
import config


def get_vision():
    try:
        r = requests.get(config.VISION_URL, timeout=1)
        return r.json()
    except requests.exceptions.RequestException:
        return {"objects": []}
    

def send_to_russparry(plan):
    if not plan:
        return
    print(json.dumps({"plan": plan}, indent=2))
    try:
        requests.post(
            config.RUSSPARRY_URL,
            json={"plan": plan},
            timeout=30
        )
    except requests.exceptions.ConnectTimeout:
        print("❌ Russparry timeout: server unreachable")
    except requests.exceptions.ConnectionError:
        print("❌ Russparry connection error")
