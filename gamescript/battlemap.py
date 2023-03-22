import threading

import pygame
import pygame.freetype
from random import randint, random, randrange
from PIL import Image, ImageFilter, ImageOps

from gamescript.common import utility

apply_sprite_colour = utility.apply_sprite_colour


class BaseMap(pygame.sprite.Sprite):
    terrain_list = None
    terrain_colour = None

    def __init__(self, main_dir):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self)
        self.main_dir = main_dir

        self.map_array = ()
        self.max_map_array = (0, 0)

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
    feature_list = None
    feature_colour = None

    def __init__(self, main_dir):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self)
        self.main_dir = main_dir

        self.map_array = ()
        self.max_map_array = (0, 0)

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
        self.map_array = tuple([[256 - col[2] for col in row] for row in pygame.surfarray.array3d(image).tolist()])
        if self.topology:
            self.topology_image = topology_map_creation(self.image, self.poster_level)

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
        height_index = self.map_array[int(new_pos[0])][int(new_pos[1])]

        return height_index

    def clear_image(self):
        self.image = None
        self.topology_image = None
        self.map_array = ()
        self.max_map_array = (0, 0)


class BeautifulMap(pygame.sprite.Sprite):
    texture_images = []
    empty_texture = None
    camp_texture = None
    load_texture_list = None
    main_dir = None
    battle_map_colour = None
    team_colour = None
    selected_team_colour = None

    def __init__(self, main_dir, screen_scale, height_map):
        self._layer = 0
        pygame.sprite.Sprite.__init__(self)
        self.main_dir = main_dir
        self.screen_scale = screen_scale
        self.height_map = height_map
        self.scale = 1
        self.mode = 0

        self.true_image = None  # image before adding effect and place name
        self.base_image = None  # image before adding height map mode
        self.image = None  # image after adding height map mode

    def draw_image(self, base_map, feature_map, place_name, camp_pos, battle):
        self.image = pygame.Surface((len(base_map.map_array[0]), len(base_map.map_array)))
        self.rect = self.image.get_rect(topleft=(0, 0))

        for row_pos in range(0, self.image.get_width()):  # recolour the map
            speed_array = []
            def_array = []
            for col_pos in range(0, self.image.get_height()):
                terrain, feature = feature_map.get_feature((row_pos, col_pos), base_map)
                new_colour = self.battle_map_colour[feature][1]
                rect = pygame.Rect(row_pos, col_pos, 1, 1)
                self.image.fill(new_colour, rect)

                map_feature_mod = feature_map.feature_mod[feature]
                speed_mod = int(map_feature_mod["Infantry Speed/Charge Effect"] * 100)
                def_mod = int(map_feature_mod["Infantry Defence Effect"] * 100)
                speed_array.append(speed_mod)
                def_array.append(def_mod)
            battle.map_move_array.append(speed_array)
            battle.map_def_array.append(def_array)

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

        for row_pos in range(0, len(base_map.map_array)):
            for col_pos in range(0, len(base_map.map_array[0])):
                if row_pos % 20 == 0 and col_pos % 20 == 0:
                    random_pos = (row_pos + randint(0, 19), col_pos + randint(0, 19))
                    terrain, this_feature = feature_map.get_feature(random_pos, base_map)
                    feature = self.texture_images[
                        self.load_texture_list.index(self.battle_map_colour[this_feature][0])]

                    choose = randint(0, len(feature) - 1)
                    if randint(0, 100) < feature_map.feature_mod[this_feature]["Texture Density"]:
                        this_texture = self.empty_texture  # empty texture
                    else:
                        this_texture = feature[choose]
                    rect = this_texture.get_rect(center=random_pos)
                    self.image.blit(this_texture, rect)

        for team, pos_list in camp_pos.items():
            for pos in pos_list:
                camp_texture = apply_sprite_colour(self.camp_texture.copy(), self.team_colour[team])
                self.image.blit(camp_texture, camp_texture.get_rect(center=pos[0]))
                pygame.draw.circle(self.image, self.team_colour[team], pos[0], pos[1], 10)

        size = (200 * self.screen_scale[0], 200 * self.screen_scale[1])  # default minimap size is 200 x 200
        self.mini_map_image = pygame.transform.smoothscale(self.image, (int(size[0]), int(size[1])))

        if place_name:
            self.image.blit(place_name, place_name.get_rect(topleft=(0, 0)))

        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width() * self.screen_scale[0] * 5,
                                                               self.image.get_height() * self.screen_scale[1] * 5))

        self.true_image = self.image.copy()

    def change_map_stuff(self, which, *args):
        if which == "effect":
            t1 = threading.Thread(target=self.add_effect, args=args, daemon=True)
            t1.start()
            t1.join()
        elif which == "mode":
            t1 = threading.Thread(target=self.change_mode, daemon=True)
            t1.start()
            t1.join()

    def add_effect(self, effect_image=None, time_image=None):
        self.base_image = self.true_image.copy()
        rect = self.base_image.get_rect(topleft=(0, 0))
        if effect_image:  # add weather filter effect
            self.base_image.blit(pygame.transform.smoothscale(effect_image,
                                                              (effect_image.get_width() * 5,
                                                               effect_image.get_height() * 5)), rect)

        if time_image:  # add day time effect
            self.base_image.blit(pygame.transform.smoothscale(time_image,
                                                              (time_image.get_width() * 5,
                                                               time_image.get_height() * 5)), rect)
        self.change_mode()

    def change_mode(self):
        """Switch between normal, height normal map, topology map mode"""
        self.image = self.base_image.copy()
        if self.mode == 1:  # with topology map
            rect = self.image.get_rect(topleft=(0, 0))
            self.image.blit(self.height_map.topology_image, rect)
        elif self.mode == 2:  # with height map
            rect = self.image.get_rect(topleft=(0, 0))
            self.image.blit(self.height_map.image, rect)

    def clear_image(self):
        self.image = None
        self.base_image = None
        self.true_image = None


