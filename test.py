import serial, time

ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)

# ser = serial.Serial("/dev/ttyAMA10", 115200, timeout=1)
time.sleep(2)

ser.write(b"J 0 45\n")
ser.write(b"J 1 120\n")
ser.write(b"J 2 90\n")
