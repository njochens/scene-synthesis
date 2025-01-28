# IMPORTS

import json
from pathlib import Path
from visualizier import draw_floorplan
from caller import send_post_request

# VARIABLES

mode = "file"
output_directory = "processed"
input_directory = Path("../3D-FRONT_processing/2D-FRONT-POPULATION-FORMAT")
address = "http://localhost"
port = 5002
endpoint = "/populate"

# MAIN

for index, file in enumerate(input_directory.iterdir()):
    if file.is_file() and file.suffix == ".json":
        with file.open("r", encoding="utf-8") as json_file:
            print(f"{index}: {file.stem}")
            payload = json.load(json_file)
            response_json = send_post_request(address, port, endpoint, payload)

            if response_json is not None:
                response_json = response_json.replace("'", '"')
                draw_floorplan(json.loads(response_json), output_directory + "/" + file.stem + ".png")
            else:
                print("No valid JSON response received.")
