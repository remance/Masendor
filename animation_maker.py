import csv
import math
import os
import random
import re
import time
from pathlib import Path

import pygame
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from gamescript import commonscript, readstat, menu, battleui
from gamescript.arcade import longscript

rotationxy = commonscript.rotationxy
load_image = commonscript.load_image
load_images = commonscript.load_images
load_base_button = commonscript.load_base_button
stat_convert = readstat.stat_convert
setrotate = longscript.setrotate

main_dir = os.path.split(os.path.abspath(__file__))[0]

default_sprite_size = (200, 200)

screen_size = (1000, 1000)
screen_scale = (screen_size[0] / 1000, screen_size[1] / 1000)

pygame.init()
pen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Animation Maker")  # set the game name on program border/tab
pygame.mouse.set_visible(True)  # set mouse as visible

direction_list = ("front", "side", "back", "sideup", "sidedown")
frame_property_list = ["hold", "turret", "effect_blur_", "effect_contrast_", "effect_brightness_", "effect_fade_", "effect_grey"]
anim_property_list = ["dmgsprite", "interuptrevert"]

# TODO animation save, delete function, special part. After 1.0: unique, lock?, sample effect, cloth sample

def apply_colour(surface, colour=None):
    """Colorise body part sprite"""
    size = (surface.get_width(), surface.get_height())
    data = pygame.image.tostring(surface, "RGBA")  # convert image to string data for filtering effect
    surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data
    alpha = surface.split()[-1]  # save alpha
    surface = surface.convert("L")  # convert to grey scale for colourise
    if colour is not None:
        max_colour = 255  # - (colour[0] + colour[1] + colour[2])
        mid_colour = [c - ((max_colour - c) / 2) for c in colour]
        surface = ImageOps.colorize(surface, black="black", mid=mid_colour, white=colour).convert("RGB")
    surface.putalpha(alpha)  # put back alpha
    surface = surface.tobytes()
    surface = pygame.image.fromstring(surface, size, "RGBA")  # convert image back to a pygame surface
    return surface

def setuplist(itemclass, currentrow, showlist, itemgroup, box, uiclass, layer=1, removeold=True, oldlist=None):
    """generate list of list item"""
    widthadjust = screen_scale[0]
    heightadjust = screen_scale[1]
    row = 5 * heightadjust
    column = 5 * widthadjust
    pos = box.rect.topleft
    if currentrow > len(showlist) - box.maxshowlist:
        currentrow = len(showlist) - box.maxshowlist

    if len(itemgroup) > 0 and removeold:  # remove previous sprite in the group before generate new one
        for stuff in itemgroup:
            stuff.kill()
            del stuff
    addrow = 0
    for index, item in enumerate(showlist):
        if index >= currentrow:
            itemgroup.add(itemclass(screen_scale, box, (pos[0] + column, pos[1] + row), item, layer=layer))  # add new subsection sprite to group
            row += (30 * heightadjust)  # next row
            addrow += 1
            if addrow > box.maxshowlist:
                break  # will not generate more than space allowed

        uiclass.add(*itemgroup)
    if oldlist is not None:
        for item in itemgroup:
            if item.name in oldlist:
                item.select()


def listscroll(mouse_scrollup, mouse_scrolldown, scroll, listbox, currentrow, namelist, namegroup, uiclass, layer=19, oldlist=None):
    if mouse_scrollup:
        currentrow -= 1
        if currentrow < 0:
            currentrow = 0
        else:
            setuplist(menu.NameList, currentrow, namelist, namegroup, listbox, uiclass, layer=layer, oldlist=oldlist)
            scroll.changeimage(newrow=currentrow, logsize=len(namelist))

    elif mouse_scrolldown:
        currentrow += 1
        if currentrow + listbox.maxshowlist - 1 < len(namelist):
            setuplist(menu.NameList, currentrow, namelist, namegroup, listbox, uiclass, layer=layer, oldlist=oldlist)
            scroll.changeimage(newrow=currentrow, logsize=len(namelist))
        else:
            currentrow -= 1
    return currentrow


def popuplist_newopen(action, newrect, newlist, uitype):
    """Move popup_listbox and scroll sprite to new location and create new name list baesd on type"""
    currentpopuprow = 0

    if uitype == "top":
        popup_listbox.rect = popup_listbox.image.get_rect(topleft=newrect)
    elif uitype == "bottom":
        popup_listbox.rect = popup_listbox.image.get_rect(bottomleft=newrect)
    popup_listbox.namelist = newlist
    popup_listbox.action = action
    setuplist(menu.NameList, 0, newlist, popup_namegroup,
              popup_listbox, ui, layer=19)

    popup_listscroll.pos = popup_listbox.rect.topright  # change position variable
    popup_listscroll.rect = popup_listscroll.image.get_rect(topleft=popup_listbox.rect.topright)
    popup_listscroll.changeimage(newrow=0, logsize=len(newlist))
    ui.add(popup_listbox, *popup_namegroup, popup_listscroll)

    popup_listbox.type = uitype


def load_textures(main_dir, subfolder=None):
    """loads all body sprite part image"""
    imgs = {}
    dirpath = os.path.join(main_dir, "data")
    if subfolder is not None:
        for folder in subfolder:
            dirpath = os.path.join(dirpath, folder)

    loadorderfile = [f for f in os.listdir(dirpath) if f.endswith("." + "png")]  # read all file
    loadorderfile.sort(key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r"[^0-9]|[0-9]+", var)])
    for file in loadorderfile:
        imgs[file.split(".")[0]] = load_image(main_dir, file, dirpath)

    return imgs


def reload_animation(animation, char):
    frames = [pygame.transform.smoothscale(thisimage, showroom.size) for thisimage in char.animation_list if thisimage is not None]
    for frame_index in range(0, 10):
        try:
            # add property effect sample
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
                            ImageFilter.GaussianBlur(radius=int(prop[prop.rfind("_") + 1:])))  # blur Image (or apply other filter in future)
                    if "contrast" in prop:
                        enhancer = ImageEnhance.Contrast(surface)
                        surface = enhancer.enhance(int(prop[prop.rfind("_") + 1:]))
                    if "brightness" in prop:
                        enhancer = ImageEnhance.Brightness(surface)
                        surface = enhancer.enhance(int(prop[prop.rfind("_") + 1:]))
                    if "fade" in prop:
                        empty = pygame.Surface((frames[frame_index].get_width(), frames[frame_index].get_height()), pygame.SRCALPHA)
                        empty.fill((255,255,255,255))
                        empty = pygame.image.tostring(empty, "RGBA")  # convert image to string data for filtering effect
                        empty = Image.frombytes("RGBA", (frames[frame_index].get_width(), frames[frame_index].get_height()),
                                                empty)  # use PIL to get image data
                        surface = Image.blend(surface, empty, alpha=int(prop[prop.rfind("_") + 1:])/10)
                    surface.putalpha(alpha)  # put back alpha
                    surface = surface.tobytes()
                    surface = pygame.image.fromstring(surface, (frames[frame_index].get_width(), frames[frame_index].get_height()), "RGBA")  # convert image back to a pygame surface
                    frames[frame_index] = surface

            filmstrip_list[frame_index].add_strip(frames[frame_index])
        except IndexError:
            filmstrip_list[frame_index].add_strip()
    animation.reload(frames)
    for helper in helperlist:
        helper.stat1 = char.part_name_list[current_frame]
        helper.stat2 = char.sprite_part
        if char.part_selected != []:
            for part in char.part_selected:
                part = list(char.rect_part_list.keys())[part]
                helper.select((0, 0), True, part)
        else:
            helper.select(None, shift_press)

def anim_to_pool(pool, char):
    """Add animation to animation pool data"""
    if animation_name not in pool[0]:
        for direction in range(0,5):
            pool[direction][animation_name] = []
    pool[char.side][animation_name] = [frame for frame in char.frame_list if frame != {}]

race_list = []
race_acro = []
with open(os.path.join(main_dir, "data", "troop", "troop_race.csv"), encoding="utf-8", mode="r") as unitfile:
    rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
    for row in rd:
        if "," in row[-2]:  # make str with , into list
            thisruleset = [int(item) if item.isdigit() else item for item in row[-2].split(",")]
        else:
            thisruleset = [row[-2]]

        for n, i in enumerate(row):
            if i.isdigit() or ("." in i and re.search("[a-zA-Z]", i) is None) or i == "inf":
                row[n] = float(i)
        race_list.append(row[1].lower())
        race_acro.append(row[3])
unitfile.close()

race_list = race_list[2:]  # remove header and any race
race_acro = race_acro[2:]
race_accept = ["human"]  # for now accept only human race

generic_animation_pool = []
for direction in direction_list:
    with open(os.path.join(main_dir, "data", "animation", "generic", direction+ ".csv"), encoding="utf-8", mode="r") as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
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
    unitfile.close()

skel_joint_list = []
for race in race_list:
    if race in race_accept:
        for direction in direction_list:
            with open(os.path.join(main_dir, "data", "sprite", "generic", race, direction, "skeleton_link.csv"), encoding="utf-8",
                      mode="r") as unitfile:
                rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
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
            unitfile.close()

with open(os.path.join(main_dir, "data", "sprite", "generic", "skin_colour_rgb.csv"), encoding="utf-8",
          mode="r") as unitfile:
    rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
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
            partfolder = Path(os.path.join(main_dir, "data", "sprite", "generic", race, direction))
            subdirectories = [str(x).split("data\\")[1].split("\\") for x in partfolder.iterdir() if x.is_dir()]
            for folder in subdirectories:
                imgs = load_textures(main_dir, folder)
                gen_body_sprite_pool[race][direction][folder[-1]] = imgs

