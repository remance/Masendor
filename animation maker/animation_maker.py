import csv
import math
import os
import random
import re
import sys
import time
from pathlib import Path

import pygame
from PIL import Image, ImageFilter, ImageEnhance

from script import colour, listpopup, pool

current_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = current_dir[:current_dir.rfind("\\") + 1]
sys.path.insert(1, main_dir)

from gamescript import datastat, menu, battleui  # keep here as it need to get sys path insert
from gamescript.common import utility

rotation_xy = utility.rotation_xy
load_image = utility.load_image
load_images = utility.load_images
load_base_button = utility.load_base_button
load_textures = utility.load_textures
stat_convert = datastat.stat_convert

apply_colour = colour.apply_colour
setup_list = listpopup.setup_list
list_scroll = listpopup.list_scroll
popup_list_open = listpopup.popup_list_open
read_anim_data = pool.read_anim_data
read_joint_data = pool.read_joint_data
anim_to_pool = pool.anim_to_pool
anim_save_pool = pool.anim_save_pool
anim_del_pool = pool.anim_del_pool

default_sprite_size = (200, 200)

screen_size = (1000, 1000)
screen_scale = (screen_size[0] / 1000, screen_size[1] / 1000)

pygame.init()
pen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Animation Maker")  # set the self name on program border/tab
pygame.mouse.set_visible(True)  # set mouse as visible

direction_list = ("front", "side", "back", "sideup", "sidedown")
max_person = 4
p_list = tuple(["p" + str(p) for p in range(1, max_person + 1)])
part_column_header = ["head", "eye", "mouth", "body", "r_arm_up", "r_arm_low", "r_hand", "l_arm_up",
                      "l_arm_low", "l_hand", "r_leg", "r_foot", "l_leg", "l_foot", "main_weapon", "sub_weapon"]
anim_column_header = ["Name"]
for p in range(1, max_person + 1):
    p_name = "p" + str(p) + "_"
    anim_column_header += [p_name + item for item in part_column_header]
anim_column_header += ["effect_1", "effect_2", "effect_3", "effect_4", "dmg_effect_1", "dmg_effect_2", "dmg_effect_3", "dmg_effect_4",
                       "special_1", "special_2", "special_3", "special_4", "special_5", "special_6", "special_7", "special_8", "special_9",
                       "special_10", "size", "frame_property", "animation_property"]  # For csv saving and accessing
frame_property_list = ["hold", "p1_turret", "p2_turret", "p3_turret", "p4_turret", "p1_fix_main_weapon", "p1_fix_sub_weapon",
                       "p2_fix_main_weapon", "p2_fix_sub_weapon", "p3_fix_main_weapon", "p3_fix_sub_weapon",
                       "p4_fix_main_weapon", "p4_fix_sub_weapon", "effect_blur_", "effect_contrast_", "effect_brightness_", "effect_fade_",
                       "effect_grey", "effect_colour_"]  # starting property list

anim_property_list = ["dmgsprite", "interuptrevert", "norestart"] + frame_property_list


# TODO: unique, lock?


def reload_animation(animation, char):
    """Reload animation frames"""
    frames = [pygame.transform.smoothscale(this_image, showroom.size) for this_image in char.animation_list if this_image is not None]
    if len(char.frame_list[current_frame]) > 1:  # has stuff to load
        for frame_index in range(0, 10):
            for prop in frame_property_select[frame_index] + anim_property_select:
                if "effect" in prop:
                    if "grey" in prop:  # not work with just convert L for some reason
                        width, height = frames[frame_index].get_size()
                        for x in range(width):
                            for y in range(height):
                                red, green, blue, alpha = frames[frame_index].get_at((x, y))
                                average = (red + green + blue) // 3
                                gs_color = (average, average, average, alpha)
                                frames[frame_index].set_at((x, y), gs_color)
                    data = pygame.image.tostring(frames[frame_index], "RGBA")  # convert image to string data for filtering effect
                    surface = Image.frombytes("RGBA", frames[frame_index].get_size(), data)  # use PIL to get image data
                    alpha = surface.split()[-1]  # save alpha
                    if "blur" in prop:
                        surface = surface.filter(
                            ImageFilter.GaussianBlur(radius=float(prop[prop.rfind("_") + 1:])))  # blur Image (or apply other filter in future)
                    if "contrast" in prop:
                        enhancer = ImageEnhance.Contrast(surface)
                        surface = enhancer.enhance(float(prop[prop.rfind("_") + 1:]))
                    if "brightness" in prop:
                        enhancer = ImageEnhance.Brightness(surface)
                        surface = enhancer.enhance(float(prop[prop.rfind("_") + 1:]))
                    if "fade" in prop:
                        empty = pygame.Surface(frames[frame_index].get_size(), pygame.SRCALPHA)
                        empty.fill((255, 255, 255, 255))
                        empty = pygame.image.tostring(empty, "RGBA")  # convert image to string data for filtering effect
                        empty = Image.frombytes("RGBA", frames[frame_index].get_size(), empty)  # use PIL to get image data
                        surface = Image.blend(surface, empty, alpha=float(prop[prop.rfind("_") + 1:]) / 10)
                    surface.putalpha(alpha)  # put back alpha
                    surface = surface.tobytes()
                    surface = pygame.image.fromstring(surface, frames[frame_index].get_size(), "RGBA")  # convert image back to a pygame surface
                    if "colour" in prop:
                        colour = prop[prop.rfind("_") + 1:]
                        colour = [int(this_colour) for this_colour in colour.split(".")]
                        surface = apply_colour(surface, colour)
                    frames[frame_index] = surface
            filmstrip_list[frame_index].add_strip(frames[frame_index])
    animation.reload(frames)
    armour_selector.change_name(char.armour[p_body_helper.ui_type + "_armour"])
    face = [char.bodypart_list[current_frame][p_body_helper.ui_type + "_eye"], char.bodypart_list[current_frame][p_body_helper.ui_type + "_mouth"]]
    head_text = ["Eye: ", "Mouth: "]
    for index, selector in enumerate([eye_selector, mouth_selector]):
        this_text = "Any"
        if face[index] not in (0, 1):
            this_text = face[index]
        selector.change_name(head_text[index] + str(this_text))
    for helper in helper_list:
        helper.stat1 = char.part_name_list[current_frame]
        helper.stat2 = char.animation_part_list[current_frame]
        if char.part_selected:  # not empty
            for part in char.part_selected:
                part = list(char.rect_part_list.keys())[part]
                helper.select_part((0, 0), True, False, part)
        else:
            helper.select_part(None, shift_press, False)


def property_to_pool_data(which):
    if which == "anim":
        for frame in model.frame_list:
            frame["animation_property"] = select_list
        if anim_prop_list_box.rect.collidepoint(mouse_pos):
            for direction in range(0, 5):
                for frame in range(0, len(current_pool[direction][animation_name])):
                    current_pool[direction][animation_name][frame]["animation_property"] = select_list
    elif which == "frame":
        model.frame_list[current_frame]["frame_property"] = select_list
        for direction in range(0, 5):
            current_pool[direction][animation_name][current_frame]["frame_property"] = select_list


def change_animation(new_name):
    global animation_name, current_frame, current_anim_row, current_frame_row, anim_property_select, frame_property_select
    current_frame = 0
    anim.show_frame = current_frame
    anim_prop_list_box.namelist = anim_property_list + ["Custom"]  # reset property list
    anim_property_select = []
    frame_prop_list_box.namelist = [frame_property_list + ["Custom"] for _ in range(10)]
    frame_property_select = [[] for _ in range(10)]
    current_anim_row = 0
    current_frame_row = 0
    model.read_animation(new_name)
    animation_name = new_name
    animation_selector.change_name(new_name)
    reload_animation(anim, model)
    anim_prop_list_box.scroll.change_image(new_row=0, row_size=len(anim_prop_list_box.namelist))
    frame_prop_list_box.scroll.change_image(new_row=0, row_size=len(frame_prop_list_box.namelist[current_frame]))


race_list = []
race_acro = []
with open(os.path.join(main_dir, "data", "troop", "troop_race.csv"), encoding="utf-8", mode="r") as edit_file:
    rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
    for row in rd:
        if "," in row[-2]:  # make str with , into list
            this_ruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
        else:
            this_ruleset = [row[-2]]

        for n, i in enumerate(row):
            if i.isdigit() or ("." in i and re.search("[a-zA-Z]", i) is None) or i == "inf":
                row[n] = float(i)
        race_list.append(row[1])
        race_acro.append(row[3])
edit_file.close()

race_list = race_list[2:]  # remove header and any race
race_acro = race_acro[2:]
race_accept = ["Human", "Horse"]  # for now accept only Human race

generic_animation_pool, part_name_header = read_anim_data(direction_list, "generic", anim_column_header)
skel_joint_list, weapon_joint_list = read_joint_data(direction_list, race_list, race_accept)

with open(os.path.join(main_dir, "data", "sprite", "generic", "skin_colour_rgb.csv"), encoding="utf-8",
          mode="r") as edit_file:
    rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
    rd = [row for row in rd]
    header = rd[0]
    skin_colour_list = {}
    int_column = ["red", "green", "blue"]  # value in list only
    int_column = [index for index, item in enumerate(header) if item in int_column]
    for row_index, row in enumerate(rd):
        if row_index > 0:
            for n, i in enumerate(row):
                row = stat_convert(row, n, i, int_column=int_column)
                key = row[0].split("/")[0]
            skin_colour_list[key] = row[1:]

gen_body_sprite_pool = {}
for race in race_list:
    if race in race_accept:
        gen_body_sprite_pool[race] = {}
        for direction in direction_list:
            gen_body_sprite_pool[race][direction] = {}
            part_folder = Path(os.path.join(main_dir, "data", "sprite", "generic", race, direction))
            subdirectories = [str(x).split("data\\")[1].split("\\") for x in part_folder.iterdir() if x.is_dir()]
            for folder in subdirectories:
                imgs = load_textures(main_dir, folder, scale=screen_scale)
                gen_body_sprite_pool[race][direction][folder[-1]] = imgs

gen_armour_sprite_pool = {}
for race in race_list:
    gen_armour_sprite_pool[race] = {}
    for direction in direction_list:
        try:
            part_subfolder = Path(os.path.join(main_dir, "data", "sprite", "generic", race, direction, "armour"))
            subdirectories = [str(x).split("data\\")[1].split("\\") for x in part_subfolder.iterdir() if x.is_dir()]
            for subfolder in subdirectories:
                part_subsubfolder = Path(os.path.join(main_dir, "data", "sprite", "generic", race, direction, "armour", subfolder[-1]))
                subsubdirectories = [str(x).split("data\\")[1].split("\\") for x in part_subsubfolder.iterdir() if x.is_dir()]
                if subfolder[-1] not in gen_armour_sprite_pool[race]:
                    gen_armour_sprite_pool[race][subfolder[-1]] = {}
                for subsubfolder in subsubdirectories:
                    if subsubfolder[-1] not in gen_armour_sprite_pool[race][subfolder[-1]]:
                        gen_armour_sprite_pool[race][subfolder[-1]][subsubfolder[-1]] = {}
                    gen_armour_sprite_pool[race][subfolder[-1]][subsubfolder[-1]][direction] = {}
                    body_subsubfolder = Path(
                        os.path.join(main_dir, "data", "sprite", "generic", race, direction, "armour", subfolder[-1], subsubfolder[-1]))
                    body_directories = [str(x).split("data\\")[1].split("\\") for x in body_subsubfolder.iterdir() if x.is_dir()]
                    for body_folder in body_directories:
                        imgs = load_textures(main_dir,
                                             ["sprite", "generic", race, direction, "armour", subfolder[-1], subsubfolder[-1], body_folder[-1]],
                                             scale=screen_scale)
                        gen_armour_sprite_pool[race][subfolder[-1]][subsubfolder[-1]][direction][body_folder[-1]] = imgs
        except FileNotFoundError:
            pass

gen_weapon_sprite_pool = {}
part_folder = Path(os.path.join(main_dir, "data", "sprite", "generic", "weapon"))
subdirectories = [str(x).split("data\\")[1].split("\\") for x in part_folder.iterdir() if x.is_dir()]
for folder in subdirectories:
    gen_weapon_sprite_pool[folder[-1]] = {}
    part_subfolder = Path(os.path.join(main_dir, "data", "sprite", "generic", "weapon", folder[-1]))
    subsubdirectories = [str(x).split("data\\")[1].split("\\") for x in part_subfolder.iterdir() if x.is_dir()]
    for subfolder in subsubdirectories:
        for direction in direction_list:
            imgs = load_textures(main_dir, ["sprite", "generic", "weapon", folder[-1], subfolder[-1], direction], scale=screen_scale)
            if direction not in gen_weapon_sprite_pool[folder[-1]]:
                gen_weapon_sprite_pool[folder[-1]][direction] = imgs
            else:
                gen_weapon_sprite_pool[folder[-1]][direction].update(imgs)

effect_sprite_pool = {}
part_folder = Path(os.path.join(main_dir, "data", "sprite", "effect"))
subdirectories = [str(x).split("data\\")[1].split("\\") for x in part_folder.iterdir() if x.is_dir()]
for folder in subdirectories:
    effect_sprite_pool[folder[-1]] = {}
    part_folder = Path(os.path.join(main_dir, "data", "sprite", "effect", folder[-1]))
    subsubdirectories = [str(x).split("data\\")[1].split("\\") for x in part_folder.iterdir() if x.is_dir()]
    for subfolder in subsubdirectories:
        imgs = load_textures(main_dir, subfolder, scale=screen_scale)
        effect_sprite_pool[folder[-1]][subfolder[-1]] = imgs


class Showroom(pygame.sprite.Sprite):
    def __init__(self, size):
        """White space for showing off sprite and animation"""
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.size = (int(size[0]), int(size[1]))
        self.image = pygame.Surface(self.size)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(screen_size[0] / 2, screen_size[1] / 2.2))
        self.grid = True

    def update(self, *args):
        self.image.fill((255, 255, 255))
        if self.grid:
            grid_width = self.image.get_width() / 10
            grid_height = self.image.get_height() / 10
            for loop in range(1, 10):
                pygame.draw.line(self.image, (0, 0, 0), (grid_width * loop, 0), (grid_width * loop, self.image.get_height()))
                pygame.draw.line(self.image, (0, 0, 0), (0, grid_height * loop), (self.image.get_width(), grid_height * loop))


