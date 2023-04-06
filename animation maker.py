import csv
import os
import random
import re
import sys
import time
from pathlib import Path

import pygame
from math import atan2, degrees, radians
from PIL import Image, ImageFilter, ImageEnhance

from gamescript import datastat, menu, battleui, popup
from gamescript.common import utility

main_dir = os.path.split(os.path.abspath(__file__))[0]
current_dir = main_dir + "/animation maker"  # animation maker folder
sys.path.insert(1, current_dir)

from script import colour, listpopup, pool  # keep here as it need to get sys path insert

rotation_xy = utility.rotation_xy
load_image = utility.load_image
load_images = utility.load_images
load_base_button = utility.load_base_button
stat_convert = datastat.stat_convert

apply_colour = colour.apply_sprite_colour
setup_list = listpopup.setup_list
list_scroll = listpopup.list_scroll
popup_list_open = listpopup.popup_list_open
read_anim_data = pool.read_anim_data
read_joint_data = pool.read_joint_data
anim_to_pool = pool.anim_to_pool
anim_save_pool = pool.anim_save_pool
anim_del_pool = pool.anim_del_pool

default_sprite_size = (200, 200)

screen_size = (1100, 900)
screen_scale = (1, 1)

pygame.init()
pen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Animation Maker")  # set the self name on program border/tab
pygame.mouse.set_visible(True)  # set mouse as visible

max_person = 4
max_frame = 22
p_list = tuple(["p" + str(p) for p in range(1, max_person + 1)])
part_column_header = ["head", "eye", "mouth", "body", "r_arm_up", "r_arm_low", "r_hand", "l_arm_up",
                      "l_arm_low", "l_hand", "r_leg", "r_foot", "l_leg", "l_foot", "main_weapon", "sub_weapon",
                      "special_1", "special_2", "special_3", "special_4", "special_5"]
anim_column_header = ["Name"]
for p in range(1, max_person + 1):
    p_name = "p" + str(p) + "_"
    anim_column_header += [p_name + item for item in part_column_header]
anim_column_header += ["effect_1", "effect_2", "effect_3", "effect_4", "dmg_effect_1", "dmg_effect_2", "dmg_effect_3",
                       "dmg_effect_4",
                       "size", "frame_property", "animation_property"]  # For csv saving and accessing
frame_property_list = ["hold", "p1_fix_main_weapon", "p1_fix_sub_weapon", "p2_fix_main_weapon", "p2_fix_sub_weapon",
                       "p3_fix_main_weapon", "p3_fix_sub_weapon", "p4_fix_main_weapon", "p4_fix_sub_weapon",
                       "p1_no_helmet", "p2_no_helmet", "p3_no_helmet", "p4_no_helmet", "play_time_mod_", "effect_blur_",
                       "effect_contrast_", "effect_brightness_",
                       "effect_fade_", "effect_grey", "effect_colour_"]  # starting property list

anim_property_list = ["interuptrevert", "norestart"] + frame_property_list


"""Property explanation:

hold: Frame or entire animation can be played until release from holding input
p(number)_fix_main_weapon or p(number)_fix_sub_weapon: Use center point instead weapon joint position and place them
at the specified position instead of automatically at user's hand (main = right hand, sub = left hand) or back for sheath
play_time_mod_: Value of play time modification, higher mean longer play time
effect_blur_: Put blur effect on entire frame based on the input value
effect_contrast_: Put colour contrast effect on entire frame based on the input value
effect_brightness_: Change brightness of entire frame based on the input value
effect_fade_: Put fade effect on entire frame based on the input value
effect_grey: Put greyscale effect on entire frame
effect_colour_: Colourise entire frame based on the input value
"""


def reload_animation(animation, char):
    """Reload animation frames"""
    frames = [pygame.transform.smoothscale(this_image, showroom.size) for this_image in char.animation_list if
              this_image is not None]
    for frame_index in range(max_frame):
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
                data = pygame.image.tostring(frames[frame_index],
                                             "RGBA")  # convert image to string data for filtering effect
                surface = Image.frombytes("RGBA", frames[frame_index].get_size(), data)  # use PIL to get image data
                alpha = surface.split()[-1]  # save alpha
                if "blur" in prop:
                    surface = surface.filter(
                        ImageFilter.GaussianBlur(
                            radius=float(prop[prop.rfind("_") + 1:])))  # blur Image (or apply other filter in future)
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
                surface = pygame.image.fromstring(surface, frames[frame_index].get_size(),
                                                  "RGBA")  # convert image back to a pygame surface
                if "colour" in prop:
                    colour = prop[prop.rfind("_") + 1:]
                    colour = [int(this_colour) for this_colour in colour.split(".")]
                    surface = apply_colour(surface, colour)
                frames[frame_index] = surface
        filmstrip_list[frame_index].add_strip(frames[frame_index])
    animation.reload(frames)
    armour_selector.change_name(char.armour[p_body_helper.ui_type + "_armour"])
    face = [char.bodypart_list[current_frame][p_body_helper.ui_type + "_eye"],
            char.bodypart_list[current_frame][p_body_helper.ui_type + "_mouth"]]
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
                part = list(char.mask_part_list.keys())[part]
                helper.select_part((0, 0), True, False, specific_part=part)
        else:
            helper.select_part(None, shift_press, False)


def property_to_pool_data(which):
    if which == "anim":
        for frame in model.frame_list:
            frame["animation_property"] = select_list
        if anim_prop_list_box.rect.collidepoint(mouse_pos):
            for frame in range(len(current_pool[animation_race][animation_name])):
                current_pool[animation_race][animation_name][frame]["animation_property"] = select_list
    elif which == "frame":
        model.frame_list[current_frame]["frame_property"] = select_list
        current_pool[animation_race][animation_name][current_frame]["frame_property"] = select_list


def change_animation_race(new_race):
    global animation_race

    animation_race = new_race
    change_animation(list(current_pool[animation_race].keys())[0])


def change_animation(new_name):
    global animation_name, current_frame, current_anim_row, current_frame_row, anim_property_select, frame_property_select
    anim_prop_list_box.namelist = anim_property_list + ["Custom"]  # reset property list
    anim_property_select = []
    frame_prop_list_box.namelist = [frame_property_list + ["Custom"] for _ in range(max_frame)]
    frame_property_select = [[] for _ in range(max_frame)]
    current_anim_row = 0
    current_frame_row = 0
    model.read_animation(new_name)
    if activate_list[current_frame] is False:
        current_frame = 0
    anim.show_frame = current_frame
    animation_name = new_name
    animation_selector.change_name(new_name)
    reload_animation(anim, model)
    anim_prop_list_box.scroll.change_image(new_row=0, row_size=len(anim_prop_list_box.namelist))
    frame_prop_list_box.scroll.change_image(new_row=0, row_size=len(frame_prop_list_box.namelist[current_frame]))
    model.clear_history()


def change_frame_process():
    global current_frame_row
    anim.show_frame = current_frame
    model.edit_part(mouse_pos, "change")
    current_frame_row = 0
    setup_list(menu.NameList, current_frame_row, frame_prop_list_box.namelist[current_frame], frame_prop_namegroup,
               frame_prop_list_box, ui, screen_scale, layer=9,
               old_list=frame_property_select[current_frame])  # change frame property list


race_list = []
for x in Path(os.path.join(main_dir, "data", "sprite", "subunit")).iterdir():  # grab race with sprite
    if os.path.normpath(x).split(os.sep)[-1] != "weapon":  # exclude weapon as race
        race_list.append(os.path.normpath(x).split(os.sep)[-1])

animation_pool_data, part_name_header = read_anim_data(anim_column_header)
weapon_joint_list = read_joint_data()

animation_race = "Human"

try:
    animation_name = list(animation_pool_data[animation_race].keys())[0]
except:
    animation_name = None

with open(os.path.join(main_dir, "data", "sprite", "colour_rgb.csv"), encoding="utf-8",
          mode="r") as edit_file:
    rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
    rd = [row for row in rd]
    header = rd[0]
    colour_list = {}
    int_column = ["red", "green", "blue"]  # value in list only
    int_column = [index for index, item in enumerate(header) if item in int_column]
    for row_index, row in enumerate(rd):
        if row_index > 0:
            for n, i in enumerate(row):
                row = stat_convert(row, n, i, int_column=int_column)
                key = row[0].split("/")[0]
            colour_list[key] = row[1:]

gen_body_sprite_pool = {}
for race in race_list:
    if race != "":
        try:
            [os.path.split(
                os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):])) for
             x in Path(os.path.join(main_dir, "data", "sprite", "subunit", race)).iterdir() if
             x.is_dir()]  # check if race folder exist
            gen_body_sprite_pool[race] = {}
            part_folder = Path(os.path.join(main_dir, "data", "sprite", "subunit", race))
            subdirectories = [os.path.split(
                os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):]))
                              for x in part_folder.iterdir() if x.is_dir()]
            for folder in subdirectories:
                imgs = load_images(main_dir, screen_scale=screen_scale, subfolder=folder)
                gen_body_sprite_pool[race][folder[-1]] = imgs
        except FileNotFoundError:
            pass

race_list = [race for race in gen_body_sprite_pool if race != ""]  # get only race with existed folder and parts

gen_armour_sprite_pool = {}
for race in race_list:
    gen_armour_sprite_pool[race] = {}
    try:
        part_subfolder = Path(os.path.join(main_dir, "data", "sprite", "subunit", race, "armour"))
        subdirectories = [os.path.split(
            os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):])) for
                          x in part_subfolder.iterdir() if x.is_dir()]
        for subfolder in subdirectories:
            part_subsubfolder = Path(
                os.path.join(main_dir, "data", "sprite", "subunit", race, "armour", subfolder[-1]))
            subsubdirectories = [os.path.split(
                os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):]))
                                 for x in part_subsubfolder.iterdir() if x.is_dir()]
            if subfolder[-1] not in gen_armour_sprite_pool[race]:
                gen_armour_sprite_pool[race][subfolder[-1]] = {}
            for subsubfolder in subsubdirectories:
                if subsubfolder[-1] not in gen_armour_sprite_pool[race][subfolder[-1]]:
                    gen_armour_sprite_pool[race][subfolder[-1]][subsubfolder[-1]] = {}
                body_subsubfolder = Path(
                    os.path.join(main_dir, "data", "sprite", "subunit", race, "armour", subfolder[-1],
                                 subsubfolder[-1]))
                body_directories = [os.path.split(os.sep.join(
                    os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):])) for x in
                                    body_subsubfolder.iterdir() if x.is_dir()]
                for body_folder in body_directories:
                    imgs = load_images(main_dir, screen_scale=screen_scale,
                                       subfolder=("sprite", "subunit", race, "armour",
                                                  subfolder[-1], subsubfolder[-1], body_folder[-1]))
                    gen_armour_sprite_pool[race][subfolder[-1]][subsubfolder[-1]][body_folder[-1]] = imgs
    except FileNotFoundError:
        pass

gen_weapon_sprite_pool = {}
part_folder = Path(os.path.join(main_dir, "data", "sprite", "subunit", "weapon"))
subdirectories = [
    os.path.split(os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):]))
    for x in part_folder.iterdir() if x.is_dir()]
for folder in subdirectories:
    gen_weapon_sprite_pool[folder[-1]] = {}
    part_subfolder = Path(os.path.join(main_dir, "data", "sprite", "subunit", "weapon", folder[-1]))
    subsubdirectories = [os.path.split(
    os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):])) for x in
                     part_subfolder.iterdir() if x.is_dir()]
    imgs = load_images(main_dir, screen_scale=screen_scale,
                       subfolder=("sprite", "subunit", "weapon", folder[-1],
                                  "common"))  # use only common weapon

    gen_weapon_sprite_pool[folder[-1]] = imgs

effect_sprite_pool = {}
part_folder = Path(os.path.join(main_dir, "data", "sprite", "effect"))
subdirectories = [
    os.path.split(os.sep.join(os.path.normpath(x).split(os.sep)[os.path.normpath(x).split(os.sep).index("sprite"):]))
    for x in part_folder.iterdir() if x.is_dir()]
for folder in subdirectories:
    part_folder = Path(os.path.join(main_dir, "data", "sprite", "effect", folder[-1]))
    imgs = load_images(main_dir, screen_scale=screen_scale, subfolder=folder)
    effect_sprite_pool[folder[-1]] = imgs


class Showroom(pygame.sprite.Sprite):
    def __init__(self, size):
        """White space for showing off sprite and animation"""
        self._layer = 10
        pygame.sprite.Sprite.__init__(self)
        self.size = (int(size[0]), int(size[1]))
        self.image = pygame.Surface(self.size)
        self.image.fill((200, 200, 200))
        self.rect = self.image.get_rect(center=(screen_size[0] / 2, screen_size[1] / 2.35))
        self.grid = True

    def update(self, *args):
        self.image.fill((200, 200, 200))
        if self.grid:
            grid_width = self.image.get_width() / 10
            grid_height = self.image.get_height() / 10
            loop_colour = ((0, 0, 0), (0, 100, 50), (100, 50, 0), (100, 200, 200), (150, 0, 0),
                           (0, 150, 0), (0, 0, 150), (150, 0, 150), (0, 150, 150), (150, 150, 0))
            for loop in range(1, 10):
                pygame.draw.line(self.image, loop_colour[loop - 1], (grid_width * loop, 0),
                                 (grid_width * loop, self.image.get_height()))
                pygame.draw.line(self.image, loop_colour[loop - 1], (0, grid_height * loop),
                                 (self.image.get_width(), grid_height * loop))


class Filmstrip(pygame.sprite.Sprite):
    """animation sprite filmstrip"""
    base_image = None

    def __init__(self, pos):
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.image = self.base_image.copy()  # original no sprite
        self.base_image2 = self.base_image.copy()  # after add sprite but before activate or deactivate
        self.base_image3 = self.base_image2.copy()  # before adding selected corner
        self.rect = self.image.get_rect(topleft=self.pos)
        self.image_scale = (self.image.get_width() / 100, self.image.get_height() / 120)
        self.blit_image = None
        self.strip_rect = None
        self.activate = False

    def update(self, *args):
        self.image = self.base_image3.copy()

    def selected(self, select=False):
        self.image = self.base_image3.copy()
        select_colour = (200, 100, 100)
        if self.activate:
            select_colour = (150, 200, 100)
        if select:
            pygame.draw.rect(self.image, select_colour, (0, 0, self.image.get_width(), self.image.get_height()),
                             int(self.image.get_width() / 5))

    def add_strip(self, image=None, change=True):
        if change:
            self.image = self.base_image.copy()
            if image is not None:
                self.blit_image = pygame.transform.smoothscale(image.copy(), (
                int(100 * self.image_scale[0]), int(100 * self.image_scale[1])))
                self.strip_rect = self.blit_image.get_rect(
                    center=(self.image.get_width() / 2, self.image.get_height() / 2))
                self.image.blit(self.blit_image, self.strip_rect)
            self.base_image2 = self.image.copy()
        else:
            self.image = self.base_image2.copy()
        self.base_image3 = self.base_image2.copy()
        if self.activate is False:  # draw black corner and replace film dot
            pygame.draw.rect(self.base_image3, (0, 0, 0), (0, 0, self.image.get_width(), self.image.get_height()),
                             int(self.image.get_width() / 5))


