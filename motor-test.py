import RPi.GPIO as GPIO
import time

# Define GPIO pins
LEFT_MOTOR_IN1 = 15
LEFT_MOTOR_IN2 = 16
RIGHT_MOTOR_IN3 = 12
RIGHT_MOTOR_IN4 = 11

# Setup GPIO
GPIO.setmode(GPIO.BOARD)
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

# Test motors
try:
    print("Setting motors to forward")
    set_motor_speed(1, 1)
    time.sleep(2)
    print("Setting motors to backward")
    set_motor_speed(-1, -1)
    time.sleep(2)
finally:
    GPIO.cleanup()