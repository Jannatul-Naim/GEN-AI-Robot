import numpy as np

L1 = 10.5
L2 = 12.5

def solve_angles_deg(z, x):
    x = float(x)   # left/right
    z = float(z)   # radial distance

    # ---------- BASE ----------
    theta0 = np.arcsin(x / z) if z != 0 else 0.0
    
    # ---------- PLANAR DISTANCE ----------
    r = np.clip(z, 6.0, L1 + L2 - 0.5)

    # ---------- ELBOW ----------
    c2 = (r*r - L1*L1 - L2*L2) / (2*L1*L2)
    c2 = np.clip(c2, -1.0, 1.0)
    theta2 = np.arccos(c2)

    # ---------- SHOULDER ----------
    phi = 0.0
    psi = np.arctan2(L2*np.sin(theta2),
                     L1 + L2*np.cos(theta2))
    theta1 = phi - psi

    # ---------- WRIST ----------
    theta3 = -(theta1 + theta2)

    return (
        int(theta0),
        int(np.degrees(theta1)),
        int(np.degrees(theta2)),
        int(np.degrees(theta3))
    )
def test():
    print(solve_angles_deg(10, 10))

test()
