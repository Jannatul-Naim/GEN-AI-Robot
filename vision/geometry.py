import math
import numpy as np
from config import *

class Geometry:
    def __init__(self):
        self.fx = (CAM_WIDTH / 2) / math.tan(math.radians(CAMERA_HFOV_DEG / 2))
        self.fy = self.fx
        self.cx = CAM_WIDTH / 2
        self.cy = CAM_HEIGHT / 2

    def pixel_to_world(self, px, py, box_width_px, class_name):
        """
        Returns X, Y, Z in cm
        Assumes object touches ground plane
        """

        
        theta = math.atan((px - self.cx) / self.fx)

        
        phi = math.atan((py - self.cy) / self.fy)
        total_phi = phi + math.radians(CAMERA_TILT_DEG)

        if total_phi <= 0:
            return None

        
        Z_ground = CAMERA_HEIGHT_CM / math.tan(total_phi)

        
        real_w = OBJECT_WIDTHS_CM.get(class_name, 8.0)
        Z_width = (real_w * self.fx) / max(box_width_px, 2)

        
        Z = 0.75 * Z_ground + 0.25 * Z_width

        X = Z * math.tan(theta)

        return {
            "x_cm": round(X, 2),
            "y_cm": 0.0,
            "z_cm": round(Z, 2)
        }
