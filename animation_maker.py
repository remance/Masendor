import csv
import os
import time
import math
import re
import random

from pathlib import Path
from PIL import Image, ImageOps

import pygame
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
pygame.mouse.set_visible(1)  # set mouse as visible

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

# for direction in ["front","side","back","cornerup","cornerdown"]:
with open(os.path.join(main_dir, "data", "arcade", "animation", "animation.csv"), encoding="utf-8", mode="r") as unitfile:
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
    generic_animation_pool = {}
    for row_index, row in enumerate(rd):
        if row_index > 0:
            key = row[0].split("/")[0]
            for n, i in enumerate(row):
                row = stat_convert(row, n, i, list_column=list_column)
            row = row[1:]
            if key in generic_animation_pool:
                generic_animation_pool[key].append({part_name_header[item_index] : item for item_index, item in enumerate(row)})
            else:
                generic_animation_pool[key] = [{part_name_header[item_index] : item for item_index, item in enumerate(row)}]

    part_name_header = [item for item in part_name_header if
                        "p2" not in item and "weapon" not in item and item not in ("effect", "property")]  # TODO remove later when have p2
unitfile.close()

# for direction in ["front","side","back","cornerup","cornerdown"]:
with open(os.path.join(main_dir, "data", "arcade", "sprite", "generic", "human", "side", "skeleton_link.csv"), encoding="utf-8",
          mode="r") as unitfile:
    rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
    rd = [row for row in rd]
    header = rd[0]
    list_column = ["Position"]  # value in list only
    list_column = [index for index, item in enumerate(header) if item in list_column]
    skel_joint_list = {}
    for row_index, row in enumerate(rd):
        if row_index > 0:
            for n, i in enumerate(row):
                row = stat_convert(row, n, i, list_column=list_column)
                key = row[0].split("/")[0]
            if key in skel_joint_list:
                skel_joint_list[key].append({row[1:][0] : pygame.Vector2(row[1:][1])})
            else:
                skel_joint_list[key] = [{row[1:][0] : pygame.Vector2(row[1:][1])}]
# print(skel_joint_list)

with open(os.path.join(main_dir, "data", "arcade", "sprite", "generic", "skin_colour_rgb.csv"), encoding="utf-8",
          mode="r") as unitfile:
    rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
    rd = [row for row in rd]
    header = rd[0]
    skin_colour_list = {}
    int_column = ["red","green","blue"]  # value in list only
    int_column = [index for index, item in enumerate(header) if item in int_column]
    for row_index, row in enumerate(rd):
        if row_index > 0:
            for n, i in enumerate(row):
                row = stat_convert(row, n, i, int_column=int_column)
                key = row[0].split("/")[0]
            skin_colour_list[key] = row[1:]

# print(skin_colour_list)

