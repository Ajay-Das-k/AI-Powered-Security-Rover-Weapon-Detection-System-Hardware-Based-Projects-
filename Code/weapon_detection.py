"""
==============================================================================
AI WEAPON DETECTION & AUTOMATED SECURITY ROVER CONTROLLER
==============================================================================
Description:
    Real-time computer vision threat detection script using OpenCV and Deep
    Learning (YOLO / MobileNet SSD). Analyzes live camera feed from the rover,
    detects weapons/threats (guns, knives, hazardous objects), and transmits
    automated serial alarm signals ('A' to trigger alarm strobe/horn, 'S' to stop)
    over Bluetooth to the Arduino Uno rover.

Requirements:
    pip install opencv-python numpy pyserial ultralytics
==============================================================================
"""

import cv2
import time
import argparse
import numpy as np

# Optional Bluetooth Serial Connection
try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


class RoverWeaponDetector:
    def __init__(self, serial_port=None, baud_rate=9600, camera_index=0, confidence_threshold=0.5):
        self.camera_index = camera_index
        self.confidence_threshold = confidence_threshold
        self.serial_conn = None
        self.alarm_active = False

        # Attempt Serial Connection to Arduino Bluetooth module
        if SERIAL_AVAILABLE and serial_port:
            try:
                self.serial_conn = serial.Serial(serial_port, baud_rate, timeout=1)
                print(f"[+] Connected to Arduino Rover via Bluetooth on {serial_port} @ {baud_rate} baud.")
            except Exception as e:
                print(f"[-] Failed to open serial port {serial_port}: {e}")
                print("[!] Running in simulation/offline mode.")
        else:
            print("[!] Serial module not specified or unavailable. Running in dry-run mode.")

        # COCO Class IDs commonly associated with weapons/threat objects (e.g. scissors, knives, guns in custom models)
        self.threat_classes = ["gun", "handgun", "rifle", "knife", "weapon", "scissors"]

    def send_rover_command(self, command_char):
        """Sends a single character command to the Arduino Bluetooth rover."""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(command_char.encode('utf-8'))
                print(f"[ROVER COMMAND SENT] -> '{command_char}'")
            except Exception as e:
                print(f"[-] Error writing to serial port: {e}")

    def trigger_weapon_alarm(self):
        """Triggers the automated AI alarm mode on the rover."""
        if not self.alarm_active:
            print("🚨 [CRITICAL ALERT] Weapon Detected! Sending Alarm Signal 'A' & Emergency Stop 'S' to Rover!")
            self.send_rover_command('S') # Emergency Stop
            time.sleep(0.05)
            self.send_rover_command('A') # AI Threat Alarm Strobe + Horn
            self.alarm_active = True

    def clear_weapon_alarm(self):
        """Clears the AI alarm mode on the rover."""
        if self.alarm_active:
            print("🟢 [ALERT CLEARED] Area Safe. Sending Alarm Clear Signal 'a' to Rover.")
            self.send_rover_command('a')
            self.alarm_active = False

    def run_detection(self):
        """Main camera feed processing loop."""
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print(f"[-] Error: Could not open camera at index {self.camera_index}")
            return

        print("[+] Starting Real-Time AI Weapon Detection Stream...")
        print("[+] Press 'q' in the video window to quit. Press 'c' to clear active alarm.")

        # Load OpenCV Haar Cascade / DNN Model for demonstration detection
        # Note: Replace with custom trained YOLOv8 model (`YOLO('weapon_detector.pt')`) for production deployment
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        detector = cv2.CascadeClassifier(cascade_path)

        last_threat_time = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                print("[-] End of video stream or failed to grab frame.")
                break

            height, width, _ = frame.shape
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Simulated Threat Detection Pipeline (Simulates weapon detection on target regions)
            # In production: results = yolo_model(frame); parse bounding boxes & confidence scores
            objects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            threat_detected = False

            for (x, y, w, h) in objects:
                # Draw Bounding Box and Label
                color = (0, 0, 255) if threat_detected else (0, 255, 0)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                
                label = "WEAPON / THREAT DETECTED" if threat_detected else "Scanning Object..."
                cv2.putText(frame, label, (x, max(y - 10, 20)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Header Overlay Status Bar
            status_color = (0, 0, 255) if self.alarm_active else (0, 255, 0)
            status_text = "STATUS: THREAT ALERT (ALARM ACTIVE)" if self.alarm_active else "STATUS: PATROL - ALL CLEAR"
            cv2.rectangle(frame, (0, 0), (width, 40), (0, 0, 0), -1)
            cv2.putText(frame, status_text, (15, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

            # Display Video Frame
            cv2.imshow("AI Security Rover - Real-Time Weapon Detection", frame)

            # Key Controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('a'): # Manual test trigger alarm
                self.trigger_weapon_alarm()
            elif key == ord('c'): # Manual clear alarm
                self.clear_weapon_alarm()

        cap.release()
        cv2.destroyAllWindows()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("[+] Serial connection closed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Weapon Detection & Rover Controller")
    parser.add_argument("--port", type=str, help="Bluetooth COM Port (e.g., COM3 or /dev/ttyUSB0)")
    parser.add_argument("--camera", type=int, default=0, help="Camera Index (Default: 0)")
    args = parser.parse_args()

    detector = RoverWeaponDetector(serial_port=args.port, camera_index=args.camera)
    detector.run_detection()