class Filmstrip(pygame.sprite.Sprite):
    """animation sprite filmstrip, always no more than 10 per animation"""
    image_original = None

    def __init__(self, pos):
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.image = self.image_original.copy()  # original no sprite
        self.image_original2 = self.image_original.copy()  # after add sprite but before activate or deactivate
        self.image_original3 = self.image_original2.copy()  # before adding selected corner
        self.rect = self.image.get_rect(topleft=self.pos)
        self.image_scale = (self.image.get_width() / 100, self.image.get_height() / 120)
        self.blit_image = None
        self.strip_rect = None
        self.activate = False

    def update(self, *args):
        self.image = self.image_original3.copy()

    def selected(self, select=False):
        self.image = self.image_original3.copy()
        select_colour = (200, 100, 100)
        if self.activate:
            select_colour = (150, 200, 100)
        if select:
            pygame.draw.rect(self.image, select_colour, (0, 0, self.image.get_width(), self.image.get_height()), 15)

    def add_strip(self, image=None, change=True):
        if change:
            self.image = self.image_original.copy()
            if image is not None:
                self.blit_image = pygame.transform.scale(image.copy(), (int(100 * self.image_scale[0]), int(100 * self.image_scale[1])))
                self.strip_rect = self.blit_image.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
                self.image.blit(self.blit_image, self.strip_rect)
            self.image_original2 = self.image.copy()
        else:
            self.image = self.image_original2.copy()
        self.image_original3 = self.image_original2.copy()
        if self.activate is False:  # draw black corner and replace film dot
            pygame.draw.rect(self.image_original3, (0, 0, 0), (0, 0, self.image.get_width(), self.image.get_height()), 15)


class Button(pygame.sprite.Sprite):
    """Normal button"""

    def __init__(self, text, image, pos, font_size=20):
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(font_size * screen_scale[1]))
        self.image = image.copy()
        self.image_original = self.image.copy()
        self.text = text
        self.pos = pos
        text_surface = self.font.render(str(text), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(int(self.image.get_width() / 2), int(self.image.get_height() / 2)))
        self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(center=self.pos)

    def change_text(self, text):
        if text != self.text:
            self.image = self.image_original.copy()
            self.text = text
            text_surface = self.font.render(self.text.capitalize(), True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(int(self.image.get_width() / 2), int(self.image.get_height() / 2)))
            self.image.blit(text_surface, text_rect)
            self.rect = self.image.get_rect(center=self.pos)


class SwitchButton(pygame.sprite.Sprite):
    """Button that switch text/option"""

    def __init__(self, text_list, image, pos, font_size=20):
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(font_size * screen_scale[1]))
        self.pos = pos
        self.current_option = 0
        self.image_original = image
        self.image = self.image_original.copy()
        self.text_list = text_list
        self.change_text(self.text_list[self.current_option])
        self.rect = self.image.get_rect(center=self.pos)

    def change_option(self, option):
        if self.current_option != option:
            self.current_option = option
            self.image = self.image_original.copy()
            self.change_text(self.text_list[self.current_option])

    def change_text(self, text):
        text_surface = self.font.render(str(text), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(int(self.image.get_width() / 2), int(self.image.get_height() / 2)))
        self.image.blit(text_surface, text_rect)


class BodyHelper(pygame.sprite.Sprite):
    def __init__(self, size, pos, ui_type, part_images):
        self._layer = 6
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font_size = int(12 * screen_scale[1])
        self.font = pygame.font.SysFont("helvetica", self.font_size)
        self.size = size
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.image.fill((255, 255, 200))
        pygame.draw.rect(self.image, (100, 150, 150), (0, 0, self.image.get_width(), self.image.get_height()), 3)
        self.image_original = self.image.copy()  # for original before add part and click
        self.rect = self.image.get_rect(center=pos)
        self.ui_type = ui_type
        self.part_images_original = [image.copy() for image in part_images]
        if "p" in self.ui_type:
            self.box_font = pygame.font.SysFont("helvetica", int(22 * screen_scale[1]))
            empty_box = self.part_images_original[-1]
            self.part_images_original = self.part_images_original[:-1]
            for box_part in ("W1", "W2"):
                text_surface = self.box_font.render(box_part, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(empty_box.get_width() / 2, empty_box.get_height() / 2))
                new_box = empty_box.copy()
                new_box.blit(text_surface, text_rect)
                self.part_images_original.append(new_box)
        else:
            self.box_font = pygame.font.SysFont("helvetica", int(18 * screen_scale[1]))
            empty_box = self.part_images_original[0]
            self.part_images_original = self.part_images_original[:-1]
            for box_part in ("S1", "S2", "S3", "S4", "S5", "E1", "E2", "DE1", "DE2", "S6", "S7", "S8", "S9", "S10", "E3", "E4", "DE3", "DE4"):
                text_surface = self.box_font.render(box_part, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(empty_box.get_width() / 2, empty_box.get_height() / 2))
                new_box = empty_box.copy()
                new_box.blit(text_surface, text_rect)
                self.part_images_original.append(new_box)
        self.part_images = [image.copy() for image in self.part_images_original]
        self.part_selected = []
        self.stat1 = {}
        self.stat2 = {}
        if "p" in self.ui_type:
            self.change_p_type(self.ui_type)
        else:
            self.rect_part_list = {"special_1": None, "special_2": None, "special_3": None, "special_4": None, "special_5": None,
                                   "effect_1": None, "effect_2": None, "dmg_effect_1": None, "dmg_effect_2": None, "special_6": None,
                                   "special_7": None, "special_8": None, "special_9": None, "special_10": None,
                                   "effect_3": None, "effect_4": None, "dmg_effect_3": None, "dmg_effect_4": None}
            self.part_pos = {"special_1": (20, 15), "special_2": (20, 45), "special_3": (20, 75), "special_4": (20, 105), "special_5": (20, 135),
                             "effect_1": (20, 165), "effect_2": (20, 195), "dmg_effect_1": (20, 225), "dmg_effect_2": (20, 255),
                             "special_6": (225, 15), "special_7": (225, 45), "special_8": (225, 75), "special_9": (225, 105),
                             "special_10": (225, 135),
                             "effect_3": (225, 165), "effect_4": (225, 195), "dmg_effect_3": (225, 225), "dmg_effect_4": (225, 255)}

        for key, item in self.part_pos.items():
            self.part_pos[key] = (item[0] * screen_scale[0], item[1] * screen_scale[1])
        self.blit_part()

    def change_p_type(self, new_type, player_change=False):
        """For helper that can change person"""
        self.ui_type = new_type
        self.rect_part_list = {self.ui_type + "_head": None, self.ui_type + "_body": None, self.ui_type + "_r_arm_up": None,
                               self.ui_type + "_r_arm_low": None, self.ui_type + "_r_hand": None,
                               self.ui_type + "_l_arm_up": None, self.ui_type + "_l_arm_low": None, self.ui_type + "_l_hand": None,
                               self.ui_type + "_r_leg": None, self.ui_type + "_r_foot": None, self.ui_type + "_l_leg": None,
                               self.ui_type + "_l_foot": None, self.ui_type + "_main_weapon": None, self.ui_type + "_sub_weapon": None}
        self.part_pos = {self.ui_type + "_head": (225, 85), self.ui_type + "_body": (225, 148), self.ui_type + "_r_arm_up": (195, 126),
                         self.ui_type + "_r_arm_low": (195, 156), self.ui_type + "_r_hand": (195, 187), self.ui_type + "_l_arm_up": (255, 126),
                         self.ui_type + "_l_arm_low": (255, 156), self.ui_type + "_l_hand": (255, 187), self.ui_type + "_r_leg": (210, 216),
                         self.ui_type + "_r_foot": (210, 246), self.ui_type + "_l_leg": (240, 216), self.ui_type + "_l_foot": (240, 246),
                         self.ui_type + "_main_weapon": (205, 30), self.ui_type + "_sub_weapon": (245, 30)}
        if player_change:
            self.select_part(None, False, False)  # reset first
            for part in model.part_selected:  # blit selected part that is in helper
                if list(model.rect_part_list.keys())[part] in self.rect_part_list:
                    self.select_part(mouse_pos, True, False, list(model.rect_part_list.keys())[part])

    def blit_part(self):
        self.image = self.image_original.copy()
        for index, image in enumerate(self.part_images):
            this_key = list(self.part_pos.keys())[index]
            pos = self.part_pos[this_key]
            new_image = image.copy()
            if this_key in self.part_selected:  # highlight selected part
                new_image = apply_colour(new_image, (34, 177, 76))

            rect = new_image.get_rect(center=pos)
            self.image.blit(new_image, rect)
            self.rect_part_list[this_key] = rect

    def select_part(self, check_mouse_pos, shift_press, ctrl_press, specific_part=None):
        if specific_part is not None:
            if specific_part is False:
                self.part_selected = []
            elif specific_part in list(self.part_pos.keys()):
                if shift_press and specific_part not in self.part_selected:
                    self.part_selected.append(specific_part)
                elif ctrl_press and specific_part in self.part_selected:
                    self.part_selected.remove(specific_part)
                else:
                    self.part_selected = [specific_part]
            self.blit_part()
        else:
            click_any = False
            if check_mouse_pos is not None:
                for index, rect in enumerate(self.rect_part_list):
                    this_rect = self.rect_part_list[rect]
                    if this_rect is not None and this_rect.collidepoint(check_mouse_pos):
                        click_any = True
                        if shift_press:
                            if list(self.part_pos.keys())[index] not in self.part_selected:
                                self.part_selected.append(list(self.part_pos.keys())[index])
                        elif ctrl_press:
                            if list(self.part_pos.keys())[index] in self.part_selected:
                                self.part_selected.remove(list(self.part_pos.keys())[index])
                        else:
                            self.part_selected = [list(self.part_pos.keys())[index]]
                            break
            if check_mouse_pos is None or (click_any is False and (shift_press is False and ctrl_press is False)):  # click at empty space
                self.part_selected = []
            self.blit_part()
        self.add_stat()

    def add_stat(self):
        for index, part in enumerate(self.rect_part_list.keys()):
            if self.stat2 is not None and part in self.stat2 and self.stat1[part] is not None and self.stat2[part] is not None:
                stat = self.stat1[part] + self.stat2[part]
                if len(stat) > 3:
                    stat.pop(3)
                    stat.pop(3)

                if stat[0] in race_acro:
                    stat[0] = race_acro[race_list.index(stat[0])]
                new_change = ["S", "F", "B", "CU", "CD"]
                for index2, change in enumerate(["side", "front", "back", "sideup", "sidedown"]):
                    if stat[1] == index2:
                        stat[1] = new_change[index2]
                stat[2] = str(stat[2])
                if len(stat) > 3:
                    try:
                        stat[3] = str([[stat[3][0], stat[3][1]]])
                    except TypeError:
                        stat[3] = str([0, 0])
                    for index2, change in enumerate(["F", "FH", "FV", "FHV"]):
                        if stat[5] == index2:
                            stat[5] = change
                    stat[4] = str(round(stat[4], 1))
                    stat[6] = "L" + str(int(stat[6]))

                stat1 = stat[0:3]  # first line with name
                # stat1.append(stat[-1])
                stat1 = str(stat1).replace("'", "")
                stat1 = stat1[1:-1]
                stat2 = stat[3:]  # second line with stat
                stat2 = str(stat2).replace("'", "")
                stat2 = stat2[1:]

                text_colour = (0, 0, 0)
                if part in self.part_selected:  # green text for selected part
                    text_colour = (20, 90, 20)
                text_surface1 = self.font.render(stat1, True, text_colour)

                text_surface2 = self.font.render(stat2, True, text_colour)
                shift_x = 50 * screen_scale[0]
                if any(ext in part for ext in ("effect", "special")):
                    text_rect1 = text_surface1.get_rect(midleft=(self.part_pos[part][0] + shift_x, self.part_pos[part][1] - 10))
                    text_rect2 = text_surface2.get_rect(midleft=(self.part_pos[part][0] + shift_x, self.part_pos[part][1] - 10 + self.font_size + 2))
                elif "body" in part:
                    head_name = part[0:2] + "_head"
                    text_rect1 = text_surface1.get_rect(midleft=(self.part_pos[head_name][0] + shift_x, self.part_pos[head_name][1] - 5))
                    text_rect2 = text_surface2.get_rect(
                        midleft=(self.part_pos[head_name][0] + shift_x, self.part_pos[head_name][1] - 5 + self.font_size + 2))
                elif "head" in part:
                    text_rect1 = text_surface1.get_rect(midright=(self.part_pos[part][0] - shift_x, self.part_pos[part][1] - 10))
                    text_rect2 = text_surface2.get_rect(midright=(self.part_pos[part][0] - shift_x, self.part_pos[part][1] - 10 + self.font_size + 2))
                else:
                    shift_x = 14 * screen_scale[0]
                    if "weapon" in part:
                        shift_x = 26 * screen_scale[0]
                    if self.part_pos[part][0] > self.image.get_width() / 2:
                        text_rect1 = text_surface1.get_rect(midleft=(self.part_pos[part][0] + shift_x, self.part_pos[part][1] - 15))
                        text_rect2 = text_surface2.get_rect(
                            midleft=(self.part_pos[part][0] + shift_x, self.part_pos[part][1] - 15 + self.font_size + 2))
                    else:
                        text_rect1 = text_surface1.get_rect(midright=(self.part_pos[part][0] - shift_x, self.part_pos[part][1] - 15))
                        text_rect2 = text_surface2.get_rect(
                            midright=(self.part_pos[part][0] - shift_x, self.part_pos[part][1] - 15 + self.font_size + 2))
                self.image.blit(text_surface1, text_rect1)
                self.image.blit(text_surface2, text_rect2)
            # else:
            #     text_surface = self.font.render("None", 1, (0, 0, 0))
            #     text_rect = text_surface.get_rect(midleft=self.part_pos[part])
            #     self.image.blit(text_surface, text_rect)


class NameBox(pygame.sprite.Sprite):
    def __init__(self, size, pos):
        self._layer = 6
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font_size = int(24 * screen_scale[1])
        self.font = pygame.font.SysFont("helvetica", int(self.font_size * screen_scale[1]))
        self.size = size
        self.image = pygame.Surface(self.size)
        self.image.fill((182, 233, 242))
        pygame.draw.rect(self.image, (100, 200, 0), (0, 0, self.image.get_width(), self.image.get_height()), 2)
        self.image_original = self.image.copy()
        self.pos = pos
        self.rect = self.image.get_rect(midtop=self.pos)
        self.text = None

    def change_name(self, text):
        if text != self.text:
            self.image = self.image_original.copy()
            self.text = text
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(int(self.image.get_width() / 2), int(self.image.get_height() / 2)))
            self.image.blit(text_surface, text_rect)