gen_body_sprite_pool = {}
for direction in ["front","side","back","cornerup","cornerdown"]:
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
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect(center=(screen_size[0] / 2, screen_size[1] / 2))
        self.grid = True
        
    def update(self):
        self.image.fill((255, 255, 255))
        if self.grid:
            grid_width = self.image.get_width() / 10
            grid_height = self.image.get_height() / 10
            for loop in range(1, 10):
                pygame.draw.line(self.image, (0,0,0), (grid_width * loop,0), (grid_width * loop, self.image.get_height()))
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

    def update(self):
        self.image = self.image_original2.copy()

    def selected(self, select=False):
        self.image = self.image_original2.copy()
        if select:
            pygame.draw.rect(self.image, (150, 200, 100), (0,0,self.image.get_width(),self.image.get_height()), 15)
            # self.add_strip(self.blitimage)

    def add_strip(self, image=None):
        self.image = self.image_original.copy()
        if image is not None:
            self.blitimage = pygame.transform.scale(image.copy(), (int(100 * self.image_scale[0]), int(100 * self.image_scale[1])))
            self.strip_rect = self.blitimage.get_rect(center=(self.image.get_width()/2, self.image.get_height()/2))
            self.image.blit(self.blitimage, self.strip_rect)
        self.image_original2 = self.image.copy()

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
        self.current_option = 0
        self.image_original = image
        self.image = self.image_original.copy()
        self.text_list = text_list
        self.change_text(self.text_list[self.current_option])
        self.rect = self.image.get_rect(center=pos)

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
        self.side = 0
        self.p1_eyebrow = list(gen_body_sprite_pool["side"]["eyebrow"].keys())[random.randint(0, len(gen_body_sprite_pool["side"]["eyebrow"]) - 1)]
        self.p1_eye = list(gen_body_sprite_pool["side"]["eye"].keys())[random.randint(0, len(gen_body_sprite_pool["side"]["eye"]) - 1)]
        self.p1_mouth = list(gen_body_sprite_pool["side"]["mouth"].keys())[random.randint(0, len(gen_body_sprite_pool["side"]["mouth"]) - 1)]

        self.rect_part_list = {"p1_r_arm_up" : None, "p1_r_arm_low" : None, "self.p1_r_hand" : None, "p1_l_arm_up" : None,
                               "p1_l_arm_low" : None, "p1_l_hand" : None, "p1_r_leg" : None, "p1_r_foot" : None,
                               "p1_l_leg" : None, "p1_l_foot" : None, "p1_main_weapon" : None, "p1_sub_weapon" : None,
                               "p2_head" : None, "p2_body" : None, "p2_r_arm_up" : None, "p2_r_arm_low" : None,
                               "p2_r_hand" : None, "p2_l_arm_up" : None, "p2_l_arm_low" : None, "p2_l_hand" : None,
                               "p2_r_leg" : None, "p2_r_foot" : None, "p2_l_leg" : None, "p2_l_foot" : None,
                               "p2_main_weapon" : None, "p2_sub_weapon" : None}
        self.part_selected = None
        self.generate_animation("Default")
        self.default = self.sprite_part.copy()

    def generate_animation(self, name):
        #  sprite animation generation
        animation_list = [generic_animation_pool[name]]  # , generic_animation_pool['Run']
        for animation in animation_list:
            for pose in animation:
                # TODO change later when have p2
                pose_layer_list = {k: v[-1] for k, v in pose.items() if k != "property" and v != 0 and v[-1] != 0}
                pose_layer_list = dict(sorted(pose_layer_list.items(), key=lambda item: item[1], reverse=True))

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
                        self.sprite_part[part] = [self.sprite_image[part], main_joint_pos_list[part], link_list[part], pose[part][4], pose[part][5]]

                image = pygame.Surface((150, 150), pygame.SRCALPHA)  # default size will scale down later
                for index, layer in enumerate(pose_layer_list):
                    if "weapon" not in layer:
                        part = self.sprite_part[layer]
                    image = self.part_to_sprite(image, part[0], index, part[1], part[2], part[3], part[4])
                self.animation_list.append(image)

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
        face[1] = self.apply_colour(face[1], [random.randint(0,255), random.randint(0,255), random.randint(0,255)])
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
            for part_link in skel_joint_list:
                if part_link in part:  # match part name, p1_head = head in part link #TODO change this when have p2
                    main_joint_pos_list[part] = list(skel_joint_list[part_link][0].values())[0]
                    break
        return main_joint_pos_list

    def click_part(self, mouse_pos):
        self.part_selected = None
        for index, rect in enumerate(self.rect_part_list):
            thisrect = self.rect_part_list[rect]
            if thisrect is not None and thisrect.collidepoint(mouse_pos):
                self.part_selected = index
                break

    def move_part(self, mouse_pos, current_frame):
        self.part_selected

    def rotate_part(self, mouse_pos, current_frame):
        self.part_selected

    def apply_colour(self, image, colour):
        size = (image.get_width(), image.get_height())
        data = pygame.image.tostring(image, "RGBA")  # convert image to string data for filtering effect
        image = Image.frombytes("RGBA", size, data)  # use PIL to get image data
        alpha = image.split()[-1]  # save alpha
        image = image.convert("L")  # convert to grey scale for colourise
        max_colour = 255 #- (colour[0] + colour[1] + colour[2])
        mid_colour = [c - ((max_colour - c) / 2) for c in colour]
        image = ImageOps.colorize(image, black="black", mid=mid_colour, white=colour).convert("RGB")
        image.putalpha(alpha)  # put back alpha
        image = image.tobytes()
        image = pygame.image.fromstring(image, size, "RGBA")  # convert image back to a pygame surface
        return image

    def make_link_pos(self, pose, index):
        part_link = [pose[index][2], pose[index][3]]
        return part_link

    def part_to_sprite(self, image, part, part_index, main_joint_pos, target, angle, flip):
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
        image.blit(part_rotated, rect)

        return image

    # def pose(self):

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
    def __init__(self, frms, spd_ms, loop):
        self.frames = frms
        self.speed_ms = spd_ms / 1000
        self.start_frame = 0
        self.end_frame = len(self.frames) - 1
        self.first_time = time.time()
        self.show_frame = 0
        self.current_frame = 0
        self.loop = loop

    def play(self, showroom, position):
        if time.time() - self.first_time >= self.speed_ms:
            self.show_frame += 1
            self.first_time = time.time()
        if self.show_frame > self.end_frame:
            self.show_frame = self.start_frame
        showroom.blit(self.frames[self.show_frame], position)

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
Filmstrip.containers = ui, filmstrips

filmstrip_list = [Filmstrip((0, 50 * screen_size[1] / 500)),Filmstrip((image.get_width(), 50 * screen_size[1] / 500)),
               Filmstrip((image.get_width() * 2, 50 * screen_size[1] / 500)), Filmstrip((image.get_width() * 3, 50 * screen_size[1] / 500)),
               Filmstrip((image.get_width() * 4, 50 * screen_size[1] / 500)), Filmstrip((image.get_width() * 5, 50 * screen_size[1] / 500)),
               Filmstrip((image.get_width() * 6, 50 * screen_size[1] / 500)), Filmstrip((image.get_width() * 7, 50 * screen_size[1] / 500)),
               Filmstrip((image.get_width() * 8, 50 * screen_size[1] / 500)),Filmstrip((image.get_width() * 9, 50 * screen_size[1] / 500))]

