## IMPORTS ##

import enum, os, sys, shutil, json, pickle
from numpy import load
import numpy as np
from panda3d.core import Triangulator, Point2

external_folder = os.path.abspath("/home/ThreedFront/")
if external_folder not in sys.path:
    sys.path.append(external_folder)
external_folder = os.path.abspath("/home/MiDiffusion/")
if external_folder not in sys.path:
    sys.path.append(external_folder)

from scripts.preprocess_floorplan import preprocess_floor_plan
from threed_front.datasets.threed_front import CachedRoom
from threed_front.rendering import get_floor_plan, scene_from_args, render_projection
from threed_front.simple_3dviz_setup import ORTHOGRAPHIC_PROJECTION_SCENE

## UTILS ##

# unfinished
def calc_scale(corners, bound):
    minx, maxx = min(corners[:, 0]), max(corners[:, 0])
    miny, maxy = min(corners[:, 1]), max(corners[:, 1])
    xlength = maxx - minx
    ylength = maxy - miny
    length = max(xlength, ylength)
    scale = bound/length
    return scale

def get_label_from_living_room(living_room_label):
    mapping = {
        LivingRoomLabel.ARMCHAIR: "Armchair",
        LivingRoomLabel.BOOOKSHELF: "Bookshelf",
        LivingRoomLabel.CABINET: "Cabinet",
        LivingRoomLabel.CEILING_LAMP: "CeilingLamp",
        LivingRoomLabel.CHAISE_LONGUE_SOFA: "ChaiseLongueSofa",
        LivingRoomLabel.CHINESE_CHAIR: "ChineseChair",
        LivingRoomLabel.COFFEE_TABLE: "CoffeeTable",
        LivingRoomLabel.CONSOLE_TABLE: "ConsoleTable",
        LivingRoomLabel.CORNER_SIDE_TABLE: "CornerSideTable",
        LivingRoomLabel.DESK: "Desk",
        LivingRoomLabel.DINING_CHAIR: "DiningChair",
        LivingRoomLabel.DINING_TABLE: "DiningTable",
        LivingRoomLabel.L_SHAPED_SOFA: "L-ShapedSofa",
        LivingRoomLabel.LAZY_SOFA: "LazySofa",
        LivingRoomLabel.LOUNGE_CHAIR: "LoungeChair",
        LivingRoomLabel.LOVESEAT_SOFA: "LoveseatSofa",
        LivingRoomLabel.MULTI_SEAT_SOFA: "Multi-SeatSofa",
        LivingRoomLabel.PENDANT_LAMP: "PendantLamp",
        LivingRoomLabel.ROUND_END_TABLE: "RoundEndTable",
        LivingRoomLabel.SHELF: "Shelf",
        LivingRoomLabel.STOOL: "Stool",
        LivingRoomLabel.TV_STAND: "TVStand",
        LivingRoomLabel.WARDROBE: "Wardrobe",
        LivingRoomLabel.WINE_CABINET: "WineCabinet",
    }
    return mapping.get(living_room_label.item(), None)

def get_label_from_bedroom(bedroom_label):
    mapping = {
        BedroomLabel.ARMCHAIR: "Armchair",
        BedroomLabel.BOOKSHELF: "Bookshelf",
        BedroomLabel.CABINET: "Cabinet",
        BedroomLabel.CEILINGLAMP: "CeilingLamp",
        BedroomLabel.CHAIR: "Chair",
        BedroomLabel.CHILDRENCABINET: "ChildrenCabinet",
        BedroomLabel.COFFEETABLE: "CoffeeTable",
        BedroomLabel.DESK: "Desk",
        BedroomLabel.DOUBLEBED: "DoubleBed",
        BedroomLabel.DRESSINGCHAIR: "DressingChair",
        BedroomLabel.DRESSINGTABLE: "DressingTable",
        BedroomLabel.KIDSBED: "KidsBed",
        BedroomLabel.NIGHTSTAND: "Nightstand",
        BedroomLabel.PENDANTLAMP: "PendantLamp",
        BedroomLabel.SHELF: "Shelf",
        BedroomLabel.SINGLEBED: "SingleBed",
        BedroomLabel.SOFA: "Sofa",
        BedroomLabel.STOOL: "Stool",
        BedroomLabel.TABLE: "Table",
        BedroomLabel.TVSTAND: "TVStand",
        BedroomLabel.WARDROBE: "Wardrobe",
    }
    return mapping.get(bedroom_label.item(), None)

