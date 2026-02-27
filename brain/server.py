import requests
import json
from . import config


def get_vision():
    try:
        r = requests.get(config.VISION_URL, timeout=1)
        return r.json()
    except requests.exceptions.RequestException:
        return {"objects": []}
    
