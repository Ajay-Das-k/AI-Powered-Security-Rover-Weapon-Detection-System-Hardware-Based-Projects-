#include <Servo.h>

/*
 * ==============================================================================
 * AI-POWERED SECURITY ROVER & WEAPON DETECTION SYSTEM - ENHANCED FIRMWARE
 * Microcontroller: Arduino Uno
 * Communications: Serial Bluetooth (HC-05 / HC-06) @ 9600 Baud
 * Motor Driver: L298N Dual H-Bridge
 * Peripherals: Front/Rear LEDs, Horn Buzzer, Camera Pan/Tilt Servos, HC-SR04
 * ==============================================================================
 */

// --- Motor Driver Pins (L298N) ---
#define in1 5 
#define in2 6
#define in3 10
#define in4 11

// --- Peripherals & Signaling Pins ---
#define light_FR  14    // LED Front Right   pin A0 for Arduino Uno
#define light_FL  15    // LED Front Left    pin A1 for Arduino Uno
#define light_BR  16    // LED Back Right    pin A2 for Arduino Uno
#define light_BL  17    // LED Back Left     pin A3 for Arduino Uno
#define horn_Buzz 18    // Horn Buzzer       pin A4 for Arduino Uno

// --- Ultrasonic Sensor Pins (HC-SR04) ---
#define TRIG_PIN  19    // Trig pin A5 for Arduino Uno
#define ECHO_PIN  3     // Echo pin D3 (Interrupt capable)

// --- Camera Servo Pan/Tilt Pins ---
#define SERVO_PAN_PIN   8  // Servo Pan (Horizontal)
#define SERVO_TILT_PIN  9  // Servo Tilt (Vertical)

// --- Global Variables & State ---
Servo servoPan;
Servo servoTilt;
int panAngle = 90;
int tiltAngle = 90;

int command;
int Speed = 204;       // 0 - 255 PWM Speed (Default ~80%)
int Speedsec;
int buttonState = 0;
int lastButtonState = 0;
int Turnradius = 0;    // Turning radius factor
int brakeTime = 45;    // Braking pulse duration in ms
int brkonoff = 1;      // Electronic braking switch (1 = Enabled)

// Light & Peripheral States
boolean lightFront = false;
boolean lightBack = false;
boolean horn = false;

// Enhanced Feature Flags
boolean hazardMode = false;       // Emergency hazard strobe lighting
boolean autoObstacleMode = true;  // Ultrasonic automatic obstacle avoidance safety
boolean alarmMode = false;        // AI Weapon Detection Threat Alarm state

unsigned long lastStrobeTime = 0;
boolean strobeState = false;

void setup() {
  // Motor Pins
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  // Peripherals
  pinMode(light_FR, OUTPUT);
  pinMode(light_FL, OUTPUT);
  pinMode(light_BR, OUTPUT);
  pinMode(light_BL, OUTPUT);
  pinMode(horn_Buzz, OUTPUT);

  // Ultrasonic Sensor
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Servos
  servoPan.attach(SERVO_PAN_PIN);
  servoTilt.attach(SERVO_TILT_PIN);
  servoPan.write(panAngle);
  servoTilt.write(tiltAngle);

  // Hardware Serial for Bluetooth (9600 Baud)
  Serial.begin(9600);
}

void loop() {
  // 1. Handle Active Hazard / Strobe Effect
  updateHazardLights();

  // 2. Handle AI Threat Alarm Effect
  updateThreatAlarm();

  // 3. Serial Bluetooth Command Processing
  if (Serial.available() > 0) {
    command = Serial.read();
    
    // Stop motors before applying new directional command
    Stop(); 

    // Handle Manual Peripheral States
    if (!hazardMode && !alarmMode) {
      digitalWrite(light_FR, lightFront ? HIGH : LOW);
      digitalWrite(light_FL, lightFront ? HIGH : LOW);
      digitalWrite(light_BR, lightBack ? HIGH : LOW);
      digitalWrite(light_BL, lightBack ? HIGH : LOW);
      digitalWrite(horn_Buzz, horn ? HIGH : LOW);
    }

    // Command Parser Switch
    switch (command) {
      // --- Directional Commands ---
      case 'F':
        if (checkObstacleSafety()) {
          forward();
        } else {
          Stop(); // Auto-brake on obstacle detection
        }
        break;
      case 'B':
        back();
        break;
      case 'L':
        left();
        break;
      case 'R':
        right();
        break;
      case 'G':
        if (checkObstacleSafety()) forwardleft(); else Stop();
        break;
      case 'I':
        if (checkObstacleSafety()) forwardright(); else Stop();
        break;
      case 'H':
        backleft();
        break;
      case 'J':
        backright();
        break;

      // --- Speed Selectors (0 - 9, q) ---
      case '0': Speed = 100; break;
      case '1': Speed = 140; break;
      case '2': Speed = 153; break;
      case '3': Speed = 165; break;
      case '4': Speed = 178; break;
      case '5': Speed = 191; break;
      case '6': Speed = 204; break;
      case '7': Speed = 216; break;
      case '8': Speed = 229; break;
      case '9': Speed = 242; break;
      case 'q': Speed = 255; break;

      // --- Manual Peripheral Controls ---
      case 'W': lightFront = true; break;
      case 'w': lightFront = false; break;
      case 'U': lightBack = true; break;
      case 'u': lightBack = false; break;
      case 'V': horn = true; break;
      case 'v': horn = false; break;

      // --- NEW FEATURE 1: Camera Pan/Tilt Servo Steering ---
      case 'K': // Pan Left
        panAngle = constrain(panAngle - 10, 0, 180);
        servoPan.write(panAngle);
        break;
      case 'M': // Pan Right
        panAngle = constrain(panAngle + 10, 0, 180);
        servoPan.write(panAngle);
        break;
      case 'N': // Tilt Up
        tiltAngle = constrain(tiltAngle - 10, 15, 165);
        servoTilt.write(tiltAngle);
        break;
      case 'O': // Tilt Down
        tiltAngle = constrain(tiltAngle + 10, 15, 165);
        servoTilt.write(tiltAngle);
        break;
      case 'P': // Reset Camera to Center
        panAngle = 90;
        tiltAngle = 90;
        servoPan.write(panAngle);
        servoTilt.write(tiltAngle);
        break;

      // --- NEW FEATURE 2: Emergency Hazard Strobe Toggle ---
      case 'X': hazardMode = true; break;
      case 'x': hazardMode = false; break;

      // --- NEW FEATURE 3: Auto Obstacle Avoidance Toggle ---
      case 'Y': autoObstacleMode = true; break;
      case 'y': autoObstacleMode = false; break;

      // --- NEW FEATURE 4: AI Weapon Threat Alarm Trigger ---
      case 'A': // Alarm Trigger (Sent by Python AI Script on weapon detection)
        alarmMode = true;
        Stop();
        break;
      case 'a': // Alarm Clear
        alarmMode = false;
        digitalWrite(horn_Buzz, LOW);
        break;
    }

    Speedsec = Turnradius;
    if (brkonoff == 1) {
      brakeOn();
    } else {
      brakeOff();
    }
  }
}

