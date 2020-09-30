"""
still not sure how collision should work in final (now main problem is when in melee combat and another unit can snuck in with rotate will finalised this after big map update 0.4+)
Optimise list
remove index and change call to the sprite itself
maybe all base pos stuff should be in smallest map pos including all calculation? should help reduce ram and cpu usage when zoom in/out, also maybe delete map.image when not shown and recreate it when change
"""
import ast
import csv
import glob
import os
import os.path
import random

import numpy as np
import pygame
import pygame.freetype
from pygame.locals import *
from pygame.transform import scale

from RTS import mainmenu
from RTS.script import gamesquad, gamebattalion, gameui, gameleader, gamemap, gamecamera, rangeattack, gamepopup

SCREENRECT = mainmenu.SCREENRECT
main_dir = mainmenu.main_dir


def load_image(file, subfolder=""):
    """loads an image, prepares it for play"""
    file = os.path.join(main_dir, 'data', subfolder, file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pygame.get_error()))
    return surface.convert_alpha()


def load_images(subfolder=[], loadorder=True):
    """loads all images(files) in folder using loadorder list file use only png file"""
    imgs = []
    dirpath = os.path.join(main_dir, 'data')
    if subfolder != []:
        for folder in subfolder:
            dirpath = os.path.join(dirpath, folder)
    if loadorder == True:
        loadorder = open(dirpath + "/load_order.txt", "r")
        loadorder = ast.literal_eval(loadorder.read())
        for file in loadorder:
            imgs.append(load_image(dirpath + "/" + file))
    else:
        loadorder = [f for f in os.listdir(dirpath) if f.endswith('.' + "png")]  ## read all file
        for file in loadorder:
            imgs.append(load_image(dirpath + "/" + file))
    return imgs


def load_sound(file):
    file = os.path.join(main_dir, 'data/sound/', file)
    sound = pygame.mixer.Sound(file)
    return sound


def addarmy(squadlist, position, gameid, colour, imagesize, leader, leaderstat, unitstat, control, coa, command=False, startangle=0):
    squadlist = squadlist[~np.all(squadlist == 0, axis=1)]
    squadlist = squadlist[:, ~np.all(squadlist == 0, axis=0)]
    army = gamebattalion.unitarmy(startposition=position, gameid=gameid,
                                  squadlist=squadlist, imgsize=imagesize,
                                  colour=colour, control=control, coa=coa, commander=command, startangle=startangle)
    army.hitbox = [gamebattalion.hitbox(army, 0, army.rect.width-10, 2),
                   gamebattalion.hitbox(army, 1, 2, army.rect.height-10),
                   gamebattalion.hitbox(army, 2, 2, army.rect.height-10),
                   gamebattalion.hitbox(army, 3, army.rect.width-10, 2)]
    army.leader = [gameleader.leader(leader[0], leader[4], 0, army, leaderstat),
                   gameleader.leader(leader[1], leader[5], 1, army, leaderstat),
                   gameleader.leader(leader[2], leader[6], 2, army, leaderstat),
                   gameleader.leader(leader[3], leader[7], 3, army, leaderstat)]
    return army


def unitsetup(playerarmy, enemyarmy, battle, imagewidth, imageheight, allweapon, allarmour, allleader, gameunitstat, coa, squad, inspectuipos,
              enactment=False):
    """squadindexlist is list of every squad index in the game for indexing the squad group"""
    # defaultarmy = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
    squadindexlist = []
    unitlist = []
    playercolour = (144, 167, 255)
    enemycolour = (255, 114, 114)
    """army num is list index for battalion in either player or enemy group"""
    playerstart, enemystart = 0, 0
    """squadindex is list index for all squad group"""
    squadindex = 0
    """firstsquad check if it the first ever in group"""
    squadgameid = 10000
    with open(main_dir + "\data" + "\map" + battle + "\\unit_pos.csv", 'r') as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit():
                    row[n] = int(i)
                if n in range(1, 12):
                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
            if row[0] < 2000:
                if row[0] == 1:
                    """First player battalion as commander"""
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   playercolour,
                                   (imagewidth, imageheight), row[10] + row[11], allleader, gameunitstat, True, coa[row[12]], True,
                                   startangle=row[13])
                else:
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   playercolour, (imagewidth, imageheight), row[10] + row[11], allleader, gameunitstat, True, coa[row[12]],
                                   startangle=row[13])
                playerarmy.append(army)
                playerstart += 1
            elif row[0] >= 2000:
                if row[0] == 2000:
                    """First enemy battalion as commander"""
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   enemycolour,
                                   (imagewidth, imageheight), row[10] + row[11], allleader, gameunitstat, enactment, coa[row[12]], True,
                                   startangle=row[13])
                elif row[0] > 2000:
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   enemycolour,
                                   (imagewidth, imageheight), row[10] + row[11], allleader, gameunitstat, enactment, coa[row[12]], startangle=row[13])
                enemyarmy.append(army)
                enemystart += 1
            """armysquadindex is list index for squad list in a specific army"""
            armysquadindex = 0
            """Setup squad in army to squad group"""
            for squadnum in np.nditer(army.armysquad, op_flags=['readwrite'], order='C'):
                if squadnum != 0:
                    addsquad = gamesquad.unitsquad(unitid=squadnum, gameid=squadgameid, weaponlist=allweapon, armourlist=allarmour,
                                                   statlist=gameunitstat,
                                                   battalion=army, position=army.squadpositionlist[armysquadindex], inspectuipos=inspectuipos)
                    squad.append(addsquad)
                    squadnum[...] = squadgameid
                    army.squadsprite.append(addsquad)
                    squadindexlist.append(squadgameid)
                    squadgameid += 1
                    squadindex += 1
                armysquadindex += 1
    unitfile.close()
    return squadindexlist


