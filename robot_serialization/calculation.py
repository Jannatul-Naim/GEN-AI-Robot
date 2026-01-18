import math
import numpy as np
from scipy.optimize import fsolve

def solve_angles_deg(D, initial_guess_deg=(30, -30)):
    # convert initial guess to radians
    initial_guess = np.radians(initial_guess_deg)


    def equationsforBig(vars):
        x1, x2 = vars
        eq1 = 10.5*np.cos(x1) + 12.5*np.cos(x2) - D
        eq2 = 10.5*np.sin(x1) + 12.5*np.sin(x2)
    
        return [eq1, eq2]

    # solve in radians
    if(D>20):
        x1_rad, x2_rad = fsolve(equationsforBig, initial_guess)    
    

    # convert to degrees
    x1_deg = np.degrees(x1_rad)
    x2_deg = np.degrees(x2_rad)

    return x1_deg, x2_deg,x1_deg+x2_deg

D = 10.5 
# Desired horizontal distance in cm
x1_deg, x2_deg, x3_deg = solve_angles_deg(D)
x1_deg = 1.11*x1_deg 
x2_deg = abs(x2_deg-60)
x3_deg = 1.16667*x3_deg+140

print(f"x1 = {x1_deg:.2f}°")
print(f"x2 = {x2_deg:.2f}°")
print(f"x3 = {x3_deg:.2f}°")
