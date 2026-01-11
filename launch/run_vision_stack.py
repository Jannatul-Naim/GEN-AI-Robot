import threading
import time

from vision.vision import VisionThread
from vision.vision_server import app as vision_app


def run_vision_server():
    vision_app.run(
        host="0.0.0.0",
        port=9100,
        debug=False,
        use_reloader=False
    )


if __name__ == "__main__":
    # Start vision thread
    VisionThread().start()

    # Start Flask server
    threading.Thread(
        target=run_vision_server,
        daemon=True
    ).start()

    # Keep main thread alive
    while True:
        time.sleep(1)
