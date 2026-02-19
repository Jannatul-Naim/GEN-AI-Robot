import time
import json
import sys

from brain.brain import Brain
from brain.server import send_to_russparry, get_vision
from brain.config import MOCK_VISION





def mock_vision():
    return {
        "objects": [
            {"name": "bottle", "x_cm": -10, "z_cm": 30},
            {"name": "cup", "x_cm": 10, "z_cm": 30}
        ]
    }


def main():
    brain = Brain()

    print("🧠 Robot Brain Online")
    print("Type a command. (quit to exit)\n")

    while True:
        try:
            user_text = input("USER > ").strip()

            if not user_text:
                continue

            if user_text.lower() in ("quit", "exit"):
                print("🔌 Shutting down brain.")
                break

            # Get vision safely
            vision = mock_vision() if MOCK_VISION else get_vision()

            result = brain.process(user_text, vision)

            # Pretty output
            print("\n🧠 RESULT")
            print(json.dumps(result, indent=2))

            # Send plan to robot if exists
            if result.get("intent") == "task" and result.get("plan"):
                send_to_russparry(result["plan"])

        except KeyboardInterrupt:
            print("\n🔌 Interrupted. Exiting.")
            break

        except Exception as e:
            print("❌ Brain error:", str(e))
            time.sleep(0.5)


if __name__ == "__main__":
    main()
