// #include <Wire.h>
// #include <Adafruit_PWMServoDriver.h>

// Adafruit_PWMServoDriver pca = Adafruit_PWMServoDriver(0x40);

// // Servo limits (SAFE)
// int minAngle[6] = {25, 0, 0, 0, 0, 0};
// int maxAngle[6] = {100, 130, 180, 180, 180, 180};

// // Servo pulse limits
// #define SERVO_MIN 102
// #define SERVO_MAX 512

// int angleToPulse(int angle) {
//   return map(angle, 0, 180, SERVO_MIN, SERVO_MAX);
// }

// void moveServo(int id, int angle) {
//   if (id < 0 || id > 5) return;

//   angle = constrain(angle, minAngle[id], maxAngle[id]);
//   int pulse = angleToPulse(angle);
//   pca.setPWM(id, 0, pulse);
// }

// void setup() {
//   Serial.begin(115200);
//   Wire.begin(21, 22);

//   pca.begin();
//   pca.setPWMFreq(50);

//   delay(1000);

//   // Safe startup pose
//   for (int i = 0; i < 6; i++) {
//     moveServo(i, minAngle[i]);
//     delay(200);
//   }

//   Serial.println("ESP32 READY");
// }

// void loop() {
//   if (!Serial.available()) return;

//   String cmd = Serial.readStringUntil('\n');
//   cmd.trim();

//   // Joint command: J id angle
//   if (cmd.startsWith("J")) {
//     int id, angle;
//     sscanf(cmd.c_str(), "J %d %d", &id, &angle);
//     moveServo(id, angle);
//   }

//   // All joints command: A a1 a2 a3 a4 a5 a6
//   if (cmd.startsWith("A")) {
//     int a[6];
//     sscanf(cmd.c_str(), "A %d %d %d %d %d %d",
//            &a[0], &a[1], &a[2], &a[3], &a[4], &a[5]);

//     for (int i = 0; i < 6; i++) {
//       moveServo(i, a[i]);
//       delay(50);  // smooth motion
//     }
//   }
// }
// #include <Wire.h>
// #include <Adafruit_PWMServoDriver.h>

// #define SDA_PIN 21
// #define SCL_PIN 22

// #define SERVO_FREQ 50

// // MG996R pulse range
// #define SERVO_MIN_US 600
// #define SERVO_MAX_US 2400

// Adafruit_PWMServoDriver pwm(0x40);

// // Joint channels
// enum {
//   BASE = 0,
//   SHOULDER1,
//   SHOULDER2,
//   ELBOW,
//   WRIST,
//   GRIPPER
// };

// // Safe angle limits
// int jointMin[6] = {10, 10, 10, 10, 10, 20};
// int jointMax[6] = {170,170,170,170,170, 90};

// uint16_t usToPulse(int us) {
//   return map(us, 0, 20000, 0, 4095);
// }

// void setServo(uint8_t ch, int deg) {
//   deg = constrain(deg, jointMin[ch], jointMax[ch]);
//   int us = map(deg, 0, 180, SERVO_MIN_US, SERVO_MAX_US);
//   pwm.setPWM(ch, 0, usToPulse(us));
// }

// void setup() {
//   Serial.begin(115200);

//   Wire.begin(SDA_PIN, SCL_PIN);
//   pwm.begin();
//   pwm.setPWMFreq(SERVO_FREQ);
//   delay(300);

//   // Home position
//   for (int i = 0; i < 6; i++)
//     setServo(i, 90);

//   setServo(GRIPPER, 40);

//   Serial.println("ESP32 Servo Controller Ready");
// }

// void processJointCmd(int id, int deg) {
//   if (id < 0 || id > 5) return;
//   setServo(id, deg);
// }

// void processAllCmd(int *v) {
//   for (int i = 0; i < 6; i++)
//     setServo(i, v[i]);
// }

// void loop() {
//   if (Serial.available()) {
//     String cmd = Serial.readStringUntil('\n');
//     cmd.trim();

//     if (cmd.startsWith("J")) {
//       int id, deg;
//       sscanf(cmd.c_str(), "J %d %d", &id, &deg);
//       processJointCmd(id, deg);
//     }

//     else if (cmd.startsWith("A")) {
//       int v[6];
//       if (sscanf(cmd.c_str(),
//           "A %d %d %d %d %d %d",
//           &v[0], &v[1], &v[2],
//           &v[3], &v[4], &v[5]) == 6) {
//         processAllCmd(v);
//       }
//     }
//   }
// }
#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 SERIAL TEST READY");
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    Serial.print("RECEIVED CMD: ");
    Serial.println(cmd);

    if (cmd.startsWith("J")) {
      int id, deg;
      sscanf(cmd.c_str(), "J %d %d", &id, &deg);

      Serial.print("Joint Command -> ID: ");
      Serial.print(id);
      Serial.print("  DEG: ");
      Serial.println(deg);
    }

    else if (cmd.startsWith("A")) {
      int v[6];
      int count = sscanf(cmd.c_str(),
        "A %d %d %d %d %d %d",
        &v[0], &v[1], &v[2],
        &v[3], &v[4], &v[5]);

      Serial.print("All Joints Count: ");
      Serial.println(count);

      if (count == 6) {
        for (int i = 0; i < 6; i++) {
          Serial.print("J");
          Serial.print(i);
          Serial.print(": ");
          Serial.println(v[i]);
        }
      }
    }
  }
}