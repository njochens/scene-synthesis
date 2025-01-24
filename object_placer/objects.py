import numpy as np
import tkinter as tk
from shapely.geometry import Polygon as spl_polygon
from random import randrange
from scipy.spatial import ConvexHull
import copy, os, json, math, random, gc

# Geometric

class Point:
    def __init__(self, x = 0, y = 0):
        self.x = float(x)
        self.y = float(y)

    def move_by(self, tx, ty):
        self.x = self.x + tx
        self.y = self.y + ty

    def resize(self, scale):
        self.x = self.x * scale
        self.y = self.y * scale

    def to_array(self):
        return [self.x, self.y]

    def same_as(self, p):
        if self.x == p.x and self.y == p.y:
            return True
        else:
            return False

    def to_str(self):
        return "x: " + "{: .3f}".format(self.x) + " y: " + "{: .3f}".format(self.y)

    def delete(self):
        del self

class Triangle:
    def __init__(self, p1 = Point(), p2 = Point(), p3 = Point()):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
    
    def move_by(self, tx, ty):
        self.p1.move_by(tx, ty)
        self.p2.move_by(tx, ty)
        self.p3.move_by(tx, ty)

    def resize(self, scale):
        self.p1.resize(scale)
        self.p2.resize(scale)
        self.p3.resize(scale)

    def same_as(self, t):
        if self.p1.same_as(t.p1) and self.p2.same_as(t.p2) and self.p3.same_as(t.p3):
            return True
        if self.p1.same_as(t.p1) and self.p2.same_as(t.p3) and self.p3.same_as(t.p2):
            return True
        if self.p1.same_as(t.p2) and self.p2.same_as(t.p3) and self.p3.same_as(t.p1):
            return True
        if self.p1.same_as(t.p2) and self.p2.same_as(t.p1) and self.p3.same_as(t.p3):
            return True
        if self.p1.same_as(t.p3) and self.p2.same_as(t.p1) and self.p3.same_as(t.p2):
            return True
        if self.p1.same_as(t.p3) and self.p2.same_as(t.p2) and self.p3.same_as(t.p1):
            return True
        return False

    def to_str(self):
        return "p1: " + self.p1.to_str() + " p2: " + self.p2.to_str() + " p3: " + self.p3.to_str()

    def to_svg_line(self, fill_color = "#FFFFFF", stroke_color = "black"):
        return f'<path d="M{self.p1.x},{self.p1.y} L{self.p2.x},{self.p2.y} L{self.p3.x},{self.p3.y} Z" fill="{fill_color}" fill-opacity="1" stroke="{stroke_color}" stroke-width="0" />'  

    def move_by(self, tx, ty):
        self.p1.move_by(tx, ty)
        self.p2.move_by(tx, ty)
        self.p3.move_by(tx, ty)

    def get_bbox(self):
        xmin = min(self.p1.x, self.p2.x, self.p3.x)
        xmax = max(self.p1.x, self.p2.x, self.p3.x)
        ymin = min(self.p1.y, self.p2.y, self.p3.y)
        ymax = max(self.p1.y, self.p2.y, self.p3.y)
        return [xmin, xmax, ymin, ymax]

    def draw(self, canvas, scale = 1, outline_color = "blue", fill_color="red"):
        canvas.create_polygon([self.p1.x * scale, self.p1.y * scale, self.p2.x * scale, self.p2.y * scale, self.p3.x * scale, self.p3.y * scale],
                            outline = outline_color,
                            fill = fill_color,
                            width=2)

    def delete(self):
        self.p1.delete()
        self.p2.delete()
        self.p3.delete()
        del self

