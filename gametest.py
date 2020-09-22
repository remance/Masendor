#make exe
# import cx_Freeze
import math
# executables = [cx_Freeze.Executable("mainmenu.py")]
#
# cx_Freeze.setup(
#     name="RTS game",
#     options={"build_exe": {"packages":["pygame"]}},
#     executables = executables
#     )

## random map generator (https://dxprog.com/files/randmaps.html)
## https://www.redblobgames.com/maps/terrain-from-noise/

import random
import sys
import os
import csv
import pygame
from pygame.transform import scale
from pygame.locals import *

main_dir = os.path.dirname(os.path.abspath(__file__))

gradelist = {}
# with open(main_dir + "\data" + '\\unit_grade.csv', 'r') as unitfile:
#     rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
#     for row in rd:
#         for n, i in enumerate(row):
#             if i.isdigit() == True:
#                 row[n] = float(i)
#         gradelist[row[0]] = row[1:]
#
#
# for grade in range(len(gradelist)):
#     if 0 in gradelist:
#         print(gradelist)

# options = {0:"Broken", 1:"Retreating", 2:"Breaking", 3:"Poor", 4:"Wavering",  5:"Balanced", 6:"Steady", 7:"Fine", 8:"Confident", 9:"Eager", 10:"Ready"}
# if 0 in options:
#     print(options[0])

import sys
import numpy as np

# skilllist = {}
# with open(main_dir + "\data" + '\\unit_ability.csv', 'r') as unitfile:
#   rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
#   for row in rd:
#     for n, i in enumerate(row):
#       if i.isdigit() == True:
#         row[n] = float(i)
#       if i == "":
#         row[n] = 100
#       if "," in i: row[n] = [row[n]]
#     skilllist[row[0]] = row[1:]
# # print(self.gradelist[0])
# unitfile.close()
# k = [21,36]
# d = []
# n = []
# k = "Swordsmen are the most basic and balanced unit in most armies. They can fight well in most situation and can hold their lines well enough. Truly the Jack of all trade of all units that are safest to pick in unknown situations. But of course, a jack of all trade lack specialities that make them excellent in a specific situation. If you by some means manage to learn the enemy composition from in and out, it will be better to employed troops that are more specialised or you can still pick swordsmen if you like well-balanced units."
# print(len(k),k.split())
# while len(k) > 0:
#     for i in k:
#         if len(n)>50:
import pygame
import timeit

# whoarray = [np.array([20000, 20001, 20002, 20003,     1]), np.array([20005, 20000]), np.array([    1, 20009]), np.array([20005, 20006, 20007, 20008, 20009])]
from PIL import Image, ImageFilter

pygame.init()
screen = pygame.display.set_mode((512, 512))
clock = pygame.time.Clock()

compressed = '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'
size, image_mode, raw = (128, 128), 'RGBA', compressed.decode("base64").decode("zlib")

# create the original pygame surface
surf = pygame.image.fromstring(raw, size, image_mode)

# create a PIL image and blur it
pil_blured = Image.fromstring("RGBA", size, raw).filter(ImageFilter.GaussianBlur(radius=6))

# convert it back to a pygame surface
other = pygame.image.fromstring(pil_blured.tostring("raw", image_mode), size, image_mode)

pygame.time.set_timer(pygame.USEREVENT, 1000)

while True:
    for e in pygame.event.get():
        if e.type == pygame.USEREVENT: surf, other = other, surf
        if e.type == pygame.QUIT: break
    else:
        screen.fill((255, 255, 255))
        screen.blit(surf, (192, 192))
        pygame.display.flip()
        clock.tick(60)
        continue
    break