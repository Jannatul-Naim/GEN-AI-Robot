import numpy as np
import serial
import time

# ============================================================
# ROTATION + TRANSFORMS
# ============================================================

def axis_angle_rot_matrix(k, q):
    k = np.array(k, dtype=float)
    k /= np.linalg.norm(k)

    c = np.cos(q)
    s = np.sin(q)
    v = 1 - c

    kx, ky, kz = k

    return np.array([
        [kx*kx*v + c,     kx*ky*v - kz*s, kx*kz*v + ky*s],
        [ky*kx*v + kz*s,  ky*ky*v + c,    ky*kz*v - kx*s],
        [kz*kx*v - ky*s,  kz*ky*v + kx*s, kz*kz*v + c   ]
    ])

def hr_matrix(k, t, q):
    R = axis_angle_rot_matrix(k, q)
    t = np.array(t).reshape(3,1)
    return np.block([
        [R, t],
        [0,0,0,1]
    ])

# ============================================================
# ROBOT ARM CLASS
# ============================================================

class RoboticArm:
    def __init__(self, k, t, limits_deg):
        self.k = np.array(k)
        self.t = np.array(t)
        self.N = len(k)
        self.limits = np.radians(limits_deg)

    def fk(self, Q, p_i=[0,0,0], index=None):
        if index is None:
            index = self.N - 1

        p = np.array([*p_i, 1.0]).reshape(4,1)

        for i in range(index, -1, -1):
            p = hr_matrix(self.k[i], self.t[i], Q[i]) @ p

        return p[:3].flatten()

    def jacobian(self, Q, p_eff):
        p_end = self.fk(Q, p_eff)
        J = np.zeros((3, self.N))

        R = np.eye(3)

        for i in range(self.N):
            if i > 0:
                R = axis_angle_rot_matrix(self.k[i-1], Q[i-1]) @ R

            k_world = R @ self.k[i]
            p_i = self.fk(Q, index=i)
            J[:, i] = np.cross(k_world, p_end - p_i)

        return J

    def ik(self, q0, p_eff, goal, steps=1000):
        Q = q0.copy()

        max_reach = np.sum(np.linalg.norm(self.t, axis=1)) + np.linalg.norm(p_eff)
        if np.linalg.norm(goal) > max_reach:
            print("❌ Target unreachable")
            return np.degrees(Q)

        for _ in range(steps):
            p = self.fk(Q, p_eff)
            err = goal - p

            if np.linalg.norm(err) < 0.5:
                break

            J = self.jacobian(Q, p_eff)

            lam = 0.1
            Jinv = J.T @ np.linalg.inv(J @ J.T + lam*np.eye(3))

            dQ = Jinv @ (0.05 * err)
            Q += np.clip(dQ, -0.08, 0.08)

            for i in range(self.N):
                Q[i] = np.clip(Q[i], self.limits[i][0], self.limits[i][1])

        return np.degrees(Q)

# ============================================================
# SERIAL COMMUNICATION
# ============================================================

PORT = "/dev/ttyUSB0"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=0.1)
time.sleep(2)

def move_joint(joint, angle):
    angle = int(np.clip(angle, 0, 180))
    cmd = f"J {joint} {angle}\n"
    ser.write(cmd.encode())
    print("Sent:", cmd.strip())

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # --------- Robot geometry (cm) ---------
    L1 = 9.5
    L2 = 10.5
    L3 = 12.5
    L4 = 7.0
    L5 = 6.0

    k = [
        [0,0,1],   # base yaw
        [0,1,0],   # shoulder pitch
        [0,1,0],
        [1,0,0],
        [0,1,0],
    ]

    t = [
        [0,0,L1],
        [0,0,0],
        [L2,0,0],
        [L3,0,0],
        [L4,0,0],
    ]

    limits = [
        (10,170),
        (10,170),
        (10,170),
        (10,170),
        (10,120),
    ]

    arm = RoboticArm(k, t, limits)

    q_start = np.radians([90, 90, 90, 90, 90])
    p_eff = [L5, 0, 0]

    print("\n=== Cartesian Control Mode ===")
    print("Enter target position in cm (Ctrl+C to exit)\n")

    while True:
        try:
            x = float(input("X : "))
            y = float(input("Y : "))
            z = float(input("Z : "))

            goal = np.array([x, y, z])

            q_sol = arm.ik(q_start, p_eff, goal)

            print("\nServo Angles (deg):")
            for i, q in enumerate(q_sol):
                print(f"Joint {i}: {q:.2f}")

            for i in range(5):
                move_joint(i, q_sol[i])
                time.sleep(1.5)

            q_start = np.radians(q_sol)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
