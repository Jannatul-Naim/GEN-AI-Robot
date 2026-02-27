import threading
from vision_thread import VisionThread
from server import create_server

vision_state = {
    "objects": [],
    "fps": 0,
    "timestamp": 0.0
}

lock = threading.Lock()
stop_event = threading.Event()

if __name__ == "__main__":
    print("[SYSTEM] Starting single-camera vision system")

    vision = VisionThread(vision_state, lock, stop_event)
    vision.start()

    app = create_server(vision_state, lock)

    try:
        app.run(host="0.0.0.0", port=9100, debug=False)
    finally:
        stop_event.set()
        print("[SYSTEM] Shutdown")