import math
import numpy as np
from scipy.optimize import fsolve



def solve_angles_deg(D,theta,task):
    initial_guess_deg=(30, -30)
    d = D-20  # adjust for base offset
    x4_deg = 30
    x0_deg = theta 
   
   
    initial_guess = np.radians(initial_guess_deg)

    def set_x5_angle(task):
        if task == 'grab':
            return 80
        elif task == 'place':
            return 190
        else:
            raise ValueError("Invalid task")

    x5_deg = set_x5_angle(task)
    

    def equationsforBig(vars):
        x1, x2 = vars
        eq1 = 10.5*np.cos(x1) + 12.5*np.cos(x2) - d
        eq2 = 10.5*np.sin(x1) + 12.5*np.sin(x2)
 
        return [eq1, eq2]
    def equationsforSmall(vars):
        x1, x2 = vars
        eq1 = 8.5*np.cos(x1) + 10.5*np.cos(x2) - d
        eq2 = 8.5*np.sin(x1) + 10.5*np.sin(x2)
 
        return [eq1, eq2]
    # solve in radians
    if(D>20 and D<40):
        x1_rad, x2_rad = fsolve(equationsforBig, initial_guess) 
        x1_deg = np.degrees(x1_rad)
        x2_deg = np.degrees(x2_rad)
        print("DEGREE",x1_deg,x2_deg)
         # calculate wrist angle    
        x3_deg = x1_deg+x2_deg
        x1_deg = 1.11*x1_deg
        x2_deg = x2_deg*(-1.11)+60
        x3_deg = 1.16667*x3_deg+150

        return x0_deg,x1_deg, x2_deg, x3_deg,x4_deg,x5_deg
    elif(D>=5 and D<=20):
        x1_rad, x2_rad = fsolve(equationsforSmall, initial_guess)
        return 0,0,0,0,0,0
    
    if d < 5 or d > 40:
        raise ValueError("Out of workspace")

    else:
        raise ValueError("Out of my buget range.")
    
    # convert to degrees



# Desired horizontal distance in cm

# x0_deg,x1_deg, x2_deg, x3_deg,x4_deg,x5_deg = solve_angles_deg(30,90,'grab')
# print(f"x0 = {x0_deg:.2f}°")
# print(f"x1 = {x1_deg:.2f}°")
# print(f"x2 = {x2_deg:.2f}°")
# print(f"x3 = {x3_deg:.2f}°")
# print(f"x4 = {x4_deg:.2f}°")
# print(f"x5 = {x5_deg:.2f}°")