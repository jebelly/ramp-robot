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
    url = f"http://10.243.91.238:5000/start?delay={delay}"
    while True:
        try:
            response = requests.post(url)
            if response.status_code == 200 and response.json().get("status") == "ok":
                print(f"Start signal sent to Robot A with delay {delay}")
                return True
            else:
                print(f"Robot A is not ready or already started, status: {response.json().get('status')}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending start signal to Robot A: {e}")
        time.sleep(1)  # Retry every second

def send_target_speed(speed):
    url = f"http://10.243.91.238:5000/speed/{speed}"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            return True
        else:
            print(f"Failed to set speed {speed}, status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error sending speed to Robot A: {e}")
        return False

@app.route('/start', methods=['POST'])
def receive_start_signal():
    global start_signal
    start_signal = True
    return jsonify({"status": "ok"}), 200

@app.route('/speed/<int:speed>', methods=['POST'])
def receive_speed(speed):
    global current_speed
    current_speed = speed
    return jsonify({"status": "ok"}), 200

def run_server():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Start the Flask server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # Example delay value
    delay = 5
    if start_robot_a(delay):
        print("Robot A started successfully")
    else:
        print("Failed to start Robot A")

    # Wait for the start signal
    while not start_signal:
        time.sleep(0.1)
    
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
        time.sleep(1)