class TriangleMesh:
    def __init__(self, triangles = []):
        self.triangles = triangles

    def move_by(self, tx, ty):
        for t in self.triangles:
            t.move_by(tx, ty)

    def resize(self, scale):
        for t in self.triangles:
            t.resize(scale)

    def from_list(self, corners):
        for i in range(int(len(corners) / (3 * 3))):
            p1 = Point(corners[i * 9 + 0], corners[i * 9 + 2])
            p2 = Point(corners[i * 9 + 3], corners[i * 9 + 5])
            p3 = Point(corners[i * 9 + 6], corners[i * 9 + 8])
            self.triangles.append(Triangle(p1,p2,p3))

    def to_svg_full(self, fill_color = "#FFFFFF", stroke_color = "black"):
        svg = []
        svg.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" baseProfile="full" width="256" height="256" viewBox="0 0 256 256">')
        svg.append(f'<rect x="0" y="0" width="256" height="256" fill="white" />')
        svg.append(self.to_svg_line(fill_color, stroke_color))
        svg.append("</svg>")
        single_line_svg = ""
        for l in svg:
            single_line_svg = single_line_svg + l + "\n"
        return single_line_svg.replace('"', "'")

    def to_svg_line(self, fill_color = "#FFFFFF", stroke_color = "black"):
        svg = []
        for t in self.triangles:
            svg.append(t.to_svg_line(fill_color, stroke_color))
        single_line_svg = ""
        for l in svg:
            single_line_svg = single_line_svg + l + "\n"
        return single_line_svg

    def get_bbox(self):
        xmin = []
        xmax = []
        ymin = []
        ymax = []
        for t in self.triangles:
            bbox = t.get_bbox()
            xmin.append(bbox[0])
            xmax.append(bbox[1])
            ymin.append(bbox[2])
            ymax.append(bbox[3])
        xmin = min(xmin)
        xmax = max(xmax)
        ymin = min(ymin)
        ymax = max(ymax)
        return [xmin, xmax, ymin, ymax]

    def resize_and_pad(self, length):
        scale = 15
        self.resize(scale)
        bbox = self.get_bbox()
        width = bbox[1] - bbox[0]
        height = bbox[3] - bbox[2]
        self.move_by(length/2-width/2-bbox[0], length/2-height/2-bbox[2])
        return [length/2-width/2-bbox[0], length/2-height/2-bbox[2], scale]

    def draw(self, canvas, scale = 1, outline_color = "black", fill_color="blue"):
        for t in self.triangles:
            t.draw(canvas, scale, outline_color, fill_color)

    def delete(self):
        for t in self.triangles:
            t.delete()
        del self

# Placer

