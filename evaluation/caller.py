# IMPORTS

import requests, json
from pathlib import Path
from visualizier import draw_floorplan

# CALLER

def send_post_request(address, port, endpoint, payload):
    url = f"{address}:{port}{endpoint}"
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
        
        # Attempt to parse the response as JSON
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    except json.JSONDecodeError:
        print("Failed to decode JSON from the response.")
        return None

# VARIABLES



# MAIN

if __name__ == "__main__":
    mode = "both"
    output_directory = "."
    input_directory = Path("../population_midiffusion/examples")
    address = "http://localhost"
    port = 5002
    endpoint = "/populate"

    for index, file in enumerate(input_directory.iterdir()):
        if file.is_file() and file.suffix == ".json":
            with file.open("r", encoding="utf-8") as json_file:
                payload = json.load(json_file)
                response_json = send_post_request(address, port, endpoint, payload)

                if response_json is not None:
                    print("Response JSON:")
                    response_json = response_json.replace("'", '"')
                    print(response_json)
                    draw_floorplan(json.loads(response_json), output_directory + file.stem + ".png")
                else:
                    print("No valid JSON response received.")


