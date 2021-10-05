import csv
import math
import os
import random
import re
import time
from pathlib import Path

import pygame
from PIL import Image, ImageOps
from gamescript import commonscript, readstat
from gamescript.arcade import longscript

rotationxy = commonscript.rotationxy
load_image = commonscript.load_image
stat_convert = readstat.stat_convert
setrotate = longscript.setrotate

main_dir = os.path.split(os.path.abspath(__file__))[0]

default_sprite_size = (150, 150)

screen_size = (1000, 1000)

pygame.init()
pen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Animation Maker")  # set the game name on program border/tab
pygame.mouse.set_visible(True)  # set mouse as visible


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


generic_animation_pool = []
for direction in ["front", "side", "back", "cornerup", "cornerdown"]:
    with open(os.path.join(main_dir, "data", "arcade", "animation", "generic", direction, "animation.csv"), encoding="utf-8", mode="r") as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        rd = [row for row in rd]
        part_name_header = rd[0]
        list_column = ["p1_head", "p1_body", "p1_r_arm_up", "p1_r_arm_low", "p1_r_hand", "p1_l_arm_up",
                       "p1_l_arm_low", "p1_l_hand", "p1_r_leg", "p1_r_foot", "p1_l_leg", "p1_l_foot",
                       "p1_main_weapon", "p1_sub_weapon", "p2_head", "p2_body", "p2_r_arm_up", "p2_r_arm_low", "p2_r_hand",
                       "p2_l_arm_up", "p2_l_arm_low", "p2_l_hand", "p2_r_leg", "p2_r_foot", "p2_l_leg",
                       "p2_l_foot", "p2_main_weapon", "p2_sub_weapon", "effect_1", "effect_2", "dmg_effect_1", "dmg_effect_2"]  # value in list only
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
        part_name_header = [item for item in part_name_header if
                            "p2" not in item and "weapon" not in item and item not in ("effect", "property")]  # TODO remove later when have p2
    unitfile.close()

skel_joint_list = []
for direction in ["front", "side", "back", "cornerup", "cornerdown"]:
    with open(os.path.join(main_dir, "data", "arcade", "sprite", "generic", "human", direction, "skeleton_link.csv"), encoding="utf-8",
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

with open(os.path.join(main_dir, "data", "arcade", "sprite", "generic", "skin_colour_rgb.csv"), encoding="utf-8",
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

# print(skin_colour_list)

gen_body_sprite_pool = {}
for direction in ["front", "side", "back", "cornerup", "cornerdown"]:
    gen_body_sprite_pool[direction] = {}
    partfolder = Path(os.path.join(main_dir, "data", "arcade", "sprite", "generic", "human", direction))
    subdirectories = [str(x).split("data\\")[1].split("\\") for x in partfolder.iterdir() if x.is_dir()]
    for folder in subdirectories:
        imgs = load_textures(main_dir, folder)
        gen_body_sprite_pool[direction][folder[-1]] = imgs


# print(gen_body_sprite_pool)

class Showroom(pygame.sprite.Sprite):
    def __init__(self, size):
        """White space for showing off sprite and animation"""
        pygame.sprite.Sprite.__init__(self)
        self.size = (int(size[0]), int(size[1]))
        self.image = pygame.Surface(self.size)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(screen_size[0] / 2, screen_size[1] / 2))
        self.grid = True

    def update(self):
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

    def update(self):
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
        self.font = pygame.font.SysFont("helvetica", int(fontsize * screen_size[1] / 1000))
        self.image = image.copy()
        self.text = text
        textsurface = self.font.render(str(text), 1, (0, 0, 0))
        textrect = textsurface.get_rect(center=(int(self.image.get_width() / 2), int(self.image.get_height() / 2)))
        self.image.blit(textsurface, textrect)
        self.rect = self.image.get_rect(center=pos)


class SwitchButton(pygame.sprite.Sprite):
    """Button that switch text/option"""

    def __init__(self, text_list, image, pos, fontsize=20):
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(fontsize * screen_size[1] / 1000))
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
    def __init__(self, pos):
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect(center=pos)


