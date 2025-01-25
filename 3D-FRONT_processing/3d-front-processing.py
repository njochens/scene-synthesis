# IMPORTS

import json, subprocess, cv2, math, os, shutil
from pathlib import Path
from itertools import chain
from file import Directory
from utils import TriangleMesh, TDFRoom, TDFFurniture

# INPUTS

dataset_directory = Path("3D-FRONT")
output_directory = "2D-FRONT"  

# FOLDER VARIABLES

svg_directory = f"{output_directory}/svg"
svg_floor_plans_directory = f"{output_directory}/svg_floor_plans"
png_directory = f"{output_directory}/png"
png_floor_plans_directory = f"{output_directory}/png_floor_plans"
json_directory = f"{output_directory}/json"

folders_to_clean = [png_floor_plans_directory,
                    svg_floor_plans_directory,
                    png_directory,
                    svg_directory,
                    json_directory]

# PATH CLEANUP AND CREATION

for folder_path in folders_to_clean:
    shutil.rmtree(folder_path)
    print(f"Cleaned and removed: {folder_path}")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# JID to CATEGORY dictionary

if os.path.exists(f"{output_directory}/jid_cat_dict.json"):
    print("JID_CAT_DICTIONARY found!")
    with open(f"{output_directory}/jid_cat_dict.json", 'r') as file:
        jid_cat_dict = json.load(file)
else:
    print("JID_CAT_DICTIONARY not found! Creating ...")
    jid_dict_file = open(f"{output_directory}/jid_cat_dict.json", "w")
    jid_cat_dict = {}
    dataset_dir_jid = Directory(dataset_directory)
    file = dataset_dir_jid.next()
    while file != None:
        if dataset_dir_jid.current_filename != "":
            print("JID_CAT_DICT - " + str(dataset_dir_jid.index) + ": " + dataset_dir_jid.current_filename)
            json_data = json.loads(file)
            json_furniture = json_data.get("furniture")
            for f in json_furniture:
                if f.get("title") != "" and f.get("title") != None:
                        jid_cat_dict[f.get("jid")] = f.get("title")
        file = dataset_dir_jid.next()
    jid_dict_file.write(json.dumps(jid_cat_dict))
    jid_dict_file.close()

# Color dictionary
color_alpha_dict = {
    # Chair
    'chair':                    ['#6b8e23', 0.9],
    # Bed
    'bed':                      ['#f39ca2', 0.9],
    # Tables
    'table':                    ['#8baddc', 0.9],
    # Storage
    'storage unit':             ['#c693c2', 0.9],
    'wardrobe':                 ['#c693c2', 0.9],
    'cabinet':                  ['#c693c2', 0.9],
    'kitchen cabinet':          ['#c693c2', 0.9],
    # Sofa
    'sofa':                     ['#8b6b5b', 0.9],
    # TV and electrics
    'media unit':               ['#555555', 0.9],
    'appliance':                ['#555555', 0.0],
    'electronics':              ['#555555', 0.0],
    'electric':                 ['#555555', 0.0],
    # Light
    'lighting':                 ['#fff59b', 0.5],
    # Plants
    'plants':                   ['#55ff55', 0.5],
    # Other
    'accessory':                ['#000000', 0.0],
    'art':                      ['#000000', 0.0],
    'recreation':               ['#000000', 0.0],
    'outdoor furniture':        ['#000000', 0.0],
    'rug':                      ['#000000', 0.0],
    'basin':                    ['#000000', 0.0],
    'mirror':                   ['#000000', 0.0],
    'bath':                     ['#000000', 0.0],
    'stair':                    ['#000000', 0.0],
    'build element':            ['#000000', 0.0],
    'shower':                   ['#000000', 0.0],
    '200 - on the floor':       ['#000000', 0.0],
    '300 - on top of others':   ['#000000', 0.0],
}

# OTHER VARIABLES

bedroom_categories = ["Bedroom", "MasterBedroom", "SecondBedroom", "Bedroom", "BedRoom"]
livingroom_categories = ["Livingroom", "LivingDiningRoom", "LivingRoom", "DiningRoom"]
bathroom_categories = ["MasterBathroom", "SecondBathroom", "BathRoom", "Bathroom"]
png_size = 500
scale = 30

# PROCESSING

