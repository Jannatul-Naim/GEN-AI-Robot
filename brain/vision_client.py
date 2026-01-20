import requests

VISION_URL = "http://192.168.0.109:9100/vision"

def get_vision():
    try:
        r = requests.get(VISION_URL, timeout=1)
        return r.json()
    except requests.exceptions.RequestException:
        return {"objects": []}