class SideChoose:
    def __init__(self):
        pass


class Skeleton:
    def __init__(self):
        self.animation_list = []
        self.animation_part_list = []
        self.side = 1  # 0 = front, 1 = side, 2 = back, 3 = cornerup, 4 = cornerdown

        #  select face use side direction to search for part name
        self.p1_eyebrow = list(gen_body_sprite_pool["side"]["eyebrow"].keys())[random.randint(0, len(gen_body_sprite_pool["side"]["eyebrow"]) - 1)]
        self.p1_eye = list(gen_body_sprite_pool["side"]["eye"].keys())[random.randint(0, len(gen_body_sprite_pool["side"]["eye"]) - 1)]
        self.p1_mouth = list(gen_body_sprite_pool["side"]["mouth"].keys())[random.randint(0, len(gen_body_sprite_pool["side"]["mouth"]) - 1)]

        self.rect_part_list = {"p1_head": None, "p1_body": None, "p1_r_arm_up": None, "p1_r_arm_low": None, "self.p1_r_hand": None,
                               "p1_l_arm_up": None, "p1_l_arm_low": None, "p1_l_hand": None, "p1_r_leg": None, "p1_r_foot": None,
                               "p1_l_leg": None, "p1_l_foot": None, "p1_main_weapon": None, "p1_sub_weapon": None,
                               "p2_head": None, "p2_body": None, "p2_r_arm_up": None, "p2_r_arm_low": None,
                               "p2_r_hand": None, "p2_l_arm_up": None, "p2_l_arm_low": None, "p2_l_hand": None,
                               "p2_r_leg": None, "p2_r_foot": None, "p2_l_leg": None, "p2_l_foot": None,
                               "p2_main_weapon": None, "p2_sub_weapon": None}
        self.part_selected = None
        self.read_animation("Default")
        self.default = {key: value[:] for key, value in self.sprite_part.items()}

    def read_animation(self, name):
        #  sprite animation generation
        animation_list = [generic_animation_pool[self.side][name]]
        self.animation_part_list = []
        for animation in animation_list:
            for pose in animation:
                # TODO change later when have p2
                link_list = {}
                bodypart_list = []
                for part in pose:
                    if pose[part] != [0] and part != "property":
                        link_list[part] = self.make_link_pos(pose, part)
                        bodypart_list.append([pose[part][0], pose[part][1]])

                main_joint_pos_list = self.generate_body(bodypart_list)

                self.sprite_part = {}
                for part in part_name_header:
                    if pose[part] != [0] and "weapon" not in part:
                        self.sprite_part[part] = [self.sprite_image[part], main_joint_pos_list[part], link_list[part], pose[part][4],
                                                  pose[part][5], pose[part][-1]]

                pose_layer_list = {k: v[-1] for k, v in self.sprite_part.items()}
                pose_layer_list = dict(sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))

                self.animation_part_list.append(self.sprite_part)
                image = self.create_animation_film(pose_layer_list)
                self.animation_list.append(image)

    def create_animation_film(self, pose_layer_list, empty=False):
        image = pygame.Surface((150, 150), pygame.SRCALPHA)  # default size will scale down later
        for key, value in self.rect_part_list.items():  # reset rect list
            self.rect_part_list[key] = None
        if empty is False:
            for index, layer in enumerate(pose_layer_list):
                if "weapon" not in layer:
                    part = self.sprite_part[layer]
                image = self.part_to_sprite(image, part[0], list(self.sprite_part.keys()).index(layer),
                                            part[1], part[2], part[3], part[4])
        return image

    def generate_body(self, bodypart_list):
        skin = list(skin_colour_list.keys())[random.randint(0, len(skin_colour_list) - 1)]
        skin_colour = skin_colour_list[skin]
        hair_colour = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]

        face = [gen_body_sprite_pool[bodypart_list[0][0]]["head"][bodypart_list[0][1]].copy(),
                gen_body_sprite_pool[bodypart_list[0][0]]["eye"][self.p1_eye].copy(),
                gen_body_sprite_pool[bodypart_list[0][0]]["eyebrow"][self.p1_eyebrow].copy(),
                gen_body_sprite_pool[bodypart_list[0][0]]["mouth"][self.p1_mouth].copy()]
        # if skin != "white":
        #     face[0] = self.apply_colour(face[0], skin_colour)
        # face[1] = self.apply_colour(face[1], [random.randint(0,255), random.randint(0,255), random.randint(0,255)])
        face[2] = self.apply_colour(face[2], hair_colour)
        face[3] = self.apply_colour(face[3], hair_colour)

        for index, item in enumerate(face):
            if index > 0:
                if index == 3:
                    head_sprite_surface = pygame.Surface((item.get_width(), item.get_height()), pygame.SRCALPHA)
                    head_rect = face[0].get_rect(midtop=(head_sprite_surface.get_width() / 2, 0))
                    head_sprite_surface.blit(face[0], head_rect)
                    head_rect = item.get_rect(midtop=(head_sprite_surface.get_width() / 2, 0))
                    head_sprite_surface.blit(item, head_rect)
                else:
                    rect = item.get_rect(topleft=(0, 0))
                    face[0].blit(item, rect)

        self.sprite_image = {"p1_head": head_sprite_surface,
                             "p1_body": gen_body_sprite_pool[bodypart_list[1][0]]["body"][bodypart_list[1][1]].copy(),
                             "p1_r_arm_up": gen_body_sprite_pool[bodypart_list[2][0]]["arm_up"][bodypart_list[2][1]].copy(),
                             "p1_r_arm_low": gen_body_sprite_pool[bodypart_list[3][0]]["arm_low"][bodypart_list[3][1]].copy(),
                             "p1_r_hand": gen_body_sprite_pool[bodypart_list[4][0]]["hand"][bodypart_list[4][1]].copy(),
                             "p1_l_arm_up": gen_body_sprite_pool[bodypart_list[5][0]]["arm_up"][bodypart_list[5][1]].copy(),
                             "p1_l_arm_low": gen_body_sprite_pool[bodypart_list[6][0]]["arm_low"][bodypart_list[6][1]].copy(),
                             "p1_l_hand": gen_body_sprite_pool[bodypart_list[7][0]]["hand"][bodypart_list[7][1]].copy(),
                             "p1_r_leg": gen_body_sprite_pool[bodypart_list[8][0]]["leg"][bodypart_list[8][1]].copy(),
                             "p1_r_foot": gen_body_sprite_pool[bodypart_list[9][0]]["foot"][bodypart_list[9][1]].copy(),
                             "p1_l_leg": gen_body_sprite_pool[bodypart_list[10][0]]["leg"][bodypart_list[10][1]].copy(),
                             "p1_l_foot": gen_body_sprite_pool[bodypart_list[11][0]]["foot"][bodypart_list[11][1]].copy()}
        # if skin != "white":
        #     for part in list(self.sprite_image.keys())[1:]:
        #         self.sprite_image[part] = self.apply_colour(self.sprite_image[part], skin_colour)

        main_joint_pos_list = {}
        for part_index, part in enumerate(part_name_header):
            for part_link in skel_joint_list[self.side]:
                if part_link in part:  # match part name, p1_head = head in part link #TODO change this when have p2
                    main_joint_pos_list[part] = list(skel_joint_list[self.side][part_link][0].values())[0]
                    break
        return main_joint_pos_list

    def click_part(self, mouse_pos):
        self.part_selected = None
        for index, rect in enumerate(self.rect_part_list):
            thisrect = self.rect_part_list[rect]
            if thisrect is not None and thisrect.collidepoint(mouse_pos):
                self.part_selected = index
                break

    def edit_part(self, mouse_pos, current_frame, edit_type):
        if edit_type == "move":
            if self.part_selected is not None:
                part_index = list(self.animation_part_list[current_frame].keys())[self.part_selected]
                self.animation_part_list[current_frame][part_index][2] = mouse_pos

        elif edit_type == "rotate":
            if self.part_selected is not None:
                part_index = list(self.animation_part_list[current_frame].keys())[self.part_selected]
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

        elif "flip" in edit_type:
            if self.part_selected is not None:
                part_index = list(self.animation_part_list[current_frame].keys())[self.part_selected]
                self.animation_part_list[current_frame][part_index][4] = int(edit_type[-1])

        elif edit_type == "default":  # reset to default
            self.animation_part_list[current_frame] = {key: value[:] for key, value in self.default.items()}

        elif edit_type == "clear":  # clear whole strip
            self.animation_part_list[current_frame] = {}
            self.part_selected = None

        elif edit_type == "change":  # change strip
            self.part_selected = None
            if current_frame > len(self.animation_part_list) - 1:
                while current_frame > len(self.animation_part_list) - 1:
                    self.animation_part_list.append({})
                    self.animation_list.append(None)
                    surface = self.create_animation_film(None, empty=True)
                    self.animation_list[-1] = surface

        if self.animation_part_list[current_frame] != {}:
            self.sprite_part = self.animation_part_list[current_frame]
            pose_layer_list = {k: v[-1] for k, v in self.sprite_part.items()}
            pose_layer_list = dict(sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))
            surface = self.create_animation_film(pose_layer_list)
        else:
            surface = self.create_animation_film(None, empty=True)
        self.animation_list[current_frame] = surface

    def apply_colour(self, surface, colour):
        """Colorise body part sprite"""
        size = (surface.get_width(), surface.get_height())
        data = pygame.image.tostring(surface, "RGBA")  # convert image to string data for filtering effect
        surface = Image.frombytes("RGBA", size, data)  # use PIL to get image data
        alpha = surface.split()[-1]  # save alpha
        surface = surface.convert("L")  # convert to grey scale for colourise
        max_colour = 255  # - (colour[0] + colour[1] + colour[2])
        mid_colour = [c - ((max_colour - c) / 2) for c in colour]
        surface = ImageOps.colorize(surface, black="black", mid=mid_colour, white=colour).convert("RGB")
        surface.putalpha(alpha)  # put back alpha
        surface = surface.tobytes()
        surface = pygame.image.fromstring(surface, size, "RGBA")  # convert image back to a pygame surface
        return surface

    def make_link_pos(self, pose, index):
        part_link = [pose[index][2], pose[index][3]]
        return part_link

    def part_to_sprite(self, surface, part, part_index, main_joint_pos, target, angle, flip):
        """Find body part's new center point from main_joint_pos with new angle, then create rotated part and blit to sprite"""
        part_rotated = part.copy()
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
        pos_different = main_joint_pos - center  # find distance between image center and connect point main_joint_pos
        new_center = target - pos_different  # find new center point
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
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos
        self.image_original = image.copy()

    def move(self, angle, pos):
        self.pos = pos
        self.image = self.image_original.copy()
        self.image = pygame.transform.rotate(self.image, angle)  # rotate part sprite
        self.rect = self.image.get_rect(center=pos)


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

    def play(self, surface, position, dt, noplay_list):
        if dt > 0:
            if time.time() - self.first_time >= self.speed_ms:
                self.show_frame += 1
                while self.show_frame < 10 and noplay_list[self.show_frame]:
                    self.show_frame += 1
                self.first_time = time.time()
            if self.show_frame > self.end_frame:
                self.show_frame = self.start_frame
        surface.blit(self.frames[int(self.show_frame)], position)


