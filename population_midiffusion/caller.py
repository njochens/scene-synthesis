import requests
import json
import numpy as np
import matplotlib.pyplot as plt

def get_color(room_type, object_category):
    if room_type == "Bedroom":
        if object_category in ["Armchair", "Chair", "DressingChair", "Stool"]:
            return "#cfe09b"
        if object_category in ["Bookshelf", "Cabinet", "ChildrenCabinet", "Shelf", "Wardrobe"]:
            return "#c693c2"
        if object_category in ["CoffeeTable", "Desk", "DressingTable", "Table", "Nightstand"]:
            return "#8baddc"
        if object_category in ["DoubleBed", "KidsBed", "SingleBed"]:
            return "#f39ca2"
        if object_category in ["CeilingLamp", "PendantLamp"]:
            return "#fff59b"
        if object_category in ["Sofa"]:
            return "#8b6b5b"
        if object_category in ["TVStand"]:
            return "#555555"
    if room_type == "Livingroom":
        if object_category in ["Armchair", "ChineseChair", "DiningChair", "LoungeChair", "Stool"]:
            return "#cfe09b"
        if object_category in ["Bookshelf", "Cabinet", "Shelf", "Wardrobe", "WineCabinet"]:
            return "#c693c2"
        if object_category in ["CoffeeTable", "ConsoleTable", "CornerSideTable", "Desk", "DiningTable", "RoundEndTable"]:
            return "#8baddc"
        if object_category in ["CeilingLamp", "PendantLamp"]:
            return "#fff59b"
        if object_category in ["L-ShapedSofa", "LazySofa", "LoveseatSofa", "Multi-SeatSofa"]:
            return "#8b6b5b"
        if object_category in ["TVStand"]:
            return "#555555"
    return "#ffffff"

# Function to rotate a point around a center
def rotate_point(point, angle, center):
    x, z = point
    cx, cz = center
    x -= cx
    z -= cz
    new_x = x * np.cos(angle) - z * np.sin(angle)
    new_z = x * np.sin(angle) + z * np.cos(angle)
    return new_x + cx, new_z + cz

# Function to draw a rotated rectangle
def draw_rotated_rectangle(ax, translation, size, angle, color='b', alpha=1):
    x, z = translation
    dx, dz = size
    center = (x, z)
    corners = [
        (x - dx / 2, z - dz / 2),
        (x + dx / 2, z - dz / 2),
        (x + dx / 2, z + dz / 2),
        (x - dx / 2, z + dz / 2)
    ]
    rotated_corners = [rotate_point(corner, angle, center) for corner in corners]
    polygon = plt.Polygon(rotated_corners, color=color, alpha=alpha)
    ax.add_patch(polygon)


def draw_floorplan(json):
    # Create a 2D plot
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlabel('X')
    ax.set_ylabel('Z')

    for room in json["floorplan"][0]["rooms"]:
        layout = room["corners"]
        if room["category"] == "Bedroom":
            color = "#777777"
        elif room["category"] == "Livingroom":
            color = "#666666"
        else:
            color = "#000000"
        polygon = plt.Polygon(layout, color=color, alpha=1)
        ax.add_patch(polygon)

        obj_categories = []
        translations = []
        sizes = []
        angles = []

        if "objects" in room:
            for obj in room["objects"]:
                obj_categories.append(obj["category"])
                translations.append(obj["position"])
                sizes.append(obj["size"])
                angles.append(obj["angle"])

            # Visualize the rectangles with rotation
            for obj_category, translation, size, angle in zip(obj_categories, translations, sizes, angles):
                alpha = 0.9
                if obj_category in ["CeilingLamp", "PendanLamp"]:
                    alpha = 0.5
                draw_rotated_rectangle(ax, translation, size, angle, color=get_color(room["category"], obj_category), alpha=alpha)

    # Set limits and aspect ratio
    ax.set_xlim(0, 250)
    ax.set_ylim(0, 250)
    ax.set_aspect('equal', 'box')


    plt.axis('off')
    plt.show()

