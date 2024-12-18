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

# Initialize PWM
left_motor_pwm = GPIO.PWM(LEFT_MOTOR_IN1, 1000)  # 1kHz frequency
right_motor_pwm = GPIO.PWM(RIGHT_MOTOR_IN3, 1000)  # 1kHz frequency

# Start PWM with 0 duty cycle to ensure motors are off
left_motor_pwm.start(0)
right_motor_pwm.start(0)

# Function to set motor direction and speed
def set_motor_speed(left_speed, right_speed):
    left_duty_cycle = min(max(abs(left_speed) / 20, 0), 50)
    right_duty_cycle = min(max(abs(right_speed) / 20, 0), 50)
    
    GPIO.output(LEFT_MOTOR_IN1, GPIO.HIGH if left_speed > 0 else GPIO.LOW)
    GPIO.output(LEFT_MOTOR_IN2, GPIO.LOW if left_speed > 0 else GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_IN3, GPIO.HIGH if right_speed > 0 else GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_IN4, GPIO.LOW if right_speed > 0 else GPIO.HIGH)
    
    left_motor_pwm.ChangeDutyCycle(left_duty_cycle)
    right_motor_pwm.ChangeDutyCycle(right_duty_cycle)

# Test motors
try:
    print("Setting motors to forward")
    set_motor_speed(20, 20)  # Use a higher speed value for testing
    time.sleep(2)
    print("Setting motors to backward")
    set_motor_speed(-20, -20)  # Use a higher speed value for testing
    time.sleep(2)
finally:
    print("Stopping motors and cleaning up GPIO")
    set_motor_speed(0, 0)
    GPIO.cleanup()