class Button(pygame.sprite.Sprite):
    """Normal button"""

    def __init__(self, text, image, pos, description=None, font_size=20):
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(font_size * screen_scale[1]))
        self.image = image.copy()
        self.base_image = self.image.copy()
        self.description = description
        self.text = text
        self.pos = pos
        text_surface = self.font.render(str(text), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(int(self.image.get_width() / 2), int(self.image.get_height() / 2)))
        self.image.blit(text_surface, text_rect)
        self.rect = self.image.get_rect(center=self.pos)

    def change_text(self, text):
        if text != self.text:
            self.image = self.base_image.copy()
            self.text = text
            text_surface = self.font.render(self.text.capitalize(), True, (0, 0, 0))
            text_rect = text_surface.get_rect(
                center=(int(self.image.get_width() / 2), int(self.image.get_height() / 2)))
            self.image.blit(text_surface, text_rect)
            self.rect = self.image.get_rect(center=self.pos)

    def update(self, *args):
        if "ON" in help_button.text:  # enable help description
            if self.rect.collidepoint(mouse_pos) and self.description is not None and mouse_left_up is False:
                text_popup.pop(mouse_pos, self.description)
                ui.add(text_popup)


class SwitchButton(pygame.sprite.Sprite):
    """Button that switch text/option"""

    def __init__(self, text_list, image, pos, description=None, font_size=20):
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(font_size * screen_scale[1]))
        self.pos = pos
        self.description = description
        self.current_option = 0
        self.base_image = image
        self.image = self.base_image.copy()
        self.text_list = text_list
        self.text = self.text_list[self.current_option]
        self.change_text(self.text)
        self.rect = self.image.get_rect(center=self.pos)

    def change_option(self, option):
        if self.current_option != option:
            self.current_option = option
            self.image = self.base_image.copy()
            self.text = self.text_list[self.current_option]
            self.change_text(self.text)

    def change_text(self, text):
        text_surface = self.font.render(str(text), True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(int(self.image.get_width() / 2), int(self.image.get_height() / 2)))
        self.image.blit(text_surface, text_rect)

    def update(self, *args):
        if "ON" in help_button.text:  # enable help description
            if self.rect.collidepoint(mouse_pos) and self.description is not None and mouse_left_up is False:
                text_popup.pop(mouse_pos, self.description)
                ui.add(text_popup)


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
        self.base_image = self.image.copy()  # for original before add part and click
        self.rect = self.image.get_rect(center=pos)
        self.ui_type = ui_type
        self.part_images_original = [image.copy() for image in part_images]
        if "effect" not in self.ui_type:
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
            for box_part in ("S1", "S2", "S3", "S4", "S5", "E1", "E2", "DE1", "DE2", "E3", "E4", "DE3", "DE4"):
                text_surface = self.box_font.render(box_part, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(empty_box.get_width() / 2, empty_box.get_height() / 2))
                new_box = empty_box.copy()
                new_box.blit(text_surface, text_rect)
                self.part_images_original.append(new_box)
        self.part_images = [image.copy() for image in self.part_images_original]
        self.selected_part_images = [apply_colour(image, (34, 177, 76), white_colour=False) for image in
                                     self.part_images_original]
        self.part_selected = []
        self.stat1 = {}
        self.stat2 = {}
        self.change_p_type(self.ui_type)
        for key, item in self.part_pos.items():
            self.part_pos[key] = (item[0] * screen_scale[0], item[1] * screen_scale[1])
        self.blit_part()

    def change_p_type(self, new_type, player_change=False):
        """For helper that can change person"""
        self.ui_type = new_type
        if "effect" not in self.ui_type:
            self.rect_part_list = {self.ui_type + "_head": None, self.ui_type + "_body": None,
                                   self.ui_type + "_r_arm_up": None,
                                   self.ui_type + "_r_arm_low": None, self.ui_type + "_r_hand": None,
                                   self.ui_type + "_l_arm_up": None, self.ui_type + "_l_arm_low": None,
                                   self.ui_type + "_l_hand": None,
                                   self.ui_type + "_r_leg": None, self.ui_type + "_r_foot": None,
                                   self.ui_type + "_l_leg": None,
                                   self.ui_type + "_l_foot": None, self.ui_type + "_main_weapon": None,
                                   self.ui_type + "_sub_weapon": None}
            self.part_pos = {self.ui_type + "_head": (225, 85), self.ui_type + "_body": (225, 148),
                             self.ui_type + "_r_arm_up": (195, 126),
                             self.ui_type + "_r_arm_low": (195, 156), self.ui_type + "_r_hand": (195, 187),
                             self.ui_type + "_l_arm_up": (255, 126),
                             self.ui_type + "_l_arm_low": (255, 156), self.ui_type + "_l_hand": (255, 187),
                             self.ui_type + "_r_leg": (210, 216),
                             self.ui_type + "_r_foot": (210, 246), self.ui_type + "_l_leg": (240, 216),
                             self.ui_type + "_l_foot": (240, 246),
                             self.ui_type + "_main_weapon": (205, 30), self.ui_type + "_sub_weapon": (245, 30)}
        else:
            p_type = self.ui_type[:2]
            self.rect_part_list = {p_type + "_special_1": None, p_type + "_special_2": None,
                                   p_type + "_special_3": None,
                                   p_type + "_special_4": None, p_type + "_special_5": None,
                                   "effect_1": None, "effect_2": None, "dmg_effect_1": None, "dmg_effect_2": None,
                                   "effect_3": None, "effect_4": None, "dmg_effect_3": None, "dmg_effect_4": None}
            self.part_pos = {p_type + "_special_1": (20, 15), p_type + "_special_2": (20, 45),
                             p_type + "_special_3": (20, 75),
                             p_type + "_special_4": (20, 105), p_type + "_special_5": (20, 135),
                             "effect_1": (20, 165), "effect_2": (20, 195), "dmg_effect_1": (20, 225),
                             "dmg_effect_2": (20, 255),
                             "effect_3": (225, 165), "effect_4": (225, 195), "dmg_effect_3": (225, 225),
                             "dmg_effect_4": (225, 255)}
        if player_change:
            self.select_part(None, False, False)  # reset first
            for part in model.part_selected:  # blit selected part that is in helper
                if list(model.mask_part_list.keys())[part] in self.rect_part_list:
                    self.select_part(mouse_pos, True, False, list(model.mask_part_list.keys())[part])

    def blit_part(self):
        self.image = self.base_image.copy()
        for index, image in enumerate(self.part_images):
            this_key = list(self.part_pos.keys())[index]
            pos = self.part_pos[this_key]
            new_image = image
            if this_key in self.part_selected:  # highlight selected part
                new_image = self.selected_part_images[index]

            rect = new_image.get_rect(center=pos)
            self.image.blit(new_image, rect)
            self.rect_part_list[this_key] = rect

    def select_part(self, check_mouse_pos, shift_press, ctrl_press, specific_part=None):
        return_selected_part = None
        if specific_part is not None:
            if specific_part is False:
                self.part_selected = []
            elif specific_part in list(self.part_pos.keys()):
                if shift_press:
                    if specific_part not in self.part_selected:
                        self.part_selected.append(specific_part)
                elif ctrl_press:
                    if specific_part in self.part_selected:
                        self.part_selected.remove(specific_part)
                else:
                    self.part_selected = [specific_part]
            self.blit_part()
        else:  # click on helper ui
            click_any = False
            if check_mouse_pos is not None:
                for index, rect in enumerate(self.rect_part_list):
                    this_rect = self.rect_part_list[rect]
                    if this_rect is not None and this_rect.collidepoint(check_mouse_pos):
                        click_any = True
                        return_selected_part = tuple(self.part_pos.keys())[index]
                        if shift_press:
                            if tuple(self.part_pos.keys())[index] not in self.part_selected:
                                self.part_selected.append(tuple(self.part_pos.keys())[index])
                        elif ctrl_press:
                            if tuple(self.part_pos.keys())[index] in self.part_selected:
                                self.part_selected.remove(tuple(self.part_pos.keys())[index])
                        else:
                            self.part_selected = [tuple(self.part_pos.keys())[index]]
                            break
            if check_mouse_pos is None or (
                    click_any is False and (shift_press is False and ctrl_press is False)):  # click at empty space
                self.part_selected = []
            self.blit_part()
        self.add_stat()

        return return_selected_part

    def add_stat(self):
        for index, part in enumerate(self.rect_part_list):
            if self.stat2 is not None and part in self.stat2 and self.stat1[part] is not None and self.stat2[
                part] is not None:
                stat = self.stat1[part] + self.stat2[part]
                if len(stat) > 2:
                    stat.pop(2)
                    stat.pop(2)

                stat[1] = str(stat[1])
                if len(stat) > 3:
                    try:
                        stat[2] = str([[round(stat[2][0], 1), round(stat[2][1], 1)]])
                    except TypeError:
                        stat[2] = str([0, 0])
                    for index2, change in enumerate(["F", "FH", "FV", "FHV"]):
                        if stat[4] == index2:
                            stat[4] = change
                    stat[3] = str(round(stat[3], 1))
                    stat[5] = "L" + str(int(stat[5]))

                stat1 = stat[0:2]  # first line with part race, name
                stat1 = str(stat1).replace("'", "")
                stat2 = stat[2:]  # second line with stat
                stat2 = str(stat2).replace("'", "")

                text_colour = (0, 0, 0)
                if part in self.part_selected:  # green text for selected part
                    text_colour = (20, 90, 20)
                text_surface1 = self.font.render(stat1, True, text_colour)

                text_surface2 = self.font.render(stat2, True, text_colour)
                shift_x = 50 * screen_scale[0]
                if any(ext in part for ext in ("effect", "special")):
                    shift_x = 30 * screen_scale[0]
                    text_rect1 = text_surface1.get_rect(
                        midleft=(self.part_pos[part][0] + shift_x, self.part_pos[part][1] - 10))
                    text_rect2 = text_surface2.get_rect(
                        midleft=(self.part_pos[part][0] + shift_x, self.part_pos[part][1] - 10 + self.font_size + 2))
                elif "body" in part:
                    head_name = part[0:2] + "_head"
                    text_rect1 = text_surface1.get_rect(
                        midleft=(self.part_pos[head_name][0] + shift_x, self.part_pos[head_name][1] - 5))
                    text_rect2 = text_surface2.get_rect(
                        midleft=(
                        self.part_pos[head_name][0] + shift_x, self.part_pos[head_name][1] - 5 + self.font_size + 2))
                elif "head" in part:
                    text_rect1 = text_surface1.get_rect(
                        midright=(self.part_pos[part][0] - shift_x, self.part_pos[part][1] - 10))
                    text_rect2 = text_surface2.get_rect(
                        midright=(self.part_pos[part][0] - shift_x, self.part_pos[part][1] - 10 + self.font_size + 2))
                else:
                    shift_x = 14 * screen_scale[0]
                    if "weapon" in part:
                        shift_x = 26 * screen_scale[0]
                    if self.part_pos[part][0] > self.image.get_width() / 2:
                        text_rect1 = text_surface1.get_rect(
                            midleft=(self.part_pos[part][0] + shift_x, self.part_pos[part][1] - 15))
                        text_rect2 = text_surface2.get_rect(
                            midleft=(
                            self.part_pos[part][0] + shift_x, self.part_pos[part][1] - 15 + self.font_size + 2))
                    else:
                        text_rect1 = text_surface1.get_rect(
                            midright=(self.part_pos[part][0] - shift_x, self.part_pos[part][1] - 15))
                        text_rect2 = text_surface2.get_rect(
                            midright=(
                            self.part_pos[part][0] - shift_x, self.part_pos[part][1] - 15 + self.font_size + 2))
                self.image.blit(text_surface1, text_rect1)
                self.image.blit(text_surface2, text_rect2)
            # else:
            #     text_surface = self.font.render("None", 1, (0, 0, 0))
            #     text_rect = text_surface.get_rect(midleft=self.part_pos[part])
            #     self.image.blit(text_surface, text_rect)


