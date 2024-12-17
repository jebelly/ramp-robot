
import time
import RPi.GPIO as GPIO

# Constants
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
GPIO.setmode(GPIO.BOARD)

def setup_gpio():
    """Setup GPIO pins and PWM."""
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

# Global variables for encoder
counter = 0
clkLastState = GPIO.input(ENCODER_CLK)

def encoder_callback(channel):
    global counter, clkLastState
    clkState = GPIO.input(ENCODER_CLK)
    dtState = GPIO.input(ENCODER_DT)
    if clkState != clkLastState:
        if dtState != clkState:
            counter += 1
        else:
            counter -= 1
    clkLastState = clkState

def main():
    setup_gpio()
    global counter, clkLastState
    clkLastState = GPIO.input(ENCODER_CLK)

    # Add a small delay before setting up event detection
    time.sleep(0.1)

    # Setup event detection for encoder
    GPIO.add_event_detect(ENCODER_CLK, GPIO.BOTH, callback=encoder_callback, bouncetime=10)

    # Control loop
    try:
        while True:
            # Read encoder value
            encoder_value = counter
            
            # Calculate error (we want encoder_value to be 0)
            error = -encoder_value
            
            # Calculate motor speed adjustment
            adjustment = Kp * error
            
            # Set motor speed to correct the error
            set_motor_speed(adjustment, -adjustment)
            
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
