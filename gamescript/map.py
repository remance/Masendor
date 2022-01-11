import ast
import csv
import os
import random

import pygame
import pygame.freetype
from PIL import Image, ImageFilter, ImageOps

# Terrain base colour, change these when add new terrain
Temperate = (166, 255, 107, 255)
Tropical = (255, 199, 13, 255)
Volcanic = (255, 127, 39, 255)
Desert = (240, 229, 176, 255)
Arctic = (211, 211, 211, 255)
Blight = (163, 73, 164, 255)
Void = (255, 255, 255, 255)
Demonic = (237, 28, 36, 255)
Death = (127, 127, 127, 255)
ShallowWater = (153, 217, 235, 255)
DeepWater = (100, 110, 214, 255)
terrain_colour = (Temperate, Tropical, Volcanic, Desert, Arctic, Blight, Void, Demonic, Death, ShallowWater, DeepWater)
terrain_list = ("Temperate", "Tropical", "Volcanic", "Desert", "Arctic", "Blight", "Void", "Demonic", "Death", "ShallowWater", "DeepWater")

# Terrain Feature colour, change these when add new feature
Plain = (181, 230, 29, 255)
Barren = (255, 127, 39, 255)
PlantField = (167, 186, 139, 255)
Forest = (16, 84, 36, 255)
InlandWater = (133, 254, 239, 255)
Road = (130, 82, 55, 255)
UrbanBuilding = (147, 140, 136, 255)
Farm = (255, 242, 0, 255)
Pandemonium = (102, 92, 118, 255)
Mana = (101, 109, 214, 255)
Rot = (200, 191, 231, 255)
Wetground = (186, 184, 109, 255)
feature_colour = (Plain, Barren, PlantField, Forest, InlandWater, Road, UrbanBuilding, Farm, Pandemonium, Mana, Rot, Wetground)
feaure_list = ("Plain", "Barren", "PlantField", "Forest", "InlandWater", "Road", "UrbanBuilding", "Farm", "Pandemonium", "Mana", "Rot", "Wetground")

default_map_width = 1000  # map default size is 1000 x 1000
default_map_height = 1000

class BaseMap(pygame.sprite.Sprite):
    max_zoom = 10

    def __init__(self, scale):
        """image file of map should be at size 1000x1000 then it will be scaled in self"""
        self._layer = 0
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.scale = scale
        self.terrain_colour = terrain_colour
        self.terrain_list = terrain_list
        # self.image = pygame.surface((0,0))
        # self.rect = self.image.get_rect(topleft=(0, 0))

    def draw_image(self, image):
        self.image = image
        self.true_image = self.image.copy()
        scale_width = self.image.get_width()
        scale_height = self.image.get_height()
        self.dim = pygame.Vector2(scale_width, scale_height)
        self.image_original = self.image.copy()
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))

    def get_terrain(self, pos):
        """get the base terrain at that exact position"""
        if (0 <= pos[0] <= 999) and (0 <= pos[1] <= 999):
            terrain = self.true_image.get_at((int(pos[0]), int(pos[1])))  # get colour at pos to obtain the terrain type
            terrain_index = self.terrain_colour.index(terrain)
        else:  # for handle terrain checking that clipping off map
            new_pos = pos
            if new_pos[0] < 0:
                new_pos[0] = 0
            elif new_pos[0] > 999:
                new_pos[0] = 999

            if new_pos[1] < 0:
                new_pos[1] = 0
            elif new_pos[1] > 999:
                new_pos[1] = 999

            terrain = self.true_image.get_at((int(new_pos[0]), int(new_pos[1])))
            terrain_index = 0
        return terrain_index

    # def update(self, dt, pos, scale):