class ColourWheel(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        self._layer = 30
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def get_colour(self):
        pos = mouse_pos[0] - self.rect.topleft[0], mouse_pos[1] - self.rect.topleft[1]
        colour = self.image.get_at(pos)  # get colour at pos
        return colour


class Model:
    def __init__(self):
        self.animation_list = []
        self.animation_part_list = []
        self.frame_list = [{}] * 10
        self.side = 1  # 0 = front, 1 = side, 2 = back, 3 = sideup, 4 = sidedown
        self.rect_part_list = {}
        self.all_part_list = {}
        for p in range(1, max_person + 1):
            self.rect_part_list = self.rect_part_list | {"p" + str(p) + "_head": None, "p" + str(p) + "_body": None, "p" + str(p) + "_r_arm_up": None,
                                                         "p" + str(p) + "_r_arm_low": None, "p" + str(p) + "_r_hand": None,
                                                         "p" + str(p) + "_l_arm_up": None, "p" + str(p) + "_l_arm_low": None,
                                                         "p" + str(p) + "_l_hand": None, "p" + str(p) + "_r_leg": None,
                                                         "p" + str(p) + "_r_foot": None, "p" + str(p) + "_l_leg": None,
                                                         "p" + str(p) + "_l_foot": None, "p" + str(p) + "_main_weapon": None,
                                                         "p" + str(p) + "_sub_weapon": None}
            self.all_part_list = self.all_part_list | {"p" + str(p) + "_head": None, "p" + str(p) + "_eye": 1, "p" + str(p) + "_mouth": 1,
                                                       "p" + str(p) + "_body": None, "p" + str(p) + "_r_arm_up": None,
                                                       "p" + str(p) + "_r_arm_low": None, "p" + str(p) + "_r_hand": None,
                                                       "p" + str(p) + "_l_arm_up": None, "p" + str(p) + "_l_arm_low": None,
                                                       "p" + str(p) + "_l_hand": None, "p" + str(p) + "_r_leg": None,
                                                       "p" + str(p) + "_r_foot": None, "p" + str(p) + "_l_leg": None,
                                                       "p" + str(p) + "_l_foot": None, "p" + str(p) + "_main_weapon": None,
                                                       "p" + str(p) + "_sub_weapon": None}
        self.rect_part_list = self.rect_part_list | {"effect_1": None, "effect_2": None, "effect_3": None, "effect_4": None,
                                                     "dmg_effect_1": None, "dmg_effect_2": None, "dmg_effect_3": None, "dmg_effect_4": None,
                                                     "special_1": None, "special_2": None, "special_3": None, "special_4": None, "special_5": None,
                                                     "special_6": None, "special_7": None, "special_8": None, "special_9": None, "special_10": None}
        self.all_part_list = self.all_part_list | {"effect_1": None, "effect_2": None, "effect_3": None, "effect_4": None,
                                                   "dmg_effect_1": None, "dmg_effect_2": None, "dmg_effect_3": None, "dmg_effect_4": None,
                                                   "special_1": None, "special_2": None, "special_3": None, "special_4": None, "special_5": None,
                                                   "special_6": None, "special_7": None, "special_8": None, "special_9": None, "special_10": None}
        self.p_eyebrow = {}
        self.p_any_eye = {}
        self.p_any_mouth = {}
        self.p_beard = {}
        self.part_selected = []
        self.p_race = {"p" + str(p): "Human" for p in range(1, max_person + 1)}
        skin = list(skin_colour_list.keys())[random.randint(0, len(skin_colour_list) - 1)]
        # skin_colour = skin_colour_list[skin]
        self.p_hair_colour = {"p" + str(p): [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)] for p in
                              range(1, max_person + 1)}
        self.p_eye_colour = {"p" + str(p): [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)] for p in range(1, max_person + 1)}
        self.weapon = {}
        self.armour = {}
        for p in range(1, max_person + 1):
            self.weapon = self.weapon | {"p" + str(p) + "_main_weapon": "Sword", "p" + str(p) + "_sub_weapon": "Sword"}
            self.armour = self.armour | {"p" + str(p) + "_armour": "None"}
        self.empty_sprite_part = [0, pygame.Vector2(0, 0), [50, 50], 0, 0, 0, 1]
        self.random_face()
        self.size = 1  # size scale of sprite
        try:
            self.read_animation(list(generic_animation_pool[0].keys())[0])
            self.default_sprite_part = {key: (value[:].copy() if value is not None else value) for key, value in self.animation_part_list[0].items()}
            self.default_body_part = {key: value for key, value in self.bodypart_list[0].items()}
            self.default_part_name = {key: value for key, value in self.part_name_list[0].items()}
        except IndexError:  # empty animation file
            self.read_animation(None)
            self.default_sprite_part = {key: None for key in self.rect_part_list.keys()}
            self.default_body_part = {key: value for key, value in self.all_part_list.items()}
            self.default_part_name = {key: None for key in self.rect_part_list.keys()}

    def random_face(self):
        for p in range(1, max_person + 1):
            this_p = "p" + str(p)
            self.p_eyebrow = self.p_eyebrow | {this_p: list(gen_body_sprite_pool[self.p_race[this_p]]["side"]["eyebrow"].keys())[
                random.randint(0, len(gen_body_sprite_pool[self.p_race[this_p]]["side"]["eyebrow"]) - 1)]}
            self.p_any_eye = self.p_any_eye | {this_p: list(gen_body_sprite_pool[self.p_race[this_p]]["side"]["eye"].keys())[
                random.randint(0, len(gen_body_sprite_pool[self.p_race[this_p]]["side"]["eye"]) - 1)]}
            self.p_any_mouth = self.p_any_mouth | {this_p: list(gen_body_sprite_pool[self.p_race[this_p]]["side"]["mouth"].keys())[
                random.randint(0, len(gen_body_sprite_pool[self.p_race[this_p]]["side"]["mouth"]) - 1)]}
            self.p_beard = self.p_beard | {this_p: list(gen_body_sprite_pool[self.p_race[this_p]]["side"]["beard"].keys())[
                random.randint(0, len(gen_body_sprite_pool[self.p_race[this_p]]["side"]["beard"]) - 1)]}

    def make_layer_list(self, sprite_part):
        pose_layer_list = {k: v[5] for k, v in sprite_part.items() if v is not None and v != []}
        pose_layer_list = dict(sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))
        return pose_layer_list

    def read_animation(self, name, old=False, new_size=True):
        global activate_list
        #  sprite animation generation from data
        self.animation_part_list = [{key: None for key in self.rect_part_list.keys()}] * 10
        self.animation_list = [self.create_animation_film(None, current_frame, empty=True)] * 10
        self.bodypart_list = [{key: value for key, value in self.all_part_list.items()}] * 10
        self.part_name_list = [{key: None for key in self.rect_part_list.keys()}] * 10
        for key, value in self.rect_part_list.items():  # reset rect list
            self.rect_part_list[key] = None
        for joint in joints:  # remove all joint first
            joint.kill()
        if name is not None:
            frame_list = current_pool[self.side][name].copy()
            if old:
                frame_list = self.frame_list
            while len(frame_list) < 10:  # add empty item
                frame_list.append({})
            if new_size:
                try:
                    self.size = frame_list[0]['size']  # use only the size from first frame, all frame should be same size
                except KeyError:
                    self.size = 1
                except TypeError:
                    if type(self.size) != float and self.size.isdigit() is False:
                        self.size = 1
                    else:
                        self.size = int(self.size)
            size_button.change_text("Size: " + str(self.size))
            for frame in frame_list:  # change frame size value
                frame['size'] = self.size
            for index, pose in enumerate(frame_list):
                sprite_part = {key: None for key in self.rect_part_list.keys()}
                link_list = {key: None for key in self.rect_part_list.keys()}
                bodypart_list = {key: value for key, value in self.all_part_list.items()}
                for part in pose:
                    if pose[part] != [0] and "property" not in part and part != "size":
                        if "eye" not in part and "mouth" not in part:
                            if "weapon" in part:
                                link_list[part] = [pose[part][2], pose[part][3]]
                                if pose[part][1] in gen_weapon_sprite_pool[self.weapon[part]][pose[part][0]]:
                                    bodypart_list[part] = [self.weapon[part], pose[part][0], pose[part][1]]
                                else:
                                    bodypart_list[part] = [self.weapon[part], pose[part][0], 0]
                            else:
                                link_list[part] = [pose[part][3], pose[part][4]]
                                bodypart_list[part] = [pose[part][0], pose[part][1], pose[part][2]]
                        elif pose[part] != 0:
                            bodypart_list[part] = pose[part]
                            part_name = pose[part]
                            if part_name == 1:
                                part_name = "Any"
                            if "mouth" in part:
                                mouth_selector.change_name("Mouth: " + part_name)
                            elif "eye" in part:
                                eye_selector.change_name("Eye: " + part_name)
                        else:
                            bodypart_list[part] = 1.0
                    elif "property" in part and pose[part] != [""]:
                        if "animation" in part:
                            for stuff in pose[part]:
                                if stuff not in anim_prop_list_box.namelist:
                                    anim_prop_list_box.namelist.insert(-1, stuff)
                                if stuff not in anim_property_select:
                                    anim_property_select.append(stuff)
                        elif "frame" in part and pose[part] != 0:
                            for stuff in pose[part]:
                                if stuff not in frame_prop_list_box.namelist[index]:
                                    frame_prop_list_box.namelist[index].insert(-1, stuff)
                                if stuff not in frame_property_select[index]:
                                    frame_property_select[index].append(stuff)
                self.bodypart_list[index] = bodypart_list
                main_joint_pos_list = self.generate_body(self.bodypart_list[index])
                part_name = {key: None for key in self.rect_part_list.keys()}

                except_list = ("eye", "mouth", "size")
                for part in part_name_header:
                    if part in pose and pose[part] != [0] and any(ext in part for ext in except_list) is False:
                        if "weapon" in part:
                            try:
                                sprite_part[part] = [self.sprite_image[part],
                                                     (self.sprite_image[part].get_width() / 2, self.sprite_image[part].get_height() / 2),
                                                     link_list[part], pose[part][4], pose[part][5], pose[part][6], pose[part][7]]
                                part_name[part] = [self.weapon[part], pose[part][0], pose[part][1]]
                            except AttributeError:  # return None, sprite not existed.
                                sprite_part[part] = [self.sprite_image[part], (0, 0),
                                                     link_list[part], pose[part][4], pose[part][5], pose[part][6], pose[part][7]]
                                part_name[part] = [self.weapon[part], pose[part][0], pose[part][1]]
                        else:
                            if any(ext in part for ext in ("effect", "special")):
                                sprite_part[part] = [self.sprite_image[part],
                                                     (self.sprite_image[part].get_width() / 2, self.sprite_image[part].get_height() / 2),
                                                     link_list[part], pose[part][5], pose[part][6], pose[part][7], pose[part][8]]
                            else:
                                sprite_part[part] = [self.sprite_image[part], main_joint_pos_list[part], link_list[part], pose[part][5],
                                                     pose[part][6], pose[part][7], pose[part][8]]
                            part_name[part] = [pose[part][0], pose[part][1], pose[part][2]]
                pose_layer_list = self.make_layer_list(sprite_part)
                self.animation_part_list[index] = sprite_part
                self.part_name_list[index] = part_name
                image = self.create_animation_film(pose_layer_list, index)
                self.animation_list[index] = image
                if index == current_frame:
                    self.create_joint(pose_layer_list)
            self.frame_list = frame_list

        activate_list = [False] * 10
        for strip_index, strip in enumerate(filmstrips):
            strip.activate = False
            for stuff in self.animation_part_list[strip_index].values():
                if stuff is not None:
                    strip.activate = True
                    activate_list[strip_index] = True
                    break

        # recreate property list
        setup_list(menu.NameList, current_anim_row, anim_prop_list_box.namelist, anim_prop_namegroup,
                   anim_prop_list_box, ui, screen_scale, layer=9, old_list=anim_property_select)
        setup_list(menu.NameList, current_frame_row, frame_prop_list_box.namelist[current_frame], frame_prop_namegroup,
                   frame_prop_list_box, ui, screen_scale, layer=9, old_list=frame_property_select[current_frame])

    def create_animation_film(self, pose_layer_list, frame, empty=False):
        image = pygame.Surface((default_sprite_size[0] * self.size, default_sprite_size[1] * self.size),
                               pygame.SRCALPHA)  # default size will scale down later
        if empty is False:
            for index, layer in enumerate(pose_layer_list):
                part = self.animation_part_list[frame][layer]
                if part[0] is not None:
                    image = self.part_to_sprite(image, part[0], list(self.animation_part_list[frame].keys()).index(layer),
                                                part[1], part[2], part[3], part[4], part[6])
        return image

    def create_joint(self, pose_layer_list):
        for index, layer in enumerate(pose_layer_list):
            part = self.animation_part_list[current_frame][layer]
            name_check = layer
            if any(ext in name_check for ext in p_list):
                name_check = name_check[3:]  # remove p*number*_
            if self.part_name_list[current_frame][layer] is not None and \
                    name_check in skel_joint_list[direction_list.index(self.part_name_list[current_frame][layer][1])]:
                for index2, item in enumerate(
                        skel_joint_list[direction_list.index(self.part_name_list[current_frame][layer][1])][name_check]):
                    joint_type = 0  # main
                    if index2 > 0:
                        joint_type = 1
                    joint_pos = list(item.values())[0]
                    pos = (part[2][0] + (joint_pos[0] - (part[0].get_width() / 2)),
                           part[2][1] + (joint_pos[1] - (part[0].get_height() / 2)))
                    Joint(joint_type, layer, name_check, (pos[0] / self.size, pos[1] / self.size), part[3])

    def grab_face_part(self, race, side, part, part_check, part_default):
        """For creating body part like eye or mouth in animation that accept any part (1) so use default instead"""
        if part_check == 1:  # any part
            surface = gen_body_sprite_pool[race][side][part][part_default].copy()
        else:
            surface = gen_body_sprite_pool[race][side][part][part_check].copy()
        return surface

    def generate_body(self, bodypart_list):
        p_head_sprite_surface = {"p" + str(p): None for p in range(1, max_person + 1)}
        for key in p_head_sprite_surface:
            head_sprite_surface = None
            try:
                head_race = bodypart_list[key + "_head"][0]
                head_side = bodypart_list[key + "_head"][1]
                head_sprite = gen_body_sprite_pool[head_race][head_side]["head"][bodypart_list[key + "_head"][2]].copy()
                head_sprite_surface = pygame.Surface(head_sprite.get_size(), pygame.SRCALPHA)
                head_rect = head_sprite.get_rect(midtop=(head_sprite_surface.get_width() / 2, 0))
                head_sprite_surface.blit(head_sprite, head_rect)
                face = [gen_body_sprite_pool[head_race][head_side]["eyebrow"][self.p_eyebrow[key]].copy(),
                        self.grab_face_part(head_race, head_side, "eye", bodypart_list[key + "_eye"], self.p_any_eye[key]),
                        gen_body_sprite_pool[head_race][head_side]["beard"][self.p_beard[key]].copy(),
                        self.grab_face_part(head_race, head_side, "mouth", bodypart_list[key + "_mouth"], self.p_any_mouth[key])]
                # if skin != "white":
                #     face[0] = self.apply_colour(face[0], skin_colour)
                face[0] = apply_colour(face[0], self.p_hair_colour[key])
                face[2] = apply_colour(face[2], self.p_hair_colour[key])
                face[1] = apply_colour(face[1], self.p_eye_colour[key])

                head_sprite_surface = pygame.Surface((face[2].get_width(), face[2].get_height()), pygame.SRCALPHA)
                rect = head_sprite.get_rect(center=(head_sprite_surface.get_width() / 2, head_sprite_surface.get_height() / 2))
                head_sprite_surface.blit(head_sprite, rect)

                for index, item in enumerate(face):  # add face to head sprite
                    rect = item.get_rect(center=(head_sprite_surface.get_width() / 2, head_sprite_surface.get_height() / 2))
                    head_sprite_surface.blit(item, rect)

            except KeyError:  # some head direction show no face
                pass
            except TypeError:  # empty
                pass

            p_head_sprite_surface[key] = head_sprite_surface

            if self.armour[key + "_armour"] != "None":
                try:
                    armour = self.armour[key + "_armour"].split("/")
                    gear_image = gen_armour_sprite_pool[head_race][armour[0]][armour[1]][head_side]["helmet"][bodypart_list[key + "_head"][2]].copy()
                    rect = gear_image.get_rect(center=(head_sprite_surface.get_width() / 2, head_sprite_surface.get_height() / 2))
                    head_sprite_surface.blit(gear_image, rect)
                    p_head_sprite_surface[key] = head_sprite_surface

                except KeyError:  # skip part that not exist
                    pass
                except UnboundLocalError:  # for when change animation
                    pass

        self.sprite_image = {key: None for key in self.rect_part_list.keys()}
        except_list = ["eye", "mouth", "head"]  # skip doing these
        for stuff in bodypart_list:  # create stat and image
            if bodypart_list[stuff] is not None:
                if any(ext in stuff for ext in except_list) is False:
                    if "weapon" in stuff:
                        part_name = self.weapon[stuff]
                        if part_name is not None and bodypart_list[stuff][2]:
                            self.sprite_image[stuff] = gen_weapon_sprite_pool[part_name][bodypart_list[stuff][1]][bodypart_list[stuff][2]].copy()
                    elif "effect_" in stuff:
                        self.sprite_image[stuff] = effect_sprite_pool[bodypart_list[stuff][0]][bodypart_list[stuff][1]][
                            bodypart_list[stuff][2]].copy()
                    else:
                        new_part_name = stuff
                        if any(ext in stuff for ext in p_list):
                            part_name = stuff[3:]  # remove p*number*_ to get part name
                            new_part_name = part_name
                        if "special" in stuff:
                            part_name = "special"
                            new_part_name = part_name
                        if "r_" in part_name[0:2] or "l_" in part_name[0:2]:
                            new_part_name = part_name[2:]  # remove side
                        self.sprite_image[stuff] = gen_body_sprite_pool[bodypart_list[stuff][0]][bodypart_list[stuff][1]][new_part_name][
                            bodypart_list[stuff][2]].copy()
                        if any(ext in stuff for ext in p_list) and self.armour[stuff[0:2] + "_armour"] != "None":
                            try:
                                armour = self.armour[stuff[0:2] + "_armour"].split("/")
                                gear_image = \
                                gen_armour_sprite_pool[bodypart_list[stuff][0]][armour[0]][armour[1]][bodypart_list[stuff][1]][part_name][
                                    bodypart_list[stuff][2]].copy()
                                rect = gear_image.get_rect(
                                    center=(self.sprite_image[stuff].get_width() / 2, self.sprite_image[stuff].get_height() / 2))
                                self.sprite_image[stuff].blit(gear_image, rect)
                            except KeyError:  # skip part that not exist
                                pass
                            except UnboundLocalError:  # for when change animation
                                pass

                elif "head" in stuff:
                    self.sprite_image[stuff] = p_head_sprite_surface[stuff[0:2]]
        # if skin != "white":
        #     for part in list(self.sprite_image.keys())[1:]:
        #         self.sprite_image[part] = self.apply_colour(self.sprite_image[part], skin_colour)

        main_joint_pos_list = {}
        for part_index, part in enumerate(part_name_header):
            for part_link in skel_joint_list[self.side]:
                if part_link in part:  # match part name, p*number*_head = head in part link
                    main_joint_pos_list[part] = list(skel_joint_list[self.side][part_link][0].values())[0]
                    break
            if part in self.weapon and self.weapon[part] in weapon_joint_list[self.side]:  # weapon joint
                main_joint_pos_list[part] = list(weapon_joint_list[self.side][self.weapon[part]][0].values())[0]

        return main_joint_pos_list

    def click_part(self, mouse_pos, shift_press, ctrl_press, part=None):
        if part is None:
            click_part = False
            if shift_press is False and ctrl_press is False:
                self.part_selected = []
            else:
                click_part = True
            for index, rect in enumerate(self.rect_part_list):
                this_rect = self.rect_part_list[rect]
                if this_rect is not None and this_rect.collidepoint(mouse_pos):
                    click_part = True
                    if shift_press:  # add
                        if index not in self.part_selected:
                            self.part_selected.append(index)
                    elif ctrl_press:  # remove
                        if index in self.part_selected:
                            self.part_selected.remove(index)
                    else:  # select
                        self.part_selected = [index]
                    break
            if click_part is False:
                self.part_selected = []
        else:
            if shift_press:
                self.part_selected.append(list(self.rect_part_list.keys()).index(part))
                self.part_selected = list(set(self.part_selected))
            elif ctrl_press:
                if list(self.rect_part_list.keys()).index(part) in self.part_selected:
                    self.part_selected.remove(list(self.rect_part_list.keys()).index(part))
            else:
                self.part_selected = [list(self.rect_part_list.keys()).index(part)]

    def edit_part(self, mouse_pos, edit_type):
        global animation_history, body_part_history, part_name_history, current_history
        key_list = list(self.rect_part_list.keys())
        if edit_type == "default":  # reset to default
            self.animation_part_list[current_frame] = {key: (value[:].copy() if value is not None else value) for key, value in
                                                       self.default_sprite_part.items()}
            self.bodypart_list[current_frame] = {key: value for key, value in self.default_body_part.items()}
            self.part_name_list[current_frame] = {key: value for key, value in self.default_part_name.items()}
            self.part_selected = []
            race_part_button.change_text("")
            direction_part_button.change_text("")
            part_selector.change_name("")

        elif edit_type == "clear":  # clear whole strip
            for part in self.part_name_list[current_frame]:
                self.bodypart_list[current_frame][part] = [0, 0, 0]
                self.part_name_list[current_frame][part] = ["", "", ""]
                self.animation_part_list[current_frame][part] = []
            self.part_selected = []

        elif edit_type == "change":  # change strip
            self.part_selected = []

        elif edit_type == "paste":  # paste copy part
            for part in copy_part.keys():
                if copy_part[part] is not None:
                    self.bodypart_list[current_frame][part] = copy_part[part].copy()
                    self.animation_part_list[current_frame][part] = copy_animation[part].copy()
                    self.part_name_list[current_frame][part] = copy_name[part].copy()

        elif "direction" in edit_type:
            if self.part_selected:
                for part in self.part_selected:
                    try:
                        part_index = key_list[part]
                        sidechange = edit_type.split("_")[1]
                        self.bodypart_list[current_frame][part_index][1] = sidechange
                        self.part_name_list[current_frame][part_index][1] = sidechange
                        self.generate_body(self.bodypart_list[current_frame])
                        self.animation_part_list[current_frame][part_index][0] = self.sprite_image[part_index]
                    except IndexError:
                        pass
                    except TypeError:  # None type
                        pass
                    except KeyError:  # change side and not found part with same name
                        self.part_name_list[current_frame][part_index][2] = ""

        elif edit_type == "undo" or edit_type == "redo":
            self.part_name_list[current_frame] = part_name_history[current_history]
            self.animation_part_list[current_frame] = animation_history[current_history]
            self.bodypart_list[current_frame] = body_part_history[current_history]

        elif "armour" in edit_type:
            if any(ext in edit_type for ext in p_list) in edit_type:
                self.armour[edit_type[0:2] + "_armour"] = edit_type.split(edit_type[0:2] + "_armour_")[1]
            main_joint_pos_list = self.generate_body(self.bodypart_list[current_frame])
            for part in self.sprite_image:
                if self.animation_part_list[current_frame][part] is not None:
                    self.animation_part_list[current_frame][part][0] = self.sprite_image[part]

        elif "eye" in edit_type:
            if "Any" in edit_type:
                self.bodypart_list[current_frame][edit_type[0:2] + "_eye"] = 1
            else:
                self.bodypart_list[current_frame][edit_type[0:2] + "_eye"] = edit_type.split(edit_type[0:2] + "_eye_")[1]
            self.generate_body(self.bodypart_list[current_frame])
            part = edit_type[0:2] + "_head"
            self.animation_part_list[current_frame][part][0] = self.sprite_image[part]

        elif "mouth" in edit_type:
            if "Any" in edit_type:
                self.bodypart_list[current_frame][edit_type[0:2] + "_mouth"] = 1
            else:
                self.bodypart_list[current_frame][edit_type[0:2] + "_mouth"] = edit_type.split(edit_type[0:2] + "_mouth_")[1]
            self.generate_body(self.bodypart_list[current_frame])
            part = edit_type[0:2] + "_head"
            self.animation_part_list[current_frame][part][0] = self.sprite_image[part]

        elif "part" in edit_type:
            if self.part_selected:
                part = self.part_selected[-1]
                part_index = key_list[part]
                part_change = edit_type[5:]
                self.bodypart_list[current_frame][part_index][2] = part_change
                self.part_name_list[current_frame][part_index][2] = part_change
                main_joint_pos_list = self.generate_body(self.bodypart_list[current_frame])
                if not self.animation_part_list[current_frame][part_index]:
                    self.animation_part_list[current_frame][part_index] = self.empty_sprite_part.copy()
                    if any(ext in part_index for ext in ("effect", "special")):
                        self.animation_part_list[current_frame][part_index][1] = "center"
                    elif "weapon" in part_index:
                        self.animation_part_list[current_frame][part_index][1] = main_joint_pos_list[part_index]
                    else:
                        self.animation_part_list[current_frame][part_index][1] = main_joint_pos_list[part_index]
                self.animation_part_list[current_frame][part_index][0] = self.sprite_image[part_index]

        elif "race" in edit_type:  # change race/base part type
            if self.part_selected:
                part = self.part_selected[-1]
                part_index = key_list[part]
                part_change = edit_type[5:]
                if "weapon" in part_index:
                    self.weapon[part_index] = part_change
                if self.bodypart_list[current_frame][part_index] is None:
                    self.bodypart_list[current_frame][part_index] = [0, 0, 0]
                    self.part_name_list[current_frame][part_index] = ["", "", ""]
                    self.animation_part_list[current_frame][part_index] = []
                self.bodypart_list[current_frame][part_index][0] = part_change
                self.part_name_list[current_frame][part_index][0] = part_change
                self.bodypart_list[current_frame][part_index][2] = self.part_name_list[current_frame][part_index][
                    2]  # attempt to get part again in case the initial reading not found
                try:
                    self.generate_body(self.bodypart_list[current_frame])
                    self.animation_part_list[current_frame][part_index][0] = self.sprite_image[part_index]
                except IndexError:
                    pass
                except KeyError:  # change side and not found part with same name
                    pass

        elif "new" in edit_type:  # new animation
            self.animation_part_list = [{key: None for key in self.rect_part_list.keys()}] * 10
            p_face = {}
            for p in range(1, max_person + 1):
                p_face = p_face | {"p" + str(p) + "_eye": 1, "p" + str(p) + "_mouth": 1}
            self.bodypart_list = [{key: value for key, value in self.all_part_list.items()}] * 10
            for stuff in self.bodypart_list:
                stuff.update(p_face)
            self.part_name_list = [{key: None for key in self.rect_part_list.keys()}] * 10
            self.part_selected = []

        elif self.part_selected:
            for part in self.part_selected:
                if part < len(key_list):  # can't edit part that not exist
                    part_index = key_list[part]
                    if self.animation_part_list[current_frame][part_index] is not None and \
                            len(self.animation_part_list[current_frame][part_index]) > 3:
                        if edit_type == "place":  # mouse place
                            new_point = mouse_pos
                            if point_edit == 1:  # use joint
                                part_image = self.sprite_image[part_index]
                                center = pygame.Vector2(part_image.get_width() / 2, part_image.get_height() / 2)
                                pos_different = center - self.animation_part_list[current_frame][part_index][
                                    1]  # find distance between image center and connect point main_joint_pos
                                new_point = new_point + pos_different
                            self.animation_part_list[current_frame][part_index][2] = new_point

                        elif "move_" in edit_type:  # keyboard move
                            try:
                                new_point = [self.animation_part_list[current_frame][part_index][2][0],
                                             self.animation_part_list[current_frame][part_index][2][1]]
                            except TypeError:  # None position
                                new_point = [0, 0]
                            if "w" in edit_type:
                                new_point[1] = new_point[1] - 0.5
                            elif "s" in edit_type:
                                new_point[1] = new_point[1] + 0.5
                            elif "a" in edit_type:
                                new_point[0] = new_point[0] - 0.5
                            elif "d" in edit_type:
                                new_point[0] = new_point[0] + 0.5
                            self.animation_part_list[current_frame][part_index][2] = new_point.copy()

                        elif "tilt_" in edit_type:  # keyboard rotate
                            new_angle = self.animation_part_list[current_frame][part_index][3]
                            if "q" in edit_type:
                                new_angle = new_angle - 0.5
                            elif "e" in edit_type:
                                new_angle = new_angle + 0.5
                            self.animation_part_list[current_frame][part_index][3] = new_angle

                        elif edit_type == "rotate":  # mouse rotate
                            base_pos = self.animation_part_list[current_frame][part_index][2]
                            myradians = math.atan2(mouse_pos[1] - base_pos[1], mouse_pos[0] - base_pos[0])
                            new_angle = math.degrees(myradians)
                            # """upper left -"""
                            if -180 <= new_angle <= -90:
                                new_angle = -new_angle - 90

                            # """upper right +"""
                            elif -90 < new_angle < 0:
                                new_angle = (-new_angle) - 90

                            # """lower right -"""
                            elif 0 <= new_angle <= 90:
                                new_angle = -(new_angle + 90)

                            # """lower left +"""
                            elif 90 < new_angle <= 180:
                                new_angle = 270 - new_angle

                            self.animation_part_list[current_frame][part_index][3] = new_angle

                        elif "scale" in edit_type:  # part scale
                            if "up" in edit_type:
                                self.animation_part_list[current_frame][part_index][6] += 0.1
                                self.animation_part_list[current_frame][part_index][6] = round(self.animation_part_list[current_frame][part_index][6],
                                                                                               1)
                            elif "down" in edit_type:
                                self.animation_part_list[current_frame][part_index][6] -= 0.1
                                if self.animation_part_list[current_frame][part_index][6] < 0:
                                    self.animation_part_list[current_frame][part_index][6] = 0
                                self.animation_part_list[current_frame][part_index][6] = round(self.animation_part_list[current_frame][part_index][6],
                                                                                               1)
                        elif "flip" in edit_type:
                            flip_type = int(edit_type[-1])
                            current_flip = self.animation_part_list[current_frame][part_index][4]
                            if current_flip == 0:  # current no flip
                                self.animation_part_list[current_frame][part_index][4] = flip_type
                            elif current_flip == 1:  # current horizon flip
                                if flip_type == 1:
                                    self.animation_part_list[current_frame][part_index][4] = 0
                                else:
                                    self.animation_part_list[current_frame][part_index][4] = 3
                            elif current_flip == 2:  # current vertical flip
                                if flip_type == 1:
                                    self.animation_part_list[current_frame][part_index][4] = 3
                                else:
                                    self.animation_part_list[current_frame][part_index][4] = 0
                            elif current_flip == 3:  # current both hori and vert flip
                                if flip_type == 1:
                                    self.animation_part_list[current_frame][part_index][4] = 2
                                else:
                                    self.animation_part_list[current_frame][part_index][4] = 1

                        elif "reset" in edit_type:
                            self.animation_part_list[current_frame][part_index][3] = 0
                            self.animation_part_list[current_frame][part_index][4] = 0

                        elif "delete" in edit_type:
                            self.bodypart_list[current_frame][part_index] = [0, 0, 0]
                            self.part_name_list[current_frame][part_index] = ["", "", ""]
                            self.animation_part_list[current_frame][part_index] = None

                        elif "layer_" in edit_type:
                            if "up" in edit_type:
                                self.animation_part_list[current_frame][part_index][5] += 1
                            elif "down" in edit_type:
                                self.animation_part_list[current_frame][part_index][5] -= 1
                                if self.animation_part_list[current_frame][part_index][5] == 0:
                                    self.animation_part_list[current_frame][part_index][5] = 1
        for key, value in self.rect_part_list.items():  # reset rect list
            self.rect_part_list[key] = None
        for joint in joints:  # remove all joint first
            joint.kill()

        # recreate frame image
        pose_layer_list = self.make_layer_list(self.animation_part_list[current_frame])
        surface = self.create_animation_film(pose_layer_list, current_frame)
        self.create_joint(pose_layer_list)
        self.animation_list[current_frame] = surface
        name_list = self.part_name_list[current_frame]
        try:
            sprite_part = self.animation_part_list[current_frame]
            self.frame_list[current_frame] = {
                key: name_list[key] + [sprite_part[key][2][0], sprite_part[key][2][1], sprite_part[key][3], sprite_part[key][4],
                                       sprite_part[key][5], sprite_part[key][6]] if sprite_part[key] is not None else [0]
                for key in list(self.rect_part_list.keys())}
        except TypeError:  # None type error from empty frame
            self.frame_list[current_frame] = {key: [0] for key in list(self.rect_part_list.keys())}
        except IndexError:
            self.frame_list[current_frame] = {key: [0] for key in list(self.rect_part_list.keys())}
        for key in list(self.frame_list[current_frame].keys()):
            if "weapon" in key and self.frame_list[current_frame][key] != [0]:
                self.frame_list[current_frame][key] = self.frame_list[current_frame][key][1:]
        p_face = {}
        for p in p_list:
            p_face = p_face | {p: {p + "_eye": self.bodypart_list[current_frame][p + "_eye"],
                                   p + "_mouth": self.bodypart_list[current_frame][p + "_mouth"]}}
        for p in p_face:
            p_face_pos = list(self.frame_list[current_frame].keys()).index(p + "_head") + 1
            self.frame_list[current_frame] = {k: v for k, v in (list(self.frame_list[current_frame].items())[:p_face_pos] + list(p_face[p].items()) +
                                                                list(self.frame_list[current_frame].items())[p_face_pos:])}

        self.frame_list[current_frame]["size"] = self.size
        self.frame_list[current_frame]["frame_property"] = frame_property_select[current_frame]
        self.frame_list[current_frame]["animation_property"] = anim_property_select
        anim_to_pool(animation_name, current_pool, self, activate_list)
        reload_animation(anim, self)

        if edit_type == "new" or edit_type == "change":
            if edit_type == "new":
                for index, frame in enumerate(self.frame_list):  # reset all frame to empty frame like the first one
                    self.frame_list[index] = {key: value for key, value in list(self.frame_list[0].items())}
                anim_to_pool(animation_name, current_pool, self, activate_list, new=True)

            # reset history when change frame or create new animation
            part_name_history = part_name_history[-1:] + [self.part_name_list[current_frame]]
            animation_history = animation_history[-1:] + [self.animation_part_list[current_frame]]
            body_part_history = body_part_history[-1:] + [self.bodypart_list[current_frame]]
            current_history = 0
        elif edit_type != "undo" and edit_type != "redo":
            if current_history < len(animation_history) - 1:
                part_name_history = part_name_history[:current_history + 1]
                animation_history = animation_history[:current_history + 1]
                body_part_history = body_part_history[:current_history + 1]

            self.add_history()

            if len(animation_history) > 1000:  # save only last 1000 activity
                new_first = len(animation_history) - 1000
                part_name_history = part_name_history[new_first:]
                animation_history = animation_history[new_first:]
                body_part_history = body_part_history[new_first:]
                current_history -= new_first

    def part_to_sprite(self, surface, part, part_index, main_joint_pos, target, angle, flip, scale):
        """Find body part's new center point from main_joint_pos with new angle, then create rotated part and blit to sprite"""
        part_rotated = part.copy()
        if scale != 1:
            part_rotated = pygame.transform.scale(part_rotated, (part_rotated.get_width() * scale,
                                                                 part_rotated.get_height() * scale))
        if flip != 0:
            if flip == 1:  # horizontal only
                part_rotated = pygame.transform.flip(part_rotated, True, False)
            elif flip == 2:  # vertical only
                part_rotated = pygame.transform.flip(part_rotated, False, True)
            elif flip == 3:  # flip both direction
                part_rotated = pygame.transform.flip(part_rotated, True, True)
        if angle != 0:
            part_rotated = pygame.transform.rotate(part_rotated, angle)  # rotate part sprite

        center = pygame.Vector2(part.get_width() / 2, part.get_height() / 2)
        new_target = target  # - pos_different  # find new center point
        # if "weapon" in list(self.rect_part_list.keys())[part_index] and main_joint_pos != "center":  # only weapon use joint to calculate position
        #     pos_different = main_joint_pos - center  # find distance between image center and connect point main_joint_pos
        #     new_target = main_joint_pos + pos_different
        # if angle != 0:
        #     radians_angle = math.radians(360 - angle)
        #     new_target = rotation_xy(target, new_target, radians_angle)  # find new center point with rotation

        rect = part_rotated.get_rect(center=new_target)
        self.rect_part_list[list(self.rect_part_list.keys())[part_index]] = rect
        surface.blit(part_rotated, rect)

        return surface

    def remake_rect_list(self):
        for key, value in self.rect_part_list.items():  # reset rect list
            self.rect_part_list[key] = None

        for part_index, part in enumerate(self.animation_part_list[current_frame]):
            rect = part.rect
            self.rect_part_list[list(self.rect_part_list.keys())[part_index]] = rect

    def add_history(self):
        global current_history
        animation_history.append(
            {key: (value[:].copy() if value is not None else value) for key, value in self.animation_part_list[current_frame].items()})
        body_part_history.append({key: value for key, value in self.bodypart_list[current_frame].items()})
        part_name_history.append({key: value for key, value in self.part_name_list[current_frame].items()})
        current_history += 1


