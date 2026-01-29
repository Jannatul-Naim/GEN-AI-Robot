import time
import json

from brain import Brain, send_to_russparry
from vision_client import get_vision


def main():
    brain = Brain()

    print("🧠 Brain online. Type commands (or 'quit').")

    while True:
        try:
            user_text = input("\nUSER> ").strip()
            if not user_text:
                continue

            if user_text.lower() in ("quit", "exit"):
                print("Shutting down brain.")
                break

            vision = get_vision()
            print("Vision data:", vision)

            result = brain.process(user_text, vision)

            print("\nBRAIN OUTPUT:")
            print(json.dumps(result, indent=2))

            if result.get("plan"):
                send_to_russparry(result["plan"])

        except KeyboardInterrupt:
            print("\nInterrupted. Exiting.")
            break

        except Exception as e:
            print("[BRAIN ERROR]:", e)
            time.sleep(0.5)


if __name__ == "__main__":
    main()
