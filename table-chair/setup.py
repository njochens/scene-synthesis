
# IMPORTS

import subprocess, copy, os, random, csv, sys
from pathlib import Path
from PIL import Image
sys.path.append(os.path.abspath('../3D-FRONT_processing/'))
from utils import Room, Object, ObjectGroup


# Clean Folders
def clean_folder(folder):
    for item in folder.iterdir():
        if item.is_dir():
            clean_folder(item)
            item.rmdir()
        else:
            item.unlink()

folders_to_clean = ["clean","messy","test","train"]

for folder_path in folders_to_clean:
    folder = Path(folder_path)
    if folder.is_dir():
        clean_folder(folder)
        print(f"Cleaned and removed: {folder_path}")

# Sizes
room_size = 256
chair_size = 3
table_length = 10
table_width = 5

# Create Objects
chair1 = Object(name = "Chair1", color = "#00AA33", corners = [[0,0],[0,chair_size],[chair_size,chair_size],[chair_size,0]])
chair2 = Object(name = "Chair2", color = "#00AA33", corners = [[0,0],[0,chair_size],[chair_size,chair_size],[chair_size,0]])
chair3 = Object(name = "Chair3", color = "#00AA33", corners = [[0,0],[0,chair_size],[chair_size,chair_size],[chair_size,0]])
chair4 = Object(name = "Chair4", color = "#00AA33", corners = [[0,0],[0,chair_size],[chair_size,chair_size],[chair_size,0]])
table = Object(name = "Table", color = "#3D228B", corners = [[0,0],[0,table_length],[table_width,table_length],[table_width,0]])

# Arrange Objects
table.move_by(4,0)
chair1.move_by(0,1)
chair2.move_by(0,6)
chair3.move_by(10,1)
chair4.move_by(10,6)

# Create Object Group
table_group = ObjectGroup(objects = [table, chair1, chair2, chair3, chair4])
table_group.resize(2)

# Train and Test Index
train_index = 1
test_index = 1

test_array = []
test_array_messy = []
train_array = []
train_array_messy = []

for i in range(200):
    print(i)
# Create room
    room = Room(corners = [[0,0],[0,room_size],[room_size,room_size],[room_size,0]])
# Place object group at random
    found_position = False
    while not found_position:
        rand_x = random.random() * room_size
        rand_y = random.random() * room_size
        rand_angle = random.random() * 360
        table_group.move_to(rand_x, rand_y)
        table_group.rotate(rand_angle)
        found_position = True
        for o in table_group.objects:
            if not room.contains(o):
                found_position = False
        if not found_position:
            table_group.rotate(-rand_angle)
            table_group.move_by(-rand_x, -rand_y)
    room.objects = table_group.objects
# Copy room
    messy_room = copy.deepcopy(room)
# Place chairs random
    chairs = messy_room.objects[1:]
    messy_room.objects = [messy_room.objects[0]]
    for o in chairs:
        is_placeable = False
        while not is_placeable:
            rand_x = random.random() * room_size
            rand_y = random.random() * room_size
            rand_angle = random.random() * 360
            o.move_to(rand_x, rand_y)
            o.rotate(rand_angle)
            if messy_room.is_placeable(o):
                is_placeable = True
                messy_room.objects.append(o)


# Export both to svg
    clean_svg = room.to_svg_file()
    messy_svg = messy_room.to_svg_file()
    with open(f"clean/{i}.svg", "w", encoding="utf-8") as file:
        file.write(clean_svg)
    with open(f"messy/{i}.svg", "w", encoding="utf-8") as file:
        file.write(messy_svg)

# Export both to png
    _ = subprocess.run(["convert", f"clean/{i}.svg", "-alpha", "off", "-antialias", "on", f"clean/{i}.png"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    _ = subprocess.run(["convert", f"messy/{i}.svg", "-alpha", "off", "-antialias", "on", f"messy/{i}.png"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

# Combine
    combined = Image.new("RGB", (512, 256))
    combined.paste(Image.open(f"clean/{i}.png"), (0, 0))
    combined.paste(Image.open(f"messy/{i}.png"), (256, 0))

# Create raw room
    raw_room = [] 
    for o in room.objects:
        if o.name == "Table":
            raw_room.append(1)
            raw_room.append(o.center[0])
            raw_room.append(o.center[1])
            raw_room.append(10)
            raw_room.append(5)
            raw_room.append(o.rotation)
        else:
            raw_room.append(0)
            raw_room.append(o.center[0])
            raw_room.append(o.center[1])
            raw_room.append(3)
            raw_room.append(3)
            raw_room.append(o.rotation)

    raw_messy = []
    for o in messy_room.objects:
        if o.name == "Table":
            raw_messy.append(1)
            raw_messy.append(o.center[0])
            raw_messy.append(o.center[1])
            raw_messy.append(10)
            raw_messy.append(5)
            raw_messy.append(o.rotation)
        else:
            raw_messy.append(0)
            raw_messy.append(o.center[0])
            raw_messy.append(o.center[1])
            raw_messy.append(3)
            raw_messy.append(3)
            raw_messy.append(o.rotation)

# Create Test Train Split
    if random.random() > 0.1:
        combined.save(f"train/{train_index}.png")
        train_index += 1
        train_array.append(raw_room)
        train_array_messy.append(raw_messy)
    else:
        combined.save(f"test/{test_index}.png")
        test_index += 1
        test_array.append(raw_room)
        test_array_messy.append(raw_messy)


with open('train.csv', mode='w', newline='') as file:
    csv_writer = csv.writer(file)
    for row in train_array:
        csv_writer.writerow(row)
with open('train_messy.csv', mode='w', newline='') as file:
    csv_writer = csv.writer(file)
    for row in train_array_messy:
        csv_writer.writerow(row)
with open('test.csv', mode='w', newline='') as file:
    csv_writer = csv.writer(file)
    for row in test_array:
        csv_writer.writerow(row)
with open('test_messy.csv', mode='w', newline='') as file:
    csv_writer = csv.writer(file)
    for row in test_array_messy:
        csv_writer.writerow(row)