gen_weapon_sprite_pool = {}
partfolder = Path(os.path.join(main_dir, "data", "sprite", "generic", "weapon"))
subdirectories = [str(x).split("data\\")[1].split("\\") for x in partfolder.iterdir() if x.is_dir()]
for folder in subdirectories:
    gen_weapon_sprite_pool[folder[-1]] = {}
    partsubfolder = Path(os.path.join(main_dir, "data", "sprite", "generic", "weapon", folder[-1]))
    subsubdirectories = [str(x).split("data\\")[1].split("\\") for x in partsubfolder.iterdir() if x.is_dir()]
    for subfolder in subsubdirectories:
        for direction in direction_list:
            imgs = load_textures(main_dir, ["sprite", "generic", "weapon", folder[-1], subfolder[-1] , direction])
            if direction not in gen_weapon_sprite_pool[folder[-1]]:
                gen_weapon_sprite_pool[folder[-1]][direction] = imgs
            else:
                gen_weapon_sprite_pool[folder[-1]][direction].update(imgs)

effect_sprite_pool = {}
partfolder = Path(os.path.join(main_dir, "data", "sprite", "effect"))
subdirectories = [str(x).split("data\\")[1].split("\\") for x in partfolder.iterdir() if x.is_dir()]
for folder in subdirectories:
    effect_sprite_pool[folder[-1]] = {}
    partfolder = Path(os.path.join(main_dir, "data", "sprite", "effect", folder[-1]))
    subsubdirectories = [str(x).split("data\\")[1].split("\\") for x in partfolder.iterdir() if x.is_dir()]
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
        self.image_original2 = self.image_original.copy()  # after add sprite but before adding selected corner
        self.rect = self.image.get_rect(topleft=self.pos)
        self.image_scale = (self.image.get_width() / 100, self.image.get_height() / 120)
        self.blitimage = None
        self.strip_rect = None
        self.activate = True

    def update(self, *args):
        self.image = self.image_original2.copy()

    def selected(self, select=False):
        self.image = self.image_original2.copy()
        select_colour = (200, 100, 100)
        if self.activate:
            select_colour = (150, 200, 100)
        if select:
            pygame.draw.rect(self.image, select_colour, (0, 0, self.image.get_width(), self.image.get_height()), 15)

    def add_strip(self, image=None):
        self.image = self.image_original.copy()
        if image is not None:
            self.blitimage = pygame.transform.scale(image.copy(), (int(100 * self.image_scale[0]), int(100 * self.image_scale[1])))
            self.strip_rect = self.blitimage.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
            self.image.blit(self.blitimage, self.strip_rect)
        self.image_original2 = self.image.copy()
        if self.activate is False:
            pygame.draw.rect(self.image_original2, (0, 0, 0), (0, 0, self.image.get_width(), self.image.get_height()), 15)


class Button(pygame.sprite.Sprite):
    """Normal button"""

    def __init__(self, text, image, pos, fontsize=20):
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(fontsize * screen_scale[1]))
        self.image = image.copy()
        self.image_original = self.image.copy()
        self.text = text
        self.pos = pos
        textsurface = self.font.render(str(text), 1, (0, 0, 0))
        textrect = textsurface.get_rect(center=(int(self.image.get_width() / 2), int(self.image.get_height() / 2)))
        self.image.blit(textsurface, textrect)
        self.rect = self.image.get_rect(center=self.pos)

    def change_text(self, text):
        if text != self.text:
            self.image = self.image_original.copy()
            self.text = text
            textsurface = self.font.render(self.text.capitalize(), 1, (0, 0, 0))
            textrect = textsurface.get_rect(center=(int(self.image.get_width() / 2), int(self.image.get_height() / 2)))
            self.image.blit(textsurface, textrect)
            self.rect = self.image.get_rect(center=self.pos)


class SwitchButton(pygame.sprite.Sprite):
    """Button that switch text/option"""

    def __init__(self, text_list, image, pos, fontsize=20):
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(fontsize * screen_scale[1]))
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
        textsurface = self.font.render(str(text), 1, (0, 0, 0))
        textrect = textsurface.get_rect(center=(int(self.image.get_width() / 2), int(self.image.get_height() / 2)))
        self.image.blit(textsurface, textrect)


class Bodyhelper(pygame.sprite.Sprite):
    def __init__(self, size, pos, type, part_images):
        self._layer = 6
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.fontsize = int(12 * screen_scale[1])
        self.font = pygame.font.SysFont("helvetica", self.fontsize)
        self.size = size
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.image.fill((255, 255, 255))
        pygame.draw.rect(self.image, (100, 150, 150), (0, 0, self.image.get_width(), self.image.get_height()), 3)
        self.image_original = self.image.copy()  # for original before add part and click
        self.rect = self.image.get_rect(center=pos)
        self.type = type
        self.part_images_original = [image.copy() for image in part_images]
        if self.type in ("p1", "p2"):
            self.boxfont = pygame.font.SysFont("helvetica", int(22 * screen_scale[1]))
            empytybox = self.part_images_original[-1]
            self.part_images_original = self.part_images_original[:-1]
            for boxpart in ("W1", "W2"):
                textsurface = self.boxfont.render(boxpart, 1, (0, 0, 0))
                textrect = textsurface.get_rect(center=(empytybox.get_width() / 2, empytybox.get_height() / 2))
                newbox = empytybox.copy()
                newbox.blit(textsurface, textrect)
                self.part_images_original.append(newbox)
        else:
            self.boxfont = pygame.font.SysFont("helvetica", int(18 * screen_scale[1]))
            empytybox = self.part_images_original[0]
            self.part_images_original = self.part_images_original[:-1]
            for boxpart in ("S1", "S2", "S3", "S4", "S5", "E1", "E2", "DE1", "DE2"):
                textsurface = self.boxfont.render(boxpart, 1, (0, 0, 0))
                textrect = textsurface.get_rect(center=(empytybox.get_width() / 2, empytybox.get_height() / 2))
                newbox = empytybox.copy()
                newbox.blit(textsurface, textrect)
                self.part_images_original.append(newbox)
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
            thiskey = list(self.part_pos.keys())[index]
            pos = self.part_pos[thiskey]
            newimage = image.copy()
            if thiskey in self.part_selected:  # highlight selected part
                newimage = apply_colour(newimage, (34, 177, 76))

            rect = newimage.get_rect(center=pos)
            self.image.blit(newimage, rect)
            self.rect_part_list[thiskey] = rect

    def select(self, check_mouse_pos, shift_press, specific_part=None):
        if specific_part is not None:
            if specific_part is False:
                self.part_selected = []
            elif specific_part in list(self.part_pos.keys()):
                if shift_press:
                    self.part_selected.append(specific_part)
                else:
                    self.part_selected = [specific_part]
            self.blit_part()
        else:
            click_any = False
            if check_mouse_pos is not None:
                for index, rect in enumerate(self.rect_part_list):
                    thisrect = self.rect_part_list[rect]
                    if thisrect is not None and thisrect.collidepoint(check_mouse_pos):
                        click_any = True
                        if shift_press:
                            self.part_selected.append(list(self.part_pos.keys())[index])
                        else:
                            self.part_selected = [list(self.part_pos.keys())[index]]
                            break
            elif check_mouse_pos is None or (click_any is False and shift_press is False):
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
                newchange = ["S", "F", "B", "CU", "CD"]
                for index, change in enumerate(["side", "front", "back", "sideup", "sidedown"]):
                    if stat[1] == index:
                        stat[1] = newchange[index]
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

                textcolour = (0, 0, 0)
                if part in self.part_selected:  # green text for selected part
                    textcolour = (20, 90, 20)
                textsurface1 = self.font.render(stat1, 1, textcolour)

                textsurface2 = self.font.render(stat2, 1, textcolour)
                shiftx = 50 * screen_scale[0]
                if any(ext in part for ext in ["effect", "special"]):
                    textrect1 = textsurface1.get_rect(midleft=(self.part_pos[part][0] + shiftx, self.part_pos[part][1] - 10))
                    textrect2 = textsurface2.get_rect(midleft=(self.part_pos[part][0] + shiftx, self.part_pos[part][1] - 10 + self.fontsize + 2))
                elif "body" in part:
                    headname = "p1_head"
                    if "p2" in part:
                        headname = "p2_head"
                    textrect1 = textsurface1.get_rect(midleft=(self.part_pos[headname][0] + shiftx, self.part_pos[headname][1] - 5))
                    textrect2 = textsurface2.get_rect(
                        midleft=(self.part_pos[headname][0] + shiftx, self.part_pos[headname][1] - 5 + self.fontsize + 2))
                elif "head" in part:
                    textrect1 = textsurface1.get_rect(midright=(self.part_pos[part][0] - shiftx, self.part_pos[part][1] - 10))
                    textrect2 = textsurface2.get_rect(midright=(self.part_pos[part][0] - shiftx, self.part_pos[part][1] - 10 + self.fontsize + 2))
                else:
                    shiftx = 14 * screen_scale[0]
                    if "weapon" in part:
                        shiftx = 26 * screen_scale[0]
                    if self.part_pos[part][0] > self.image.get_width() / 2:
                        textrect1 = textsurface1.get_rect(midleft=(self.part_pos[part][0] + shiftx, self.part_pos[part][1] - 15))
                        textrect2 = textsurface2.get_rect(midleft=(self.part_pos[part][0] + shiftx, self.part_pos[part][1] - 15 + self.fontsize + 2))
                    else:
                        textrect1 = textsurface1.get_rect(midright=(self.part_pos[part][0] - shiftx, self.part_pos[part][1] - 15))
                        textrect2 = textsurface2.get_rect(midright=(self.part_pos[part][0] - shiftx, self.part_pos[part][1] - 15 + self.fontsize + 2))
                self.image.blit(textsurface1, textrect1)
                self.image.blit(textsurface2, textrect2)
            # else:
            #     text_surface = self.font.render("None", 1, (0, 0, 0))
            #     text_rect = text_surface.get_rect(midleft=self.part_pos[part])
            #     self.image.blit(text_surface, text_rect)


