import serial
import time
import sys

PORT = "/dev/ttyUSB0"
BAUD = 115200

ser = None

def move_joint(joint, angle):
    cmd = f"J {joint} {angle}\n"
    ser.write(cmd.encode())
    print("Sent:", cmd.strip())

def move_all(angles):
    cmd = "A " + " ".join(map(str, angles)) + "\n"
    ser.write(cmd.encode())
    print("Sent:", cmd.strip())

try:
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    time.sleep(2)

    # ========= TEST =========
    move_joint(0, 120)
    time.sleep(0.5)

    while ser.in_waiting:
        print("ESP32:", ser.readline().decode(errors="ignore").strip())

    # ========= INTERACTIVE LOOP =========
    while True:
        joint = int(input("Joint (0-5): "))
        angle = int(input("Angle (0-180): "))

        if 0 <= joint <= 5 and 0 <= angle <= 180:
            move_joint(joint, angle)
        else:
            print("❌ Invalid joint or angle")

except KeyboardInterrupt:
    print("\n🛑 Interrupted by user (Ctrl+C)")

except Exception as e:
    print("❌ Error:", e)

finally:
    if ser and ser.is_open:
        ser.close()
        print("✅ Serial port closed safely")
    sys.exit(0)
