import ast
import csv
import os
import random

import pygame
import pygame.freetype
from PIL import Image, ImageFilter, ImageOps


class BaseMap(pygame.sprite.Sprite):
    def __init__(self, main_dir):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self)
        self.main_dir = main_dir

        self.map_array = ()
        self.max_map_array = (0, 0)
        self.terrain_colour = {}
        with open(os.path.join(self.main_dir, "data", "map", "terrain.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    for n, i in enumerate(row):
                        if i.isdigit():
                            row[n] = int(i)
                        elif "," in i:
                            row[n] = ast.literal_eval(i)
                    self.terrain_colour[row[0]] = row[1:]
        self.terrain_list = tuple(self.terrain_colour.keys())
        self.terrain_colour = tuple([value[0] for value in self.terrain_colour.values()])

    def draw_image(self, image):
        self.map_array = tuple([[tuple(col) for col in row] for row in pygame.surfarray.array3d(image).tolist()])
        self.max_map_array = (len(self.map_array[0]) - 1, len(self.map_array) - 1)

    def get_terrain(self, pos):
        """get the base terrain at that exact position, typically called in get_feature"""
        terrain = self.map_array[int(pos[0])][int(pos[1])]  # use already calculated pos from get_feature
        terrain_index = self.terrain_colour.index(terrain)
        return terrain_index

    def clear_image(self):
        self.map_array = ()
        self.max_map_array = (0, 0)


class FeatureMap(pygame.sprite.Sprite):
    main_dir = None
    feature_mod = None

    def __init__(self, main_dir):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self)
        self.main_dir = main_dir

        self.map_array = ()
        self.max_map_array = (0, 0)
        self.feature_colour = {}
        with open(os.path.join(self.main_dir, "data", "map", "feature.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    for n, i in enumerate(row):
                        if i.isdigit():
                            row[n] = int(i)
                        elif "," in i:
                            row[n] = ast.literal_eval(i)
                    self.feature_colour[row[0]] = row[1:]

        self.feature_list = tuple(self.feature_colour.keys())
        self.feature_colour = tuple([value[0] for value in self.feature_colour.values()])

    def draw_image(self, image):
        self.map_array = tuple([[tuple(col) for col in row] for row in pygame.surfarray.array3d(image).tolist()])
        self.max_map_array = (len(self.map_array[0]) - 1, len(self.map_array) - 1)

    def get_feature(self, pos, base_map):
        """get the terrain feature at that exact position"""
        new_pos = pygame.Vector2(pos)  # create new pos to avoid replacing input one
        if new_pos[0] < 0:
            new_pos[0] = 0
        elif new_pos[0] > self.max_map_array[0]:
            new_pos[0] = self.max_map_array[0]

        if new_pos[1] < 0:
            new_pos[1] = 0
        elif new_pos[1] > self.max_map_array[1]:
            new_pos[1] = self.max_map_array[1]

        terrain_index = base_map.get_terrain(new_pos)
        feature = self.map_array[int(new_pos[0])][int(new_pos[1])]  # get colour at pos to obtain the terrain type
        feature_index = self.feature_colour.index(feature)
        feature_index = (terrain_index * len(self.feature_colour)) + feature_index
        return terrain_index, feature_index

    def clear_image(self):
        self.map_array = ()
        self.max_map_array = (0, 0)


class HeightMap(pygame.sprite.Sprite):
    poster_level = 4

    def __init__(self):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self)
        self.topology = True
        self.map_array = ()
        self.max_map_array = (0, 0)
        self.topology_image = None

    def draw_image(self, image):
        self.image = image.copy()
        self.map_array = tuple([[col[2] for col in row] for row in pygame.surfarray.array3d(image).tolist()])
        if self.topology:
            data = pygame.image.tostring(self.image, "RGB")  # convert image to string data for filtering effect
            img = Image.frombytes("RGB", (self.image.get_width(), self.image.get_height()),
                                  data)  # use PIL to get image data
            img = ImageOps.grayscale(img)  # grey scale the image
            img = img.filter(ImageFilter.GaussianBlur(radius=2))  # blur Image
            img = ImageOps.posterize(img, self.poster_level)  # posterise
            img = img.filter(ImageFilter.FIND_EDGES)  # get edge
            # images = ImageOps.invert(images)  # invert
            # enhancer = ImageEnhance.Contrast(images)
            # images = enhancer.enhance(5)

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
            self.topology_image = pygame.image.fromstring(img, (self.image.get_width(), self.image.get_height()),
                                                          "RGBA")  # convert image back to a pygame surface

    def get_height(self, pos):
        """get the terrain height at that exact position"""
        new_pos = pygame.Vector2(pos)
        if new_pos[0] < 0:
            new_pos[0] = 0
        elif new_pos[0] > self.max_map_array[0]:
            new_pos[0] = self.max_map_array[0]

        if new_pos[1] < 0:
            new_pos[1] = 0
        elif new_pos[1] > self.max_map_array[1]:
            new_pos[1] = self.max_map_array[1]

        colour = self.map_array[int(new_pos[0])][int(new_pos[1])]

        if colour == 0:
            colour = 255
        height_index = 256 - colour  # get colour at pos to obtain the terrain type
        return height_index

    def clear_image(self):
        self.image = None
        self.topology_image = None
        self.map_array = ()
        self.max_map_array = (0, 0)


class BeautifulMap(pygame.sprite.Sprite):
    texture_images = []
    empty_texture = None
    load_texture_list = None
    main_dir = None

    def __init__(self, main_dir, screen_scale):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self)
        self.main_dir = main_dir
        self.screen_scale = screen_scale
        self.scale = 1
        self.mode = 0
        self.battle_map_colour = {}
        with open(os.path.join(self.main_dir, "data", "map", "colourchange.csv"), encoding="utf-8",
                  mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row_index, row in enumerate(rd):
                if row_index > 0:
                    for n, i in enumerate(row):
                        if i.isdigit():
                            row[n] = int(i)
                        elif "," in i:
                            row[n] = ast.literal_eval(i)
                    self.battle_map_colour[row[0]] = row[1:]

    def draw_image(self, base_map, feature_map, height_map, place_name, battle, editor_map):
        self.image = pygame.Surface((len(base_map.map_array[0]), len(base_map.map_array)))
        self.rect = self.image.get_rect(topleft=(0, 0))

        if editor_map:
            terrain, feature = feature_map.get_feature((1, 1), base_map)
            new_colour = self.battle_map_colour[feature][1]
            self.image.fill(new_colour)
            map_feature_mod = feature_map.feature_mod[feature]
            speed_mod = int(map_feature_mod["Infantry Speed/Charge Effect"] * 100)
            battle.map_move_array = [[speed_mod] * self.image.get_width()] * self.image.get_height()
        else:
            for row_pos in range(0, self.image.get_width()):  # recolour the map
                speed_array = []
                for col_pos in range(0, self.image.get_height()):
                    terrain, feature = feature_map.get_feature((row_pos, col_pos), base_map)
                    new_colour = self.battle_map_colour[feature][1]
                    rect = pygame.Rect(row_pos, col_pos, 1, 1)
                    self.image.fill(new_colour, rect)

                    map_feature_mod = feature_map.feature_mod[feature]
                    speed_mod = int(map_feature_mod["Infantry Speed/Charge Effect"] * 100)
                    # infcombatmod = int(map_feature_mod[3] * 100)
                    # cavcombatmod = int(map_feature_mod[6] * 100)
                    speed_array.append(speed_mod)
                battle.map_move_array.append(speed_array)

        # Blur map to make it look older
        data = pygame.image.tostring(self.image, "RGB")  # convert image to string data for filtering effect
        img = Image.frombytes("RGB", (self.image.get_width(), self.image.get_height()),
                              data)  # use PIL to get image data
        img = img.filter(ImageFilter.GaussianBlur(radius=2))  # blur Image (or apply other filter in future)
        img = img.tobytes()
        img = pygame.image.fromstring(img, (self.image.get_width(), self.image.get_height()),
                                      "RGB")  # convert image back to a pygame surface
        self.image = pygame.Surface(
            (self.image.get_width(),
             self.image.get_height()))  # using the above surface cause a lot of fps drop so make a new one and blit the above here
        rect = self.image.get_rect(topleft=(0, 0))
        self.image.blit(img, rect)

        # Put in terrain feature texture
        if editor_map is False:
            for row_pos in range(0, len(base_map.map_array)):
                for col_pos in range(0, len(base_map.map_array[0])):
                    if row_pos % 20 == 0 and col_pos % 20 == 0:
                        random_pos = (row_pos + random.randint(0, 19), col_pos + random.randint(0, 19))
                        terrain, this_feature = feature_map.get_feature(random_pos, base_map)
                        feature = self.texture_images[
                            self.load_texture_list.index(self.battle_map_colour[this_feature][0])]
                        choose = random.randint(0, len(feature) - 1)
                        if this_feature - (terrain * 12) in (0, 1, 4, 5, 7) and \
                                random.randint(0, 100) < 60:  # reduce special texture in empty terrain like glassland
                            this_texture = self.empty_texture  # empty texture
                        else:
                            this_texture = feature[choose]
                        rect = this_texture.get_rect(center=random_pos)
                        self.image.blit(this_texture, rect)

        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width() * self.screen_scale[0],
                                                               self.image.get_height() * self.screen_scale[1]))

        # Save place name image as variable
        if place_name is not None:
            place_name_map = pygame.transform.smoothscale(place_name, (self.image.get_size()))
        else:
            place_name_map = pygame.Surface((0, 0))

        rect = self.image.get_rect(topleft=(0, 0))
        self.image.blit(place_name_map, rect)  # add place_name layer to map

        self.true_image = self.image.copy()  # image before adding effect and place name

    def add_effect(self, effect_image=None, time_image=None):
        self.image = self.true_image.copy()
        rect = self.image.get_rect(topleft=(0, 0))
        if effect_image is not None:
            self.image.blit(effect_image, rect)  # add weather filter effect

        if time_image is not None:
            self.image.blit(time_image, rect)  # add day time effect

        self.base_image = self.image.copy()
        self.change_scale(self.scale)

    def change_mode(self, height_map, mode):
        """Switch between normal, height normal map, topology map mode"""
        self.mode = mode
        self.image = self.base_image.copy()
        if self.mode == 1:  # with topology map
            rect = self.image.get_rect(topleft=(0, 0))
            self.image.blit(height_map.topology_image, rect)
        elif self.mode == 2:  # with height map
            rect = self.image.get_rect(topleft=(0, 0))
            self.image.blit(height_map.image, rect)
        self.change_scale(self.scale)

    def change_scale(self, scale):
        """Change map scale based on current camera zoom"""
        self.scale = scale
        self.image = pygame.transform.smoothscale(self.image, (int(self.base_image.get_width() * self.scale),
                                                               int(self.base_image.get_height() * self.scale)))

    def clear_image(self):
        self.image = None
        self.true_image = None
