
# IMPORTS

import json, math
from pathlib import Path

# INPUT VARIABLES

dataset_directory = Path("2D-FRONT/json")
output_directory = "2D-FRONT-POPULATION-FORMAT"
seed = 1

# UTILS


def rectangle_to_transform(corners):
    top_left, top_right, bottom_right, bottom_left = corners
    center_x = (top_left[0] + top_right[0] + bottom_right[0] + bottom_left[0]) / 4
    center_y = (top_left[1] + top_right[1] + bottom_right[1] + bottom_left[1]) / 4
    width = math.sqrt((top_right[0] - top_left[0])**2 + (top_right[1] - top_left[1])**2)
    height = math.sqrt((bottom_left[0] - top_left[0])**2 + (bottom_left[1] - top_left[1])**2)
    delta_x = top_right[0] - top_left[0]
    delta_y = top_right[1] - top_left[1]
    rotation = math.atan2(delta_y, delta_x)
    return {
        "position": (center_x, center_y),
        "size": (width, height),
        "rotation": rotation
    }

THREED_FRONT_LIVINGROOM_FURNITURE = {
    "bookcase":                                "Bookshelf",
    "bookshelf":                               "Bookshelf",
    "jewelry armoire":                         "Bookshelf",
    "desk":                                    "Desk",
    "pendant lamp":                            "PendantLamp",
    "ceiling lamp":                            "CeilingLamp",
    "pendant light":                           "PendantLamp",
    "ceiling light":                           "CeilingLamp",
    "lounge chair":                            "LoungeChair",
    "cafe chair":                              "LoungeChair",
    "office chair":                            "LoungeChair",
    "dining chair":                            "DiningChair",
    "dining table":                            "DiningTable",
    "table":                                   "DiningTable",
    "corner":                                  "CornerSideTable",
    "side table":                              "CornerSideTable",
    "classic chinese chair":                   "ChineseChair",
    "chair":                                   "DiningChair",
    "armchair":                                "Armchair",
    "shelf":                                   "Shelf",
    "sideboard":                               "ConsoleTable",
    "side cabinet":                            "ConsoleTable",
    "console table":                           "ConsoleTable",
    "footstool":                               "Stool",
    "sofastool":                               "Stool",
    "bed end stool":                           "Stool",
    "stool":                                   "Stool",
    "barstool":                                "Stool",
    "round end table":                         "RoundEndTable",
    "loveseat sofa":                           "LoveseatSofa",
    "drawer chest":                            "Cabinet",
    "corner cabinet":                          "Cabinet",
    "cabinet":                                 "Cabinet",
    "wardrobe":                                "Wardrobe",
    "three-seat":                              "MultiSeatSofa",
    " multi-seat sofa":                        "MultiSeatSofa",
    "wine cabinet":                            "WineCabinet",
    "coffee table":                            "CoffeeTable",
    "coffee table - rectangular":              "CoffeeTable",
    "coffee table - round":                    "CoffeeTable",
    "lazy sofa":                               "LazySofa",
    "single seat sofa":                        "LazySofa",
    "children cabinet":                        "Cabinet",
    "chaise longue sofa":                      "ChaiseLongueSofa",
    "l-shaped sofa":                           "L-ShapedSofa",
    "sofa":                                    "Multi-SeatSofa",
    "tv stand":                                "TVStand",
    "media unit":                              "TVStand",
}

THREED_FRONT_BEDROOM_FURNITURE = {
    "desk":                                    "Desk",
    "nightstand":                              "Nightstand",
    "night table":                             "Nightstand",
    "king-size bed":                           "DoubleBed",
    "double bed":                              "DoubleBed",
    "single bed":                              "SingleBed",
    "kids bed":                                "KidsBed",
    "bed":                                     "DoubleBed",
    "ceiling lamp":                            "CeilingLamp",
    "pendant lamp":                            "PendantLamp",
    "pendant light":                           "PendantLamp",
    "ceiling light":                           "CeilingLamp",
    "bookshelf":                               "Bookshelf",
    "bookcase":                                "Bookshelf",
    "jewelry armoire":                         "Bookshelf",
    "tv stand":                                "TVStand",
    "media unit":                              "TVStand",
    "wardrobe":                                "Wardrobe",
    "lounge chair":                            "LoungeChair",
    "cafe chair":                              "LoungeChair",
    "office chair":                            "LoungeChair",
    "dining chair":                            "Chair",
    "classic chinese chair":                   "Chair",
    "chair":                                   "Chair",
    "armchair":                                "Armchair",
    "dressing table":                          "DressingTable",
    "dressing chair":                          "DressingChair",
    "corner":                                  "CornerSideTable",
    "side table":                              "CornerSideTable",
    "table":                                   "Table",
    "dining table":                            "Table",
    "round end table":                         "Table",
    "drawer chest":                            "Cabinet",
    "corner cabinet":                          "Cabinet",
    "sideboard":                               "Cabinet",
    "side cabinet":                            "Cabinet",
    "console table":                           "Cabinet",
    "cabinet":                                 "Cabinet",
    "children cabinet":                        "ChildrenCabinet",
    "shelf":                                   "Shelf",
    "footstool":                               "Stool",
    "sofastool":                               "Stool",
    "bed end stool":                           "Stool",
    "stool":                                   "Stool",
    "coffee table":                            "CoffeeTable",
    "loveseat sofa":                           "Sofa",
    "three-seat":                              "Sofa",
    " multi-seat sofa":                        "Sofa",
    "l-shaped sofa":                           "Sofa",
    "lazy sofa":                               "Sofa",
    "chaise longue sofa":                      "Sofa",
    "sofa":                                    "Sofa"
}

# PROCESSING

for index, file in enumerate(dataset_directory.iterdir()):
    if file.is_file() and file.suffix == ".json":
        with file.open("r", encoding="utf-8") as json_file:
            data = json.load(json_file)

            new_json = {}
            floorplans = []
            floorplan = {}
            rooms = []
            room = {}
            objects = []

            room["category"] = data["category"]
            room["corners"] = data["corners"]

            for obj in data["objects"]:
                new_object = {}
                translation = rectangle_to_transform(obj["corners"][0:4])
                if room["category"] == "Bedroom":
                    if obj["category_detailed"] in THREED_FRONT_BEDROOM_FURNITURE:
                        new_object["category"] = THREED_FRONT_BEDROOM_FURNITURE[obj["category_detailed"]]
                    elif obj["category"] in THREED_FRONT_BEDROOM_FURNITURE:
                        new_object["category"] = THREED_FRONT_BEDROOM_FURNITURE[obj["category"]]
                    else:
                        continue
                elif room["category"] == "Livingroom":
                    if obj["category_detailed"] in THREED_FRONT_LIVINGROOM_FURNITURE:
                        new_object["category"] = THREED_FRONT_LIVINGROOM_FURNITURE[obj["category_detailed"]]
                    elif obj["category"] in THREED_FRONT_LIVINGROOM_FURNITURE:
                        new_object["category"] = THREED_FRONT_LIVINGROOM_FURNITURE[obj["category"]]
                    else:
                        continue
                else:
                    continue
                new_object["position"] = translation["position"]
                new_object["size"] = translation["size"]
                new_object["angle"] = translation["rotation"]
                objects.append(new_object)
            
            room["objects"] = objects
            new_json["seed"] = seed
            rooms.append(room)
            floorplan["rooms"] = rooms
            floorplans.append(floorplan)
            new_json["floorplan"] = floorplans

            with open(f"{output_directory}/{file.name}", "w", encoding="utf-8") as new_json_file:
                new_json_file.write(json.dumps(new_json))