def send_post_request(address, port, endpoint, payload):
    """
    Sends a POST request to the specified address and port with a JSON payload.

    :param address: The target address (e.g., 'http://example.com').
    :param port: The target port (e.g., 8080).
    :param endpoint: The API endpoint (e.g., '/api/data').
    :param payload: The JSON payload to send as a dictionary.
    :return: The JSON response from the server.
    """
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

if __name__ == "__main__":
    # Example usage
    address = "http://localhost"
    port = 5002
    endpoint = "/populate"
    payload = {
        "seed": 2,
        "floorplan": [
        {
            "rooms": [
                {
                    "category": "Bedroom",
                    "objects": [
                        {
                            "category": "DoubleBed"
                        },
                        {
                            "category": "Nightstand"
                        },
                        {
                            "category": "Nightstand"
                        },
                        {
                            "category": "Desk"
                        },
                        {
                            "category": "Chair"
                        }
                    ],
                    "corners": [
                        [
                            48,
                            128
                        ],
                        [
                            48,
                            207
                        ],
                        [
                            75,
                            207
                        ],
                        [
                            75,
                            128
                        ]
                    ]
                },
                {
                    "corners": [
                        [
                            72,
                            48
                        ],
                        [
                            72,
                            103
                        ],
                        [
                            71,
                            104
                        ],
                        [
                            60,
                            104
                        ],
                        [
                            60,
                            119
                        ],
                        [
                            75,
                            119
                        ],
                        [
                            76,
                            120
                        ],
                        [
                            76,
                            135
                        ],
                        [
                            151,
                            135
                        ],
                        [
                            151,
                            84
                        ],
                        [
                            152,
                            83
                        ],
                        [
                            155,
                            83
                        ],
                        [
                            155,
                            48
                        ]
                    ],
                    "category": "Livingroom",
                    "objects": [
                        {
                            "category": "TVStand"
                        },
                        {
                            "category": "L-ShapedSofa"
                        },
                        {
                            "category": "DiningTable"
                        },
                        {
                            "category": "DiningChair"
                        },
                        {
                            "category": "DiningChair"
                        },
                        {
                            "category": "DiningChair"
                        },
                        {
                            "category": "DiningChair"
                        },
                        {
                            "category": "Bookshelf"
                        }
                    ]
                },
                {
                    "category": "Bedroom",
                    "objects": [
                        {
                            "category": "DoubleBed"
                        },
                        {
                            "category": "Nightstand"
                        },
                        {
                            "category": "Nightstand"
                        },
                        {
                            "category": "Desk"
                        },
                        {
                            "category": "Chair"
                        }
                    ],
                    "corners": [
                        [
                            152,
                            84
                        ],
                        [
                            152,
                            135
                        ],
                        [
                            207,
                            135
                        ],
                        [
                            207,
                            84
                        ]
                    ],
                },
                {
                    "category": "Bedroom",
                    "objects": [
                        {
                            "category": "DoubleBed"
                        },
                        {
                            "category": "Nightstand"
                        },
                        {
                            "category": "Nightstand"
                        },
                        {
                            "category": "Desk"
                        },
                        {
                            "category": "Chair"
                        }
                    ],
                    "corners": [
                        [
                            104,
                            136
                        ],
                        [
                            104,
                            203
                        ],
                        [
                            155,
                            203
                        ],
                        [
                            155,
                            136
                        ]
                    ],
                },
                {
                    "category": "Kitchen",
                    "corners": [
                        [
                            76,
                            160
                        ],
                        [
                            76,
                            203
                        ],
                        [
                            103,
                            203
                        ],
                        [
                            103,
                            160
                        ]
                    ],
                },
                {
                    "category": "Hallway",
                    "corners": [
                        [
                            76,
                            136
                        ],
                        [
                            76,
                            159
                        ],
                        [
                            103,
                            159
                        ],
                        [
                            103,
                            136
                        ]
                    ]
                }
            ]
        }
    ]
}

    response_json = send_post_request(address, port, endpoint, payload)

    if response_json is not None:
        print("Response JSON:")
        response_json = response_json.replace("'", '"')
        print(response_json)
        draw_floorplan(json.loads(response_json))
    else:
        print("No valid JSON response received.")
