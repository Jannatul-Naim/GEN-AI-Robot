import numpy as np
from scipy.optimize import fsolve

def solve_angles_deg(D, x):
    # ---------------- SAFETY ----------------
    D = float(D)
    x = float(x)

    if D <= 1e-3:
        raise ValueError("Invalid D (too small)")

    # Clamp x so acos is valid
    x = np.clip(x, -D + 1e-3, D - 1e-3)

    # ---------------- BASE ------------------
    x0_rad = np.arccos(x / D)
    x0_deg = np.degrees(x0_rad)

    # ---------------- WORKSPACE -------------
    d = D - 10
    d = np.clip(d, 5, 40)

    # ---------------- LINK LENGTHS ----------
    if D > 25:
        L1, L2 = 10.5, 12.5
    else:
        L1, L2 = 8.5, 10.5

    # ---------------- SOLVER ----------------
    def equations(v):
        a, b = v
        return [
            L1*np.cos(a) + L2*np.cos(b) - d,
            L1*np.sin(a) + L2*np.sin(b)
        ]

    guess = np.radians([40, -60])

    try:
        a1, a2 = fsolve(equations, guess, maxfev=300)
    except Exception:
        raise ValueError("IK solver failed")

    a1_deg = np.degrees(a1)
    a2_deg = np.degrees(a2)

    # ---------------- WRIST -----------------
    a3_deg = -a2_deg
    a4_deg = 60

    # ---------------- SERVO MAP -------------


    return (
        int(x0_deg),
        int(a1_deg),
        int(a2_deg),
        int(a3_deg),
        int(a4_deg)
    )
