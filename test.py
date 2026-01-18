# import vision.vision as vision

# vision.test_vision()  

import cv2
import glob
import numpy as np

CHECKERBOARD = (9,6)
SQUARE_SIZE = 2.5  # cm

objp = np.zeros((CHECKERBOARD[0]*CHECKERBOARD[1],3), np.float32)
objp[:,:2] = np.mgrid[0:CHECKERBOARD[0],0:CHECKERBOARD[1]].T.reshape(-1,2)
objp *= SQUARE_SIZE

objpoints = []
imgpoints = []

images = glob.glob("calib/*.jpg")  # take ~20 photos

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, None)
    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)

ret, mtx, dist, _, _ = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

print("CAMERA MATRIX:\n", mtx)
print("DIST COEFFS:\n", dist)