class Joint(pygame.sprite.Sprite):
    images = None

    def __init__(self, joint_type, name, part, pos, angle):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.joint_type = joint_type
        self.part = part
        self.name = name
        self.pos = (pos[0] * showroom_scale_mul[0], pos[1] * showroom_scale_mul[1])
        self.image = self.images[self.joint_type].copy()
        self.image = pygame.transform.rotate(self.image, angle)  # rotate part sprite
        self.rect = self.image.get_rect(center=self.pos)


class Animation:
    # created in 22 dec 2020 by cenk
    def __init__(self, spd_ms, loop):
        self.frames = None
        self.speed_ms = spd_ms / 1000
        self.start_frame = 0
        self.end_frame = 0
        self.first_time = time.time()
        self.show_frame = 0
        self.loop = loop

    def reload(self, frames):
        self.frames = frames
        self.end_frame = len(self.frames) - 1

    def play(self, surface, position, play_list):
        global current_frame
        if dt > 0 and True in play_list:
            if time.time() - self.first_time >= self.speed_ms:
                self.show_frame += 1
                while self.show_frame < 10 and play_list[self.show_frame] is False:
                    self.show_frame += 1
                self.first_time = time.time()
            if self.show_frame > self.end_frame:
                self.show_frame = self.start_frame
                while self.show_frame < 10 and play_list[self.show_frame] is False:
                    self.show_frame += 1

        surface.blit(self.frames[int(self.show_frame)], position)
        if dt == 0 and show_joint:
            for joint in joints:
                surface.blit(joint.image, joint.rect)


