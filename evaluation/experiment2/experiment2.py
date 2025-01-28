#IMPORTS

import json, sys, os

external_folder = os.path.relpath("..")
if external_folder not in sys.path:
    sys.path.append(external_folder)

from visualizier import draw_floorplan
from caller import send_post_request

# VARIABLES

mode = "file"
output_directory = "output"
address = "http://localhost"
port = 5002
endpoint = "/populate"

# PROCESS JSONS

floorplan1_path = "input/floorplan1.json"
floorplan2_path = "input/floorplan2.json"

for path in [floorplan1_path, floorplan2_path]:
    with open(path, "r") as file:
        input_json = json.load(file)
        for seed in range(1,5):
            input_json["seed"] = seed
            response_json = send_post_request(address, port, endpoint, input_json)
            response_json = response_json.replace("'", '"')
            draw_floorplan(json.loads(response_json), f'{output_directory}/{path.split("/")[1].split(".")[0]}-{seed}.png')