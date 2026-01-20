#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define SDA_PIN 21
#define SCL_PIN 22

#define SERVO_FREQ 50

// MG996R pulse range
#define SERVO_MIN_US 600
#define SERVO_MAX_US 2400

Adafruit_PWMServoDriver pwm(0x40);

// Joint channels
enum {
  BASE = 0,
  SHOULDER1,
  SHOULDER2,
  ELBOW,
  WRIST,
  GRIPPER
};

int jointMin[6] = {10, 10, 10, 10, 10, 40};
int jointMax[6] = {170,170,320,320,320, 130};

uint16_t usToPulse(int us) {
  return map(us, 0, 20000, 0, 4095);
}

void setServo(uint8_t ch, int deg) {
  deg = constrain(deg, jointMin[ch], jointMax[ch]);
  int us = map(deg, 0, 180, SERVO_MIN_US, SERVO_MAX_US);
  pwm.setPWM(ch, 0, usToPulse(us));
}

void setup() {
  Serial.begin(115200);

  Wire.begin(SDA_PIN, SCL_PIN);
  pwm.begin();
  pwm.setPWMFreq(SERVO_FREQ);
  delay(300);

  for (int i = 0; i < 6; i++)
    setServo(i, 90);

  setServo(GRIPPER, 40);

}

void processJointCmd(int id, int deg) {
  if (id < 0 || id > 5) return;
  setServo(id, deg);
}

void processAllCmd(int *v) {
  for (int i = 0; i < 6; i++)
    setServo(i, v[i]);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.startsWith("J")) {
      int id, deg;
      sscanf(cmd.c_str(), "J %d %d", &id, &deg);
      processJointCmd(id, deg);
    }

    else if (cmd.startsWith("A")) {
      int v[6];
      if (sscanf(cmd.c_str(),
          "A %d %d %d %d %d %d",
          &v[0], &v[1], &v[2],
          &v[3], &v[4], &v[5]) == 6) {
        processAllCmd(v);
      }
    }
  }
}
