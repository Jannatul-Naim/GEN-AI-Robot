from flask import Flask, request, jsonify
import time
import serial
import threading
import queue
import numpy as np

from utils.calculation import solve_angles_deg




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
    0: (-180, 180),   # base
    1: (0, 320),     # shoulder
    2: (0, 320),     # elbow
    3: (60, 320),    # wrist
    4: (-130, 320),  # wrist rotate
    5: (60, 200)     # gripper
}

SAFE_HEIGHT_CM = 20
MAX_REACH_CM = 45




def set_default_position():
    print("[ROBOT] Moving to default position")
    move_joint(5, 150)
    move_joint(4, -90)
    move_joint(3, 210)
    move_joint(2, 220)
    move_joint(1, 100)
    move_joint(0, 120)
    time.sleep(0.5)




TASK_QUEUE = queue.Queue()
STOP_EVENT = threading.Event()

def execute_step(step):
    if STOP_EVENT.is_set():
        return

    action = step["action"]

    # Extract z/theta safely
    ref = step.get("grasp") or step.get("reference") or {}
    z = float(ref.get("z_cm", SAFE_HEIGHT_CM))
    theta = float(ref.get("degree", 0))

    # Clamp workspace
    z = np.clip(z, 5, MAX_REACH_CM)

    # 1️⃣ Move to SAFE HEIGHT first
    apply_angles(solve_angles_deg(SAFE_HEIGHT_CM, theta, "grab"))
    time.sleep(0.25)

    if STOP_EVENT.is_set():
        return

    # 2️⃣ Execute action
    if action == "pick":
        apply_angles(solve_angles_deg(z, theta, "grab"))
        time.sleep(0.4)

    elif action == "place":
        apply_angles(solve_angles_deg(z, theta, "place"))
        time.sleep(0.4)

    elif action == "give":
        apply_angles(solve_angles_deg(z, theta, "grab"))
        time.sleep(0.4)
        apply_angles(solve_angles_deg(z, theta, "place"))
        time.sleep(0.4)

    else:
        raise ValueError(f"Unknown action: {action}")

    # 3️⃣ Retreat back to SAFE HEIGHT
    apply_angles(solve_angles_deg(SAFE_HEIGHT_CM, theta, "grab"))
    time.sleep(0.25)


def worker():
    print("[ROBOT] Worker started")
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

        except Exception as e:
            print("[ROBOT ERROR]", e)

        finally:
            set_default_position()
            TASK_QUEUE.task_done()

threading.Thread(target=worker, daemon=True).start()



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
    set_default_position()
    return jsonify({"status": "STOPPED"}), 200




if __name__ == "__main__":
    print("[SYSTEM] Russparry Robot Controller Online")
    app.run(host="0.0.0.0", port=9000)
