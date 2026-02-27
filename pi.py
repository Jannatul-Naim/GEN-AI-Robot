import time
import json
import os

from brain.brain import Brain
from brain.server import get_vision
from brain.config import MOCK_VISION

from utils import planner, serializer
from utils.ik import IK

from speech.stt import SpeechToText   # your STT class file


# -----------------------------
# Mock Vision
# -----------------------------
def mock_vision():
    return {
        "objects": [
            {"name": "bottle", "x_cm": -10, "z_cm": 30},
            {"name": "cup", "x_cm": 10, "z_cm": 30}
        ]
    }


# -----------------------------
# Main Loop
# -----------------------------
def main():
    brain = Brain()
    ik = IK()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(BASE_DIR, "speech", "models", "vosk-model-small-en-us-0.15")
    stt = SpeechToText(model_path)

    print("🧠 Robot Brain Online (Speech Mode)")
    print("Say 'quit' to exit.\n")

    stt.start()

    try:
        for user_text in stt.listen():

            print(f"\n🎤 USER > {user_text}")

            if user_text.lower() in ("quit", "exit", "stop"):
                print("🔌 Shutting down brain.")
                break

            # Get vision
            vision = mock_vision() if MOCK_VISION else get_vision()

            # Process with LLM Brain
            result = brain.process(user_text, vision)

            print("\n🧠 RESULT")
            print(json.dumps(result, indent=3))

            # Execute Task
            if result.get("intent") == "task" and result.get("plan"):

                grip, x, y, z = planner.plan(result["plan"])

                solutions = ik.solve(x, y, z)

                if not solutions:
                    print("❌ No IK solution found")
                    continue

                angles = list(solutions[0])

                # Wrist angle
                angles.append(90)

                # Gripper
                angles.append(90 if grip else 20)

                for joint_id, angle in enumerate(angles):
                    serializer.move_joint(joint_id, angle)
                    print(f"🤖 Moving Joint {joint_id} → {angle}°")
                    time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n🔌 Interrupted.")

    finally:
        stt.stop()


if __name__ == "__main__":
    main()