def int_to_one_hot(i, roomtype):
    if roomtype == RoomType.BEDROOM:
        length = 22
    else:
        length = 25
    if not (0 <= i-1 < length):
        raise ValueError(f"Index {i} is out of bounds for a one-hot vector of length {length}.")
    one_hot = [0] * length
    one_hot[i-1] = 1
    float_array = [float(x) for x in one_hot]
    return float_array

def room_type_converter(type):
    if type == "Bedroom":
        return RoomType.BEDROOM
    elif type == "Livingroom":
        return RoomType.LIVINGROOM
    else:
        print(f"## ATTENTION: room type '{type}' is not supported! Using 'Bedroom' instead ##")
        return RoomType.BEDROOM

def get_bedroom_label(label):
    if label == "Armchair":
        return BedroomLabel.ARMCHAIR
    elif label == "Bookshelf":
        return BedroomLabel.BOOKSHELF
    elif label == "Cabinet":
        return BedroomLabel.CABINET
    elif label == "CeilingLamp":
        return BedroomLabel.CEILINGLAMP
    elif label == "Chair":
        return BedroomLabel.CHAIR
    elif label == "ChildrenCabinet":
        return BedroomLabel.CHILDRENCABINET
    elif label == "CoffeeTable":
        return BedroomLabel.COFFEETABLE
    elif label == "Desk":
        return BedroomLabel.DESK
    elif label == "DoubleBed":
        return BedroomLabel.DOUBLEBED
    elif label == "DressingChair":
        return BedroomLabel.DRESSINGCHAIR
    elif label == "DressingTable":
        return BedroomLabel.DRESSINGTABLE
    elif label == "KidsBed":
        return BedroomLabel.KIDSBED
    elif label == "Nightstand":
        return BedroomLabel.NIGHTSTAND
    elif label == "PendantLamp":
        return BedroomLabel.PENDANTLAMP
    elif label == "Shelf":
        return BedroomLabel.SHELF
    elif label == "SingleBed":
        return BedroomLabel.SINGLEBED
    elif label == "Sofa":
        return BedroomLabel.SOFA
    elif label == "Stool":
        return BedroomLabel.STOOL
    elif label == "Table":
        return BedroomLabel.TABLE
    elif label == "TVStand":
        return BedroomLabel.TVSTAND
    elif label == "Wardrobe":
        return BedroomLabel.WARDROBE
    else:
        print(f"## ATTENTION: object '{label}' is not supported for bedrooms! Using 'Shelf' instead ##")
        return BedroomLabel.SHELF
    