class NameBox(pygame.sprite.Sprite):
    def __init__(self, size, pos):
        self._layer = 6
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.fontsize = int(24 * screen_scale[1])
        self.font = pygame.font.SysFont("helvetica", int(self.fontsize * screen_scale[1]))
        self.size = size
        self.image = pygame.Surface(self.size)
        self.image.fill((255, 255, 255))
        pygame.draw.rect(self.image, (150, 200, 0), (0, 0, self.image.get_width(), self.image.get_height()), 2)
        self.image_original = self.image.copy()
        self.pos = pos
        self.rect = self.image.get_rect(midtop=self.pos)
        self.text = None

    def change_name(self, text):
        if text != self.text:
            self.image = self.image_original.copy()
            self.text = text
            textsurface = self.font.render(self.text, 1, (0, 0, 0))
            textrect = textsurface.get_rect(center=(int(self.image.get_width() / 2), int(self.image.get_height() / 2)))
            self.image.blit(textsurface, textrect)


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
        self.part_selected = []
        self.not_show = []
        self.p1_race = "human"
        self.p2_race = "human"
        skin = list(skin_colour_list.keys())[random.randint(0, len(skin_colour_list) - 1)]
        skin_colour = skin_colour_list[skin]
        self.p1_hair_colour = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.p1_eye_colour = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.p2_hair_colour = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.p2_eye_colour = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
        self.weapon = {"p1_main_weapon": "sword", "p1_sub_weapon": None, "p2_main_weapon": None, "p2_sub_weapon": None}
        self.empty_sprite_part = [0, pygame.Vector2(0, 0), [50, 50], 0, 0, 0, 1]
        self.randomface()
        self.p1_any_eye = self.p1_eye
        self.p1_any_mouth = self.p1_mouth
        self.p2_any_eye = self.p2_eye
        self.p2_any_mouth = self.p2_mouth
        self.size = 1  # size scale of sprite
        try:
            self.read_animation(list(animation_pool.keys())[0])
            self.default_sprite_part = {key: (value[:] if value is not None else value) for key, value in self.animation_part_list[0].items()}
            self.default_body_part = {key: value for key, value in self.bodypart_list[0].items()}
            self.default_part_name = {key: value for key, value in self.part_name_list[0].items()}
        except IndexError:  # empty animation file
            self.read_animation(None)
            self.default_sprite_part = {key: None for key in self.rect_part_list.keys()}
            self.default_body_part = {key: None for key in self.rect_part_list.keys()}
            self.default_part_name = {key: None for key in self.rect_part_list.keys()}

    def randomface(self):  # todo change when add option to change face
        self.p1_eyebrow = list(gen_body_sprite_pool[self.p1_race]["side"]["eyebrow"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p1_race]["side"]["eyebrow"]) - 1)]
        self.p1_eye = list(gen_body_sprite_pool[self.p1_race]["side"]["eye"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p1_race]["side"]["eye"]) - 1)]
        self.p1_mouth = list(gen_body_sprite_pool[self.p1_race]["side"]["mouth"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p1_race]["side"]["mouth"]) - 1)]
        self.p1_beard = list(gen_body_sprite_pool[self.p1_race]["side"]["beard"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p1_race]["side"]["beard"]) - 1)]
        self.p2_eyebrow = list(gen_body_sprite_pool[self.p2_race]["side"]["eyebrow"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p2_race]["side"]["eyebrow"]) - 1)]
        self.p2_eye = list(gen_body_sprite_pool[self.p2_race]["side"]["eye"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p1_race]["side"]["eye"]) - 1)]
        self.p2_mouth = list(gen_body_sprite_pool[self.p2_race]["side"]["mouth"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p2_race]["side"]["mouth"]) - 1)]
        self.p2_beard = list(gen_body_sprite_pool[self.p2_race]["side"]["beard"].keys())[
            random.randint(0, len(gen_body_sprite_pool[self.p2_race]["side"]["beard"]) - 1)]

    def read_animation(self, name, old=False, newsize=True):
        #  sprite animation generation from data
        self.animation_part_list = []
        self.animation_list = []
        self.bodypart_list = [{key: None for key in self.rect_part_list.keys()}] * 10
        self.part_name_list = [{key: None for key in self.rect_part_list.keys()}] * 10
        self.sprite_part = {key: None for key in self.rect_part_list.keys()}
        if name is not None:
            frame_list = generic_animation_pool[self.side][name].copy()
            if old:
                frame_list = self.frame_list
            if newsize:
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
                if old is False:
                    link_list = {key: None for key in self.rect_part_list.keys()}
                    bodypart_list = {key: None for key in self.rect_part_list.keys()}
                    bodypart_list.update({"p1_eye": None, "p1_mouth": None, "p2_eye": None, "p2_mouth": None})
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
                                    anim_prop_listbox.namelist.insert(-1, stuff)
                                    anim_property_select.append(stuff)
                            elif "frame" in part and pose[part] != 0:
                                for stuff in pose[part]:
                                    frame_prop_listbox.namelist[index].insert(-1, stuff)
                                    frame_property_select[index].append(stuff)
                    self.bodypart_list[index] = bodypart_list
                    self.sprite_part = {key: None for key in self.rect_part_list.keys()}

                main_joint_pos_list = self.generate_body(self.bodypart_list[index])
                part_name = {key: None for key in self.rect_part_list.keys()}

                exceptlist = ["eye", "mouth", "size"]
                for part in part_name_header:
                    if pose[part] != [0] and any(ext in part for ext in exceptlist) is False:
                        if "weapon" in part:
                            if old is False:
                                self.sprite_part[part] = [self.sprite_image[part],
                                                          (self.sprite_image[part].get_width() / 2, self.sprite_image[part].get_height() / 2),
                                                          link_list[part], pose[part][4], pose[part][5], pose[part][6], pose[part][7]]
                            part_name[part] = [self.weapon[part], pose[part][0], pose[part][1]]
                        else:
                            if old is False:
                                self.sprite_part[part] = [self.sprite_image[part], main_joint_pos_list[part], link_list[part], pose[part][5],
                                                          pose[part][6], pose[part][7], pose[part][8]]
                            part_name[part] = [pose[part][0], pose[part][1], pose[part][2]]
                pose_layer_list = {k: v[5] for k, v in self.sprite_part.items() if v is not None}
                pose_layer_list = dict(sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))
                self.animation_part_list.append(self.sprite_part)
                self.part_name_list[index] = part_name
                image = self.create_animation_film(pose_layer_list)
                self.animation_list.append(image)
            self.frame_list = frame_list
            while len(self.frame_list) < 10:  # add empty item
                self.frame_list.append({})


    def create_animation_film(self, pose_layer_list, empty=False):
        image = pygame.Surface((default_sprite_size[0] * self.size, default_sprite_size[1] * self.size),
                               pygame.SRCALPHA)  # default size will scale down later
        for key, value in self.rect_part_list.items():  # reset rect list
            self.rect_part_list[key] = None
        for joint in joints:  # remove all joint first
            joint.kill()
        if empty is False:
            for index, layer in enumerate(pose_layer_list):
                if layer not in self.not_show:
                    part = self.sprite_part[layer]
                    try:
                        image = self.part_to_sprite(image, part[0], list(self.sprite_part.keys()).index(layer),
                                                    part[1], part[2], part[3], part[4], part[6])
                        namecheck = layer
                        if "p1" in namecheck or "p2" in namecheck:
                            namecheck = namecheck[3:]  # remove p1_
                        if namecheck in skel_joint_list[direction_list.index(self.part_name_list[current_frame][layer][1])]:
                            for index, item in enumerate(
                                    skel_joint_list[direction_list.index(self.part_name_list[current_frame][layer][1])][namecheck]):
                                joint_type = 0  # main
                                if index > 0:
                                    joint_type = 1
                                joint_pos = list(item.values())[0]
                                pos = (part[2][0] + (joint_pos[0] - (part[0].get_width() / 2)),
                                       part[2][1] + (joint_pos[1] - (part[0].get_height() / 2)))
                                Joint(joint_type, layer, namecheck, (pos[0] / self.size, pos[1] / self.size), part[3])
                    except IndexError:
                        pass
        return image

    def select_part(self, race, side, part, part_check, part_default):
        """For creating body part like eye or mouth in animation that accept any part (1) so use default instead"""
        if part_check == 1:
            surface = gen_body_sprite_pool[race][side][part][part_default].copy()
        else:
            surface = gen_body_sprite_pool[part_check[0]][part_check[1]][part][part_check[2]].copy()
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
                       self.select_part(p1_head_race, p1_head_side, "eye", bodypart_list["p1_eye"], self.p1_eye),
                       gen_body_sprite_pool[p1_head_race][p1_head_side]["beard"][self.p1_beard].copy(),
                       self.select_part(p1_head_race, p1_head_side, "mouth", bodypart_list["p1_mouth"], self.p1_mouth)]
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
                       self.select_part(p2_head_race, p2_head_side, "eye", bodypart_list["p2_eye"], self.p2_eye),
                       gen_body_sprite_pool[p2_head_race][p2_head_side]["beard"][self.p2_beard].copy(),
                       self.select_part(p2_head_race, p2_head_side, "mouth", bodypart_list["p2_mouth"], self.p2_mouth)]
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
        exceptlist = ["eye", "mouth", "head"]
        for stuff in bodypart_list:
            if bodypart_list[stuff] is not None:
                if any(ext in stuff for ext in exceptlist) is False:
                    if "weapon" in stuff:
                        partname = self.weapon[stuff]
                        if partname is not None and bodypart_list[stuff][2]:
                            self.sprite_image[stuff] = gen_weapon_sprite_pool[partname][bodypart_list[stuff][1]][bodypart_list[stuff][2]].copy()
                    elif "effect_" in stuff:
                        self.sprite_image[stuff] = effect_sprite_pool[bodypart_list[stuff][0]][bodypart_list[stuff][1]][
                            bodypart_list[stuff][2]].copy()
                    else:
                        partname = stuff[3:]  # remove p1_ or p2_ to get part name
                        if "r_" in partname[0:2] or "l_" in partname[0:2]:
                            partname = partname[2:]  # remove side
                        self.sprite_image[stuff] = gen_body_sprite_pool[bodypart_list[stuff][0]][bodypart_list[stuff][1]][partname][
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

    def click_part(self, mouse_pos, shift_press, part=None):
        if part is None:
            click_part = False
            if shift_press is False:
                self.part_selected = []
            for index, rect in enumerate(self.rect_part_list):
                thisrect = self.rect_part_list[rect]
                if thisrect is not None and thisrect.collidepoint(mouse_pos):
                    click_part = True
                    if shift_press:
                        if index not in self.part_selected:
                            self.part_selected.append(index)
                            self.part_selected = list(set(self.part_selected))
                        break
                    elif shift_press is False:
                        self.part_selected = [index]
                        break
            if click_part is False:
                self.part_selected = []
        else:
            if shift_press:
                self.part_selected.append(list(self.rect_part_list.keys()).index(part))
                self.part_selected = list(set(self.part_selected))
            else:
                self.part_selected = [list(self.rect_part_list.keys()).index(part)]

    def edit_part(self, mouse_pos, edit_type):
        global animation_history, bodypart_history, partname_history, current_history
        keylist = list(self.rect_part_list.keys())
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
            if current_frame > len(self.animation_part_list) - 1:
                while current_frame > len(self.animation_part_list) - 1:
                    self.animation_part_list.append({key: None for key in self.rect_part_list.keys()})
                    self.animation_list.append(None)
                    surface = self.create_animation_film(None, empty=True)
                    self.animation_list[-1] = surface

        elif edit_type == "paste":  # paste copy part
            for part in copy_part.keys():
                self.bodypart_list[current_frame][part] = copy_part[part].copy()
                self.animation_part_list[current_frame][part] = copy_animation[part].copy()
                self.part_name_list[current_frame][part] = copy_name[part].copy()

        elif "direction" in edit_type:
            if self.part_selected != []:
                for part in self.part_selected:
                    try:
                        part_index = keylist[part]
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
                        if part_index not in self.not_show:
                            self.not_show.append(part_index)

        elif edit_type == "undo" or edit_type == "redo":
            self.part_name_list[current_frame] = partname_history[current_history]
            self.animation_part_list[current_frame] = animation_history[current_history]
            self.bodypart_list[current_frame] = bodypart_history[current_history]

        elif "eye" in edit_type:
            if "Any" in edit_type:
                if "p1" in edit_type:
                    self.p1_eye = self.p1_any_eye
                elif "p2" in edit_type:
                    self.p2_eye = self.p2_any_eye
            else:
                if "p1" in edit_type:
                    self.p1_eye = edit_type[7:]
                elif "p2" in edit_type:
                    self.p2_eye = edit_type[7:]
            main_joint_pos_list = self.generate_body(self.bodypart_list[current_frame])

        elif "mouth" in edit_type:
            if "Any" in edit_type:
                if "p1" in edit_type:
                    self.p1_mouth = self.p1_any_mouth
                elif "p2" in edit_type:
                    self.p2_mouth = self.p2_any_mouth
            else:
                if "p1" in edit_type:
                    self.p1_eye = edit_type[10:]
                elif "p2" in edit_type:
                    self.p2_eye = edit_type[10:]
            main_joint_pos_list = self.generate_body(self.bodypart_list[current_frame])

        elif "part" in edit_type:
            if self.part_selected != []:
                part = self.part_selected[-1]
                part_index = keylist[part]
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
                if part_index in self.not_show:
                    self.not_show.remove(part_index)

        elif "race" in edit_type:
            if self.part_selected != []:
                part = self.part_selected[-1]
                part_index = keylist[part]
                if part_index in self.not_show:
                    self.not_show.remove(part_index)
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
                    if part_index not in self.not_show:
                        self.not_show.append(part_index)

        elif "new" in edit_type:  # new animation
            self.animation_part_list = [{key: None for key in self.rect_part_list.keys()}]
            p1_face = {"p1_eye": self.p1_eye if self.p1_eye != self.p1_any_eye else 1,
                       "p1_mouth": self.p1_mouth if self.p1_mouth != self.p1_any_mouth else 1}
            p2_face = {"p2_eye": self.p2_eye if self.p2_eye != self.p2_any_eye else 1,
                       "p2_mouth": self.p2_mouth if self.p2_mouth != self.p2_any_mouth else 1}
            self.bodypart_list = [{key: None for key in self.rect_part_list.keys()}] * 10
            for stuff in self.bodypart_list:
                stuff.update(p1_face)
                stuff.update(p2_face)
            self.part_name_list = [{key: None for key in self.rect_part_list.keys()}] * 10
            self.part_selected = []

        elif self.part_selected != []:
            for part in self.part_selected:
                if part < len(keylist):  # can't edit part that not exist
                    part_index = keylist[part]
                    if self.animation_part_list[current_frame][part_index] is not None and \
                            len(self.animation_part_list[current_frame][part_index]) > 3:
                        if edit_type == "place":  # mouse place
                            new_point = mouse_pos
                            if point_edit == 1:  # use joint
                                part_image = self.sprite_image[part_index]
                                center = pygame.Vector2(part_image.get_width() / 2, part_image.get_height() / 2)
                                pos_different = center - self.sprite_part[part_index][
                                    1]  # find distance between image center and connect point main_joint_pos
                                new_point = new_point + pos_different
                            self.animation_part_list[current_frame][part_index][2] = new_point

                        elif "move" in edit_type:  # keyboard move
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

                        elif "tilt" in edit_type:  # keyboard rotate
                            new_angle = self.animation_part_list[current_frame][part_index][3]
                            if "q" in edit_type:
                                new_angle = new_angle - 0.5
                            elif "e" in edit_type:
                                new_angle = new_angle + 0.5
                            self.animation_part_list[current_frame][part_index][3] = new_angle

                        elif edit_type == "rotate":  # mouse rotate
                            base_pos = self.animation_part_list[current_frame][part_index][2]
                            myradians = math.atan2(mouse_pos[1] - base_pos[1], mouse_pos[0] - base_pos[0])
                            newangle = math.degrees(myradians)
                            # """upper left -"""
                            if -180 <= newangle <= -90:
                                newangle = -newangle - 90

                            # """upper right +"""
                            elif -90 < newangle < 0:
                                newangle = (-newangle) - 90

                            # """lower right -"""
                            elif 0 <= newangle <= 90:
                                newangle = -(newangle + 90)

                            # """lower left +"""
                            elif 90 < newangle <= 180:
                                newangle = 270 - newangle

                            self.animation_part_list[current_frame][part_index][3] = newangle

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
                            elif current_flip == 1:  # current hori flip
                                if flip_type == 1:
                                    self.animation_part_list[current_frame][part_index][4] = 0
                                else:
                                    self.animation_part_list[current_frame][part_index][4] = 3
                            elif current_flip == 2:  # current vert flip
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
                            if part_index in self.not_show:
                                self.not_show.remove(part_index)
                            else:
                                self.not_show.append(part_index)

                        elif "layer" in edit_type:
                            if "up" in edit_type:
                                self.animation_part_list[current_frame][part_index][5] += 1
                            elif "down" in edit_type:
                                self.animation_part_list[current_frame][part_index][5] -= 1
                                if self.animation_part_list[current_frame][part_index][5] == 0:
                                    self.animation_part_list[current_frame][part_index][5] = 1
        if len(self.animation_part_list) > 0 and self.animation_part_list[current_frame] != {}:
            self.sprite_part = self.animation_part_list[current_frame]
            pose_layer_list = {k: v[5] for k, v in self.sprite_part.items() if v is not None and v != []}
            pose_layer_list = dict(sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))
            surface = self.create_animation_film(pose_layer_list)
        else:  # create new frame
            self.sprite_part = None
            surface = self.create_animation_film(None, empty=True)
        self.animation_list[current_frame] = surface
        name_list = self.part_name_list[current_frame]
        try:
            self.frame_list[current_frame] = {key: name_list[key] + [self.sprite_part[key][2][0], self.sprite_part[key][2][1], self.sprite_part[key][3], self.sprite_part[key][4],
                                                   self.sprite_part[key][5], self.sprite_part[key][6]] if self.sprite_part[key] is not None else [0]
                                              for key in list(self.rect_part_list.keys())}
        except TypeError:  # None type error from empty frame
            self.frame_list[current_frame] = {key: [0] for key in list(self.rect_part_list.keys())}
        except IndexError:
            self.frame_list[current_frame] = {key: [0] for key in list(self.rect_part_list.keys())}
        for key in list(self.frame_list[current_frame].keys()):
            if "weapon" in key and self.frame_list[current_frame][key] != [0]:
                self.frame_list[current_frame][key] = self.frame_list[current_frame][key][1:]
        p1_face = {"p1_eye": self.p1_eye if self.p1_eye != self.p1_any_eye else 1, "p1_mouth": self.p1_mouth if self.p1_mouth != self.p1_any_mouth else 1}
        p2_face = {"p2_eye": self.p2_eye if self.p2_eye != self.p2_any_eye else 1, "p2_mouth": self.p2_mouth if self.p2_mouth != self.p2_any_mouth else 1}
        p2_face_pos = 13
        self.frame_list[current_frame] = {k: v for k, v in (list(self.frame_list[current_frame].items())[:p2_face_pos] + list(p2_face.items()) +
                                                            list(self.frame_list[current_frame].items())[p2_face_pos:])}
        p1_face_pos = 1
        self.frame_list[current_frame] = {k: v for k, v in (list(self.frame_list[current_frame].items())[:p1_face_pos] + list(p1_face.items()) +
                                                            list(self.frame_list[current_frame].items())[p1_face_pos:])}
        self.frame_list[current_frame]["size"] = self.size
        self.frame_list[current_frame]["frame_property"] = frame_property_select[current_frame]
        self.frame_list[current_frame]["animation_property"] = anim_property_select
        anim_to_pool(generic_animation_pool, self)
        reload_animation(anim, self)

        if edit_type == "new" or edit_type == "change":  # reset history when change frame or create new animation
            partname_history = partname_history[-1:] + [self.part_name_list[current_frame]]
            animation_history = animation_history[-1:] + [self.animation_part_list[current_frame]]
            bodypart_history = bodypart_history[-1:] + [self.bodypart_list[current_frame]]
            current_history = 0

        elif edit_type != "undo" and edit_type != "redo":
            if current_history < len(animation_history) - 1:
                partname_history = partname_history[:current_history + 1]
                animation_history = animation_history[:current_history + 1]
                bodypart_history = bodypart_history[:current_history + 1]

            animation_history.append({key: (value[:] if value is not None else value) for key, value in self.animation_part_list[current_frame].items()})
            bodypart_history.append({key: value for key, value in self.bodypart_list[current_frame].items()})
            partname_history.append({key: value for key, value in self.part_name_list[current_frame].items()})
            current_history += 1

            if len(animation_history) > 100:  # save only last 100 activity
                newfirst = len(animation_history) - 100
                partname_history = partname_history[newfirst:]
                animation_history = animation_history[newfirst:]
                bodypart_history = bodypart_history[newfirst:]
                current_history -= newfirst

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
            new_center = rotationxy(target, new_center, radians_angle)  # find new center point with rotation

        rect = part_rotated.get_rect(center=new_center)
        self.rect_part_list[list(self.rect_part_list.keys())[part_index]] = rect
        surface.blit(part_rotated, rect)

        return surface

    def remake_rectlist(self):
        for key, value in self.rect_part_list.items():  # reset rect list
            self.rect_part_list[key] = None

        for part_index, part in enumerate(self.sprite_part):
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

    def play(self, surface, position, noplay_list):
        if dt > 0:
            if time.time() - self.first_time >= self.speed_ms:
                self.show_frame += 1
                while self.show_frame < 10 and noplay_list[self.show_frame]:
                    self.show_frame += 1
                self.first_time = time.time()
            if self.show_frame > self.end_frame:
                self.show_frame = self.start_frame

        surface.blit(self.frames[int(self.show_frame)], position)
        if dt == 0 and show_joint:
            for joint in joints:
                surface.blit(joint.image, joint.rect)


