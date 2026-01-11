import threading
from vision.vision import VisionThread
from vision.vision_server import app as vision_app
from robot_serialization.robot_server import app as robot_app

def run_vision_server():
    vision_app.run(host="0.0.0.0", port=9100, debug=False, use_reloader=False)

def run_robot_server():
    robot_app.run(host="0.0.0.0", port=9000, debug=False, use_reloader=False)

if __name__ == "__main__":
    VisionThread().start()

    threading.Thread(target=run_vision_server, daemon=True).start()
    threading.Thread(target=run_robot_server, daemon=True).start()

    while True:
        pass
