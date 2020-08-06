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
# mapname = '\\test'
# unitlist = []
# with open(main_dir + "\data" + "\map" + mapname + '.csv', 'r') as unitfile:
#        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
#        for row in rd:
#               for n, i in enumerate(row):
#                      if i.isdigit():
#                             row[n] = int(i)
#                      if n in range(1,11):
#                             row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
#                             # print(row[n])
#               unitlist.append(row)
# print(unitlist)
# a = {22: ['Anti-Cavalry', 1.0, 1.0, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 0.0, 0.0, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 'This squad is specialised in combat against cavalry squads. Cavalry charge and combat will be much less effective against this squad.', 100]}
# for d in a.items():
#        print(d)
# calsquadlist = np.array([0,0,0,1,1,2,0,0],[0,0,0,1,1,2,0,0])
# calsquadlist = np.delete(calsquadlist, (calsquadlist <= 1).nonzero()[0][:round(
#                 (np.count_nonzero(calsquadlist <= 1)) * 70 / 100)])
# print(calsquadlist)
a = [[10000, 10001, 10002, 10003, 10004, 10005, 10006, 10007],
 [10008, 10009, 10010, 10011, 10012, 10013, 10014, 10015]]
# print(len(a))
nearbysquadlist = []
cornersquad = []
for rowindex, rowlist in enumerate(a):
       for squad in rowlist:
              if squad == 10008:
                     if rowlist.index(10008) - 1 != -1:  # get squad from left if not at first column
                            nearbysquadlist.append(a[rowindex][rowlist.index(10008) - 1])
                     else:
                            nearbysquadlist.append(0)
                     if rowlist.index(10008) + 1 != 8:  # get squad from right if not at last column
                            nearbysquadlist.append(a[rowindex][rowlist.index(10008) + 1])
                     else:
                            nearbysquadlist.append(0)
                     if rowindex != 0:  # get bottom squad
                            nearbysquadlist.append(a[rowindex - 1][rowlist.index(10008)])
                            if rowlist.index(10008) - 1 != -1:
                                   cornersquad.append(a[rowindex - 1][rowlist.index(10008) - 1])
                            else:
                                   cornersquad.append(0)
                            if rowlist.index(10008) + 1 != 8:
                                   cornersquad.append(a[rowindex - 1][rowlist.index(10008) + 1])
                            else:
                                   cornersquad.append(0)
                     else:
                            nearbysquadlist.append(0)
                     if rowindex != len(a) - 1:  # get above squad
                            nearbysquadlist.append(a[rowindex + 1][rowlist.index(10008)])
                     else:
                            nearbysquadlist.append(0)
print(nearbysquadlist, cornersquad)