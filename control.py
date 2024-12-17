import RPi.GPIO as GPIO
import time
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

#  Main Control Loop for Robot A (our robot)


# In this script, we will implement the main control loop for Robot A.
# We use two buttons to sense if the tube is skewed, therefore meaning the speed of Robot B is different from the speed of Robot A.
# There are two different starting conditions when the robot is on the left ramp, and the robot is on the right ramp
# We are not using an encoder.

# If the left button is pressed while on the right ramp, the tube must look like / 
    # Robot A is faster than Robot B, so we need to slow down Robot A by adjusting the speed of the left motor.

# If the right button is pressed while on the right ramp, the tube must look like \
    # Robot A is slower than Robot B, so we need to speed up Robot A by adjusting the speed of the left motor.

# If the left button is pressed while on the left ramp, the tube must look like /
    # Robot A is slower than Robot B, so we need to speed up Robot A by adjusting the speed of the right motor.

# If the right button is pressed while on the left ramp, the tube must look like \
    # Robot A is faster than Robot B, so we need to slow down Robot A by adjusting the speed of the right motor.


# GPIO setup
# We will use the GPIO library to read the button inputs and control the motors.
# We will use the BOARD numbering scheme for the GPIO pins.
# We will also use the PWM feature of the GPIO library to control the speed of the motors.
# We will set up the GPIO pins for the buttons and the motors.
# We will NOT use the PMW pins on the L298N motor driver for this script.
# We will USE the IN1, IN2, IN3, and IN4 pins on the L298N motor driver to control the direction of the motors.


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

# Global variables to store the target speed, start signal, and stop signal
target_speed = 0
start_signal = False
stop_signal = False

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

def control_loop():
    global start_signal, stop_signal, target_speed
    while not start_signal:
        time.sleep(0.1)  # Wait for the start signal

    print("Begin autonomous operation for Robot A")
    while not stop_signal:
        left_button_pressed = GPIO.input(LEFT_BUTTON_PIN) == GPIO.LOW
        right_button_pressed = GPIO.input(RIGHT_BUTTON_PIN) == GPIO.LOW

        if left_button_pressed:
            # Adjust speed based on button input
            set_motor_speed(target_speed * 0.9, target_speed)  # Slow down left motor
        elif right_button_pressed:
            # Adjust speed based on button input
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

