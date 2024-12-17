import RPi.GPIO as GPIO
import time
from flask import Flask, request, jsonify
import threading
import argparse
import requests

app = Flask(__name__)

# Global variables to store the target speed, start signal, stop signal, and IP address
target_speed = 0
start_signal = False
stop_signal = False
on_left_ramp = None  # Variable to store the side of the ramp
robot_b_ip = None  # Variable to store the IP address of Robot B

# Define GPIO pins
LEFT_BUTTON_PIN = 36  # GPIO pin for left button
RIGHT_BUTTON_PIN = 32  # GPIO pin for right button
LEFT_MOTOR_IN1 = 15  # GPIO pin for IN1 (Left Motor)
LEFT_MOTOR_IN2 = 16  # GPIO pin for IN2 (Left Motor)
RIGHT_MOTOR_IN3 = 12  # GPIO pin for IN3 (Right Motor)
RIGHT_MOTOR_IN4 = 11  # GPIO pin for IN4 (Right Motor)

# Setup button pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LEFT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # zero when pressed
GPIO.setup(RIGHT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # zero when pressed

# Setup motor pins
GPIO.setup(LEFT_MOTOR_IN1, GPIO.OUT)
GPIO.setup(LEFT_MOTOR_IN2, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR_IN3, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR_IN4, GPIO.OUT)

# Function to set motor direction and speed
def set_motor_speed(left_speed, right_speed):
    GPIO.output(LEFT_MOTOR_IN1, GPIO.HIGH if left_speed > 0 else GPIO.LOW)
    GPIO.output(LEFT_MOTOR_IN2, GPIO.LOW if left_speed > 0 else GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_IN3, GPIO.HIGH if right_speed > 0 else GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_IN4, GPIO.LOW if right_speed > 0 else GPIO.HIGH)
    # Assuming speed is controlled by duty cycle, adjust accordingly
    # left_motor_pwm.ChangeDutyCycle(abs(left_speed))
    # right_motor_pwm.ChangeDutyCycle(abs(right_speed))

@app.route('/start/<int:delay>', methods=['POST'])
def start(delay):
    global start_signal
    if 1 <= delay <= 10:
        print(f"Received start request with delay: {delay}")
        threading.Timer(delay, set_start_signal).start()
        return jsonify({"status": "Robot A will start after delay"}), 200
    else:
        print(f"Invalid start delay: {delay}")
        return jsonify({"error": "Invalid delay value"}), 400

def set_start_signal():
    global start_signal
    start_signal = True
    print("Start signal set to True")

@app.route('/speed/<int:speed>', methods=['POST'])
def speed(speed):
    global target_speed
    if 1 <= speed <= 1000:
        target_speed = speed
        print(f"Received target speed: {target_speed}")
        return jsonify({"status": "Speed set"}), 200
    else:
        print(f"Invalid target speed: {speed}")
        return jsonify({"error": "Invalid speed value"}), 400

def check_robot_b_start_signal():
    url = f"http://{robot_b_ip}:5000/start"
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Received start signal from Robot B")
                return True
        except requests.exceptions.RequestException as e:
            print(f"Error checking Robot B start signal: {e}")
        time.sleep(1)  # Retry every second

def receive_speed_from_robot_b():
    url = f"http://{robot_b_ip}:5000/speed"
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                speed = response.json().get('speed')
                if speed:
                    global target_speed
                    target_speed = speed
                    print(f"Received speed from Robot B: {target_speed}")
        except requests.exceptions.RequestException as e:
            print(f"Error receiving speed from Robot B: {e}")
        time.sleep(1)  # Retry every second

def control_loop():
    global start_signal, stop_signal, target_speed, on_left_ramp
    print("Entering control loop")
    while not start_signal:
        time.sleep(0.1)  # Wait for the start signal

    print("Begin autonomous operation for Robot A")
    while not stop_signal:
        left_button_pressed = GPIO.input(LEFT_BUTTON_PIN) == GPIO.LOW
        right_button_pressed = GPIO.input(RIGHT_BUTTON_PIN) == GPIO.LOW

        if on_left_ramp:
            if left_button_pressed:
                # Adjust speed based on button input
                set_motor_speed(target_speed * 0.9, target_speed)  # Slow down left motor
                print("Left button pressed, slowing down left motor")
            elif right_button_pressed:
                # Adjust speed based on button input
                set_motor_speed(target_speed * 1.1, target_speed)  # Speed up left motor
                print("Right button pressed, speeding up left motor")
            else:
                set_motor_speed(target_speed, target_speed)  # Set to target speed
                print("No button pressed, setting to target speed")
        else:
            if right_button_pressed:
                # Adjust speed based on button input
                set_motor_speed(target_speed * 0.9, target_speed)  # Slow down right motor
                print("Right button pressed, slowing down right motor")
            elif left_button_pressed:
                # Adjust speed based on button input
                set_motor_speed(target_speed, target_speed * 1.1)  # Speed up right motor
                print("Left button pressed, speeding up right motor")
            else:
                set_motor_speed(target_speed, target_speed)  # Set to target speed
                print("No button pressed, setting to target speed")

        time.sleep(0.1)  # Ensure control loop runs at a reasonable rate

    # Stop the motors when stop signal is received
    set_motor_speed(0, 0)
    print("Robot A stopped")

def run_server():
    print("Starting Flask server")
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Run Robot A control script.')
    parser.add_argument('--side', choices=['left', 'right'], required=True, help='Specify the side of the ramp (left or right).')
    parser.add_argument('--ip', required=True, help='Specify the IP address of Robot B.')
    args = parser.parse_args()

    # Set the side of the ramp and IP address
    on_left_ramp = (args.side == 'left')
    robot_b_ip = args.ip

    print(f"Running with side: {args.side}, IP: {args.ip}")

    # Start the Flask server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # Check for start signal from Robot B
    if check_robot_b_start_signal():
        # Start the control loop
        control_loop()

    # Start receiving speed from Robot B
    speed_thread = threading.Thread(target=receive_speed_from_robot_b)
    speed_thread.start()