def reload_animation(animation):
    frames = [pygame.transform.smoothscale(thisimage, showroom.size) for thisimage in skeleton.animation_list]
    for frame_index in range(0, 10):
        try:
            filmstrip_list[frame_index].add_strip(frames[frame_index])
        except IndexError:
            filmstrip_list[frame_index].add_strip()
    animation.reload(frames)


# start animation maker
clock = pygame.time.Clock()

ui = pygame.sprite.LayeredUpdates()

skeleton = Skeleton()
image = pygame.transform.scale(load_image(main_dir, "film.png", ["animation_maker_ui"]),
                               (int(100 * screen_size[1] / 1000), int(100 * screen_size[1] / 1000)))
Filmstrip.image_original = image
filmstrips = pygame.sprite.Group()

Button.containers = ui
SwitchButton.containers = ui
Bodyhelper.containers = ui
Joint.containers = ui
Filmstrip.containers = ui, filmstrips

filmstrip_list = [Filmstrip((0, 50 * screen_size[1] / 500)), Filmstrip((image.get_width(), 50 * screen_size[1] / 500)),
                  Filmstrip((image.get_width() * 2, 50 * screen_size[1] / 500)), Filmstrip((image.get_width() * 3, 50 * screen_size[1] / 500)),
                  Filmstrip((image.get_width() * 4, 50 * screen_size[1] / 500)), Filmstrip((image.get_width() * 5, 50 * screen_size[1] / 500)),
                  Filmstrip((image.get_width() * 6, 50 * screen_size[1] / 500)), Filmstrip((image.get_width() * 7, 50 * screen_size[1] / 500)),
                  Filmstrip((image.get_width() * 8, 50 * screen_size[1] / 500)), Filmstrip((image.get_width() * 9, 50 * screen_size[1] / 500))]

