import ast
import csv
import datetime
import math
import os
import random
import re

import numpy as np
import pygame
import pygame.freetype



def make_bar_list(main, listtodo, menuimage):
    """Make a drop down bar list option button"""
    from gamescript.tactical import prepare
    main_dir = main.main_dir
    barlist = []
    img = load_image(main_dir, "bar_normal.jpg", "ui\\mainmenu_ui")
    img2 = load_image(main_dir, "bar_mouse.jpg", "ui\\mainmenu_ui")
    img3 = img2
    for index, bar in enumerate(listtodo):
        barimage = (img.copy(), img2.copy(), img3.copy())
        bar = prepare.MenuButton(main, images=barimage, pos=(menuimage.pos[0], menuimage.pos[1] + img.get_height() * (index + 1)), text=bar)
        barlist.append(bar)
    return barlist


def load_base_button(main_dir):
    img = load_image(main_dir, "idle_button.png", ["ui", "mainmenu_ui"])
    img2 = load_image(main_dir, "mouse_button.png", ["ui", "mainmenu_ui"])
    img3 = load_image(main_dir, "click_button.png", ["ui", "mainmenu_ui"])
    return [img, img2, img3]


def text_objects(text, font):
    textsurface = font.render(text, True, (200, 200, 200))
    return textsurface, textsurface.get_rect()


def load_image(main_dir, file, subfolder=""):
    """loads an image, prepares it for play"""
    newsubfolder = subfolder
    if isinstance(newsubfolder, list):
        newsubfolder = ""
        for folder in subfolder:
            newsubfolder = os.path.join(newsubfolder, folder)
    thisfile = os.path.join(main_dir, "data", newsubfolder, file)
    surface = pygame.image.load(thisfile).convert_alpha()
    return surface


def load_images(main_dir, subfolder=None, loadorder=True, returnorder=False):
    """loads all images(files) in folder using loadorder list file use only png file"""
    imgs = []
    dirpath = os.path.join(main_dir, "data")
    if subfolder is not None:
        for folder in subfolder:
            dirpath = os.path.join(dirpath, folder)

    if loadorder:  # load in the order of load_order file
        loadorderfile = open(os.path.join(dirpath, "load_order.txt"), "r")
        loadorderfile = ast.literal_eval(loadorderfile.read())
        for file in loadorderfile:
            imgs.append(load_image(main_dir, file, dirpath))
    else:  # load every file
        loadorderfile = [f for f in os.listdir(dirpath) if f.endswith("." + "png")]  # read all file
        loadorderfile.sort(key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r"[^0-9]|[0-9]+", var)])
        for file in loadorderfile:
            imgs.append(load_image(main_dir, file, dirpath))

    if returnorder is False:
        return imgs
    else:  # return order of the file as list
        loadorderfile = [int(name.replace(".png", "")) for name in loadorderfile]
        return imgs, loadorderfile

def csv_read(maindir, file, subfolder=(), outputtype=0):
    """output type 0 = dict, 1 = list"""
    main_dir = maindir
    returnoutput = {}
    if outputtype == 1:
        returnoutput = []

    folder_dir = ""
    for folder in subfolder:
        folder_dir = os.path.join(folder_dir, folder)
    folder_dir = os.path.join(folder_dir, file)
    folder_dir = os.path.join(main_dir, folder_dir)
    with open(folder_dir, encoding="utf-8", mode="r") as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit() or ("-" in i and re.search("[a-zA-Z]", i) is None):
                    row[n] = int(i)
            if outputtype == 0:
                returnoutput[row[0]] = row[1:]
            elif outputtype == 1:
                returnoutput.append(row)
        unitfile.close()
    return returnoutput


def load_sound(main_dir, file):
    file = os.path.join(main_dir, "data", "sound", file)
    sound = pygame.mixer.Sound(file)
    return sound


def edit_config(section, option, value, filename, config):
    config.set(section, option, value)
    with open(filename, "w") as configfile:
        config.write(configfile)

def trait_skill_blit(self):
    """For blitting skill and trait icon into subunit info ui"""
    from gamescript import battleui
    SCREENRECT = self.SCREENRECT

    position = self.gameui[2].rect.topleft
    position = [position[0] + 70, position[1] + 60]  # start position
    startrow = position[0]

    for icon in self.skill_icon.sprites():
        icon.kill()

    for trait in self.gameui[2].value2[0]:
        self.skill_icon.add(battleui.SkillCardIcon(self.trait_imgs[0], (position[0], position[1]), 0, gameid=trait))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= SCREENRECT.width:
            position[1] += 30
            position[0] = startrow

    position = self.gameui[2].rect.topleft
    position = [position[0] + 70, position[1] + 100]
    startrow = position[0]

    for skill in self.gameui[2].value2[1]:
        self.skill_icon.add(battleui.SkillCardIcon(self.skill_imgs[0], (position[0], position[1]), 1, gameid=skill))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= SCREENRECT.width:
            position[1] += 30
            position[0] = startrow


def effect_icon_blit(self):
    """For blitting all status effect icon"""
    from gamescript import battleui
    SCREENRECT = self.SCREENRECT

    position = self.gameui[2].rect.topleft
    position = [position[0] + 70, position[1] + 140]
    startrow = position[0]

    for icon in self.effect_icon.sprites():
        icon.kill()

    for status in self.gameui[2].value2[4]:
        self.effect_icon.add(battleui.SkillCardIcon(self.status_imgs[0], (position[0], position[1]), 4, gameid=status))
        position[0] += 40
        if position[0] >= SCREENRECT.width:
            position[1] += 30
            position[0] = startrow


def countdown_skill_icon(self):
    """Count down timer on skill icon for activate and cooldown time"""
    for skill in self.skill_icon:
        if skill.icontype == 1:  # only do skill icon not trait
            cd = 0
            activetime = 0
            if skill.gameid in self.gameui[2].value2[2]:
                cd = int(self.gameui[2].value2[2][skill.gameid])
            if skill.gameid in self.gameui[2].value2[3]:
                activetime = int(self.gameui[2].value2[3][skill.gameid][3])
            skill.iconchange(cd, activetime)
    # for effect in self.effect_icon:
    #     cd = 0
    #     if effect.id in self.gameui[2].value2[4]:
    #         cd = int(self.gameui[2].value2[4][effect.id][3])
    #     effect.iconchange(cd, 0)


def rotationxy(self, origin, point, angle):
    ox, oy = origin
    px, py = point
    x = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    y = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return pygame.Vector2(x, y)

def convert_str_time(event):
    for index, item in enumerate(event):
        newtime = datetime.datetime.strptime(item[1], "%H:%M:%S").time()
        newtime = datetime.timedelta(hours=newtime.hour, minutes=newtime.minute, seconds=newtime.second)
        event[index] = [item[0], newtime]
        if len(item) == 3:
            event[index].append(item[2])