# start animation maker
clock = pygame.time.Clock()

runtime = 0
mouse_timer = 0
play_animation = False
show_joint = False
current_frame = 0
copy_animation_frame = None
copy_part = None
copy_name_frame = None
copy_stat = None
current_popup_row = 0
keypress_delay = 0
point_edit = 0
text_input_popup = (None, None)
animation_history = []
body_part_history = []
part_name_history = []
current_history = 0
current_pool = generic_animation_pool

ui = pygame.sprite.LayeredUpdates()
fake_group = pygame.sprite.LayeredUpdates()  # just fake group to add for container and not get auto update

showroom_scale = (default_sprite_size[0] * screen_size[0] / 500, default_sprite_size[1] * screen_size[1] / 500)
showroom_scale_mul = (showroom_scale[0] / default_sprite_size[0], showroom_scale[1] / default_sprite_size[1])
showroom = Showroom(showroom_scale)
ui.add(showroom)

Joint.images = [pygame.transform.scale(load_image(current_dir, screen_scale, "mainjoint.png", ["animation_maker_ui"]),
                                       (int(20 * screen_scale[0]), int(20 * screen_scale[1]))),
                pygame.transform.scale(load_image(current_dir, screen_scale, "subjoint.png", ["animation_maker_ui"]),
                                       (int(20 * screen_scale[0]), int(20 * screen_scale[1])))]
joints = pygame.sprite.Group()

image = pygame.transform.scale(load_image(current_dir, screen_scale, "film.png", ["animation_maker_ui"]),
                               (int(100 * screen_scale[0]), int(100 * screen_scale[1])))

Filmstrip.image_original = image
filmstrips = pygame.sprite.Group()

Button.containers = ui
SwitchButton.containers = ui
BodyHelper.containers = ui
Joint.containers = joints
Filmstrip.containers = ui, filmstrips
NameBox.containers = ui
menu.MenuButton.containers = fake_group
menu.NameList.containers = ui
popup_list_box = pygame.sprite.Group()
popup_namegroup = pygame.sprite.Group()
anim_prop_namegroup = pygame.sprite.Group()
frame_prop_namegroup = pygame.sprite.Group()

filmstrip_list = [Filmstrip((0, 42 * screen_scale[1])), Filmstrip((image.get_width(), 42 * screen_scale[1])),
                  Filmstrip((image.get_width() * 2, 42 * screen_scale[1])), Filmstrip((image.get_width() * 3, 42 * screen_scale[1])),
                  Filmstrip((image.get_width() * 4, 42 * screen_scale[1])), Filmstrip((image.get_width() * 5, 42 * screen_scale[1])),
                  Filmstrip((image.get_width() * 6, 42 * screen_scale[1])), Filmstrip((image.get_width() * 7, 42 * screen_scale[1])),
                  Filmstrip((image.get_width() * 8, 42 * screen_scale[1])), Filmstrip((image.get_width() * 9, 42 * screen_scale[1]))]

filmstrips.add(*filmstrip_list)

images = load_images(current_dir, screen_scale, ["animation_maker_ui", "helper_parts"])
body_helper_size = (450 * screen_scale[0], 270 * screen_scale[1])
effect_helper_size = (450 * screen_scale[0], 270 * screen_scale[1])
effect_helper = BodyHelper(effect_helper_size, (screen_size[0] / 1.25, screen_size[1] - (body_helper_size[1] / 2)),
                           "effect", [images["smallbox_helper.png"]])
del images["smallbox_helper.png"]
p_body_helper = BodyHelper(body_helper_size, (body_helper_size[0] / 2,
                                              screen_size[1] - (body_helper_size[1] / 2)), "p1", list(images.values()))
helper_list = [p_body_helper, effect_helper]

image = load_image(current_dir, screen_scale, "button.png", ["animation_maker_ui"])
image = pygame.transform.scale(image, (int(image.get_width() * screen_scale[1]),
                                       int(image.get_height() * screen_scale[1])))

new_button = Button("New", image, (image.get_width() / 2, image.get_height() / 2))
save_button = Button("Save", image, (image.get_width() * 1.5, image.get_height() / 2))
size_button = Button("Size: ", image, (image.get_width() * 2.5, image.get_height() / 2))
direction_button = Button("", image, (image.get_width() * 3.5, image.get_height() / 2))
rename_button = Button("Rename", image, (screen_size[0] - (image.get_width() * 3.5), image.get_height() / 2))
duplicate_button = Button("Duplicate", image, (screen_size[0] - (image.get_width() * 2.5), image.get_height() / 2))
export_button = Button("Export", image, (screen_size[0] - (image.get_width() * 1.5), image.get_height() / 2))
delete_button = Button("Delete", image, (screen_size[0] - (image.get_width() / 2), image.get_height() / 2))

play_animation_button = SwitchButton(["Play", "Stop"], image,
                                     (screen_size[1] / 2, filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 0.5)))