def topology_map_creation(image, poster_level):
    data = pygame.image.tostring(image, "RGB")  # convert image to string data for filtering effect
    img = Image.frombytes("RGB", (image.get_width(), image.get_height()),
                          data)  # use PIL to get image data
    img = ImageOps.grayscale(img)  # grey scale the image
    img = img.filter(ImageFilter.GaussianBlur(radius=2))  # blur Image
    img = ImageOps.posterize(img, poster_level)  # posterise
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
    return pygame.image.fromstring(img, (image.get_width(), image.get_height()), "RGBA")  # convert to a pygame surface


# Random map creation

def random_matrix(matrix, max_random):
    for i in range(len(matrix)):
        for j in (range(len(matrix[i]))):
            matrix[i][j] = int(round(random() * max_random, 0))
    return matrix


def rrange(value_1, value_2):
    if value_1 == value_2:
        return value_1
    if value_1 - value_2 > 0:
        return randrange(value_2, value_1, 1)
    else:
        return randrange(value_1, value_2, 1)


def arm_horizontal(matrix):
    result = []
    temp = []
    for i in range(len(matrix)):
        for j in (range(len(matrix[i]) - 1)):
            temp.append(matrix[i][j])
            temp.append(int(rrange(int(matrix[i][j]), int(matrix[i][j + 1]))))
        temp.append(matrix[i][-1])
        result.append(temp)
        temp = []
    return result


def arm_vertical(matrix):
    result = []
    temp = []
    for i in range(len(matrix) - 1):
        result.append(matrix[i])
        for j in (range(len(matrix[i]))):
            temp.append(int(rrange(int(matrix[i][j]), int(matrix[i + 1][j]))))
        result.append(temp)
        temp = []
    result.append(matrix[-1])
    return result


def create_matrix(seed, rounds, max_value):
    r = random_matrix([[0] * seed for _ in range(seed)], max_value)
    for i in range(rounds):
        r = arm_horizontal(r)
        r = arm_vertical(r)
    return r


def create_random_map(terrain_list, feature_list, terrain_random, feature_random, height_random, map_size=(1000, 1000)):
    terrain = create_matrix(terrain_random, 5, (len(terrain_list) - 1) * 10)
    terrain = matrix_to_map(terrain, False, map_size, colour_list=terrain_list)
    feature = create_matrix(feature_random, 5, (len(feature_list) - 1) * 10)
    feature = matrix_to_map(feature, False, map_size, colour_list=feature_list)
    height = create_matrix(height_random, 5, 200)
    height = matrix_to_map(height, True, map_size)
    return terrain, feature, height


def matrix_to_map(matrix, alpha, map_size, colour_list=None):
    if alpha:
        map_image = pygame.Surface((len(matrix[0]), len(matrix)), pygame.SRCALPHA)
    else:
        map_image = pygame.Surface((len(matrix[0]), len(matrix)))
    k = pygame.Surface((1, 1), pygame.SRCALPHA)
    for y_index, y in enumerate(matrix):
        for x_index, x in enumerate(y):
            if alpha:  # only height map has alpha
                k.fill((255, x, x, 200))
            else:
                k.fill(colour_list[int(round(x, 0) / 10)])
            map_image.blit(k, k.get_rect(center=(x_index, y_index)))
    if alpha:
        return pygame.transform.smoothscale(map_image, map_size)
    else:
        return pygame.transform.scale(map_image, map_size)