Vision Module – Robotic Perception System
Description

This directory contains the vision subsystem of the robotic platform. The module performs real-time object detection and ground-plane position estimation using a monocular camera and deep learning.

The vision system runs independently from robot motion control and communicates with other subsystems via a RESTful API.

Directory Structure
vision/
│
├── main.py        # Entry point
├── config.py      # System configuration and constants
├── geometry.py    # Camera geometry and coordinate projection
├── vision.py      # YOLO-based vision processing thread
├── server.py      # Flask REST API
├── __init__.py
└── README.txt

Dependencies

The following Python packages are required:

opencv-python

ultralytics

flask

numpy

Camera Assumptions

Camera is mounted at a fixed height above the ground

Camera is tilted downward by a known angle

All detected objects are assumed to lie on the ground plane

Coordinate system:

X: left/right (cm)

Z: forward distance (cm)

Y: vertical (fixed at 0)

Execution

Run the vision module using:

python main.py


The system starts camera capture, object detection, and launches a REST server.

API Endpoint
GET /vision


Returns a JSON object containing:

Detected object list

Estimated world coordinates

Detection confidence

System FPS and timestamp

Performance

Expected performance:

YOLOv8n (320 resolution): ~18–25 FPS

With visualization enabled: ~15–20 FPS

Stable operation with REST API enabled