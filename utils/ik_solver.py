import numpy as np
from scipy.optimize import least_squares

def dof3(d, h, tol=1e-4):

    def equations(x):
        x1, x2 = x
        eq1 = 10.5 + 12.5*np.cos(np.deg2rad(x1)) + 17.5*np.cos(np.deg2rad(x2)) - d
        eq2 = 12.5*np.sin(np.deg2rad(x1)) + 17.5*np.sin(np.deg2rad(x2)) - h
        return [eq1, eq2]

    lower_bounds = [0, -120]
    upper_bounds = [160, 0]

    solutions = []

    # Scan different starting guesses
    for x1_guess in np.linspace(0,120,9):
        for x2_guess in np.linspace(-120,0,9):

            sol = least_squares(
                equations,
                [x1_guess, x2_guess],
                bounds=(lower_bounds, upper_bounds)
            )

            x1, x2 = sol.x

            # --- Cross Check ---
            eq1_check = 10.5 + 12.5*np.cos(np.deg2rad(x1)) + 17.5*np.cos(np.deg2rad(x2))
            eq2_check = 12.5*np.sin(np.deg2rad(x1)) + 17.5*np.sin(np.deg2rad(x2))

            if abs(eq1_check - d) < tol and abs(eq2_check - h) < tol:

                # Check duplicate
                duplicate = False
                for s in solutions:
                    if np.linalg.norm(np.array(s)-np.array([x1,x2])) < 0.5:
                        duplicate = True
                        break

                if not duplicate:
                    solutions.append([x1, x2])

    return solutions

print(dof3(d=32, h=1))