# start animation maker
clock = pygame.time.Clock()

runtime = 0
mousetimer = 0
play_animation = False
show_joint = True
current_frame = 0
copy_animation_frame = None
copy_part = None
copy_name_frame = None
copy_stat = None
deactivate_list = [False] * 10
currentpopuprow = 0
keypress_delay = 0
point_edit = 0
textinputpopup = (None, None)
animation_history = []
bodypart_history = []
partname_history = []
current_history = 0

ui = pygame.sprite.LayeredUpdates()
fakegroup = pygame.sprite.LayeredUpdates()  # just fake group to add for container and not get auto update

showroom_scale = ((default_sprite_size[0] * screen_size[0] / 500, default_sprite_size[1] * screen_size[1] / 500))
showroom_scale_mul = (showroom_scale[0] / default_sprite_size[0], showroom_scale[1] / default_sprite_size[1])
showroom = Showroom(showroom_scale)
ui.add(showroom)

Joint.images = [pygame.transform.scale(load_image(main_dir, "mainjoint.png", ["animation_maker_ui"]),
                                       (int(20 * screen_scale[0]), int(20 * screen_scale[1]))),
                pygame.transform.scale(load_image(main_dir, "subjoint.png", ["animation_maker_ui"]),
                                       (int(20 * screen_scale[0]), int(20 * screen_scale[1])))]
