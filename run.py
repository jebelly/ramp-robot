import requests
import time
import json
import RPi.GPIO as GPIO
from flask import Flask, request, jsonify
from threading import Thread

# Configuration
ROBOT_B_URL = "http://robot_b_address:5000"  # Replace with Robot B's API address
INITIAL_SPEED = 50  # Starting speed for negotiation
PWM_FREQ = 1000  # PWM frequency in Hz
TUNING_FACTOR = 1.0  # Tuning factor for ramp angle adjustment
Kp = 0.1  # Proportional gain, adjust as needed
RIGHT_MOTOR_CALIBRATION = 0.9  # Calibration factor for the right motor

# GPIO Configuration
LEFT_IN1 = 15  # GPIO pin for IN1 (Left Motor)
LEFT_IN2 = 16  # GPIO pin for IN2 (Left Motor)
RIGHT_IN3 = 12  # GPIO pin for IN3 (Right Motor)
RIGHT_IN4 = 11  # GPIO pin for IN4 (Right Motor)
ENCODER_CLK = 38 # GPIO pin for encoder CLK (clock)
ENCODER_DT = 36 # GPIO pin for encoder DT (data)
ENCODER_SW = 40 # GPIO pin for encoder SW (switch)

# Initialize Flask app
app = Flask(__name__)
target_speed = 0