def get_living_room_label(label):
    if label == "Armchair":
        return LivingRoomLabel.ARMCHAIR
    elif label == "Bookshelf":
        return LivingRoomLabel.BOOOKSHELF
    elif label == "Cabinet":
        return LivingRoomLabel.CABINET
    elif label == "CeilingLamp":
        return LivingRoomLabel.CEILING_LAMP
    elif label == "ChaiseLongueSofa":
        return LivingRoomLabel.CHAISE_LONGUE_SOFA
    elif label == "ChineseChair":
        return LivingRoomLabel.CHINESE_CHAIR
    elif label == "CoffeeTable":
        return LivingRoomLabel.COFFEE_TABLE
    elif label == "ConsoleTable":
        return LivingRoomLabel.CONSOLE_TABLE
    elif label == "CornerSideTable":
        return LivingRoomLabel.CORNER_SIDE_TABLE
    elif label == "Desk":
        return LivingRoomLabel.DESK
    elif label == "DiningChair":
        return LivingRoomLabel.DINING_CHAIR
    elif label == "DiningTable":
        return LivingRoomLabel.DINING_TABLE
    elif label == "L-ShapedSofa":
        return LivingRoomLabel.L_SHAPED_SOFA
    elif label == "LazySofa":
        return LivingRoomLabel.LAZY_SOFA
    elif label == "LoungeChair":
        return LivingRoomLabel.LOUNGE_CHAIR
    elif label == "LoveseatSofa":
        return LivingRoomLabel.LOVESEAT_SOFA
    elif label == "Multi-SeatSofa":
        return LivingRoomLabel.MULTI_SEAT_SOFA
    elif label == "PendantLamp":
        return LivingRoomLabel.PENDANT_LAMP
    elif label == "RoundEndTable":
        return LivingRoomLabel.ROUND_END_TABLE
    elif label == "Shelf":
        return LivingRoomLabel.SHELF
    elif label == "Stool":
        return LivingRoomLabel.STOOL
    elif label == "TVStand":
        return LivingRoomLabel.TV_STAND
    elif label == "Wardrobe":
        return LivingRoomLabel.WARDROBE
    elif label == "WineCabinet":
        return LivingRoomLabel.WINE_CABINET
    else:
        print(f"## ATTENTION: object '{label}' is not supported for living room! Using 'Shelf' instead ##")
        return LivingRoomLabel.SHELF

def object_label_converter(room_type, label):
    if room_type == RoomType.BEDROOM:
        return get_bedroom_label(label)
    else:
        return get_living_room_label(label)

def triangulate_polygon(points):
    triangulator = Triangulator()

    vertex_indices = []
    for point in points:
        index = triangulator.add_vertex(point[0], point[1])  # Add the x, y coordinates
        vertex_indices.append(index)

    for i in range(len(points)):
        triangulator.add_polygon_vertex(vertex_indices[i])

    triangulator.triangulate()

    vertices = [Point2(triangulator.get_vertex(i).get_x(), triangulator.get_vertex(i).get_y())
                for i in range(triangulator.get_num_vertices())]

    faces = []
    for i in range(triangulator.get_num_triangles()):
        v0 = triangulator.get_triangle_v0(i)
        v1 = triangulator.get_triangle_v1(i)
        v2 = triangulator.get_triangle_v2(i)
        faces.append((v0, v1, v2))

    return vertices, faces

def calculate_triangles(corners):
    print(corners[:, 0])
    min0, max0 = min(corners[:, 0]), max(corners[:, 0])
    min1, max1 = min(corners[:, 1]), max(corners[:, 1])
    pcenter = [min0 + (max0 - min0)/2, min1 + (max1 - min1)/2]
    for i, c in enumerate(corners):
        corners[i] = c - pcenter

    vertices, faces = triangulate_polygon(corners)

    floor_plan_vertices = []
    for f in faces:
        for i in f:
            floor_plan_vertices.append([vertices[i][0], 0., vertices[i][1]])
    floor_plan_faces = []
    i = 0
    for f in faces:
        floor_plan_faces.append([0+i*3, 1+i*3, 2+i*3])
        i += 1
    return floor_plan_faces, floor_plan_vertices, pcenter

def prepare_boxes_file(room_type, objects, room_layout, num_objects, floor_plan_vertices, floor_plan_faces):
    # translations, sizes and angles
    translations = []
    sizes = []
    angles = []
    for i in range(num_objects):
        translations.append([0., 0., 0.])
        sizes.append([0., 0., 0.])
        angles.append([0.])

    # class labels
    class_labels = []
    for obj in objects:
        class_labels.append(int_to_one_hot(obj, room_type))

    # dictionary
    data = {}
    data["scene_id"] = 1
    data["class_labels"] = class_labels
    data["translations"] = translations
    data["sizes"] = sizes
    data["angles"] = angles
    data["uids"] = []
    data["jids"] = []
    data["scene_uid"] = []
    data["scene_type"] = []
    data["json_path"] = []
    data["room_layout"] = room_layout
    data["floor_plan_vertices"] = floor_plan_vertices
    data["floor_plan_faces"] = floor_plan_faces
    data["floor_plan_centroid"] = [0., 0., 0.]

    return data

