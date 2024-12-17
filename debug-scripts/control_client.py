import requests

# Send a start request with a delay of 5 seconds
start_url = "http://10.243.91.238:5000/start/5"
try:
    response = requests.post(start_url)
    response.raise_for_status()
    print("Start request sent successfully")
except requests.exceptions.RequestException as e:
    print(f"Error sending start request: {e}")

# Send a target speed request with a speed of 500 mm/second
target_url = "http://10.243.91.238:5000/target/500"
try:
    response = requests.post(target_url)
    response.raise_for_status()
    print("Target speed request sent successfully")
except requests.exceptions.RequestException as e:
    print(f"Error sending target speed request: {e}")