#!/usr/bin/env python3

import cv2
import time
import json
import math
import threading
import asyncio
import websockets

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from ultralytics import YOLO

CAMERA_INDEX = 0
CAM_WIDTH = 640
CAM_HEIGHT = 480
CAM_FPS = 12

YOLO_MODEL = "yolov8n.pt"
YOLO_IMGSZ = 320
YOLO_CONF = 0.45

INFER_INTERVAL = 0.35
VISION_UPDATE_INTERVAL = 0.01
CAMERA_HFOV_DEG = 78.0

TARGET_CLASSES = ["bottle", "cup", "cell phone"]

OBJECT_WIDTHS_CM = {
    "bottle": 7.0,
    "cup": 8.0,
    "cell phone": 7.5,
    "book": 15.0,
    "person": 45.0
}

COLAB_WS = "wss://YOUR_COLAB_WS_URL"

vision_state = {"objects": [], "fps": 0, "timestamp": 0.0}
vision_lock = threading.Lock()
stop_event = threading.Event()


def focal_length_px(w, hfov):
    return (w / 2) / math.tan(math.radians(hfov / 2))


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

    def run(self):
        while not stop_event.is_set():
            now = time.time()
            if now - self.last_update < VISION_UPDATE_INTERVAL:
                continue
            self.last_update = now
            if now - self.last_infer < INFER_INTERVAL:
                continue
            self.last_infer = now

            ret, frame = self.cap.read()
            if not ret:
                continue

            results = self.model(frame, imgsz=YOLO_IMGSZ, conf=YOLO_CONF, verbose=False)
            objects = []

            r = results[0]
            if r.boxes:
                for b in r.boxes:
                    name = self.model.names[int(b.cls[0])]
                    if name not in TARGET_CLASSES:
                        continue

                    x1, y1, x2, y2 = map(int, b.xyxy[0])
                    bw = max(x2 - x1, 2)
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    z = (OBJECT_WIDTHS_CM[name] * self.fx) / bw

                    objects.append({
                        "name": name,
                        "confidence": round(float(b.conf[0]), 2),
                        "distance_cm": round(z, 1),
                        "center": [cx, cy]
                    })

            fps = int(1 / max(time.time() - self.prev_time, 0.001))
            self.prev_time = time.time()

            with vision_lock:
                vision_state["objects"] = objects
                vision_state["fps"] = fps
                vision_state["timestamp"] = time.time()


class VisionROS(Node):
    def __init__(self):
        super().__init__("vision_node")
        self.pub = self.create_publisher(String, "/vision/objects", 10)
        self.timer = self.create_timer(0.1, self.publish)

    def publish(self):
        with vision_lock:
            msg = String()
            msg.data = json.dumps(vision_state)
            self.pub.publish(msg)


async def colab_stream():
    while not stop_event.is_set():
        try:
            async with websockets.connect(COLAB_WS, ping_interval=None) as ws:
                while not stop_event.is_set():
                    with vision_lock:
                        await ws.send(json.dumps(vision_state))
                    await asyncio.sleep(0.1)
        except:
            await asyncio.sleep(1)


def main():
    VisionThread().start()
    threading.Thread(target=lambda: asyncio.run(colab_stream()), daemon=True).start()

    rclpy.init()
    node = VisionROS()
    rclpy.spin(node)
    stop_event.set()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
