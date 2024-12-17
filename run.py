import RPi.GPIO as GPIO
import signal
import sys
import time
import threading
import argparse
from flask import Flask, jsonify

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

# Initialize PWM on both IN1 and IN3 pins for speed control
left_motor_pwm = GPIO.PWM(LEFT_MOTOR_IN1, 1000)  # 1kHz frequency
right_motor_pwm = GPIO.PWM(RIGHT_MOTOR_IN3, 1000)  # 1kHz frequency

# Start PWM with 0 duty cycle to ensure motors are off
left_motor_pwm.start(0)
right_motor_pwm.start(0)

# Set the other two unused IN pins to LOW
GPIO.output(LEFT_MOTOR_IN2, GPIO.LOW)
GPIO.output(RIGHT_MOTOR_IN4, GPIO.LOW)

def set_motor_speed(left_speed, right_speed):
    # Scale the speed values to 0-100%
    left_duty_cycle = min(max(abs(left_speed) / 10, 0), 100)
    right_duty_cycle = min(max(abs(right_speed) / 10, 0), 100)
    
    GPIO.output(LEFT_MOTOR_IN1, GPIO.HIGH if left_speed > 0 else GPIO.LOW)
    GPIO.output(LEFT_MOTOR_IN2, GPIO.LOW if left_speed > 0 else GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_IN3, GPIO.HIGH if right_speed > 0 else GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_IN4, GPIO.LOW if right_speed > 0 else GPIO.HIGH)
    
    left_motor_pwm.ChangeDutyCycle(left_duty_cycle)
    right_motor_pwm.ChangeDutyCycle(right_duty_cycle)

def button_callback(channel):
    global target_speed
    if channel == LEFT_BUTTON_PIN:
        print("Left button pressed! Adjusting speed to straighten tube.")
        set_motor_speed(target_speed - 200, target_speed + 200)
        time.sleep(0.5)  # Adjust the duration as needed
        set_motor_speed(target_speed, target_speed)
    elif channel == RIGHT_BUTTON_PIN:
        print("Right button pressed! Adjusting speed to straighten tube.")
        set_motor_speed(target_speed + 200, target_speed - 200)
        time.sleep(0.5)  # Adjust the duration as needed
        set_motor_speed(target_speed, target_speed)

# Register button press callbacks
GPIO.add_event_detect(LEFT_BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)
GPIO.add_event_detect(RIGHT_BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)

def cleanup_gpio(signal, frame):
    print("Cleaning up GPIO and stopping motors")
    set_motor_speed(0, 0)
    GPIO.cleanup()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, cleanup_gpio)

@app.route('/start/<int:delay>', methods=['POST'])
def start(delay):
    global start_signal
    print(f"Received start signal with delay: {delay}")
    for i in range(delay, 0, -1):
        print(f"Starting in {i} seconds...")
        time.sleep(1)
    start_signal = True
    print("Start signal set to True")
    return jsonify({"status": "ok"}), 200

@app.route('/speed/<int:speed>', methods=['POST'])
def speed(speed):
    global target_speed
    if 1 <= speed <= 1000:
        target_speed = speed
        print(f"Received target speed: {target_speed}")
        return jsonify({"status": "ok"}), 200
    else:
        print(f"Invalid target speed: {speed}")
        return jsonify({"error": "Invalid speed value"}), 400

def control_loop():
    global target_speed, start_signal
    current_speed = 0
    acceleration = 10  # Adjust this value to control the acceleration rate

    while True:
        if not start_signal:
            if current_speed != 0:
                set_motor_speed(0, 0)
                current_speed = 0
                print("Motors stopped. Waiting for start signal...")
            time.sleep(0.1)
            continue

        if current_speed < target_speed:
            current_speed += acceleration
            if current_speed > target_speed:
                current_speed = target_speed
        elif current_speed > target_speed:
            current_speed -= acceleration
            if current_speed < target_speed:
                current_speed = target_speed

        set_motor_speed(current_speed, current_speed)  # Set both motors to the same speed
        print(f"Setting motor speed to {current_speed}")

        time.sleep(0.1)  # Ensure control loop runs at a reasonable rate

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

    # Start the control loop in a separate thread
    control_thread = threading.Thread(target=control_loop)
    control_thread.daemon = True  # Ensure the thread exits when the main program exits
    control_thread.start()

    # Run the Flask server
    run_server()
