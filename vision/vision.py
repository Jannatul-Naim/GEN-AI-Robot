import cv2
import time
import json
import math
import threading
from ultralytics import YOLO

CAMERA_INDEX = 0
CAM_WIDTH = 640
CAM_HEIGHT = 480
CAM_FPS = 12

YOLO_MODEL = "yolov8n.pt"
YOLO_IMGSZ = 320
YOLO_CONF = 0.45

SHOW_CAMERA = True

INFER_INTERVAL = 0.35
VISION_UPDATE_INTERVAL = 0.01

CAMERA_HFOV_DEG = 78.0

GRASP_OFFSET_X = 0
GRASP_OFFSET_Y = 20

LOCK_LOST_TIMEOUT = 1.0

TARGET_CLASSES = ["bottle", "cup", "cell phone"]





OBJECT_WIDTHS_CM = {
    "bottle": 7.0,
    "cup": 8.0,
    "cell phone": 7.5,
    "book": 15.0,
    "person": 45.0
}

vision_state = {
    "objects": [],
    "fps": 0,
    "timestamp": 0.0
}

vision_lock = threading.Lock()
stop_event = threading.Event()

def focal_length_px(w, hfov):
    return (w / 2) / math.tan(math.radians(hfov / 2))

calib_points = []
calibrating = False
fx_calibrated = None

def mouse_callback(event, x, y, flags, param):
    global calib_points
    if event == cv2.EVENT_LBUTTONDOWN:
        calib_points.append((x, y))

class VisionThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.model = YOLO(YOLO_MODEL)
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAM_FPS)
        self.fx = focal_length_px(CAM_WIDTH, CAMERA_HFOV_DEG)
        self.last_update = 0
        self.last_infer = 0
        self.prev_time = time.time()
        self.locked_target = None
        self.lock_last_seen = 0

    def run(self):
        global calibrating, fx_calibrated
        if SHOW_CAMERA:
            cv2.namedWindow("Vision")
            cv2.setMouseCallback("Vision", mouse_callback)

        while not stop_event.is_set():
            now = time.time()

            if now - self.last_update < VISION_UPDATE_INTERVAL:
                time.sleep(0.002)
                continue
            self.last_update = now

            if now - self.last_infer < INFER_INTERVAL:
                continue
            self.last_infer = now

            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            results = self.model(frame, imgsz=YOLO_IMGSZ, conf=YOLO_CONF, verbose=False)

            objects = []

            r = results[0]
            if r.boxes:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    name = self.model.names[cls]
                    if name not in TARGET_CLASSES:
                        continue

                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    bw = max(x2 - x1, 2)

                    fx_use = fx_calibrated if fx_calibrated else self.fx
                    z_cm = (OBJECT_WIDTHS_CM.get(name, 10.0) * fx_use) / bw

                    obj = {
                        "name": name,
                        "confidence": round(conf, 2),
                        "distance_cm": round(z_cm, 1),
                        "center": [cx, cy],
                        "grasp_center": [cx + GRASP_OFFSET_X, cy + GRASP_OFFSET_Y]
                    }
                    objects.append(obj)

                    if self.locked_target:
                        lx, ly = self.locked_target["center"]
                        if abs(cx - lx) < 50 and abs(cy - ly) < 50:
                            self.locked_target = obj
                            self.lock_last_seen = now
                    elif not self.locked_target:
                        self.locked_target = obj
                        self.lock_last_seen = now

            if self.locked_target and now - self.lock_last_seen > LOCK_LOST_TIMEOUT:
                self.locked_target = None

            fps = int(1 / max(time.time() - self.prev_time, 0.001))
            self.prev_time = time.time()

            with vision_lock:
                vision_state["objects"] = objects
                vision_state["fps"] = fps
                vision_state["timestamp"] = time.time()

            if SHOW_CAMERA:
                if self.locked_target:
                    cx, cy = self.locked_target["center"]
                    cv2.circle(frame, (cx, cy), 8, (0, 0, 255), -1)

                cv2.putText(frame, f"FPS {fps}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                cv2.imshow("Vision", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    stop_event.set()
                elif key == ord('r'):
                    self.locked_target = None
                elif key == ord('c'):
                    calibrating = True
                    calib_points.clear()

        self.cap.release()
        cv2.destroyAllWindows()

def get_vision_json():
    with vision_lock:
        return json.dumps(vision_state, indent=2)

def test_vision():
    VisionThread().start()
    try:
        while not stop_event.is_set():
            print(get_vision_json())
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_event.set()