for index, file in enumerate(dataset_directory.iterdir()):
    if file.is_file() and file.suffix == ".json":
        print(f"{index} - {file.name}")
        with file.open("r", encoding="utf-8") as json_file:
            json_obj = json.load(json_file)
            # Copy general furniture information
            furniture_collection = json_obj.get("furniture")
            # Cycle through rooms
            for room_entry in json_obj.get("scene").get("room"):
                # Check if its a living or bedroom
                if room_entry.get("type") in bedroom_categories + livingroom_categories + bathroom_categories:
                    bed_placed = False
                    # Process floor plan info
                    room_meshes = [entry.get("xyz") for entry in json_obj.get("mesh") if room_entry.get('instanceid').split("-")[1] in entry.get("uid")]
                    room_mesh = list(chain.from_iterable(room_meshes))
                    # Draw room_meshes in a svg file
                    triangle_mesh = TriangleMesh([])
                    triangle_mesh.from_list(room_mesh)
                    if len(triangle_mesh.triangles) > 0:
                        tdfroom = TDFRoom(room_entry, file.name)
                        [tx, ty, scale] = triangle_mesh.resize_and_pad(png_size, scale = scale)
                        with open(f"{svg_floor_plans_directory}/{file.name}-{room_entry.get('instanceid')}.svg", "w", encoding="utf-8") as svg_file:
                            svg_file.write(triangle_mesh.to_svg_full("#000000", "#000000", width = png_size, height = png_size))
                        # Convert svg to png
                        _ = subprocess.run(["convert", f"{svg_floor_plans_directory}/{file.name}-{room_entry.get('instanceid')}.svg", "-alpha", "off", "-antialias", "-threshold", "50%", f"{png_floor_plans_directory}/{file.name}-{room_entry.get('instanceid')}.png"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                        # Extract corners from png
                        image = cv2.imread(f"{png_floor_plans_directory}/{file.name}-{room_entry.get('instanceid')}.png", cv2.IMREAD_GRAYSCALE)
                        _, binary_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
                        contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE )
                        contour = max(contours, key=cv2.contourArea)
                        #approx = cv2.approxPolyDP(contour, 0.00000001 * cv2.arcLength(contour, True), True)
                        corners = [[x, y] for [x, y] in map(lambda p: p.ravel(), contour)]
                        # Check for disconnected components
                        num_labels, labels = cv2.connectedComponents(binary_image)
                        num_components = num_labels - 2
                        if num_components > 1:
                            if os.path.exists(f"{svg_floor_plans_directory}/{file.name}-{room_entry.get('instanceid')}.svg"):
                                os.remove(f"{svg_floor_plans_directory}/{file.name}-{room_entry.get('instanceid')}.svg")
                            if os.path.exists(f"{png_floor_plans_directory}/{file.name}-{room_entry.get('instanceid')}.png"):
                                os.remove(f"{png_floor_plans_directory}/{file.name}-{room_entry.get('instanceid')}.png")
                        else:
                            tdfroom.set_corners(corners)
                            # Extract furniture from file
                            for child in room_entry.get("children"):
                                if child.get('instanceid').split("/")[0] == "furniture":
                                    rot = child.get("rot")
                                    pos = child.get("pos")
                                    model = child.get("ref")
                                    if not math.isnan(child.get("pos")[0]):  
                                        for furniture_entry in furniture_collection:
                                            if furniture_entry.get("uid") == model:
                                                if furniture_entry.get("title") != None and furniture_entry.get("bbox") != None:
                                                    tdffurniture = TDFFurniture(furniture_entry, child)
                                                    category = jid_cat_dict.get(tdffurniture.jid)
                                                    if category != None:
                                                        category_split = category.split("/")
                                                        meta_category = category_split[0]
                                                        if len(category_split) > 1:
                                                            category_detailed = category_split[1]
                                                        tdffurniture.category = meta_category
                                                        tdffurniture.category_detailed = category_detailed
                                                        color_alpha = color_alpha_dict.get(tdffurniture.category)
                                                        if color_alpha == None:
                                                            color_alpha = ['#000000', 0.0]
                                                        tdffurniture.color = color_alpha[0]
                                                        tdffurniture.alpha = color_alpha[1]
                                                        if tdffurniture.category == "bed":
                                                            bed_placed = True
                                                        tdfroom.add_tdffurniture(tdffurniture)
                            if len(tdfroom.furniture) > 0: # Check that room is populated
                                if room_entry.get("type") in bedroom_categories and not bed_placed:
                                    if os.path.exists(f"{svg_floor_plans_directory}/{file.name}-{room_entry.get('instanceid')}.svg"):
                                        os.remove(f"{svg_floor_plans_directory}/{file.name}-{room_entry.get('instanceid')}.svg")
                                    if os.path.exists(f"{png_floor_plans_directory}/{file.name}-{room_entry.get('instanceid')}.png"):
                                        os.remove(f"{png_floor_plans_directory}/{file.name}-{room_entry.get('instanceid')}.png")
                                    continue
                                # Concert to regular room object
                                room = tdfroom.to_room()
                                # Correct furniture scaling
                                for obj in room.objects:
                                    obj.resize(scale)
                                    obj.move_by(tx, ty)
                                # Save to json file
                                with open(f"{json_directory}/{room_entry.get('instanceid')}.json", "w", encoding="utf-8") as json_file:
                                    json_file.write(json.dumps(room.to_json()))
                                # Save as svg file
                                with open(f"{svg_directory}/{room_entry.get('instanceid')}.svg", "w", encoding="utf-8") as svg_file:
                                    svg_file.write(room.to_svg_file(height = png_size, width = png_size))
                                # Convert to png file
                                _ = subprocess.run(["convert", f"{svg_directory}/{room_entry.get('instanceid')}.svg", "-alpha", "off", "-antialias", "off", f"{png_directory}/{room_entry.get('instanceid')}.png"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                                            
# CLEANUP

shutil.rmtree(svg_floor_plans_directory)
shutil.rmtree(svg_directory)
shutil.rmtree(png_floor_plans_directory)
