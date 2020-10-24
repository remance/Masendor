import csv

import pygame.freetype

from RTS import mainmenu

main_dir = mainmenu.main_dir


class Factiondata():
    images = []

    def __init__(self, option):
        """Unit stat data read"""
        self.factionlist = {}
        with open(main_dir + "\data" + "\\ruleset" + option + "\\faction" + '\\faction.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                    # if n in (5, 6, 11, 22, 23):
                    #     if "," in i:
                    #         row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
                    #     elif i.isdigit():
                    #         row[n] = [int(i)]
                self.factionlist[row[0]] = row[1:]
            unitfile.close()


class Faction(pygame.sprite.Sprite):
    factionlist = None

    def __init__(self, factionid):
        self.gameid = factionid
        self.name = self.factionlist[self.gameid][0]
        self.image = self.factionlist.images[factionid]