filmstrips.add(*filmstrip_list)

# p1_body_helper = Bodyhelper()
# p2_body_helper = Bodyhelper()
# effect_helper = Bodyhelper()

image = load_image(main_dir, "button.png", ["animation_maker_ui"])
image = pygame.transform.scale(image, (int(image.get_width() * screen_size[1] / 1000),
                                       int(image.get_height() * screen_size[1] / 1000)))

new_button = Button("New", image, (image.get_width() / 2, image.get_height() / 2))
save_button = Button("Save", image, (image.get_width() * 2, image.get_height() / 2))
delete_button = Button("Delete", image, (image.get_width() * 10, image.get_height() / 2))

play_animation_button = SwitchButton(["Play", "Stop"], image,
                                     (screen_size[1] / 2, filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 2)))
copy_button = Button("Copy", image, (play_animation_button.pos[0] - play_animation_button.image.get_width(),
                                     filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 2)))
paste_button = Button("Paste", image, (play_animation_button.pos[0] + play_animation_button.image.get_width(),
                                       filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 2)))
default_button = Button("Default", image, (play_animation_button.pos[0] + play_animation_button.image.get_width() * 3,
                                           filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 2)))
clear_button = Button("Clear", image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 3,
                                       filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 2)))
activate_button = Button("Enable", image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 4,
                                       filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 2)))