class battle():
    def __init__(self, winstyle):
        # Initialize pygame
        pygame.init()
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer = None
        # Set the display mode
        self.bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
        self.screen = pygame.display.set_mode(SCREENRECT.size, winstyle | pygame.RESIZABLE, self.bestdepth)
        # for when implement game and map camera
        # self.battle_surf = pygame.surface.Surface(width, height)
        # in your main loop
        # or however you draw your sprites
        # your_sprite_group.draw(game_surf)
        # then blit to screen
        # self.screen.blit(self.battle_surf, the_position)
        # Load images, assign to sprite classes
        # (do this before the classes are used, after screen setup)
        ## create game map
        featurelist = ["Grassland","Draught","Bushland","Forest","Inland Water","Road","Building","Farm","Wall","Mana Flux","Creeping Rot","Mud","Savanna","Draught","Tropical Shrubland","Jungle","Inland Water","Road","Building","Farm","Wall","Heat Mana","Creeping Rot","Mud","Volcanic Soil","Scorched Land","","","","Road","","Fertile Farm","Wall","Fire Mana","Creeping Rot","","Desert Plain","Desert Sand","Desert Shrubland","Desert Forest","Oasis","Sand Road","Desert Dwelling","Desert Farm","Wall","Earth Mana","Creeping Rot","Quicksand","Snow","Tundra","Arctic Shrubland","Arctic Forest","Frozen Water","Snow Road","Warm Shelter","Arctic Farm","Wall","Ice Mana","Preserving Rot","Ice Ground","","","","","Poisoned Water","","","","Wall","Poisoned Mana","Creeping Rot","","","Void","","","","","","","","Leyline","Creeping Rot","","","","","","","","","","Demonic Wall","","Creeping Rot","","","","","","","","","","Death Wall","","Rotten Land","","Lively Water","Empty Water","Marsh","Swamp","Water","Bridge","Swamp Building","Swamp Farm","Wall","Cold Mana","Creeping Rot","","Sea","Ocean","Coral Reef","Underwater Forest","Fresh Water","Bridge","Sunken City","Fishery","Submerged Wall","Water Mana","Creeping Rot",""]
        mapselected = "testmap"
        imgs = load_images(['map', mapselected],loadorder=False)
        gamemap.map.images = [imgs[0]]
        gamemap.mapfeature.images = [imgs[1]]
        gamemap.mapheight.images = [imgs[2]]
        gamemap.beautifulmap.placename = imgs[3]
        img = load_image('effect.png', 'map')
        gamemap.beautifulmap.effectimage = img
        empty = load_image('empty.png', 'map/texture')
        maptexture = []
        loadtexturefolder = []
        for feature in featurelist:
            loadtexturefolder.append(feature.replace(" ", "").lower())
        loadtexturefolder = list(set(loadtexturefolder))
        loadtexturefolder = [item for item in loadtexturefolder if item != ""] ## For now remove terrain with no planned name/folder yet
        for index, texturefolder in enumerate(loadtexturefolder):
            imgs = load_images(['map','texture', texturefolder], loadorder=False)
            maptexture.append(imgs)
        gamemap.beautifulmap.textureimages = maptexture
        gamemap.beautifulmap.loadtexturelist = loadtexturefolder
        gamemap.beautifulmap.emptyimage = empty
        ## create unit
        imgsold = load_images(['war', 'unit_ui'])
        imgs = []
        for img in imgsold:
            # x, y = img.get_width(), img.get_height()
            # img = pygame.transform.scale(img, (int(x),int(y/2)))
            imgs.append(img)
        gamesquad.unitsquad.images = imgs
        self.imagewidth, self.imageheight = imgs[0].get_width(), imgs[0].get_height()
        imgs = []
        imgsold = load_images(['war', 'unit_ui', 'battalion'])
        for img in imgsold:
            imgs.append(img)
        gamebattalion.unitarmy.images = imgs
        imgsold = load_images(['war', 'unit_ui', 'weapon'])
        imgs = []
        for img in imgsold:
            x, y = img.get_width(), img.get_height()
            img = pygame.transform.scale(img, (int(x / 1.7), int(y / 1.7)))
            imgs.append(img)
        self.allweapon = gamebattalion.weaponstat(imgs)  ## create weapon class
        imgs = load_images(['war', 'unit_ui', 'armour'])
        self.allarmour = gamebattalion.armourstat(imgs)  ## create armour class
        imgsold = load_images(['ui', 'skill_icon'], loadorder=False)
        imgs = []
        for img in imgsold:
            imgs.append(img)
        self.gameunitstat = gamebattalion.unitstat(imgs, imgs, imgs, imgs)
        ## create leader list
        imgsold = load_images(['leader', 'historic'])
        imgs = []
        for img in imgsold:
            x, y = img.get_width(), img.get_height()
            img = pygame.transform.scale(img, (int(x / 2), int(y / 2)))
            imgs.append(img)
        self.allleader = gameleader.leaderdata(imgs, option="\historic")
        ## coa imagelist
        imgsold = load_images(['leader', 'historic', 'coa'])
        imgs = []
        for img in imgsold:
            imgs.append(img)
        self.coa = imgs
        ## Game Effect
        imgsold = load_images(['effect'])
        imgs = []
        for img in imgsold:
            x, y = img.get_width(), img.get_height()
            # img = pygame.transform.scale(img, (int(x ), int(y / 2)))
            imgs.append(img)
        self.gameeffect = imgs
        rangeattack.arrow.images = [self.gameeffect[0]]
        ## Popup Ui
        imgs =  load_images(['ui','popup_ui','terraincheck'], loadorder=False)
        gamepopup.terrainpopup.images = imgs
        # decorate the game window
        # icon = load_image('sword.jpg')
        # icon = pygame.transform.scale(icon, (32, 32))
        # pygame.display.set_icon(icon)
        pygame.display.set_caption('Masendor RTS')
        pygame.mouse.set_visible(1)

        # #load the sound effects
        # boom_sound = load_sound('boom.wav')
        # shoot_sound = load_sound('car_door.wav')
        """Random music played from list"""
        if pygame.mixer:
            self.SONG_END = pygame.USEREVENT + 1
            # musiclist = os.path.join(main_dir, 'data/sound/')
            self.musiclist = glob.glob(main_dir + '/data/sound/*.mp3')
            self.pickmusic = random.randint(1, 1)
            pygame.mixer.music.set_endevent(self.SONG_END)
            pygame.mixer.music.load(self.musiclist[self.pickmusic])
            pygame.mixer.music.play(0)
        """Initialize Game Groups"""
        self.allcamera = pygame.sprite.LayeredUpdates() ## the layer is as followed 0 = terrain map, 1 = dead army, 2 = map special feature, 3 = hitbox, 4 = direction arrow, 5 = battalion, 6 = flying battalion, 7 = arrow/range, 8 = ui/button, 9 = squad inspect, 10 pop up
        self.allui = pygame.sprite.LayeredUpdates()
        self.unitupdater = pygame.sprite.Group()
        self.uiupdater = pygame.sprite.Group()
        self.mapupdater = pygame.sprite.Group()
        self.effectupdater = pygame.sprite.Group()
        self.battlemap = pygame.sprite.Group()
        self.battlemapfeature = pygame.sprite.Group()
        self.battlemapheight = pygame.sprite.Group()
        self.showmap = pygame.sprite.Group()
        self.playerarmy = pygame.sprite.Group()
        self.enemyarmy = pygame.sprite.Group()
        self.squad = pygame.sprite.Group()
        self.armyleader = pygame.sprite.Group()
        self.hitboxs = pygame.sprite.Group()
        self.arrows = pygame.sprite.Group()
        self.directionarrows = pygame.sprite.Group()
        self.deadunit = pygame.sprite.Group()
        self.gameui = pygame.sprite.Group()
        self.minimap = pygame.sprite.Group()
        self.buttonui = pygame.sprite.Group()
        self.squadselectedborder = pygame.sprite.Group()
        self.fpscount = pygame.sprite.Group()
        self.switchbuttonui = pygame.sprite.Group()
        self.terraincheck = pygame.sprite.Group()
        self.buttonnamepopup = pygame.sprite.Group()
        self.leaderpopup = pygame.sprite.Group()
        """assign default groups"""
        gamemap.map.containers = self.battlemap, self.mapupdater
        gamemap.mapfeature.containers = self.battlemapfeature, self.mapupdater
        gamemap.mapheight.containers = self.battlemapheight, self.mapupdater
        gamemap.beautifulmap.containers = self.showmap, self.mapupdater, self.allcamera
        gamebattalion.unitarmy.containers = self.playerarmy, self.enemyarmy, self.unitupdater, self.squad, self.allcamera
        gamesquad.unitsquad.containers = self.playerarmy, self.enemyarmy, self.unitupdater, self.squad
        gamebattalion.deadarmy.containers = self.deadunit, self.unitupdater, self.allcamera
        gamebattalion.hitbox.containers = self.hitboxs, self.unitupdater, self.allcamera
        gameleader.leader.containers = self.armyleader, self.unitupdater
        rangeattack.arrow.containers = self.arrows, self.effectupdater, self.allcamera
        gamebattalion.directionarrow.containers = self.directionarrows, self.effectupdater, self.allcamera
        gameui.Gameui.containers = self.gameui, self.uiupdater
        gameui.minimap.containers = self.minimap, self.allui
        gameui.fpscount.containers = self.allui
        gameui.uibutton.containers = self.buttonui, self.uiupdater
        gameui.switchuibutton.containers = self.switchbuttonui, self.uiupdater
        gameui.selectedsquad.containers = self.squadselectedborder
        gamepopup.terrainpopup.containers = self.terraincheck
        gamepopup.onelinepopup.containers = self.buttonnamepopup, self.leaderpopup
        ## create the background map
        self.camerapos = pygame.Vector2(500,500) ## Camera pos at the current zoom
        self.basecamerapos = pygame.Vector2(500,500) ## Camera pos at furthest zoom for recalculate sprite pos after zoom
        self.camerascale = 1 ## Camera zoom
        self.battlemap = gamemap.map(self.camerascale)
        self.battlemapfeature = gamemap.mapfeature(self.camerascale)
        self.battlemapheight = gamemap.mapheight(self.camerascale)
        self.showmap = gamemap.beautifulmap(self.camerascale, self.battlemap, self.battlemapfeature, self.battlemapheight)
        gamebattalion.unitarmy.gamemap = self.battlemap ## add battle map to all battalion class
        gamebattalion.unitarmy.gamemapfeature = self.battlemapfeature  ## add battle map to all battalion class
        gamebattalion.unitarmy.gamemapheight = self.battlemapheight
        self.camera = gamecamera.camera(self.camerapos, self.camerascale)
        self.background = pygame.Surface(SCREENRECT.size)
        self.background.fill((255,255,255))
        # pygame.display.flip()
        """Create Starting Values"""
        self.enactment = True
        self.timer = 0
        self.dt = 0
        self.combattimer = 0
        self.clock = pygame.time.Clock()
        self.lastmouseover = 0
        """use same position as squad front index 0 = front, 1 = left, 2 = rear, 3 = right"""
        self.battlesidecal = [1, 0.5, 0.1, 0.5]
        """create game ui"""
        self.minimap = gameui.minimap(SCREENRECT.width, SCREENRECT.height, self.showmap.trueimage, self.camera)
        topimage = load_images(['ui', 'battle_ui'])
        iconimage = load_images(['ui', 'battle_ui', 'topbar_icon'])
        self.gameui = [
            gameui.Gameui(screen=self.screen, X=SCREENRECT.width - topimage[0].get_size()[0] / 2, Y=topimage[0].get_size()[1] / 2, image=topimage[0],
                          icon=iconimage, uitype="topbar")]
        iconimage = load_images(['ui', 'battle_ui', 'commandbar_icon'])
        self.gameui.append(
            gameui.Gameui(screen=self.screen, X=topimage[1].get_size()[0] / 2, Y=topimage[1].get_size()[1] / 2, image=topimage[1], icon=iconimage,
                          uitype="commandbar"))
        iconimage = load_images(['ui', 'battle_ui', 'unitcard_icon'])
        self.gameui.append(
            gameui.Gameui(screen=self.screen, X=SCREENRECT.width - topimage[2].get_size()[0] / 2, Y=SCREENRECT.height - 310, image=topimage[2],
                          icon="", uitype="unitcard"))
        self.gameui[2].featurelist = featurelist
        self.gameui.append(
            gameui.Gameui(screen=self.screen, X=SCREENRECT.width - topimage[5].get_size()[0] / 2, Y=topimage[0].get_size()[1] + 150,
                          image=topimage[5], icon="", uitype="armybox"))
        self.popgameui = self.gameui
        self.buttonui = [gameui.uibutton(self.gameui[2].X - 152, self.gameui[2].Y + 10, topimage[3], 0),
                         gameui.uibutton(self.gameui[2].X - 152, self.gameui[2].Y - 70, topimage[4], 1),
                         gameui.uibutton(self.gameui[2].X - 152, self.gameui[2].Y - 30, topimage[7], 2),
                         gameui.uibutton(self.gameui[2].X - 152, self.gameui[2].Y + 50, topimage[22], 3),
                         gameui.uibutton(self.gameui[0].X - 206, self.gameui[0].Y, topimage[6], 1),
                         gameui.uibutton(self.gameui[1].X - 115, self.gameui[1].Y + 26, topimage[8], 0),
                         gameui.uibutton(self.gameui[1].X - 115, self.gameui[1].Y + 56, topimage[9], 1),
                         gameui.uibutton(self.gameui[1].X - 115, self.gameui[1].Y + 96, topimage[14], 1)]
        self.switchbuttonui = [gameui.switchuibutton(self.gameui[1].X - 70, self.gameui[1].Y + 96, topimage[10:14]),
                               gameui.switchuibutton(self.gameui[1].X - 30, self.gameui[1].Y + 96, topimage[15:17]),
                               gameui.switchuibutton(self.gameui[1].X, self.gameui[1].Y + 96, topimage[17:20]),
                               gameui.switchuibutton(self.gameui[1].X + 40, self.gameui[1].Y + 96, topimage[20:22])]
        self.squadselectedborder = gameui.selectedsquad(topimage[-1])
        self.terraincheck = gamepopup.terrainpopup()
        self.buttonnamepopup = gamepopup.onelinepopup()
        self.leaderpopup = gamepopup.onelinepopup()
        self.fpscount = gameui.fpscount()
        """initialise starting unit sprites"""
        self.playerarmy, self.enemyarmy, self.squad = [], [], []
        self.inspectuipos = [self.gameui[0].rect.bottomleft[0] - self.imagewidth / 1.25,
                             self.gameui[0].rect.bottomleft[1] - self.imageheight / 3]
        self.squadindexlist = unitsetup(self.playerarmy, self.enemyarmy, '\\testmap',
                                        self.imagewidth, self.imageheight, self.allweapon, self.allarmour, self.allleader,
                                        self.gameunitstat, self.coa, self.squad,
                                        self.inspectuipos, enactment=self.enactment)
        self.allunitlist = self.playerarmy.copy()
        self.allunitlist = self.allunitlist + self.enemyarmy
        self.allunitindex = [army.gameid for army in self.allunitlist]
        self.deadindex = 0
        self.playerposlist = {}
        self.enemyposlist = {}
        self.showingsquad = []

    def squadselectside(self, targetside, side, position):
        """side 0 is left 1 is right"""
        thisposition = position
        if side == 0:
            max = 0
            while targetside[thisposition] <= 1 and thisposition != max:
                thisposition -= 1
        else:
            max = 7
            while targetside[thisposition] <= 1 and thisposition != max:
                thisposition += 1
        if thisposition < 0:
            thisposition = 0
        elif thisposition > 7:
            thisposition = 7
        if targetside[thisposition] != 0:
            fronttarget = targetside[thisposition]
        else:
            fronttarget = 0
        return fronttarget

    def changeside(self, side, position):
        """position is attacker position against defender 0 = front 1 = left 2 = rear 3 = right"""
        """side is side of attack for rotating to find the correct side the defender got attack accordingly (e.g. left attack on right side is front)"""
        subposition = position
        if subposition == 2:
            subposition = 3
        elif subposition == 3:
            subposition = 2
        changepos = 1
        if subposition == 2:
            changepos = -1
        finalposition = subposition + changepos  ## right
        if side == 0: finalposition = subposition - changepos  ## left
        if finalposition == -1:
            finalposition = 3
        elif finalposition == 4:
            finalposition = 0
        return finalposition

    def combatpositioncal(self, sortmidfront, attacker, receiver, attackerside, receiverside, squadside):
        for thiswho in sortmidfront:
            if thiswho > 1:
                position = np.where(attacker.frontline[attackerside] == thiswho)[0][0]
                fronttarget = receiver.frontline[receiverside][position]
                """check if squad not already fighting if true skip picking new enemy """
                if any(battle > 1 for battle in self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside) == False:
                    """get front of another battalion frontline to assign front combat if it 0 squad will find another unit on the left or right"""
                    if fronttarget > 1:
                        """only attack if the side is already free else just wait until it free"""
                        if self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[squadside] in (-1, 0):
                            self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[attackerside] = fronttarget
                            self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[squadside] = thiswho
                    else:
                        """pick flank attack if no enemy already fighting and not already fighting"""
                        chance = random.randint(0, 1)
                        secondpick = 0
                        if chance == 0: secondpick = 1
                        """attack left array side of the squad if get random 0, right if 1"""
                        truetargetside = self.changeside(chance, receiverside)
                        fronttarget = self.squadselectside(receiver.frontline[receiverside], chance, position)
                        """attack if the found defender at that side is free if not check other side"""
                        if fronttarget > 1:
                            if self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] in (-1, 0):
                                self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[attackerside] = fronttarget
                                self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] = thiswho
                        else:
                            """Switch to another side if above not found"""
                            truetargetside = self.changeside(secondpick, receiverside)
                            fronttarget = self.squadselectside(receiver.frontline[receiverside], secondpick, position)
                            if fronttarget > 1:
                                if self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] in (-1, 0):
                                    self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[attackerside] = fronttarget
                                    self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] = thiswho
                            else:
                                self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[receiverside] = 0

    def squadcombatcal(self, who, target, whoside, targetside):
        """calculate squad engagement using information after battalionengage who is player battalion, target is enemy battalion"""
        squadwhoside = [2 if whoside == 3 else 3 if whoside == 2 else 1 if whoside == 1 else 0][0]
        squadtargetside = [2 if targetside == 3 else 3 if targetside == 2 else 1 if targetside == 1 else 0][0]
        sortmidfront = [who.frontline[whoside][3], who.frontline[whoside][4], who.frontline[whoside][2], who.frontline[whoside][5],
                        who.frontline[whoside][1], who.frontline[whoside][6], who.frontline[whoside][0], who.frontline[whoside][7]]
        """only calculate if the attack is attack with the front side"""
        if whoside == 0:
            self.combatpositioncal(sortmidfront, who, target, whoside, targetside, squadtargetside)
        """only calculate if the target is attacked on the front side"""
        if targetside == 0:
            sortmidfront = [target.frontline[targetside][3], target.frontline[targetside][4],
                            target.frontline[targetside][2],
                            target.frontline[targetside][5], target.frontline[targetside][1],
                            target.frontline[targetside][6],
                            target.frontline[targetside][0], target.frontline[targetside][7]]
            self.combatpositioncal(sortmidfront, target, who, targetside, whoside, squadwhoside)

    def losscal(self, who, target, hit, defense, type):
        heightadventage = who.battalion.height - target.battalion.height
        hit += heightadventage
        if hit < 0: hit = 0
        """ignore def trait"""
        if defense < 0 or 30 in who.trait: defense = 0
        hitchance = hit - defense
        if hitchance <= 10:
            combatscore = 0
            finalchance = random.randint(0, 100)
            if finalchance > 97:
                combatscore = 0.1
        elif hitchance > 10 and hitchance <= 20:
            combatscore = 0.1
        elif hitchance > 20 and hitchance <= 40:
            combatscore = 0.5
        elif hitchance > 40 and hitchance <= 80:
            combatscore = 1
        elif hitchance > 80:
            combatscore = 1.5
        leaderdmgbonus = 0
        if who.leader is not None: leaderdmgbonus = who.leader.combat * 10
        if type == 0:  ##melee dmg
            dmg = who.dmg
            """include charge in dmg if charging, ignore charge defense if have ignore trait"""
            if who.charging == True and 29 not in who.trait:
                dmg = round(dmg + (who.charge / 10) - (target.chargedef / 10))
            elif who.charging == True and 29 in who.trait:
                dmg = round(dmg + (who.charge / 10))
            leaderdmg = round((dmg * ((100 - (target.armour * ((100 - who.penetrate) / 100))) / 100) * combatscore) / 5)
            dmg = round(((leaderdmg * who.troopnumber) + leaderdmgbonus)/5)
            if target.state in (1, 2, 3, 4, 5, 6, 7, 8, 9): dmg = dmg * 5
        elif type == 1:  ##range dmg
            leaderdmg = round(who.rangedmg * ((100 - (target.armour * ((100 - who.rangepenetrate) / 100))) / 100) * combatscore)
            dmg = round((leaderdmg * who.troopnumber) + leaderdmgbonus)
        if (21 in who.trait and target.type in (1, 2)) or (23 in who.trait and target.type in (4, 5, 6, 7)):  ## Anti trait dmg bonus
            dmg = dmg * 1.25
        if dmg > target.unithealth:
            dmg = target.unithealth
        moraledmg = round(dmg / 100)
        return dmg, moraledmg, leaderdmg

    def applystatustoenemy(self, inflictstatus, receiver, attackerside):
        for status in inflictstatus.items():
            if status[1] == 1 and attackerside == 0:
                receiver.statuseffect[status[0]] = self.gameunitstat.statuslist[status[0]].copy()
            elif status[1] in (2, 3):
                receiver.statuseffect[status[0]] = self.gameunitstat.statuslist[status[0]].copy()
                if status[1] == 3:
                    for squad in receiver.nearbysquadlist[0:2]:
                        if squad != 0:
                            squad.statuseffect[status[0]] = self.gameunitstat.statuslist[status[0]].copy()
            elif status[1] == 4:
                for squad in receiver.battalion.spritearray.flat:
                    if squad.state != 100:
                        squad.statuseffect[status[0]] = self.gameunitstat.statuslist[status[0]].copy()

    def dmgcal(self, who, target, whoside, targetside):
        """target position 0 = Front, 1 = Side, 3 = Rear, whoside and targetside is the side attacking and defending respectively"""
        # print(target.gameid, target.battleside)
        wholuck = random.randint(-50, 50)
        targetluck = random.randint(-50, 50)
        whopercent = self.battlesidecal[whoside]
        """34 battlemaster no flanked penalty"""
        if 34 in who.trait or 91 in who.statuseffect: whopercent = 1
        targetpercent = self.battlesidecal[targetside]
        if 34 in target.trait or 91 in target.statuseffect: targetpercent = 1
        dmgeffect = who.frontdmgeffect
        targetdmgeffect = target.frontdmgeffect
        if whoside != 0 and whopercent != 1:  ## if attack or defend from side will use discipline to help reduce penalty a bit
            whopercent = self.battlesidecal[whoside] + (who.discipline / 300)
            dmgeffect = who.sidedmgeffect
            if whopercent > 1: whopercent = 1
        if targetside != 0 and targetpercent != 1:
            targetpercent = self.battlesidecal[targetside] + (target.discipline / 300)
            targetdmgeffect = target.sidedmgeffect
            if targetpercent > 1: targetpercent = 1
        whohit, whodefense = float(who.attack * whopercent) + wholuck, float(who.meleedef * whopercent) + wholuck
        """33 backstabber ignore def when atk rear, 55 Oblivious To Unexpected can't def from rear"""
        if (33 in target.trait and whoside == 2) or (55 in who.trait and whoside == 2) or (47 in who.trait and targetside in (1, 3)): whodefense = 0
        targethit, targetdefense = float(who.attack * targetpercent) + targetluck, float(target.meleedef * targetpercent) + targetluck
        if (33 in who.trait and targetside == 2) or (55 in target.trait and targetside == 2) or (
                47 in target.trait and whoside in (1, 3)): targetdefense = 0
        whodmg, whomoraledmg, wholeaderdmg = self.losscal(who, target, whohit, targetdefense, 0)
        targetdmg, targetmoraledmg, targetleaderdmg = self.losscal(target, who, targethit, whodefense, 0)
        who.unithealth -= round(targetdmg * (dmgeffect / 100))
        who.basemorale -= round(targetmoraledmg * (dmgeffect / 100))
        if target.elemrange not in (0, 5):  ## apply element effect if atk has element
            who.elemcount[target.elemrange - 1] += round((targetdmg * (dmgeffect / 100)) / 100 * who.elemresist[target.elemrange - 1])
        target.basemorale += round((targetmoraledmg * (dmgeffect / 100) / 2))
        if who.leader is not None and who.leader.health > 0 and random.randint(0, 10) > 5:  ## dmg on who leader
            who.leader.health -= targetleaderdmg
            if who.leader.health <= 0 and who.leader.battalion.commander == True and who.leader.armyposition == 0:  ## reduce morale to whole army if commander die from the dmg (leader die cal is in gameleader.py)
                whicharmy = self.enemyarmy
                if who.battalion.gameid < 2000:
                    whicharmy = self.playerarmy
                for army in whicharmy:
                    for squad in army.squadsprite:
                        squad.basemorale -= 20
        target.unithealth -= round(whodmg * (targetdmgeffect / 100))
        target.basemorale -= round(whomoraledmg * (targetdmgeffect / 100))
        if who.elemrange not in (0, 5):  ## apply element effect if atk has element
            target.elemcount[who.elemrange - 1] += round(whodmg * (targetdmgeffect / 100) / 100 * target.elemresist[who.elemrange - 1])
        who.basemorale += round((whomoraledmg * (targetdmgeffect / 100) / 2))
        if target.leader is not None and target.leader.health > 0 and random.randint(0, 10) > 5:  ## dmg on target leader
            target.leader.health -= wholeaderdmg
            if target.leader.health <= 0 and target.leader.battalion.commander == True and target.leader.armyposition == 0:  ## reduce morale to whole army if commander die from the dmg
                whicharmy = self.enemyarmy
                if target.battalion.gameid < 2000:
                    whicharmy = self.playerarmy
                for army in whicharmy:
                    for squad in army.squadsprite:
                        squad.basemorale -= 30
        if who.corneratk == True:  ##attack corner (side) of self with aoe attack
            listloop = target.nearbysquadlist[2:4]
            if targetside in (0, 2): listloop = target.nearbysquadlist[0:2]
            for squad in listloop:
                if squad != 0 and squad.state != 100:
                    targethit, targetdefense = float(who.attack * targetpercent) + targetluck, float(squad.meleedef * targetpercent) + targetluck
                    whodmg, whomoraledmg = self.losscal(who, squad, whohit, targetdefense, 0)
                    squad.unithealth -= round(whodmg * (dmgeffect / 100))
                    squad.basemorale -= whomoraledmg
        """inflict status based on aoe 1 = front only 2 = all 4 side, 3 corner enemy unit, 4 entire battalion"""
        if who.inflictstatus != {}:
            self.applystatustoenemy(who.inflictstatus, target, whoside)
        if target.inflictstatus != {}:
            self.applystatustoenemy(target.inflictstatus, who, targetside)

    def splitunit(self, who, how):
        """split battalion either by row or column into two seperate battalion"""
        if how == 0:  ## split by row
            newarmysquad = np.array_split(who.armysquad, 2)[1]
            who.armysquad = np.array_split(who.armysquad, 2)[0]
            who.squadalive = np.array_split(who.squadalive, 2)[0]
            newpos = who.allsidepos[3] - ((who.allsidepos[3] - who.basepos) / 2)
            who.basepos = who.allsidepos[0] - ((who.allsidepos[0] - who.basepos) / 2)
        else:  ## split by column
            newarmysquad = np.array_split(who.armysquad, 2, axis=1)[1]
            who.armysquad = np.array_split(who.armysquad, 2, axis=1)[0] 
            who.squadalive = np.array_split(who.squadalive, 2, axis=1)[0]
            newpos = who.allsidepos[2] - ((who.allsidepos[2] - who.basepos) / 2)
            who.basepos = who.allsidepos[1] - ((who.allsidepos[1] - who.basepos) / 2)
        if who.leader[1].squad.gameid not in newarmysquad:  ## move leader if squad not in new one
            if who.leader[1].squad.unittype in (1, 3, 5, 6, 7, 10, 11):  ## if squad type melee move to front
                leaderreplace = [np.where(who.armysquad == who.leader[1].squad.gameid)[0][0],
                                 np.where(who.armysquad == who.leader[1].squad.gameid)[1][0]]
                leaderreplaceflat = np.where(who.armysquad.flat == who.leader[1].squad.gameid)[0]
                who.armysquad[leaderreplace[0]][leaderreplace[1]] = newarmysquad[0][int(len(newarmysquad[0]) / 2)]
                newarmysquad[0][int(len(newarmysquad[0]) / 2)] = who.leader[1].squad.gameid
            else:  ## if not move to center of battalion
                leaderreplace = [np.where(who.armysquad == who.leader[1].squad.gameid)[0][0],
                                 np.where(who.armysquad == who.leader[1].squad.gameid)[1][0]]
                leaderreplaceflat = np.where(who.armysquad.flat == who.leader[1].squad.gameid)[0]
                who.armysquad[leaderreplace[0]][leaderreplace[1]] = newarmysquad[int(len(newarmysquad) / 2)][int(len(newarmysquad[0]) / 2)]
                newarmysquad[int(len(newarmysquad) / 2)][int(len(newarmysquad[0]) / 2)] = who.leader[1].squad.gameid
            who.squadalive[leaderreplace[0]][leaderreplace[1]] = \
            [0 if who.armysquad[leaderreplace[0]][leaderreplace[1]] == 0 else 1 if who.squadsprite[leaderreplaceflat[0]].state == 100 else 2][0]
        squadsprite = [squad for squad in who.squadsprite if squad.gameid in newarmysquad]  ## list of sprite not sorted yet
        newsquadsprite = []
        for squadindex in newarmysquad.flat:  ## sort so the new leader squad position match what set before
            for squad in squadsprite:
                if squad.gameid == squadindex:
                    newsquadsprite.append(squad)
                    break
        who.squadsprite = [squad for squad in who.squadsprite if squad.gameid in who.armysquad]
        for thissprite in (who.squadsprite, newsquadsprite):  ## reset position in inspectui for both battalion
            width, height = 0, 0
            squadnum = 0
            for squad in thissprite:
                width += self.imagewidth
                if squadnum >= len(who.armysquad[0]):
                    width = 0
                    width += self.imagewidth
                    height += self.imageheight
                    squadnum = 0
                squad.inspposition = (width + self.inspectuipos[0], height + self.inspectuipos[1])
                squad.rect = squad.image.get_rect(topleft=squad.inspposition)
                squad.pos = pygame.Vector2(squad.rect.centerx, squad.rect.centery)
                squadnum += 1
        newleader = [who.leader[1], gameleader.leader(0, 0, 1, who, self.allleader), gameleader.leader(0, 0, 2, who, self.allleader),
                     gameleader.leader(0, 0, 3, who, self.allleader)]
        who.leader = [who.leader[0], who.leader[2], who.leader[3], gameleader.leader(0, 0, 3, who, self.allleader)]
        for index, leader in enumerate(who.leader):  ## also change army position of all leader in that battalion
            leader.armyposition = index  ## change army position to new one
            leader.imgposition = leader.baseimgposition[leader.armyposition]
            leader.rect = leader.image.get_rect(center=leader.imgposition)
        coa = who.coa
        who.recreatesprite()
        who.makeallsidepos()
        who.setuparmy()
        who.setupfrontline()
        who.viewmode = self.camerascale
        who.changescale()
        who.height = who.gamemapheight.getheight(who.basepos)
        for thishitbox in who.hitbox: thishitbox.kill()
        who.hitbox = [gamebattalion.hitbox(who, 0, who.rect.width-10, 1),
                      gamebattalion.hitbox(who, 1, 1, who.rect.height - 10),
                      gamebattalion.hitbox(who, 2, 1, who.rect.height - 10),
                      gamebattalion.hitbox(who, 3, who.rect.width-10, 1)]
        who.rotate()
        who.newangle = who.angle
        ## need to recal max stat again for the original battalion
        maxhealth = []
        maxstamina = []
        maxmorale = []
        for squad in who.squadsprite:
            maxhealth.append(squad.maxtroop)
            maxstamina.append(squad.maxstamina)
            maxmorale.append(squad.maxmorale)
        maxhealth = sum(maxhealth)
        maxstamina = sum(maxstamina) / len(maxstamina)
        maxmorale = sum(maxmorale) / len(maxmorale)
        who.maxhealth, who.health75, who.health50, who.health25, = maxhealth, round(maxhealth * 75 / 100), round(
            maxhealth * 50 / 100), round(maxhealth * 25 / 100)
        who.maxstamina, who.stamina75, who.stamina50, who.stamina25, = maxstamina, round(maxstamina * 75 / 100), round(
            maxstamina * 50 / 100), round(maxstamina * 25 / 100)
        who.maxmorale = maxmorale
        ## start making new battalion
        if who.gameid < 2000:
            playercommand = True
            newgameid = self.playerarmy[-1].gameid + 1
            colour = (144, 167, 255)
            army = gamebattalion.unitarmy(startposition=newpos, gameid=newgameid,
                                          squadlist=newarmysquad, imgsize=(self.imagewidth, self.imageheight),
                                          colour=colour, control=playercommand, coa=coa, commander=False)
            self.playerarmy.append(army)
        else:
            playercommand = self.enactment
            newgameid = self.enemyarmy[-1].gameid + 1
            colour = (255, 114, 114)
            army = gamebattalion.unitarmy(startposition=newpos, gameid=newgameid,
                                          squadlist=newarmysquad, imgsize=(self.imagewidth, self.imageheight),
                                          colour=colour, control=playercommand, coa=coa, commander=False, startangle=who.angle)
            self.enemyarmy.append(army)
        army.leader = newleader
        army.squadsprite = newsquadsprite
        for squad in army.squadsprite:
            squad.battalion = army
        for index, leader in enumerate(army.leader):  ## change army position of all leader in new battalion
            if how == 0:
                leader.squadpos -= newarmysquad.size  ## just minus the row gone to find new position
            else:
                for index, squad in enumerate(army.squadsprite):  ## loop to find new squad pos based on new squadsprite list
                    if squad.gameid == leader.squad.gameid:
                        leader.squadpos = index
                    break
            leader.battalion = army  ## set leader battalion to new one
            leader.armyposition = index  ## change army position to new one
            leader.imgposition = leader.baseimgposition[leader.armyposition]  ## change image pos
            leader.rect = leader.image.get_rect(center=leader.imgposition)
            leader.poschangestat(leader)  ## change stat based on new army position
        army.commandbuff = [(army.leader[0].meleecommand - 5) * 0.1, (army.leader[0].rangecommand - 5) * 0.1, (army.leader[0].cavcommand - 5) * 0.1]
        army.leadersocial = army.leader[0].social
        army.authrecal()
        self.allunitlist.append(army)
        army.newangle = army.angle
        army.rotate()
        army.viewmode = self.camerascale
        army.changescale()
        army.makeallsidepos()
        army.terrain, army.feature = army.getfeature(army.basepos, army.gamemap)
        army.sidefeature = [army.getfeature(army.allsidepos[0], army.gamemap), army.getfeature(army.allsidepos[1], army.gamemap),
                            army.getfeature(army.allsidepos[2], army.gamemap), army.getfeature(army.allsidepos[3], army.gamemap)]
        army.hitbox = [gamebattalion.hitbox(army, 0, army.rect.width, 1),
                       gamebattalion.hitbox(army, 1, 1, army.rect.height - 5),
                       gamebattalion.hitbox(army, 2, 1, army.rect.height - 5),
                       gamebattalion.hitbox(army, 3, army.rect.width, 1)]
        army.autosquadplace = False

    def changefaction(self, who):
        """Change army group and gameid when change side"""
        oldgroup = self.enemyarmy
        newgroup = self.playerarmy
        oldposlist = self.enemyposlist
        who.colour = (144, 167, 255)
        who.control = True
        if who.gameid < 2000:
            oldgroup = self.playerarmy
            newgroup = self.enemyarmy
            oldposlist = self.playerposlist
            who.colour = (255, 114, 114)
            if self.enactment == False:
                who.control = False
        newgameid = newgroup[-1].gameid + 1
        oldgroup.remove(who)
        newgroup.append(who)
        oldposlist.pop(who.gameid)
        self.allunitindex = [newgameid if index == who.gameid else index for index in self.allunitindex]
        who.gameid = newgameid
        who.recreatesprite()

    def die(self, who, group, deadgroup, rendergroup, hitboxgroup):
        """remove battalion,hitbox when it dies"""
        self.deadindex += 1
        if who.commander == True:  ## more morale penalty if the battalion is a command battalion
            for army in group:
                for squad in army.squadsprite:
                    squad.basemorale -= 30
        for hitbox in who.hitbox:
            rendergroup.remove(hitbox)
            hitboxgroup.remove(hitbox)
            hitbox.kill()
        group.remove(who)
        deadgroup.add(who)
        rendergroup.change_layer(sprite=who, new_layer=1)
        who.gotkilled = 1

    def checksplit(self, whoinput):
        if np.array_split(whoinput.armysquad, 2, axis=1)[0].size >= 10 and np.array_split(whoinput.armysquad, 2, axis=1)[1].size >= 10 and \
                whoinput.leader[1].name != "None":
            self.allui.add(self.buttonui[5])
        elif self.buttonui[5] in self.allui:
            self.buttonui[5].kill()
        if np.array_split(whoinput.armysquad, 2)[0].size >= 10 and np.array_split(whoinput.armysquad, 2)[1].size >= 10 and whoinput.leader[
            1].name != "None":
            self.allui.add(self.buttonui[6])
        elif self.buttonui[6] in self.allui:
            self.buttonui[6].kill()

    def uimouseover(self):
        for ui in self.gameui:
            if ui in self.allui and ui.rect.collidepoint(self.mousepos):
                if ui.uitype not in ("unitcard", 'armybox'):
                    self.clickcheck = 1
                    self.uicheck = 1  ## for avoiding clicking unit under ui
                    break
                else:
                    if self.inspectui == 1:
                        self.clickcheck = 1
                        self.uicheck = 1
                        break
        return self.clickcheck

    def buttonmouseover(self):
        for button in self.buttonui:
            if button in self.allui and button.rect.collidepoint(self.mousepos):
                self.clickcheck = 1
                self.uicheck = 1  ## for avoiding clicking unit under ui
                break
        return self.clickcheck

    def leadermouseover(self):
        leadermouseover = False
        for leader in self.leadernow:
            if leader.rect.collidepoint(self.mousepos):
                self.leaderpopup.pop(self.mousepos, leader.name)
                self.allui.add(self.leaderpopup)
                leadermouseover = True
                break
        return leadermouseover

    def rungame(self):
        self.gamestate = 1
        self.clickcheck = 0  ## For checking if unit or ui is clicked
        self.clickcheck2 = 0  ##  For checking if another unit is clicked when inspect ui open"
        self.inspectui = 0
        self.lastselected = None
        self.mapviewmode = 0
        self.mapshown = self.showmap
        self.squadlastselected = None
        self.beforeselected = None
        self.splithappen = False
        self.splitbutton = False
        self.leadernow = []
        self.rightcorner = SCREENRECT.width - 5
        self.bottomcorner = SCREENRECT.height - 5
        self.centerscreen = [SCREENRECT.width / 2, SCREENRECT.height / 2]
        self.battlemousepos = [0,0]
        while True:
            self.fpscount.fpsshow(self.clock)
            keypress = None
            self.mousepos = pygame.mouse.get_pos()
            mouse_up = False
            mouse_right = False
            double_mouse_right = False
            keystate = pygame.key.get_pressed()
            if keystate[K_s] or self.mousepos[1] >= self.bottomcorner: ## down
                self.basecamerapos[1] += 5 * abs(11- self.camerascale)
                self.camerapos[1] = self.basecamerapos[1] * self.camerascale
            elif keystate[K_w] or self.mousepos[1] <= 5: ## up
                self.basecamerapos[1] -= 5 * abs(11- self.camerascale)
                self.camerapos[1] = self.basecamerapos[1] * self.camerascale
            if keystate[K_a] or self.mousepos[0] <= 5: ## left
                self.basecamerapos[0] -= 5 * abs(11- self.camerascale)
                self.camerapos[0] = self.basecamerapos[0] * self.camerascale
            elif keystate[K_d] or self.mousepos[0] >= self.rightcorner: ## right
                self.basecamerapos[0] += 5 * abs(11- self.camerascale)
                self.camerapos[0] = self.basecamerapos[0] * self.camerascale
            if self.camerapos[0] > self.mapshown.image.get_width(): self.camerapos[0] = self.mapshown.image.get_width()
            elif self.camerapos[0] < 0: self.camerapos[0] = 0
            if self.camerapos[1] > self.mapshown.image.get_height(): self.camerapos[1] = self.mapshown.image.get_height()
            elif self.camerapos[1] < 0: self.camerapos[1] = 0
            if self.basecamerapos[0] > 1000:
                self.basecamerapos[0] = 1000
            elif self.basecamerapos[0] < 0:
                self.basecamerapos[0] = 0
            if self.basecamerapos[1] > 1000:
                self.basecamerapos[1] = 1000
            elif self.basecamerapos[1] < 0:
                self.basecamerapos[1] = 0
            self.cameraupcorner = (self.camerapos[0] - self.centerscreen[0], self.camerapos[1] - self.centerscreen[1])
            self.battlemousepos[0] = pygame.Vector2((self.mousepos[0] - self.centerscreen[0]) + self.camerapos[0],
                                                  self.mousepos[1] - self.centerscreen[1] + self.camerapos[1])
            self.battlemousepos[1] = self.battlemousepos[0] / self.camerascale
            for event in pygame.event.get():  ## get event input
                if event.type == QUIT or \
                        (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.allui.clear(self.screen, self.background)
                    self.allcamera.clear(self.screen, self.background)
                    return
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  ## left click
                        mouse_up = True
                    elif event.button == 3:  ## Right Click
                        mouse_right = True
                        if self.timer == 0:
                            self.timer = 0.001  ##Start timer after first mouse click
                        elif self.timer < 0.3:
                            double_mouse_right = True
                            self.timer = 0
                    elif event.button == 4:
                        self.camerascale += 1
                        if self.camerascale > 10: self.camerascale = 10
                        else:
                            self.camerapos[0] = self.basecamerapos[0] *  self.camerascale
                            self.camerapos[1] = self.basecamerapos[1] *  self.camerascale
                            self.mapshown.changescale(self.camerascale)
                    elif event.button == 5:
                        self.camerascale -= 1
                        if self.camerascale < 1: self.camerascale = 1
                        else:
                            self.camerapos[0] = self.basecamerapos[0] *  self.camerascale
                            self.camerapos[1] = self.basecamerapos[1] *  self.camerascale
                            self.mapshown.changescale(self.camerascale)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        if self.mapviewmode == 0: ## Currently in normal mode
                            self.mapviewmode = 1
                            self.showmap.changemode(self.mapviewmode)
                        else: ## Currently in height mode
                            self.mapviewmode = 0
                            self.showmap.changemode(self.mapviewmode)
                        self.mapshown.changescale(self.camerascale)
                    if event.key == pygame.K_p:  ## Pause Button
                        if self.gamestate == 1:
                            self.gamestate = 0
                        else:
                            self.gamestate = 1
                    elif event.key == pygame.K_SPACE and self.lastselected is not None:
                        whoinput.command(self.battlemousepos, mouse_up, mouse_right, double_mouse_right,
                                        self.lastmouseover, self.enemyposlist, keystate, othercommand=1)
                    elif event.key == pygame.K_q and self.lastselected is not None:
                        self.changefaction(whoinput)
                    elif event.key == pygame.K_l and self.lastselected is not None:
                        for squad in whoinput.squadsprite:
                            squad.basemorale = 0
                    else:
                        keypress = event.key
                if event.type == self.SONG_END:
                    # pygame.mixer.music.unload()
                    self.pickmusic = random.randint(1, 1)
                    pygame.mixer.music.load(self.musiclist[self.pickmusic])
                    pygame.mixer.music.play(0)
            if self.timer != 0:
                self.timer += self.dt
                if self.timer >= 0.5:
                    self.timer = 0
            self.allui.clear(self.screen, self.background)  ##clear sprite before update new one
            self.uiupdater.update()  # update ui outside of combat loop so it update even when game pause
            # self.mapupdater.update(self.dt,self.camerapos,self.camerascale)
            # self.screen.blit(self.background, self.camerapos)
            self.lastmouseover = 0
            if self.terraincheck in self.allui and (self.terraincheck.pos != self.mousepos or keystate[K_s] or keystate[K_w] or keystate[K_a] or keystate[K_d]):
                self.allui.remove(self.terraincheck)
            if mouse_up or mouse_right:
                self.uicheck = 0
                if mouse_up:
                    self.clickcheck = 0
                    self.clickcheck2 = 0
                if self.minimap.rect.collidepoint(self.mousepos):
                    if mouse_up:
                        posmask = pygame.Vector2(int(self.mousepos[0] - self.minimap.rect.x), int(self.mousepos[1] - self.minimap.rect.y))
                        self.basecamerapos = posmask * 5
                        self.camerapos = self.basecamerapos * self.camerascale
                        self.clickcheck = 1
                    elif  mouse_right and self.lastselected is not None:
                        self.uicheck = 1
                    elif mouse_right and self.lastselected is None:
                        pass
                elif self.uimouseover() == 1:
                    pass
                elif self.buttonmouseover() == 1:
                    pass
                elif mouse_right and self.lastselected is None and self.uicheck != 1:
                    terrainpop, featurepop = self.battlemapfeature.getfeature(self.battlemousepos[1], self.battlemap)
                    featurepop = self.battlemapfeature.featuremod[featurepop]
                    self.terraincheck.pop(self.mousepos, featurepop)
                    self.allui.add(self.terraincheck)
            for army in self.allunitlist:
                if army.gameid < 2000:
                    self.playerposlist[army.gameid] = army.basepos
                else:
                    self.enemyposlist[army.gameid] = army.basepos
                if army.rect.collidepoint(self.battlemousepos[0]):
                    posmask = int(self.battlemousepos[0][0] - army.rect.x), int(self.battlemousepos[0][1] - army.rect.y)
                    try:
                        if army.mask.get_at(posmask) == 1:
                            army.mouse_over = True
                            self.lastmouseover = army
                            if mouse_up and self.uicheck == 0:
                                self.lastselected = army
                                self.clickcheck = 1
                    except:
                        army.mouse_over = False
                else:
                    army.mouse_over = False
                if army.changefaction == True:  ## change side via surrender or betrayal
                    self.changefaction(army)
                    army.changefaction = False
                if army.state == 100 and army.gotkilled == 0:
                    if army.gameid < 2000:
                        self.die(army, self.playerarmy, self.deadunit, self.allcamera, self.hitboxs)
                        for thisarmy in self.enemyarmy:  ## get bonus authority when destroy enemy battalion
                            thisarmy.authority += 5
                        for thisarmy in self.playerarmy:  ## morale dmg to every squad in army when allied battalion destroyed
                            for squad in thisarmy.squadsprite:
                                squad.basemorale -= 20
                    else:
                        self.die(army, self.enemyarmy, self.deadunit, self.allcamera, self.hitboxs)
                        for thisarmy in self.playerarmy:  ## get bonus authority when destroy enemy battalion
                            thisarmy.authority += 5
                        for thisarmy in self.enemyarmy:  ## morale dmg to every squad in army when allied battalion destroyed
                            for squad in thisarmy.squadsprite:
                                squad.basemorale -= 20
            if self.lastselected is not None and self.lastselected.state != 100:
                """if not found in army class then it is in dead class"""
                whoinput = self.lastselected
                if (mouse_up or mouse_right) and self.uicheck == 0:
                    whoinput.command(self.battlemousepos, mouse_up, mouse_right, double_mouse_right,
                                     self.lastmouseover, self.enemyposlist, keystate)
                    # if whoinput.target != whoinput.pos and whoinput.rotateonly == False and whoinput.moverotate == 0 and whoinput.directionarrow == False:
                    #     gamebattalion.directionarrow(whoinput)
                if self.beforeselected == 0:  ## add back the pop up ui to group so it get shown when click unit with none selected before
                    self.gameui = self.popgameui
                    self.allui.add(*self.gameui[0:2])  ## add leader and top ui
                    self.allui.add(self.buttonui[4])  ## add inspection ui open/close button
                    self.allui.add(self.buttonui[7])  ## add decimation button
                    self.allui.add(*self.switchbuttonui[0:4])  ## add skill condition change, fire at will buttons
                    self.switchbuttonui[0].event = whoinput.useskillcond
                    self.switchbuttonui[1].event = whoinput.fireatwill
                    self.switchbuttonui[2].event = whoinput.hold
                    self.switchbuttonui[3].event = whoinput.useminrange
                    self.leadernow = whoinput.leader
                    self.allui.add(*self.leadernow)
                    if np.array_split(whoinput.armysquad, 2, axis=1)[0].size >= 10 and np.array_split(whoinput.armysquad, 2, axis=1)[1].size >= 10 and \
                            whoinput.leader[0].name != "None":
                        self.allui.add(self.buttonui[5])  ## add column split button
                    if np.array_split(whoinput.armysquad, 2)[0].size >= 10 and np.array_split(whoinput.armysquad, 2)[1].size >= 10 and \
                            whoinput.leader[0].name != "None":
                        self.allui.add(self.buttonui[6])  ## add row split button
                elif self.beforeselected != self.lastselected:  ## change ui when click other battalion
                    if self.inspectui == 1:
                        self.clickcheck2 = 1
                        self.allui.remove(*self.showingsquad)
                        self.showingsquad = []
                    self.checksplit(whoinput)
                    self.allui.remove(*self.leadernow)
                    self.switchbuttonui[0].event = whoinput.useskillcond
                    self.switchbuttonui[1].event = whoinput.fireatwill
                    self.switchbuttonui[2].event = whoinput.hold
                    self.switchbuttonui[3].event = whoinput.useminrange
                    self.leadernow = whoinput.leader
                    self.allui.add(*self.leadernow)
                self.gameui[0].valueinput(who=whoinput, leader=self.allleader, splithappen=self.splithappen)
                self.gameui[1].valueinput(who=whoinput, leader=self.allleader, splithappen=self.splithappen)
                self.splithappen = False
                if self.buttonui[4].rect.collidepoint(self.mousepos) or (
                        mouse_up and self.inspectui == 1 and self.clickcheck2 == 1):
                    if self.buttonui[4].rect.collidepoint(self.mousepos):
                        self.buttonnamepopup.pop(self.mousepos, "Inspect Squad")
                        self.allui.add(self.buttonnamepopup)
                    if (mouse_up and self.inspectui == 0) or (
                            mouse_up and self.inspectui == 1 and self.clickcheck2 == 1):  ## Add army inspect ui when left click at ui button or when change unit with inspect open
                        self.inspectui = 1
                        self.allui.add(*self.gameui[2:4])
                        self.allui.add(*self.buttonui[0:4])
                        self.showingsquad = whoinput.squadsprite
                        self.squadlastselected = self.showingsquad[0]
                        self.squadselectedborder.pop(self.showingsquad[0].inspposition)
                        self.allui.add(self.squadselectedborder)
                    elif mouse_up == True and self.inspectui == 1:  ## Remove when click again and the ui already open
                        self.allui.remove(*self.showingsquad)
                        self.allui.remove(self.squadselectedborder)
                        self.showingsquad = []
                        for ui in self.gameui[2:4]: ui.kill()
                        for button in self.buttonui[0:4]: button.kill()
                        self.inspectui = 0
                        self.clickcheck2 = 0
                elif self.switchbuttonui[0].rect.collidepoint(self.mousepos) or keypress == pygame.K_g:
                    if mouse_up == True or keypress == pygame.K_g:  ## rotate skill condition when clicked
                        whoinput.useskillcond += 1
                        if whoinput.useskillcond > 3:
                            whoinput.useskillcond = 0
                        self.switchbuttonui[0].event = whoinput.useskillcond
                    if self.switchbuttonui[0].rect.collidepoint(self.mousepos): ## popup name when mouse over
                        poptext = ("Free Use", "Conserve 50% Stamina", "Conserve 25% stamina", "Forbid Skill")
                        self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[0].event])
                        self.allui.add(self.buttonnamepopup)
                elif self.switchbuttonui[1].rect.collidepoint(self.mousepos) or keypress == pygame.K_f:
                    if mouse_up == True or keypress == pygame.K_f:  ## rotate fire at will condition when clicked
                        whoinput.fireatwill += 1
                        if whoinput.fireatwill > 1:
                            whoinput.fireatwill = 0
                        self.switchbuttonui[1].event = whoinput.fireatwill
                    if self.switchbuttonui[1].rect.collidepoint(self.mousepos): ## popup name when mouse over
                        poptext = ("Fire at will", "Hold fire until order")
                        self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[1].event])
                        self.allui.add(self.buttonnamepopup)
                elif self.switchbuttonui[2].rect.collidepoint(self.mousepos) or keypress == pygame.K_h:
                    if mouse_up == True or keypress == pygame.K_h:  ## rotate hold condition when clicked
                        whoinput.hold += 1
                        if whoinput.hold > 2:
                            whoinput.hold = 0
                        self.switchbuttonui[2].event = whoinput.hold
                    if self.switchbuttonui[2].rect.collidepoint(self.mousepos):  ## popup name when mouse over
                        poptext = ("Aggressive", "Skirmish/Scout", "Hold Ground")
                        self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[2].event])
                        self.allui.add(self.buttonnamepopup)
                elif self.switchbuttonui[3].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                    if mouse_up == True or keypress == pygame.K_j:  ## rotate min range condition when clicked
                        whoinput.useminrange += 1
                        if whoinput.useminrange > 1:
                            whoinput.useminrange = 0
                        self.switchbuttonui[3].event = whoinput.useminrange
                    if self.switchbuttonui[3].rect.collidepoint(self.mousepos):  ## popup name when mouse over
                        poptext = ("Shoot from min range", "Shoot from max range")
                        self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[3].event])
                        self.allui.add(self.buttonnamepopup)
                elif self.buttonui[5] in self.allui and self.buttonui[5].rect.collidepoint(self.mousepos):
                    self.buttonnamepopup.pop(self.mousepos, "Split by middle column")
                    self.allui.add(self.buttonnamepopup)
                    if mouse_up == True and whoinput.basepos.distance_to(list(whoinput.neartarget.values())[0]) > 50:
                        self.splitunit(whoinput, 1)
                        self.splithappen = True
                        self.checksplit(whoinput)
                        self.allui.remove(*self.leadernow)
                        self.leadernow = whoinput.leader
                        self.allui.add(*self.leadernow)
                elif self.buttonui[6] in self.allui and self.buttonui[6].rect.collidepoint(self.mousepos):
                    self.buttonnamepopup.pop(self.mousepos, "Split by middle row")
                    self.allui.add(self.buttonnamepopup)
                    if mouse_up == True and whoinput.basepos.distance_to(list(whoinput.neartarget.values())[0]) > 50:
                        self.splitunit(whoinput, 0)
                        self.splithappen = True
                        self.checksplit(whoinput)
                        self.allui.remove(*self.leadernow)
                        self.leadernow = whoinput.leader
                        self.allui.add(*self.leadernow)
                elif self.buttonui[7].rect.collidepoint(self.mousepos):  ## decimation effect
                    self.buttonnamepopup.pop(self.mousepos, "Decimation")
                    self.allui.add(self.buttonnamepopup)
                    if mouse_up == True and whoinput.state == 0:
                        for squad in whoinput.squadsprite:
                            squad.statuseffect[98] = self.gameunitstat.statuslist[98].copy()
                            squad.unithealth -= round(squad.unithealth * 0.1)
                elif self.gameui[1] in self.allui and self.gameui[1].rect.collidepoint(self.mousepos) and self.leadermouseover() == True:
                    pass
                else:
                    self.allui.remove(self.leaderpopup)
                    self.allui.remove(self.buttonnamepopup) ## remove popup if no mouseover on any button

                if self.inspectui == 1:
                    if self.splithappen == True:  ## change showing squad in inspectui if split happen
                        self.allui.remove(*self.showingsquad)
                        self.showingsquad = whoinput.squadsprite
                        self.allui.add(*self.showingsquad)
                    self.allui.add(*self.showingsquad)
                    if mouse_up == True:  ## Change showing stat to the clicked squad one
                        for squad in self.showingsquad:
                            if squad.rect.collidepoint(self.mousepos) == True:
                                self.clickcheck = 1
                                self.uicheck = 1
                                squad.command(self.battlemousepos, mouse_up, mouse_right, self.squadlastselected.wholastselect)
                                self.squadlastselected = squad
                                self.squadselectedborder.pop(squad.inspposition)
                                self.allui.add(self.squadselectedborder)
                                self.gameui[2].valueinput(who=squad, weaponlist=self.allweapon, armourlist=self.allarmour, leader=self.allleader,
                                                          gameunitstat=self.gameunitstat, splithappen=self.splithappen)
                            for button in self.buttonui:  ## Change unit card option based on button clicking
                                if button.rect.collidepoint(self.mousepos):
                                    self.clickcheck = 1
                                    self.uicheck = 1
                                    if self.gameui[2].option != button.event:
                                        self.gameui[2].option = button.event
                                        self.gameui[2].valueinput(who=squad, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                                  leader=self.allleader, changeoption=1, gameunitstat=self.gameunitstat,
                                                                  splithappen=self.splithappen)
                    if self.squadlastselected is not None:  ## Update value of the clicked squad
                        self.gameui[2].valueinput(who=self.squadlastselected, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                  leader=self.allleader, gameunitstat=self.gameunitstat, splithappen=self.splithappen)
                self.beforeselected = self.lastselected
            """remove the pop up ui when click at no group"""
            if self.clickcheck != 1:
                self.lastselected = None
                for ui in self.gameui: ui.kill()
                for button in self.buttonui: button.kill()
                self.allui.remove(*self.switchbuttonui)
                self.allui.remove(*self.showingsquad)
                self.showingsquad = []
                self.inspectui = 0
                self.beforeselected = 0
                self.allui.remove(*self.leadernow)
                self.squadlastselected = None
                self.allui.remove(self.squadselectedborder)
                self.leadernow = []
            # fight_sound.play()
            """Combat and unit update"""
            for hitbox in self.hitboxs:
                collidelist = pygame.sprite.spritecollide(hitbox, self.hitboxs, dokill=False, collided=pygame.sprite.collide_mask)
                for hitbox2 in collidelist:
                    if hitbox.who.gameid != hitbox2.who.gameid and hitbox.who.gameid < 2000 and hitbox2.who.gameid >= 2000:
                        # if pygame.sprite.collide_mask(hitbox, hitbox2) is not None:
                        hitbox.collide, hitbox2.collide = hitbox2.who.gameid, hitbox.who.gameid
                        """run combatprepare when combat start if army is the attacker"""
                        if hitbox.who.gameid not in hitbox.who.battleside:
                            hitbox.who.battleside[hitbox.side] = hitbox2.who.gameid
                            hitbox2.who.battleside[hitbox2.side] = hitbox.who.gameid
                            """set up army position to the enemyside"""
                            if hitbox.side == 0 and hitbox.who.state in (1, 2, 3, 4, 5, 6) and hitbox.who.combatpreparestate == 0:
                                hitbox.who.combatprepare(hitbox2)
                            elif hitbox2.side == 0 and hitbox2.who.state in (1, 2, 3, 4, 5, 6) and hitbox2.who.combatpreparestate == 0:
                                hitbox2.who.combatprepare(hitbox)
                            for battle in hitbox.who.battleside:
                                if battle != 0:
                                    self.squadcombatcal(hitbox.who, hitbox2.who, hitbox.who.battleside.index(battle),
                                                        hitbox2.who.battleside.index(hitbox.who.gameid))
                        """Rotate army side to the enemyside"""
                        if hitbox.who.combatpreparestate == 1:
                            if hitbox.who.allsidepos != hitbox2.who.allsidepos:
                                hitbox.who.setrotate(settarget=hitbox2.who.pos, instant=True)
                        if hitbox2.who.combatpreparestate == 1:
                            if hitbox.who.allsidepos != hitbox2.who.allsidepos:
                                hitbox2.who.setrotate(settarget=hitbox.who.pos, instant=True)
                    elif hitbox.who.gameid != hitbox2.who.gameid and ((hitbox.who.gameid < 2000 and hitbox2.who.gameid < 2000)
                                                                      or (
                                                                              hitbox.who.gameid >= 2000 and hitbox2.who.gameid >= 2000)):  ##colide battalion in same faction
                        hitbox.collide, hitbox2.collide = hitbox2.who.gameid, hitbox.who.gameid
            """Calculate squad combat dmg"""
            if self.combattimer >= 0.2:
                for thissquad in self.squad:
                    if any(battle > 1 for battle in thissquad.battleside) == True:
                        for index, combat in enumerate(thissquad.battleside):
                            if combat > 1:
                                if thissquad.gameid not in self.squad[np.where(self.squadindexlist == combat)[0][0]].battleside:
                                    thissquad.battleside[index] = -1
                                else:
                                    self.dmgcal(thissquad, self.squad[np.where(self.squadindexlist == combat)[0][0]], index,
                                                self.squad[np.where(self.squadindexlist == combat)[0][0]].battleside.index(thissquad.gameid))
                    if thissquad.state in (11, 12, 13):
                        if type(thissquad.attacktarget) == int and thissquad.attacktarget != 0:
                            thissquad.attacktarget = self.allunitlist[self.allunitindex.index(thissquad.attacktarget)]
                        if thissquad.reloadtime >= thissquad.reload and (
                                (thissquad.attacktarget == 0 and thissquad.attackpos != 0) or (thissquad.attacktarget != 0 and thissquad.attacktarget.state != 100)):
                            rangeattack.arrow(thissquad, thissquad.combatpos.distance_to(thissquad.attackpos), thissquad.range, self.camerascale)
                            thissquad.ammo -= 1
                            thissquad.reloadtime = 0
                        elif thissquad.attacktarget != 0 and thissquad.attacktarget.state == 100:
                            thissquad.battalion.rangecombatcheck, thissquad.battalion.attacktarget = 0, 0
                    self.combattimer = 0
            self.unitupdater.update(self.gameunitstat.statuslist, self.squad, self.dt, self.camerascale, self.playerposlist, self.enemyposlist)
            self.effectupdater.update(self.playerarmy, self.enemyarmy, self.hitboxs, self.squad, self.squadindexlist, self.dt, self.camerascale)
            self.combattimer += self.dt
            self.camera.update(self.camerapos, self.allcamera)
            self.minimap.update(self.camerascale, [self.camerapos, self.cameraupcorner],self.playerposlist,self.enemyposlist)
            self.clock.tick(60)
            self.dt = 0
            if self.gamestate == 1:
                self.dt = self.clock.tick(60) / 1000
            self.screen.blit(self.camera.image, (0,0))
            self.allui.draw(self.screen)  # draw the scene
            # pygame.display.update(dirty)
            pygame.display.flip()
        if pygame.mixer:
            pygame.mixer.music.fadeout(1000)
        pygame.time.wait(1000)
        pygame.quit()


if __name__ == '__main__':
    main = battle()
    main.rungame()
