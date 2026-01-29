# main.py (PI)
from flask import Flask, request, jsonify
import time, serial, threading, queue
import numpy as np

from utils.ik_solver import solve_angles_deg

PORT = "/dev/ttyUSB0"

BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=0.1)
time.sleep(2)

LOCK = threading.Lock()

def send(cmd):
    with LOCK:
        ser.write(cmd.encode())
        print("[SERIAL]", cmd.strip())

def move_joint(joint, angle):
    send(f"J {joint} {angle}\n")

SAFE_Z = 20
MAX_Z = 38

def apply_ik(x, z):
    z = float(np.clip(z, 8, MAX_Z))
    x = float(x)

    base, sh, el, wr = solve_angles_deg(z, x)

    move_joint(0, base)
    move_joint(1, sh)
    move_joint(2, el)
    move_joint(3, wr)
    # ❌ DO NOT TOUCH joint 4 or 5

def set_home():
    move_joint(0, 0)
    move_joint(1, 0)
    move_joint(2, 150)
    move_joint(3, -70)
    time.sleep(0.5)

TASK_QUEUE = queue.Queue()
STOP = threading.Event()

def execute(step):
    x = step.get("x", 0)
    z = step.get("z", SAFE_Z)

    apply_ik(x, SAFE_Z)
    time.sleep(0.2)

    apply_ik(x, z)
    time.sleep(0.8)

    apply_ik(x, SAFE_Z)
    time.sleep(0.2)

def worker():
    set_home()
    while not STOP.is_set():
        try:
            plan = TASK_QUEUE.get(timeout=0.1)
        except queue.Empty:
            continue

        for step in plan:
            if STOP.is_set():
                break
            execute(step)

        set_home()
        TASK_QUEUE.task_done()

threading.Thread(target=worker, daemon=True).start()

app = Flask(__name__)

@app.route("/robot", methods=["POST"])
def robot():
    data = request.get_json()
    TASK_QUEUE.put(data["plan"])
    return jsonify({"ok": True})

@app.route("/stop", methods=["POST"])
def stop():
    STOP.set()
    set_home()
    return jsonify({"stopped": True})

if __name__ == "__main__":
    print("[SYSTEM] Russparry Online")
    app.run(host="0.0.0.0", port=9000)
