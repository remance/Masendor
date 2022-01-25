import csv
import math
import os
import random
import re
import time
import sys
from pathlib import Path

import pygame
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

current_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = current_dir[:current_dir.rfind("\\")+1]
sys.path.insert(1, main_dir)

from gamescript import readstat, menu, battleui
from gamescript.common import utility

rotation_xy = utility.rotation_xy
load_image = utility.load_image
load_images = utility.load_images
load_base_button = utility.load_base_button
stat_convert = readstat.stat_convert



default_sprite_size = (200, 200)

screen_size = (1000, 1000)
screen_scale = (screen_size[0] / 1000, screen_size[1] / 1000)

pygame.init()
pen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Animation Maker")  # set the self name on program border/tab
pygame.mouse.set_visible(True)  # set mouse as visible

direction_list = ("front", "side", "back", "sideup", "sidedown")
anim_column_header = ["Name", "p1_head", "p1_eye", "p1_mouth", "p1_body", "p1_r_arm_up", "p1_r_arm_low", "p1_r_hand", "p1_l_arm_up",
                      "p1_l_arm_low", "p1_l_hand", "p1_r_leg", "p1_r_foot", "p1_l_leg", "p1_l_foot", "p1_main_weapon", "p1_sub_weapon",
                      "p2_head", "p2_eye", "p2_mouth", "p2_body", "p2_r_arm_up", "p2_r_arm_low", "p2_r_hand", "p2_l_arm_up",
                      "p2_l_arm_low", "p2_l_hand", "p2_r_leg", "p2_r_foot", "p2_l_leg", "p2_l_foot", "p2_main_weapon", "p2_sub_weapon",
                      "effect_1", "effect_2", "dmg_effect_1", "dmg_effect_2", "special_1", "special_2", "special_3", "special_4",
                      "special_5", "size", "frame_property", "animation_property"]  # For csv saving
frame_property_list = ["hold", "p1_turret", "p2_turret", "effect_blur_", "effect_contrast_", "effect_brightness_", "effect_fade_",
                       "effect_grey", "effect_colour_"]
anim_property_list = ["dmgsprite", "interuptrevert"]

# TODO animation After 1.0: unique, lock?, cloth sample


def apply_colour(surface, colour=None):
    """Colorise body part sprite"""
    size = (surface.get_width(), surface.get_height())
    data = pygame.image.tostring(surface, "RGBA")  # convert image to string data for filtering effect
    surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data
    alpha = surface.split()[-1]  # save alpha
    surface = surface.convert("L")  # convert to grey scale for colourise
    if colour is not None:
        max_colour = 255  # - (colour[0] + colour[1] + colour[2])
        mid_colour = [int(c - ((max_colour - c) / 2)) for c in colour]
        surface = ImageOps.colorize(surface, black="black", mid=mid_colour, white=colour).convert("RGB")
    surface.putalpha(alpha)  # put back alpha
    surface = surface.tobytes()
    surface = pygame.image.fromstring(surface, size, "RGBA")  # convert image back to a pygame surface
    return surface


def setup_list(item_class, current_row, show_list, item_group, box, ui_class, layer=1, remove_old=True, old_list=None):
    """generate list of list item"""
    width_adjust = screen_scale[0]
    height_adjust = screen_scale[1]
    row = 5 * height_adjust
    column = 5 * width_adjust
    pos = box.rect.topleft
    if current_row > len(show_list) - box.max_show:
        current_row = len(show_list) - box.max_show

    if len(item_group) > 0 and remove_old:  # remove previous sprite in the group before generate new one
        for stuff in item_group:
            stuff.kill()
            del stuff
    add_row = 0
    for index, item in enumerate(show_list):
        if index >= current_row:
            item_group.add(item_class(screen_scale, box, (pos[0] + column, pos[1] + row), item,
                                      layer=layer))  # add new subsection sprite to group
            row += (30 * height_adjust)  # next row
            add_row += 1
            if add_row > box.max_show:
                break  # will not generate more than space allowed

        ui_class.add(*item_group)
    if old_list is not None:
        for item in item_group:
            if item.name in old_list:
                item.select()


def list_scroll(scroll, listbox, current_row, name_list, name_group, ui_object, layer=19, old_list=None):
    if mouse_scroll_up:
        current_row -= 1
        if current_row < 0:
            current_row = 0
        else:
            setup_list(menu.NameList, current_row, name_list, name_group, listbox, ui_object, layer=layer, old_list=old_list)
            scroll.change_image(new_row=current_row, log_size=len(name_list))

    elif mouse_scroll_down:
        current_row += 1
        if current_row + listbox.max_show - 1 < len(name_list):
            setup_list(menu.NameList, current_row, name_list, name_group, listbox, ui_object, layer=layer,
                       old_list=old_list)
            scroll.change_image(new_row=current_row, log_size=len(name_list))
        else:
            current_row -= 1
    return current_row


def popup_list_open(action, new_rect, new_list, ui_type):
    """Move popup_listbox and scroll sprite to new location and create new name list based on type"""

    if ui_type == "top":
        popup_listbox.rect = popup_listbox.image.get_rect(topleft=new_rect)
    elif ui_type == "bottom":
        popup_listbox.rect = popup_listbox.image.get_rect(bottomleft=new_rect)
    popup_listbox.namelist = new_list
    popup_listbox.action = action
    setup_list(menu.NameList, 0, new_list, popup_namegroup,
               popup_listbox, ui, layer=19)

    popup_listscroll.pos = popup_listbox.rect.topright  # change position variable
    popup_listscroll.rect = popup_listscroll.image.get_rect(topleft=popup_listbox.rect.topright)
    popup_listscroll.change_image(new_row=0, log_size=len(new_list))
    ui.add(popup_listbox, *popup_namegroup, popup_listscroll)

    popup_listbox.type = ui_type


def load_textures(main_dir, subfolder=None):
    """loads all body sprite part image"""
    imgs = {}
    dir_path = os.path.join(main_dir, "data")
    if subfolder is not None:
        for folder in subfolder:
            dir_path = os.path.join(dir_path, folder)

    loadorderfile = [f for f in os.listdir(dir_path) if f.endswith("." + "png")]  # read all file
    loadorderfile.sort(key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r"[^0-9]|[0-9]+", var)])
    for file in loadorderfile:
        imgs[file.split(".")[0]] = load_image(main_dir, screen_scale, file, dir_path)

    return imgs


def reload_animation(animation, char):
    """Reload animation frames"""
    frames = [pygame.transform.smoothscale(thisimage, showroom.size) for thisimage in char.animation_list if thisimage is not None]
    face = [char.frame_list[current_frame]["p1_eye"], char.frame_list[current_frame]["p1_mouth"],
            char.frame_list[current_frame]["p2_eye"], char.frame_list[current_frame]["p2_mouth"]]
    head_text = ["P1 Eye: ", "P1 Mouth: ", "P2 Eye: ", "P2 Mouth: "]
    for index, selector in enumerate([p1_eye_selector, p1_mouth_selector, p2_eye_selector, p2_mouth_selector]):
        this_text = "Any"
        if face[index] not in (0, 1):
            this_text = face[index]
        selector.change_name(head_text[index] + str(this_text))
    for frame_index in range(0, 10):
        for prop in frame_property_select[frame_index]:
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
                surface = Image.frombytes("RGBA", (frames[frame_index].get_width(), frames[frame_index].get_height()),
                                          data)  # use PIL to get image data
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
                    empty = pygame.Surface((frames[frame_index].get_width(), frames[frame_index].get_height()), pygame.SRCALPHA)
                    empty.fill((255, 255, 255, 255))
                    empty = pygame.image.tostring(empty, "RGBA")  # convert image to string data for filtering effect
                    empty = Image.frombytes("RGBA", (frames[frame_index].get_width(), frames[frame_index].get_height()),
                                            empty)  # use PIL to get image data
                    surface = Image.blend(surface, empty, alpha=float(prop[prop.rfind("_") + 1:]) / 10)
                surface.putalpha(alpha)  # put back alpha
                surface = surface.tobytes()
                surface = pygame.image.fromstring(surface, (frames[frame_index].get_width(), frames[frame_index].get_height()),
                                                  "RGBA")  # convert image back to a pygame surface
                if "colour" in prop:
                    colour = prop[prop.rfind("_")+1:]
                    colour = [int(this_colour) for this_colour in colour.split(",")]
                    surface = apply_colour(surface, colour)
                frames[frame_index] = surface
        filmstrip_list[frame_index].add_strip(frames[frame_index])
    animation.reload(frames)
    for helper in helper_list:
        helper.stat1 = char.part_name_list[current_frame]
        helper.stat2 = char.animation_part_list[current_frame]
        if char.part_selected:  # not empty
            for part in char.part_selected:
                part = list(char.rect_part_list.keys())[part]
                helper.select_part((0, 0), True, False, part)
        else:
            helper.select_part(None, shift_press, False)


def change_animation(new_name):
    global animation_name, current_frame, current_anim_row, current_frame_row, anim_property_select, frame_property_select
    current_frame = 0
    anim.show_frame = current_frame
    anim_prop_listbox.namelist = anim_property_list + ["Custom"]  # reset property list
    anim_property_select = []
    frame_prop_listbox.namelist = [frame_property_list + ["Custom"] for _ in range(10)]
    frame_property_select = [[] for _ in range(10)]
    current_anim_row = 0
    current_frame_row = 0
    skeleton.read_animation(new_name)
    animation_name = new_name
    animation_selector.change_name(new_name)
    reload_animation(anim, skeleton)
    anim_prop_listscroll.change_image(new_row=0, log_size=len(anim_prop_listbox.namelist))
    frame_prop_listscroll.change_image(new_row=0, log_size=len(frame_prop_listbox.namelist[current_frame]))


def anim_to_pool(pool, char, new=False, replace=None, duplicate=None):
    """Add animation to animation pool data"""
    if replace is not None:  # rename animation
        for direction in range(0, 5):
            pool[direction] = {animation_name if k == replace else k: v for k, v in pool[direction].items()}
    if duplicate is not None:
        for direction in range(0, 5):
            pool[direction][animation_name] = pool[direction][duplicate]
    else:
        if animation_name not in pool[0]:
            for direction in range(0, 5):
                pool[direction][animation_name] = []
        if new:
            for direction in range(0, 5):
                pool[direction][animation_name] = [frame for index, frame in enumerate(char.frame_list) if frame != {} and activate_list[index]]
        else:
            pool[char.side][animation_name] = [frame for index, frame in enumerate(char.frame_list) if frame != {} and activate_list[index]]


