

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define SDA_PIN 21
#define SCL_PIN 22

#define SERVO_FREQ 50
#define SERVO_MIN_US 600
#define SERVO_MAX_US 2400
#define SERVO_STEP_DELAY 15

#define IR_OPEN_PIN  26
#define IR_CLOSE_PIN 27
#define IR_DETECTED  HIGH

#define GRIP_OPEN_ANGLE  40
#define GRIP_CLOSE_ANGLE 100

Adafruit_PWMServoDriver pwm(0x40);





enum { BASE, SHOULDER, ELBOW, WRIST_PITCH, WRIST_ROTATE, GRIPPER };

struct ServoCal {
  int minDeg;
  int maxDeg;
  int offset;
  int sign;
};

ServoCal cal[6] = {
  {10, 170, 90,  +1},   // BASE
  {10, 170, 100, +1},   // SHOULDER
  {10, 320, 220, -1},   // ELBOW
  {10, 320, 210, +1},   // WRIST PITCH
  {10, 320, 90,  +1},   // WRIST ROTATE
  {40, 130, 40,  +1}    // GRIPPER
};

int currentDeg[6] = {90, 90, 90, 90, 90, GRIP_OPEN_ANGLE};

uint16_t usToPulse(int us) {
  return map(us, 0, 20000, 0, 4095);
}

void writeServo(uint8_t ch, int deg) {
  deg = constrain(deg, cal[ch].minDeg, cal[ch].maxDeg);
  int us = map(deg, 0, 180, SERVO_MIN_US, SERVO_MAX_US);
  pwm.setPWM(ch, 0, usToPulse(us));
}

void moveServoSlow(uint8_t ch, int target) {
  target = constrain(target, cal[ch].minDeg, cal[ch].maxDeg);
  int step = (target > currentDeg[ch]) ? 1 : -1;

  while (currentDeg[ch] != target) {
    currentDeg[ch] += step;
    writeServo(ch, currentDeg[ch]);
    delay(SERVO_STEP_DELAY);
  }
}

int mapLogical(uint8_t j, int logical) {
  return cal[j].sign * logical + cal[j].offset;
}

void handleGripperIR() {
  if (digitalRead(IR_OPEN_PIN) == IR_DETECTED)
    moveServoSlow(GRIPPER, GRIP_OPEN_ANGLE);
  else if (digitalRead(IR_CLOSE_PIN) == IR_DETECTED)
    moveServoSlow(GRIPPER, GRIP_CLOSE_ANGLE);
}



void setup() {
  Serial.begin(115200);         


  pinMode(IR_OPEN_PIN, INPUT);
  pinMode(IR_CLOSE_PIN, INPUT);

  Wire.begin(SDA_PIN, SCL_PIN);
  pwm.begin();
  pwm.setPWMFreq(SERVO_FREQ);
  delay(300);

  for (int i = 0; i < 6; i++)
    writeServo(i, currentDeg[i]);
}


void loop() {
  handleGripperIR();

  if (Serial.available()) {
    String cmd = Serial2.readStringUntil('\n');
    int id, deg;

    if (sscanf(cmd.c_str(), "J %d %d", &id, &deg) == 2) {

      if (id == GRIPPER &&
         (digitalRead(IR_OPEN_PIN) == IR_DETECTED ||
          digitalRead(IR_CLOSE_PIN) == IR_DETECTED))
        return;

      int servoDeg = mapLogical(id, deg);
      moveServoSlow(id, servoDeg);
    }
  }
}

