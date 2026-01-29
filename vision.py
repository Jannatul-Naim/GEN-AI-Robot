import cv2
import time
import math
import threading
from flask import Flask, jsonify
from ultralytics import YOLO




CAMERA_INDEX = 2
CAM_WIDTH = 640
CAM_HEIGHT = 480
CAM_FPS = 12

CAMERA_HFOV_DEG = 75
CAMERA_TILT_DEG = 15
CAMERA_HEIGHT_CM = 30


YOLO_MODEL = "yolov8n.pt"
YOLO_IMGSZ = 320
YOLO_CONF = 0.45

TARGET_CLASSES = ["bottle", "cup", "apple"]

OBJECT_WIDTHS_CM = {
    "bottle": 5.0,
    "cup": 10.0,
    "apple": 8.0
}


SHOW_CAMERA = True
INFER_INTERVAL = 0.35

vision_state = {"objects": [], "fps": 0, "timestamp": 0.0}
vision_lock = threading.Lock()
stop_event = threading.Event()


def focal_length_px(w, hfov):
    return (w / 2) / math.tan(math.radians(hfov / 2))

FX = focal_length_px(CAM_WIDTH, CAMERA_HFOV_DEG)
FY = FX
CX = CAM_WIDTH / 2
CY = CAM_HEIGHT / 2


def pixel_to_ground(cx, cy, bw, name):
    real_w = OBJECT_WIDTHS_CM.get(name, 10.0)

    theta = math.atan((cx - CX) / FX)

    phi = math.atan((cy - CY) / FY)

    total_angle = phi + math.radians(CAMERA_TILT_DEG)

    if total_angle <= 0:
        return None


    Z_ground = CAMERA_HEIGHT_CM / math.tan(total_angle)

    Z_width = (real_w * FX) / max(bw, 2)

    Z = 0.7 * Z_ground + 0.3 * Z_width

    X = Z * math.tan(theta)

    return {
        "z_cm": round(Z, 2),
        "theta_deg": round(math.degrees(theta), 2),
        "x_cm": round(X, 2)
    }



class VisionThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.model = YOLO(YOLO_MODEL)
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAM_FPS)
        self.last = time.time()
        self.prev = time.time()

    def run(self):
        if SHOW_CAMERA:
            cv2.namedWindow("Vision")

        while not stop_event.is_set():
            if time.time() - self.last < INFER_INTERVAL:
                time.sleep(0.002)
                continue

            self.last = time.time()
            ret, frame = self.cap.read()
            if not ret:
                continue

            results = self.model(frame, imgsz=YOLO_IMGSZ, conf=YOLO_CONF, verbose=False)
            objs = []

            r = results[0]
            if r.boxes:
                for b in r.boxes:
                    cls = int(b.cls[0])
                    name = self.model.names[cls]
                    if name not in TARGET_CLASSES:
                        continue

                    conf = float(b.conf[0])
                    x1, y1, x2, y2 = map(int, b.xyxy[0])
                    cx = (x1 + x2) // 2
                    cy = y2   
                    bw = max(x2 - x1, 2)

                    pose = pixel_to_ground(cx, cy, bw, name)
                    if pose is None:
                        continue

                    objs.append({
                        "name": name,
                        "confidence": round(conf, 2),
                        "z_cm": pose["z_cm"],
                        "theta_deg": pose["theta_deg"],
                        "x_cm": pose["x_cm"],
                        "pixel": [cx, cy]
                    })

                    if SHOW_CAMERA:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            frame,
                            f"{name} Z:{pose['z_cm']}cm θ:{pose['x_cm']}°",
                            (x1, y1 - 6),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 0),
                            2
                        )

            fps = int(1 / max(time.time() - self.prev, 0.001))
            self.prev = time.time()

            with vision_lock:
                vision_state["objects"] = objs
                vision_state["fps"] = fps
                vision_state["timestamp"] = time.time()

            if SHOW_CAMERA:
                cv2.putText(frame, f"FPS {fps}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                cv2.imshow("Vision", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    stop_event.set()

        self.cap.release()
        cv2.destroyAllWindows()
        





app = Flask(__name__)

@app.route("/vision", methods=["GET"])
def vision():
    with vision_lock:
        return jsonify(vision_state)

if __name__ == "__main__":
    print("[SYSTEM] Starting vision system...", flush=True)

    vision_thread = VisionThread()
    vision_thread.start()

    try:
        app.run(host="0.0.0.0", port=9100, debug=False)
    finally:
        stop_event.set()
        print("[SYSTEM] Shutdown", flush=True)