class NameBox(pygame.sprite.Sprite):
    def __init__(self, size, pos, description=None):
        self._layer = 6
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font_size = int(24 * screen_scale[1])
        self.font = pygame.font.SysFont("helvetica", int(self.font_size * screen_scale[1]))
        self.description = description
        self.size = size
        self.image = pygame.Surface(self.size)
        self.image.fill((182, 233, 242))
        pygame.draw.rect(self.image, (100, 200, 0), (0, 0, self.image.get_width(), self.image.get_height()), 2)
        self.base_image = self.image.copy()
        self.pos = pos
        self.rect = self.image.get_rect(midtop=self.pos)
        self.text = None

    def change_name(self, text):
        if text != self.text:
            self.image = self.base_image.copy()
            self.text = text
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(
                center=(int(self.image.get_width() / 2), int(self.image.get_height() / 2)))
            self.image.blit(text_surface, text_rect)

    def update(self, *args):
        if "ON" in help_button.text:  # enable help description
            if self.rect.collidepoint(mouse_pos) and self.description is not None and mouse_left_up is False:
                text_popup.pop(mouse_pos, self.description)
                ui.add(text_popup)


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
        self.animation_list = {}  # dict of animation frame image surface
        self.animation_part_list = {}  # dict of part image surface
        self.bodypart_list = []  # list of part stat
        self.part_name_list = []  # list of part name
        self.frame_list = [{}] * max_frame
        self.current_history = -1  # start with -1 as the first history will be added later to 0
        self.animation_history = []
        self.body_part_history = []
        self.part_name_history = []
        self.mask_part_list = {}
        self.all_part_list = {}
        for p in range(1, max_person + 1):
            self.mask_part_list = self.mask_part_list | {"p" + str(p) + "_head": None, "p" + str(p) + "_body": None,
                                                         "p" + str(p) + "_r_arm_up": None,
                                                         "p" + str(p) + "_r_arm_low": None,
                                                         "p" + str(p) + "_r_hand": None,
                                                         "p" + str(p) + "_l_arm_up": None,
                                                         "p" + str(p) + "_l_arm_low": None,
                                                         "p" + str(p) + "_l_hand": None, "p" + str(p) + "_r_leg": None,
                                                         "p" + str(p) + "_r_foot": None, "p" + str(p) + "_l_leg": None,
                                                         "p" + str(p) + "_l_foot": None,
                                                         "p" + str(p) + "_main_weapon": None,
                                                         "p" + str(p) + "_sub_weapon": None,
                                                         "p" + str(p) + "_special_1": None,
                                                         "p" + str(p) + "_special_2": None,
                                                         "p" + str(p) + "_special_3": None,
                                                         "p" + str(p) + "_special_4": None,
                                                         "p" + str(p) + "_special_5": None}
            self.all_part_list = self.all_part_list | {"p" + str(p) + "_head": None, "p" + str(p) + "_eye": 1,
                                                       "p" + str(p) + "_mouth": 1,
                                                       "p" + str(p) + "_body": None, "p" + str(p) + "_r_arm_up": None,
                                                       "p" + str(p) + "_r_arm_low": None,
                                                       "p" + str(p) + "_r_hand": None,
                                                       "p" + str(p) + "_l_arm_up": None,
                                                       "p" + str(p) + "_l_arm_low": None,
                                                       "p" + str(p) + "_l_hand": None, "p" + str(p) + "_r_leg": None,
                                                       "p" + str(p) + "_r_foot": None, "p" + str(p) + "_l_leg": None,
                                                       "p" + str(p) + "_l_foot": None,
                                                       "p" + str(p) + "_main_weapon": None,
                                                       "p" + str(p) + "_sub_weapon": None,
                                                       "p" + str(p) + "_special_1": None,
                                                       "p" + str(p) + "_special_2": None,
                                                       "p" + str(p) + "_special_3": None,
                                                       "p" + str(p) + "_special_4": None,
                                                       "p" + str(p) + "_special_5": None}
        self.mask_part_list = self.mask_part_list | {"effect_1": None, "effect_2": None, "effect_3": None,
                                                     "effect_4": None,
                                                     "dmg_effect_1": None, "dmg_effect_2": None, "dmg_effect_3": None,
                                                     "dmg_effect_4": None,
                                                     }
        self.all_part_list = self.all_part_list | {"effect_1": None, "effect_2": None, "effect_3": None,
                                                   "effect_4": None,
                                                   "dmg_effect_1": None, "dmg_effect_2": None, "dmg_effect_3": None,
                                                   "dmg_effect_4": None}
        self.p_eyebrow = {}
        self.p_any_eye = {}
        self.p_any_mouth = {}
        self.p_beard = {}
        self.part_selected = []
        self.head_race = {"p" + str(p): "Human" for p in range(1, max_person + 1)}  # for head generation
        self.body_race = {"p" + str(p): "Human" for p in range(1, max_person + 1)}  # for armour preview
        skin = list(colour_list.keys())[random.randint(0, len(colour_list) - 1)]
        # skin_colour = skin_colour_list[skin]
        self.p_hair_colour = {"p" + str(p): [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)] for
                              p in
                              range(1, max_person + 1)}
        self.p_eye_colour = {"p" + str(p): [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)] for
                             p in range(1, max_person + 1)}
        self.weapon = {}
        self.armour = {}
        for p in range(1, max_person + 1):
            self.weapon = self.weapon | {"p" + str(p) + "_main_weapon": "Sword", "p" + str(p) + "_sub_weapon": "Sword"}
            self.armour = self.armour | {"p" + str(p) + "_armour": "None"}
        self.empty_sprite_part = [0, pygame.Vector2(0, 0), [50, 50], 0, 0, 0, 1]
        self.get_face()
        self.size = 1  # size scale of sprite
        try:
            self.read_animation(tuple((animation_pool_data[animation_race].keys()))[0])
            self.default_sprite_part = {key: (value[:].copy() if value is not None else value) for key, value in
                                        self.animation_part_list[0].items()}
            self.default_body_part = {key: value for key, value in self.bodypart_list[0].items()}
            self.default_part_name = {key: value for key, value in self.part_name_list[0].items()}
        except IndexError:  # empty animation file
            self.read_animation(None)
            self.default_sprite_part = {key: None for key in self.mask_part_list}
            self.default_body_part = {key: value for key, value in self.all_part_list.items()}
            self.default_part_name = {key: None for key in self.mask_part_list}

    def get_face(self):
        """Grab face parts"""
        for p in range(1, max_person + 1):
            this_p = "p" + str(p)
            self.p_eyebrow = self.p_eyebrow | {this_p: "normal"}
            self.p_any_eye = self.p_any_eye | {this_p: "normal"}
            self.p_any_mouth = self.p_any_mouth | {this_p: "normal"}
            self.p_beard = self.p_beard | {this_p: "none"}

    def make_layer_list(self, sprite_part):
        pose_layer_list = {k: v[5] for k, v in sprite_part.items() if v is not None and v != []}
        pose_layer_list = dict(sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))
        return pose_layer_list

    def read_animation(self, name, old=False, new_size=True):
        global activate_list
        #  sprite animation generation from data
        self.animation_part_list = [{key: None for key in self.mask_part_list}] * max_frame
        self.animation_list = [self.create_animation_film(None, current_frame, empty=True)] * max_frame
        self.bodypart_list = [{key: value for key, value in self.all_part_list.items()}] * max_frame
        self.part_name_list = [{key: None for key in self.mask_part_list}] * max_frame
        for key, value in self.mask_part_list.items():  # reset rect list
            self.mask_part_list[key] = None
        for joint in joints:  # remove all joint first
            joint.kill()
        if name is not None:
            frame_list = current_pool[animation_race][name].copy()
            if old:
                frame_list = self.frame_list
            while len(frame_list) < max_frame:  # add empty item
                frame_list.append({})
            if new_size:
                try:
                    self.size = frame_list[0][
                        'size']  # use only the size from first frame, all frame should be same size
                except KeyError:
                    self.size = 1
                except TypeError:
                    if type(self.size) is not float and self.size.isdigit() is False:
                        self.size = 1
                    else:
                        self.size = int(self.size)
            size_button.change_text("Size: " + str(self.size))
            for frame in frame_list:  # change frame size value
                frame['size'] = self.size
            for index, pose in enumerate(frame_list):
                sprite_part = {key: None for key in self.mask_part_list}
                link_list = {key: None for key in self.mask_part_list}
                bodypart_list = {key: value for key, value in self.all_part_list.items()}
                for part in pose:
                    if pose[part] != [0] and "property" not in part and part != "size":
                        if "eye" not in part and "mouth" not in part:
                            if "weapon" in part:
                                link_list[part] = [pose[part][1], pose[part][2]]
                                if pose[part][0] in gen_weapon_sprite_pool[self.weapon[part]]:
                                    bodypart_list[part] = [self.weapon[part], pose[part][0]]
                                else:
                                    bodypart_list[part] = [self.weapon[part], 0]
                            else:
                                link_list[part] = [pose[part][2], pose[part][3]]
                                bodypart_list[part] = [pose[part][0], pose[part][1]]
                        elif pose[part] != 0:  # eye or mouth change
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
                self.generate_body(self.bodypart_list[index])
                part_name = {key: None for key in self.mask_part_list}

                except_list = ("eye", "mouth", "size")
                for part in part_name_header:
                    if part in pose and pose[part] != [0] and any(ext in part for ext in except_list) is False:
                        if "weapon" in part:
                            try:
                                sprite_part[part] = [self.sprite_image[part],
                                                     (self.sprite_image[part].get_width() / 2,
                                                      self.sprite_image[part].get_height() / 2),
                                                     link_list[part], pose[part][3], pose[part][4], pose[part][5],
                                                     pose[part][6]]
                                part_name[part] = [self.weapon[part], pose[part][0]]
                            except AttributeError:  # return None, sprite not existed.
                                sprite_part[part] = [self.sprite_image[part], (0, 0),
                                                     link_list[part], pose[part][3], pose[part][4], pose[part][5],
                                                     pose[part][6]]
                                part_name[part] = [self.weapon[part], pose[part][0]]
                        else:
                            if any(ext in part for ext in ("effect", "special")):
                                sprite_part[part] = [self.sprite_image[part],
                                                     (self.sprite_image[part].get_width() / 2,
                                                      self.sprite_image[part].get_height() / 2),
                                                     link_list[part], pose[part][4], pose[part][5], pose[part][6],
                                                     pose[part][7]]
                            else:
                                sprite_part[part] = [self.sprite_image[part], "center", link_list[part], pose[part][4],
                                                     pose[part][5], pose[part][6], pose[part][7]]
                            part_name[part] = [pose[part][0], pose[part][1]]
                pose_layer_list = self.make_layer_list(sprite_part)
                self.animation_part_list[index] = sprite_part
                self.part_name_list[index] = part_name
                image = self.create_animation_film(pose_layer_list, index)
                self.animation_list[index] = image
            self.frame_list = frame_list

        activate_list = [False] * max_frame
        for strip_index, strip in enumerate(filmstrips):
            strip.activate = False
            for stuff in self.animation_part_list[strip_index].values():
                if stuff is not None:
                    strip.activate = True
                    activate_list[strip_index] = True
                    break

        # recreate property list
        anim_prop_list_box.namelist = [item for item in anim_prop_list_box.namelist if item in anim_property_select] + \
                                      [item for item in anim_prop_list_box.namelist if item not in anim_property_select]
        for frame in range(0, len(frame_prop_list_box.namelist)):
            frame_prop_list_box.namelist[frame] = [item for item in frame_prop_list_box.namelist[frame] if
                                                   item in frame_property_select[frame]] + \
                                                  [item for item in frame_prop_list_box.namelist[frame] if
                                                   item not in frame_property_select[frame]]

        setup_list(menu.NameList, current_anim_row, anim_prop_list_box.namelist, anim_prop_namegroup,
                   anim_prop_list_box, ui, screen_scale, layer=9, old_list=anim_property_select)
        setup_list(menu.NameList, current_frame_row, frame_prop_list_box.namelist[current_frame], frame_prop_namegroup,
                   frame_prop_list_box, ui, screen_scale, layer=9, old_list=frame_property_select[current_frame])

    def change_size(self):
        """Scale position of all parts when change animation size"""
        frame_size = self.frame_list[0]["size"]
        old_size = self.frame_list[1]["size"]
        min_x = 9999999
        min_y = 9999999
        max_x = 0
        max_y = 0
        for frame_index, this_frame in enumerate(current_pool[animation_race][animation_name]):
            current_pool[animation_race][animation_name][frame_index]["size"] = frame_size
            for key, value in this_frame.items():  # loop to find min and max point for center of all frames to avoid unequal placement
                if type(value) is list and len(value) > 2:
                    pos_index = (2, 3)
                    if "weapon" in key:
                        pos_index = (1, 2)
                    x = value[pos_index[0]]
                    y = value[pos_index[1]]
                    if min_x > x:
                        min_x = x
                    if max_x < x:
                        max_x = x
                    if min_y > y:
                        min_y = y
                    if max_y < y:
                        max_y = y

        for frame_index, this_frame in enumerate(current_pool[animation_race][animation_name]):
            center_x = (min_x + max_x) / 2  # find center of all parts
            center_y = (min_y + max_y) / 2
            new_center = ((center_x / old_size) * frame_size, (center_y / old_size) * frame_size)

            for key, value in this_frame.items():
                if type(value) is list and len(value) > 2:
                    pos_index = (2, 3)
                    if "weapon" in key:
                        pos_index = (1, 2)
                    x = value[pos_index[0]]
                    y = value[pos_index[1]]
                    diff_center = (x - center_x, y - center_y)
                    current_pool[animation_race][animation_name][frame_index][key][pos_index[0]] = new_center[0] + \
                                                                                   diff_center[0]
                    current_pool[animation_race][animation_name][frame_index][key][pos_index[1]] = new_center[1] + \
                                                                                   diff_center[1]

    def create_animation_film(self, pose_layer_list, frame, empty=False):
        image = pygame.Surface((default_sprite_size[0] * self.size, default_sprite_size[1] * self.size),
                               pygame.SRCALPHA)  # default size will scale down later
        save_mask = False
        if frame == current_frame:
            save_mask = True
        if empty is False:
            for index, layer in enumerate(pose_layer_list):
                part = self.animation_part_list[frame][layer]
                if part is not None and part[0] is not None:
                    image = self.part_to_sprite(image, part[0], layer, part[2], part[3], part[4], part[6],
                                                save_mask=save_mask)
        return image

    def grab_face_part(self, race, part, part_check, part_default=None):
        """For creating body part like eye or mouth in animation that accept any part (1) so use default instead"""
        try:
            if part_check == 1:  # any part
                surface = gen_body_sprite_pool[race][part][part_default].copy()
            else:
                surface = gen_body_sprite_pool[race][part][part_check].copy()
            return surface
        except KeyError:
            return None

    def generate_body(self, bodypart_list):
        self.sprite_image = {key: None for key in self.mask_part_list}
        p_head_sprite_surface = {"p" + str(p): None for p in range(1, max_person + 1)}
        for key in p_head_sprite_surface:
            head_sprite_surface = pygame.Surface((0, 0))
            try:
                head_race = bodypart_list[key + "_head"][0]
                self.head_race[key] = head_race
                head_sprite = gen_body_sprite_pool[head_race]["head"][bodypart_list[key + "_head"][1]].copy()
                head_sprite_surface = pygame.Surface(head_sprite.get_size(), pygame.SRCALPHA)
                head_rect = head_sprite.get_rect(midtop=(head_sprite_surface.get_width() / 2, 0))
                head_sprite_surface.blit(head_sprite, head_rect)
                face = [self.grab_face_part(head_race, "eyebrow", self.p_eyebrow[key]),
                        self.grab_face_part(head_race, "eye", bodypart_list[key + "_eye"],
                                            self.p_any_eye[key]),
                        self.grab_face_part(head_race, "beard", self.p_beard[key]),
                        self.grab_face_part(head_race, "mouth", bodypart_list[key + "_mouth"],
                                            self.p_any_mouth[key])]
                # if skin != "white":
                #     face[0] = self.apply_colour(face[0], skin_colour)
                face[0] = apply_colour(face[0], self.p_hair_colour[key])
                face[2] = apply_colour(face[2], self.p_hair_colour[key])
                face[1] = apply_colour(face[1], self.p_eye_colour[key])

                head_sprite_surface = pygame.Surface(head_sprite.get_size(), pygame.SRCALPHA)
                rect = head_sprite.get_rect(
                    center=(head_sprite_surface.get_width() / 2, head_sprite_surface.get_height() / 2))
                head_sprite_surface.blit(head_sprite, rect)

                for index, item in enumerate(face):  # add face to head sprite
                    if item is not None:
                        rect = item.get_rect(
                            center=(head_sprite_surface.get_width() / 2, head_sprite_surface.get_height() / 2))
                        head_sprite_surface.blit(item, rect)
            except (KeyError, TypeError):  # empty
                pass

            p_head_sprite_surface[key] = head_sprite_surface

            if self.armour[key + "_armour"] != "None":
                try:
                    armour = self.armour[key + "_armour"].split("/")
                    gear_image = gen_armour_sprite_pool[head_race][armour[0]][armour[1]]["head"][
                        bodypart_list[key + "_head"][1]]

                    gear_image_sprite = pygame.Surface(gear_image.get_size(), pygame.SRCALPHA)
                    rect = head_sprite_surface.get_rect(
                        center=(gear_image_sprite.get_width() / 2, gear_image_sprite.get_height() / 2))
                    gear_image_sprite.blit(head_sprite_surface, rect)

                    rect = gear_image.get_rect(
                        center=(gear_image_sprite.get_width() / 2, gear_image_sprite.get_height() / 2))
                    gear_image_sprite.blit(gear_image, rect)

                    p_head_sprite_surface[key] = gear_image_sprite

                except (KeyError, UnboundLocalError, TypeError):  # skip part that not exist
                    pass

            self.sprite_image[key + "_head"] = p_head_sprite_surface[key]

            try:
                race = bodypart_list[key + "_body"][0]
                self.body_race[key] = race
            except (KeyError, UnboundLocalError, TypeError):
                pass

        except_list = ("eye", "mouth", "head")  # skip doing these
        for stuff in bodypart_list:  # create stat and image
            if bodypart_list[stuff] is not None and bodypart_list[stuff] != [0, 0]:
                if any(ext in stuff for ext in except_list) is False:
                    try:
                        if "weapon" in stuff:
                            part_name = self.weapon[stuff]
                            if part_name is not None and bodypart_list[stuff][1]:
                                self.sprite_image[stuff] = gen_weapon_sprite_pool[part_name][
                                    bodypart_list[stuff][1]].copy()
                        elif "effect_" in stuff:
                            self.sprite_image[stuff] = effect_sprite_pool[bodypart_list[stuff][0]][
                                bodypart_list[stuff][1]].copy()
                        else:
                            new_part_name = stuff
                            if any(ext in stuff for ext in p_list):
                                part_name = stuff[3:]  # remove p*number*_ to get part name
                                new_part_name = part_name
                            if "special" in stuff:
                                part_name = "special"
                                new_part_name = part_name
                            if "r_" in part_name[0:2] or "l_" in part_name[0:2]:
                                new_part_name = part_name[2:]  # remove part side
                            self.sprite_image[stuff] = gen_body_sprite_pool[bodypart_list[stuff][0]][new_part_name][
                                bodypart_list[stuff][1]].copy()
                        if any(ext in stuff for ext in p_list) and self.armour[stuff[0:2] + "_armour"] != "None":
                            armour = self.armour[stuff[0:2] + "_armour"].split("/")

                            gear_image = gen_armour_sprite_pool[bodypart_list[stuff][0]][armour[0]][armour[1]][
                                part_name][bodypart_list[stuff][1]].copy()
                            gear_surface = pygame.Surface(gear_image.get_size(), pygame.SRCALPHA)
                            rect = self.sprite_image[stuff].get_rect(
                                center=(gear_surface.get_width() / 2, gear_surface.get_height() / 2))
                            gear_surface.blit(self.sprite_image[stuff], rect)
                            rect = gear_image.get_rect(center=(gear_surface.get_width() / 2,
                                                               gear_surface.get_height() / 2))
                            gear_surface.blit(gear_image, rect)
                            self.sprite_image[stuff] = gear_surface
                    except (KeyError, UnboundLocalError):  # no part name known for current race, skip getting image
                        pass

        # if skin != "white":
        #     for part in list(self.sprite_image.keys())[1:]:
        #         self.sprite_image[part] = self.apply_colour(self.sprite_image[part], skin_colour)

    def click_part(self, mouse_pos, shift_press, ctrl_press, part=None):
        if part is None:
            click_part = False
            if shift_press is False and ctrl_press is False:
                self.part_selected = []
            else:
                click_part = True
            for index, rect in enumerate(self.mask_part_list):
                this_rect = self.mask_part_list[rect]
                if this_rect is not None and this_rect[0].collidepoint(mouse_pos) and this_rect[1].get_at(
                        mouse_pos - this_rect[0].topleft) == 1:
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
                self.part_selected.append(list(self.mask_part_list.keys()).index(part))
                self.part_selected = list(set(self.part_selected))
            elif ctrl_press:
                if list(self.mask_part_list.keys()).index(part) in self.part_selected:
                    self.part_selected.remove(list(self.mask_part_list.keys()).index(part))
            else:
                self.part_selected = [list(self.mask_part_list.keys()).index(part)]

    def edit_part(self, mouse_pos, edit_type, specific_frame=None):
        edit_frame = current_frame
        if specific_frame is not None:
            edit_frame = specific_frame
        key_list = list(self.mask_part_list.keys())

        if edit_type not in ("undo", "redo", "change", "new"):
            accept_history = True
            if edit_type == "place" and mouse_right_down:  # save only when release mouse for mouse input
                accept_history = False
            if accept_history:
                if self.current_history < len(self.animation_history) - 1:
                    self.part_name_history = self.part_name_history[
                                             :self.current_history + 1]  # remove all future redo history
                    self.animation_history = self.animation_history[:self.current_history + 1]
                    self.body_part_history = self.body_part_history[:self.current_history + 1]
                self.add_history()

        if edit_type == "default":  # reset to default
            self.animation_part_list[edit_frame] = {key: (value[:].copy() if value is not None else value) for
                                                    key, value in
                                                    self.default_sprite_part.items()}
            self.bodypart_list[edit_frame] = {key: value for key, value in self.default_body_part.items()}
            self.part_name_list[edit_frame] = {key: value for key, value in self.default_part_name.items()}
            self.part_selected = []
            race_part_button.change_text("")
            part_selector.change_name("")

        elif edit_type == "clear":  # clear whole strip
            for part in self.part_name_list[edit_frame]:
                self.bodypart_list[edit_frame][part] = [0, 0]
                self.part_name_list[edit_frame][part] = ["", ""]
                self.animation_part_list[edit_frame][part] = []
            self.part_selected = []
            frame_property_select[edit_frame] = []
            self.frame_list[edit_frame]["frame_property"] = frame_property_select[edit_frame]
            setup_list(menu.NameList, current_frame_row, frame_prop_list_box.namelist[edit_frame], frame_prop_namegroup,
                       frame_prop_list_box, ui, screen_scale, layer=9,
                       old_list=frame_property_select[edit_frame])  # change frame property list

        # elif edit_type == "change":  # change strip
        #     self.part_selected = []

        elif edit_type == "paste":  # paste copy part
            for part in copy_part:
                if copy_part[part] is not None:
                    self.bodypart_list[edit_frame][part] = copy_part[part].copy()
                    self.animation_part_list[edit_frame][part] = copy_animation[part].copy()
                    self.part_name_list[edit_frame][part] = copy_name[part].copy()

        elif edit_type == "all frame selected part paste":  # paste copy part for all
            for frame in all_copy_part:
                for part in all_copy_part[frame]:
                    if all_copy_part[frame][part] is not None:
                        self.bodypart_list[frame][part] = all_copy_part[frame][part].copy()
                        self.animation_part_list[frame][part] = all_copy_animation[frame][part].copy()
                        self.part_name_list[frame][part] = all_copy_name[frame][part].copy()
                    else:
                        self.bodypart_list[frame][part] = None
                        self.bodypart_list[frame][part] = None
                        self.part_name_list[frame][part] = None

        elif edit_type == "paste part stat":  # paste copy stat
            for part in copy_part_stat:
                new_part = part
                if any(ext in part for ext in ("effect", )) is False:
                    new_part = p_body_helper.ui_type + part[2:]
                if copy_part_stat[part] is not None:
                    self.bodypart_list[edit_frame][new_part] = copy_part_stat[part].copy()
                    self.animation_part_list[edit_frame][new_part] = copy_animation_stat[part].copy()
                    self.part_name_list[edit_frame][new_part] = copy_name_stat[part].copy()
                else:
                    self.bodypart_list[edit_frame][new_part] = None
                    self.animation_part_list[edit_frame][new_part] = None
                    self.part_name_list[edit_frame][new_part] = None

        elif edit_type == "undo" or edit_type == "redo":
            for frame_num, _ in enumerate(self.animation_part_list):
                self.part_name_list[frame_num] = {key: value for key, value in
                                                  self.part_name_history[self.current_history][frame_num].items()}
                self.animation_part_list[frame_num] = {key: (value[:].copy() if value is not None else value) for
                                                       key, value in
                                                       self.animation_history[self.current_history][frame_num].items()}
                self.bodypart_list[frame_num] = {key: value for key, value in
                                                 self.body_part_history[self.current_history][frame_num].items()}

        elif "armour" in edit_type:
            if any(ext in edit_type for ext in p_list):
                self.armour[edit_type[0:2] + "_armour"] = edit_type.split(edit_type[0:2] + "_armour_")[1]
                change_animation(animation_name)

        elif "eye" in edit_type:
            if "Any" in edit_type:
                self.bodypart_list[edit_frame][edit_type[0:2] + "_eye"] = 1
            else:
                self.bodypart_list[edit_frame][edit_type[0:2] + "_eye"] = edit_type.split(edit_type[0:2] + "_eye_")[1]
            self.generate_body(self.bodypart_list[edit_frame])
            part = edit_type[0:2] + "_head"
            self.animation_part_list[edit_frame][part][0] = self.sprite_image[part]

        elif "mouth" in edit_type:
            if "Any" in edit_type:
                self.bodypart_list[edit_frame][edit_type[0:2] + "_mouth"] = 1
            else:
                self.bodypart_list[edit_frame][edit_type[0:2] + "_mouth"] = edit_type.split(edit_type[0:2] + "_mouth_")[
                    1]
            self.generate_body(self.bodypart_list[edit_frame])
            part = edit_type[0:2] + "_head"
            self.animation_part_list[edit_frame][part][0] = self.sprite_image[part]

        elif "part" in edit_type:
            if self.part_selected:
                part = self.part_selected[-1]
                part_index = key_list[part]
                part_change = edit_type[5:]
                self.bodypart_list[edit_frame][part_index][1] = part_change
                self.part_name_list[edit_frame][part_index][1] = part_change
                self.generate_body(self.bodypart_list[edit_frame])
                if not self.animation_part_list[edit_frame][part_index]:
                    self.animation_part_list[edit_frame][part_index] = self.empty_sprite_part.copy()
                    self.animation_part_list[edit_frame][part_index][1] = "center"
                self.animation_part_list[edit_frame][part_index][0] = self.sprite_image[part_index]

        elif "race" in edit_type:  # change race/base part type
            if self.part_selected:
                part = self.part_selected[-1]
                part_index = key_list[part]
                part_change = edit_type[5:]
                if "weapon" in part_index:
                    self.weapon[part_index] = part_change
                if self.bodypart_list[edit_frame][part_index] is None:
                    self.bodypart_list[edit_frame][part_index] = [0, 0]
                    self.part_name_list[edit_frame][part_index] = ["", ""]
                    self.animation_part_list[edit_frame][part_index] = []
                self.bodypart_list[edit_frame][part_index][0] = part_change
                self.part_name_list[edit_frame][part_index][0] = part_change
                self.bodypart_list[edit_frame][part_index][1] = self.part_name_list[edit_frame][part_index][
                    1]  # attempt to get part again in case the initial reading not found
                try:
                    self.generate_body(self.bodypart_list[edit_frame])
                    self.animation_part_list[edit_frame][part_index][0] = self.sprite_image[part_index]
                except IndexError:
                    pass

        elif "new" in edit_type:  # new animation
            self.animation_part_list = [{key: None for key in self.mask_part_list}] * max_frame
            p_face = {}
            for p in range(1, max_person + 1):
                p_face = p_face | {"p" + str(p) + "_eye": 1, "p" + str(p) + "_mouth": 1}
            self.bodypart_list = [{key: value for key, value in self.all_part_list.items()}] * max_frame
            for stuff in self.bodypart_list:
                stuff.update(p_face)
            self.part_name_list = [{key: None for key in self.mask_part_list}] * max_frame
            self.part_selected = []

        elif edit_type == "weapon joint to hand":
            for part_index in key_list:
                if "_weapon" in part_index:
                    if self.animation_part_list[edit_frame][part_index] is not None and \
                            len(self.animation_part_list[edit_frame][part_index]) > 3 and \
                            "sheath" not in self.part_name_list[edit_frame][part_index][-1]:
                        hand = "r_"
                        if "sub" in part_index:
                            hand = "l_"
                        hand_part = part_index[:3] + hand + "hand"
                        if self.animation_part_list[edit_frame][hand_part] is not None and \
                                len(self.animation_part_list[edit_frame][hand_part]) > 3:  # hand exist
                            hand_pos = self.animation_part_list[edit_frame][hand_part][2]
                            part_image = self.animation_part_list[edit_frame][part_index][0]
                            if part_image is not None:
                                center = pygame.Vector2(part_image.get_width() / 2, part_image.get_height() / 2)
                                if weapon_joint_list[self.weapon[part_index]] != "center":
                                    pos_different = center - weapon_joint_list[self.weapon[part_index]]  # find distance between image center and connect point main_joint_pos
                                    target = hand_pos + pos_different
                                else:
                                    target = hand_pos
                                if self.animation_part_list[edit_frame][part_index][3] != 0:
                                    radians_angle = radians(360 - self.animation_part_list[edit_frame][part_index][3])
                                    target = rotation_xy(hand_pos, target, radians_angle)  # find new point with rotation

                                self.animation_part_list[edit_frame][part_index][2] = target

        elif self.part_selected:
            if edit_type == "place":  # find center point of all selected parts
                min_x = 9999999
                min_y = 9999999
                max_x = 0
                max_y = 0
                for part in self.part_selected:  # loop to find min and max point for center
                    if part < len(key_list):  # skip part that not exist
                        part_index = key_list[part]
                        if self.animation_part_list[edit_frame][part_index] is not None and \
                                len(self.animation_part_list[edit_frame][part_index]) > 3:
                            value = self.animation_part_list[edit_frame][part_index][2]
                            x = value[0]
                            y = value[1]
                            if min_x > x:
                                min_x = x
                            if max_x < x:
                                max_x = x
                            if min_y > y:
                                min_y = y
                            if max_y < y:
                                max_y = y
                center = ((min_x + max_x) / 2, (min_y + max_y) / 2)  # find center of all parts

            for part in self.part_selected:
                if part < len(key_list):  # can't edit part that not exist
                    part_index = key_list[part]
                    if self.animation_part_list[edit_frame][part_index] is not None and \
                            len(self.animation_part_list[edit_frame][part_index]) > 3:
                        if edit_type == "place":  # mouse place
                            new_point = mouse_pos
                            offset = (self.animation_part_list[edit_frame][part_index][2][0] - center[0],
                                      self.animation_part_list[edit_frame][part_index][2][1] - center[1])
                            if point_edit == 1:  # use joint
                                part_image = self.sprite_image[part_index]
                                center = pygame.Vector2(part_image.get_width() / 2, part_image.get_height() / 2)
                                pos_different = center - self.animation_part_list[edit_frame][part_index][
                                    1]  # find distance between image center and connect point main_joint_pos
                                new_point = new_point + pos_different
                            new_point = new_point + offset
                            self.animation_part_list[edit_frame][part_index][2] = [round(new_point[0], 1), round(new_point[1], 1)]

                        elif "move_" in edit_type:  # keyboard move
                            try:
                                new_point = [self.animation_part_list[edit_frame][part_index][2][0],
                                             self.animation_part_list[edit_frame][part_index][2][1]]
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
                            self.animation_part_list[edit_frame][part_index][2] = new_point.copy()

                        elif "tilt_" in edit_type:  # keyboard rotate
                            new_angle = self.animation_part_list[edit_frame][part_index][3]
                            if "q" in edit_type:
                                new_angle = new_angle - 0.5
                            elif "e" in edit_type:
                                new_angle = new_angle + 0.5
                            self.animation_part_list[edit_frame][part_index][3] = new_angle

                        elif edit_type == "rotate":  # mouse rotate
                            base_pos = self.animation_part_list[edit_frame][part_index][2]
                            rotate_radians = atan2(mouse_pos[1] - base_pos[1], mouse_pos[0] - base_pos[0])
                            new_angle = degrees(rotate_radians)
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

                            self.animation_part_list[edit_frame][part_index][3] = new_angle

                        elif "scale" in edit_type:  # part scale
                            if "up" in edit_type:
                                self.animation_part_list[edit_frame][part_index][6] += 0.1
                                self.animation_part_list[edit_frame][part_index][6] = round(
                                    self.animation_part_list[edit_frame][part_index][6],
                                    1)
                            elif "down" in edit_type:
                                self.animation_part_list[edit_frame][part_index][6] -= 0.1
                                if self.animation_part_list[edit_frame][part_index][6] < 0:
                                    self.animation_part_list[edit_frame][part_index][6] = 0
                                self.animation_part_list[edit_frame][part_index][6] = round(
                                    self.animation_part_list[edit_frame][part_index][6],
                                    1)
                        elif "flip" in edit_type:
                            flip_type = int(edit_type[-1])
                            current_flip = self.animation_part_list[edit_frame][part_index][4]
                            if current_flip == 0:  # current no flip
                                self.animation_part_list[edit_frame][part_index][4] = flip_type
                            elif current_flip == 1:  # current horizon flip
                                if flip_type == 1:
                                    self.animation_part_list[edit_frame][part_index][4] = 0
                                else:
                                    self.animation_part_list[edit_frame][part_index][4] = 3
                            elif current_flip == 2:  # current vertical flip
                                if flip_type == 1:
                                    self.animation_part_list[edit_frame][part_index][4] = 3
                                else:
                                    self.animation_part_list[edit_frame][part_index][4] = 0
                            elif current_flip == 3:  # current both hori and vert flip
                                if flip_type == 1:
                                    self.animation_part_list[edit_frame][part_index][4] = 2
                                else:
                                    self.animation_part_list[edit_frame][part_index][4] = 1

                        elif "reset" in edit_type:
                            self.animation_part_list[edit_frame][part_index][3] = 0
                            self.animation_part_list[edit_frame][part_index][4] = 0

                        elif "delete" in edit_type:
                            self.bodypart_list[edit_frame][part_index] = None
                            self.part_name_list[edit_frame][part_index] = None
                            self.animation_part_list[edit_frame][part_index] = None

                        elif "layer_" in edit_type:
                            if "up" in edit_type:
                                self.animation_part_list[edit_frame][part_index][5] += 1
                            elif "down" in edit_type:
                                self.animation_part_list[edit_frame][part_index][5] -= 1
                                if self.animation_part_list[edit_frame][part_index][5] == 0:
                                    self.animation_part_list[edit_frame][part_index][5] = 1
        for key, value in self.mask_part_list.items():  # reset rect list
            self.mask_part_list[key] = None
        for joint in joints:  # remove all joint first
            joint.kill()

        # recreate frame image
        pose_layer_list = self.make_layer_list(self.animation_part_list[edit_frame])
        for frame_num, _ in enumerate(self.animation_list):
            pose_layer_list = self.make_layer_list(self.animation_part_list[frame_num])
            surface = self.create_animation_film(pose_layer_list, frame_num)
            self.animation_list[frame_num] = surface
        for frame, _ in enumerate(self.frame_list):
            self.frame_list[frame] = {}
            name_list = self.part_name_list[frame]
            for key in self.mask_part_list:
                try:
                    sprite_part = self.animation_part_list[frame]
                    if sprite_part[key] is not None:
                        self.frame_list[frame][key] = name_list[key] + [sprite_part[key][2][0], sprite_part[key][2][1],
                                                                             sprite_part[key][3], sprite_part[key][4],
                                                                             sprite_part[key][5], sprite_part[key][6]]
                    else:
                        self.frame_list[frame][key] = [0]
                except (TypeError, IndexError):  # None type error from empty frame
                    self.frame_list[frame][key] = [0]
            for key in self.frame_list[frame]:
                if "weapon" in key and self.frame_list[frame][key] != [0]:
                    self.frame_list[frame][key] = self.frame_list[frame][key][1:]
            p_face = {}
            for p in p_list:
                p_face = p_face | {p: {p + "_eye": self.bodypart_list[frame][p + "_eye"],
                                       p + "_mouth": self.bodypart_list[frame][p + "_mouth"]}}
            for p in p_face:
                p_face_pos = list(self.frame_list[frame].keys()).index(p + "_head") + 1
                self.frame_list[frame] = {k: v for k, v in (
                            list(self.frame_list[frame].items())[:p_face_pos] + list(p_face[p].items()) +
                            list(self.frame_list[frame].items())[p_face_pos:])}

            self.frame_list[frame]["size"] = self.size
            self.frame_list[frame]["frame_property"] = frame_property_select[frame]
            self.frame_list[frame]["animation_property"] = anim_property_select
        anim_to_pool(animation_name, current_pool[animation_race], self, activate_list)
        reload_animation(anim, self)

        if edit_type == "new":
            for index, frame in enumerate(self.frame_list):  # reset all frame to empty frame like the first one
                self.frame_list[index] = {key: value for key, value in list(self.frame_list[0].items())}
            anim_to_pool(animation_name, current_pool[animation_race], self, activate_list, new=True)

            # reset history when create new animation
            self.clear_history()

        if len(self.animation_history) > 2:  # save only last 1000 activity
            new_first = len(self.animation_history) - 2
            self.part_name_history = self.part_name_history[new_first:]
            self.animation_history = self.animation_history[new_first:]
            self.body_part_history = self.body_part_history[new_first:]
            self.current_history -= new_first

    def part_to_sprite(self, surface, part, part_name, target, angle, flip, scale, save_mask=False):
        """Find body part's new center point from main_joint_pos with new angle, then create rotated part and blit to sprite"""
        part_rotated = part.copy()
        if scale != 1:
            part_rotated = pygame.transform.smoothscale(part_rotated, (part_rotated.get_width() * scale,
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

        # center = pygame.Vector2(part.get_width() / 2, part.get_height() / 2)
        # new_target = target  # - pos_different  # find new center point
        # if "weapon" in list(self.mask_part_list.keys())[part_index] and main_joint_pos != "center":  # only weapon use joint to calculate position
        #     pos_different = main_joint_pos - center  # find distance between image center and connect point main_joint_pos
        #     new_target = main_joint_pos + pos_different
        # if angle != 0:
        #     radians_angle = math.radians(360 - angle)
        #     new_target = rotation_xy(target, new_target, radians_angle)  # find new center point with rotation
        rect = part_rotated.get_rect(center=target)
        if save_mask:
            mask = pygame.mask.from_surface(part_rotated)
            self.mask_part_list[part_name] = (rect, mask)

        surface.blit(part_rotated, rect)

        return surface

    def remake_mask_list(self):
        for key, value in self.mask_part_list.items():  # reset rect list
            self.mask_part_list[key] = None

        for part_index, part in enumerate(self.animation_part_list[current_frame]):
            rect = part.rect
            self.mask_part_list[list(self.mask_part_list.keys())[part_index]] = rect

    def add_history(self):
        self.current_history += 1
        self.part_name_history.append(
            {frame_num: {key: value for key, value in self.part_name_list[frame_num].items()} for frame_num, _ in
             enumerate(self.part_name_list)})

        self.animation_history.append(
            {frame_num: {key: (value[:].copy() if value is not None else value) for key, value in
                         self.animation_part_list[frame_num].items()} for frame_num, _ in
             enumerate(self.animation_part_list)})

        self.body_part_history.append(
            {frame_num: {key: value for key, value in self.bodypart_list[frame_num].items()} for frame_num, _ in
             enumerate(self.bodypart_list)})

    def clear_history(self):
        self.part_name_history = [
            {frame_num: {key: value for key, value in self.part_name_list[frame_num].items()} for frame_num, _ in
             enumerate(self.part_name_list)}]
        self.animation_history = [
            {frame_num: {key: (value[:].copy() if value is not None else value) for key, value in
                         self.animation_part_list[frame_num].items()} for
             frame_num, _ in enumerate(self.animation_part_list)}]
        self.body_part_history = [
            {frame_num: {key: value for key, value in self.bodypart_list[frame_num].items()} for frame_num, _ in
             enumerate(self.bodypart_list)}]
        self.current_history = 0


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
            play_speed = self.speed_ms
            if any("play_time_mod_" in item for item in frame_property_select[self.show_frame]):
                play_speed *= float([item for item in frame_property_select[self.show_frame] if
                                   "play_time_mod_" in item][0].split("_")[-1])
            elif any("play_time_mod_" in item for item in anim_property_select):
                play_speed *= float([item for item in anim_property_select if "play_time_mod_" in item][0].split("_")[-1])
            if time.time() - self.first_time >= play_speed:
                self.show_frame += 1
                while self.show_frame < max_frame and play_list[self.show_frame] is False:
                    self.show_frame += 1
                self.first_time = time.time()
            if self.show_frame > self.end_frame:
                self.show_frame = self.start_frame
                while self.show_frame < max_frame and play_list[self.show_frame] is False:
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
copy_animation_stat = None
current_popup_row = 0
keypress_delay = 0
point_edit = 0
text_delay = 0
text_input_popup = (None, None)
current_pool = animation_pool_data

ui = pygame.sprite.LayeredUpdates()
fake_group = pygame.sprite.LayeredUpdates()  # just fake group to add for container and not get auto update

button_group = pygame.sprite.Group()
text_popup_group = pygame.sprite.Group()

Button.containers = button_group
SwitchButton.containers = button_group
popup.TextPopup.containers = text_popup_group

showroom_scale = (default_sprite_size[0] * 2, default_sprite_size[1] * 2)
showroom_scale_mul = (showroom_scale[0] / default_sprite_size[0], showroom_scale[1] / default_sprite_size[1])
showroom = Showroom(showroom_scale)
ui.add(showroom)

Joint.images = [
    pygame.transform.smoothscale(load_image(current_dir, screen_scale, "mainjoint.png", "animation_maker_ui"),
                                 (int(20 * screen_scale[0]), int(20 * screen_scale[1]))),
    pygame.transform.smoothscale(load_image(current_dir, screen_scale, "subjoint.png", "animation_maker_ui"),
                                 (int(20 * screen_scale[0]), int(20 * screen_scale[1])))]
joints = pygame.sprite.Group()

image = pygame.transform.smoothscale(load_image(current_dir, screen_scale, "film.png", "animation_maker_ui"),
                                     (int(50 * screen_scale[0]), int(50 * screen_scale[1])))

Filmstrip.base_image = image
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

filmstrip_list = [Filmstrip((0, 42 * screen_scale[1]))]

filmstrip_list += [Filmstrip((image.get_width() * this_index, 42 * screen_scale[1])) for this_index in
                   range(1, max_frame)]

filmstrips.add(*filmstrip_list)

images = load_images(current_dir, screen_scale=screen_scale, subfolder=("animation_maker_ui", "helper_parts"),
                     load_order=True)
body_helper_size = (450 * screen_scale[0], 270 * screen_scale[1])
effect_helper_size = (450 * screen_scale[0], 270 * screen_scale[1])
effect_helper = BodyHelper(effect_helper_size, (screen_size[0] / 1.25, screen_size[1] - (body_helper_size[1] / 2)),
                           "p1_effect", [images["smallbox_helper"]])
del images["smallbox_helper"]
p_body_helper = BodyHelper(body_helper_size, (body_helper_size[0] / 2,
                                              screen_size[1] - (body_helper_size[1] / 2)), "p1", list(images.values()))
helper_list = [p_body_helper, effect_helper]

image = load_image(current_dir, screen_scale, "button.png", "animation_maker_ui")
image = pygame.transform.smoothscale(image, (int(image.get_width() * screen_scale[1]),
                                             int(image.get_height() * screen_scale[1])))

text_popup = popup.TextPopup(screen_scale, screen_size)

animation_race_button = Button("Ani Race", image, (image.get_width() / 2, image.get_height() / 2),
                    description=("Select animation race type", "Select animation race type pool to edit."))
new_button = Button("New Ani", image, (image.get_width() * 1.5, image.get_height() / 2),
                    description=("Create new animation", "Create new empty animation with name input."))
save_button = Button("Save", image, (image.get_width() * 2.5, image.get_height() / 2),
                     description=("Save all animation", "Save the current state of all animation only for this race."))
size_button = Button("Size: ", image, (image.get_width() * 3.5, image.get_height() / 2),
                     description=(
                     "Change animation frame size", "This does not change the size of the animation editor UI."))

rename_button = Button("Rename", image, (screen_size[0] - (image.get_width() * 3.5), image.get_height() / 2),
                       description=("Rename animation",
                                    "Input will not be accepted if another animation with the input name exists."))
duplicate_button = Button("Duplicate", image, (screen_size[0] - (image.get_width() * 2.5), image.get_height() / 2),
                          description=("Duplicate animation", "Duplicate the current animation as a new animation."))
filter_button = Button("Filter", image, (screen_size[0] - (image.get_width() * 1.5), image.get_height() / 2),
                       description=("Filter animation list according to input", "Capital letter sensitive.",
                                    "Use ',' for multiple filters (e.g., Human,Slash).",
                                    "Add '--' in front of the keyword for exclusion instead of inclusion."))
export_button = Button("Export", image, (screen_size[0] - (image.get_width() * 1.5),
                                         p_body_helper.rect.midtop[1] - (image.get_height() * 5)),
                       description=("Export animation", "Export the current animation to several png image files."))

weapon_joint_to_hand_button = Button("W.J.T.H", image, (screen_size[0] - (image.get_width() * 3.5),
                                                        p_body_helper.rect.midtop[1] - (image.get_height() * 5)),
                       description=("Weapon Joint To Hand", "Move weapon to person hand part based on its joint.",
                                    "This affects weapon pos in game if fix property enable.",
                                    "Does not affect weapon part with 'sheath' name."))

delete_button = Button("Delete", image, (screen_size[0] - (image.get_width() / 2), image.get_height() / 2),
                       description=("Delete animation", "Delete the current animation."))

play_animation_button = SwitchButton(["Play", "Stop"], image,
                                     (screen_size[0] / 2,
                                      filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 0.6)),
                                     description=("Play/Stop animation",
                                                  "Preview the current animation with auto filmstrip selection."))

all_frame_part_copy_button = Button("Copy PA", image, (screen_size[0] / 2 - play_animation_button.image.get_width() * 2,
                                                       filmstrip_list[0].rect.midbottom[1] + (
                                                                   image.get_height() / 0.6)),
                                    description=("Copy selected parts in all frame",))
all_frame_part_paste_button = Button("Paste PA", image, (screen_size[0] / 2 - play_animation_button.image.get_width(),
                                                         filmstrip_list[0].rect.midbottom[1] + (
                                                                     image.get_height() / 0.6)),
                                     description=("Paste parts in all frame", "Only copied from all frame part copy."))

add_frame_button = Button("Add F", image, (play_animation_button.image.get_width() + screen_size[0] / 2,
                                           filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 0.6)),
                          description=(
                          "Add empty frame and move the other after frames", "Will remove the last frame."))