filmstrips.add(*filmstrip_list)

# p1_body_helper = Bodyhelper()
# p2_body_helper = Bodyhelper()
# effect_helper = Bodyhelper()

image = load_image(main_dir, "button.png", ["animation_maker_ui"])
image = pygame.transform.scale(image,  (int(image.get_width() * screen_size[1] / 1000),
                                        int(image.get_height() * screen_size[1] / 1000)))

# copy_button = Button("Copy",image, (100,200))
# paste_button = Button("Paste",image, (100,200))
# default_button = Button("Default",image, (100,200))
# clear_button = Button("Clear",image, (100,200))

# flip_vert_button = Button("Flip Vert",image, (100,200))
# flip_hori_button = Button("Flip Hori",image, (100,200))
# reset_button = Button("Reset",image, (100,200))

new_button = Button("New",image, (image.get_width() / 2, image.get_height()/2))
save_button = Button("Save",image, (image.get_width() * 2, image.get_height()/2))
delete_button = Button("Delete",image, (image.get_width() * 10, image.get_height()/2))


play_animation_button = SwitchButton(["Play", "Stop"], image,
                                     (screen_size[1]/2, filmstrip_list[0].rect.midbottom[1] + (image.get_height()/2)))
# loop_button = SwitchButton(["Loop:Yes", "Loop:No"],image, (100,200))

showroom = Showroom((150 * screen_size[0] / 500, 150 * screen_size[1] / 500))

runtime = 0
mousetimer = 0
play_animation = False
current_frame = 0

while True:
    dt = clock.get_time() / 1000
    mouse_pos = pygame.mouse.get_pos()  # current mouse pos based on screen
    mouse_up = False  # left click
    mouse_leftdown = False  # hold left click
    mouse_right = False  # right click
    mouse_rightdown = False  # hold right click
    double_mouse_right = False  # double right click
    mouse_scrolldown = False
    mouse_scrollup = False
    mouse_wheel = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # left click
                mouse_up = True
            if event.button == 2:  # left click
                print('test')
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
        #     if self.textinputpopup[0] == "text_input":  # event update to input box
        #         self.input_box.userinput(event)
        #     else:
        #         keypress = event.key

        if pygame.mouse.get_pressed()[0]:  # Hold left click
            mouse_leftdown = True
        elif pygame.mouse.get_pressed()[2]:  # Hold left click
            mouse_rightdown = True

    if mousetimer != 0:  # player click mouse once before
        mousetimer += dt  # increase timer for mouse click using real time
        if mousetimer >= 0.3:  # time pass 0.3 second no longer count as double click
            mousetimer = 0

    if mouse_up:
        if play_animation_button.rect.collidepoint(mouse_pos):
            if play_animation_button.current_option == 0:  #  start playing animation
                play_animation_button.change_option(1)
                play_animation = True
            else:  # stop animation
                play_animation_button.change_option(0)
                play_animation = False
        else:
            for strip_index, strip in enumerate(filmstrips):
                if strip.rect.collidepoint(mouse_pos):
                    current_frame = strip_index
                    break

    if runtime == 0:
        runtime = 0.1
        skeleton.animation_list = []
        skeleton.generate_animation('Default')
        frames = [pygame.transform.smoothscale(image, showroom.size) for image in skeleton.animation_list]
        for frame_index in range(0, 10):
            try:
                filmstrip_list[frame_index].add_strip(frames[frame_index])
            except IndexError:
                filmstrip_list[frame_index].add_strip()
        anim = Animation(frames, 1000, True)

    showroom.update()
    ui.update()

    if play_animation:
        runtime += dt
        if runtime >= 1:
            runtime = 0
    else:
        if showroom.rect.collidepoint(mouse_pos):
            mouse_pos = pygame.Vector2((mouse_pos[0] - showroom.rect.topleft[0]) / screen_size[0] * 500,
                                       (mouse_pos[1] - showroom.rect.topleft[1]) / screen_size[1] * 500)
            if mouse_up:
                skeleton.click_part(mouse_pos)
            if mouse_wheel:
                skeleton.move_part(mouse_pos, current_frame)
            elif mouse_right:
                skeleton.rotate_part(mouse_pos, current_frame)

    for strip_index, strip in enumerate(filmstrips):
        if strip_index == current_frame:
            strip.selected(True)
            break

    pen.fill((0, 0, 0))
    ui.draw(pen)
    anim.play(showroom.image, (0, 0))
    pen.blit(showroom.image, showroom.rect)
    pygame.display.update()
    clock.tick(60)
