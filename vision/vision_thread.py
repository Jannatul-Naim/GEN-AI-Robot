import cv2
import time
import threading
from ultralytics import YOLO
from geometry import Geometry
from config import *

class VisionThread(threading.Thread):
    def __init__(self, shared_state, lock, stop_event):
        super().__init__(daemon=True)
        self.state = shared_state
        self.lock = lock
        self.stop_event = stop_event

        self.geom = Geometry()
        

        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAM_FPS)

        self.last_infer = 0
        self.prev_time = time.time()

    def run(self):
        self.model = YOLO(YOLO_MODEL)
        if SHOW_CAMERA:
            cv2.namedWindow("Vision")

        while not self.stop_event.is_set():
            ret, frame = self.cap.read()
            if not ret:
                continue

            now = time.time()
            if now - self.last_infer < INFER_INTERVAL:
                continue
            self.last_infer = now

            results = self.model(
                frame,
                imgsz=YOLO_IMGSZ,
                conf=YOLO_CONF,
                verbose=False,
                device=0,
                half=True
            )

            objects = []

            for r in results:
                if not r.boxes:
                    continue

                for b in r.boxes:
                    cls = int(b.cls[0])
                    name = self.model.names[cls]

                    if name not in TARGET_CLASSES:
                        continue

                    x1, y1, x2, y2 = map(int, b.xyxy[0])
                    px = (x1 + x2) // 2
                    py = y2
                    bw = max(x2 - x1, 2)

                    pose = self.geom.pixel_to_world(px, py, bw, name)
                    if not pose:
                        continue

                    objects.append({
                        "name": name,
                        "confidence": round(float(b.conf[0]), 2),
                        **pose,
                        "pixel": [px, py]
                    })

                    if SHOW_CAMERA:
                        cv2.rectangle(frame, (x1,y1),(x2,y2),(0,255,0),2)
                        cv2.putText(
                            frame,
                            f"{name} Z:{pose['z_cm']}cm X:{pose['x_cm']}cm",
                            (x1, y1-5),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,(0,255,0),2
                        )

            fps = int(1 / max(time.time() - self.prev_time, 0.001))
            self.prev_time = time.time()

            with self.lock:
                self.state["objects"] = objects
                self.state["fps"] = fps
                self.state["timestamp"] = time.time()

            if SHOW_CAMERA:
                cv2.putText(frame, f"FPS {fps}", (10,30),
                            cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,0,0),2)
                cv2.imshow("Vision", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.stop_event.set()

        self.cap.release()
        cv2.destroyAllWindows()