joints = pygame.sprite.Group()

image = pygame.transform.scale(load_image(main_dir, "film.png", ["animation_maker_ui"]),
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

imgs = load_images(main_dir, ["animation_maker_ui", "helper_parts"])
bodyhelper_size = (370 * screen_scale[0], 270 * screen_scale[1])
p1_body_helper = Bodyhelper(bodyhelper_size, (bodyhelper_size[0] / 2,
                                              screen_size[1] - (bodyhelper_size[1] / 2)), "p1", imgs[0:13])
p2_body_helper = Bodyhelper(bodyhelper_size, (screen_size[0] - (bodyhelper_size[0] / 2),
                                              screen_size[1] - (bodyhelper_size[1] / 2)), "p2", imgs[0:13])
effecthelper_size = (250 * screen_scale[0], 270 * screen_scale[1])
effect_helper = Bodyhelper(effecthelper_size, (screen_size[0] / 2,  screen_size[1] - (bodyhelper_size[1] / 2)),
                           "effect", imgs[13:14])
helperlist = [p1_body_helper, p2_body_helper, effect_helper]

image = load_image(main_dir, "button.png", ["animation_maker_ui"])
image = pygame.transform.scale(image, (int(image.get_width() * screen_scale[1]),
                                       int(image.get_height() * screen_scale[1])))

new_button = Button("New", image, (image.get_width() / 2, image.get_height() / 2))
save_button = Button("Save", image, (image.get_width() * 1.5, image.get_height() / 2))
size_button = Button("Size: ", image, (image.get_width() * 2.5, image.get_height() / 2))
direction_button = Button("", image, (image.get_width() * 3.5, image.get_height() / 2))
duplicate_button = Button("Duplicate", image, (image.get_width() * 11, image.get_height() / 2))
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
p1_eye_selector.change_name("P1 Eye: Any")
p1_mouth_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 1.8,
                                                        p1_body_helper.rect.midtop[1] - (image.get_height() * 2.2)))
p1_mouth_selector.change_name("P1 Mouth: Any")
p2_eye_selector = NameBox((250, image.get_height()), (screen_size[0] - (reset_button.image.get_width() * 1.8),
                                                      p1_body_helper.rect.midtop[1] - (image.get_height() * 3.2)))
p2_eye_selector.change_name("P2 Eye: Any")
p2_mouth_selector = NameBox((250, image.get_height()), (screen_size[0] - (reset_button.image.get_width() * 1.8),
                                                        p1_body_helper.rect.midtop[1] - (image.get_height() * 2.2)))
p2_mouth_selector.change_name("P2 Mouth: Any")
# lock_button = SwitchButton(["Lock:OFF","Lock:ON"], image, (reset_button.pos[0] + reset_button.image.get_width() * 2,
#                                            p1_body_helper.rect.midtop[1] - (image.get_height() / 1.5)))

input_ui_img = load_image(main_dir, "inputui.png", "ui\\mainmenu_ui")
inputui = menu.InputUI(screen_scale, input_ui_img,
                       (screen_size[0] / 2, screen_size[1] / 2))  # user text input ui box popup

imagelist = load_base_button(main_dir)

input_ok_button = menu.MenuButton(screen_scale, imagelist, pos=(inputui.rect.midleft[0] + imagelist[0].get_width(),
                                                                inputui.rect.midleft[1] + imagelist[0].get_height()),
                                  text="Confirm", layer=31)
input_cancel_button = menu.MenuButton(screen_scale, imagelist,
                                      pos=(inputui.rect.midright[0] - imagelist[0].get_width(),
                                           inputui.rect.midright[1] + imagelist[0].get_height()),
                                      text="Cancel", layer=31)
input_button = (input_ok_button, input_cancel_button)
input_box = menu.InputBox(screen_scale, inputui.rect.center, inputui.image.get_width())  # user text input box

inputui_pop = (inputui, input_box, input_ok_button, input_cancel_button)

confirmui = menu.InputUI(screen_scale, input_ui_img,
                         (screen_size[0] / 2, screen_size[1] / 2))  # user confirm input ui box popup
confirmui_pop = (confirmui, input_ok_button, input_cancel_button)

boximg = load_image(main_dir, "unit_presetbox.png", "ui\\mainmenu_ui")

menu.ListBox.containers = popup_listbox
popup_listbox = menu.ListBox(screen_scale, (0, 0), boximg, 15)  # popup listbox need to be in higher layer
popup_listscroll = battleui.UIScroller(popup_listbox.rect.topright,
                                       popup_listbox.image.get_height(),
                                       popup_listbox.maxshowlist,
                                       layer=14)
