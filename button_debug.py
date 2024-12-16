import RPi.GPIO as GPIO
import time

# Define GPIO pins
LEFT_BUTTON_PIN = 36  # GPIO pin for left button
RIGHT_BUTTON_PIN = 32  # GPIO pin for right button

# Setup GPIO mode
GPIO.setmode(GPIO.BOARD)

# Setup button pins
GPIO.setup(LEFT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(RIGHT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        left_button_pressed = GPIO.input(LEFT_BUTTON_PIN)
        right_button_pressed = GPIO.input(RIGHT_BUTTON_PIN)

        # Print button states
        print(f"Left button pressed: {left_button_pressed}")
        print(f"Right button pressed: {right_button_pressed}")

        time.sleep(0.5)  # Delay to make the output readable

except KeyboardInterrupt:
    print("Exiting program")

finally:
    GPIO.cleanup()  # Clean up GPIO settings