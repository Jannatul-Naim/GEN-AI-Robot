# Raspberry Pi 5 Vision Base (YOLOv8n)

A **Python-based real-time vision system** for **Raspberry Pi 5** using **Ultralytics YOLOv8n**, designed to run **safely without active cooling** while maintaining usable detection performance.

This project focuses on **thermal safety, predictable FPS, and clean JSON output** for robotics and embedded vision pipelines.

---

## Key Goals

* Stable operation on Raspberry Pi 5 **without a fan**
* Controlled inference rate to avoid thermal throttling
* Clean **machine-readable JSON output**
* Simple calibration and tuning
* Robotics-friendly features (distance + grasp point)

---

## Features

* ✅ Real-time **multi-object detection** (YOLOv8n)
* ✅ **JSON output** for all detected objects
* ✅ **Target class filtering**
* ✅ **Distance estimation (cm)** using object width + focal length
* ✅ **Grasp point calculation**
* ✅ Optional live visualization window
* ✅ Configurable inference throttling
* ✅ Focal length calibration mode
* ✅ Lock-loss timeout protection

---

## Hardware Tested

* Raspberry Pi 5 (4GB / 8GB)
* Raspberry Pi Camera Module (v2 / v3 / USB webcam)
* **No heatsink, no fan**

> ⚠️ If you add active cooling, you may safely reduce `INFER_INTERVAL` for higher FPS.

---

## Software Requirements

* Python **3.10+**
* Raspberry Pi OS (64-bit recommended)

### Python Dependencies

```bash
pip install ultralytics opencv-python
```

`numpy` is included automatically with YOLO dependencies.

---

## Project Structure

```text
vision_base.py      # Main vision system
full.md             # Documentation (this file)
```

---

## Configuration

Edit the constants at the top of `vision_base.py`:

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

### Runtime Controls

```python
SHOW_CAMERA = True

INFER_INTERVAL = 0.35        # Higher = cooler
VISION_UPDATE_INTERVAL = 0.01
```

### Camera Geometry

```python
CAMERA_HFOV_DEG = 78.0
```

Used for distance estimation.

### Grasp Point Offset

```python
GRASP_OFFSET_X = 0
GRASP_OFFSET_Y = 20
```

Offsets grasp point downward from object center (useful for bottles, cups, tools).

### Object Lock Protection

```python
LOCK_LOST_TIMEOUT = 1.0
```

Automatically releases stale detections.

### Target Classes

```python
TARGET_CLASSES = ["bottle", "cup", "cell phone"]
```

Only objects in this list appear in JSON output.

---

## Usage

Run the vision system:

```bash
python vision_base.py
```

### While Running

* JSON output printed every **0.5 seconds**
* Optional camera window with overlays

### Keyboard Controls

| Key | Action                         |
| --- | ------------------------------ |
| `q` | Quit program                   |
| `r` | Reset target lock              |
| `c` | Start focal-length calibration |

---

## Visualization Overlay (Optional)

If `SHOW_CAMERA = True`:

* Bounding boxes for detected objects
* **Red circle** → grasp point
* FPS display (top-left)

Disable for headless or maximum performance.

---

## JSON Output Format

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

| Field          | Meaning                 |
| -------------- | ----------------------- |
| `name`         | Object class            |
| `confidence`   | YOLO confidence score   |
| `distance_cm`  | Estimated distance      |
| `center`       | Object center (pixels)  |
| `grasp_center` | Recommended grasp point |
| `fps`          | Current inference FPS   |
| `timestamp`    | UNIX timestamp          |

---

## Distance Estimation Notes

* Based on **horizontal FOV + bounding box width**
* Requires correct `CAMERA_HFOV_DEG`
* Accuracy improves after calibration
* Intended for **robot guidance**, not metrology

---

## Calibration Mode

1. Place a known-width object at a known distance
2. Press `c`
3. Follow terminal instructions
4. Update focal length constant

Recalibration recommended if camera or resolution changes.

---

## Performance & Thermal Safety

Typical values on Raspberry Pi 5 (no cooling):

* Resolution: **640×480**
* YOLO input: **320×320**
* FPS: **5–8**
* CPU temp: **< 75°C**

> Pushing FPS higher **will throttle** without cooling. This design avoids that.

---

## Intended Use Cases

* Robotics vision pipeline
* Object-aware grasping
* Edge AI experiments
* Embedded AI research
* Headless vision services

---

## Non-Goals

* High-speed tracking
* Multi-camera fusion
* Sub-centimeter accuracy
* GPU acceleration (Pi-only)

---

## License

MIT License — use, modify, and integrate freely.

---

## Final Notes

This project prioritizes **stability over raw speed**.

If you want higher FPS, add cooling or move inference to:

* Coral TPU
* Jetson Nano / Orin
* Desktop GPU

For Raspberry Pi 5 **alone**, this is the realistic sweet spot.
