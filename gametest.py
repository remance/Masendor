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


#Resizes an image and keeps aspect ratio. Set mywidth to the desired with in pixels.

# import PIL
# from PIL import Image
#
# mywidth = 300
#
# img = Image.open('someimage.jpg')
# wpercent = (mywidth/float(img.size[0]))
# hsize = int((float(img.size[1])*float(wpercent)))
# img = img.resize((mywidth,hsize), PIL.Image.ANTIALIAS)
# img.save('resized.jpg')

"""next goal: moving army with mouse click, config file, sound volume adjust """

#!/usr/bin/env python

"""An zoomed image viewer that demonstrates Surface.scroll

This example shows a scrollable image that has a zoom factor of eight.
It uses the Surface.scroll function to shift the image on the display
surface. A clip rectangle protects a margin area. If called as a function,
the example accepts an optional image file path. If run as a program
it takes an optional file path command line argument. If no file
is provided a default image file is used.

When running click on a black triangle to move one pixel in the direction
the triangle points. Or use the arrow keys. Close the window or press ESC
to quit.

"""
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

# k = np.array([[1,1,1,1,1,0,0,0],[1,1,1,1,1,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
# whofrontline = np.array([1,2,3,4,0,5])
# targetfrontline = np.array([6,0,7,8,9,10])
# battleside= [0,0,0,0]
# side = 3
# for who in whofrontline:
#     print(who)
#     position = np.where(whofrontline == who)[0][0]
#     fronttarget = targetfrontline[position]
#     if fronttarget == 0:
#         print('ye')
#
# print(whofrontline)
# print(targetfrontline)
# x = {0:3,1:2}
# x = {k: v for k, v in sorted(x.items(), key=lambda item: item[1])}
# print(list(x.keys())[0])
# whoarray = np.array([[1,2,3,4,5],[6,7,8,9,10]])
fullwhoarray = [np.array([[20000, 20001, 20002, 20003,     1],
       [20005, 20006, 20007, 20008, 1]]), np.array([[20005, 20000],
       [20006, 20001],
       [20007, 20002],
       [20008, 20003],
       [20009,    1]]), np.array([[    1, 20009],
       [20003, 20008],
       [20002, 20007],
       [20001, 20006],
       [20000, 20005]]), np.array([[20005, 20006, 20007, 20008, 1],
       [20000, 20001, 20002, 20003,     1]])]
# whoarray = [np.array([20000, 20001, 20002, 20003,     1]), np.array([20005, 20000]), np.array([    1, 20009]), np.array([20005, 20006, 20007, 20008, 20009])]
# squadalive = np.array([1,1,1,2,2])
# print(squadalive[np.where(armysquad == 1)[0][0]] )
# squadalive[np.where(armysquad == 1)[0][0]] = 5
list = {0:1,1:2,2:3,3:4}
# starttime = timeit.default_timer()
# print("The start time is :",starttime)
# run = 0
# while run != 5:
#     k = 0
#     a = random.randint(0,20)
#     if a > 10:
#         k = 10
#     run += 1
# print("The time difference is :", timeit.default_timer() - starttime)
# starttime = timeit.default_timer()
# print("The start time is :",starttime)
# run = 0
# k = 10
# while run != 5:
#     a = random.randint(0,20)
#     if a > 10:
#         k = 10
#     else: 0
#     run += 1
# print("The time difference is :", timeit.default_timer() - starttime)

a = {1:[0,1,2,3,4]}
a = {key: val for key, val in a.items() if val[0] > 0}
print(a)
