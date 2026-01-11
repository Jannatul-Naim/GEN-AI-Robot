import threading
from vision.vision import VisionThread
from vision.vision_server import app

def run_flask():
    app.run(host="0.0.0.0", port=9100, debug=False, use_reloader=False)

if __name__ == "__main__":
    vision_thread = VisionThread()
    vision_thread.start()

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    vision_thread.join()
