# make exe
# import cx_Freeze
# executables = [cx_Freeze.Executable("main.py")]
#
# cx_Freeze.setup(
#     name="RTS game",
#     options={"build_exe": {"packages":["pygame"]}},
#     executables = executables
#     )

## random map generator (https://dxprog.com/files/randmaps.html)
## https://www.redblobgames.com/maps/terrain-from-noise/

# column to list
# https://convert.town/column-to-comma-separated-list

## Flash screen

## https://stackoverflow.com/questions/41255357/cpu-efficient-way-to-flash-the-screen-a-certain-color-in-pygame

import os

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
import timeit
import re
import numpy as np

# starttime = timeit.default_timer()
# print("The start time is :", starttime)
# for i in range(0,10000):
#     if i in [1,2,3,4,5,6,7,8,9,10]:
#         print(i)
#     # if o < 0:
#     #     o = 0
# print("The time difference is :", timeit.default_timer() - starttime)
# #0.000859586999999995
# #0.0010708489999999848

a = 4.9
print(a.is_integer())

import pygame,time
#created in 22 dec 2020 by cenk
pen=pygame.display.set_mode((200,200))
frms=[pygame.Surface((20,20)),pygame.Surface((20,20)),pygame.Surface((20,20))]
frms[0].fill((255,0,0))#red frame
frms[1].fill((0,255,0))#green frame
frms[2].fill((0,0,255))#blue frame
#this is actual class
class animation:
	def __init__(self,frms,spd_ms):
		self.frames=frms
		self.speed_ms=spd_ms/1000
		self.start_frame=0
		self.end_frame=len(self.frames)-1
		self.first_time=time.time()
		self.show_frame=0
	def blit(self,pen,crd):
		if time.time()-self.first_time>=self.speed_ms:
			self.show_frame=self.show_frame+1
			self.first_time=time.time()
		if self.show_frame>self.end_frame:
			self.show_frame=self.start_frame
		#pen mean to window and is abbreivation of "pencere"
		pen.blit(self.frames[self.show_frame],crd)
anim=animation(frms,500)
run=True
while run:
	for i in pygame.event.get():
		if i.type==pygame.QUIT:
			run=False
	pen.fill((0,0,0))
	anim.blit(pen,(50,50))
	pygame.display.flip()