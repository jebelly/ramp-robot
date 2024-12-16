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

# Main control loop
try:
    TARGET_SPEED = 50  # Example target speed from Robot B
    while True:
        left_button_pressed = GPIO.input(LEFT_BUTTON_PIN)
        right_button_pressed = GPIO.input(RIGHT_BUTTON_PIN)

        # Debugging print statements for button inputs
        print(f"Left button pressed: {left_button_pressed}")
        print(f"Right button pressed: {right_button_pressed}")

        left_speed = TARGET_SPEED
        right_speed = TARGET_SPEED

        if left_button_pressed and not right_button_pressed:
            # Adjust speed based on left button press
            left_speed -= 10  # Slow down left motor
        elif right_button_pressed and not left_button_pressed:
            # Adjust speed based on right button press
            right_speed -= 10  # Slow down right motor
        elif left_button_pressed and right_button_pressed:
            # Adjust speed based on both buttons pressed
            left_speed -= 5
            right_speed -= 5

        set_motor_speed(left_speed, right_speed)

        # Print motor speeds for debugging
        print(f"Left motor speed: {left_speed}, Right motor speed: {right_speed}")

        time.sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()

