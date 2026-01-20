from flask import Flask, request, jsonify
import time
import serial
import threading
import queue
import numpy as np
from scipy.optimize import fsolve


PORT = "/dev/ttyUSB0"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=0.1, exclusive=True)
time.sleep(2)

SERIAL_LOCK = threading.Lock()

def send(cmd: str):
    with SERIAL_LOCK:
        ser.write(cmd.encode())
        print("[SERIAL]", cmd.strip())

def move_joint(joint: int, angle: float):
    angle = int(np.clip(angle, JOINT_LIMITS[joint][0], JOINT_LIMITS[joint][1]))
    send(f"J {joint} {angle}\n")

def apply_angles(angles):
    for i, a in enumerate(angles):
        move_joint(i, a)
        time.sleep(0.06)


JOINT_LIMITS = {
    0: (-180, 180),     # base
    1: (0, 320),      # shoulder
    2: (0, 320),      # elbow
    3: (60, 320),     # wrist
    4: (-130, 320),     # wrist rotate
    5: (60, 200)      # gripper
}

MAX_REACH_CM = 45
SAFE_HEIGHT_CM = 20

from utils.calculation import solve_angles_deg


TASK_QUEUE = queue.Queue()
STOP_EVENT = threading.Event()

def execute_step(step):
    action = step["action"]

    if action == "pick":
        z = step["grasp"]["z_cm"]
        theta = step["grasp"]["degree"]
        apply_angles(solve_angles_deg(z, theta, "grab"))

    elif action == "place":
        z = step["reference"]["z_cm"]
        theta = step["reference"]["degree"]
        apply_angles(solve_angles_deg(z, theta, "place"))

    elif action == "give":
        z = step["reference"]["z_cm"]
        theta = step["reference"]["degree"]
        apply_angles(solve_angles_deg(z, theta, "grab"))
        time.sleep(0.6)
        apply_angles(solve_angles_deg(z, theta, "place"))

    else:
        raise ValueError("Unknown action")

def set_default_position():
    move_joint(5, 150)
    move_joint(4, -90)
    move_joint(3, 210)
    move_joint(2, 220)
    move_joint(1, 100)
    move_joint(0, 120)
def worker():
    print("[ROBOT] Worker started")
    while not STOP_EVENT.is_set():
        try:
            plan = TASK_QUEUE.get(timeout=0.1)
        except queue.Empty:
            continue

        try:
            for step in plan:
                if STOP_EVENT.is_set():
                    break
                execute_step(step)
        except Exception as e:
            print("[ROBOT ERROR]", e)
        finally:
            TASK_QUEUE.task_done()

threading.Thread(target=worker, daemon=True).start()

# ============================================================
# FLASK API
# ============================================================
app = Flask(__name__)

@app.route("/robot", methods=["POST"])
def robot():
    data = request.get_json(force=True, silent=True)
    if not data or "plan" not in data:
        return jsonify({"error": "Invalid request"}), 400

    if not isinstance(data["plan"], list):
        return jsonify({"error": "Plan must be a list"}), 400

    TASK_QUEUE.put(data["plan"])
    return jsonify({"status": "accepted"}), 202

@app.route("/stop", methods=["POST"])
def stop():
    STOP_EVENT.set()
    return jsonify({"status": "STOPPED"}), 200
def test_move():
    set_default_position()
    x = int(input("Enter distance in cm (10-45): "))
    theta = int(input("Enter angle in degrees (-90 to 90): "))
    try:
        angles = solve_angles_deg(x, theta, "grab")
        print("Moving to:", angles)
        apply_angles(angles)
    except Exception as e:
        print("Error:", e)
    time.sleep(30)
# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    # print("[SYSTEM] Russparry Robot Controller Online")
    # app.run(host="0.0.0.0", port=9000)
    while True:
        test_move()