remove_frame_button = Button("Del F", image, ((play_animation_button.image.get_width() * 2) + screen_size[0] / 2,
                                              filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 0.6)),
                             description=("Remove current frame",))

joint_button = SwitchButton(["Joint:OFF", "Joint:ON"], image,
                            (play_animation_button.pos[0] + play_animation_button.image.get_width() * 5,
                             filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.6)),
                            description=("Show part joints", "Display or hide part's joint icon."))
grid_button = SwitchButton(["Grid:ON", "Grid:OFF"], image,
                           (play_animation_button.pos[0] + play_animation_button.image.get_width() * 6,
                            filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.6)),
                           description=("Show editor grid", "Display or hide animation editor grid."))
all_copy_button = Button("Copy A", image, (play_animation_button.pos[0] - (play_animation_button.image.get_width() * 2),
                                           filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.6)),
                         description=("Copy all frames",))
all_paste_button = Button("Paste A", image, (play_animation_button.pos[0] - play_animation_button.image.get_width(),
                                             filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.6)),
                          description=("Paste all copied frames",))
frame_copy_button = Button("Copy F", image, (play_animation_button.pos[0] + play_animation_button.image.get_width(),
                                             filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.6)),
                           description=(
                           "Copy frame (CTRL + C)", "Does not copy frame properties."))
