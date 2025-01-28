#IMPORTS

import json, sys, os, random
from PIL import Image

external_folder = os.path.relpath("..")
if external_folder not in sys.path:
    sys.path.append(external_folder)

from visualizier import draw_floorplan
from caller import send_post_request

# UTILS


def fuse_images_side_by_side(image_path1, image_path2, output_path):
    img1 = Image.open(image_path1)
    img2 = Image.open(image_path2)
    if img1.height != img2.height:
        img2 = img2.resize((int(img2.width * (img1.height / img2.height)), img1.height))
    fused_width = img1.width + img2.width
    fused_height = img1.height
    fused_image = Image.new("RGB", (fused_width, fused_height))
    fused_image.paste(img1, (0, 0))
    fused_image.paste(img2, (img1.width, 0))
    fused_image.save(output_path)

# VARIABLES

mode = "file"
output_directory = "output"
original_directory = "../../3D-FRONT_processing/2D-FRONT-CUSTOM-FORMAT"
address = "http://localhost"
port = 5002
endpoint = "/populate"

# PROCESS JSONS

all_files = [f for f in os.listdir(original_directory) if os.path.isfile(os.path.join(original_directory, f))]

for i in range(1,11):
    random_file = random.choice(all_files)
    with open(f'{original_directory}/{random_file}', "r") as file:
        input_json = json.load(file)
        response_json = send_post_request(address, port, endpoint, input_json)
        response_json = response_json.replace("'", '"')
        draw_floorplan(input_json, f'{output_directory}/{i}-original.png')
        draw_floorplan(json.loads(response_json), f'{output_directory}/{i}-generated.png')
        fuse_images_side_by_side(f'{output_directory}/{i}-original.png', f'{output_directory}/{i}-generated.png', f'{output_directory}/{i}.png')
        os.remove(f'{output_directory}/{i}-original.png')
        os.remove(f'{output_directory}/{i}-generated.png')