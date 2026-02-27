from multiprocessing import util
import time
import json

from ultralytics import solutions

from utils import planner,serializer

from brain.brain import Brain
from brain.server import get_vision
from brain.config import MOCK_VISION

from utils.ik import IK

def mock_vision():
    return {
        "objects": [
            {"name": "bottle", "x_cm": -10, "z_cm": 30},
            {"name": "cup", "x_cm": 10, "z_cm": 30}
        ]
    }


def main():
    brain = Brain()
    ik = IK()

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

            
            vision = mock_vision() if MOCK_VISION else get_vision()
            result = brain.process(user_text, vision)

            
            print("\n🧠 RESULT")
            print(json.dumps(result, indent=3))

            
            if result.get("intent") == "task" and result.get("plan"):
                grip,x,y,z=planner.plan(result["plan"])

                solutions = ik.solve(x, y, z)

                angles = list(solutions[0])

                angles.append(90)  

                if grip:
                    angles.append(90)  
                else:
                    angles.append(20)  
                x = 0
                for t in angles:
                    serializer.move_joint(x, t)
                    print(f"Moving to angle: {t}°")
                    time.sleep(0.5)  
                    x += 1
            
        except KeyboardInterrupt:
            print("\n🔌 Interrupted. Exiting.")
            break

        except Exception as e:
            print("❌ Brain error:", str(e))
            time.sleep(0.5)


if __name__ == "__main__":
    main()
