
import numpy as np
from scipy.optimize import least_squares

class IK:
    def __init__(self, l1=12.5, l2=10.5, l3=17.5):
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3

    def solve_d(self, z, y , tol=1e-4):

        def equations(x):
            x1, x2 = x

            eq1 = self.l2 + \
                  self.l1*np.cos(np.deg2rad(x1)) + \
                  self.l3*np.cos(np.deg2rad(x2)) - z

            eq2 = self.l1*np.sin(np.deg2rad(x1)) + \
                  self.l3*np.sin(np.deg2rad(x2)) - y

            return [eq1, eq2]

        lower_bounds = [0, -120]
        upper_bounds = [160, 0]

        solutions = []

        for x1_guess in np.linspace(0, 120, 9):
            for x2_guess in np.linspace(-120, 0, 9):

                sol = least_squares(
                    equations,
                    [x1_guess, x2_guess],
                    bounds=(lower_bounds, upper_bounds)
                )

                x1, x2 = sol.x


                check = equations([x1, x2])

                if abs(check[0]) < tol and abs(check[1]) < tol:

                    duplicate = False
                    for s in solutions:
                        if np.linalg.norm(np.array(s) - np.array([x1, x2])) < 0.5:
                            duplicate = True
                            break

                    if not duplicate:
                        solutions.append([x1, x2])
        return solutions
    
    def solve(self, x, y, z):
        planar_solutions = self.solve_d(z, y)
        theta0 = self.solve_theta(x, z)
        full_solutions = []

        for x1, x2 in planar_solutions:
            theta1, theta2, theta3 = self.expand_to_full_angles(x1, x2)
            full_solutions.append((int(theta0), int(theta1), int(theta2), int(theta3)))

        return full_solutions

    
    def solve_theta(self, x, z):
        if x == 0:
            return 0
        theta = np.degrees(np.arctan(z/ x))
        return theta

    def expand_to_full_angles(self, x1, x2):
        theta1 = x1
        theta2 = -x1
        theta3 = x2
        return theta1, theta2, theta3


def test_ik():
    ik = IK()
    x, y, z = 10, 0, 30
    solutions = ik.solve(x, y, z)
    print(f"Target: ({x}, {y}, {z})")
    for idx, (theta0, theta1, theta2, theta3) in enumerate(solutions):
        print(f"Solution {idx+1}: θ0={theta0}°, θ1={theta1}°, θ2={theta2}°, θ3={theta3}°")