anim_prop_listbox = menu.ListBox(screen_scale, (0, filmstrip_list[0].rect.midbottom[1] +
                                                (reset_button.image.get_height() * 1.5)), boximg, 8)
anim_prop_listbox.namelist = anim_property_list + ["Custom"]
frame_prop_listbox = menu.ListBox(screen_scale, (screen_size[0] - boximg.get_width(), filmstrip_list[0].rect.midbottom[1] +
                                                (reset_button.image.get_height() * 1.5)), boximg, 8)
frame_prop_listbox.namelist = [ frame_property_list + ["Custom"] for _ in range(10) ]
anim_prop_listscroll = battleui.UIScroller(anim_prop_listbox.rect.topright,
                                       anim_prop_listbox.image.get_height(),
                                       anim_prop_listbox.maxshowlist,
                                       layer=10)
frame_prop_listscroll = battleui.UIScroller(frame_prop_listbox.rect.topright,
                                       frame_prop_listbox.image.get_height(),
                                       frame_prop_listbox.maxshowlist,
                                       layer=10)
current_anim_row = 0
current_frame_row = 0
frame_property_select = [ [] for _ in range(10) ]
anim_property_select = []
setuplist(menu.NameList, current_anim_row, anim_prop_listbox.namelist, anim_prop_namegroup,
          anim_prop_listbox, ui, layer=9, removeold=False)
setuplist(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
          frame_prop_listbox, ui, layer=9, removeold=False)
anim_prop_listscroll.changeimage(newrow=0, logsize=len(anim_prop_listbox.namelist))
frame_prop_listscroll.changeimage(newrow=0, logsize=len(frame_prop_listbox.namelist[current_frame]))
ui.add(anim_prop_listbox, frame_prop_listbox, anim_prop_listscroll, frame_prop_listscroll)

animation_selector = NameBox((400, image.get_height()), (screen_size[0] / 2, 0))
part_selector = NameBox((250, image.get_height()), (reset_button.image.get_width() * 4,
                                                    reset_button.rect.midtop[1]))

