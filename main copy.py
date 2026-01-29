from flask import Flask, request, jsonify
import time
import serial
import threading
import queue
import numpy as np

from utils.ik_solver import solve_angles_deg


PORT = "/dev/ttyUSB1"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=0.1, exclusive=True)
time.sleep(2)

SERIAL_LOCK = threading.Lock()

def send(cmd):
    with SERIAL_LOCK:
        ser.write(cmd.encode())
        print("[SERIAL]", cmd.strip())

def move_joint(joint, angle):
    angle = int(np.clip(angle, JOINT_LIMITS[joint][0], JOINT_LIMITS[joint][1]))
    send(f"J {joint} {angle}\n")


JOINT_LIMITS = {
    0: (-180, 180),
    1: (0, 320),
    2: (0, 320),
    3: (60, 320),
    4: (-130, 320),
    
}

SAFE_Z = 20
MAX_Z = 38


def apply_ik(x, z):
    z = float(np.clip(z, 10, MAX_Z))
    x = float(x)

    angles = solve_angles_deg(z, x)  

    for i, a in enumerate(angles):
        move_joint(i, a)
        time.sleep(0.05)


def set_default_position():
    move_joint(4, 40)
    move_joint(3, 210)
    move_joint(2, 220)
    move_joint(1, 100)
    move_joint(0, 120)
    time.sleep(0.4)


def set_give_position():
    move_joint(2, 130)
    move_joint(3, 180)
    move_joint(1, 100)
    time.sleep(0.4)


TASK_QUEUE = queue.Queue()
STOP_EVENT = threading.Event()


def execute_step(step):
    if STOP_EVENT.is_set():
        return

    action = step["action"]
    x = float(step.get("x", 0))
    z = float(step.get("z", SAFE_Z))

    apply_ik(x, SAFE_Z)
    time.sleep(0.2)

    if STOP_EVENT.is_set():
        return

    if action == "pick":
        apply_ik(x, z)
        time.sleep(1.0)

    elif action == "place":
        apply_ik(x, z)
        time.sleep(0.6)

    elif action == "give":
        apply_ik(x, z)
        time.sleep(0.6)
        set_give_position()
        time.sleep(2.0)

    else:
        return

    apply_ik(x, SAFE_Z)
    time.sleep(0.2)


def worker():
    set_default_position()

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
        finally:
            time.sleep(0.4)
            set_default_position()
            TASK_QUEUE.task_done()


threading.Thread(target=worker, daemon=True).start()


app = Flask(__name__)

@app.route("/robot", methods=["POST"])
def robot():
    data = request.get_json(force=True, silent=True)

    if not data or "plan" not in data:
        return jsonify({"error": "invalid"}), 400

    if not isinstance(data["plan"], list):
        return jsonify({"error": "plan must be list"}), 400

    TASK_QUEUE.put(data["plan"])
    return jsonify({"status": "accepted"}), 202


@app.route("/stop", methods=["POST"])
def stop():
    STOP_EVENT.set()
    set_default_position()
    return jsonify({"status": "stopped"}), 200


if __name__ == "__main__":
    print("[SYSTEM] Russparry Online")
    app.run(host="0.0.0.0", port=900)
