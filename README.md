# Vision (YOLOv8n)

A **Python-based real-time vision system** for **Raspberry Pi 5** using **Ultralytics YOLOv8n**, designed for **safe, low-temperature operation without active cooling**.

This project is suitable as a **vision backbone** for robotics, manipulation, and AI-assisted embedded systems.

---

## 🚀 Features

- Real-time **multi-object detection**
- Structured **JSON output** for all detected objects
- **Customizable target classes**
- **Distance estimation (cm)** using camera calibration
- **Grasp point calculation** for robotic manipulation
- Optional **visualization window**
- Configurable **inference rate** to control temperature
- Designed for **headless operation**
- Calibratable focal length

---

## 🧠 System Overview

```
Camera
  ↓
YOLOv8n Inference
  ↓
Object Filtering (Target Classes)
  ↓
Distance Estimation
  ↓
Grasp Point Calculation
  ↓
JSON Output (Terminal / Serial / Network)
```

---

## 🧰 Requirements

- Raspberry Pi 5
- Python **3.10+**
- USB or Pi Camera

### Python Dependencies

```bash
pip install ultralytics opencv-python
```

> `numpy` is included automatically with Ultralytics.

---

## ⚙️ Configuration

Edit `vision_base.py` to tune performance and behavior:

### Camera Settings

```python
CAMERA_INDEX = 0
CAM_WIDTH = 640
CAM_HEIGHT = 480
CAM_FPS = 12
```

### YOLO Settings

```python
YOLO_MODEL = "yolov8n.pt"
YOLO_IMGSZ = 320
YOLO_CONF = 0.45
```

### Performance & Safety

```python
INFER_INTERVAL = 0.35      # Higher = cooler CPU
VISION_UPDATE_INTERVAL = 0.01
```

### Display

```python
SHOW_CAMERA = True         # False for headless mode
```

### Camera Calibration

```python
CAMERA_HFOV_DEG = 78.0
```

### Grasp Point Offset

```python
GRASP_OFFSET_X = 0
GRASP_OFFSET_Y = 20
```

### Target Locking

```python
LOCK_LOST_TIMEOUT = 1.0
```

### Target Classes

```python
TARGET_CLASSES = ["bottle", "cup", "cell phone"]
```

Only objects in `TARGET_CLASSES` will be included in JSON output.

---

## ▶️ Usage

Run the vision system:

```bash
python vision_base.py
```

### Runtime Controls

- **q** → Quit
- **r** → Reset target lock
- **c** → Start calibration

### Display (if enabled)

- Bounding boxes with labels
- 🔴 Red circle → grasp point
- FPS overlay (top-left)

---

## 📤 JSON Output Format

Printed to terminal every **0.5 seconds**:

```json
{
  "objects": [
    {
      "name": "bottle",
      "confidence": 0.82,
      "distance_cm": 42.3,
      "center": [312, 221],
      "grasp_center": [312, 241]
    },
    {
      "name": "cup",
      "confidence": 0.76,
      "distance_cm": 55.1,
      "center": [180, 260],
      "grasp_center": [180, 280]
    }
  ],
  "fps": 7,
  "timestamp": 1736100000.12
}
```

### Field Description

| Field | Description |
|-----|------------|
| `objects` | List of detected objects |
| `confidence` | YOLO confidence score |
| `distance_cm` | Estimated distance from camera |
| `center` | Object center (pixels) |
| `grasp_center` | Suggested grasp location |
| `fps` | Inference FPS |
| `timestamp` | Unix time |

---

## 🤖 Robotics Integration

- Send JSON over **Serial (USB / UART)**
- Stream via **Socket / REST / MQTT**
- Feed directly into:
  - ESP32 / ESP8266
  - Motion planners
  - Grasping controllers
  - LLM-based decision systems

---

## 🌡️ Thermal Notes

- Optimized for **no active cooling**
- Expected temperature: **60–70°C**
- Avoid increasing:
  - FPS
  - Image size
  - Model size

Without additional cooling.

---

## 📄 License

MIT License

---

## 🙌 Acknowledgements

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- OpenCV Community
- Raspberry Pi Foundation

---

**Built for safe, intelligent, and scalable embedded vision systems.**

