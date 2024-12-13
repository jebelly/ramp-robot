import requests
import time

# Configuration
ROBOT_B_URL = "http://robot_b_address:5000"  # Replace with Robot B's API address
INITIAL_SPEED = 50  # Starting speed for negotiation

def propose_speed(speed):
    """Send a proposed speed to Robot B."""
    payload = {"type": "proposal", "speed": speed}
    try:
        response = requests.post(f"{ROBOT_B_URL}/negotiate", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error proposing speed: {e}")
        return {}

def respond_to_proposal(response_type):
    """Send a response (ok or no) to Robot B."""
    payload = {"type": "response", "response": response_type}
    try:
        response = requests.post(f"{ROBOT_B_URL}/negotiate", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error responding to proposal: {e}")
        return {}

def main():
    speed = INITIAL_SPEED
    agreed = False

    print("Starting negotiation with Robot B...")

    while not agreed:
        try:
            # Step 1: Propose a speed to Robot B
            print(f"Proposing speed: {speed}")
            response = propose_speed(speed)

            # Step 2: Handle Robot B's response
            if response.get("type") == "response":
                if response.get("response") == "ok":
                    print("Robot B agreed! Target speed:", speed)
                    agreed = True
                elif response.get("response") == "no":
                    print("Robot B disagreed. Adjusting speed...")
                    speed += 10  # Adjust speed (you can choose a smarter logic here)
                else:
                    print("Unknown response from Robot B:", response)

            elif response.get("type") == "proposal":
                proposed_speed = response.get("speed")
                print(f"Robot B proposed: {proposed_speed}")
                if proposed_speed == speed:
                    print("Agreeing to Robot B's proposal!")
                    respond_to_proposal("ok")
                    agreed = True
                else:
                    print("Disagreeing with Robot B's proposal.")
                    respond_to_proposal("no")
                    speed = (speed + proposed_speed) // 2  # Adjust speed

            time.sleep(1)  # Add a delay to avoid spamming

        except Exception as e:
            print("Unexpected error:", e)
            break

if __name__ == "__main__":
    main()