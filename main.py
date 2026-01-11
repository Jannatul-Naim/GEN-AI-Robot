import time
import json
from vision_client import get_vision
from brain import Brain
import requests

RUSSPARRY_URL = "http://192.168.0.109:9000/robot"

def send_to_russparry(data):
    try:
        requests.post(RUSSPARRY_URL, json=data, timeout=2)
    except requests.exceptions.RequestException:
        pass

if __name__ == "__main__":
    brain = Brain()

    while True:
        vision = get_vision()

        user_command = input("\nUSER COMMAND: ")

        result = brain.process(user_command, vision)

        print(json.dumps(result, indent=2))

        send_to_russparry(result)

        time.sleep(0.1)