class FeatureMap(pygame.sprite.Sprite):
    max_zoom = 10
    main_dir = None
    feature_mod = None

    def __init__(self, scale):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self, self.containers)
        # self.image = pygame.surface((0,0))
        self.scale = scale
        self.feature_colour = feature_colour
        self.feature_list = feaure_list
        # self.rect = self.image.get_rect(topleft=(0, 0))

    def draw_image(self, image):
        self.image = image
        self.true_image = self.image.copy()
        scale_width = self.image.get_width()
        scale_height = self.image.get_height()
        self.dim = pygame.Vector2(scale_width, scale_height)
        self.image_original = self.image.copy()
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))

    def get_feature(self, pos, gamemap):
        """get the terrain feature at that exact position"""
        terrain_index = gamemap.get_terrain(pos)
        if (0 <= pos[0] <= 999) and (0 <= pos[1] <= 999):
            feature = self.true_image.get_at((int(pos[0]), int(pos[1])))  # get colour at pos to obtain the terrain type
            feature_index = None
            if feature in self.feature_colour:
                feature_index = self.feature_colour.index(feature)
                feature_index = (terrain_index * len(self.feature_list)) + feature_index
        else:
            new_pos = pos
            if new_pos[0] < 0:
                new_pos[0] = 0
            elif new_pos[0] > 999:
                new_pos[0] = 999

            if new_pos[1] < 0:
                new_pos[1] = 0
            elif new_pos[1] > 999:
                new_pos[1] = 999

            feature = self.true_image.get_at((int(new_pos[0]), int(new_pos[1])))  # get colour at pos to obtain the terrain type
            feature_index = None
            if feature in self.feature_colour:
                feature_index = self.feature_colour.index(feature)
                feature_index = (terrain_index * len(self.feature_list)) + feature_index
        return terrain_index, feature_index


class HeightMap(pygame.sprite.Sprite):
    max_zoom = 10
    poster_level = 4

    def __init__(self, scale):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.scale = scale
        self.topology = True
        # self.rect = self.image.get_rect(topleft=(0, 0))

    def draw_image(self, image):
        self.image = image
        self.true_image = self.image.copy()
        scale_width = self.image.get_width()
        scale_height = self.image.get_height()
        self.dim = pygame.Vector2(scale_width, scale_height)
        self.image_original = self.image.copy()
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        if self.topology:
            data = pygame.image.tostring(self.image.copy(), "RGB")  # convert image to string data for filtering effect
            img = Image.frombytes("RGB", (default_map_width, default_map_height), data)  # use PIL to get image data
            img = ImageOps.grayscale(img)  # grey scale the image
            img = img.filter(ImageFilter.GaussianBlur(radius=2))  # blur Image
            img = ImageOps.posterize(img, self.poster_level)  # posterise
            img = img.filter(ImageFilter.FIND_EDGES)  # get edge
            # img = ImageOps.invert(img)  # invert
            # enhancer = ImageEnhance.Contrast(img)
            # img = enhancer.enhance(5)

            # replace black background with transparent
            img = img.convert("RGBA")
            data = img.getdata()
            new_data = []
            for item in data:
                if item == (0, 0, 0, 255):
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            img.putdata(new_data)

            img = img.tobytes()
            self.topology_image = pygame.image.fromstring(img, (default_map_width, default_map_height),
                                                          "RGBA")  # convert image back to a pygame surface

    def get_height(self, pos):
        """get the terrain height at that exact position"""
        new_pos = pos
        if new_pos[0] < 0:
            new_pos[0] = 0
        elif new_pos[0] > 999:
            new_pos[0] = 999

        if new_pos[1] < 0:
            new_pos[1] = 0
        elif new_pos[1] > 999:
            new_pos[1] = 999

        colour = self.true_image.get_at((int(new_pos[0]), int(new_pos[1])))[2]

        if colour == 0:
            colour = 255
        height_index = 256 - colour  # get colour at pos to obtain the terrain type
        return height_index

