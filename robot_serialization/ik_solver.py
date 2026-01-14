import numpy as np

# ------------------ ROTATION + TRANSFORMS ------------------

def axis_angle_rot_matrix(k, q):
    k = np.array(k, dtype=float)
    k = k / np.linalg.norm(k)

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
    H = np.block([[R, t],
                  [0,0,0,1]])
    return H

# ------------------ ROBOT ARM CLASS ------------------

class RoboticArm:
    def __init__(self, k, t, limits_deg):
        self.k = np.array(k)
        self.t = np.array(t)
        self.N = len(k)
        self.limits = np.radians(limits_deg)

    def fk(self, Q, p_i=[0,0,0], index=None):
        if index is None:
            index = self.N - 1

        p = np.array([*p_i,1]).reshape(4,1)
        for i in range(index, -1, -1):
            p = hr_matrix(self.k[i], self.t[i], Q[i]) @ p

        return p[:3].flatten()

    def jacobian(self, Q, p_eff):
        p_end = self.fk(Q, p_eff)
        J = np.zeros((3, self.N))

        for i in range(self.N):
            p_i = self.fk(Q, index=i)
            k_i = self.k[i]
            J[:,i] = np.cross(k_i, p_end - p_i)

        return J

    def ik(self, q0, p_eff, goal, steps=800):
        Q = q0.copy()

        for _ in range(steps):
            p = self.fk(Q, p_eff)
            err = goal - p
            if np.linalg.norm(err) < 0.5:
                break

            J = self.jacobian(Q, p_eff)

            # Damped least squares (VERY important)
            lam = 0.1
            Jinv = J.T @ np.linalg.inv(J @ J.T + lam*np.eye(3))

            dQ = Jinv @ (0.05 * err)

            Q += np.clip(dQ, -0.1, 0.1)

            # Enforce servo limits
            for i in range(self.N):
                Q[i] = np.clip(Q[i], self.limits[i][0], self.limits[i][1])

        return np.degrees(Q)

# ------------------ MAIN ------------------

if __name__ == "__main__":

    # Link lengths (cm)
    L1 = 9.5
    L2 = 10.5
    L3 = 12.5
    L4 = 7.0
    L5 = 6.0   # end-effector offset

    k = [
        [0,0,1],  # base
        [0,1,0],  # extra shoulder
        [0,1,0],  # shoulder
        [0,1,0],  # elbow
        [0,1,0],  # wrist
    ]

    t = [
        [0,0,L1],
        [L2,0,0],
        [L3,0,0],
        [L4,0,0],
        [0,0,0],
    ]

    limits = [
        (10,170),
        (10,170),
        (10,170),
        (10,170),
        (10,120),
    ]

    arm = RoboticArm(k, t, limits)

    q_start = np.radians([90,90,90,90,60])

    p_eff = [L5,0,0]

    goal = np.array([15, 10, 12])  # cm (reachable)

    q_sol = arm.ik(q_start, p_eff, goal)

    print("\nServo Angles (degrees):")
    for i, q in enumerate(q_sol):
        print(f"Joint {i+1}: {q:.2f}")