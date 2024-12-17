import RPi.GPIO as GPIO
import time
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# GPIO setup
GPIO.setmode(GPIO.BOARD)

# Define GPIO pins
LEFT_BUTTON_PIN = 36 # GPIO pin for left button
RIGHT_BUTTON_PIN = 32 # GPIO pin for right button
LEFT_MOTOR_IN1 = 15  # GPIO pin for IN1 (Left Motor)
LEFT_MOTOR_IN2 = 16  # GPIO pin for IN2 (Left Motor)
RIGHT_MOTOR_IN3 = 12  # GPIO pin for IN3 (Right Motor)
RIGHT_MOTOR_IN4 = 11  # GPIO pin for IN4 (Right Motor)

# Setup button pins
GPIO.setup(LEFT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # zero when pressed
GPIO.setup(RIGHT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # zero when pressed

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

# Global variables to store the target speed, start signal, stop signal, and ramp side
target_speed = 0
start_signal = False
stop_signal = False
on_left_ramp = True

@app.route('/start/<int:delay>', methods=['POST'])
def start(delay):
    global start_signal
    if 1 <= delay <= 10:
        threading.Timer(delay, set_start_signal).start()
        return jsonify({"status": "Robot A will start after delay"}), 200
    else:
        return jsonify({"error": "Invalid delay value"}), 400

def set_start_signal():
    global start_signal
    start_signal = True

@app.route('/target/<int:speed>', methods=['POST'])
def target(speed):
    global target_speed
    if 1 <= speed <= 1000:
        target_speed = speed
        return jsonify({"status": "Speed set"}), 200
    else:
        return jsonify({"error": "Invalid speed value"}), 400

@app.route('/stop', methods=['POST'])
def stop():
    global stop_signal
    stop_signal = True
    return jsonify({"status": "Robot A stopped"}), 200

@app.route('/ready', methods=['GET'])
def ready():
    return jsonify({"status": "Robot A is ready"}), 200

@app.route('/ramp/<string:side>', methods=['POST'])
def ramp(side):
    global on_left_ramp
    if side.lower() == 'left':
        on_left_ramp = True
        return jsonify({"status": "Robot A set to left ramp"}), 200
    elif side.lower() == 'right':
        on_left_ramp = False
        return jsonify({"status": "Robot A set to right ramp"}), 200
    else:
        return jsonify({"error": "Invalid ramp side"}), 400

def control_loop():
    global start_signal, stop_signal, target_speed, on_left_ramp
    while not start_signal:
        time.sleep(0.1)  # Wait for the start signal

    print("Begin autonomous operation for Robot A")
    while not stop_signal:
        left_button_pressed = GPIO.input(LEFT_BUTTON_PIN) == GPIO.LOW
        right_button_pressed = GPIO.input(RIGHT_BUTTON_PIN) == GPIO.LOW

        if on_left_ramp:
            if left_button_pressed:
                set_motor_speed(target_speed, target_speed * 1.1)  # Speed up right motor
            elif right_button_pressed:
                set_motor_speed(target_speed, target_speed * 0.9)  # Slow down right motor
            else:
                set_motor_speed(target_speed, target_speed)  # Set to target speed
        else:
            if left_button_pressed:
                set_motor_speed(target_speed * 0.9, target_speed)  # Slow down left motor
            elif right_button_pressed:
                set_motor_speed(target_speed * 1.1, target_speed)  # Speed up left motor
            else:
                set_motor_speed(target_speed, target_speed)  # Set to target speed

        time.sleep(0.1)  # Ensure control loop runs at a reasonable rate

    # Stop the motors when stop signal is received
    set_motor_speed(0, 0)
    print("Robot A stopped")

def run_server():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Start the Flask server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # Start the control loop
    control_loop()