frame_paste_button = Button("Paste F", image,
                            (play_animation_button.pos[0] + play_animation_button.image.get_width() * 2,
                             filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.6)),
                            description=("Paste copied frame (CTRL + V)",
                                         "Does not paste frame properties."))
speed_button = Button("Speed: 1", image, (screen_size[0] / 2,
                                          filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.6)),
                      description=("Change preview play speed", "Change according to the input number."))
default_button = Button("Default", image, (play_animation_button.pos[0] + play_animation_button.image.get_width() * 3,
                                           filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.6)),
                        description=("Reset frame to default", "Reset to the same as the default animation."))
help_button = SwitchButton(["Help:ON", "Help:OFF"], image,
                           (play_animation_button.pos[0] + play_animation_button.image.get_width() * 4,
                            filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.6)),
                           description=("Enable or disable help popup.",
                                        "Control for parts selection:", "Left Click on part = Part selection",
                                        "Shift + Left Click = Add selection", "CTRL + Left Click = Remove selection",
                                        "- (minus) or = (equal) = Previous or next frame",
                                        "[ or ] = Previous or next animation",
                                        "Control with selected parts: ", "W,A,S,D = Move", "Mouse Right = Place",
                                        "Hold mouse wheel or Q,E = Rotate", "DEL = Clear part",
                                        "Page Up/Down = Change layer"))
