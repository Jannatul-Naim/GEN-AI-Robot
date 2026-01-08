# Vision (YOLOv8n)

This project provides a **lightweight, thermally safe vision system** for **Raspberry Pi 5** using **YOLOv8n**.  
It is designed to run **without active cooling**, even in long sessions, and outputs **JSON for all detected objects**.

---

## Key Goals

- Stable operation on Raspberry Pi 5 (no fan, no heatsink)
- Low CPU/GPU temperature
- Multi-object detection
- Clean JSON output for robotics integration
- Camera open / close handled in code
- No ROS / ROS2 dependency

---

## Features

- Real-time object detection using **YOLOv8n**
- Outputs **JSON for all detected objects**
- Distance estimation using known object widths
- Grasp point calculation
- Target lock logic
- Adjustable inference rate for thermal safety
- Optional camera display
- Focal length calibration support

---

## Hardware Tested

- Raspberry Pi 5
- USB Camera / Pi Camera (V4L2)
- No active cooling

Expected operating temperature: **~60–70 °C**

---

## Software Requirements

- Python 3.10+
- OpenCV
- Ultralytics YOLOv8

Install dependencies:

```bash
pip install ultralytics opencv-python
