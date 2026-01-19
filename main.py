from flask import Flask, request
import time
import serial
import numpy as np
from scipy.optimize import fsolve

# ================= SERIAL =================
PORT = "/dev/ttyUSB0"
BAUD = 115200
ser = serial.Serial(PORT, BAUD, timeout=0.1, exclusive=True)
time.sleep(2)

def move_joint(joint, angle):
    cmd = f"J {joint} {int(angle)}\n"
    ser.write(cmd.encode())
    print("Sent:", cmd.strip())

def apply_angles(angles):
    for i, a in enumerate(angles):
        move_joint(i, a)
        time.sleep(0.05)

# ================= IK =================
def solve_angles_deg(D, theta, task):
    d = D - 20
    x4_deg = 60
    x0_deg = theta

    def x5(task):
        return 80 if task == "grab" else 190

    def eq(vars):
        x1, x2 = vars
        return [
            10.5*np.cos(x1) + 12.5*np.cos(x2) - d,
            10.5*np.sin(x1) + 12.5*np.sin(x2)
        ]

    x1, x2 = fsolve(eq, np.radians([30, -30]))
    x1 = np.degrees(x1)
    x2 = np.degrees(x2)

    x3 = x1 + x2
    x1 = 1.11 * x1
    x2 = abs(x2 - 60)
    x3 = 1.16667 * x3 + 140

    return [x0_deg, x1, x2, x3, x4_deg, x5(task)]

# ================= PLANNER =================
def execute_plan(plan):
    for step in plan:
        if step["action"] == "pick":
            z = step["grasp"]["z_cm"]
            theta = step["grasp"]["degree"]
            angles = solve_angles_deg(z, theta, "grab")
            apply_angles(angles)

        elif step["action"] == "place":
            z = step["reference"]["z_cm"]
            theta = step["reference"]["degree"]
            angles = solve_angles_deg(z, theta, "place")
            apply_angles(angles)

# ================= FLASK =================
app = Flask(__name__)

@app.route("/robot", methods=["POST"])
def robot():
    data = request.get_json(force=True)
    print("RECEIVED:", data)

    try:
        execute_plan(data["plan"])
        return "OK", 200
    except Exception as e:
        return str(e), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