class BeautifulMap(pygame.sprite.Sprite):
    texture_images = []
    empty_image = None
    load_texture_list = None
    main_dir = None

    def __init__(self, scale):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self, self.containers)
        # self.image = pygame.surface((0,0))
        self.scale = scale
        self.mode = 0
        self.new_colour_list = {}
        with open(os.path.join(self.main_dir, "data", "map", "colourchange.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                    elif "," in i:
                        row[n] = ast.literal_eval(i)
                self.new_colour_list[row[0]] = row[1:]

    def draw_image(self, base_map, feature_map, height_map, place_name, gamebattle, editor_map):

        self.image = feature_map.image.copy()
        self.rect = self.image.get_rect(topleft=(0, 0))

        gamebattle.map_move_array = []  # array for pathfinding
        gamebattle.map_def_array = []

        if editor_map:
            terrain, feature = feature_map.get_feature((1, 1), base_map)
            new_colour = self.new_colour_list[feature][1]
            self.image.fill(new_colour)
            map_feature_mod = feature_map.feature_mod[feature]
            speed_mod = int(map_feature_mod[2] * 100)
            gamebattle.map_move_array = [[speed_mod] * default_map_width] * default_map_height
        else:
            for row_pos in range(0, default_map_width):  # recolour the map
                speed_array = []
                for col_pos in range(0, default_map_height):
                    terrain, feature = feature_map.get_feature((row_pos, col_pos), base_map)
                    new_colour = self.new_colour_list[feature][1]
                    rect = pygame.Rect(row_pos, col_pos, 1, 1)
                    self.image.fill(new_colour, rect)

                    map_feature_mod = feature_map.feature_mod[feature]
                    speed_mod = int(map_feature_mod[2] * 100)
                    # infcombatmod = int(map_feature_mod[3] * 100)
                    # cavcombatmod = int(map_feature_mod[6] * 100)
                    speed_array.append(speed_mod)
                gamebattle.map_move_array.append(speed_array)

        # v Comment out this part and import PIL above if not want to use blur filtering
        data = pygame.image.tostring(self.image, "RGB")  # convert image to string data for filtering effect
        img = Image.frombytes("RGB", (default_map_width, default_map_height), data)  # use PIL to get image data
        img = img.filter(ImageFilter.GaussianBlur(radius=2))  # blur Image (or apply other filter in future)
        img = img.tobytes()
        img = pygame.image.fromstring(img, (default_map_width, default_map_height), "RGB")  # convert image back to a pygame surface
        self.image = pygame.Surface(
            (default_map_width, default_map_height))  # for unknown reason using the above surface cause a lot of fps drop so make a new one and blit the above here
        rect = self.image.get_rect(topleft=(0, 0))
        self.image.blit(img, rect)
        # ^ PIL module code

        # v Put in terrain feature texture
        if editor_map is False:
            for row_pos in range(0, 991):
                for col_pos in range(0, 991):
                    if row_pos % 20 == 0 and col_pos % 20 == 0:
                        random_pos = (row_pos + random.randint(0, 19), col_pos + random.randint(0, 19))
                        terrain, this_feature = feature_map.get_feature(random_pos, base_map)
                        feature = self.texture_images[self.load_texture_list.index(self.new_colour_list[this_feature][0].replace(" ", "").lower())]
                        choose = random.randint(0, len(feature) - 1)
                        if this_feature - (terrain * 12) in (0, 1, 4, 5, 7) and \
                                random.randint(0, 100) < 60:  # reduce special texture in empty terrain like glassland
                            this_texture = self.empty_image  # empty texture
                        else:
                            this_texture = feature[choose]
                        rect = this_texture.get_rect(center=random_pos)
                        self.image.blit(this_texture, rect)
        # ^ End terrain feature

        self.true_image = self.image.copy()  # image before adding effect and place name
        scale_width = self.image.get_width()
        scale_height = self.image.get_height()
        self.dim = pygame.Vector2(scale_width, scale_height)

        self.place_name = place_name  # save place name image as variable

        self.add_effect(height_map)

    def add_effect(self, height_map, effect_image=None):
        rect = self.image.get_rect(topleft=(0, 0))
        self.image = self.true_image.copy()

        if effect_image is not None:
            self.image.blit(effect_image, rect)  # add special filter effect that make it look like old map

        if self.place_name is not None:
            self.image.blit(self.place_name, rect)  # add place_name layer to map

        self.image_original = self.image.copy()
        self.image_height_original = self.image.copy()
        self.image_height_original.blit(height_map.image, rect)
        self.image_topology_original = self.image.copy()
        self.image_topology_original.blit(height_map.topology_image, rect)
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))

    def change_mode(self, mode):
        """Switch between normal, height normal map, topology map mode"""
        self.mode = mode
        print(self.mode)
        self.change_scale(self.scale)

    def change_scale(self, scale):
        """Change map scale based on current camera zoom"""
        self.scale = scale
        scale_width = self.image_original.get_width() * self.scale
        scale_height = self.image_original.get_height() * self.scale
        self.dim = pygame.Vector2(scale_width, scale_height)
        if self.mode == 0:  # no height map
            self.image = self.image_original.copy()
        elif self.mode == 1:  # with topology map
            self.image = self.image_topology_original.copy()
        elif self.mode == 2:  # with height map
            self.image = self.image_height_original.copy()
        self.image = pygame.transform.scale(self.image, (int(self.dim[0]), int(self.dim[1])))