class Polygon:
    def __init__(self, corners = []):
        self.corners = np.empty((len(corners), 2))
        self.center = np.zeros(2)
        for i in range(len(corners)):
            self.corners[i] = np.matrix(corners[i])
            self.center = np.add(self.center, self.corners[i])
        if len(corners) != 0:
            self.center = self.center/len(corners)
        else:
            self.center = [0,0]
        self.rotation = 0
    
    def rotate(self, angle): # angle is between 0 and 360
        pi_angle = (angle/360) * 2 * math.pi
        rotation_matrix = np.matrix([[math.cos(pi_angle), -math.sin(pi_angle)],[math.sin(pi_angle),math.cos(pi_angle)]])

        vector = self.center
        self.move_to(0, 0)

        for i in range(len(self.corners)):
            self.corners[i] = np.matmul(rotation_matrix, self.corners[i])

        self.move_to(vector[0], vector[1])
        
        self.rotation = (self.rotation + angle) % 360

    def rotate_spot(self, angle):
        pi_angle = (angle/360) * 2 * math.pi
        rotation_matrix = np.matrix([[math.cos(pi_angle), -math.sin(pi_angle)],[math.sin(pi_angle),math.cos(pi_angle)]])
        for i in range(len(self.corners)):
            self.corners[i] = np.matmul(rotation_matrix, self.corners[i])
        self.rotation = self.rotation + angle
        self.center = np.matmul(rotation_matrix, self.center)
        self.center = self.center.tolist()[0]

    def move_by(self, tx, ty):
        for i in range(len(self.corners)):
            self.corners[i][0] = self.corners[i][0] + tx
            self.corners[i][1] = self.corners[i][1] + ty
        self.center = [self.center[0] + tx, self.center[1] + ty]

    def move_to(self, tx, ty):
        self.move_by(-self.center[0], -self.center[1])
        self.center = [0, 0]
        self.move_by(tx, ty)     
    
    def resize(self, scale):
        for i in range(len(self.corners)):
            self.corners[i] = np.multiply(self.corners[i], scale)
        self.center = np.multiply(self.center, scale)

    def contains(self, polygon):
        p1 = spl_polygon(self.corners.tolist())
        p2 = spl_polygon(polygon.corners.tolist())
        return(p1.contains(p2))

    def intersects(self, polygon):
        p1 = spl_polygon(self.corners.tolist())
        p2 = spl_polygon(polygon.corners.tolist())
        return(p1.intersects(p2))

    def from_json(self, json):
        self.corners = np.matrix(json.get("corners"))
        self.rotation = np.matrix(json.get("rotation"))
        self.center = np.zeros(2)
        for i in range(len(self.corners)):
            self.corners[i] = np.matrix(self.corners[i])
            self.center = np.add(self.center, self.corners[i])
        if len(self.corners) != 0:
            self.center = self.center/len(self.corners)
        else:
            self.center = [0,0]

    def to_json(self):
        json = {}
        json["corners"] = self.corners.tolist()
        json["rotation"] = self.rotation
        return json

    def to_svg_line(self, fill_color = "#FFFFFF", stroke_color = "black"):
        string = '<path d="M'
        for i in range(len(self.corners)):
            if i < len(self.corners) - 1:
                string = string + str(self.corners[i][0]) + "," + str(self.corners[i][1]) + " L"
            else:
                string = string + str(self.corners[i][0]) + "," + str(self.corners[i][1])
        return string + f' Z" fill="{fill_color}" fill-opacity="1" stroke="{stroke_color}" stroke-width="1" />'            

    def draw(self, canvas, scale = 1, outline_color = "black", fill_color = "blue"):
        canvas.create_polygon(np.multiply(self.corners, scale).flatten().tolist(),
                            outline = outline_color,
                            fill = fill_color,
                            width=0)

class Object(Polygon):
    def __init__(self, name = "", category = "", id = -1, corners = [], color = "#000000"):
        super().__init__(corners)
        self.name = name
        self.category = category
        self.id = id
        self.color = color

    def to_svg_line(self, fill_color = "#FFFFFF", stroke_color = "black"):
        string = '<path d="M'
        for i in range(len(self.corners)):
            if i < len(self.corners) - 1:
                string = string + str(self.corners[i][0]) + "," + str(self.corners[i][1]) + " L"
            else:
                string = string + str(self.corners[i][0]) + "," + str(self.corners[i][1])
        return string + f' Z" fill="{self.color}" fill-opacity="1" stroke="{self.color}" stroke-width="0" />'            

    def from_json(self, json):
        super.from_json(json)
        self.name = json.get("name")
        self.category = json.get("category")
        self.id = json.get("id")

    def to_json(self):
        json = super().to_json()
        json["name"] = self.name
        json["category"] = self.category
        json["id"] = self.id
        return json

class ObjectGroup():
    def __init__(self, objects):
        self.objects = objects
    
    def move_by(self, tx, ty):
        for o in self.objects:
            o.move_by(tx, ty)
    
    def move_to(self, tx, ty):
        center = self.get_center()
        for o in self.objects:
            o.move_by(-center[0],-center[1])
            o.move_by(tx, ty)
    
    def get_center(self):
        x_values = []
        y_values = []
        for o in self.objects:
            for c in o.corners:
                x_values.append(c[0])
                y_values.append(c[1])
        return [min(x_values)+(max(x_values)-min(x_values))/2,
                min(y_values)+(max(y_values)-min(y_values))/2]

    def rotate(self, angle):
        center = self.get_center()
        self.move_by(-center[0],-center[1])
        for o in self.objects:
            o.rotate_spot(angle)
        self.move_by(center[0],center[1])

    def resize(self, scale):
        for o in self.objects:
            o.resize(scale)   

class Door(Object):
    def __init__(self, name = "", category = "", id = -1, corners = []):
        super().__init__(name, category, id, corners)

