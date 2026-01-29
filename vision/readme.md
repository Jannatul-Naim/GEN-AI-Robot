# AI-Driven Single-Camera Vision System for Ground Object Localization

## Abstract
This project presents a real-time single-camera vision system capable of detecting everyday objects and estimating their real-world positions on a ground plane. Using a monocular RGB camera, YOLOv8 object detection, and geometric projection, the system computes the X–Z coordinates (in centimeters) of detected objects assuming they lie on the ground. The system runs in real time, exposes results via a RESTful Flask API, and is designed to integrate directly with robotic manipulation or navigation systems.

---

## 1. Introduction
Robotic systems often require spatial awareness of objects in their environment. While stereo vision or depth sensors are common solutions, they increase hardware cost and system complexity. This project demonstrates that reasonable ground-plane localization accuracy can be achieved using a single calibrated camera combined with geometric reasoning.

The system is designed with the following goals:
- Real-time performance on low-cost hardware
- Modular and extensible architecture
- Easy integration with robot controllers via HTTP
- Stable distance estimation for ground-level objects

---

## 2. System Overview

### 2.1 Architecture
The system is divided into five main modules:

- **main.py** – Entry point that initializes threads and the web server
- **config.py** – Centralized configuration and system constants
- **geometry.py** – Camera model and pixel-to-world projection
- **vision.py** – Camera capture, YOLO inference, and coordinate estimation
- **server.py** – Flask-based REST API for external access

The vision pipeline runs in a dedicated thread, while the Flask server runs in the main thread, sharing state through a thread-safe data structure.

---

## 3. Coordinate System Definition
The system uses a ground-plane coordinate frame:

- **X-axis**: Left / Right on the ground (cm)
- **Z-axis**: Forward distance from the camera (cm)
- **Y-axis**: Vertical (fixed at 0, assuming objects rest on the ground)

The camera is mounted at a fixed height **H** above the ground and tilted downward by a known angle.

---

## 4. Camera Model and Geometry

### 4.1 Camera Parameters
Key camera parameters are defined in `config.py`:

- Camera height above ground
- Tilt angle
- Horizontal field of view (HFOV)
- Image resolution

From these parameters, the intrinsic focal length is computed as:

```
fx = (image_width / 2) / tan(HFOV / 2)
```

### 4.2 Pixel-to-World Projection
For each detected object:

1. The bottom-center of the bounding box is assumed to touch the ground plane.
2. Horizontal and vertical angles are computed from pixel offsets.
3. The camera tilt angle is added to the vertical angle.
4. Ground distance (Z) is computed using trigonometric projection.
5. A secondary depth estimate is computed using known object width.
6. Both estimates are fused using a weighted average for stability.

This approach provides robust distance estimation even when bounding box size fluctuates.

---

## 5. Object Detection

### 5.1 YOLOv8 Integration
The system uses **YOLOv8n** from the Ultralytics framework for fast inference. Detection runs at a fixed interval to maintain stable FPS.

Target object classes are configurable and include:
- Bottle
- Cup
- Apple

Each detection provides:
- Object class
- Confidence score
- Pixel location
- Estimated real-world coordinates

---

## 6. Multithreading and Performance

- Camera capture and inference run in a dedicated daemon thread
- Flask API runs independently without blocking vision processing
- Shared state is protected using a threading lock

### Expected Performance

| Setting | FPS |
|------|------|
| YOLOv8n (320px) | ~18–25 |
| With drawing | ~15–20 |
| Flask enabled | Stable |

---

## 7. Accuracy Evaluation

The system provides practical accuracy for short-range robotic tasks:

| Distance Range | Typical Error |
|--------------|---------------|
| 10–20 cm | ±1–2 cm |
| 20–40 cm | ±2–4 cm |

Accuracy depends on camera calibration, mounting stability, and object size assumptions.

---

## 8. API Design

### GET /vision
Returns the current perception state:

- Detected objects
- Real-world coordinates
- FPS
- Timestamp

This endpoint is designed for easy integration with robotic arms, planners, or LLM-based controllers.

---

## 9. Applications

- Robotic grasping and pick-and-place
- Autonomous navigation
- Human–robot interaction
- Vision input for LLM-based robotic reasoning

---

## 10. Limitations and Future Work

Current limitations:
- Assumes flat ground plane
- Limited accuracy at long distances
- Requires known object sizes

Future improvements:
- Automatic camera calibration
- Dynamic ground plane estimation
- Temporal filtering (Kalman / EMA)
- Multi-object tracking
- Stereo or depth sensor fusion

---

## 11. Conclusion
This project demonstrates that a carefully designed monocular vision system can provide reliable spatial information for real-time robotic applications. Its modular structure, real-time performance, and clean API make it suitable as a core perception module in larger AI-driven robotic systems.

---

# README.md

## 📷 Single-Camera Vision System (YOLO + Geometry)

A real-time monocular vision system that detects objects and estimates their real-world ground coordinates using a single RGB camera.

---

## ✨ Features

- YOLOv8-based object detection
- Real-world X/Z coordinate estimation (cm)
- Single-camera setup (no depth sensor)
- Real-time performance
- Flask REST API
- Modular and clean architecture

---

## 📁 Project Structure

```
vision/
│
├── main.py        # Entry point
├── config.py      # System configuration
├── geometry.py    # Pixel-to-world projection
├── vision.py      # YOLO + camera thread
├── server.py      # Flask API
├── __init__.py
└── .FILE.txt
```

---

## 📦 Requirements

```
opencv-python
ultralytics
flask
numpy
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Edit `config.py` to set:

- Camera resolution and FPS
- Camera height and tilt angle
- YOLO model and confidence
- Target object classes
- Known object widths

---

## ▶️ Running the System

```
python main.py
```

- Camera window opens (press `q` to quit)
- Flask server runs on port **9100**

---

## 🌐 API Usage

**GET /vision**

Returns JSON:

```
{
  "objects": [
    {
      "name": "bottle",
      "confidence": 0.82,
      "x_cm": -4.3,
      "y_cm": 0.0,
      "z_cm": 22.1,
      "pixel": [312, 410]
    }
  ],
  "fps": 18,
  "timestamp": 1700000000.0
}
```

---

## 🎯 Accuracy

| Distance | Error |
|--------|-------|
| 10–20 cm | ±1–2 cm |
| 20–40 cm | ±2–4 cm |

---

## 🤖 Intended Use

- Robotic arms
- Autonomous systems
- AI + LLM robotic control
- Research and academic projects

---

## 📌 Notes

- Objects are assumed to lie on a flat ground plane
- Camera must be mounted rigidly
- Best accuracy achieved at short to medium range

---

## 📜 License

Open-source, free to use for academic and personal projects.

---

**Author:** Jannatul Naim Apu