clear_button = Button("Clear", image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 3,
                                       filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.6)),
                      description=("Clear frame", "Clear the current frame."))
activate_button = SwitchButton(["Enable", "Disable"], image,
                               (play_animation_button.pos[0] - play_animation_button.image.get_width() * 4,
                                filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.6)),
                               description=("Enable or disable the current frame",
                                            "Disabled frame will be cleared when change animation",
                                            "and will not be saved."))
undo_button = Button("Undo", image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 5,
                                     filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.6)),
                     description=("Undo to previous edit (CTRL + Z)",
                                  "The undo also go back for other frame in the same animation."))
redo_button = Button("Redo", image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 6,
                                     filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.6)),
                     description=("Redo edit (CTRL + Y)", "Redo to last undo edit."))

reset_button = Button("Reset", image, (screen_size[0] / 2.1, p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)),
                      description=("Reset part edit", "Reset angle and flip."))
flip_hori_button = Button("Flip H", image, (reset_button.pos[0] + reset_button.image.get_width(),
                                            p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)),
                          description=("Horizontal Flip part", "Flip the selected part horizontally."))
flip_vert_button = Button("Flip V", image, (reset_button.pos[0] + (reset_button.image.get_width() * 2),
                                            p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)),
                          description=("Vertical Flip part", "Flip the selected part vertically."))
part_copy_button = Button("Copy P", image, (reset_button.pos[0] + reset_button.image.get_width() * 3,
                                            p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)),
                          description=("Copy parts (ALT + C)", "Copy the selected part only from this frame."))
part_paste_button = Button("Paste P", image, (reset_button.pos[0] + reset_button.image.get_width() * 4,
                                              p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)),
                           description=("Paste parts (ALT + V)", "Pasted the copied part only for this frame."))
part_stat_copy_button = Button("Copy PS", image, (reset_button.pos[0] + reset_button.image.get_width() * 5,
                                                  p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)),
                               description=("Copy parts 'stat", "Copy the stat of selected part."))
part_stat_paste_button = Button("Paste PS", image, (reset_button.pos[0] + reset_button.image.get_width() * 6,
                                                    p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)),
                                description=("Paste parts' stat", "Pasted the copied stats on same type of parts."))
p_all_button = Button("P All", image, (reset_button.pos[0] + reset_button.image.get_width() * 7,
                                       p_body_helper.rect.midtop[1] - (image.get_height() * 2)),
                      description=("Select all current person parts",))
all_button = Button("All", image, (reset_button.pos[0] + reset_button.image.get_width() * 6,
                                   p_body_helper.rect.midtop[1] - (image.get_height() * 2)),
                    description=("Select all parts",))
race_part_button = Button("", image, (reset_button.image.get_width() / 2,
                                      p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)),
                          description=("Select part type",
                                       "Select race for body part, weapon type for weapon part, and effect type for effect part"))
p_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 1.8,
                                                 p_body_helper.rect.midtop[1] - (image.get_height() * 5.2)),
                     description=("Select person to display in edit helper",
                                  "Parts from different person can still be selected in editor preview."))
armour_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 1.8,
                                                      p_body_helper.rect.midtop[1] - (image.get_height() * 4.2)),
                          description=("Select preview armour", "Only for preview and not saved in animation file."))
eye_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 1.8,
                                                   p_body_helper.rect.midtop[1] - (image.get_height() * 3.2)),
                       description=("Select person's eyes",
                                    "Select person eye for the specific animation frame, 'Any' eye will saved as 1.0 value."))
mouth_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 1.8,
                                                     p_body_helper.rect.midtop[1] - (image.get_height() * 2.2)),
                         description=("Select person's mouth", "Select person mouth for the specific animation frame, "
                                                               "'Any' mouth will saved as 1.0 value."))
# lock_button = SwitchButton(["Lock:OFF","Lock:ON"], image, (reset_button.pos[0] + reset_button.image.get_width() * 2,
#                                            p_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))