deactivate_button = Button("Disable", image, (play_animation_button.pos[0] - play_animation_button.image.get_width() * 5,
                                       filmstrip_list[0].rect.midbottom[1] + (image.get_height() / 2)))

# flip_vert_button = Button("Flip Vert",image, (100,200))
# flip_hori_button = Button("Flip Hori",image, (100,200))
# reset_button = Button("Reset",image, (100,200))

# loop_button = SwitchButton(["Loop:Yes", "Loop:No"],image, (100,200))

showroom = Showroom((150 * screen_size[0] / 500, 150 * screen_size[1] / 500))

runtime = 0
mousetimer = 0
play_animation = False
current_frame = 0
copy_frame = None
deactivate_list = [False] * 10

skeleton.animation_list = []
skeleton.read_animation('Default')
anim = Animation(1000, True)
reload_animation(anim)

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
    del_press = False

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
            elif event.button == 4:  # Mouse scroll up
                mouse_scrollup = True
                rowchange = -1
            elif event.button == 5:  # Mouse scroll down
                mouse_scrolldown = True
                rowchange = 1

        # elif event.type == pygame.KEYDOWN:
        # #     if self.textinputpopup[0] == "text_input":  # event update to input box
        # #         self.input_box.userinput(event)
        # #     else:
        #     keypress = event.key
    if pygame.mouse.get_pressed()[0]:  # Hold left click
        mouse_leftdown = True
    elif pygame.mouse.get_pressed()[1]:  # Hold left click
        mouse_wheeldown = True
    elif pygame.mouse.get_pressed()[2]:  # Hold left click
        mouse_rightdown = True

    if keypress is not None and keypress[pygame.K_LCTRL]:
        if keypress[pygame.K_c]:  # copy frame
            copy_press = True
        elif keypress[pygame.K_v]:  # paste frame
            paste_press = True

    if mousetimer != 0:  # player click mouse once before
        mousetimer += uidt  # increase timer for mouse click using real time
        if mousetimer >= 0.3:  # time pass 0.3 second no longer count as double click
            mousetimer = 0

    if mouse_up:
        if play_animation_button.rect.collidepoint(mouse_pos):
            if play_animation_button.current_option == 0:  # start playing animation
                play_animation_button.change_option(1)
                play_animation = True
            else:  # stop animation
                play_animation_button.change_option(0)
                play_animation = False

    # change animation
    # skeleton.animation_list = []
    # skeleton.generate_animation('Default')
    # frames = [pygame.transform.smoothscale(image, showroom.size) for image in skeleton.animation_list]
    # for frame_index in range(0, 10):
    #     try:
    #         filmstrip_list[frame_index].add_strip(frames[frame_index])
    #     except IndexError:
    #         filmstrip_list[frame_index].add_strip()
    # anim = Animation(frames, 1000, True)

    showroom.update()
    ui.update()

    for strip_index, strip in enumerate(filmstrips):
        if strip_index == current_frame:
            strip.selected(True)
            break

    pen.fill((0, 0, 0))
    ui.draw(pen)

    if play_animation:
        current_frame = int(anim.show_frame)
    else:
        dt = 0
        if mouse_up and clear_button.rect.collidepoint(mouse_pos):
            skeleton.edit_part(mouse_pos, current_frame, "clear")
            reload_animation(anim)
        elif mouse_up and default_button.rect.collidepoint(mouse_pos):
            skeleton.edit_part(mouse_pos, current_frame, "default")
            reload_animation(anim)
        elif copy_press or (mouse_up and copy_button.rect.collidepoint(mouse_pos)):
            copy_frame = {key: value[:] for key, value in skeleton.animation_part_list[current_frame].items()}
        elif paste_press or (mouse_up and paste_button.rect.collidepoint(mouse_pos)):
            if copy_frame is not None:
                skeleton.animation_part_list[current_frame] = {key: value[:] for key, value in copy_frame.items()}
                skeleton.edit_part(mouse_pos, current_frame, "change")
                reload_animation(anim)
        elif mouse_up and activate_button.rect.collidepoint(mouse_pos):
            pass
            for strip_index, strip in enumerate(filmstrips):
                if strip_index == current_frame:
                    strip.activate = True
                    deactivate_list[strip_index] = False
                    break
        elif mouse_up and deactivate_button.rect.collidepoint(mouse_pos):
            for strip_index, strip in enumerate(filmstrips):
                if strip_index == current_frame:
                    strip.activate = False
                    deactivate_list[strip_index] = True
                    break
        elif mouse_up:
            for strip_index, strip in enumerate(filmstrips):
                if strip.rect.collidepoint(mouse_pos):
                    current_frame = strip_index
                    anim.show_frame = current_frame
                    skeleton.edit_part(mouse_pos, current_frame, "change")
                    reload_animation(anim)
                    break

        if showroom.rect.collidepoint(mouse_pos):
            mouse_pos = pygame.Vector2((mouse_pos[0] - showroom.rect.topleft[0]) / screen_size[0] * 500,
                                       (mouse_pos[1] - showroom.rect.topleft[1]) / screen_size[1] * 500)
            if mouse_up:
                skeleton.click_part(mouse_pos)
            if mouse_wheel or mouse_wheeldown:
                skeleton.edit_part(mouse_pos, current_frame, "rotate")
                reload_animation(anim)
            elif mouse_right or mouse_rightdown:
                skeleton.edit_part(mouse_pos, current_frame, "move")
                reload_animation(anim)

    anim.play(showroom.image, (0, 0), dt, deactivate_list)

    pen.blit(showroom.image, showroom.rect)
    pygame.display.update()
    clock.tick(60)
