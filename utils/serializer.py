import serial
import time

PORT = "/dev/ttyUSB0"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=0.1)
time.sleep(2)

def move_joint(joint, angle):
    cmd = f"J {joint} {angle}\n"
    ser.write(cmd.encode()) 
    print("Sent:", cmd.strip())

def set_default_position():
    move_joint(5, )
    move_joint(4, 60)
    move_joint(3, 210)
    move_joint(2, 220)
    move_joint(1, 100)
    move_joint(0, 120)

set_default_position()

time.sleep(0.2)
while ser.in_waiting:
    print("ESP32:", ser.readline().decode(errors="ignore").strip())

while True:
    joint = int(input("Joint (0-5): "))
    angle = int(input("Angle (0-180): "))
    if 0 <= joint <= 5 and 0 <= angle <= 240:
        move_joint(joint, angle)