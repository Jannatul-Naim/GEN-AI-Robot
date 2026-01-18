import serial
import time
import utils.calculation as calc

PORT = "/dev/ttyUSB0"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=0.1,exclusive=True)
time.sleep(2)

def move_joint(joint, angle):
    cmd = f"J {joint} {angle}\n"
    ser.write(cmd.encode()) 
    print("Sent:", cmd.strip())

def set_default_position():
    move_joint(5, 150)
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
    D = float(input("Enter desired horizontal distance (cm) between 20 and 40: "))
    try:
        x1_deg, x2_deg, x3_deg = calc.solve_angles_deg(D)
        print(f"Calculated angles: x1 = {x1_deg:.2f}°, x2 = {x2_deg:.2f}°, x3 = {x3_deg:.2f}°")

        move_joint(1, int(x1_deg))
        move_joint(2, int(x2_deg))
        move_joint(3, int(x3_deg))

        time.sleep(0.2)
        while ser.in_waiting:
            print("ESP32:", ser.readline().decode(errors="ignore").strip())
    except ValueError as e:
        print(e)