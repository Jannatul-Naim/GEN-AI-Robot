import cv2
import time
import json
import math
import threading
from ultralytics import YOLO

# ===================== CAMERA CONFIG =====================
CAMERA_INDEX = 0
CAM_WIDTH = 640
CAM_HEIGHT = 480
CAM_FPS = 12

CAMERA_HFOV_DEG = 78.0
CAMERA_TILT_DEG = 45.0           # 🔥 FIXED 45 DEG
CAMERA_HEIGHT_CM = 40.0          # 🔥 CAMERA HEIGHT FROM FLOOR

# ===================== YOLO CONFIG =====================
YOLO_MODEL = "yolov8n.pt"
YOLO_IMGSZ = 320
YOLO_CONF = 0.45

TARGET_CLASSES = ["bottle", "cup", "apple"]

OBJECT_WIDTHS_CM = {
    "bottle": 6.0,
    "cup": 10.0,
    "apple": 8.0
}

# ===================== SYSTEM =====================
SHOW_CAMERA = True
INFER_INTERVAL = 0.35

vision_state = {"objects": [], "fps": 0, "timestamp": 0.0}
vision_lock = threading.Lock()
stop_event = threading.Event()

# ===================== CAMERA INTRINSICS =====================
def focal_length_px(w, hfov):
    return (w / 2) / math.tan(math.radians(hfov / 2))

FX = focal_length_px(CAM_WIDTH, CAMERA_HFOV_DEG)
FY = FX
CX = CAM_WIDTH / 2
CY = CAM_HEIGHT / 2

# ===================== GEOMETRY (45° TILT CORRECT) =====================
def pixel_to_ground(cx, cy, bw, name):
    real_w = OBJECT_WIDTHS_CM.get(name, 10.0)

    # --- Horizontal bearing ---
    theta = math.atan((cx - CX) / FX)

    # --- Vertical ray angle ---
    phi = math.atan((cy - CY) / FY)

    # --- Total downward angle ---
    total_angle = phi + math.radians(CAMERA_TILT_DEG)

    # --- Ground intersection distance ---
    if total_angle <= 0:
        return None

    Z = CAMERA_HEIGHT_CM / math.tan(total_angle)

    # --- Lateral position ---
    X = Z * math.tan(theta)

    return {
        "z_cm": round(Z, 2),                         # forward distance
        "theta_deg": round(math.degrees(theta), 2), # bearing
        "x_cm": round(X, 2)
    }

# ===================== VISION THREAD =====================
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
                    cy = (y1 + y2) // 2
                    bw = max(x2 - x1, 2)

                    pose = pixel_to_ground(cx, cy, bw, name)
                    if pose is None:
                        continue

                    objs.append({
                        "name": name,
                        "confidence": round(conf, 2),
                        "pose": pose,
                        "pixel": [cx, cy]
                    })

                    if SHOW_CAMERA:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            frame,
                            f"{name} Z:{pose['z_cm']}cm θ:{pose['theta_deg']}°",
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

# ===================== MAIN =====================
def main():
    VisionThread().start()
    try:
        while not stop_event.is_set():
            with vision_lock:
                print(json.dumps(vision_state, indent=2))
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_event.set()

if __name__ == "__main__":
    main()
