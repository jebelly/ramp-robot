import requests

def start_robot_b(speed):
    url = 'http://10.243.91.50:5000/start'  # Replace <robot_b_ip> with the actual IP address of Robot B
    payload = {'speed': speed}
    response = requests.post(url, json=payload)
    return response.json()

if __name__ == "__main__":
    speed = 50  # Example speed value
    response = start_robot_b(speed)
    print(response)