shift_press = False
anim = Animation(500, True)
skeleton = Skeleton()
skeleton.animation_list = []
direction = 1
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
    uidt = dt
    mouse_pos = pygame.mouse.get_pos()  # current mouse pos based on screen
    mouse_up = False  # left click
    mouse_leftdown = False  # hold left click
    mouse_right = False  # right click
    mouse_rightdown = False  # hold right click
    double_mouse_right = False  # double right click
    mouse_scrolldown = False
    mouse_scrollup = False
    mouse_wheel = False  # mouse wheel click
    mouse_wheeldown = False  # hold mouse wheel click
    copy_press = False
    paste_press = False
    part_copy_press = False
    part_paste_press = False
    undo_press = False
    redo_press = False
    del_press = False
    shift_press = False
    popup_click = False
    input_esc = False
    popup_list = []

    keypress = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # left click
                mouse_up = True
            if event.button == 2:  # left click
                mouse_wheel = True
            elif event.button == 3:  # Right Click
                mouse_right = True
                if mousetimer == 0:
                    mousetimer = 0.001  # Start timer after first mouse click
                elif mousetimer < 0.3:  # if click again within 0.3 second for it to be considered double click
                    double_mouse_right = True  # double right click
                    mousetimer = 0
            elif event.button == 4 or event.button == 5:
                if event.button == 4:  # Mouse scroll up
                    mouse_scrollup = True
                else:  # Mouse scroll down
                    mouse_scrolldown = True
                if popup_listbox in ui and popup_listbox.rect.collidepoint(mouse_pos):
                    currentpopuprow = listscroll(mouse_scrollup, mouse_scrolldown, popup_listscroll, popup_listbox,
                                                 currentpopuprow, popup_listbox.namelist, popup_namegroup, ui)
                elif skeleton.part_selected != [] and showroom.rect.collidepoint(mouse_pos):
                    if event.button == 4:  # Mouse scroll up
                        skeleton.edit_part(mouse_pos, "scale_up")
                    else:  # Mouse scroll down
                        skeleton.edit_part(mouse_pos, "scale_down")
                elif anim_prop_listbox.rect.collidepoint(mouse_pos) or anim_prop_listscroll.rect.collidepoint(mouse_pos):
                    current_anim_row = listscroll(mouse_scrollup, mouse_scrolldown, anim_prop_listscroll, anim_prop_listbox,
                                                  current_anim_row, anim_prop_listbox.namelist, anim_prop_namegroup, ui,
                                                  oldlist=anim_property_select)
                elif frame_prop_listbox.rect.collidepoint(mouse_pos) or frame_prop_listscroll.rect.collidepoint(mouse_pos):
                    current_frame_row = listscroll(mouse_scrollup, mouse_scrolldown, frame_prop_listscroll, frame_prop_listbox,
                                                 current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup, ui,
                                                   oldlist=frame_property_select[current_frame])

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                input_esc = True
            elif textinputpopup[0] == "text_input":
                input_box.userinput(event, keypress)

    if pygame.mouse.get_pressed()[0]:  # Hold left click
        mouse_leftdown = True
    elif pygame.mouse.get_pressed()[1]:  # Hold left click
        mouse_wheeldown = True
    elif pygame.mouse.get_pressed()[2]:  # Hold left click
        mouse_rightdown = True

    if inputui not in ui:
        if keypress is not None and keypress_delay < 0.1:
            if keypress[pygame.K_LCTRL] or keypress[pygame.K_RCTRL]:
                if keypress[pygame.K_c]:  # copy frame
                    copy_press = True
                elif keypress[pygame.K_v]:  # paste frame
                    paste_press = True
                elif keypress[pygame.K_z]:  # undo change
                    keypress_delay = 0.1
                    undo_press = True
                elif keypress[pygame.K_y]:  # redo change
                    keypress_delay = 0.1
                    redo_press = True
            elif keypress[pygame.K_LALT] or keypress[pygame.K_RALT]:
                if keypress[pygame.K_c]:  # copy part
                    part_copy_press = True
                elif keypress[pygame.K_v]:  # paste part
                    part_paste_press = True
            elif keypress[pygame.K_LSHIFT] or keypress[pygame.K_RSHIFT]:
                shift_press = True
            elif keypress[pygame.K_w]:
                skeleton.edit_part(mouse_pos, "movew")
            elif keypress[pygame.K_s]:
                skeleton.edit_part(mouse_pos, "moves")
            elif keypress[pygame.K_a]:
                skeleton.edit_part(mouse_pos, "movea")
            elif keypress[pygame.K_d]:
                skeleton.edit_part(mouse_pos, "moved")
            elif keypress[pygame.K_q]:
                skeleton.edit_part(mouse_pos, "tiltq")
            elif keypress[pygame.K_e]:
                skeleton.edit_part(mouse_pos, "tilte")
            elif keypress[pygame.K_DELETE]:
                keypress_delay = 0.1
                if skeleton.part_selected != []:
                    skeleton.edit_part(mouse_pos, "delete")
            elif keypress[pygame.K_PAGEUP]:
                keypress_delay = 0.1
                if skeleton.part_selected != []:
                    skeleton.edit_part(mouse_pos, "layerup")
            elif keypress[pygame.K_PAGEDOWN]:
                keypress_delay = 0.1
                if skeleton.part_selected != []:
                    skeleton.edit_part(mouse_pos, "layerdown")

        if mousetimer != 0:  # player click mouse once before
            mousetimer += uidt  # increase timer for mouse click using real time
            if mousetimer >= 0.3:  # time pass 0.3 second no longer count as double click
                mousetimer = 0

        if keypress_delay != 0:  # player click mouse once before
            keypress_delay += uidt  # increase timer for mouse click using real time
            if keypress_delay >= 0.3:  # time pass 0.3 second no longer count as double click
                keypress_delay = 0

        if mouse_up:
            if popup_listbox in ui:
                if popup_listbox.rect.collidepoint(mouse_pos):
                    popup_click = True
                    for index, name in enumerate(popup_namegroup):  # change leader with the new selected one
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
                                if "p1" in popup_listbox.action:
                                    p1_eye_selector.change_name("P1 Eye: " + name.name)
                                elif "p2" in popup_listbox.action:
                                    p2_eye_selector.change_name("P2 Eye: " + name.name)
                                skeleton.read_animation(animation_name)
                                reload_animation(anim, skeleton)
                            elif "mouth" in popup_listbox.action:
                                skeleton.edit_part(mouse_pos, popup_listbox.action[0:3] + "mouth_" + name.name)
                                if "p1" in popup_listbox.action:
                                    p1_mouth_selector.change_name("P1 Mouth: " + name.name)
                                elif "p2" in popup_listbox.action:
                                    p2_mouth_selector.change_name("P2 Mouth: " + name.name)
                                skeleton.read_animation(animation_name)
                                reload_animation(anim, skeleton)
                            elif popup_listbox.action == "animation_select":
                                if animation_name != name.name:
                                    current_frame = 0
                                    anim.show_frame = current_frame
                                    anim_prop_listbox.namelist = anim_property_list + ["Custom"]
                                    anim_property_select = []
                                    frame_prop_listbox.namelist = [frame_property_list + ["Custom"] for _ in range(10)]
                                    frame_property_select = [[] for _ in range(10)]
                                    current_anim_row = 0
                                    current_frame_row = 0
                                    skeleton.read_animation(name.name)
                                    animation_name = name.name
                                    animation_selector.change_name(animation_name)
                                    reload_animation(anim, skeleton)
                                    setuplist(menu.NameList, current_anim_row, anim_prop_listbox.namelist, anim_prop_namegroup,
                                              anim_prop_listbox, ui, layer=9, oldlist=anim_property_select)
                                    setuplist(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
                                              frame_prop_listbox, ui, layer=9, oldlist=frame_property_select[current_frame])
                                    anim_prop_listscroll.changeimage(newrow=0, logsize=len(anim_prop_listbox.namelist))
                                    frame_prop_listscroll.changeimage(newrow=0, logsize=len(frame_prop_listbox.namelist[current_frame]))
                            elif popup_listbox.action == "animation_side":
                                direction_button.change_text(name.name)
                                current_frame = 0
                                anim.show_frame = current_frame
                                skeleton.side = direction_list.index(name.name)
                                skeleton.read_animation(animation_name, newsize=False)
                                reload_animation(anim, skeleton)
                            for thisname in popup_namegroup:  # remove name list
                                thisname.kill()
                                del thisname
                            ui.remove(popup_listbox, popup_listscroll)
                            currentpopuprow = 0  # reset row
                elif popup_listscroll.rect.collidepoint(mouse_pos):  # scrolling on list
                    popup_click = True
                    newrow = popup_listscroll.update(mouse_pos, mouse_up)  # update the scroller and get new current subsection
                    if newrow is not None:
                        currentpopuprow = newrow
                        setuplist(menu.NameList, currentpopuprow, popup_listbox.namelist, popup_namegroup,
                                  popup_listbox, ui, layer=19)
                else:  # click other stuffs
                    for thisname in popup_namegroup:  # remove name list
                        thisname.kill()
                        del thisname
                    ui.remove(popup_listbox, popup_listscroll)

            if popup_click is False:
                if play_animation_button.rect.collidepoint(mouse_pos):
                    if play_animation_button.current_option == 0:
                        play_animation_button.change_option(1)  # start playing animation
                        play_animation = True
                    else:
                        play_animation_button.change_option(0)  # stop animation
                        play_animation = False
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
                    newrow = anim_prop_listscroll.update(mouse_pos, mouse_up)  # update the scroller and get new current subsection
                    if newrow is not None:
                        current_anim_row = newrow
                        setuplist(menu.NameList, current_anim_row, anim_prop_listbox.namelist, anim_prop_namegroup,
                                  anim_prop_listbox, ui, layer=9, oldlist=anim_property_list)
                elif frame_prop_listscroll.rect.collidepoint(mouse_pos):  # scrolling on list
                    newrow = frame_prop_listscroll.update(mouse_pos, mouse_up)  # update the scroller and get new current subsection
                    if newrow is not None:
                        current_frame_row = newrow
                        setuplist(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
                                  frame_prop_listbox, ui, layer=9, oldlist=frame_property_select[current_frame])
                elif anim_prop_listbox.rect.collidepoint(mouse_pos):
                    for index, name in enumerate(anim_prop_namegroup):  # change leader with the new selected one
                        if name.rect.collidepoint(mouse_pos):
                            if name.name == "Custom":
                                textinputpopup = ("text_input", "new_anim_prop")
                                inputui.changeinstruction("Custom Anim Prop:")
                                ui.add(inputui_pop)
                            else:
                                name.select()
                                if name.selected:
                                    anim_property_select.append(name.name)
                                else:
                                    anim_property_select.remove(name.name)
                                for frame in skeleton.frame_list:
                                    frame["animation_property"] = anim_property_select
                elif frame_prop_listbox.rect.collidepoint(mouse_pos):
                    for index, name in enumerate(frame_prop_namegroup):  # change leader with the new selected one
                        if name.rect.collidepoint(mouse_pos):
                            if name.name == "Custom":
                                textinputpopup = ("text_input", "new_frame_prop")
                                inputui.changeinstruction("Custom Frame Prop:")
                                ui.add(inputui_pop)
                            elif "effect_" in name.name:
                                if (name.name[-1] == "_" or name.name[-1].isdigit()):  # effect that need number value
                                    if name.selected is False:
                                        textinputpopup = ("text_input", "frame_prop_num_" + name.name)
                                        inputui.changeinstruction("Input Number Value:")
                                        ui.add(inputui_pop)
                                elif name.selected is False:  # effect that no need input
                                    frame_property_select[current_frame].append(name.name)
                                    setuplist(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
                                              frame_prop_listbox, ui, layer=9, oldlist=frame_property_select[current_frame])
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
            if popup_click is False:
                if mouse_up:
                    if clear_button.rect.collidepoint(mouse_pos):
                        skeleton.edit_part(mouse_pos, "clear")

                    elif default_button.rect.collidepoint(mouse_pos):
                        skeleton.edit_part(mouse_pos, "default")

                    elif copy_button.rect.collidepoint(mouse_pos):
                        copy_press = True

                    elif paste_button.rect.collidepoint(mouse_pos):
                        paste_press = True

                    elif part_copy_button.rect.collidepoint(mouse_pos):
                        part_copy_press = True

                    elif part_paste_button.rect.collidepoint(mouse_pos):
                        part_paste_press = True

                    elif p1_all_button.rect.collidepoint(mouse_pos):
                        if shift_press is False:
                            skeleton.part_selected = []
                        for index, part in enumerate(list(skeleton.rect_part_list.keys())):
                            if "p1" in part:
                                skeleton.click_part(mouse_pos, True, part)
                        for index, helper in enumerate(helperlist):
                            helper.select(mouse_pos, shift_press)
                            for part in skeleton.part_selected:
                                if list(skeleton.rect_part_list.keys())[part] in helper.rect_part_list:
                                    helper.select(mouse_pos, True, list(skeleton.rect_part_list.keys())[part])
                                else:
                                    helper.select(None, shift_press)

                    elif p2_all_button.rect.collidepoint(mouse_pos):
                        if shift_press is False:
                            skeleton.part_selected = []
                        for part in list(skeleton.rect_part_list.keys()):
                            if "p2" in part:
                                skeleton.click_part(mouse_pos, True, part)
                        for index, helper in enumerate(helperlist):
                            helper.select(mouse_pos, shift_press)
                            for part in skeleton.part_selected:
                                if list(skeleton.rect_part_list.keys())[part] in helper.rect_part_list:
                                    helper.select(mouse_pos, True, list(skeleton.rect_part_list.keys())[part])
                                else:
                                    helper.select(None, shift_press)

                    elif all_button.rect.collidepoint(mouse_pos):
                        for part in list(skeleton.rect_part_list.keys()):
                            skeleton.click_part(mouse_pos, True, part)
                        for index, helper in enumerate(helperlist):
                            for part in skeleton.part_selected:
                                if list(skeleton.rect_part_list.keys())[part] in helper.rect_part_list:
                                    helper.select(mouse_pos, True, list(skeleton.rect_part_list.keys())[part])

                    elif activate_button.rect.collidepoint(mouse_pos):
                        for strip_index, strip in enumerate(filmstrips):
                            if strip_index == current_frame:
                                if strip.activate == False:
                                    strip.activate = True
                                    deactivate_list[strip_index] = False
                                    activate_button.change_option(0)
                                else:
                                    strip.activate = False
                                    deactivate_list[strip_index] = True
                                    activate_button.change_option(1)
                                break

                    elif undo_button.rect.collidepoint(mouse_pos):
                        undo_press = True

                    elif redo_button.rect.collidepoint(mouse_pos):
                        redo_press = True

                    elif export_button.rect.collidepoint(mouse_pos):
                        for index, frame in enumerate(anim.frames):
                            pygame.image.save(frame, animation_name + "_" + str(index) + ".png")

                    elif flip_hori_button.rect.collidepoint(mouse_pos):
                        skeleton.edit_part(mouse_pos, "flip1")

                    elif flip_vert_button.rect.collidepoint(mouse_pos):
                        skeleton.edit_part(mouse_pos, "flip2")

                    elif reset_button.rect.collidepoint(mouse_pos):
                        skeleton.edit_part(mouse_pos, "reset")

                    elif direction_button.rect.collidepoint(mouse_pos):
                        popuplist_newopen("animation_side", direction_button.rect.bottomleft, direction_list, "top")

                    elif direction_part_button.rect.collidepoint(mouse_pos):
                        if race_part_button.text != "":
                            popuplist_newopen("part_side", direction_part_button.rect.topleft, direction_list, "bottom")

                    elif part_selector.rect.collidepoint(mouse_pos):
                        if direction_part_button.text != "" and race_part_button.text != "":
                            currentpart = list(skeleton.animation_part_list[current_frame].keys())[skeleton.part_selected[-1]]
                            try:
                                if "p1" in currentpart or "p2" in currentpart:
                                    selectpart = currentpart[3:]
                                    if selectpart[0:2] == "r_" or selectpart[0:2] == "l_":
                                        selectpart = selectpart[2:]
                                    part_list = list(gen_body_sprite_pool[race_part_button.text][direction_part_button.text][selectpart].keys())
                                elif "effect" in currentpart:
                                    part_list = list(effect_sprite_pool[race_part_button.text][direction_part_button.text].keys())
                            except KeyError:  # look at weapon next
                                selectpart = race_part_button.text
                                part_list = list(gen_weapon_sprite_pool[selectpart][direction_part_button.text].keys())
                            popuplist_newopen("part_select", part_selector.rect.topleft, part_list, "bottom")

                    elif p1_eye_selector.rect.collidepoint(mouse_pos):
                        part_list = ["Any"] + list(gen_body_sprite_pool[skeleton.p1_race][direction_list[skeleton.side]]["eye"].keys())
                        popuplist_newopen("p1_eye_select", p1_eye_selector.rect.topleft, part_list, "bottom")

                    elif p1_mouth_selector.rect.collidepoint(mouse_pos):
                        part_list = ["Any"] + list(gen_body_sprite_pool[skeleton.p1_race][direction_list[skeleton.side]]["mouth"].keys())
                        popuplist_newopen("p1_mouth_select", p1_mouth_selector.rect.topleft, part_list, "bottom")

                    elif p2_eye_selector.rect.collidepoint(mouse_pos):
                        part_list = ["Any"] + list(gen_body_sprite_pool[skeleton.p2_race][direction_list[skeleton.side]]["eye"].keys())
                        popuplist_newopen("p2_eye_select", (p2_eye_selector.rect.topleft[0] - (45 * screen_scale[0]), p2_eye_selector.rect.topleft[1]), part_list, "bottom")

                    elif p2_mouth_selector.rect.collidepoint(mouse_pos):
                        part_list = ["Any"] + list(gen_body_sprite_pool[skeleton.p2_race][direction_list[skeleton.side]]["mouth"].keys())
                        popuplist_newopen("p2_mouth_select", (p2_mouth_selector.rect.topleft[0] - (45 * screen_scale[0]), p2_mouth_selector.rect.topleft[1]), part_list, "bottom")

                    elif race_part_button.rect.collidepoint(mouse_pos):
                        if skeleton.part_selected != []:
                            currentpart = list(skeleton.rect_part_list.keys())[skeleton.part_selected[-1]]
                            if "weapon" in currentpart:
                                part_list = list(gen_weapon_sprite_pool)
                            elif "effect" in currentpart:
                                part_list = list(effect_sprite_pool)
                            else:
                                part_list = list(gen_body_sprite_pool.keys())
                            popuplist_newopen("race_select", race_part_button.rect.topleft, part_list, "bottom")

                    elif new_button.rect.collidepoint(mouse_pos):
                        textinputpopup = ("text_input", "new_animation")
                        inputui.changeinstruction("New Animation Name:")
                        ui.add(inputui_pop)

                    elif delete_button.rect.collidepoint(mouse_pos):
                        textinputpopup = ("confirm_input", "del_animation")
                        inputui.changeinstruction("Delete This Animation?")
                        ui.add(inputui_pop)

                    elif size_button.rect.collidepoint(mouse_pos):
                        textinputpopup = ("text_input", "change_size")
                        inputui.changeinstruction("Input Size Number:")
                        ui.add(inputui_pop)

                    elif animation_selector.rect.collidepoint(mouse_pos):
                        popuplist_newopen("animation_select", animation_selector.rect.bottomleft,
                                          [item for item in generic_animation_pool[direction]], "top")

                    else:  # click on other stuff
                        for strip_index, strip in enumerate(filmstrips):
                            if strip.rect.collidepoint(mouse_pos) and current_frame != strip_index:
                                current_frame = strip_index
                                anim.show_frame = current_frame
                                skeleton.part_selected = []
                                skeleton.edit_part(mouse_pos, "change")
                                current_frame_row = 0
                                setuplist(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
                                          frame_prop_listbox, ui, layer=9, oldlist=frame_property_select[current_frame])  # change frame property list
                                for index, helper in enumerate(helperlist):
                                    helper.select(None, False)
                                if strip.activate:
                                    activate_button.change_option(0)
                                else:
                                    activate_button.change_option(1)
                                break

                        helper_click = False
                        for index, helper in enumerate(helperlist):
                            if helper.rect.collidepoint(mouse_pos):
                                helper_click = helper
                                break
                        if helper_click is not False:  # to avoid removing selected part when click other stuff
                            mouse_pos = pygame.Vector2((mouse_pos[0] - helper_click.rect.topleft[0]) / screen_size[0] * 1000,
                                                       (mouse_pos[1] - helper_click.rect.topleft[1]) / screen_size[1] * 1000)
                            helper_click.select(mouse_pos, shift_press)
                            if shift_press is False:  # remove selected part in other helpers
                                skeleton.part_selected = []  # clear old list first
                                for index, helper in enumerate(helperlist):
                                    if helper != helper_click:
                                        helper.select(None, shift_press)
                            if helper_click.part_selected != []:
                                for part in helper_click.part_selected:
                                    skeleton.click_part(mouse_pos, True, part)

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
                        copy_part = {item: copy_part[item] for index, item in enumerate(copy_part.keys()) if index in skeleton.part_selected}
                        copy_animation = {item: copy_animation[item] for index, item in enumerate(copy_animation.keys()) if index in skeleton.part_selected}
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

                if showroom.rect.collidepoint(mouse_pos):
                    new_mouse_pos = pygame.Vector2((mouse_pos[0] - showroom.rect.topleft[0]) / screen_size[0] * 500 * skeleton.size,
                                               (mouse_pos[1] - showroom.rect.topleft[1]) / screen_size[1] * 500 * skeleton.size)
                    if mouse_up:
                        skeleton.click_part(new_mouse_pos, shift_press)
                        for index, helper in enumerate(helperlist):
                            if shift_press is False:  # reset all first if no shift select
                                helper.select(mouse_pos, shift_press)  # use old mouse pos for helper
                            if skeleton.part_selected != []:
                                for part in skeleton.part_selected:
                                    if list(skeleton.rect_part_list.keys())[part] in helper.rect_part_list:
                                        helper.select(mouse_pos, shift_press, list(skeleton.rect_part_list.keys())[part])
                                    else:
                                        helper.select(None, shift_press)
                            else:
                                helper.select(None, shift_press)
                    if mouse_wheel or mouse_wheeldown:
                        skeleton.edit_part(new_mouse_pos, "rotate")
                    elif mouse_right or mouse_rightdown:
                        if keypress_delay == 0:
                            skeleton.edit_part(new_mouse_pos, "place")
                            keypress_delay = 0.1

            if skeleton.part_selected != []:
                part = skeleton.part_selected[-1]
                if skeleton.sprite_part is not None and \
                        list(skeleton.rect_part_list.keys())[part] in list(skeleton.sprite_part.keys()):
                    nametext = skeleton.part_name_list[current_frame][list(skeleton.rect_part_list.keys())[part]]
                    if nametext is None:
                        nametext = ["", "", ""]
                    race_part_button.change_text(nametext[0])
                    direction_part_button.change_text(nametext[1])
                    part_selector.change_name(nametext[2])
                else:
                    race_part_button.change_text("")
                    direction_part_button.change_text("")
                    part_selector.change_name("")
            else:
                race_part_button.change_text("")
                direction_part_button.change_text("")
                part_selector.change_name("")
    else:
        dt = 0
        if input_ok_button.event:
            input_ok_button.event = False

            if textinputpopup[1] == "new_animation":
                animation_name = input_box.text
                animation_selector.change_name(animation_name)
                current_frame = 0
                skeleton.edit_part(mouse_pos, "new")

            # elif textinputpopup[1] == "del_animation":
            #     if animation_name !=
            elif textinputpopup[1] == "new_anim_prop":
                anim_prop_listbox.namelist.insert(-1, input_box.text)
                anim_property_select.append(input_box.text)
                setuplist(menu.NameList, current_anim_row, anim_prop_listbox.namelist, anim_prop_namegroup,
                          anim_prop_listbox, ui, layer=9, oldlist=anim_property_select)
                for frame in skeleton.frame_list:
                    frame["animation_property"] = anim_property_select
            elif textinputpopup[1] == "new_frame_prop":
                frame_prop_listbox.namelist[current_frame].insert(-1, input_box.text)
                frame_property_select[current_frame].append(input_box.text)
                setuplist(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
                          frame_prop_listbox, ui, layer=9, oldlist=frame_property_select[current_frame])
            elif "frame_prop_num" in textinputpopup[1] and input_box.text.isdigit():
                for name in frame_prop_listbox.namelist[current_frame]:
                    if name in (textinputpopup[1]):
                        index = frame_prop_listbox.namelist[current_frame].index(name)
                        frame_prop_listbox.namelist[current_frame][index] = name[0:name.rfind("_")+1] + input_box.text
                        frame_property_select[current_frame].append(name[0:name.rfind("_")+1] + input_box.text)
                        setuplist(menu.NameList, current_frame_row, frame_prop_listbox.namelist[current_frame], frame_prop_namegroup,
                                  frame_prop_listbox, ui, layer=9, oldlist=frame_property_select[current_frame])
                        reload_animation(anim, skeleton)
                        break
            elif textinputpopup[1] == "change_size" and input_box.text.isdigit():
                skeleton.frame_list[0]["size"] = int(input_box.text)
                skeleton.read_animation(animation_name, old=True)
                reload_animation(anim, skeleton)
            elif textinputpopup[1] == "quit":
                pygame.time.wait(1000)
                if pygame.mixer:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.unload()
                pygame.quit()

            input_box.textstart("")
            textinputpopup = (None, None)
            ui.remove(*inputui_pop)

        elif input_cancel_button.event or input_esc:
            input_cancel_button.event = False
            input_box.textstart("")
            textinputpopup = (None, None)
            ui.remove(*inputui_pop, *confirmui_pop)

    ui.update(mouse_pos, mouse_up, mouse_leftdown, "any")
    anim.play(showroom.image, (0, 0), deactivate_list)
    for strip_index, strip in enumerate(filmstrips):
        if strip_index == current_frame:
            strip.selected(True)
            break

    pen.fill((0, 0, 0))
    ui.draw(pen)

    pygame.display.update()
    clock.tick(60)