input_ui = menu.InputUI(screen_scale, load_image(main_dir, screen_scale, "input_ui.png", ("ui", "mainmenu_ui")),
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

confirm_ui = menu.InputUI(screen_scale, load_image(main_dir, screen_scale, "input_ui.png", ("ui", "mainmenu_ui")),
                          (screen_size[0] / 2, screen_size[1] / 2))  # user confirm input ui box popup
confirm_ui_popup = (confirm_ui, input_ok_button, input_cancel_button)

colour_ui = menu.InputUI(screen_scale, load_image(current_dir, screen_scale, "colour.png", "animation_maker_ui"),
                         (screen_size[0] / 2, screen_size[1] / 2))  # user text input ui box popup
colour_wheel = ColourWheel(load_image(main_dir, screen_scale, "rgb.png", "sprite"),
                           (colour_ui.pos[0], colour_ui.pos[1] / 1.5))
colour_input_box = menu.InputBox(screen_scale, (colour_ui.rect.center[0], colour_ui.rect.center[1] * 1.2),
                                 input_ui.image.get_width())  # user text input box

colour_ok_button = menu.MenuButton(screen_scale, image_list, pos=(colour_ui.rect.midleft[0] + image_list[0].get_width(),
                                                                  colour_ui.rect.midleft[1] + (
                                                                              image_list[0].get_height() * 2)),
                                   text="Confirm", layer=31)
colour_cancel_button = menu.MenuButton(screen_scale, image_list,
                                       pos=(colour_ui.rect.midright[0] - image_list[0].get_width(),
                                            colour_ui.rect.midright[1] + (image_list[0].get_height() * 2)),
                                       text="Cancel", layer=31)
colour_ui_popup = (colour_ui, colour_wheel, colour_input_box, colour_ok_button, colour_cancel_button)

box_img = load_image(current_dir, screen_scale, "property_box.png", "animation_maker_ui")
big_box_img = load_image(current_dir, screen_scale, "biglistbox.png", "animation_maker_ui")

menu.ListBox.containers = popup_list_box
popup_list_box = menu.ListBox(screen_scale, (0, 0), big_box_img, 16)  # popup box need to be in higher layer
battleui.UIScroll(popup_list_box, popup_list_box.rect.topright)  # create scroll for popup list box
anim_prop_list_box = menu.ListBox(screen_scale, (0, filmstrip_list[0].rect.midbottom[1] +
                                                 (reset_button.image.get_height() * 1.5)), box_img, 8)
anim_prop_list_box.namelist = anim_property_list + ["Custom"]
frame_prop_list_box = menu.ListBox(screen_scale,
                                   (screen_size[0] - box_img.get_width(), filmstrip_list[0].rect.midbottom[1] +
                                    (reset_button.image.get_height() * 1.5)), box_img, 8)
frame_prop_list_box.namelist = [frame_property_list + ["Custom"] for _ in range(max_frame)]
battleui.UIScroll(anim_prop_list_box, anim_prop_list_box.rect.topright)  # create scroll for animation prop box
battleui.UIScroll(frame_prop_list_box, frame_prop_list_box.rect.topright)  # create scroll for frame prop box
current_anim_row = 0
current_frame_row = 0
frame_property_select = [[] for _ in range(max_frame)]
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
all_copy_part = {}
all_copy_animation = {}
all_copy_name = {}
activate_list = [False] * max_frame

model.read_animation(animation_name)
animation_selector.change_name(animation_name)
if animation_name is not None:
    reload_animation(anim, model)
else:
    model.animation_list = [None] * max_frame
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
model.add_history()
animation_filter = [""]

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
                if popup_list_box in ui and (
                        popup_list_box.rect.collidepoint(mouse_pos) or popup_list_box.scroll.rect.collidepoint(
                        mouse_pos)):
                    current_popup_row = list_scroll(mouse_scroll_up, mouse_scroll_down,
                                                    popup_list_box, current_popup_row, popup_list_box.namelist,
                                                    popup_namegroup, ui, screen_scale)
                elif model.part_selected != [] and showroom.rect.collidepoint(mouse_pos):
                    if event.button == 4:  # Mouse scroll up
                        model.edit_part(mouse_pos, "scale_up")
                    else:  # Mouse scroll down
                        model.edit_part(mouse_pos, "scale_down")
                elif anim_prop_list_box.rect.collidepoint(mouse_pos) or anim_prop_list_box.scroll.rect.collidepoint(
                        mouse_pos):
                    current_anim_row = list_scroll(mouse_scroll_up, mouse_scroll_down,
                                                   anim_prop_list_box, current_anim_row, anim_prop_list_box.namelist,
                                                   anim_prop_namegroup, ui, screen_scale, old_list=anim_property_select)
                elif frame_prop_list_box.rect.collidepoint(mouse_pos) or frame_prop_list_box.scroll.rect.collidepoint(
                        mouse_pos):
                    current_frame_row = list_scroll(mouse_scroll_up, mouse_scroll_down,
                                                    frame_prop_list_box, current_frame_row,
                                                    frame_prop_list_box.namelist[current_frame], frame_prop_namegroup,
                                                    ui, screen_scale, old_list=frame_property_select[current_frame])
        elif event.type == pygame.KEYDOWN:
            if text_input_popup[0] == "text_input":
                if input_box in ui:
                    input_box.player_input(event, key_press)
                elif colour_input_box in ui:
                    colour_input_box.player_input(event, key_press)
                text_delay = 0.15

            elif event.key == pygame.K_ESCAPE:
                input_esc = True

    if text_input_popup[0] == "text_input" and text_delay == 0 and key_press[input_box.hold_key]:
        if input_box in ui:
            input_box.player_input(None, key_press)
        elif colour_input_box in ui:
            colour_input_box.player_input(None, key_press)
        text_delay = 0.1

    if pygame.mouse.get_pressed()[0]:  # Hold left click
        mouse_left_down = True
    elif pygame.mouse.get_pressed()[1]:  # Hold wheel click
        mouse_wheel_down = True
    elif pygame.mouse.get_pressed()[2]:  # Hold left click
        mouse_right_down = True

    ui.remove(text_popup)

    if text_delay > 0:
        text_delay += ui_dt
        if text_delay >= 0.3:
            text_delay = 0

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
            elif key_press[pygame.K_PAGEUP] or key_press[pygame.K_KP_PLUS]:
                keypress_delay = 0.1
                if model.part_selected:
                    model.edit_part(mouse_pos, "layer_up")
            elif key_press[pygame.K_PAGEDOWN] or key_press[pygame.K_KP_MINUS]:
                keypress_delay = 0.1
                if model.part_selected:
                    model.edit_part(mouse_pos, "layer_down")
            elif key_press[pygame.K_LEFTBRACKET] or key_press[pygame.K_RIGHTBRACKET]:
                if keypress_delay == 0:
                    keypress_delay = 0.1
                    animation_change = 1
                    if key_press[pygame.K_LEFTBRACKET]:
                        animation_change = -1
                    animation_list = list(current_pool[animation_race].keys())
                    if animation_filter[0] != "":
                        for key_filter in animation_filter:
                            if len(key_filter) > 0:
                                if key_filter[:2] == "--":  # exclude
                                    animation_list = [item for item in animation_list if key_filter[2:] not in item]
                                else:
                                    animation_list = [item for item in animation_list if key_filter in item]
                    try:
                        new_animation = animation_list[animation_list.index(animation_name) + animation_change]
                        change_animation(new_animation)
                    except (IndexError, ValueError):
                        if len(animation_list) > 0:
                            new_animation = animation_list[0]
                            change_animation(new_animation)
            elif key_press[pygame.K_MINUS] or key_press[pygame.K_EQUALS]:
                if keypress_delay == 0:
                    keypress_delay = 0.1
                    if key_press[pygame.K_MINUS]:
                        current_frame -= 1
                        if current_frame < 0:
                            current_frame = max_frame - 1
                    elif key_press[pygame.K_EQUALS]:
                        current_frame += 1
                        if current_frame > max_frame - 1:
                            current_frame = 0
                    change_frame_process()

        if mouse_timer != 0:  # player click mouse once before
            mouse_timer += ui_dt  # increase timer for mouse click using real time
            if mouse_timer >= 0.3:  # time pass 0.3 second no longer count as double click
                mouse_timer = 0

        if keypress_delay != 0:  # player press key once before
            keypress_delay += ui_dt
            if keypress_delay >= 0.3:
                keypress_delay = 0

        if mouse_left_up:
            if popup_list_box in ui:
                if popup_list_box.rect.collidepoint(mouse_pos):
                    popup_click = True
                    for index, name in enumerate(popup_namegroup):  # click on popup list
                        if name.rect.collidepoint(mouse_pos):
                            if popup_list_box.action == "part_select":
                                model.edit_part(mouse_pos, "part_" + name.name)
                            elif popup_list_box.action == "race_select":
                                model.edit_part(mouse_pos, "race_" + name.name)
                            elif "person" in popup_list_box.action:
                                p_body_helper.change_p_type(name.name, player_change=True)
                                effect_helper.change_p_type(name.name + "_effect", player_change=True)
                                p_selector.change_name(name.name)
                                armour_selector.change_name(model.armour[name.name + "_armour"])
                                face = [model.bodypart_list[current_frame][p_body_helper.ui_type + "_eye"],
                                        model.bodypart_list[current_frame][p_body_helper.ui_type + "_mouth"]]
                                head_text = ["Eye: ", "Mouth: "]
                                for index, selector in enumerate([eye_selector, mouth_selector]):
                                    this_text = "Any"
                                    if face[index] not in (0, 1):
                                        this_text = face[index]
                                    selector.change_name(head_text[index] + str(this_text))

                            elif "armour" in popup_list_box.action:
                                model.edit_part(mouse_pos, popup_list_box.action[0:3] + "armour_" + name.name)
                                armour_selector.change_name(name.name)
                            elif "eye" in popup_list_box.action:
                                eye_selector.change_name("Eye: " + name.name)
                                model.edit_part(mouse_pos, popup_list_box.action[0:3] + "eye_" + name.name)
                            elif "mouth" in popup_list_box.action:
                                mouth_selector.change_name("Mouth: " + name.name)
                                model.edit_part(mouse_pos, popup_list_box.action[0:3] + "mouth_" + name.name)
                            elif popup_list_box.action == "animation_race_select":
                                if name.name == "New Race":
                                    text_input_popup = ("text_input", "new_race")
                                    input_ui.change_instruction("Enter Race Name:")
                                    input_box.text_start("")
                                    ui.add(input_ui_popup)
                                elif animation_race != name.name:
                                    change_animation_race(name.name)
                            elif popup_list_box.action == "animation_select":
                                if animation_name != name.name:
                                    change_animation(name.name)
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

                elif help_button.rect.collidepoint(mouse_pos):
                    if help_button.current_option == 0:  # disable help
                        help_button.change_option(1)
                    else:
                        help_button.change_option(0)

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
                        setup_list(menu.NameList, current_frame_row, frame_prop_list_box.namelist[current_frame],
                                   frame_prop_namegroup,
                                   frame_prop_list_box, ui, screen_scale, layer=9,
                                   old_list=frame_property_select[current_frame])

                elif anim_prop_list_box.rect.collidepoint(mouse_pos) or frame_prop_list_box.rect.collidepoint(
                        mouse_pos):
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
                            if name.selected:  # unselect
                                name.select()
                                select_list.remove(name.name)
                                reload_animation(anim, model)
                            else:
                                if name.name == "Custom":
                                    text_input_popup = ("text_input", "new_anim_prop")
                                    input_ui.change_instruction("Custom Property:")
                                    ui.add(input_ui_popup)
                                elif name.name[-1] == "_" or name.name[-1].isdigit():  # property that need number value
                                    if name.selected is False:
                                        if "colour" in name.name:
                                            text_input_popup = ("text_input", naming + "_prop_colour_" + name.name)
                                            ui.add(colour_ui_popup)
                                        else:
                                            text_input_popup = ("text_input", naming + "_prop_num_" + name.name)
                                            input_ui.change_instruction("Input Number Value:")
                                            ui.add(input_ui_popup)
                                else:
                                    name.select()
                                    select_list.append(name.name)
                                    setup_list(menu.NameList, current_frame_row, namelist, namegroup,
                                               list_box, ui, screen_scale, layer=9, old_list=select_list)
                                    reload_animation(anim, model)
                            property_to_pool_data(naming)

        if play_animation:
            current_frame = int(anim.show_frame)
            setup_list(menu.NameList, current_anim_row, anim_prop_list_box.namelist, anim_prop_namegroup,
                       anim_prop_list_box, ui, screen_scale, layer=9, old_list=anim_property_select)
            setup_list(menu.NameList, current_frame_row, frame_prop_list_box.namelist[current_frame],
                       frame_prop_namegroup,
                       frame_prop_list_box, ui, screen_scale, layer=9,
                       old_list=frame_property_select[current_frame])
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
                                if type(value) is not list:
                                    frame_item[key] = value
                                else:
                                    frame_item[key] = value.copy()
                            copy_list.append(frame_item)

                    elif all_paste_button.rect.collidepoint(mouse_pos):
                        if copy_list:
                            frame_property_select = [[] for _ in range(max_frame)]
                            anim_property_select = []
                            for frame_index, frame in enumerate(copy_list):
                                old_size = model.frame_list[frame_index]["size"]
                                model.frame_list[frame_index] = {key: value.copy() if type(value) is list else value for
                                                                 key, value in frame.items()}
                                model.frame_list[frame_index]["size"] = old_size
                            model.read_animation(animation_name, old=True)
                            reload_animation(anim, model)

                            model.edit_part(mouse_pos, "change")

                    elif all_frame_part_copy_button.rect.collidepoint(mouse_pos):
                        if model.part_selected:
                            for frame in range(len(model.frame_list)):
                                all_copy_part[frame] = {key: (value[:].copy() if type(value) is list else value) for
                                                        key, value in
                                                        model.bodypart_list[frame].items()}
                                all_copy_animation[frame] = {key: (value[:].copy() if value is not None else value) for
                                                             key, value in
                                                             model.animation_part_list[frame].items()}
                                all_copy_name[frame] = {key: (value[:].copy() if value is not None else value) for
                                                        key, value in
                                                        model.part_name_list[frame].items()}

                                # keep only selected one
                                all_copy_part[frame] = {item: all_copy_part[frame][item] for item in all_copy_part[frame] if
                                     item in model.mask_part_list and list(model.mask_part_list.keys()).index(
                                         item) in model.part_selected}
                                all_copy_animation[frame] = {item: all_copy_animation[frame][item] for index, item in
                                                             enumerate(all_copy_animation[frame].keys())
                                                             if
                                                             index in model.part_selected}
                                all_copy_name[frame] = {item: all_copy_name[frame][item] for index, item in
                                                        enumerate(all_copy_name[frame].keys()) if
                                                        index in model.part_selected}

                    elif all_frame_part_paste_button.rect.collidepoint(mouse_pos):
                        if all_copy_part:
                            model.edit_part(mouse_pos, "all frame selected part paste")

                    elif add_frame_button.rect.collidepoint(mouse_pos):
                        model.add_history()
                        change_frame = len(model.bodypart_list) - 1
                        frame_property_select = [[] for _ in range(max_frame)]
                        while change_frame > current_frame:
                            model.frame_list[change_frame] = {key: value.copy() if type(value) is list else value for
                                                              key, value
                                                              in model.frame_list[change_frame - 1].items()}
                            model.read_animation(animation_name, old=True)
                            change_frame -= 1
                        model.edit_part(mouse_pos, "clear")
                        model.edit_part(mouse_pos, "change")
                        reload_animation(anim, model)

                        for strip_index, strip in enumerate(filmstrips):  # enable frame that not empty
                            for stuff in model.animation_part_list[strip_index].values():
                                if stuff is not None:
                                    strip.activate = True
                                    activate_list[strip_index] = True
                                    strip.add_strip(change=False)
                                    break

                    elif remove_frame_button.rect.collidepoint(mouse_pos):
                        model.add_history()
                        change_frame = current_frame
                        frame_property_select = [[] for _ in range(max_frame)]
                        while change_frame < len(model.bodypart_list) - 1:
                            model.frame_list[change_frame] = model.frame_list[change_frame + 1]
                            model.read_animation(animation_name, old=True)
                            change_frame += 1
                        model.edit_part(mouse_pos, "clear", specific_frame=len(model.bodypart_list) - 1)
                        model.edit_part(mouse_pos, "change")
                        reload_animation(anim, model)

                        for strip_index, strip in enumerate(filmstrips):  # enable frame that not empty
                            for stuff in model.animation_part_list[strip_index].values():
                                if stuff is not None:
                                    strip.activate = True
                                    activate_list[strip_index] = True
                                    strip.add_strip(change=False)
                                    break

                    elif frame_copy_button.rect.collidepoint(mouse_pos):
                        copy_press = True

                    elif frame_paste_button.rect.collidepoint(mouse_pos):
                        paste_press = True

                    elif part_copy_button.rect.collidepoint(mouse_pos):
                        part_copy_press = True

                    elif part_paste_button.rect.collidepoint(mouse_pos):
                        part_paste_press = True

                    elif part_stat_copy_button.rect.collidepoint(mouse_pos):
                        if model.part_selected:
                            copy_part_stat = {key: (value[:].copy() if type(value) is list else value) for key, value in
                                              model.bodypart_list[current_frame].items()}
                            copy_animation_stat = {key: (value[:].copy() if value is not None else value) for key, value
                                                   in
                                                   model.animation_part_list[current_frame].items()}
                            copy_name_stat = {key: (value[:].copy() if value is not None else value) for key, value in
                                              model.part_name_list[current_frame].items()}

                            # keep only selected one
                            copy_part_stat = {item: copy_part_stat[item] for item in copy_part_stat if
                                              item in model.mask_part_list and list(model.mask_part_list.keys()).index(
                                                  item) in model.part_selected}
                            copy_animation_stat = {item: copy_animation_stat[item] for index, item in
                                                   enumerate(copy_animation_stat.keys()) if
                                                   index in model.part_selected}
                            copy_name_stat = {item: copy_name_stat[item] for index, item in
                                              enumerate(copy_name_stat.keys()) if index in model.part_selected}

                    elif part_stat_paste_button.rect.collidepoint(mouse_pos):
                        if copy_animation_stat is not None:
                            model.edit_part(mouse_pos, "paste part stat")

                    elif p_all_button.rect.collidepoint(mouse_pos):
                        part_change = p_body_helper.ui_type + "_"
                        for part in model.mask_part_list:
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
                                if list(model.mask_part_list.keys())[part] in helper.rect_part_list:
                                    helper.select_part(mouse_pos, True, False,
                                                       specific_part=list(model.mask_part_list.keys())[part])

                    elif all_button.rect.collidepoint(mouse_pos):
                        for part in model.mask_part_list:
                            if ctrl_press is False:  # add all parts
                                model.click_part(mouse_pos, True, ctrl_press, part)
                            else:
                                model.click_part(mouse_pos, False, ctrl_press, part)
                        for part in model.part_selected:
                            for helper in helper_list:
                                if list(model.mask_part_list.keys())[part] in helper.rect_part_list:
                                    helper.select_part(mouse_pos, True, False,
                                                       specific_part=list(model.mask_part_list.keys())[part])
                                    break

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
                                anim_to_pool(animation_name, current_pool[animation_race], model, activate_list)
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
                        text_input_popup = ("text_input", "duplicate_animation")
                        input_ui.change_instruction("Duplicate Current Animation?")
                        last_char = str(1)
                        if animation_name + "(copy" + last_char + ")" in current_pool[animation_race]:  # copy exist
                            while animation_name + "(copy" + last_char + ")" in current_pool[animation_race]:
                                last_char = str(int(last_char) + 1)
                        elif "(copy" in animation_name and animation_name[-2].isdigit() and animation_name[-1] == ")":
                            last_char = str(int(animation_name[-2]) + 1)
                        input_box.text_start(animation_name + "(copy" + last_char + ")")

                        ui.add(input_ui_popup)

                    elif filter_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("text_input", "filter")
                        input_ui.change_instruction("Input text filters:")
                        input_filter = str(animation_filter)
                        for character in "'[]":
                            input_filter = input_filter.replace(character, "")
                        input_filter = input_filter.replace(", ", ",")
                        input_box.text_start(input_filter)
                        ui.add(input_ui_popup)

                    elif export_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("confirm_input", "export_animation")
                        input_ui.change_instruction("Export to PNG Files?")
                        ui.add(input_ui_popup)

                    elif weapon_joint_to_hand_button.rect.collidepoint(mouse_pos):
                        model.edit_part(mouse_pos, "weapon joint to hand")

                    elif flip_hori_button.rect.collidepoint(mouse_pos):
                        model.edit_part(mouse_pos, "flip1")

                    elif flip_vert_button.rect.collidepoint(mouse_pos):
                        model.edit_part(mouse_pos, "flip2")

                    elif reset_button.rect.collidepoint(mouse_pos):
                        model.edit_part(mouse_pos, "reset")

                    elif part_selector.rect.collidepoint(mouse_pos):
                        if race_part_button.text != "":
                            current_part = list(model.animation_part_list[current_frame].keys())[
                                model.part_selected[-1]]
                            try:
                                if "special" in current_part:
                                    part_list = list(
                                        gen_body_sprite_pool[race_part_button.text]["special"].keys())
                                elif any(ext in current_part for ext in p_list):
                                    selected_part = current_part[3:]
                                    if selected_part[0:2] == "r_" or selected_part[0:2] == "l_":
                                        selected_part = selected_part[2:]
                                    part_list = list(
                                        gen_body_sprite_pool[race_part_button.text][selected_part].keys())
                                elif "effect" in current_part:
                                    part_list = list(
                                        effect_sprite_pool[race_part_button.text].keys())

                            except KeyError:  # look at weapon next
                                try:
                                    selected_part = race_part_button.text
                                    part_list = list(
                                        gen_weapon_sprite_pool[selected_part].keys())
                                except KeyError:  # part not exist
                                    part_list = []
                            popup_list_open(popup_list_box, popup_namegroup, ui, "part_select",
                                            part_selector.rect.topleft, part_list, "bottom", screen_scale)

                    elif p_selector.rect.collidepoint(mouse_pos):
                        popup_list_open(popup_list_box, popup_namegroup, ui, "person_select",
                                        p_selector.rect.topleft, p_list, "bottom", screen_scale)
                    elif armour_selector.rect.collidepoint(mouse_pos):
                        armour_part_list = []
                        for item in list(gen_armour_sprite_pool[model.body_race[p_body_helper.ui_type]].keys()):
                            for armour in gen_armour_sprite_pool[model.body_race[p_body_helper.ui_type]][item]:
                                armour_part_list.append(item + "/" + armour)
                        part_list = ["None"] + armour_part_list
                        popup_list_open(popup_list_box, popup_namegroup, ui, p_body_helper.ui_type + "_armour_select",
                                        armour_selector.rect.topleft, part_list, "bottom", screen_scale)

                    elif eye_selector.rect.collidepoint(mouse_pos) and model.bodypart_list[current_frame][
                        p_body_helper.ui_type + "_head"] is not None:
                        part_list = ["Any"]
                        if "eye" in gen_body_sprite_pool[model.head_race[p_body_helper.ui_type]]:
                            part_list = ["Any"] + list(gen_body_sprite_pool[model.head_race[p_body_helper.ui_type]][
                                                           "eye"].keys())
                        popup_list_open(popup_list_box, popup_namegroup, ui, p_body_helper.ui_type + "_eye_select",
                                        eye_selector.rect.topleft, part_list, "bottom", screen_scale)

                    elif mouth_selector.rect.collidepoint(mouse_pos) and model.bodypart_list[current_frame][
                        p_body_helper.ui_type + "_head"] is not None:
                        ui_type = p_body_helper.ui_type
                        part_list = ["Any"]
                        if "mouth" in gen_body_sprite_pool[model.head_race[p_body_helper.ui_type]]:

                            part_list = ["Any"] + list(gen_body_sprite_pool[model.head_race[p_body_helper.ui_type]][
                                                           "mouth"].keys())
                        popup_list_open(popup_list_box, popup_namegroup, ui, ui_type + "_mouth_select",
                                        mouth_selector.rect.topleft, part_list, "bottom", screen_scale)

                    elif race_part_button.rect.collidepoint(mouse_pos):
                        if model.part_selected:
                            current_part = list(model.mask_part_list.keys())[model.part_selected[-1]]
                            if "weapon" in current_part:
                                part_list = list(gen_weapon_sprite_pool)
                            elif "effect" in current_part:
                                part_list = list(effect_sprite_pool)
                            else:
                                part_list = list(gen_body_sprite_pool.keys())
                            popup_list_open(popup_list_box, popup_namegroup, ui, "race_select",
                                            race_part_button.rect.topleft, part_list, "bottom", screen_scale)

                    elif animation_race_button.rect.collidepoint(mouse_pos):
                        current_popup_row = 0  # move current selected animation to top if not in filtered list
                        popup_list_open(popup_list_box, popup_namegroup, ui, "animation_race_select",
                                        (animation_race_button.rect.bottomleft[0],
                                         animation_race_button.rect.bottomleft[1]),
                                        ["New Race"] + [key for key in current_pool if key != "template"],
                                        "top", screen_scale, current_row=current_popup_row)

                    elif new_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("text_input", "new_animation")
                        input_ui.change_instruction("New Animation Name:")
                        ui.add(input_ui_popup)

                    elif save_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("confirm_input", "save_animation")
                        input_ui.change_instruction("Save This Race Animation?")
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
                        animation_list = list(current_pool[animation_race].keys())
                        if animation_filter[0] != "":
                            for key_filter in animation_filter:
                                if len(key_filter) > 0:
                                    if key_filter[:2] == "--":  # exclude
                                        animation_list = [item for item in animation_list if key_filter[2:] not in item]
                                    else:
                                        animation_list = [item for item in animation_list if key_filter in item]
                        current_popup_row = 0  # move current selected animation to top if not in filtered list
                        if animation_name in animation_list:
                            current_popup_row = animation_list.index(animation_name)
                        popup_list_open(popup_list_box, popup_namegroup, ui, "animation_select",
                                        (animation_selector.rect.bottomleft[0] - 100,
                                         animation_selector.rect.bottomleft[1]),
                                        animation_list, "top", screen_scale,
                                        current_row=current_popup_row)

                    else:  # click on other stuff
                        for strip_index, strip in enumerate(filmstrips):  # click on frame film list
                            if strip.rect.collidepoint(mouse_pos) and current_frame != strip_index:  # click new frame
                                current_frame = strip_index
                                change_frame_process()

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
                            mouse_pos = pygame.Vector2(
                                (mouse_pos[0] - helper_click.rect.topleft[0]),
                                (mouse_pos[1] - helper_click.rect.topleft[1]))
                            this_part = helper_click.select_part(mouse_pos, shift_press, ctrl_press)
                            if shift_press is False and ctrl_press is False:  # remove selected part in other helpers
                                model.part_selected = []  # clear old list first
                                for index, helper in enumerate(helper_list):
                                    if helper != helper_click:
                                        helper.select_part(None, False, True)
                            elif this_part is not None and ctrl_press and tuple(model.mask_part_list.keys()).index(this_part) in model.part_selected:
                                model.part_selected.remove(tuple(model.mask_part_list.keys()).index(this_part))  # clear old list first
                            for index, helper in enumerate(helper_list):  # add selected part to model selected
                                if helper.part_selected:
                                    for part in helper.part_selected:
                                        model.click_part(mouse_pos, True, False, part)

                if copy_press:
                    copy_part_frame = {key: (value[:].copy() if type(value) is list else value) for key, value in
                                       model.bodypart_list[current_frame].items()}
                    copy_animation_frame = {key: (value[:].copy() if value is not None else value) for key, value in
                                            model.animation_part_list[current_frame].items()}
                    copy_name_frame = {key: (value[:].copy() if value is not None else value) for key, value in
                                       model.part_name_list[current_frame].items()}

                elif paste_press:
                    if copy_animation_frame is not None:
                        model.add_history()
                        model.bodypart_list[current_frame] = {key: (value[:].copy() if type(value) is list else value)
                                                              for key, value in
                                                              copy_part_frame.items()}
                        model.animation_part_list[current_frame] = {
                            key: (value[:].copy() if value is not None else value) for key, value in
                            copy_animation_frame.items()}
                        model.part_name_list[current_frame] = {key: (value[:].copy() if value is not None else value)
                                                               for key, value in
                                                               copy_name_frame.items()}
                        model.edit_part(mouse_pos, "change")

                elif part_copy_press:
                    if model.part_selected:
                        copy_part = {key: (value[:].copy() if type(value) is list else value) for key, value in
                                     model.bodypart_list[current_frame].items()}
                        copy_animation = {key: (value[:].copy() if value is not None else value) for key, value in
                                          model.animation_part_list[current_frame].items()}
                        copy_name = {key: (value[:].copy() if value is not None else value) for key, value in
                                     model.part_name_list[current_frame].items()}

                        # keep only selected one
                        copy_part = {item: copy_part[item] for item in copy_part if
                                     item in model.mask_part_list and list(model.mask_part_list.keys()).index(
                                         item) in model.part_selected}
                        copy_animation = {item: copy_animation[item] for index, item in enumerate(copy_animation.keys())
                                          if
                                          index in model.part_selected}
                        copy_name = {item: copy_name[item] for index, item in enumerate(copy_name.keys()) if
                                     index in model.part_selected}

                elif part_paste_press:
                    if copy_part is not None:
                        model.edit_part(mouse_pos, "paste")

                elif undo_press:
                    if model.current_history > 0:
                        model.current_history -= 1
                        model.edit_part(None, "undo")

                elif redo_press:
                    if len(model.animation_history) - 1 > model.current_history:
                        model.current_history += 1
                        model.edit_part(None, "redo")

                if showroom.rect.collidepoint(mouse_pos):  # mouse at showroom
                    new_mouse_pos = pygame.Vector2(
                        (mouse_pos[0] - showroom.rect.topleft[0]) / 2 * model.size,
                        (mouse_pos[1] - showroom.rect.topleft[1]) / 2 * model.size)
                    if mouse_left_up:  # left click on showroom
                        model.click_part(new_mouse_pos, shift_press, ctrl_press)
                        for index, helper in enumerate(helper_list):
                            helper.select_part(None, shift_press, ctrl_press)
                            if model.part_selected:
                                for part in model.part_selected:
                                    if list(model.mask_part_list.keys())[part] in helper.rect_part_list:
                                        helper.select_part(mouse_pos, True, False,
                                                           specific_part=list(model.mask_part_list.keys())[part])
                    if mouse_wheel_up or mouse_wheel_down:
                        model.edit_part(new_mouse_pos, "rotate")
                    elif mouse_right_up or mouse_right_down:
                        if mouse_right_down:
                            if keypress_delay == 0:
                                model.edit_part(new_mouse_pos, "place")
                                keypress_delay = 0.1
                        else:
                            model.edit_part(new_mouse_pos, "place")

            if model.part_selected:
                part = model.part_selected[-1]
                if model.animation_part_list[current_frame] is not None and \
                        list(model.mask_part_list.keys())[part] in list(
                    model.animation_part_list[current_frame].keys()):
                    name_text = model.part_name_list[current_frame][list(model.mask_part_list.keys())[part]]
                    if name_text is None:
                        name_text = ["", ""]
                    race_part_button.change_text(name_text[0])
                    part_selector.change_name(name_text[1])
                else:
                    race_part_button.change_text("")
                    part_selector.change_name("")
            elif race_part_button.text != "":
                race_part_button.change_text("")
                part_selector.change_name("")
    else:  # input box function
        dt = 0
        if (input_ok_button in ui and input_ok_button.event) or (colour_ok_button in ui and colour_ok_button.event) or \
                key_press[pygame.K_RETURN] or key_press[pygame.K_KP_ENTER]:
            input_ok_button.event = False
            colour_ok_button.event = False

            if text_input_popup[1] == "new_animation":
                if input_box.text not in current_pool[animation_race]:  # no existing name already
                    animation_name = input_box.text
                    animation_selector.change_name(animation_name)
                    current_frame = 0
                    model.edit_part(mouse_pos, "new")
                    change_animation(animation_name)

            elif text_input_popup[1] == "new_race":
                if input_box.text not in current_pool:  # no existing name already
                    animation_race = input_box.text
                    current_pool[animation_race] = {key: value.copy() for key, value in current_pool["template"].items()}
                    for key in current_pool[animation_race]:
                        for index in range(len(current_pool[animation_race][key])):
                            current_pool[animation_race][key][index] = {key2: value2.copy() if type(value2) is list else value2 for key2, value2 in
                                                                        current_pool[animation_race][key][index].items()}
                    change_animation_race(animation_race)

            elif text_input_popup[1] == "save_animation":
                anim_save_pool(current_pool[animation_race], animation_race, anim_column_header)

            elif text_input_popup[1] == "new_name":
                old_name = animation_name
                if input_box.text not in current_pool[animation_race]:  # no existing name already
                    animation_name = input_box.text
                    animation_selector.change_name(animation_name)
                    anim_to_pool(animation_name, current_pool[animation_race], model, activate_list, replace=old_name)

            elif text_input_popup[1] == "export_animation":
                for index, frame in enumerate(anim.frames):
                    if activate_list[index]:
                        pygame.image.save(frame, animation_name + "_" + str(index + 1) + ".png")

            elif text_input_popup[1] == "duplicate_animation":
                old_name = animation_name
                if input_box.text not in current_pool[animation_race]:  # no existing name already
                    animation_name = input_box.text
                    animation_selector.change_name(animation_name)
                    anim_to_pool(animation_name, current_pool[animation_race], model, activate_list, duplicate=old_name)
                    model.read_animation(animation_name)
                    model.clear_history()

            elif text_input_popup[1] == "del_animation":
                anim_del_pool(current_pool[animation_race], animation_name)
                if len(current_pool[animation_race]) == 0:  # no animation left, create empty one
                    animation_name = "empty"
                    animation_selector.change_name(animation_name)
                    current_frame = 0
                    model.edit_part(mouse_pos, "new")
                else:  # reset to the first animation
                    change_animation(list(current_pool[animation_race].keys())[0])

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
                setup_list(menu.NameList, current_frame_row, frame_prop_list_box.namelist[current_frame],
                           frame_prop_namegroup,
                           frame_prop_list_box, ui, screen_scale, layer=9,
                           old_list=frame_property_select[current_frame])
                select_list = frame_property_select[current_frame]
                property_to_pool_data("frame")

            elif "_prop_num" in text_input_popup[1] and (
                    input_box.text.isdigit() or "." in input_box.text and re.search("[a-zA-Z]",
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
                namegroup = anim_prop_namegroup
                naming = "anim"
                list_box = anim_prop_list_box
                name_list = list_box.namelist
                select_list = anim_property_select
                if "frame" in text_input_popup[1]:  # click on frame property list
                    namegroup = frame_prop_namegroup
                    naming = "frame"
                    list_box = frame_prop_list_box
                    name_list = list_box.namelist[current_frame]
                    select_list = frame_property_select[current_frame]
                colour = colour_input_box.text.replace(" ", "")
                colour = colour.replace(",", ".")
                for name in name_list:
                    if name in (text_input_popup[1]):
                        if naming == "frame":
                            index = name_list.index(name)
                        elif naming == "anim":
                            index = name_list.index(name)

                        name_list[index] = name[0:name.rfind("_") + 1] + colour
                        select_list.append(name[0:name.rfind("_") + 1] + colour)
                        setup_list(menu.NameList, current_frame_row, name_list, namegroup, list_box, ui, screen_scale,
                                   layer=9, old_list=select_list)
                        reload_animation(anim, model)
                        property_to_pool_data(naming)
                        break

            elif text_input_popup[1] == "change_size" and input_box.text.isdigit():
                if int(input_box.text) != model.frame_list[0]["size"]:
                    model.frame_list[0]["size"] = int(input_box.text)
                    model.change_size()
                    model.read_animation(animation_name, old=True)
                    reload_animation(anim, model)

            elif text_input_popup[1] == "filter":
                animation_filter = input_box.text.split(",")

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

        elif (input_cancel_button in ui and input_cancel_button.event) or (
                colour_cancel_button in ui and colour_cancel_button.event) or input_esc:
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
