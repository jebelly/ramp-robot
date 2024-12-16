import RPi.GPIO as GPIO
import time

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
# We will also set up the PWM pins for the motors.

GPIO.setmode(GPIO.BOARD)

# Define GPIO pins
left_button_pin = 16
right_button_pin = 18
left_motor_in1 = 11
left_motor_in2 = 13
right_motor_in3 = 15
right_motor_in4 = 19
left_motor_pwm_pin = 33
right_motor_pwm_pin = 35

# Setup button pins
GPIO.setup(left_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(right_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Setup motor pins
GPIO.setup(left_motor_in1, GPIO.OUT)
GPIO.setup(left_motor_in2, GPIO.OUT)
GPIO.setup(right_motor_in3, GPIO.OUT)
GPIO.setup(right_motor_in4, GPIO.OUT)
GPIO.setup(left_motor_pwm_pin, GPIO.OUT)
GPIO.setup(right_motor_pwm_pin, GPIO.OUT)

# Setup PWM for motors
left_motor_pwm = GPIO.PWM(left_motor_pwm_pin, 1000)
right_motor_pwm = GPIO.PWM(right_motor_pwm_pin, 1000)
left_motor_pwm.start(0)
right_motor_pwm.start(0)

# Function to set motor speed
def set_motor_speed(left_speed, right_speed):
    GPIO.output(left_motor_in1, GPIO.HIGH if left_speed > 0 else GPIO.LOW)
    GPIO.output(left_motor_in2, GPIO.LOW if left_speed > 0 else GPIO.HIGH)
    GPIO.output(right_motor_in3, GPIO.HIGH if right_speed > 0 else GPIO.LOW)
    GPIO.output(right_motor_in4, GPIO.LOW if right_speed > 0 else GPIO.HIGH)
    left_motor_pwm.ChangeDutyCycle(abs(left_speed))
    right_motor_pwm.ChangeDutyCycle(abs(right_speed))


# Motor control
# We control the left and right motors using a L298N motor driver.
# The L298N motor driver has two inputs for each motor (IN1, IN2 for the left motor, IN3, IN4 for the right motor).
# We will use PWM to control the speed of the motors.


# Main control loop
# We will implement the main control loop for Robot A.
# We will read the button inputs to determine if the tube is skewed.
# We will adjust the speed of the motors based on the button inputs.
# We will use the PWM feature of the GPIO library to control the speed of the motors.
# We will continuously read the button inputs and adjust the speed of the motors accordingly.
# We will also print the speed of the motors to the console for debugging purposes.

try:
    while True:
        left_button_pressed = GPIO.input(left_button_pin)
        right_button_pressed = GPIO.input(right_button_pin)

        if left_button_pressed and not right_button_pressed:
            # Adjust speed based on left button press
            # ...existing code...
            set_motor_speed(50, 60)  # Example values
        elif right_button_pressed and not left_button_pressed:
            # Adjust speed based on right button press
            # ...existing code...
            set_motor_speed(60, 50)  # Example values
        elif left_button_pressed and right_button_pressed:
            # Adjust speed based on both buttons pressed
            # ...existing code...
            set_motor_speed(55, 55)  # Example values
        else:
            # Default motor speed
            set_motor_speed(50, 50)  # Example values

        # Print motor speeds for debugging
        print(f"Left motor speed: {left_motor_pwm_pin}, Right motor speed: {right_motor_pwm_pin}")

        time.sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    left_motor_pwm.stop()
    right_motor_pwm.stop()
    GPIO.cleanup()

