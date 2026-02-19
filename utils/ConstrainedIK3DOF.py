
import numpy as np
from scipy.optimize import least_squares

class ConstrainedIK3DOF:
    def __init__(self, l1=12.5, l2=10.5, l3=17.5):
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3

    def solve_z(self, d, h = 2, tol=1e-4):

        def equations(x):
            x1, x2 = x

            eq1 = self.l2 + \
                  self.l1*np.cos(np.deg2rad(x1)) + \
                  self.l3*np.cos(np.deg2rad(x2)) - d

            eq2 = self.l1*np.sin(np.deg2rad(x1)) + \
                  self.l3*np.sin(np.deg2rad(x2)) - h

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

    def expand_to_full_angles(self, x1, x2):
        theta1 = x1
        theta2 = -x1
        theta3 = x2
        return theta1, theta2, theta3


