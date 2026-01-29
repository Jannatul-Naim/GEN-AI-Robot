import cv2
import numpy as np

cap = cv2.VideoCapture(0)
points = []

# ===== CHANGE THIS =====
# Real-world coordinates in cm (round table, center = 0,0)
world_pts = np.array([
    [-30,  0],   # left
    [ 30,  0],   # right
    [  0, 30],   # top
    [  0,-30],   # bottom
], dtype=np.float32)

def mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
        points.append([x, y])
        print(f"Point {len(points)}: pixel = ({x}, {y})")

cv2.namedWindow("frame")
cv2.setMouseCallback("frame", mouse)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    for p in points:
        cv2.circle(frame, tuple(p), 6, (0,0,255), -1)

    cv2.imshow("frame", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()

pixel_pts = np.array(points, dtype=np.float32)
H, _ = cv2.findHomography(pixel_pts, world_pts)

np.save("homography.npy", H)
print("\nHomography saved as homography.npy")
