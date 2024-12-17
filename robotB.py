import requests
from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)

def start_robot_b(delay):
    url = f"http://10.243.91.238:5000/start/{delay}"
    try:
        response = requests.post(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
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
    if 1 <= delay <= 10:
        threading.Thread(target=autonomous_operation, args=(delay,)).start()
        return jsonify({"status": "Robot started"}), 200
    else:
        return jsonify({"error": "Invalid delay value"}), 400

@app.route('/target/<int:speed>', methods=['POST'])
def target(speed):
    if 1 <= speed <= 1000:
        response = send_target_speed(speed)
        if response:
            return jsonify({"status": "Speed set"}), 200
        else:
            return jsonify({"error": "Failed to set speed"}), 500
    else:
        return jsonify({"error": "Invalid speed value"}), 400

@app.route('/receive_message', methods=['POST'])
def receive_message():
    data = request.json
    print(f"Received message: {data}")
    return jsonify({"status": "Message received"}), 200

def autonomous_operation(delay):
    time.sleep(delay)
    print("Begin autonomous operation for Robot B")
    while True:
        # Example autonomous operation
        speed = 50  # Example speed value
        response = send_target_speed(speed)
        if response:
            print("Speed set successfully")
        else:
            print("Failed to set speed")
        time.sleep(0.5)  # Ensure requests are not sent more frequently than 10 Hz

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
        # Start autonomous operation with a delay of 5 seconds
        autonomous_operation(5)