def process_result(room_type, scale, offset):
    with open("/home/output/one-room/results.pkl", 'rb') as file:
        data = pickle.load(file)[0][1]

    object_list = []
    for i in range(len(data["class_labels"])):
        o = {}
        o["category"] = convert_label_backwards(room_type, data["class_labels"][i])
        o["angle"] = data["angles"][i][0]
        o["size"] = [data["sizes"][i][0]/scale*2, data["sizes"][i][2]/scale*2]
        o["position"] = [(data["translations"][i][0] + offset[0]) / scale, (data["translations"][i][2] + offset[1]) / scale]
        object_list.append(o)

    return object_list

def convert_label_backwards(room_type, label):
    if room_type == RoomType.LIVINGROOM:
        return get_label_from_living_room(np.where(label == 1.0)[0]+1)
    else:
        return get_label_from_bedroom(np.where(label == 1.0)[0]+1)

## DATATYPES ##

class RoomType(str, enum.Enum):
    BEDROOM = "Bedroom"
    LIVINGROOM = "Living"
    ORIGINAL = "original"

class BedroomLabel(int, enum.Enum):
    ARMCHAIR        = 1
    BOOKSHELF       = 2
    CABINET         = 3
    CEILINGLAMP     = 4
    CHAIR           = 5
    CHILDRENCABINET = 6
    COFFEETABLE     = 7
    DESK            = 8
    DOUBLEBED       = 9
    DRESSINGCHAIR   = 10
    DRESSINGTABLE   = 11
    KIDSBED         = 12
    NIGHTSTAND      = 13
    PENDANTLAMP     = 14
    SHELF           = 15
    SINGLEBED       = 16
    SOFA            = 17
    STOOL           = 18
    TABLE           = 19
    TVSTAND         = 20
    WARDROBE        = 21
    END             = 22

class LivingRoomLabel(int, enum.Enum):
    ARMCHAIR            = 1
    BOOOKSHELF          = 2
    CABINET             = 3
    CEILING_LAMP        = 4
    CHAISE_LONGUE_SOFA  = 5
    CHINESE_CHAIR       = 6
    COFFEE_TABLE        = 7
    CONSOLE_TABLE       = 8
    CORNER_SIDE_TABLE   = 9
    DESK                = 10
    DINING_CHAIR        = 11
    DINING_TABLE        = 12
    L_SHAPED_SOFA       = 13
    LAZY_SOFA           = 14
    LOUNGE_CHAIR        = 15
    LOVESEAT_SOFA       = 16
    MULTI_SEAT_SOFA     = 17
    PENDANT_LAMP        = 18
    ROUND_END_TABLE     = 19
    SHELF               = 20
    STOOL               = 21
    TV_STAND            = 22
    WARDROBE            = 23
    WINE_CABINET        = 24
    END                 = 25

# REQUIRED STRURCUTE
"""
/home/MiDiffusion/
/home/ThreedFront/
/home/
    - input/
        - bedroom-weights/
            - config.yaml
            - model.yaml
        - livingroom-weights/
            - config.yaml
            - model.yaml
        - one-room/
            custom_room-1/
            - dataset_stats_bedroom.txt
            - dataset_stats_livingroom.txt
        - one-room-weights/
    - output/
        - one-room/
    - interface.py
"""


# FILE PATHS

output_dir = "input/one-room/custom_room-1/"
output_file = output_dir + "boxes.npz"


# MAIN FUNCTIONALITY

