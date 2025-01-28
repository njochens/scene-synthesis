# IMPORTS

import json
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageColor
import numpy as np
from pathlib import Path

# UTILS

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import to_rgba


def draw_polygons_with_centering_and_colors(polygons, rooms, colors, alphas, 
                                            image_size=(500, 500), border=20, output_file="output.png"):
    


    # Get the main polygon and calculate its bounding box
    main_polygon = [item for sublist in rooms for item in sublist]
    main_x_coords, main_y_coords = zip(*main_polygon)
    main_x_min, main_x_max = min(main_x_coords), max(main_x_coords)
    main_y_min, main_y_max = min(main_y_coords), max(main_y_coords)

    # Determine the bounding box of the main polygon with the fixed border
    view_x_min = main_x_min
    view_x_max = main_x_max
    view_y_min = main_y_min
    view_y_max = main_y_max

    view_width = view_x_max - view_x_min
    view_height = view_y_max - view_y_min

    # Ensure that the main polygon with the border fits in the output image
    scale_x = (image_size[0] - 2 * border) / view_width
    scale_y = (image_size[1] - 2 * border) / view_height
    scale = min(scale_x, scale_y)  # Maintain aspect ratio

    # Adjust the center of the main polygon in the view
    if view_height < view_width:
        offset_x = border - (view_x_min * scale)
        offset_y = border - (view_y_min * scale) + (view_width - view_height) / 2 * scale
    else:
        offset_x = border - (view_x_min * scale) + (view_height - view_width) / 2 * scale
        offset_y = border - (view_y_min * scale) 

    # Create the plot with a white canvas
    fig, ax = plt.subplots(figsize=(image_size[0] / 100, image_size[1] / 100), dpi=100)
    ax.set_xlim(0, image_size[0])
    ax.set_ylim(0, image_size[1])

    # Set canvas background to white
    ax.set_facecolor("white")

    # Remove axis for better aesthetics
    ax.axis('off')

    # Helper function to scale and translate points
    def transform_point(point):
        x, y = point
        x = x * scale + offset_x
        y = y * scale + offset_y
        return x, y

    # Draw all polygons with corresponding colors and alpha values
    for i, polygon in enumerate(polygons):
        # Transform the polygon's points to fit within the image
        transformed_polygon = [transform_point(point) for point in polygon]

        # Get the corresponding color and alpha
        color = colors[i]
        alpha = alphas[i]  # Use the alpha directly for transparency

        # Create a Polygon patch with the given color and alpha (no border)
        poly = Polygon(transformed_polygon, closed=True, facecolor=to_rgba(color, alpha), edgecolor="none")
        ax.add_patch(poly)

    # Save the image
    plt.savefig(output_file, bbox_inches='tight', pad_inches=0, transparent=False)
    plt.close()
    print(f"Image saved to {output_file}")

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
def rotate_rectangle(translation, size, angle):
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
    return rotated_corners

# FUNCTIONS

def draw_floorplan(json, output, img_size = 500, padding = 40):

    polygons = []
    colors = []
    alphas = []
    rooms = []


    for room in json["floorplan"][0]["rooms"]:
        layout = room["corners"]
        polygons.append(layout)
        rooms.append(layout)
        alphas.append(1)
        if room["category"] == "Bedroom":
            colors.append("#777777")
        elif room["category"] == "Livingroom":
            colors.append("#777777")
        else:
            colors.append("#000000")

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
                
            for obj_category, translation, size, angle in zip(obj_categories, translations, sizes, angles):
                alphas.append(0.9)
                colors.append(get_color(room["category"], obj_category))
                if obj_category in ["CeilingLamp", "PendanLamp"]:
                    alphas.append(0.5)
                polygons.append(rotate_rectangle(translation, size, angle))

    draw_polygons_with_centering_and_colors(polygons, rooms, colors, alphas, image_size=(img_size, img_size), border=padding, output_file=output)

# VARIABLES
if __name__ == "__main__":
    mode = "file"
    output_directory = "."
    input_directory = Path("../population_midiffusion/examples")

    for index, file in enumerate(input_directory.iterdir()):
        if file.is_file() and file.suffix == ".json" and index < 1:
            with file.open("r", encoding="utf-8") as json_file:
                draw_floorplan(json.load(json_file), output_directory + "/" + file.stem + ".png", padding=40)