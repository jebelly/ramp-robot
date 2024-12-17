# This file contains the code for the negotiation server that will be run on computer A. 
# The server will handle the negotiation process with Robot B to determine the optimal speed for both robots. 
# The server will receive proposals from Robot B, propose speeds to Robot B, and respond to proposals from Robot B. 
# The negotiation process will continue until a mutually acceptable speed is reached by both robots.
# Import necessary libraries
import requests
from flask import Flask, request, jsonify
import threading
import time

# Initialize Flask app
app = Flask(__name__)

# Define constants
INITIAL_SPEED = 50  # Starting speed for negotiation
ROBOT_B_URL = 'http://10.243.91.50:5000'  # Replace <robot_b_ip> with the actual IP address of Robot B

# Script Outline

@app.route('/start/<int:delay>', methods=['POST'])
def start(delay):
    if 1 <= delay <= 10:
        threading.Thread(target=autonomous_operation, args=(delay,)).start()
        return jsonify({"status": "Robot A started"}), 200
    else:
        return jsonify({"error": "Invalid delay value"}), 400

@app.route('/target/<int:speed>', methods=['POST'])
def target(speed):
    if 1 <= speed <= 100:
        response = send_target_speed(speed)
        if response:
            return jsonify({"status": "Speed set"}), 200
        else:
            return jsonify({"error": "Failed to set speed"}), 500
    else:
        return jsonify({"error": "Invalid speed value"}), 400

def send_target_speed(speed):
    url = f"http://10.243.91.50:5000/target/{speed}"
    try:
        response = requests.post(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def autonomous_operation(delay):
    time.sleep(delay)
    print("Begin autonomous operation for Robot A")
    while True:
        # Example autonomous operation
        speed = 50  # Example speed value
        response = send_target_speed(speed)
        if response:
            print("Speed set successfully")
        else:
            print("Failed to set speed")
        time.sleep(0.1)  # Ensure requests are not sent more frequently than 10 Hz

# Main entry point
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)