def process_request(json_file):
    json_data = dict(json_file)
    #scale = json_data["floorplan"][0]["midiffscale"]

    seed = json_data["seed"]

    lscales = [1000000]
    bscales = [1000000]

    for i, room in enumerate(json_data["floorplan"][0]["rooms"]):
        room_type = room_type_converter(room["category"])
        corners = np.array(room["corners"])
        if room_type == RoomType.LIVINGROOM:
            lscales.append(calc_scale(corners, 8))
        elif room_type == RoomType.BEDROOM:
            bscales.append(calc_scale(corners, 5))

    lscale = min(lscales)
    bscale = min(bscales)

    for i, room in enumerate(json_data["floorplan"][0]["rooms"]):
        print(f'## Processing room {i} of {len(json_data["floorplan"][0]["rooms"])}')
        if not "objects" in room:
            continue
        if len(room["objects"]) == 0:
            continue

        # extract information from json
        room_type = room_type_converter(room["category"])

        # perform cleanup of directories
        if os.path.exists("input/one-room-weights/"):
            shutil.rmtree("input/one-room-weights/")

        # perform directory preperation
        if room_type == RoomType.LIVINGROOM:
            shutil.copy("input/one-room/dataset_stats_livingroom.txt", "input/one-room/dataset_stats.txt")
            #shutil.copy("input/threed_future_model_livingroom.pkl", "/home/ThreedFront/output/threed_future_model_one-room.pkl")
            shutil.copytree("input/livingroom-weights/", "input/one-room-weights/")
            room_side = 6.1
            scale = lscale
        elif room_type == RoomType.BEDROOM:
            shutil.copy("input/one-room/dataset_stats_bedroom.txt", "input/one-room/dataset_stats.txt")
            #shutil.copy("input/threed_future_model_bedroom.pkl", "/home/ThreedFront/output/threed_future_model_one-room.pkl")
            shutil.copytree("input/bedroom-weights/", "input/one-room-weights/")
            room_side = 3.1
            scale = bscale

        corners = np.array(room["corners"])
        corners = corners * scale
        objects = []
        for obj in room["objects"]:
            objects.append(object_label_converter(room_type, obj["category"]))

        # perform triangulation
        floor_plan_faces, floor_plan_vertices, offset = calculate_triangles(corners)

        # caluclate room layout and room_mask
        cached_room = CachedRoom(None, None, floor_plan_vertices, floor_plan_faces, [0., 0., 0.], None, None, None, None, None, None, None)
        scene_params = ORTHOGRAPHIC_PROJECTION_SCENE
        scene_params["room_side"] = room_side
        scene = scene_from_args(scene_params)
        room_layout = render_projection(scene, [get_floor_plan(cached_room)[0]], (1.0, 1.0, 1.0), "flat", output_dir + "room_mask.png")[:, :, 0:1]

        # get boxes file
        boxes_data = prepare_boxes_file(room_type, objects, room_layout, len(objects), floor_plan_vertices, floor_plan_faces)

        # save npz
        np.savez(output_file, **boxes_data)
        preprocess_floor_plan("input/one-room/", room_side, overwrite=True)
        shutil.copy("input/one-room/custom_room-1/room_mask.png", f"input/room-masks/room_mask_{i}.png")

        # copy original dataset_stats.txt
        if room_type == RoomType.LIVINGROOM:
            shutil.copy("input/one-room/dataset_stats_livingroom.txt", "input/one-room/dataset_stats.txt")
        else:
            shutil.copy("input/one-room/dataset_stats_bedroom.txt", "input/one-room/dataset_stats.txt")

        # execute MiDiffusion
        args = f"/home/input/one-room-weights/model.pt \
                --output_dir /home/output/ \
                --result_tag one-room \
                --n_syn_scenes 1 \
                --batch_size 1 \
                --experiment object_conditioned \
                --seed {seed}"
        os.system(f"python3 /home/MiDiffusion/scripts/generate_results.py {args}")

        # render scene (optional)
        #args = "/home/output/one-room/results.pkl \
        #        --output_directory /home/output/one-room/"
        #os.system(f"python3 /home/ThreedFront/scripts/render_results.py {args}")

        # process results
        object_list = process_result(room_type, scale, offset)
        json_data["floorplan"][0]["rooms"][i]["objects"] = object_list

    return json_data

