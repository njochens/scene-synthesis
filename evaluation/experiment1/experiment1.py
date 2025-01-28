import copy, json, os, sys

external_folder = os.path.relpath("..")
if external_folder not in sys.path:
    sys.path.append(external_folder)

from visualizier import draw_floorplan
from caller import send_post_request

# FLOOR PLAN

corners = [[0,0], [1,0], [1,1], [0,1]]

# BEDROOMS

doubleroom = ["DoubleBed", "Nightstand", "Nightstand", "Desk", "Chair", "Wardrobe"]
singleroom = ["SingleBed", "Nightstand", "TVStand", "Sofa", "CoffeeTable", "Wardrobe", "Bookshelf"]
girlsroom = ["SingleBed", "Nightstand", "Desk", "Chair", "DressingTable", "DressingChair", "Wardrobe"]
kidsroom = ["KidsBed", "ChildrenCabinet", "Armchair", "Bookshelf", "Shelf", "Stool"]

# LIVINGROOMS

simpleliving = ["DiningTable", "DiningChair", "DiningChair", "DiningChair", "DiningChair", "Multi-SeatSofa", "TVStand"]
extraliving = ["L-ShapedSofa", "LazySofa", "Bookshelf", "TVStand", "ConsoleTable", "DiningTable", "DiningChair", "DiningChair", "DiningChair", "DiningChair", "Cabinet"]

# VARIABLES

rooms = [["Bedroom", "doubleroom", doubleroom],
         ["Bedroom", "singleroom", singleroom],
         ["Bedroom", "girlsroom", girlsroom],
         ["Bedroom", "kidsroom", kidsroom],
         ["Livingroom", "simpleliving", simpleliving],
         ["Livingroom", "extraliving", extraliving]]

base_json =  {}
base_json["floorplan"] = []

mode = "file"
output_directory = "output"
address = "http://localhost"
port = 5002
endpoint = "/populate"

# GENERATE JSONS

input_jsons = []

for seed in range(1,11):
    for room in rooms:
        input_json = copy.deepcopy(base_json)
        input_json["seed"] = seed
        floorplan = {}
        rooms_array = []
        room_dict = {}
        objects = []
        for object_category in room[2]:
            new_object = {}
            new_object["category"] = object_category
            objects.append(new_object)
        room_dict["corners"] = corners
        room_dict["objects"] = objects
        room_dict["category"] = room[0]
        rooms_array.append(room_dict)
        floorplan["rooms"] = rooms_array
        input_json["name"] = room[1]
        input_json["category"] = room[0]
        input_json["floorplan"].append(floorplan)
        input_jsons.append(json.dumps(input_json))

# PROCESS JSONS

for input_json in input_jsons:
    response_json = send_post_request(address, port, endpoint, json.loads(input_json))
    response_json = response_json.replace("'", '"')
    input_json = json.loads(input_json)
    draw_floorplan(json.loads(response_json), f'{output_directory}/{input_json["category"]}-{input_json["name"]}-{input_json["seed"]}.png')
            
