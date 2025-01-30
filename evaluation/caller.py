# IMPORTS

import requests

# CALLER

def send_post_request(address, port, endpoint, payload):
    url = f"{address}:{port}{endpoint}"
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    except json.JSONDecodeError:
        print("Failed to decode JSON from the response.")
        return None
