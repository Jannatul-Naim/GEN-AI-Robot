import serial
import time
from serial import SerialException

ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)
time.sleep(2)

ser.write(b"J 0 90\n")

time.sleep(0.2)

try :
    while ser.in_waiting:
        print("ESP32:", ser.readline().decode().strip())
except SerialException:
    pass