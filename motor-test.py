import RPi.GPIO as GPIO
import time



# Function to set motor direction and speed
def set_motor_speed(left_speed, right_speed):
    GPIO.output(LEFT_MOTOR_IN1, GPIO.HIGH if left_speed > 0 else GPIO.LOW)
    GPIO.output(LEFT_MOTOR_IN2, GPIO.LOW if left_speed > 0 else GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_IN3, GPIO.HIGH if right_speed > 0 else GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_IN4, GPIO.LOW if right_speed > 0 else GPIO.HIGH)

# Test motors
try:

        # Define GPIO pins
    LEFT_MOTOR_IN1 = 15
    LEFT_MOTOR_IN2 = 16
    RIGHT_MOTOR_IN3 = 12
    RIGHT_MOTOR_IN4 = 11
    
    # Setup GPIO
    GPIO.setmode(GPIO.BOARD)
    
    left_motor_pwm = GPIO.PWM(LEFT_MOTOR_IN1, 1000)  # 1kHz frequency
    right_motor_pwm = GPIO.PWM(RIGHT_MOTOR_IN3, 1000)  # 1kHz frequency

    # Start PWM with 0 duty cycle to ensure motors are off
    left_motor_pwm.start(0)
    right_motor_pwm.start(0)
    print("Setting motors to forward")
    set_motor_speed(1, 1)
    time.sleep(2)
    print("Setting motors to backward")
    set_motor_speed(-1, -1)
    time.sleep(2)

finally:
    GPIO.cleanup()