def anim_save_pool(pool, pool_name):
    """Save animation pool data"""
    activate_list
    for index, direction in enumerate(direction_list):
        with open(os.path.join(main_dir, "data", "animation", pool_name, direction + ".csv"), mode="w", encoding='utf-8', newline="") as edit_file:
            filewriter = csv.writer(edit_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
            save_list = pool[index]
            final_save = [[item for item in anim_column_header]]
            for item in list(save_list.items()):
                for frame_num, frame in enumerate(item[1]):
                    subitem = [tiny_item for tiny_item in list(frame.values())]
                    for item_index, min_item in enumerate(subitem):
                        if type(min_item) == list:
                            new_item = str(min_item)
                            for character in "'[] ":
                                new_item = new_item.replace(character, '')
                            subitem[item_index] = new_item
                    new_item = [item[0] + "/" + str(frame_num)] + subitem
                    final_save.append(new_item)
            for row in final_save:
                filewriter.writerow(row)
        edit_file.close()


def anim_del_pool(pool):
    """Delete animation from animation pool data"""
    if animation_name in pool[0]:
        for direction in range(0, 5):
            try:
                del pool[direction][animation_name]
            except:
                pass

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
        race_list.append(row[1].lower())
        race_acro.append(row[3])
edit_file.close()

race_list = race_list[2:]  # remove header and any race
race_acro = race_acro[2:]
race_accept = ["human", "horse"]  # for now accept only human race

generic_animation_pool = []
for direction in direction_list:
    with open(os.path.join(main_dir, "data", "animation", "generic", direction + ".csv"), encoding="utf-8", mode="r") as edit_file:
        rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
        rd = [row for row in rd]
        part_name_header = rd[0]
        list_column = ["p1_head", "p1_face", "p1_body", "p1_r_arm_up", "p1_r_arm_low", "p1_r_hand", "p1_l_arm_up",
                       "p1_l_arm_low", "p1_l_hand", "p1_r_leg", "p1_r_foot", "p1_l_leg", "p1_l_foot",
                       "p1_main_weapon", "p1_sub_weapon", "p2_head", "p2_face", "p2_body", "p2_r_arm_up", "p2_r_arm_low", "p2_r_hand",
                       "p2_l_arm_up", "p2_l_arm_low", "p2_l_hand", "p2_r_leg", "p2_r_foot", "p2_l_leg",
                       "p2_l_foot", "p2_main_weapon", "p2_sub_weapon", "effect_1", "effect_2", "dmg_effect_1", "dmg_effect_2",
                       "frame_property", "animation_property", "special_1", "special_2", "special_3", "special_4", "special_5"]  # value in list only
        list_column = [index for index, item in enumerate(part_name_header) if item in list_column]
        part_name_header = part_name_header[1:]  # keep only part name for list ref later
        animation_pool = {}
        for row_index, row in enumerate(rd):
            if row_index > 0:
                key = row[0].split("/")[0]
                for n, i in enumerate(row):
                    row = stat_convert(row, n, i, list_column=list_column)
                row = row[1:]
                if key in animation_pool:
                    animation_pool[key].append({part_name_header[item_index]: item for item_index, item in enumerate(row)})
                else:
                    animation_pool[key] = [{part_name_header[item_index]: item for item_index, item in enumerate(row)}]
        generic_animation_pool.append(animation_pool)
        part_name_header = [item for item in part_name_header if item != "effect" and "property" not in item]
    edit_file.close()

skel_joint_list = []
for race in race_list:
    if race in race_accept:
        for direction in direction_list:
            with open(os.path.join(main_dir, "data", "sprite", "generic", race, direction, "skeleton_link.csv"), encoding="utf-8",
                      mode="r") as edit_file:
                rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
                rd = [row for row in rd]
                header = rd[0]
                list_column = ["Position"]  # value in list only
                list_column = [index for index, item in enumerate(header) if item in list_column]
                joint_list = {}
                for row_index, row in enumerate(rd):
                    if row_index > 0:
                        for n, i in enumerate(row):
                            row = stat_convert(row, n, i, list_column=list_column)
                            key = row[0].split("/")[0]
                        if key in joint_list:
                            joint_list[key].append({row[1:][0]: pygame.Vector2(row[1:][1])})
                        else:
                            joint_list[key] = [{row[1:][0]: pygame.Vector2(row[1:][1])}]
                skel_joint_list.append(joint_list)
            edit_file.close()

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
                imgs = load_textures(main_dir, folder)
                gen_body_sprite_pool[race][direction][folder[-1]] = imgs

gen_weapon_sprite_pool = {}
part_folder = Path(os.path.join(main_dir, "data", "sprite", "generic", "weapon"))
subdirectories = [str(x).split("data\\")[1].split("\\") for x in part_folder.iterdir() if x.is_dir()]
for folder in subdirectories:
    gen_weapon_sprite_pool[folder[-1]] = {}
    part_subfolder = Path(os.path.join(main_dir, "data", "sprite", "generic", "weapon", folder[-1]))
    subsubdirectories = [str(x).split("data\\")[1].split("\\") for x in part_subfolder.iterdir() if x.is_dir()]
    for subfolder in subsubdirectories:
        for direction in direction_list:
            imgs = load_textures(main_dir, ["sprite", "generic", "weapon", folder[-1], subfolder[-1], direction])
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
        imgs = load_textures(main_dir, subfolder)
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


class Bodyhelper(pygame.sprite.Sprite):
    def __init__(self, size, pos, type, part_images):
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
        self.type = type
        self.part_images_original = [image.copy() for image in part_images]
        if self.type in ("p1", "p2"):
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
            for box_part in ("S1", "S2", "S3", "S4", "S5", "E1", "E2", "DE1", "DE2"):
                text_surface = self.box_font.render(box_part, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(empty_box.get_width() / 2, empty_box.get_height() / 2))
                new_box = empty_box.copy()
                new_box.blit(text_surface, text_rect)
                self.part_images_original.append(new_box)
        self.part_images = [image.copy() for image in self.part_images_original]
        self.part_selected = []
        self.stat1 = {}
        self.stat2 = {}
        if self.type == "p1":
            self.rect_part_list = {"p1_head": None, "p1_body": None, "p1_r_arm_up": None, "p1_r_arm_low": None, "p1_r_hand": None,
                                   "p1_l_arm_up": None, "p1_l_arm_low": None, "p1_l_hand": None, "p1_r_leg": None, "p1_r_foot": None,
                                   "p1_l_leg": None, "p1_l_foot": None, "p1_main_weapon": None, "p1_sub_weapon": None}
            self.part_pos = {"p1_head": (185, 85), "p1_body": (185, 148), "p1_r_arm_up": (155, 126), "p1_r_arm_low": (155, 156),
                             "p1_r_hand": (155, 187), "p1_l_arm_up": (215, 126), "p1_l_arm_low": (215, 156), "p1_l_hand": (215, 187),
                             "p1_r_leg": (170, 216), "p1_r_foot": (170, 246), "p1_l_leg": (200, 216), "p1_l_foot": (200, 246),
                             "p1_main_weapon": (165, 30), "p1_sub_weapon": (205, 30)}
        elif self.type == "p2":
            self.rect_part_list = {"p2_head": None, "p2_body": None, "p2_r_arm_up": None, "p2_r_arm_low": None,
                                   "p2_r_hand": None, "p2_l_arm_up": None, "p2_l_arm_low": None, "p2_l_hand": None,
                                   "p2_r_leg": None, "p2_r_foot": None, "p2_l_leg": None, "p2_l_foot": None,
                                   "p2_main_weapon": None, "p2_sub_weapon": None}
            self.part_pos = {"p2_head": (185, 85), "p2_body": (185, 148), "p2_r_arm_up": (155, 126), "p2_r_arm_low": (155, 156),
                             "p2_r_hand": (155, 187), "p2_l_arm_up": (215, 126), "p2_l_arm_low": (215, 156), "p2_l_hand": (215, 187),
                             "p2_r_leg": (170, 216), "p2_r_foot": (170, 246), "p2_l_leg": (200, 216), "p2_l_foot": (200, 246),
                             "p2_main_weapon": (155, 30), "p2_sub_weapon": (215, 30)}
        else:
            self.rect_part_list = {"special_1": None, "special_2": None, "special_3": None, "special_4": None, "special_5": None,
                                   "effect_1": None, "effect_2": None, "dmg_effect_1": None, "dmg_effect_2": None}
            self.part_pos = {"special_1": (20, 15), "special_2": (20, 45), "special_3": (20, 75), "special_4": (20, 105), "special_5": (20, 135),
                             "effect_1": (20, 165), "effect_2": (20, 195), "dmg_effect_1": (20, 225), "dmg_effect_2": (20, 255)}

        for key, item in self.part_pos.items():
            self.part_pos[key] = (item[0] * screen_scale[0], item[1] * screen_scale[1])
        self.blit_part()

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
                for index, change in enumerate(["side", "front", "back", "sideup", "sidedown"]):
                    if stat[1] == index:
                        stat[1] = new_change[index]
                stat[2] = str(stat[2])
                if len(stat) > 3:
                    stat[3] = str([stat[3][0], stat[3][1]])
                    for index, change in enumerate(["F", "FH", "FV", "FHV"]):
                        if stat[5] == index:
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
                if any(ext in part for ext in ["effect", "special"]):
                    text_rect1 = text_surface1.get_rect(midleft=(self.part_pos[part][0] + shift_x, self.part_pos[part][1] - 10))
                    text_rect2 = text_surface2.get_rect(midleft=(self.part_pos[part][0] + shift_x, self.part_pos[part][1] - 10 + self.font_size + 2))
                elif "body" in part:
                    head_name = "p1_head"
                    if "p2" in part:
                        head_name = "p2_head"
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
                        text_rect2 = text_surface2.get_rect(midleft=(self.part_pos[part][0] + shift_x, self.part_pos[part][1] - 15 + self.font_size + 2))
                    else:
                        text_rect1 = text_surface1.get_rect(midright=(self.part_pos[part][0] - shift_x, self.part_pos[part][1] - 15))
                        text_rect2 = text_surface2.get_rect(midright=(self.part_pos[part][0] - shift_x, self.part_pos[part][1] - 15 + self.font_size + 2))
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


class Skeleton:
    def __init__(self):
        self.animation_list = []
        self.animation_part_list = []
        self.frame_list = [{}] * 10
        self.side = 1  # 0 = front, 1 = side, 2 = back, 3 = sideup, 4 = sidedown

        self.rect_part_list = {"p1_head": None, "p1_body": None, "p1_r_arm_up": None, "p1_r_arm_low": None, "p1_r_hand": None,
                               "p1_l_arm_up": None, "p1_l_arm_low": None, "p1_l_hand": None, "p1_r_leg": None, "p1_r_foot": None,
                               "p1_l_leg": None, "p1_l_foot": None, "p1_main_weapon": None, "p1_sub_weapon": None,
                               "p2_head": None, "p2_body": None, "p2_r_arm_up": None, "p2_r_arm_low": None,
                               "p2_r_hand": None, "p2_l_arm_up": None, "p2_l_arm_low": None, "p2_l_hand": None,
                               "p2_r_leg": None, "p2_r_foot": None, "p2_l_leg": None, "p2_l_foot": None,
                               "p2_main_weapon": None, "p2_sub_weapon": None, "effect_1": None, "effect_2": None,
                               "dmg_effect_1": None, "dmg_effect_2": None, "special_1": None, "special_2": None,
                               "special_3": None, "special_4": None, "special_5": None}
        self.all_part_list = {"p1_head": None, "p1_eye": 1, "p1_mouth": 1, "p1_body": None, "p1_r_arm_up": None,
                              "p1_r_arm_low": None, "p1_r_hand": None, "p1_l_arm_up": None, "p1_l_arm_low": None, "p1_l_hand": None,
                              "p1_r_leg": None, "p1_r_foot": None, "p1_l_leg": None, "p1_l_foot": None, "p1_main_weapon": None,
                              "p1_sub_weapon": None, "p2_head": None, "p2_eye": 1, "p2_mouth": 1, "p2_body": None,
                              "p2_r_arm_up": None, "p2_r_arm_low": None, "p2_r_hand": None, "p2_l_arm_up": None, "p2_l_arm_low": None,
                              "p2_l_hand": None, "p2_r_leg": None, "p2_r_foot": None, "p2_l_leg": None, "p2_l_foot": None,
                              "p2_main_weapon": None, "p2_sub_weapon": None, "effect_1": None, "effect_2": None,
                              "dmg_effect_1": None, "dmg_effect_2": None, "special_1": None, "special_2": None,
                              "special_3": None, "special_4": None, "special_5": None}
        self.part_selected = []
        self.p1_race = "human"
        self.p2_race = "human"
        skin = list(skin_colour_list.keys())[random.randint(0, len(skin_colour_list) - 1)]
        skin_colour = skin_colour_list[skin]
        self.p1_hair_colour = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.p1_eye_colour = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.p2_hair_colour = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.p2_eye_colour = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.weapon = {"p1_main_weapon": "sword", "p1_sub_weapon": "sword", "p2_main_weapon": "sword", "p2_sub_weapon": "sword"}
        self.empty_sprite_part = [0, pygame.Vector2(0, 0), [50, 50], 0, 0, 0, 1]
        self.random_face()
        self.size = 1  # size scale of sprite
        try:
            self.read_animation(list(animation_pool.keys())[0])
            self.default_sprite_part = {key: (value[:] if value is not None else value) for key, value in self.animation_part_list[0].items()}
            self.default_body_part = {key: value for key, value in self.bodypart_list[0].items()}
            self.default_part_name = {key: value for key, value in self.part_name_list[0].items()}
        except IndexError:  # empty animation file
            self.read_animation(None)
            self.default_sprite_part = {key: None for key in self.rect_part_list.keys()}
            self.default_body_part = {key: value for key, value in self.all_part_list.items()}
            self.default_part_name = {key: None for key in self.rect_part_list.keys()}

    def random_face(self):  # todo change when add option to change face
        self.p1_eyebrow = list(gen_body_sprite_pool[self.p1_race]["side"]["eyebrow"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p1_race]["side"]["eyebrow"]) - 1)]
        self.p1_any_eye = list(gen_body_sprite_pool[self.p1_race]["side"]["eye"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p1_race]["side"]["eye"]) - 1)]
        self.p1_any_mouth = list(gen_body_sprite_pool[self.p1_race]["side"]["mouth"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p1_race]["side"]["mouth"]) - 1)]
        self.p1_beard = list(gen_body_sprite_pool[self.p1_race]["side"]["beard"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p1_race]["side"]["beard"]) - 1)]
        self.p2_eyebrow = list(gen_body_sprite_pool[self.p2_race]["side"]["eyebrow"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p2_race]["side"]["eyebrow"]) - 1)]
        self.p2_any_eye = list(gen_body_sprite_pool[self.p2_race]["side"]["eye"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p1_race]["side"]["eye"]) - 1)]
        self.p2_any_mouth = list(gen_body_sprite_pool[self.p2_race]["side"]["mouth"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p2_race]["side"]["mouth"]) - 1)]
        self.p2_beard = list(gen_body_sprite_pool[self.p2_race]["side"]["beard"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p2_race]["side"]["beard"]) - 1)]

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
                self.size = frame_list[0]['size']  # use only the size from first frame, all frame should be same size
                if type(self.size) != int:  # in case the row is empty
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
                                if pose[part][1] in gen_weapon_sprite_pool[self.weapon[part]][pose[part][0]]:
                                    link_list[part] = [pose[part][2], pose[part][3]]
                                    bodypart_list[part] = [self.weapon[part], pose[part][0], pose[part][1]]
                            elif any(ext in part for ext in ["effect", "special"]):
                                if pose[part][1] in effect_sprite_pool[pose[part][1]][pose[part][0]]:
                                    link_list[part] = [pose[part][2], pose[part][3]]
                                    bodypart_list[part] = [self.weapon[part], pose[part][0], pose[part][1]]
                            else:
                                link_list[part] = [pose[part][3], pose[part][4]]
                                bodypart_list[part] = [pose[part][0], pose[part][1], pose[part][2]]
                        elif pose[part] != 0:
                            bodypart_list[part] = pose[part]
                        else:
                            bodypart_list[part] = 1.0
                    elif "property" in part and pose[part] != [""]:
                        if "animation" in part:
                            for stuff in pose[part]:
                                if stuff not in anim_prop_listbox.namelist:
                                    anim_prop_listbox.namelist.insert(-1, stuff)
                                if stuff not in anim_property_select:
                                    anim_property_select.append(stuff)
                        elif "frame" in part and pose[part] != 0:
                            for stuff in pose[part]:
                                if stuff not in frame_prop_listbox.namelist[index]:
                                    frame_prop_listbox.namelist[index].insert(-1, stuff)
                                if stuff not in frame_property_select[index]:
                                    frame_property_select[index].append(stuff)
                self.bodypart_list[index] = bodypart_list
                main_joint_pos_list = self.generate_body(self.bodypart_list[index])
                part_name = {key: None for key in self.rect_part_list.keys()}

                except_list = ["eye", "mouth", "size"]
                for part in part_name_header:
                    if part in pose and pose[part] != [0] and any(ext in part for ext in except_list) is False:
                        if "weapon" in part:
                            sprite_part[part] = [self.sprite_image[part],
                                                 (self.sprite_image[part].get_width() / 2, self.sprite_image[part].get_height() / 2),
                                                 link_list[part], pose[part][4], pose[part][5], pose[part][6], pose[part][7]]
                            part_name[part] = [self.weapon[part], pose[part][0], pose[part][1]]
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
        setup_list(menu.NameList, current_anim_row, anim_prop_listbox.namelist, anim_prop_namegroup,
                   anim_prop_listbox, ui, layer=9, old_list=anim_property_select)
        setup_list(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
                   frame_prop_listbox, ui, layer=9, old_list=frame_property_select[current_frame])

    def create_animation_film(self, pose_layer_list, frame, empty=False):
        image = pygame.Surface((default_sprite_size[0] * self.size, default_sprite_size[1] * self.size),
                               pygame.SRCALPHA)  # default size will scale down later
        if empty is False:
            for index, layer in enumerate(pose_layer_list):
                part = self.animation_part_list[frame][layer]
                image = self.part_to_sprite(image, part[0], list(self.animation_part_list[frame].keys()).index(layer),
                                            part[1], part[2], part[3], part[4], part[6])
        return image

    def create_joint(self, pose_layer_list):
        for index, layer in enumerate(pose_layer_list):
            part = self.animation_part_list[current_frame][layer]
            name_check = layer
            if "p1" in name_check or "p2" in name_check:
                name_check = name_check[3:]  # remove p1_
            if self.part_name_list[current_frame][layer] is not None and \
                    name_check in skel_joint_list[direction_list.index(self.part_name_list[current_frame][layer][1])]:
                for index, item in enumerate(
                        skel_joint_list[direction_list.index(self.part_name_list[current_frame][layer][1])][name_check]):
                    joint_type = 0  # main
                    if index > 0:
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
        p1_head_sprite_surface = None
        try:
            p1_head_race = bodypart_list["p1_head"][0]
            p1_head_side = bodypart_list["p1_head"][1]
            p1_head = gen_body_sprite_pool[p1_head_race][p1_head_side]["head"][bodypart_list["p1_head"][2]].copy()
            p1_head_sprite_surface = pygame.Surface((p1_head.get_width(), p1_head.get_height()), pygame.SRCALPHA)
            head_rect = p1_head.get_rect(midtop=(p1_head_sprite_surface.get_width() / 2, 0))
            p1_head_sprite_surface.blit(p1_head, head_rect)
            p1_face = [gen_body_sprite_pool[p1_head_race][p1_head_side]["eyebrow"][self.p1_eyebrow].copy(),
                       self.grab_face_part(p1_head_race, p1_head_side, "eye", bodypart_list["p1_eye"], self.p1_any_eye),
                       gen_body_sprite_pool[p1_head_race][p1_head_side]["beard"][self.p1_beard].copy(),
                       self.grab_face_part(p1_head_race, p1_head_side, "mouth", bodypart_list["p1_mouth"], self.p1_any_mouth)]
            # if skin != "white":
            #     face[0] = self.apply_colour(face[0], skin_colour)
            p1_face[0] = apply_colour(p1_face[0], self.p1_hair_colour)
            p1_face[2] = apply_colour(p1_face[2], self.p1_hair_colour)
            p1_face[1] = apply_colour(p1_face[1], self.p1_eye_colour)

            p1_head_sprite_surface = pygame.Surface((p1_face[2].get_width(), p1_face[2].get_height()), pygame.SRCALPHA)
            head_rect = p1_head.get_rect(midtop=(p1_head_sprite_surface.get_width() / 2, 0))
            p1_head_sprite_surface.blit(p1_head, head_rect)

            for index, item in enumerate(p1_face):
                rect = item.get_rect(topleft=(0, 0))
                p1_head_sprite_surface.blit(item, rect)
        except KeyError:  # some head direction show no face
            pass
        except TypeError:  # empty
            pass

        p2_head_sprite_surface = None
        try:
            p2_head_race = bodypart_list["p2_head"][0]
            p2_head_side = bodypart_list["p2_head"][1]
            p2_head = gen_body_sprite_pool[p2_head_race][p2_head_side]["head"][bodypart_list["p2_head"][2]].copy()
            p2_head_sprite_surface = pygame.Surface((p2_head.get_width(), p2_head.get_height()), pygame.SRCALPHA)
            head_rect = p2_head.get_rect(midtop=(p2_head_sprite_surface.get_width() / 2, 0))
            p2_head_sprite_surface.blit(p2_head, head_rect)
            p2_face = [gen_body_sprite_pool[p2_head_race][p2_head_side]["eyebrow"][self.p2_eyebrow].copy(),
                       self.grab_face_part(p2_head_race, p2_head_side, "eye", bodypart_list["p2_eye"], self.p2_any_eye),
                       gen_body_sprite_pool[p2_head_race][p2_head_side]["beard"][self.p2_beard].copy(),
                       self.grab_face_part(p2_head_race, p2_head_side, "mouth", bodypart_list["p2_mouth"], self.p2_any_mouth)]
            # if skin != "white":
            #     face[0] = self.apply_colour(face[0], skin_colour)
            p2_face[0] = apply_colour(p2_face[0], self.p2_hair_colour)
            p2_face[2] = apply_colour(p2_face[2], self.p2_hair_colour)
            p2_face[1] = apply_colour(p2_face[1], self.p2_eye_colour)
            p2_head_sprite_surface = pygame.Surface((p2_face[2].get_width(), p2_face[2].get_height()), pygame.SRCALPHA)
            head_rect = p2_head.get_rect(midtop=(p2_head_sprite_surface.get_width() / 2, 0))
            p2_head_sprite_surface.blit(p2_head, head_rect)

            for index, item in enumerate(p2_face):
                rect = item.get_rect(topleft=(0, 0))
                p2_head_sprite_surface.blit(item, rect)
        except KeyError:  # some head direction show no face
            pass
        except TypeError:  # empty
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
                        if "p1_" in stuff or "p2_" in stuff:
                            part_name = stuff[3:]  # remove p1_ or p2_ to get part name
                        if "special" in stuff:
                            part_name = "special"
                        if "r_" in part_name[0:2] or "l_" in part_name[0:2]:
                            part_name = part_name[2:]  # remove side
                        self.sprite_image[stuff] = gen_body_sprite_pool[bodypart_list[stuff][0]][bodypart_list[stuff][1]][part_name][
                            bodypart_list[stuff][2]].copy()
                elif "head" in stuff:
                    if "p1" in stuff:
                        self.sprite_image[stuff] = p1_head_sprite_surface
                    else:
                        self.sprite_image[stuff] = p2_head_sprite_surface

        # if skin != "white":
        #     for part in list(self.sprite_image.keys())[1:]:
        #         self.sprite_image[part] = self.apply_colour(self.sprite_image[part], skin_colour)

        main_joint_pos_list = {}
        for part_index, part in enumerate(part_name_header):
            for part_link in skel_joint_list[self.side]:
                if part_link in part:  # match part name, p1_head = head in part link
                    main_joint_pos_list[part] = list(skel_joint_list[self.side][part_link][0].values())[0]
                    break
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
        global animation_history, bodypart_history, partname_history, current_history
        key_list = list(self.rect_part_list.keys())
        if edit_type == "default":  # reset to default
            self.animation_part_list[current_frame] = {key: (value[:] if value is not None else value) for key, value in
                                                       self.default_sprite_part.items()}
            self.bodypart_list[current_frame] = {key: value for key, value in self.default_body_part.items()}
            self.part_name_list[current_frame] = {key: value for key, value in self.default_part_name.items()}
            self.part_selected = []
            race_part_button.change_text("")
            direction_part_button.change_text("")
            part_selector.change_name("")

        elif edit_type == "clear":  # clear whole strip
            for part in self.part_name_list[current_frame]:
                self.bodypart_list[current_frame][part] = None
                self.part_name_list[current_frame][part] = ["", "", ""]
                self.animation_part_list[current_frame][part] = []
            self.part_selected = []

        elif edit_type == "change":  # change strip
            self.part_selected = []

        elif edit_type == "paste":  # paste copy part
            for part in copy_part.keys():
                self.bodypart_list[current_frame][part] = copy_part[part].copy()
                self.animation_part_list[current_frame][part] = copy_animation[part].copy()
                self.part_name_list[current_frame][part] = copy_name[part].copy()

        elif "direction" in edit_type:
            if self.part_selected != []:
                for part in self.part_selected:
                    try:
                        part_index = key_list[part]
                        sidechange = edit_type.split("_")[1]
                        self.bodypart_list[current_frame][part_index][1] = sidechange
                        self.part_name_list[current_frame][part_index][1] = sidechange
                        main_joint_pos_list = self.generate_body(self.bodypart_list[current_frame])
                        self.animation_part_list[current_frame][part_index][0] = self.sprite_image[part_index]
                    except IndexError:
                        pass
                    except TypeError:  # None type
                        pass
                    except KeyError:  # change side and not found part with same name
                        self.part_name_list[current_frame][part_index][2] = ""

        elif edit_type == "undo" or edit_type == "redo":
            self.part_name_list[current_frame] = partname_history[current_history]
            self.animation_part_list[current_frame] = animation_history[current_history]
            self.bodypart_list[current_frame] = bodypart_history[current_history]

        elif "eye" in edit_type:
            if "Any" in edit_type:
                if "p1_" in edit_type:
                    self.bodypart_list[current_frame]["p1_eye"] = self.p1_any_eye
                elif "p2_" in edit_type:
                    self.bodypart_list[current_frame]["p2_eye"] = self.p2_any_eye
            else:
                if "p1_" in edit_type:
                    self.bodypart_list[current_frame]["p1_eye"] = edit_type[7:]
                elif "p2_" in edit_type:
                    self.bodypart_list[current_frame]["p2_eye"] = edit_type[7:]
            main_joint_pos_list = self.generate_body(self.bodypart_list[current_frame])
            part = "p1_head"
            if "p2_" in edit_type:
                part = "p2_head"
            self.animation_part_list[current_frame][part][0] = self.sprite_image[part]

        elif "mouth" in edit_type:
            if "Any" in edit_type:
                if "p1_" in edit_type:
                    self.bodypart_list[current_frame]["p1_mouth"] = self.p1_any_mouth
                elif "p2_" in edit_type:
                    self.bodypart_list[current_frame]["p2_mouth"] = self.p2_any_mouth
            else:
                if "p1_" in edit_type:
                    self.bodypart_list[current_frame]["p1_mouth"] = edit_type[9:]
                elif "p2_" in edit_type:
                    self.bodypart_list[current_frame]["p2_mouth"] = edit_type[9:]
            main_joint_pos_list = self.generate_body(self.bodypart_list[current_frame])
            part = "p1_head"
            if "p2_" in edit_type:
                part = "p2_head"
            self.animation_part_list[current_frame][part][0] = self.sprite_image[part]

        elif "part" in edit_type:
            if self.part_selected != []:
                part = self.part_selected[-1]
                part_index = key_list[part]
                partchange = edit_type[5:]
                self.bodypart_list[current_frame][part_index][2] = partchange
                self.part_name_list[current_frame][part_index][2] = partchange
                main_joint_pos_list = self.generate_body(self.bodypart_list[current_frame])
                if self.animation_part_list[current_frame][part_index] == []:
                    self.animation_part_list[current_frame][part_index] = self.empty_sprite_part.copy()
                    if any(ext in part_index for ext in ["weapon", "effect", "special"]):
                        self.animation_part_list[current_frame][part_index][1] = "center"
                    else:
                        self.animation_part_list[current_frame][part_index][1] = main_joint_pos_list[part_index]
                self.animation_part_list[current_frame][part_index][0] = self.sprite_image[part_index]

        elif "race" in edit_type:
            if self.part_selected != []:
                part = self.part_selected[-1]
                part_index = key_list[part]
                partchange = edit_type[5:]
                if "weapon" in part_index:
                    self.weapon[part_index] = partchange
                if self.bodypart_list[current_frame][part_index] is None:
                    self.bodypart_list[current_frame][part_index] = [0, 0, 0]
                    self.part_name_list[current_frame][part_index] = ["", "", ""]
                    self.animation_part_list[current_frame][part_index] = []
                self.bodypart_list[current_frame][part_index][0] = partchange
                self.part_name_list[current_frame][part_index][0] = partchange
                try:
                    main_joint_pos_list = self.generate_body(self.bodypart_list[current_frame])
                    self.animation_part_list[current_frame][part_index][0] = self.sprite_image[part_index]
                except IndexError:
                    pass
                except KeyError:  # change side and not found part with same name
                    self.part_name_list[current_frame][part_index][2] = ""

        elif "new" in edit_type:  # new animation
            self.animation_part_list = [{key: None for key in self.rect_part_list.keys()}] * 10
            p1_face = {"p1_eye": 1,
                       "p1_mouth": 1}
            p2_face = {"p2_eye": 1,
                       "p2_mouth": 1}
            self.bodypart_list = [{key: value for key, value in self.all_part_list.items()}] * 10
            for stuff in self.bodypart_list:
                stuff.update(p1_face)
                stuff.update(p2_face)
            self.part_name_list = [{key: None for key in self.rect_part_list.keys()}] * 10
            self.part_selected = []

        elif self.part_selected != []:
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
                            new_point = self.animation_part_list[current_frame][part_index][2]
                            if "w" in edit_type:
                                new_point[1] = new_point[1] - 0.5
                            elif "s" in edit_type:
                                new_point[1] = new_point[1] + 0.5
                            elif "a" in edit_type:
                                new_point[0] = new_point[0] - 0.5
                            elif "d" in edit_type:
                                new_point[0] = new_point[0] + 0.5
                            self.animation_part_list[current_frame][part_index][2] = new_point

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
                            self.bodypart_list[current_frame][part_index] = None
                            self.part_name_list[current_frame][part_index] = ["", "", ""]
                            self.animation_part_list[current_frame][part_index] = []

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
        p1_face = {"p1_eye": self.bodypart_list[current_frame]["p1_eye"] if self.bodypart_list[current_frame]["p1_eye"] != self.p1_any_eye else 1,
                   "p1_mouth": self.bodypart_list[current_frame]["p1_mouth"] if self.bodypart_list[current_frame][
                                                                                    "p1_mouth"] != self.p1_any_mouth else 1}
        p2_face = {"p2_eye": self.bodypart_list[current_frame]["p2_eye"] if self.bodypart_list[current_frame]["p2_eye"] != self.p2_any_eye else 1,
                   "p2_mouth": self.bodypart_list[current_frame]["p2_mouth"] if self.bodypart_list[current_frame][
                                                                                    "p2_mouth"] != self.p2_any_mouth else 1}
        p2_face_pos = 15
        self.frame_list[current_frame] = {k: v for k, v in (list(self.frame_list[current_frame].items())[:p2_face_pos] + list(p2_face.items()) +
                                                            list(self.frame_list[current_frame].items())[p2_face_pos:])}
        p1_face_pos = 1
        self.frame_list[current_frame] = {k: v for k, v in (list(self.frame_list[current_frame].items())[:p1_face_pos] + list(p1_face.items()) +
                                                            list(self.frame_list[current_frame].items())[p1_face_pos:])}
        self.frame_list[current_frame]["size"] = self.size
        self.frame_list[current_frame]["frame_property"] = frame_property_select[current_frame]
        self.frame_list[current_frame]["animation_property"] = anim_property_select
        anim_to_pool(current_pool, self)
        reload_animation(anim, self)

        if edit_type == "new" or edit_type == "change":
            if edit_type == "new":
                for index, frame in enumerate(self.frame_list):  # reset all empty like the first frame
                    self.frame_list[index] = {key: value for key, value in list(self.frame_list[0].items())}
            anim_to_pool(current_pool, self, new=True)

            # reset history when change frame or create new animation
            partname_history = partname_history[-1:] + [self.part_name_list[current_frame]]
            animation_history = animation_history[-1:] + [self.animation_part_list[current_frame]]
            bodypart_history = bodypart_history[-1:] + [self.bodypart_list[current_frame]]
            current_history = 0

        elif edit_type != "undo" and edit_type != "redo":
            if current_history < len(animation_history) - 1:
                partname_history = partname_history[:current_history + 1]
                animation_history = animation_history[:current_history + 1]
                bodypart_history = bodypart_history[:current_history + 1]

            animation_history.append(
                {key: (value[:] if value is not None else value) for key, value in self.animation_part_list[current_frame].items()})
            bodypart_history.append({key: value for key, value in self.bodypart_list[current_frame].items()})
            partname_history.append({key: value for key, value in self.part_name_list[current_frame].items()})
            current_history += 1

            if len(animation_history) > 1000:  # save only last 1000 activity
                new_first = len(animation_history) - 1000
                partname_history = partname_history[new_first:]
                animation_history = animation_history[new_first:]
                bodypart_history = bodypart_history[new_first:]
                current_history -= new_first

    def part_to_sprite(self, surface, part, part_index, main_joint_pos, target, angle, flip, scale):
        """Find body part's new center point from main_joint_pos with new angle, then create rotated part and blit to sprite"""
        part_rotated = part.copy()
        if scale != 1:
            part_rotated = pygame.transform.scale(part_rotated, (part_rotated.get_width() * scale,
                                                                 part_rotated.get_height() * scale))
        if flip != 0:
            if flip == 1:
                part_rotated = pygame.transform.flip(part_rotated, True, False)
            elif flip == 2:
                part_rotated = pygame.transform.flip(part_rotated, False, True)
            elif flip == 3:
                part_rotated = pygame.transform.flip(part_rotated, True, True)
        if angle != 0:
            part_rotated = pygame.transform.rotate(part_rotated, angle)  # rotate part sprite

        center = pygame.Vector2(part.get_width() / 2, part.get_height() / 2)
        if main_joint_pos == "center":
            main_joint_pos = (part.get_width() / 2, part.get_height() / 2)
        # pos_different = main_joint_pos - center  # find distance between image center and connect point main_joint_pos
        # main_joint_pos = main_joint_pos + pos_different
        new_center = target  # - pos_different  # find new center point
        if angle != 0:
            radians_angle = math.radians(360 - angle)
            new_center = rotation_xy(target, new_center, radians_angle)  # find new center point with rotation

        rect = part_rotated.get_rect(center=new_center)
        self.rect_part_list[list(self.rect_part_list.keys())[part_index]] = rect
        surface.blit(part_rotated, rect)

        return surface

    def remake_rect_list(self):
        for key, value in self.rect_part_list.items():  # reset rect list
            self.rect_part_list[key] = None

        for part_index, part in enumerate(self.animation_part_list[current_frame]):
            rect = part.rect
            self.rect_part_list[list(self.rect_part_list.keys())[part_index]] = rect


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
show_joint = True
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
bodypart_history = []
partname_history = []
current_history = 0
current_pool = generic_animation_pool

