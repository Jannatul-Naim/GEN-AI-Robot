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

CAMERA_HFOV_DEG = 78.0
CAMERA_TILT_DEG = 15.0
CAMERA_HEIGHT_CM = 15.0

YOLO_MODEL = "yolov8n.pt"
YOLO_IMGSZ = 320
YOLO_CONF = 0.45

TARGET_CLASSES = ["bottle", "cup", "apple"]

SHOW_CAMERA = True
INFER_INTERVAL = 0.35

vision_state = {"objects": []}
vision_lock = threading.Lock()
stop_event = threading.Event()

def focal_length_px(w, hfov):
    return (w / 2) / math.tan(math.radians(hfov / 2))

FX = focal_length_px(CAM_WIDTH, CAMERA_HFOV_DEG)
FY = FX
CX = CAM_WIDTH / 2
CY = CAM_HEIGHT / 2

def pixel_to_ground(cx, cy):
    theta = math.atan((cx - CX) / FX)
    phi = math.atan((cy - CY) / FY)
    total_angle = phi + math.radians(CAMERA_TILT_DEG)
    if total_angle <= 0:
        return None
    z = CAMERA_HEIGHT_CM / math.tan(total_angle)
    return round(z, 2), round(math.degrees(theta), 2)

class VisionThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.model = YOLO(YOLO_MODEL)
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAM_FPS)
        self.last = time.time()

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

                    x1, y1, x2, y2 = map(int, b.xyxy[0])
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2

                    res = pixel_to_ground(cx, cy)
                    if res is None:
                        continue

                    z, deg = res
                    objs.append({
                        "name": name,
                        "z_cm": z,
                        "degree": deg
                    })

                    if SHOW_CAMERA:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            frame,
                            f"{name} Z:{z}cm θ:{deg}°",
                            (x1, y1 - 6),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 0),
                            2
                        )

            with vision_lock:
                vision_state["objects"] = objs

            if SHOW_CAMERA:
                cv2.imshow("Vision", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    stop_event.set()

        self.cap.release()
        cv2.destroyAllWindows()




def get_vision_json():
    with vision_lock:
        return json.dumps(vision_state, indent=2)

def main():
    VisionThread().start()
    try:
        while not stop_event.is_set():
            with vision_lock:
                print(json.dumps(vision_state["objects"], indent=2))
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_event.set()

if __name__ == "__main__":
    main()