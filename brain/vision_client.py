import requests

VISION_URL = "http://10.15.14.212:9100/vision"

def get_vision():
    try:
        r = requests.get(VISION_URL, timeout=1)
        return r.json()
    except requests.exceptions.RequestException:
        return {"objects": []}