def setup_gpio():
    """Setup GPIO pins and PWM."""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LEFT_IN1, GPIO.OUT)
    GPIO.setup(LEFT_IN2, GPIO.OUT)
    GPIO.setup(RIGHT_IN3, GPIO.OUT)
    GPIO.setup(RIGHT_IN4, GPIO.OUT)
    GPIO.setup(ENCODER_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ENCODER_DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ENCODER_SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    global pwm_left_in1, pwm_left_in2, pwm_right_in3, pwm_right_in4
    pwm_left_in1 = GPIO.PWM(LEFT_IN1, PWM_FREQ)
    pwm_left_in2 = GPIO.PWM(LEFT_IN2, PWM_FREQ)
    pwm_right_in3 = GPIO.PWM(RIGHT_IN3, PWM_FREQ)
    pwm_right_in4 = GPIO.PWM(RIGHT_IN4, PWM_FREQ)

    pwm_left_in1.start(0)
    pwm_left_in2.start(0)
    pwm_right_in3.start(0)
    pwm_right_in4.start(0)

def set_motor_speed(left_speed, right_speed):
    """
    Set the speed of the left and right motors using PWM.
    
    :param left_speed: Speed for the left motor (0-100)
    :param right_speed: Speed for the right motor (0-100)
    """
    right_speed *= RIGHT_MOTOR_CALIBRATION  # Apply calibration factor

    pwm_left_in1.ChangeDutyCycle(left_speed if left_speed >= 0 else 0)
    pwm_left_in2.ChangeDutyCycle(-left_speed if left_speed < 0 else 0)
    pwm_right_in3.ChangeDutyCycle(right_speed if right_speed >= 0 else 0)
    pwm_right_in4.ChangeDutyCycle(-right_speed if right_speed < 0 else 0)

# Global variables for encoder and PWM adjustments
counter = 0
clkLastState = GPIO.input(ENCODER_CLK)
left_pwm_adjustment = 0
right_pwm_adjustment = 0

def encoder_callback(channel):
    """Callback function to handle encoder state changes."""
    global counter, clkLastState
    clkState = GPIO.input(ENCODER_CLK)
    dtState = GPIO.input(ENCODER_DT)
    if clkState != clkLastState:
        if dtState != clkState:
            counter += 1
        else:
            counter -= 1
    clkLastState = clkState

@app.route('/set_speed', methods=['POST'])
def set_speed():
    """Endpoint to set the target speed."""
    global target_speed
    data = request.get_json()
    target_speed = data.get('speed', 0)
    return jsonify({"status": "success", "speed": target_speed})

@app.route('/set_pwm', methods=['POST'])
def set_pwm():
    """Endpoint to set PWM adjustments."""
    global left_pwm_adjustment, right_pwm_adjustment
    data = request.get_json()
    left_pwm_adjustment = data.get('left_pwm', 0)
    right_pwm_adjustment = data.get('right_pwm', 0)
    return jsonify({"status": "success", "left_pwm": left_pwm_adjustment, "right_pwm": right_pwm_adjustment})

def propose_speed(speed):
    """Send a proposed speed to Robot B."""
    payload = {"type": "proposal", "speed": speed}
    try:
        response = requests.post(f"{ROBOT_B_URL}/negotiate", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error proposing speed: {e}")
        return {}

def respond_to_proposal(response_type):
    """Send a response (ok or no) to Robot B."""
    payload = {"type": "response", "response": response_type}
    try:
        response = requests.post(f"{ROBOT_B_URL}/negotiate", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error responding to proposal: {e}")
        return {}

def negotiate_speed():
    """Negotiate speed with Robot B."""
    speed = INITIAL_SPEED
    agreed = False

    print("Starting negotiation with Robot B...")

    while not agreed:
        try:
            # Step 1: Propose a speed to Robot B
            print(f"Proposing speed: {speed}")
            response = propose_speed(speed)

            # Step 2: Handle Robot B's response
            if response.get("type") == "response":
                if response.get("response") == "ok":
                    print("Robot B agreed! Target speed:", speed)
                    agreed = True
                    target_speed = speed  # Set the agreed speed
                elif response.get("response") == "no":
                    print("Robot B disagreed. Adjusting speed...")
                    speed += 10  # Adjust speed (you can choose a smarter logic here)
                else:
                    print("Unknown response from Robot B:", response)

            elif response.get("type") == "proposal":
                proposed_speed = response.get("speed")
                print(f"Robot B proposed: {proposed_speed}")
                if proposed_speed == speed:
                    print("Agreeing to Robot B's proposal!")
                    respond_to_proposal("ok")
                    agreed = True
                    target_speed = speed  # Set the agreed speed
                else:
                    print("Disagreeing with Robot B's proposal.")
                    respond_to_proposal("no")
                    speed = (speed + proposed_speed) // 2  # Adjust speed

            time.sleep(1)  # Add a delay to avoid spamming

        except Exception as e:
            print("Unexpected error:", e)
            break

def main():
    """Main function to setup GPIO, start Flask server, and control loop."""
    setup_gpio()
    global counter, clkLastState
    clkLastState = GPIO.input(ENCODER_CLK)

    # Add a small delay before setting up event detection
    time.sleep(0.1)

    # Setup event detection for encoder
    GPIO.add_event_detect(ENCODER_CLK, GPIO.BOTH, callback=encoder_callback, bouncetime=10)

    # Start Flask server in a separate thread
    flask_thread = Thread(target=app.run, kwargs={"port": 5001})
    flask_thread.start()

    # Start negotiation in a separate thread
    negotiation_thread = Thread(target=negotiate_speed)
    negotiation_thread.start()

    # Control loop
    try:
        while True:
            # Read encoder value
            encoder_value = counter
            
            # Calculate error (we want encoder_value to be 0)
            error = target_speed - encoder_value
            
            # Calculate motor speed adjustment
            adjustment = Kp * error
            
            # Apply PWM adjustments
            left_speed = adjustment + left_pwm_adjustment
            right_speed = -adjustment + right_pwm_adjustment
            
            # Set motor speed to correct the error
            set_motor_speed(left_speed, right_speed)
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop PWM and clean up GPIO
        pwm_left_in1.stop()
        pwm_left_in2.stop()
        pwm_right_in3.stop()
        pwm_right_in4.stop()
        set_motor_speed(0, 0)
        GPIO.cleanup()

if __name__ == "__main__":
    main()
