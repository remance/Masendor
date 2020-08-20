import csv
import math
import random
from statistics import mean

import numpy as np
import pygame
import pygame.freetype
from pygame.transform import scale

from RTS import mainmenu

main_dir = mainmenu.main_dir

class leaderdata():
    def __init__(self, img, option):
        self.imgs = img
        self.leaderlist = {}
        with open(main_dir + "\data\leader" + str(option) + '\\historical_leader.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = int(i)
                    # if and n in []:
                    #     if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                    # else: row[n] = [int(i)]
                self.leaderlist[row[0]] = row[1:]
        unitfile.close()

        self.leaderclass = {}
        with open(main_dir + "\data\leader" + '\\leader_class.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit(): row[n] = int(i)
                    # if and n in []:
                    #     if "," in i: row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                    # else: row[n] = [int(i)]
                self.leaderclass[row[0]] = row[1:]
        unitfile.close()

class leader(pygame.sprite.Sprite):

    def __init__(self, leaderid, squadposition, armyposition, battalion, leaderstat):
        self._layer = 6
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.morale = 100
        stat = leaderstat.leaderlist[leaderid]
        self.name = stat[0]
        self.health = stat[1]
        self.authority = stat[2]
        self.meleecommand = stat[3]
        self.rangecommand = stat[4]
        self.cavcommand = stat[5]
        self.combat = stat[6]
        self.social = leaderstat.leaderclass[stat[7]]
        self.description = stat[-1]
        self.squadpos = squadposition
        # self.trait = stat
        # self.skill = stat
        self.state = 0 ## 0 = alive, 98 = missing 99 = wound, 100 = dead
        self.battalion = battalion
        # self.mana = stat
        self.gamestart = 0
        self.armyposition = armyposition
        self.imgposition = [(133,65),(80,115),(190,115),(133,163)]
        self.imgposition = self.imgposition[self.armyposition]
        ## put leader image into leader slot
        self.image = leaderstat.imgs[leaderid]
        self.rect = self.image.get_rect(center=self.imgposition)

    def update(self, statuslist, squadgroup, dt, viewmode, playerposlist, enemyposlist):
        if self.gamestart == 0:
            self.squad = self.battalion.squadsprite[self.squadpos]
            self.gamestart = 1
        if self.state not in [100,101]:
            if self.health < 0:
                self.state = 100