class Room(Polygon):
    def __init__(self, name = "", category = "", id = -1, corners = []):
        super().__init__(corners)
        self.name = name
        self.category = category
        self.source_file = ""
        self.id = id
        self.objects = []
        self.doors = []
        self.extra = None

    def is_placeable(self, o):
        if self.contains(o):
            for oo in self.objects:
                if o.intersects(oo):
                    return False
            return True
        return False
    
    def place_objects_random(self, objects):
        for o in objects:
            self.place_object_random(o)

    def place_object_random(self, o):
        found_suitable_location = False
        bbox = spl_polygon(self.corners.tolist()).bounds
        while not found_suitable_location:
            rand_x = random.random()
            rand_y = random.random()
            rand_rot = random.random()
            x = bbox[0] + (bbox[2] - bbox[0]) * rand_x
            y = bbox[1] + (bbox[3] - bbox[1]) * rand_y
            o.move_to(x, y)
            o.rotate(rand_rot*360)
            if self.is_placeable(o):
                found_suitable_location = True
        self.objects.append(o)

    def move_by(self, tx, ty):
        super().move_by(tx, ty)
        for o in self.objects:
            o.move_by(tx, ty)
        for d in self.doors:
            d.move_by(tx, ty)

    def resize(self, scale):
        super().resize(scale)
        for o in self.objects:
            o.resize(scale)
        for d in self.doors:
            d.resize(scale)

    def from_json(self, json):
        super().from_json(json)
        self.name = json.get("name")
        self.category = json.get("category")
        self.id = json.get("id")
        
        if json.get("doors") != None:
            for d in json.get("doors"):
                door = Door()
                door.from_json(d)
                self.doors.append(door)

        if json.get("objects") != None:
            for o in json.get("objects"):
                oo = Object()
                oo.from_json(o)
                self.objects.append(oo)

    def to_json(self):
        json = {}
        json["sourcefile"] = self.source_file
        json["category"] = self.category
        json["name"] = self.name
        json["id"] = self.id
        json["rotation"] = self.rotation
        json["corners"] = self.corners.tolist()
        objects = []
        for o in self.objects:
            objects.append(o.to_json())
        json["objects"] = objects
        doors = []
        for d in self.doors:
            doors.append(d.to_json())
        json["doors"] = doors
        return json

    def to_svg_file(self, fill_color = "#FFFFFF", stroke_color = "black"):
        svg = []
        svg.append('<?xml version="1.0" encoding="UTF-8"?>')
        svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" baseProfile="full" width="256" height="256" viewBox="0 0 256 256">')
        svg.append(f'<rect x="0" y="0" width="256" height="256" fill="white" />')
        svg.append(self.to_svg_line("#FFFFFF", "#FFFFFF"))
        for obj in self.objects:
            svg.append(obj.to_svg_line(fill_color = "#AB00BB", stroke_color = "#AB00BB"))
        svg.append("</svg>")
        single_line_svg = ""
        for l in svg:
            single_line_svg = single_line_svg + l + "\n"
        return single_line_svg.replace('"', "'")

    def draw(self, canvas, scale):
        super().draw(canvas, scale, "black", "white")
        for o in self.objects:
            o.draw(canvas, scale, "blue", "blue")
        for d in self.doors:
            d.draw(canvas, scale, "white", "white")

# 3D-FRONT

class TDFRoom():
    def __init__(self, room, source_file):
        self.type = room.get("type")
        self.instanceid = room.get("instanceid")
        self.size = room.get("size")
        self.empty = room.get("empty")
        self.pos = room.get("pos")
        self.pos = room.get("rot")
        self.pos = room.get("scale")
        self.source_file = source_file
        self.corners = []
        self.furniture = []

    def set_corners(self, corners):
        self.corners = corners

    def add_tdffurniture(self, tdffurniture):
        self.furniture.append(tdffurniture)

    def to_room(self):
        room = Room(corners = self.corners)
        room.name = self.instanceid
        if "Living" in self.instanceid.split("-")[0]:
            room.category = "Livingroom"
        else:
            room.category = "Bedroom"
        room.id = self.instanceid.split("-")[1]
        room.source_file = self.source_file
        for tdffurniture in self.furniture:
            room.objects.append(tdffurniture.to_object())
        return room