ui = pygame.sprite.LayeredUpdates()
fakegroup = pygame.sprite.LayeredUpdates()  # just fake group to add for container and not get auto update

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
Bodyhelper.containers = ui
Joint.containers = joints
Filmstrip.containers = ui, filmstrips
NameBox.containers = ui
menu.MenuButton.containers = fakegroup
menu.NameList.containers = ui
popup_listbox = pygame.sprite.Group()
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
body_helper_size = (370 * screen_scale[0], 270 * screen_scale[1])
effect_helper_size = (250 * screen_scale[0], 270 * screen_scale[1])
effect_helper = Bodyhelper(effect_helper_size, (screen_size[0] / 2, screen_size[1] - (body_helper_size[1] / 2)),
                           "effect", [images["smallbox_helper.png"]])
del images["smallbox_helper.png"]
p1_body_helper = Bodyhelper(body_helper_size, (body_helper_size[0] / 2,
                                               screen_size[1] - (body_helper_size[1] / 2)), "p1", list(images.values()))
p2_body_helper = Bodyhelper(body_helper_size, (screen_size[0] - (body_helper_size[0] / 2),
                                               screen_size[1] - (body_helper_size[1] / 2)), "p2", list(images.values()))
helper_list = [p1_body_helper, p2_body_helper, effect_helper]

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
                                     (screen_size[1] / 2, filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
joint_button = SwitchButton(["Joint:ON", "Joint:OFF"], image, (play_animation_button.pos[0] + play_animation_button.image.get_width() * 5,
                                                               filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
grid_button = SwitchButton(["Grid:ON", "Grid:OFF"], image, (play_animation_button.pos[0] + play_animation_button.image.get_width() * 6,
                                                            filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))

copy_button = Button("Copy", image, (play_animation_button.pos[0] - play_animation_button.image.get_width(),
                                     filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
paste_button = Button("Paste", image, (play_animation_button.pos[0] + play_animation_button.image.get_width(),
                                       filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
speed_button = Button("Speed: 1", image, (play_animation_button.pos[0] + play_animation_button.image.get_width() * 2,
                                           filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
default_button = Button("Default", image, (play_animation_button.pos[0] + play_animation_button.image.get_width() * 3,
                                           filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
pointedit_button = SwitchButton(["Center", "Joint"], image, (play_animation_button.pos[0] + play_animation_button.image.get_width() * 4,
                                                             filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
clear_button = Button("Clear", image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 3,
                                       filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
activate_button = SwitchButton(["Enable", "Disable"], image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 4,
                                                              filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
undo_button = Button("Undo", image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 5,
                                     filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))
redo_button = Button("Redo", image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 6,
                                     filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 1.5)))

reset_button = Button("Reset", image, (screen_size[0] / 2.1, p1_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))

flip_hori_button = Button("Flip H", image, (reset_button.pos[0] + reset_button.image.get_width(),
                                            p1_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
flip_vert_button = Button("Flip V", image, (reset_button.pos[0] + (reset_button.image.get_width() * 2),
                                            p1_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
part_copy_button = Button("Copy", image, (reset_button.pos[0] + reset_button.image.get_width() * 3,
                                          p1_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
part_paste_button = Button("Paste", image, (reset_button.pos[0] + reset_button.image.get_width() * 4,
                                            p1_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
p1_all_button = Button("P1 All", image, (reset_button.pos[0] + reset_button.image.get_width() * 5,
                                         p1_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
p2_all_button = Button("P2 All", image, (reset_button.pos[0] + reset_button.image.get_width() * 6,
                                         p1_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
all_button = Button("All", image, (reset_button.pos[0] + reset_button.image.get_width() * 7,
                                   p1_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
race_part_button = Button("", image, (reset_button.image.get_width() / 2,
                                      p1_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
direction_part_button = Button("", image, (race_part_button.pos[0] + race_part_button.image.get_width(),
                                           p1_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))
p1_eye_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 1.8,
                                                      p1_body_helper.rect.midtop[1] - (image.get_height() * 3.2)))
p1_mouth_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 1.8,
                                                        p1_body_helper.rect.midtop[1] - (image.get_height() * 2.2)))
p2_eye_selector = NameBox((250, image.get_height()), (screen_size[0] - (reset_button.image.get_width() * 1.8),
                                                      p1_body_helper.rect.midtop[1] - (image.get_height() * 3.2)))
p2_mouth_selector = NameBox((250, image.get_height()), (screen_size[0] - (reset_button.image.get_width() * 1.8),
                                                        p1_body_helper.rect.midtop[1] - (image.get_height() * 2.2)))
# lock_button = SwitchButton(["Lock:OFF","Lock:ON"], image, (reset_button.pos[0] + reset_button.image.get_width() * 2,
#                                            p1_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))

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
colour_input_box = menu.InputBox(screen_scale, (colour_ui.rect.center[0], colour_ui.rect.center[1] * 1.2), input_ui.image.get_width())  # user text input box

colour_ok_button = menu.MenuButton(screen_scale, image_list, pos=(colour_ui.rect.midleft[0] + image_list[0].get_width(),
                                                                 colour_ui.rect.midleft[1] + (image_list[0].get_height() * 2)),
                                  text="Confirm", layer=31)
colour_cancel_button = menu.MenuButton(screen_scale, image_list,
                                      pos=(colour_ui.rect.midright[0] - image_list[0].get_width(),
                                           colour_ui.rect.midright[1] + (image_list[0].get_height() * 2)),
                                      text="Cancel", layer=31)
colour_ui_popup = (colour_ui, colour_wheel, colour_input_box, colour_ok_button, colour_cancel_button)

box_img = load_image(main_dir, screen_scale, "unit_presetbox.png", "ui\\mainmenu_ui")

menu.ListBox.containers = popup_listbox
popup_listbox = menu.ListBox(screen_scale, (0, 0), box_img, 15)  # popup box need to be in higher layer
popup_listscroll = battleui.UIScroller(popup_listbox.rect.topright,
                                       popup_listbox.image.get_height(),
                                       popup_listbox.max_show,
                                       layer=14)
anim_prop_listbox = menu.ListBox(screen_scale, (0, filmstrip_list[0].rect.midbottom[1] +
                                                (reset_button.image.get_height() * 1.5)), box_img, 8)
anim_prop_listbox.namelist = anim_property_list + ["Custom"]
frame_prop_listbox = menu.ListBox(screen_scale, (screen_size[0] - box_img.get_width(), filmstrip_list[0].rect.midbottom[1] +
                                                 (reset_button.image.get_height() * 1.5)), box_img, 8)
frame_prop_listbox.namelist = [frame_property_list + ["Custom"] for _ in range(10)]
anim_prop_listscroll = battleui.UIScroller(anim_prop_listbox.rect.topright,
                                           anim_prop_listbox.image.get_height(),
                                           anim_prop_listbox.max_show,
                                           layer=10)
frame_prop_listscroll = battleui.UIScroller(frame_prop_listbox.rect.topright,
                                            frame_prop_listbox.image.get_height(),
                                            frame_prop_listbox.max_show,
                                            layer=10)
current_anim_row = 0
current_frame_row = 0
frame_property_select = [[] for _ in range(10)]
anim_property_select = []
anim_prop_listscroll.change_image(new_row=0, log_size=len(anim_prop_listbox.namelist))
frame_prop_listscroll.change_image(new_row=0, log_size=len(frame_prop_listbox.namelist[current_frame]))
ui.add(anim_prop_listbox, frame_prop_listbox, anim_prop_listscroll, frame_prop_listscroll)

animation_selector = NameBox((400, image.get_height()), (screen_size[0] / 2, 0))
part_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 4,
                                                    reset_button.rect.midtop[1]))

shift_press = False
anim = Animation(500, True)
skeleton = Skeleton()
skeleton.animation_list = []
direction = 1
activate_list = [False] * 10
direction_button.change_text(direction_list[direction])
try:
    animation_name = list(animation_pool.keys())[0]
except:
    animation_name = None
skeleton.read_animation(animation_name)
animation_selector.change_name(animation_name)
if animation_name is not None:
    reload_animation(anim, skeleton)
else:
    skeleton.animation_list = [None] * 10
    skeleton.edit_part(None, "new")
animation_history.append({key: (value[:] if value is not None else value) for key, value in skeleton.animation_part_list[current_frame].items()})
bodypart_history.append({key: value for key, value in skeleton.bodypart_list[current_frame].items()})
partname_history.append({key: value for key, value in skeleton.part_name_list[current_frame].items()})

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
                if popup_listbox in ui and popup_listbox.rect.collidepoint(mouse_pos):
                    current_popup_row = list_scroll(popup_listscroll, popup_listbox, current_popup_row, popup_listbox.namelist, popup_namegroup, ui)
                elif skeleton.part_selected != [] and showroom.rect.collidepoint(mouse_pos):
                    if event.button == 4:  # Mouse scroll up
                        skeleton.edit_part(mouse_pos, "scale_up")
                    else:  # Mouse scroll down
                        skeleton.edit_part(mouse_pos, "scale_down")
                elif anim_prop_listbox.rect.collidepoint(mouse_pos) or anim_prop_listscroll.rect.collidepoint(mouse_pos):
                    current_anim_row = list_scroll(anim_prop_listscroll, anim_prop_listbox, current_anim_row, anim_prop_listbox.namelist, anim_prop_namegroup, ui,
                                                   old_list=anim_property_select)
                elif frame_prop_listbox.rect.collidepoint(mouse_pos) or frame_prop_listscroll.rect.collidepoint(mouse_pos):
                    current_frame_row = list_scroll(frame_prop_listscroll, frame_prop_listbox, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup, ui,
                                                    old_list=frame_property_select[current_frame])

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                input_esc = True
            elif text_input_popup[0] == "text_input":
                if input_box in ui:
                    input_box.user_input(event, key_press)
                elif colour_input_box in ui:
                    colour_input_box.user_input(event, key_press)

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
                skeleton.edit_part(mouse_pos, "move_w")
            elif key_press[pygame.K_s]:
                skeleton.edit_part(mouse_pos, "move_s")
            elif key_press[pygame.K_a]:
                skeleton.edit_part(mouse_pos, "move_a")
            elif key_press[pygame.K_d]:
                skeleton.edit_part(mouse_pos, "move_d")
            elif key_press[pygame.K_q]:
                skeleton.edit_part(mouse_pos, "tilt_q")
            elif key_press[pygame.K_e]:
                skeleton.edit_part(mouse_pos, "tilt_e")
            elif key_press[pygame.K_DELETE]:
                keypress_delay = 0.1
                if skeleton.part_selected != []:
                    skeleton.edit_part(mouse_pos, "delete")
            elif key_press[pygame.K_PAGEUP]:
                keypress_delay = 0.1
                if skeleton.part_selected != []:
                    skeleton.edit_part(mouse_pos, "layer_up")
            elif key_press[pygame.K_PAGEDOWN]:
                keypress_delay = 0.1
                if skeleton.part_selected != []:
                    skeleton.edit_part(mouse_pos, "layer_down")

        if mouse_timer != 0:  # player click mouse once before
            mouse_timer += ui_dt  # increase timer for mouse click using real time
            if mouse_timer >= 0.3:  # time pass 0.3 second no longer count as double click
                mouse_timer = 0

        if keypress_delay != 0:  # player click mouse once before
            keypress_delay += ui_dt  # increase timer for mouse click using real time
            if keypress_delay >= 0.3:  # time pass 0.3 second no longer count as double click
                keypress_delay = 0

        if mouse_left_up:
            if popup_listbox in ui:
                if popup_listbox.rect.collidepoint(mouse_pos):
                    popup_click = True
                    for index, name in enumerate(popup_namegroup):  # click on popup list
                        if name.rect.collidepoint(mouse_pos):
                            if popup_listbox.action == "part_side":
                                direction_part_button.change_text(name.name)
                                if skeleton.part_selected != []:
                                    skeleton.edit_part(mouse_pos, "direction_" + name.name)
                            elif popup_listbox.action == "part_select":
                                skeleton.edit_part(mouse_pos, "part_" + name.name)
                            elif popup_listbox.action == "race_select":
                                skeleton.edit_part(mouse_pos, "race_" + name.name)
                            elif "eye" in popup_listbox.action:
                                skeleton.edit_part(mouse_pos, popup_listbox.action[0:3] + "eye_" + name.name)
                                reload_animation(anim, skeleton)
                            elif "mouth" in popup_listbox.action:
                                skeleton.edit_part(mouse_pos, popup_listbox.action[0:3] + "mouth_" + name.name)
                                if "p1" in popup_listbox.action:
                                    p1_mouth_selector.change_name("P1 Mouth: " + name.name)
                                elif "p2" in popup_listbox.action:
                                    p2_mouth_selector.change_name("P2 Mouth: " + name.name)
                                reload_animation(anim, skeleton)
                            elif popup_listbox.action == "animation_select":
                                if animation_name != name.name:
                                    change_animation(name.name)
                            elif popup_listbox.action == "animation_side":
                                direction_button.change_text(name.name)
                                current_frame = 0
                                anim.show_frame = current_frame
                                skeleton.side = direction_list.index(name.name)
                                skeleton.read_animation(animation_name, new_size=False)
                                reload_animation(anim, skeleton)
                            for this_name in popup_namegroup:  # remove name list
                                this_name.kill()
                                del this_name
                            ui.remove(popup_listbox, popup_listscroll)
                            current_popup_row = 0  # reset row

                elif popup_listscroll.rect.collidepoint(mouse_pos):  # scrolling on list
                    popup_click = True
                    new_row = popup_listscroll.user_input(mouse_pos)
                    if new_row is not None:
                        current_popup_row = new_row
                        setup_list(menu.NameList, current_popup_row, popup_listbox.namelist, popup_namegroup,
                                   popup_listbox, ui, layer=19)

                else:  # click other stuffs
                    for this_name in popup_namegroup:  # remove name list
                        this_name.kill()
                        del this_name
                    ui.remove(popup_listbox, popup_listscroll)

            if popup_click is False:  # button that can be clicked even when animation playing
                if play_animation_button.rect.collidepoint(mouse_pos):
                    if play_animation_button.current_option == 0:
                        play_animation_button.change_option(1)  # start playing animation
                        play_animation = True
                    else:
                        play_animation_button.change_option(0)  # stop animation
                        play_animation = False
                        skeleton.edit_part(None, "change")

                elif grid_button.rect.collidepoint(mouse_pos):
                    if grid_button.current_option == 0:  # remove grid
                        grid_button.change_option(1)
                        showroom.grid = False
                    else:
                        grid_button.change_option(0)
                        showroom.grid = True

                elif pointedit_button.rect.collidepoint(mouse_pos):
                    if pointedit_button.current_option == 0:
                        pointedit_button.change_option(1)  # use center point for edit
                    else:
                        pointedit_button.change_option(0)  # use joint point for edit
                    point_edit = pointedit_button.current_option

                elif joint_button.rect.collidepoint(mouse_pos):
                    if joint_button.current_option == 0:  # remove joint sprite
                        joint_button.change_option(1)
                        show_joint = False
                    else:  # stop animation
                        joint_button.change_option(0)
                        show_joint = True

                elif anim_prop_listscroll.rect.collidepoint(mouse_pos):  # scrolling on list
                    new_row = anim_prop_listscroll.user_input(mouse_pos)
                    if new_row is not None:
                        current_anim_row = new_row
                        setup_list(menu.NameList, current_anim_row, anim_prop_listbox.namelist, anim_prop_namegroup,
                                   anim_prop_listbox, ui, layer=9, old_list=anim_property_select)

                elif frame_prop_listscroll.rect.collidepoint(mouse_pos):  # scrolling on list
                    new_row = frame_prop_listscroll.user_input(mouse_pos)
                    if new_row is not None:
                        current_frame_row = new_row
                        setup_list(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
                                   frame_prop_listbox, ui, layer=9, old_list=frame_property_select[current_frame])

                elif anim_prop_listbox.rect.collidepoint(mouse_pos):  # click on animation property list
                    for index, name in enumerate(anim_prop_namegroup):
                        if name.rect.collidepoint(mouse_pos):
                            if name.name == "Custom":
                                text_input_popup = ("text_input", "new_anim_prop")
                                input_ui.change_instruction("Custom Anim Prop:")
                                ui.add(input_ui_popup)
                            else:
                                name.select()
                                if name.selected:
                                    anim_property_select.append(name.name)
                                else:
                                    anim_property_select.remove(name.name)
                                for frame in skeleton.frame_list:
                                    frame["animation_property"] = anim_property_select

                elif frame_prop_listbox.rect.collidepoint(mouse_pos):  # click on frame property list
                    for index, name in enumerate(frame_prop_namegroup):
                        if name.rect.collidepoint(mouse_pos):
                            if name.name == "Custom":
                                text_input_popup = ("text_input", "new_frame_prop")
                                input_ui.change_instruction("Custom Frame Prop:")
                                ui.add(input_ui_popup)
                            elif "effect_" in name.name:
                                if name.name[-1] == "_" or name.name[-1].isdigit():  # effect that need number value
                                    if name.selected is False:
                                        if "colour" not in name.name:
                                            text_input_popup = ("text_input", "frame_prop_num_" + name.name)
                                            input_ui.change_instruction("Input Number Value:")
                                            ui.add(input_ui_popup)
                                        else:
                                            text_input_popup = ("text_input", "frame_prop_colour_" + name.name)
                                            ui.add(colour_ui_popup)
                                elif name.selected is False:  # effect that no need input
                                    frame_property_select[current_frame].append(name.name)
                                    setup_list(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
                                               frame_prop_listbox, ui, layer=9, old_list=frame_property_select[current_frame])
                                    reload_animation(anim, skeleton)
                                if name.selected:
                                    name.select()
                                    frame_property_select[current_frame].remove(name.name)
                                    skeleton.frame_list[current_frame]["frame_property"] = frame_property_select[current_frame]
                                    reload_animation(anim, skeleton)
                            else:
                                name.select()
                                if name.selected:
                                    frame_property_select[current_frame].append(name.name)
                                else:
                                    frame_property_select[current_frame].remove(name.name)
                                skeleton.frame_list[current_frame]["frame_property"] = frame_property_select[current_frame]

        if play_animation:
            current_frame = int(anim.show_frame)
        else:
            dt = 0
            if popup_click is False:  # button that can't be clicked even when animation playing
                if mouse_left_up:
                    if clear_button.rect.collidepoint(mouse_pos):
                        skeleton.edit_part(mouse_pos, "clear")

                    elif default_button.rect.collidepoint(mouse_pos):
                        skeleton.edit_part(mouse_pos, "default")

                    elif speed_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("text_input", "change_speed")
                        input_ui.change_instruction("Input Speed Number Value:")
                        ui.add(input_ui_popup)

                    elif copy_button.rect.collidepoint(mouse_pos):
                        copy_press = True

                    elif paste_button.rect.collidepoint(mouse_pos):
                        paste_press = True

                    elif part_copy_button.rect.collidepoint(mouse_pos):
                        part_copy_press = True

                    elif part_paste_button.rect.collidepoint(mouse_pos):
                        part_paste_press = True

                    elif p1_all_button.rect.collidepoint(mouse_pos) or p2_all_button.rect.collidepoint(mouse_pos):
                        if p1_all_button.rect.collidepoint(mouse_pos):
                            part_change = "p1_"
                        elif p2_all_button.rect.collidepoint(mouse_pos):
                            part_change = "p2_"
                        for part in list(skeleton.rect_part_list.keys()):
                            if part_change in part:
                                if ctrl_press is False:  # add parts
                                    skeleton.click_part(mouse_pos, True, ctrl_press, part)
                                else:
                                    skeleton.click_part(mouse_pos, False, ctrl_press, part)
                            elif part_change not in part and shift_press is False and ctrl_press is False:  # remove other parts
                                skeleton.click_part(mouse_pos, False, True, part)
                        for helper in helper_list:
                            helper.select_part(None, False, False)  # reset first
                            for part in skeleton.part_selected:
                                if list(skeleton.rect_part_list.keys())[part] in helper.rect_part_list:
                                    helper.select_part(mouse_pos, True, False, list(skeleton.rect_part_list.keys())[part])

                    elif all_button.rect.collidepoint(mouse_pos):
                        for part in list(skeleton.rect_part_list.keys()):
                            if ctrl_press is False:  # add all parts
                                skeleton.click_part(mouse_pos, True, ctrl_press, part)
                            else:
                                skeleton.click_part(mouse_pos, False, ctrl_press, part)
                        for helper in helper_list:
                            for part in skeleton.part_selected:
                                if list(skeleton.rect_part_list.keys())[part] in helper.rect_part_list:
                                    helper.select_part(mouse_pos, True, False, list(skeleton.rect_part_list.keys())[part])

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
                                anim_to_pool(current_pool, skeleton)
                                break

                    elif undo_button.rect.collidepoint(mouse_pos):
                        undo_press = True

                    elif redo_button.rect.collidepoint(mouse_pos):
                        redo_press = True

                    elif rename_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("text_input", "new_name")
                        input_ui.change_instruction("Rename Animation:")
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
                        skeleton.edit_part(mouse_pos, "flip1")

                    elif flip_vert_button.rect.collidepoint(mouse_pos):
                        skeleton.edit_part(mouse_pos, "flip2")

                    elif reset_button.rect.collidepoint(mouse_pos):
                        skeleton.edit_part(mouse_pos, "reset")

                    elif direction_button.rect.collidepoint(mouse_pos):
                        popup_list_open("animation_side", direction_button.rect.bottomleft, direction_list, "top")

                    elif direction_part_button.rect.collidepoint(mouse_pos):
                        if race_part_button.text != "":
                            popup_list_open("part_side", direction_part_button.rect.topleft, direction_list, "bottom")

                    elif part_selector.rect.collidepoint(mouse_pos):
                        if direction_part_button.text != "" and race_part_button.text != "":
                            current_part = list(skeleton.animation_part_list[current_frame].keys())[skeleton.part_selected[-1]]
                            # try:
                            if "p1" in current_part or "p2" in current_part:
                                selected_part = current_part[3:]
                                if selected_part[0:2] == "r_" or selected_part[0:2] == "l_":
                                    selected_part = selected_part[2:]
                                part_list = list(gen_body_sprite_pool[race_part_button.text][direction_part_button.text][selected_part].keys())
                            elif "effect" in current_part:
                                part_list = list(effect_sprite_pool[race_part_button.text][direction_part_button.text].keys())
                            elif "special" in current_part:
                                part_list = list(
                                    gen_body_sprite_pool[race_part_button.text][direction_part_button.text]["special"].keys())
                            # except KeyError:  # look at weapon next
                            #     selected_part = race_part_button.text
                            #     part_list = list(gen_weapon_sprite_pool[selected_part][direction_part_button.text].keys())
                            popup_list_open("part_select", part_selector.rect.topleft, part_list, "bottom")

                    elif p1_eye_selector.rect.collidepoint(mouse_pos):
                        part_list = ["Any"] + list(gen_body_sprite_pool[skeleton.p1_race][direction_list[skeleton.side]]["eye"].keys())
                        popup_list_open("p1_eye_select", p1_eye_selector.rect.topleft, part_list, "bottom")

                    elif p1_mouth_selector.rect.collidepoint(mouse_pos):
                        part_list = ["Any"] + list(gen_body_sprite_pool[skeleton.p1_race][direction_list[skeleton.side]]["mouth"].keys())
                        popup_list_open("p1_mouth_select", p1_mouth_selector.rect.topleft, part_list, "bottom")

                    elif p2_eye_selector.rect.collidepoint(mouse_pos):
                        part_list = ["Any"] + list(gen_body_sprite_pool[skeleton.p2_race][direction_list[skeleton.side]]["eye"].keys())
                        popup_list_open("p2_eye_select",
                                        (p2_eye_selector.rect.topleft[0] - (45 * screen_scale[0]), p2_eye_selector.rect.topleft[1]), part_list,
                                          "bottom")

                    elif p2_mouth_selector.rect.collidepoint(mouse_pos):
                        part_list = ["Any"] + list(gen_body_sprite_pool[skeleton.p2_race][direction_list[skeleton.side]]["mouth"].keys())
                        popup_list_open("p2_mouth_select",
                                        (p2_mouth_selector.rect.topleft[0] - (45 * screen_scale[0]), p2_mouth_selector.rect.topleft[1]), part_list,
                                          "bottom")

                    elif race_part_button.rect.collidepoint(mouse_pos):
                        if skeleton.part_selected != []:
                            current_part = list(skeleton.rect_part_list.keys())[skeleton.part_selected[-1]]
                            if "weapon" in current_part:
                                part_list = list(gen_weapon_sprite_pool)
                            elif "effect" in current_part:
                                part_list = list(effect_sprite_pool)
                            else:
                                part_list = list(gen_body_sprite_pool.keys())
                            popup_list_open("race_select", race_part_button.rect.topleft, part_list, "bottom")

                    elif new_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("text_input", "new_animation")
                        input_ui.change_instruction("New Animation Name:")
                        ui.add(input_ui_popup)

                    elif save_button.rect.collidepoint(mouse_pos):
                        text_input_popup = ("confirm_input", "save_animation")
                        input_ui.change_instruction("Save Current Animation?")
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
                        popup_list_open("animation_select", animation_selector.rect.bottomleft,
                                        [item for item in current_pool[direction]], "top")

                    else:  # click on other stuff
                        for strip_index, strip in enumerate(filmstrips):  # click on frame film list
                            if strip.rect.collidepoint(mouse_pos) and current_frame != strip_index:  # click new frame
                                current_frame = strip_index
                                anim.show_frame = current_frame
                                skeleton.edit_part(mouse_pos, "change")
                                current_frame_row = 0
                                setup_list(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
                                           frame_prop_listbox, ui, layer=9, old_list=frame_property_select[current_frame])  # change frame property list
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
                            skeleton.part_selected = []  # clear old list first
                            if shift_press is False and ctrl_press is False:  # remove selected part in other helpers
                                for index, helper in enumerate(helper_list):
                                    if helper != helper_click:
                                        helper.select_part(None, False, True)
                            if helper_click.part_selected != []:
                                for part in helper_click.part_selected:
                                    skeleton.click_part(mouse_pos, True, False, part)

                if copy_press:
                    copy_part_frame = {key: (value[:] if type(value) == list else value) for key, value in
                                       skeleton.bodypart_list[current_frame].items()}
                    copy_animation_frame = {key: (value[:] if value is not None else value) for key, value in
                                            skeleton.animation_part_list[current_frame].items()}
                    copy_name_frame = {key: (value[:] if value is not None else value) for key, value in
                                       skeleton.part_name_list[current_frame].items()}

                elif paste_press:
                    if copy_animation_frame is not None:
                        skeleton.bodypart_list[current_frame] = {key: (value[:] if type(value) == list else value) for key, value in
                                                                 copy_part_frame.items()}
                        skeleton.animation_part_list[current_frame] = {key: (value[:] if value is not None else value) for key, value in
                                                                       copy_animation_frame.items()}
                        skeleton.part_name_list[current_frame] = {key: (value[:] if value is not None else value) for key, value in
                                                                  copy_name_frame.items()}
                        skeleton.edit_part(mouse_pos, "change")

                elif part_copy_press:
                    if skeleton.part_selected != []:
                        copy_part = {key: (value[:] if type(value) == list else value) for key, value in
                                     skeleton.bodypart_list[current_frame].items()}
                        copy_animation = {key: (value[:] if value is not None else value) for key, value in
                                          skeleton.animation_part_list[current_frame].items()}
                        copy_name = {key: (value[:] if value is not None else value) for key, value in
                                     skeleton.part_name_list[current_frame].items()}

                        # keep only selected one
                        copy_part = {item: copy_part[item] for item in copy_part.keys() if item in skeleton.rect_part_list and list(skeleton.rect_part_list.keys()).index(item) in skeleton.part_selected}
                        copy_animation = {item: copy_animation[item] for index, item in enumerate(copy_animation.keys()) if
                                          index in skeleton.part_selected}
                        copy_name = {item: copy_name[item] for index, item in enumerate(copy_name.keys()) if index in skeleton.part_selected}

                elif part_paste_press:
                    if copy_part is not None:
                        skeleton.edit_part(mouse_pos, "paste")

                elif undo_press:
                    if current_history != 0:
                        current_history -= 1
                        skeleton.edit_part(None, "undo")

                elif redo_press:
                    if len(animation_history) - 1 > current_history:
                        current_history += 1
                        skeleton.edit_part(None, "redo")

                if showroom.rect.collidepoint(mouse_pos):  # mouse at show room
                    new_mouse_pos = pygame.Vector2((mouse_pos[0] - showroom.rect.topleft[0]) / screen_size[0] * 500 * skeleton.size,
                                                   (mouse_pos[1] - showroom.rect.topleft[1]) / screen_size[1] * 500 * skeleton.size)
                    if mouse_left_up:  # left click on showroom
                        skeleton.click_part(new_mouse_pos, shift_press, ctrl_press)
                        for index, helper in enumerate(helper_list):
                            helper.select_part(None, shift_press, ctrl_press)
                            if skeleton.part_selected != []:
                                for part in skeleton.part_selected:
                                    if list(skeleton.rect_part_list.keys())[part] in helper.rect_part_list:
                                        helper.select_part(mouse_pos, shift_press, ctrl_press, list(skeleton.rect_part_list.keys())[part])
                    if mouse_wheel_up or mouse_wheel_down:
                        skeleton.edit_part(new_mouse_pos, "rotate")
                    elif mouse_right_up or mouse_right_down:
                        if keypress_delay == 0:
                            skeleton.edit_part(new_mouse_pos, "place")
                            keypress_delay = 0.1

            if skeleton.part_selected != []:
                part = skeleton.part_selected[-1]
                if skeleton.animation_part_list[current_frame] is not None and \
                        list(skeleton.rect_part_list.keys())[part] in list(skeleton.animation_part_list[current_frame].keys()):
                    name_text = skeleton.part_name_list[current_frame][list(skeleton.rect_part_list.keys())[part]]
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
                animation_name = input_box.text
                animation_selector.change_name(animation_name)
                current_frame = 0
                skeleton.edit_part(mouse_pos, "new")
                change_animation(animation_name)

            elif text_input_popup[1] == "save_animation":
                anim_save_pool(current_pool, "generic")

            elif text_input_popup[1] == "new_name":
                old_name = animation_name
                animation_name = input_box.text
                animation_selector.change_name(animation_name)
                anim_to_pool(current_pool, skeleton, replace=old_name)

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
                anim_to_pool(current_pool, skeleton, duplicate=old_name)

            elif text_input_popup[1] == "del_animation":
                anim_del_pool(current_pool)
                if len(current_pool[0]) == 0:  # no animation left, create empty one
                    animation_name = "empty"
                    animation_selector.change_name(animation_name)
                    current_frame = 0
                    skeleton.edit_part(mouse_pos, "new")
                else:  # reset to the first animation
                    change_animation(list(current_pool[0].keys())[0])

            elif text_input_popup[1] == "change_speed":
                if input_box.text.isdigit():
                    new_speed = int(input_box.text)
                    speed_button.change_text("Speed: " + input_box.text)
                    anim.speed_ms = (500 / new_speed) / 1000

            elif text_input_popup[1] == "new_anim_prop":
                if input_box.text not in anim_prop_listbox:
                    anim_prop_listbox.namelist.insert(-1, input_box.text)
                if input_box.text not in anim_property_select:
                    anim_property_select.append(input_box.text)
                setup_list(menu.NameList, current_anim_row, anim_prop_listbox.namelist, anim_prop_namegroup,
                           anim_prop_listbox, ui, layer=9, old_list=anim_property_select)
                for frame in skeleton.frame_list:
                    frame["animation_property"] = anim_property_select

            elif text_input_popup[1] == "new_frame_prop":
                if input_box.text not in frame_prop_listbox:
                    frame_prop_listbox.namelist[current_frame].insert(-1, input_box.text)
                if input_box.text not in frame_property_select[current_frame]:
                    frame_property_select[current_frame].append(input_box.text)
                setup_list(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
                           frame_prop_listbox, ui, layer=9, old_list=frame_property_select[current_frame])

            elif "frame_prop_num" in text_input_popup[1] and (input_box.text.isdigit() or "." in input_box.text and re.search("[a-zA-Z]", input_box.text) is None):
                for name in frame_prop_listbox.namelist[current_frame]:
                    if name in (text_input_popup[1]):
                        index = frame_prop_listbox.namelist[current_frame].index(name)
                        frame_prop_listbox.namelist[current_frame][index] = name[0:name.rfind("_") + 1] + input_box.text
                        frame_property_select[current_frame].append(name[0:name.rfind("_") + 1] + input_box.text)
                        setup_list(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
                                   frame_prop_listbox, ui, layer=9, old_list=frame_property_select[current_frame])
                        reload_animation(anim, skeleton)
                        break

            elif "frame_prop_colour" in text_input_popup[1] and re.search("[a-zA-Z]", colour_input_box.text) is None and \
                    colour_input_box.text.count(",") >= 2:
                for name in frame_prop_listbox.namelist[current_frame]:
                    if name in (text_input_popup[1]):
                        index = frame_prop_listbox.namelist[current_frame].index(name)
                        frame_prop_listbox.namelist[current_frame][index] = name[0:name.rfind("_") + 1] + colour_input_box.text.replace(" ", "")
                        frame_property_select[current_frame].append(name[0:name.rfind("_") + 1] + colour_input_box.text.replace(" ", ""))
                        setup_list(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
                                   frame_prop_listbox, ui, layer=9, old_list=frame_property_select[current_frame])
                        reload_animation(anim, skeleton)
                        break

            elif text_input_popup[1] == "change_size" and input_box.text.isdigit():
                skeleton.frame_list[0]["size"] = int(input_box.text)
                skeleton.read_animation(animation_name, old=True)
                reload_animation(anim, skeleton)

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

    ui.update(mouse_pos, mouse_left_up, mouse_left_down, "any")
    anim.play(showroom.image, (0, 0), activate_list)
    for strip_index, strip in enumerate(filmstrips):
        if strip_index == current_frame:
            strip.selected(True)
            break
    pen.fill((150, 150, 150))
    ui.draw(pen)

    pygame.display.update()
    clock.tick(60)
