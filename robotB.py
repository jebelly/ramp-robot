import requests
from flask import Flask, request, jsonify
import threading
import time
import random

app = Flask(__name__)

# Global variables to store the target speed and start signal
current_speed = None  # Variable to keep track of the current speed
start_signal = False

def start_robot_a(delay):
    url = f"http://10.243.91.238:5000/start/{delay}"
    try:
        response = requests.post(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error sending start signal to Robot A: {e}")
        return None

def send_target_speed(speed):
    url = f"http://10.243.91.238:5000/target/{speed}"
    try:
        response = requests.post(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

@app.route('/start/<int:delay>', methods=['POST'])
def start(delay):
    global start_signal
    if 1 <= delay <= 10:
        threading.Timer(delay, set_start_signal).start()
        return jsonify({"status": "Robot B will start after delay"}), 200
    else:
        return jsonify({"error": "Invalid delay value"}), 400

def set_start_signal():
    global start_signal
    start_signal = True

def autonomous_operation(delay):
    global current_speed
    time.sleep(delay)
    print("Begin autonomous operation for Robot B")
    while True:
        # Generate a random speed value between 1 and 1000
        speed = random.randint(1, 1000)
        
        if speed != current_speed:
            response = send_target_speed(speed)
            if response:
                print(f"Speed {speed} set successfully")
                current_speed = speed
            else:
                print(f"Failed to set speed {speed}")
        
        time.sleep(2)  # Ensure requests are not sent more frequently than every 2 seconds

def check_robot_a_ready():
    url = "http://10.243.91.238:5000/ready"
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("Robot A is ready")
                return True
        except requests.exceptions.RequestException as e:
            print(f"Error checking Robot A readiness: {e}")
        time.sleep(1)  # Retry every second

def run_server():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Start the Flask server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # Check if Robot A is ready
    if check_robot_a_ready():
        # Send start signal to Robot A with a delay of 5 seconds
        start_robot_a(5)
        # Start autonomous operation with a delay of 5 seconds
        autonomous_operation(5)