// --- Movement Functions ---
void forward() {
  analogWrite(in1, Speed);
  analogWrite(in3, Speed);
}

void back() {
  analogWrite(in2, Speed);
  analogWrite(in4, Speed);
}

void left() {
  analogWrite(in3, Speed);
  analogWrite(in2, Speed);
}

void right() {
  analogWrite(in4, Speed);
  analogWrite(in1, Speed);
}

void forwardleft() {
  analogWrite(in1, Speedsec);
  analogWrite(in3, Speed);
}

void forwardright() {
  analogWrite(in1, Speed);
  analogWrite(in3, Speedsec);
}

void backright() {
  analogWrite(in2, Speed);
  analogWrite(in4, Speedsec);
}

void backleft() {
  analogWrite(in2, Speedsec);
  analogWrite(in4, Speed);
}

void Stop() {
  analogWrite(in1, 0);
  analogWrite(in2, 0);
  analogWrite(in3, 0);
  analogWrite(in4, 0);
}

void brakeOn() {
  buttonState = command;
  if (buttonState != lastButtonState) {
    if (buttonState == 'S') {
      if (lastButtonState != buttonState) {
        digitalWrite(in1, HIGH);
        digitalWrite(in2, HIGH);
        digitalWrite(in3, HIGH);
        digitalWrite(in4, HIGH);
        delay(brakeTime);
        Stop();
      }
    }
    lastButtonState = buttonState;
  }
}

void brakeOff() {
}

// --- Ultrasonic Distance Safety Measurement ---
long measureDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH, 25000); // 25ms timeout
  if (duration == 0) return 999; // No echo
  return duration * 0.034 / 2;
}

boolean checkObstacleSafety() {
  if (!autoObstacleMode) return true;
  long dist = measureDistanceCM();
  if (dist < 20) { // Object closer than 20 cm
    // Trigger momentary warning beep
    digitalWrite(horn_Buzz, HIGH);
    delay(50);
    digitalWrite(horn_Buzz, LOW);
    return false; // Unsafe to proceed forward
  }
  return true;
}

// --- Hazard Strobe Light Mode Routine ---
void updateHazardLights() {
  if (!hazardMode) return;
  unsigned long currentMillis = millis();
  if (currentMillis - lastStrobeTime >= 150) { // 150ms toggle speed
    lastStrobeTime = currentMillis;
    strobeState = !strobeState;

    digitalWrite(light_FR, strobeState ? HIGH : LOW);
    digitalWrite(light_FL, strobeState ? HIGH : LOW);
    digitalWrite(light_BR, strobeState ? LOW : HIGH);
    digitalWrite(light_BL, strobeState ? LOW : HIGH);
  }
}

// --- AI Threat Alarm Routine ---
void updateThreatAlarm() {
  if (!alarmMode) return;
  unsigned long currentMillis = millis();
  if (currentMillis - lastStrobeTime >= 100) {
    lastStrobeTime = currentMillis;
    strobeState = !strobeState;

    // Rapid strobe lighting & horn pulsing
    digitalWrite(light_FR, strobeState ? HIGH : LOW);
    digitalWrite(light_FL, strobeState ? HIGH : LOW);
    digitalWrite(light_BR, strobeState ? HIGH : LOW);
    digitalWrite(light_BL, strobeState ? HIGH : LOW);
    digitalWrite(horn_Buzz, strobeState ? HIGH : LOW);
  }
}