class TDFFurniture():
    def __init__(self, furniture_entry, furniture):
        self.uid              = furniture_entry.get("uid")
        self.jid              = furniture_entry.get("jid")
        self.aid              = furniture_entry.get("aid")
        self.title            = furniture_entry.get("title")
        self.type             = furniture_entry.get("type")
        self.sourceCategoryId = furniture_entry.get("sourceCategoryId")
        self.valid            = furniture_entry.get("valid")
        self.size             = furniture_entry.get("bbox")
        self.pos              = [0, 0, 0]
        self.scale            = furniture.get("scale")
        self.ref              = furniture.get("ref")
        self.instanceid       = furniture.get("instanceid")
        self.category         = ""
        self.color            = ""
        if len(self.size) == 1:
            self.size = self.size[0]
        w = self.size[0]
        h = self.size[1]
        l = self.size[2]
        self.size = [w, l, h]
        self.rot = [[1,0,0],[0,1,0],[0,0,1]]
        self.corners = [[-self.size[0]/2, -self.size[1]/2, -self.size[2]/2],
                        [ self.size[0]/2, -self.size[1]/2, -self.size[2]/2],
                        [ self.size[0]/2,  self.size[1]/2, -self.size[2]/2],
                        [ self.size[0]/2,  self.size[1]/2,  self.size[2]/2],
                        [-self.size[0]/2,  self.size[1]/2,  self.size[2]/2],
                        [-self.size[0]/2, -self.size[1]/2,  self.size[2]/2],
                        [ self.size[0]/2, -self.size[1]/2,  self.size[2]/2],
                        [-self.size[0]/2,  self.size[1]/2, -self.size[2]/2]]
        rot = furniture.get("rot")
        self.move_to(furniture.get("pos")[0], furniture.get("pos")[1], furniture.get("pos")[2])
        self.rotate(rot[0], rot[1], rot[2], rot[3])

    def rotate(self, qx, qy, qz, qw):
        pos = self.pos
        self.move_to(0, 0, 0)
        m00 = 1 - 2*qy**2 - 2*qz**2
        m01 = 2*qx*qy - 2*qz*qw
        m02 = 2*qx*qz + 2*qy*qw
        m10 = 2*qx*qy + 2*qz*qw
        m11 = 1 - 2*qx**2 - 2*qz**2
        m12 = 2*qy*qz - 2*qx*qw
        m20 = 2*qx*qz - 2*qy*qw
        m21 = 2*qy*qz + 2*qx*qw
        m22 = 1 - 2*qx**2 - 2*qy**2
        for i in range(len(self.corners)):
            self.corners[i] = np.matmul([[m00,m01,m02],[m10,m11,m12],[m20,m21,m22]], self.corners[i]).tolist()
        self.rot = np.matmul(self.rot, [[m00,m01,m02],[m10,m11,m12],[m20,m21,m22]]).tolist()
        self.move_to(pos[0], pos[1], pos[2])

    def move_by(self, x, y, z):
        for i in range(len(self.corners)):
            self.corners[i] = np.add(self.corners[i],[x, y, z]).tolist()
        self.pos = np.add(self.pos,[x, y, z]).tolist()

    def move_to(self, x, y, z):
        self.move_by(-self.pos[0], -self.pos[1], -self.pos[2])
        self.move_by(x, y, z)

    def get_floor_projection(self):
        corners = []
        for c in self.corners:
            corners.append([c[0], c[2]])
        hull = ConvexHull(corners)
        points = []
        for i in hull.vertices:        
            points.append(corners[i])
        return points

    def get_level(self):
        z = []
        for c in self.corners:
            z.append(c[1])
        return min(z)

    def to_object(self):
        obj = Object(corners = self.get_floor_projection())
        obj.name = self.ref
        obj.category = self.category
        obj.color = self.color
        return obj