joint_button = SwitchButton(["Joint:OFF", "Joint:ON"], image, (play_animation_button.pos[0] + play_animation_button.image.get_width() * 5,
                                                               filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
grid_button = SwitchButton(["Grid:ON", "Grid:OFF"], image, (play_animation_button.pos[0] + play_animation_button.image.get_width() * 6,
                                                            filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
all_copy_button = Button("Copy A", image, (play_animation_button.pos[0] - (play_animation_button.image.get_width() * 2),
                                           filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
all_paste_button = Button("Paste A", image, (play_animation_button.pos[0] - play_animation_button.image.get_width(),
                                             filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
frame_copy_button = Button("Copy F", image, (play_animation_button.pos[0] + play_animation_button.image.get_width(),
                                             filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
frame_paste_button = Button("Paste F", image, (play_animation_button.pos[0] + play_animation_button.image.get_width() * 2,
                                               filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
speed_button = Button("Speed: 1", image, (screen_size[1] / 2,
                                          filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
default_button = Button("Default", image, (play_animation_button.pos[0] + play_animation_button.image.get_width() * 3,
                                           filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
point_edit_button = SwitchButton(["Center", "Joint"], image, (play_animation_button.pos[0] + play_animation_button.image.get_width() * 4,
                                                              filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
clear_button = Button("Clear", image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 3,
                                       filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
activate_button = SwitchButton(["Enable", "Disable"], image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 4,
                                                              filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
undo_button = Button("Undo", image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 5,
                                     filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
redo_button = Button("Redo", image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 6,
                                     filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))

reset_button = Button("Reset", image, (screen_size[0] / 2.1, p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))

flip_hori_button = Button("Flip H", image, (reset_button.pos[0] + reset_button.image.get_width(),
                                            p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
flip_vert_button = Button("Flip V", image, (reset_button.pos[0] + (reset_button.image.get_width() * 2),
                                            p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
part_copy_button = Button("Copy P", image, (reset_button.pos[0] + reset_button.image.get_width() * 3,
                                            p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
part_paste_button = Button("Paste P", image, (reset_button.pos[0] + reset_button.image.get_width() * 4,
                                              p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
p_all_button = Button("P All", image, (reset_button.pos[0] + reset_button.image.get_width() * 7,
                                       p_body_helper.rect.midtop[1] - (image.get_height() * 2)))
all_button = Button("All", image, (reset_button.pos[0] + reset_button.image.get_width() * 7,
                                   p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
race_part_button = Button("", image, (reset_button.image.get_width() / 2,
                                      p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
direction_part_button = Button("", image, (race_part_button.pos[0] + race_part_button.image.get_width(),
                                           p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
p_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 1.8,
                                                 p_body_helper.rect.midtop[1] - (image.get_height() * 5.2)))
armour_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 1.8,
                                                      p_body_helper.rect.midtop[1] - (image.get_height() * 4.2)))
eye_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 1.8,
                                                   p_body_helper.rect.midtop[1] - (image.get_height() * 3.2)))
mouth_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 1.8,
                                                     p_body_helper.rect.midtop[1] - (image.get_height() * 2.2)))
# lock_button = SwitchButton(["Lock:OFF","Lock:ON"], image, (reset_button.pos[0] + reset_button.image.get_width() * 2,
#                                            p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))

input_ui = menu.InputUI(screen_scale, load_image(main_dir, screen_scale, "input_ui.png", "ui\\mainmenu_ui"),
                        (screen_size[0] / 2, screen_size[1] / 2))  # user text input ui box popup

image_list = load_base_button(main_dir, screen_scale)

input_ok_button = menu.MenuButton(screen_scale, image_list, pos=(input_ui.rect.midleft[0] + image_list[0].get_width(),
                                                                 input_ui.rect.midleft[1] + image_list[0].get_height()),
                                  text="Confirm", layer=31)
input_cancel_button = menu.MenuButton(screen_scale, image_list,
                                      pos=(input_ui.rect.midright[0] - image_list[0].get_width(),
                                           input_ui.rect.midright[1] + image_list[0].get_height()),
                                      text="Cancel", layer=31)
input_button = (input_ok_button, input_cancel_button)
input_box = menu.InputBox(screen_scale, input_ui.rect.center, input_ui.image.get_width())  # user text input box

input_ui_popup = (input_ui, input_box, input_ok_button, input_cancel_button)

confirm_ui = menu.InputUI(screen_scale, load_image(main_dir, screen_scale, "input_ui.png", "ui\\mainmenu_ui"),
                          (screen_size[0] / 2, screen_size[1] / 2))  # user confirm input ui box popup
confirm_ui_popup = (confirm_ui, input_ok_button, input_cancel_button)

colour_ui = menu.InputUI(screen_scale, load_image(current_dir, screen_scale, "colour.png", "animation_maker_ui"),
                         (screen_size[0] / 2, screen_size[1] / 2))  # user text input ui box popup
colour_wheel = ColourWheel(load_image(main_dir, screen_scale, "rgb.png", ["sprite"]), (colour_ui.pos[0], colour_ui.pos[1] / 1.5))
colour_input_box = menu.InputBox(screen_scale, (colour_ui.rect.center[0], colour_ui.rect.center[1] * 1.2),
                                 input_ui.image.get_width())  # user text input box

colour_ok_button = menu.MenuButton(screen_scale, image_list, pos=(colour_ui.rect.midleft[0] + image_list[0].get_width(),
                                                                  colour_ui.rect.midleft[1] + (image_list[0].get_height() * 2)),
                                   text="Confirm", layer=31)
colour_cancel_button = menu.MenuButton(screen_scale, image_list,
                                       pos=(colour_ui.rect.midright[0] - image_list[0].get_width(),
                                            colour_ui.rect.midright[1] + (image_list[0].get_height() * 2)),
                                       text="Cancel", layer=31)
colour_ui_popup = (colour_ui, colour_wheel, colour_input_box, colour_ok_button, colour_cancel_button)

box_img = load_image(current_dir, screen_scale, "property_box.png", "animation_maker_ui")
big_box_img = load_image(main_dir, screen_scale, "biglistbox.png", "ui\\mainmenu_ui")

menu.ListBox.containers = popup_list_box
popup_list_box = menu.ListBox(screen_scale, (0, 0), big_box_img, 16)  # popup box need to be in higher layer
battleui.UIScroll(popup_list_box, popup_list_box.rect.topright) # create scroll for popup list box
anim_prop_list_box = menu.ListBox(screen_scale, (0, filmstrip_list[0].rect.midbottom[1] +
                                                 (reset_button.image.get_height() * 1.5)), box_img, 8)
anim_prop_list_box.namelist = anim_property_list + ["Custom"]
frame_prop_list_box = menu.ListBox(screen_scale, (screen_size[0] - box_img.get_width(), filmstrip_list[0].rect.midbottom[1] +
                                                  (reset_button.image.get_height() * 1.5)), box_img, 8)
frame_prop_list_box.namelist = [frame_property_list + ["Custom"] for _ in range(10)]
battleui.UIScroll(anim_prop_list_box, anim_prop_list_box.rect.topright)  # create scroll for animation prop box
battleui.UIScroll(frame_prop_list_box, frame_prop_list_box.rect.topright)  # create scroll for frame prop box
current_anim_row = 0
current_frame_row = 0
frame_property_select = [[] for _ in range(10)]
anim_property_select = []
anim_prop_list_box.scroll.change_image(new_row=0, row_size=len(anim_prop_list_box.namelist))
frame_prop_list_box.scroll.change_image(new_row=0, row_size=len(frame_prop_list_box.namelist[current_frame]))
ui.add(anim_prop_list_box, frame_prop_list_box, anim_prop_list_box.scroll, frame_prop_list_box.scroll)

animation_selector = NameBox((400, image.get_height()), (screen_size[0] / 2, 0))
part_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 4,
                                                    reset_button.rect.midtop[1]))

shift_press = False
anim = Animation(500, True)
model = Model()
model.animation_list = []
copy_list = []  # list of copied animation frames
direction = 1
activate_list = [False] * 10
direction_button.change_text(direction_list[direction])
try:
    animation_name = list(generic_animation_pool[0].keys())[0]
except:
    animation_name = None
model.read_animation(animation_name)
animation_selector.change_name(animation_name)
if animation_name is not None:
    reload_animation(anim, model)
else:
    model.animation_list = [None] * 10
    model.edit_part(None, "new")
face = [model.frame_list[current_frame]["p1_eye"], model.frame_list[current_frame]["p1_mouth"]]
head_text = ["Eye: ", "Mouth: "]
p_selector.change_name("p1")
armour_selector.change_name(model.armour["p1_armour"])
for index, selector in enumerate([eye_selector, mouth_selector]):
    this_text = "Any"
    if face[index] not in (0, 1):
        this_text = face[index]
    selector.change_name(head_text[index] + str(this_text))
animation_history.append({key: (value[:].copy() if value is not None else value) for key, value in model.animation_part_list[current_frame].items()})
body_part_history.append({key: value for key, value in model.bodypart_list[current_frame].items()})
part_name_history.append({key: value for key, value in model.part_name_list[current_frame].items()})

while True:
    dt = clock.get_time() / 1000
    ui_dt = dt
    mouse_pos = pygame.mouse.get_pos()  # current mouse pos based on screen
    mouse_left_up = False  # left click
    mouse_left_down = False  # hold left click
    mouse_right_up = False  # right click
    mouse_right_down = False  # hold right click
    double_mouse_right = False  # double right click
    mouse_scroll_down = False
    mouse_scroll_up = False
    mouse_wheel_up = False  # mouse wheel click
    mouse_wheel_down = False  # hold mouse wheel click
    copy_press = False
    paste_press = False
    part_copy_press = False
    part_paste_press = False
    undo_press = False
    redo_press = False
    del_press = False
    shift_press = False
    ctrl_press = False
    popup_click = False
    input_esc = False
    popup_list = []

    key_press = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # left click
                mouse_left_up = True
            if event.button == 2:  # click on mouse wheel
                mouse_wheel_up = True
            elif event.button == 3:  # Right Click
                mouse_right_up = True
                if mouse_timer == 0:
                    mouse_timer = 0.001  # Start timer after first mouse click
                elif mouse_timer < 0.3:  # if click again within 0.3 second for it to be considered double click
                    double_mouse_right = True  # double right click
                    mouse_timer = 0
            elif event.button == 4 or event.button == 5:
                if event.button == 4:  # Mouse scroll up
                    mouse_scroll_up = True
                else:  # Mouse scroll down
                    mouse_scroll_down = True
                if popup_list_box in ui and popup_list_box.rect.collidepoint(mouse_pos):
                    current_popup_row = list_scroll(mouse_scroll_up, mouse_scroll_down,
                                                    popup_list_box, current_popup_row, popup_list_box.namelist,
                                                    popup_namegroup, ui, screen_scale)
                elif model.part_selected != [] and showroom.rect.collidepoint(mouse_pos):
                    if event.button == 4:  # Mouse scroll up
                        model.edit_part(mouse_pos, "scale_up")
                    else:  # Mouse scroll down
                        model.edit_part(mouse_pos, "scale_down")
                elif anim_prop_list_box.rect.collidepoint(mouse_pos) or anim_prop_list_box.scroll.rect.collidepoint(mouse_pos):
                    current_anim_row = list_scroll(mouse_scroll_up, mouse_scroll_down,
                                                   anim_prop_list_box, current_anim_row, anim_prop_list_box.namelist,
                                                   anim_prop_namegroup, ui, screen_scale, old_list=anim_property_select)
                elif frame_prop_list_box.rect.collidepoint(mouse_pos) or frame_prop_list_box.scroll.rect.collidepoint(mouse_pos):
                    current_frame_row = list_scroll(mouse_scroll_up, mouse_scroll_down,
                                                    frame_prop_list_box, current_frame_row,
                                                    frame_prop_list_box.namelist[current_frame], frame_prop_namegroup,
                                                    ui, screen_scale, old_list=frame_property_select[current_frame])

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                input_esc = True
            elif text_input_popup[0] == "text_input":
                if input_box in ui:
                    input_box.player_input(event, key_press)
                elif colour_input_box in ui:
                    colour_input_box.player_input(event, key_press)

    if pygame.mouse.get_pressed()[0]:  # Hold left click
        mouse_left_down = True
    elif pygame.mouse.get_pressed()[1]:  # Hold wheel click
        mouse_wheel_down = True
    elif pygame.mouse.get_pressed()[2]:  # Hold left click
        mouse_right_down = True

    if input_ui not in ui and colour_ui not in ui:
        if key_press is not None and keypress_delay < 0.1:
            if key_press[pygame.K_LCTRL] or key_press[pygame.K_RCTRL]:
                ctrl_press = True
                if key_press[pygame.K_c]:  # copy frame
                    copy_press = True
                elif key_press[pygame.K_v]:  # paste frame
                    paste_press = True
                elif key_press[pygame.K_z]:  # undo change
                    keypress_delay = 0.1
                    undo_press = True
                elif key_press[pygame.K_y]:  # redo change
                    keypress_delay = 0.1
                    redo_press = True
            elif key_press[pygame.K_LALT] or key_press[pygame.K_RALT]:
                if key_press[pygame.K_c]:  # copy part
                    part_copy_press = True
                elif key_press[pygame.K_v]:  # paste part
                    part_paste_press = True
            elif key_press[pygame.K_LSHIFT] or key_press[pygame.K_RSHIFT]:
                shift_press = True
            elif key_press[pygame.K_w]:
                model.edit_part(mouse_pos, "move_w")
            elif key_press[pygame.K_s]:
                model.edit_part(mouse_pos, "move_s")
            elif key_press[pygame.K_a]:
                model.edit_part(mouse_pos, "move_a")
            elif key_press[pygame.K_d]:
                model.edit_part(mouse_pos, "move_d")
            elif key_press[pygame.K_q]:
                model.edit_part(mouse_pos, "tilt_q")
            elif key_press[pygame.K_e]:
                model.edit_part(mouse_pos, "tilt_e")
            elif key_press[pygame.K_DELETE]:
                keypress_delay = 0.1
                if model.part_selected:
                    model.edit_part(mouse_pos, "delete")
            elif key_press[pygame.K_PAGEUP]:
                keypress_delay = 0.1
                if model.part_selected:
                    model.edit_part(mouse_pos, "layer_up")
            elif key_press[pygame.K_PAGEDOWN]:
                keypress_delay = 0.1
                if model.part_selected:
                    model.edit_part(mouse_pos, "layer_down")

        if mouse_timer != 0:  # player click mouse once before
            mouse_timer += ui_dt  # increase timer for mouse click using real time
            if mouse_timer >= 0.3:  # time pass 0.3 second no longer count as double click
                mouse_timer = 0

        if keypress_delay != 0:  # player click mouse once before
            keypress_delay += ui_dt  # increase timer for mouse click using real time
            if keypress_delay >= 0.3:  # time pass 0.3 second no longer count as double click
                keypress_delay = 0

        if mouse_left_up:
            if popup_list_box in ui:
                if popup_list_box.rect.collidepoint(mouse_pos):
                    popup_click = True
                    for index, name in enumerate(popup_namegroup):  # click on popup list
                        if name.rect.collidepoint(mouse_pos):
                            if popup_list_box.action == "part_side":
                                direction_part_button.change_text(name.name)
                                if model.part_selected:
                                    model.edit_part(mouse_pos, "direction_" + name.name)
                            elif popup_list_box.action == "part_select":
                                model.edit_part(mouse_pos, "part_" + name.name)
                            elif popup_list_box.action == "race_select":
                                model.edit_part(mouse_pos, "race_" + name.name)
                            elif "person" in popup_list_box.action:
                                p_body_helper.change_p_type(name.name, player_change=True)
                                p_selector.change_name(name.name)
                            elif "armour" in popup_list_box.action:
                                model.edit_part(mouse_pos, popup_list_box.action[0:3] + "armour_" + name.name)
                                armour_selector.change_name(name.name)
                            elif "eye" in popup_list_box.action:
                                eye_selector.change_name("Eye: " + name.name)
                                model.edit_part(mouse_pos, popup_list_box.action[0:3] + "eye_" + name.name)
                            elif "mouth" in popup_list_box.action:
                                mouth_selector.change_name("Mouth: " + name.name)
                                model.edit_part(mouse_pos, popup_list_box.action[0:3] + "mouth_" + name.name)
                            elif popup_list_box.action == "animation_select":
                                if animation_name != name.name:
                                    change_animation(name.name)
                            elif popup_list_box.action == "animation_side":
                                direction_button.change_text(name.name)
                                current_frame = 0
                                anim.show_frame = current_frame
                                model.side = direction_list.index(name.name)
                                model.read_animation(animation_name, new_size=False)
                                reload_animation(anim, model)
                            for this_name in popup_namegroup:  # remove name list
                                this_name.kill()
                                del this_name
                            ui.remove(popup_list_box, popup_list_box.scroll)
                            current_popup_row = 0  # reset row

                elif popup_list_box.scroll.rect.collidepoint(mouse_pos):  # scrolling on list
                    popup_click = True
                    new_row = popup_list_box.scroll.player_input(mouse_pos)
                    if new_row is not None:
                        current_popup_row = new_row
                        setup_list(menu.NameList, current_popup_row, popup_list_box.namelist, popup_namegroup,
                                   popup_list_box, ui, screen_scale, layer=19)

                else:  # click other stuffs
                    for this_name in popup_namegroup:  # remove name list
                        this_name.kill()
                        del this_name
                    ui.remove(popup_list_box, popup_list_box.scroll)

            if popup_click is False:  # button that can be clicked even when animation playing
                if play_animation_button.rect.collidepoint(mouse_pos):
                    if play_animation_button.current_option == 0:
                        play_animation_button.change_option(1)  # start playing animation
                        play_animation = True
                    else:
                        play_animation_button.change_option(0)  # stop animation
                        play_animation = False
                        model.edit_part(None, "change")

                elif grid_button.rect.collidepoint(mouse_pos):
                    if grid_button.current_option == 0:  # remove grid
                        grid_button.change_option(1)
                        showroom.grid = False
                    else:
                        grid_button.change_option(0)
                        showroom.grid = True

                elif point_edit_button.rect.collidepoint(mouse_pos):
                    if point_edit_button.current_option == 0:
                        point_edit_button.change_option(1)  # use center point for edit
                    else:
                        point_edit_button.change_option(0)  # use joint point for edit
                    point_edit = point_edit_button.current_option

                elif joint_button.rect.collidepoint(mouse_pos):
                    if joint_button.current_option == 0:  # remove joint sprite
                        joint_button.change_option(1)
                        show_joint = True
                    else:  # stop animation
                        joint_button.change_option(0)
                        show_joint = False

                elif anim_prop_list_box.scroll.rect.collidepoint(mouse_pos):  # scrolling on list
                    new_row = anim_prop_list_box.scroll.player_input(mouse_pos)
                    if new_row is not None:
                        current_anim_row = new_row
                        setup_list(menu.NameList, current_anim_row, anim_prop_list_box.namelist, anim_prop_namegroup,
                                   anim_prop_list_box, ui, screen_scale, layer=9, old_list=anim_property_select)

                elif frame_prop_list_box.scroll.rect.collidepoint(mouse_pos):  # scrolling on list
                    new_row = frame_prop_list_box.scroll.player_input(mouse_pos)
                    if new_row is not None:
                        current_frame_row = new_row
                        setup_list(menu.NameList, current_frame_row, frame_prop_list_box.namelist[current_frame], frame_prop_namegroup,
                                   frame_prop_list_box, ui, screen_scale, layer=9, old_list=frame_property_select[current_frame])

                elif anim_prop_list_box.rect.collidepoint(mouse_pos) or frame_prop_list_box.rect.collidepoint(mouse_pos):
                    namegroup = anim_prop_namegroup  # click on animation property list
                    list_box = anim_prop_list_box
                    select_list = anim_property_select
                    namelist = list_box.namelist
                    naming = "anim"
                    if frame_prop_list_box.rect.collidepoint(mouse_pos):  # click on frame property list
                        namegroup = frame_prop_namegroup
                        list_box = frame_prop_list_box
                        select_list = frame_property_select[current_frame]
                        namelist = list_box.namelist[current_frame]
                        naming = "frame"

                    for index, name in enumerate(namegroup):
                        if name.rect.collidepoint(mouse_pos):
                            if name.name == "Custom":
                                text_input_popup = ("text_input", "new_anim_prop")
                                input_ui.change_instruction("Custom Property:")
                                ui.add(input_ui_popup)
                            elif "effect_" in name.name:
                                if name.name[-1] == "_" or name.name[-1].isdigit():  # effect that need number value
                                    if name.selected is False:
                                        if "colour" not in name.name:
                                            text_input_popup = ("text_input", naming + "_prop_num_" + name.name)
                                            input_ui.change_instruction("Input Number Value:")
                                            ui.add(input_ui_popup)
                                        else:
                                            text_input_popup = ("text_input", naming + "_prop_colour_" + name.name)
                                            ui.add(colour_ui_popup)
                                elif name.selected is False:  # effect that no need input
                                    select_list.append(name.name)
                                    setup_list(menu.NameList, current_frame_row, namelist, namegroup,
                                               list_box, ui, screen_scale, layer=9, old_list=select_list)
                                    reload_animation(anim, model)
                                    property_to_pool_data(naming)

                                if name.selected:  # unselected property
                                    name.select()
                                    select_list.remove(name.name)
                                    property_to_pool_data(naming)
                                    reload_animation(anim, model)

                            else:
                                name.select()
                                if name.selected:
                                    select_list.append(name.name)
                                else:
                                    select_list.remove(name.name)
                                property_to_pool_data(naming)

        if play_animation:
            current_frame = int(anim.show_frame)
        else:
            dt = 0
            if popup_click is False:  # button that can't be clicked even when animation playing
                if mouse_left_up:
                    if clear_button.rect.collidepoint(mouse_pos):
                        model.edit_part(mouse_pos, "clear")

                    elif default_button.rect.collidepoint(mouse_pos):
                        model.edit_part(mouse_pos, "default")

                    elif speed_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("text_input", "change_speed")
                        input_ui.change_instruction("Input Speed Number Value:")
                        ui.add(input_ui_popup)

                    elif all_copy_button.rect.collidepoint(mouse_pos):
                        copy_list = []
                        for frame in model.frame_list:
                            frame_item = {}
                            for key, value in frame.items():
                                if type(value) != list:
                                    frame_item[key] = value
                                else:
                                    frame_item[key] = value.copy()
                            copy_list.append(frame_item)

                    elif all_paste_button.rect.collidepoint(mouse_pos):
                        if copy_list:
                            for frame_index, frame in enumerate(copy_list):
                                model.frame_list[frame_index] = {key: value.copy() if type(value) == list else value for key, value in frame.items()}
                            model.read_animation(animation_name, old=True)
                            reload_animation(anim, model)

                    elif frame_copy_button.rect.collidepoint(mouse_pos):
                        copy_press = True

                    elif frame_paste_button.rect.collidepoint(mouse_pos):
                        paste_press = True

                    elif part_copy_button.rect.collidepoint(mouse_pos):
                        part_copy_press = True

                    elif part_paste_button.rect.collidepoint(mouse_pos):
                        part_paste_press = True

                    elif p_all_button.rect.collidepoint(mouse_pos):
                        part_change = p_body_helper.ui_type + "_"
                        for part in list(model.rect_part_list.keys()):
                            if part_change in part:
                                if ctrl_press is False:  # add parts
                                    model.click_part(mouse_pos, True, ctrl_press, part)
                                else:
                                    model.click_part(mouse_pos, False, ctrl_press, part)
                            elif part_change not in part and shift_press is False and ctrl_press is False:  # remove other parts
                                model.click_part(mouse_pos, False, True, part)
                        for helper in helper_list:
                            helper.select_part(None, False, False)  # reset first
                            for part in model.part_selected:
                                if list(model.rect_part_list.keys())[part] in helper.rect_part_list:
                                    helper.select_part(mouse_pos, True, False, list(model.rect_part_list.keys())[part])

                    elif all_button.rect.collidepoint(mouse_pos):
                        for part in list(model.rect_part_list.keys()):
                            if ctrl_press is False:  # add all parts
                                model.click_part(mouse_pos, True, ctrl_press, part)
                            else:
                                model.click_part(mouse_pos, False, ctrl_press, part)
                        for helper in helper_list:
                            for part in model.part_selected:
                                if list(model.rect_part_list.keys())[part] in helper.rect_part_list:
                                    helper.select_part(mouse_pos, True, False, list(model.rect_part_list.keys())[part])

                    elif activate_button.rect.collidepoint(mouse_pos):
                        for strip_index, strip in enumerate(filmstrips):
                            if strip_index == current_frame:
                                if strip.activate is False:
                                    strip.activate = True
                                    activate_list[strip_index] = True
                                    activate_button.change_option(0)
                                    strip.add_strip(change=False)
                                else:
                                    strip.activate = False
                                    activate_list[strip_index] = False
                                    activate_button.change_option(1)
                                    strip.add_strip(change=False)
                                anim_to_pool(animation_name, current_pool, model, activate_list)
                                break

                    elif undo_button.rect.collidepoint(mouse_pos):
                        undo_press = True

                    elif redo_button.rect.collidepoint(mouse_pos):
                        redo_press = True

                    elif rename_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("text_input", "new_name")
                        input_ui.change_instruction("Rename Animation:")
                        input_box.text_start(animation_name)
                        ui.add(input_ui_popup)

                    elif duplicate_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("confirm_input", "duplicate_animation")
                        input_ui.change_instruction("Duplicate Current Animation?")
                        ui.add(input_ui_popup)

                    elif export_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("confirm_input", "export_animation")
                        input_ui.change_instruction("Export to PNG Files?")
                        ui.add(input_ui_popup)

                    elif flip_hori_button.rect.collidepoint(mouse_pos):
                        model.edit_part(mouse_pos, "flip1")

                    elif flip_vert_button.rect.collidepoint(mouse_pos):
                        model.edit_part(mouse_pos, "flip2")

                    elif reset_button.rect.collidepoint(mouse_pos):
                        model.edit_part(mouse_pos, "reset")

                    elif direction_button.rect.collidepoint(mouse_pos):
                        popup_list_open(popup_list_box, popup_namegroup, ui, "animation_side",
                                        direction_button.rect.bottomleft, direction_list, "top", screen_scale)

                    elif direction_part_button.rect.collidepoint(mouse_pos):
                        if race_part_button.text != "":
                            popup_list_open(popup_list_box, popup_namegroup, ui, "part_side",
                                            direction_part_button.rect.topleft, direction_list, "bottom", screen_scale)

                    elif part_selector.rect.collidepoint(mouse_pos):
                        if direction_part_button.text != "" and race_part_button.text != "":
                            current_part = list(model.animation_part_list[current_frame].keys())[model.part_selected[-1]]
                            try:
                                if any(ext in current_part for ext in p_list):
                                    selected_part = current_part[3:]
                                    if selected_part[0:2] == "r_" or selected_part[0:2] == "l_":
                                        selected_part = selected_part[2:]
                                    part_list = list(gen_body_sprite_pool[race_part_button.text][direction_part_button.text][selected_part].keys())
                                elif "effect" in current_part:
                                    part_list = list(effect_sprite_pool[race_part_button.text][direction_part_button.text].keys())
                                elif "special" in current_part:
                                    part_list = list(
                                        gen_body_sprite_pool[race_part_button.text][direction_part_button.text]["special"].keys())
                            except KeyError:  # look at weapon next
                                selected_part = race_part_button.text
                                part_list = list(gen_weapon_sprite_pool[selected_part][direction_part_button.text].keys())
                            popup_list_open(popup_list_box, popup_namegroup, ui, "part_select",
                                            part_selector.rect.topleft, part_list, "bottom", screen_scale)

                    elif p_selector.rect.collidepoint(mouse_pos):
                        popup_list_open(popup_list_box, popup_namegroup, ui, "person_select",
                                        p_selector.rect.topleft, p_list, "bottom", screen_scale)
                    elif armour_selector.rect.collidepoint(mouse_pos):
                        armour_part_list = []
                        for item in list(gen_armour_sprite_pool[model.p_race[p_body_helper.ui_type]].keys()):
                            for armour in gen_armour_sprite_pool[model.p_race[p_body_helper.ui_type]][item]:
                                armour_part_list.append(item + "/" + armour)
                        part_list = ["None"] + armour_part_list
                        popup_list_open(popup_list_box, popup_namegroup, ui, p_body_helper.ui_type + "_armour_select",
                                        armour_selector.rect.topleft, part_list, "bottom", screen_scale)

                    elif eye_selector.rect.collidepoint(mouse_pos):
                        part_list = ["Any"] + list(gen_body_sprite_pool[model.p_race[p_body_helper.ui_type]][
                                                       model.bodypart_list[current_frame][p_body_helper.ui_type + "_head"][1]]["eye"].keys())
                        popup_list_open(popup_list_box, popup_namegroup, ui, p_body_helper.ui_type + "_eye_select",
                                        eye_selector.rect.topleft, part_list, "bottom", screen_scale)

                    elif mouth_selector.rect.collidepoint(mouse_pos):
                        part_list = ["Any"] + list(gen_body_sprite_pool[model.p_race[p_body_helper.ui_type]][
                                                       model.bodypart_list[current_frame][p_body_helper.ui_type + "_head"][1]]["mouth"].keys())
                        popup_list_open(popup_list_box, popup_namegroup, ui, p_body_helper.ui_type + "_mouth_select",
                                        mouth_selector.rect.topleft, part_list, "bottom", screen_scale)

                    elif race_part_button.rect.collidepoint(mouse_pos):
                        if model.part_selected:
                            current_part = list(model.rect_part_list.keys())[model.part_selected[-1]]
                            if "weapon" in current_part:
                                part_list = list(gen_weapon_sprite_pool)
                            elif "effect" in current_part:
                                part_list = list(effect_sprite_pool)
                            else:
                                part_list = list(gen_body_sprite_pool.keys())
                            popup_list_open(popup_list_box, popup_namegroup, ui, "race_select",
                                            race_part_button.rect.topleft, part_list, "bottom", screen_scale)

                    elif new_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("text_input", "new_animation")
                        input_ui.change_instruction("New Animation Name:")
                        ui.add(input_ui_popup)

                    elif save_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("confirm_input", "save_animation")
                        input_ui.change_instruction("Save All Animation?")
                        ui.add(input_ui_popup)

                    elif delete_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("confirm_input", "del_animation")
                        input_ui.change_instruction("Delete This Animation?")
                        ui.add(input_ui_popup)

                    elif size_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("text_input", "change_size")
                        input_ui.change_instruction("Input Size Number:")
                        ui.add(input_ui_popup)

                    elif animation_selector.rect.collidepoint(mouse_pos):
                        popup_list_open(popup_list_box, popup_namegroup, ui, "animation_select",
                                        animation_selector.rect.bottomleft,
                                        [item for item in current_pool[direction]], "top", screen_scale,
                                        current_row=list(current_pool[direction].keys()).index(animation_name))
                        current_popup_row = list(current_pool[direction].keys()).index(animation_name)

                    else:  # click on other stuff
                        for strip_index, strip in enumerate(filmstrips):  # click on frame film list
                            if strip.rect.collidepoint(mouse_pos) and current_frame != strip_index:  # click new frame
                                current_frame = strip_index
                                anim.show_frame = current_frame
                                model.edit_part(mouse_pos, "change")
                                current_frame_row = 0
                                setup_list(menu.NameList, current_frame_row, frame_prop_list_box.namelist[current_frame], frame_prop_namegroup,
                                           frame_prop_list_box, ui, screen_scale, layer=9,
                                           old_list=frame_property_select[current_frame])  # change frame property list
                                for index, helper in enumerate(helper_list):
                                    helper.select_part(None, False, False)
                                if strip.activate:
                                    activate_button.change_option(0)
                                else:
                                    activate_button.change_option(1)
                                break

                        helper_click = False
                        for index, helper in enumerate(helper_list):  # click on helper
                            if helper.rect.collidepoint(mouse_pos):
                                helper_click = helper
                                break
                        if helper_click is not False:  # to avoid removing selected part when click other stuff
                            mouse_pos = pygame.Vector2((mouse_pos[0] - helper_click.rect.topleft[0]) / screen_size[0] * 1000,
                                                       (mouse_pos[1] - helper_click.rect.topleft[1]) / screen_size[1] * 1000)
                            helper_click.select_part(mouse_pos, shift_press, ctrl_press)
                            model.part_selected = []  # clear old list first
                            if shift_press is False and ctrl_press is False:  # remove selected part in other helpers
                                for index, helper in enumerate(helper_list):
                                    if helper != helper_click:
                                        helper.select_part(None, False, True)
                            if helper_click.part_selected:
                                for part in helper_click.part_selected:
                                    model.click_part(mouse_pos, True, False, part)

                if copy_press:
                    copy_part_frame = {key: (value[:].copy() if type(value) == list else value) for key, value in
                                       model.bodypart_list[current_frame].items()}
                    copy_animation_frame = {key: (value[:].copy() if value is not None else value) for key, value in
                                            model.animation_part_list[current_frame].items()}
                    copy_name_frame = {key: (value[:].copy() if value is not None else value) for key, value in
                                       model.part_name_list[current_frame].items()}

                elif paste_press:
                    if copy_animation_frame is not None:
                        model.bodypart_list[current_frame] = {key: (value[:].copy() if type(value) == list else value) for key, value in
                                                              copy_part_frame.items()}
                        model.animation_part_list[current_frame] = {key: (value[:].copy() if value is not None else value) for key, value in
                                                                    copy_animation_frame.items()}
                        model.part_name_list[current_frame] = {key: (value[:].copy() if value is not None else value) for key, value in
                                                               copy_name_frame.items()}
                        model.edit_part(mouse_pos, "change")

                elif part_copy_press:
                    if model.part_selected:
                        copy_part = {key: (value[:].copy() if type(value) == list else value) for key, value in
                                     model.bodypart_list[current_frame].items()}
                        copy_animation = {key: (value[:].copy() if value is not None else value) for key, value in
                                          model.animation_part_list[current_frame].items()}
                        copy_name = {key: (value[:].copy() if value is not None else value) for key, value in
                                     model.part_name_list[current_frame].items()}

                        # keep only selected one
                        copy_part = {item: copy_part[item] for item in copy_part.keys() if
                                     item in model.rect_part_list and list(model.rect_part_list.keys()).index(item) in model.part_selected}
                        copy_animation = {item: copy_animation[item] for index, item in enumerate(copy_animation.keys()) if
                                          index in model.part_selected}
                        copy_name = {item: copy_name[item] for index, item in enumerate(copy_name.keys()) if index in model.part_selected}

                elif part_paste_press:
                    if copy_part is not None:
                        model.edit_part(mouse_pos, "paste")

                elif undo_press:
                    if current_history != 0:
                        current_history -= 1
                        model.edit_part(None, "undo")

                elif redo_press:
                    if len(animation_history) - 1 > current_history:
                        current_history += 1
                        model.edit_part(None, "redo")

                if showroom.rect.collidepoint(mouse_pos):  # mouse at showroom
                    new_mouse_pos = pygame.Vector2((mouse_pos[0] - showroom.rect.topleft[0]) / screen_size[0] * 500 * model.size,
                                                   (mouse_pos[1] - showroom.rect.topleft[1]) / screen_size[1] * 500 * model.size)
                    if mouse_left_up:  # left click on showroom
                        model.click_part(new_mouse_pos, shift_press, ctrl_press)
                        for index, helper in enumerate(helper_list):
                            helper.select_part(None, shift_press, ctrl_press)
                            if model.part_selected:
                                for part in model.part_selected:
                                    if list(model.rect_part_list.keys())[part] in helper.rect_part_list:
                                        helper.select_part(mouse_pos, shift_press, ctrl_press, list(model.rect_part_list.keys())[part])
                    if mouse_wheel_up or mouse_wheel_down:
                        model.edit_part(new_mouse_pos, "rotate")
                    elif mouse_right_up or mouse_right_down:
                        if keypress_delay == 0:
                            model.edit_part(new_mouse_pos, "place")
                            keypress_delay = 0.1

            if model.part_selected:
                part = model.part_selected[-1]
                if model.animation_part_list[current_frame] is not None and \
                        list(model.rect_part_list.keys())[part] in list(model.animation_part_list[current_frame].keys()):
                    name_text = model.part_name_list[current_frame][list(model.rect_part_list.keys())[part]]
                    if name_text is None:
                        name_text = ["", "", ""]
                    race_part_button.change_text(name_text[0])
                    direction_part_button.change_text(name_text[1])
                    part_selector.change_name(name_text[2])
                else:
                    race_part_button.change_text("")
                    direction_part_button.change_text("")
                    part_selector.change_name("")
            elif race_part_button.text != "":
                race_part_button.change_text("")
                direction_part_button.change_text("")
                part_selector.change_name("")
    else:  # input box function
        dt = 0
        if (input_ok_button in ui and input_ok_button.event) or (colour_ok_button in ui and colour_ok_button.event) or \
                key_press[pygame.K_RETURN] or key_press[pygame.K_KP_ENTER]:
            input_ok_button.event = False
            colour_ok_button.event = False

            if text_input_popup[1] == "new_animation":
                if input_box.text not in current_pool[0]:  # no existing name already
                    animation_name = input_box.text
                    animation_selector.change_name(animation_name)
                    current_frame = 0
                    model.edit_part(mouse_pos, "new")
                    change_animation(animation_name)

            elif text_input_popup[1] == "save_animation":
                anim_save_pool(current_pool, "generic", direction_list, anim_column_header)

            elif text_input_popup[1] == "new_name":
                old_name = animation_name
                if input_box.text not in current_pool[0]:  # no existing name already
                    animation_name = input_box.text
                    animation_selector.change_name(animation_name)
                    anim_to_pool(animation_name, current_pool, model, activate_list, activate_list, replace=old_name)

            elif text_input_popup[1] == "export_animation":
                save_num = 1
                for index, frame in enumerate(anim.frames):
                    if activate_list[index]:
                        pygame.image.save(frame, animation_name + "_" + str(save_num) + ".png")
                        save_num += 1

            elif text_input_popup[1] == "duplicate_animation":
                old_name = animation_name
                last_char = str(1)
                if animation_name + "(copy" + last_char + ")" in current_pool[0]:  # copy exist
                    while animation_name + "(copy" + last_char + ")" in current_pool[0]:
                        last_char = str(int(last_char) + 1)
                elif "(copy" in animation_name and animation_name[-2].isdigit() and animation_name[-1] == ")":
                    last_char = int(animation_name[-2]) + 1
                animation_name = animation_name + "(copy" + last_char + ")"
                animation_selector.change_name(animation_name)
                anim_to_pool(animation_name, current_pool, model, activate_list, activate_list, duplicate=old_name)

            elif text_input_popup[1] == "del_animation":
                anim_del_pool(current_pool, animation_name)
                if len(current_pool[0]) == 0:  # no animation left, create empty one
                    animation_name = "empty"
                    animation_selector.change_name(animation_name)
                    current_frame = 0
                    model.edit_part(mouse_pos, "new")
                else:  # reset to the first animation
                    change_animation(list(current_pool[0].keys())[0])

            elif text_input_popup[1] == "change_speed":
                if input_box.text.isdigit():
                    new_speed = int(input_box.text)
                    speed_button.change_text("Speed: " + input_box.text)
                    anim.speed_ms = (500 / new_speed) / 1000

            elif text_input_popup[1] == "new_anim_prop":  # custom animation property
                if input_box.text not in anim_prop_list_box.namelist:
                    anim_prop_list_box.namelist.insert(-1, input_box.text)
                if input_box.text not in anim_property_select:
                    anim_property_select.append(input_box.text)
                setup_list(menu.NameList, current_anim_row, anim_prop_list_box.namelist, anim_prop_namegroup,
                           anim_prop_list_box, ui, screen_scale, layer=9, old_list=anim_property_select)
                select_list = anim_property_select
                property_to_pool_data("anim")

            elif text_input_popup[1] == "new_frame_prop":  # custom frame property
                if input_box.text not in frame_prop_list_box.namelist:
                    frame_prop_list_box.namelist[current_frame].insert(-1, input_box.text)
                if input_box.text not in frame_property_select[current_frame]:
                    frame_property_select[current_frame].append(input_box.text)
                setup_list(menu.NameList, current_frame_row, frame_prop_list_box.namelist[current_frame], frame_prop_namegroup,
                           frame_prop_list_box, ui, screen_scale, layer=9, old_list=frame_property_select[current_frame])
                select_list = frame_property_select[current_frame]
                property_to_pool_data("frame")

            elif "_prop_num" in text_input_popup[1] and (input_box.text.isdigit() or "." in input_box.text and re.search("[a-zA-Z]",
                                                                                                                         input_box.text) is None):  # add property that need value
                namegroup = anim_prop_namegroup  # click on animation property list
                list_box = anim_prop_list_box
                namelist = list_box.namelist
                select_list = anim_property_select
                naming = "anim"
                if "frame" in text_input_popup[1]:  # click on frame property list
                    namegroup = frame_prop_namegroup
                    list_box = frame_prop_list_box
                    namelist = list_box.namelist[current_frame]
                    select_list = frame_property_select[current_frame]
                    naming = "frame"
                for name in namelist:
                    if name in (text_input_popup[1]):
                        index = namelist.index(name)
                        namelist[index] = name[0:name.rfind("_") + 1] + input_box.text
                        select_list.append(name[0:name.rfind("_") + 1] + input_box.text)
                        setup_list(menu.NameList, current_frame_row, namelist, namegroup,
                                   list_box, ui, screen_scale, layer=9, old_list=select_list)
                        reload_animation(anim, model)
                        property_to_pool_data(naming)
                        break

            elif "_prop_colour" in text_input_popup[1] and re.search("[a-zA-Z]", colour_input_box.text) is None and \
                    colour_input_box.text.count(",") >= 2:  # add colour related property
                naming = "anim"
                if "frame" in text_input_popup[1]:  # click on frame property list
                    naming = "frame"
                colour = colour_input_box.text.replace(" ", "")
                colour = colour.replace(",", ".")
                for name in frame_prop_list_box.namelist[current_frame]:
                    if name in (text_input_popup[1]):
                        index = frame_prop_list_box.namelist[current_frame].index(name)
                        frame_prop_list_box.namelist[current_frame][index] = name[0:name.rfind("_") + 1] + colour
                        frame_property_select[current_frame].append(name[0:name.rfind("_") + 1] + colour)
                        setup_list(menu.NameList, current_frame_row, frame_prop_list_box.namelist[current_frame], frame_prop_namegroup,
                                   frame_prop_list_box, ui, screen_scale, layer=9, old_list=frame_property_select[current_frame])
                        reload_animation(anim, model)
                        property_to_pool_data(naming)
                        break

            elif text_input_popup[1] == "change_size" and input_box.text.isdigit():
                model.frame_list[0]["size"] = int(input_box.text)
                model.read_animation(animation_name, old=True)
                reload_animation(anim, model)

            elif text_input_popup[1] == "quit":
                pygame.time.wait(1000)
                if pygame.mixer:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                pygame.quit()

            input_box.text_start("")
            text_input_popup = (None, None)
            ui.remove(*input_ui_popup, *colour_ui_popup)

        elif colour_wheel in ui and mouse_left_up and colour_wheel.rect.collidepoint(mouse_pos):
            colour = str(colour_wheel.get_colour())
            colour = colour[1:-1]  # remove bracket ()
            colour_input_box.text_start(colour[:colour.rfind(",")])  # keep only 3 first colour value not transparent

        elif (input_cancel_button in ui and input_cancel_button.event) or (colour_cancel_button in ui and colour_cancel_button.event) or input_esc:
            input_cancel_button.event = False
            colour_cancel_button.event = False
            input_box.text_start("")
            text_input_popup = (None, None)
            ui.remove(*input_ui_popup, *confirm_ui_popup, *colour_ui_popup)

    ui.update(mouse_pos, mouse_left_up, mouse_left_down)
    anim.play(showroom.image, (0, 0), activate_list)
    for strip_index, strip in enumerate(filmstrips):
        if strip_index == current_frame:
            strip.selected(True)
            break
    pen.fill((150, 150, 150))
    ui.draw(pen)

    pygame.display.update()
    clock.tick(60)
