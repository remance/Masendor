"""next goal: , menu in main game(0.3.1), proper broken retreat after map function (0.4) also skirmish
FIX
add chase in 2.7 change stance
still not sure how collision should work in final (now main problem is when in melee combat and another unit can snuck in with rotate will finalised this after big map update 0.4+)
maybe add state change based on previous command (unit resume attacking if move to attack but get caught in combat with another unit)
Optimise list
remove index and change call to the sprite itself
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
from RTS.script import gamesquad, gamebattalion, gameui, gameleader, rangeattack

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
    army.hitbox = [gamebattalion.hitbox(army, 0, army.rect.width, 5),
                   gamebattalion.hitbox(army, 1, 5, army.rect.height - 5),
                   gamebattalion.hitbox(army, 2, 5, army.rect.height - 5),
                   gamebattalion.hitbox(army, 3, army.rect.width, 5)]
    army.leader = [gameleader.leader(leader[0],leader[4],0,army,leaderstat),
                   gameleader.leader(leader[1],leader[5],1,army,leaderstat),
                   gameleader.leader(leader[2],leader[6],2,army,leaderstat),
                   gameleader.leader(leader[3],leader[7],3,army,leaderstat)]
    return army


def unitsetup(playerarmy, enemyarmy, battle, imagewidth, imageheight, allweapon, allleader, gameunitstat, coa, squad, inspectuipos, enactment=False):
    """squadindexlist is list of every squad index in the game for indexing the squad group"""
    # defaultarmy = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
    squadindexlist = []
    unitlist = []
    playercolour = (144, 167, 255)
    enemycolour = (255, 114, 114)
    """army num is list index for battalion in either player or enemy group"""
    playerarmynum, enemyarmynum, playerstart, enemystart = {}, {}, 0, 0
    """squadindex is list index for all squad group"""
    squadindex = 0
    """firstsquad check if it the first ever in group"""
    squadgameid = 10000
    with open(main_dir + "\data" + "\map" + battle + '.csv', 'r') as unitfile:
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
                                   (imagewidth, imageheight), row[10]+row[11], allleader, gameunitstat, True, coa[row[12]], True, startangle = row[13])
                else:
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   playercolour, (imagewidth, imageheight), row[10]+row[11], allleader, gameunitstat, True, coa[row[12]], startangle = row[13])
                playerarmy.append(army)
                playerarmynum[row[0]] = playerstart
                playerstart += 1
            elif row[0] >= 2000:
                if row[0] == 2000:
                    """First enemy battalion as commander"""
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   enemycolour,
                                   (imagewidth, imageheight), row[10]+row[11], allleader, gameunitstat, enactment, coa[row[12]], True, startangle = row[13])
                elif row[0] > 2000:
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   enemycolour,
                                   (imagewidth, imageheight), row[10]+row[11], allleader, gameunitstat, enactment, coa[row[12]], startangle = row[13])
                enemyarmy.append(army)
                enemyarmynum[row[0]] = enemystart
                enemystart += 1
            """armysquadindex is list index for squad list in a specific army"""
            armysquadindex = 0
            """Setup squad in army to squad group"""
            for squadnum in np.nditer(army.armysquad, op_flags=['readwrite'], order='C'):
                if squadnum != 0:
                    addsquad = gamesquad.unitsquad(unitid=squadnum, gameid=squadgameid, weaponlist=allweapon, statlist=gameunitstat,
                                                   battalion=army, position=army.squadpositionlist[armysquadindex], inspectuipos=inspectuipos)
                    squad.append(addsquad)
                    squadnum[...] = squadgameid
                    army.squadsprite.append(addsquad)
                    squadindexlist.append(squadgameid)
                    squadgameid += 1
                    squadindex += 1
                armysquadindex += 1
    unitfile.close()
    return playerarmynum, enemyarmynum, squadindexlist


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

        # create unit
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
        # create weapon icon
        imgsold = load_images(['war', 'unit_ui', 'weapon'])
        imgs = []
        for img in imgsold:
            x, y = img.get_width(), img.get_height()
            img = pygame.transform.scale(img, (int(x / 1.7), int(y / 1.7)))
            imgs.append(img)
        self.allweapon = gamebattalion.weaponstat(imgs)
        imgsold = load_images(['ui', 'skill_icon'], loadorder=False)
        imgs = []
        for img in imgsold:
            imgs.append(img)
        self.gameunitstat = gamebattalion.unitstat(imgs, imgs, imgs, imgs)
        # create leader list
        imgsold = load_images(['leader', 'historic'])
        imgs = []
        for img in imgsold:
            x, y = img.get_width(), img.get_height()
            img = pygame.transform.scale(img, (int(x / 2), int(y / 2)))
            imgs.append(img)
        self.allleader = gameleader.leaderdata(imgs, option="\historic")
        # coa imagelist
        imgsold = load_images(['leader', 'historic', 'coa'])
        imgs = []
        for img in imgsold:
            imgs.append(img)
        self.coa = imgs
        """Game Effect"""
        imgsold = load_images(['effect'])
        imgs = []
        for img in imgsold:
            x, y = img.get_width(), img.get_height()
            # img = pygame.transform.scale(img, (int(x ), int(y / 2)))
            imgs.append(img)
        self.gameeffect = imgs
        rangeattack.arrow.images = [self.gameeffect[0]]
        # decorate the game window
        # icon = load_image('sword.jpg')
        # icon = pygame.transform.scale(icon, (32, 32))
        # pygame.display.set_icon(icon)
        pygame.display.set_caption('Masendor RTS')
        pygame.mouse.set_visible(1)

        # create the background, tile the bgd image
        bgdtile = load_image('background_tile.png', 'ui')
        self.background = pygame.Surface(SCREENRECT.size)
        # for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        for x in range(0, SCREENRECT.width, bgdtile.get_width()):
            for y in range(0, SCREENRECT.height, bgdtile.get_height()):
                self.background.blit(bgdtile, (x, 0))
                self.background.blit(bgdtile, (x, y))
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
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
        self.all = pygame.sprite.LayeredUpdates()
        self.unitupdater = pygame.sprite.Group()
        self.uiupdater = pygame.sprite.Group()
        self.effectupdater = pygame.sprite.Group()
        self.playerarmy = pygame.sprite.Group()
        self.enemyarmy = pygame.sprite.Group()
        self.squad = pygame.sprite.Group()
        self.armyleader = pygame.sprite.Group()
        self.hitboxs = pygame.sprite.Group()
        self.arrows = pygame.sprite.Group()
        self.directionarrows = pygame.sprite.Group()
        self.deadunit = pygame.sprite.Group()
        self.gameui = pygame.sprite.Group()
        self.buttonui = pygame.sprite.Group()
        self.fpscount = pygame.sprite.Group()
        """assign default groups"""
        gamebattalion.unitarmy.containers = self.playerarmy, self.enemyarmy, self.unitupdater, self.all, self.squad
        gamesquad.unitsquad.containers = self.playerarmy, self.enemyarmy, self.unitupdater, self.squad
        gamebattalion.deadarmy.containers = self.deadunit, self.unitupdater, self.all
        gamebattalion.hitbox.containers = self.hitboxs, self.unitupdater, self.all
        gameleader.leader.containers = self.armyleader, self.unitupdater
        rangeattack.arrow.containers = self.arrows, self.all, self.effectupdater
        gamebattalion.directionarrow.containers = self.directionarrows, self.all, self.effectupdater
        gameui.Gameui.containers = self.gameui, self.uiupdater
        gameui.fpscount.containers = self.all
        gameui.uibutton.containers = self.buttonui, self.uiupdater
        """Create Starting Values"""
        self.enactment = True
        self.timer = 0
        self.dt = 0
        self.combattimer = 0
        self.clock = pygame.time.Clock()
        self.lastmouseover = 0
        self.unitviewmode = 0
        """use same position as squad front index 0 = front, 1 = left, 2 = rear, 3 = right"""
        self.battlesidecal = [1, 0.5, 0.1, 0.5]
        """create game ui"""
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
        self.gameui.append(
            gameui.Gameui(screen=self.screen, X=SCREENRECT.width - topimage[5].get_size()[0] / 2, Y=topimage[0].get_size()[1] + 150,
                          image=topimage[5], icon="", uitype="armybox"))
        self.popgameui = self.gameui
        self.buttonui = [gameui.uibutton(self.gameui[2].X - 170, self.gameui[2].Y + 41, topimage[3], 0),
                         gameui.uibutton(self.gameui[2].X - 170, self.gameui[2].Y - 65, topimage[4], 1),
                         gameui.uibutton(self.gameui[2].X - 170, self.gameui[2].Y - 12, topimage[7], 2),
                         gameui.uibutton(self.gameui[0].X - 206, self.gameui[0].Y, topimage[6], 1),
                         gameui.uibutton(self.gameui[1].X - 50, self.gameui[1].Y+96, topimage[8], 0),
                         gameui.uibutton(self.gameui[1].X - 100, self.gameui[1].Y+96, topimage[9], 1)]
        self.pause_text = pygame.font.SysFont("helvetica", 100).render("PAUSE", 1, (0, 0, 0))
        self.fpscount = gameui.fpscount()
        """initialise starting unit sprites"""
        self.playerarmy, self.enemyarmy, self.squad = [], [], []
        self.playerarmynum, self.enemyarmynum, self.squadindexlist = unitsetup(self.playerarmy, self.enemyarmy, '\\test',
                                                                               self.imagewidth, self.imageheight, self.allweapon, self.allleader,
                                                                               self.gameunitstat, self.coa, self.squad,
                                                                               [self.gameui[0].rect.bottomleft[0] - self.imagewidth / 1.25,
                                                                                self.gameui[0].rect.bottomleft[1] - self.imageheight / 3],
                                                                               enactment=self.enactment)
        self.allunitlist = self.playerarmy.copy()
        self.allunitlist = self.allunitlist + self.enemyarmy
        self.allunitindex = [army.gameid for army in self.allunitlist]
        self.deadarmynum = {}
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
                        if self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[squadside] in [-1, 0]:
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
                            if self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] in [-1, 0]:
                                self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[attackerside] = fronttarget
                                self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] = thiswho
                        else:
                            """Switch to another side if above not found"""
                            truetargetside = self.changeside(secondpick, receiverside)
                            fronttarget = self.squadselectside(receiver.frontline[receiverside], secondpick, position)
                            if fronttarget > 1:
                                if self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] in [-1, 0]:
                                    self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[attackerside] = fronttarget
                                    self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] = thiswho
                            else:
                                self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[receiverside] = 0

    def squadcombatcal(self, who, target, whoside, targetside):
        """calculate squad engagement using information after battalionengage who is player battalion, target is enemy battalion"""
        # print(target.frontline)
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
        if who.leader != None: leaderdmgbonus = who.leader.combat * 10
        if type == 0:  ##melee dmg
            dmg = who.dmg
            """include charge in dmg if charging, ignore charge defense if have ignore trait"""
            if who.charging == True and 29 not in who.trait:
                dmg = round(dmg + (who.charge / 10) - (target.chargedef / 10))
            elif who.charging == True and 29 in who.trait:
                dmg = round(dmg + (who.charge / 10))
            leaderdmg = round(dmg * ((100 - (target.armour * ((100 - who.penetrate) / 100))) / 100) * combatscore)
            dmg = round((leaderdmg * who.troopnumber) + leaderdmgbonus)
        elif type == 1:  ##range dmg
            leaderdmg = round(who.rangedmg * ((100 - (target.armour * ((100 - who.rangepenetrate) / 100))) / 100) * combatscore)
            dmg = round((leaderdmg * who.troopnumber) + leaderdmgbonus)
        """Anti trait dmg bonus"""
        if (21 in who.trait and target.type in [1, 2]) or (23 in who.trait and target.type in [4, 5, 6, 7]):
            dmg = dmg * 1.25
        if dmg > target.unithealth:
            dmg = target.unithealth
        elif dmg <= 0:
            dmg = 1
        moraledmg = round(dmg / 100)
        return dmg, moraledmg, leaderdmg

    def applystatustoenemy(self, inflictstatus, receiver, attackerside):
        for status in inflictstatus.items():
            if status[1] == 1 and attackerside == 0:
                receiver.statuseffect[status[0]] = self.gameunitstat.statuslist[status[0]].copy()
            elif status[1] in [2, 3]:
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
        """if attack or defend from side will use discipline to help reduce penalty"""
        if whoside != 0 and whopercent != 1:
            whopercent = self.battlesidecal[whoside] + (who.discipline / 300)
            dmgeffect = who.sidedmgeffect
            if whopercent > 1: whopercent = 1
        if targetside != 0 and targetpercent != 1:
            targetpercent = self.battlesidecal[targetside] + (target.discipline / 300)
            targetdmgeffect = target.sidedmgeffect
            if targetpercent > 1: targetpercent = 1
        whohit, whodefense = float(who.attack * whopercent) + wholuck, float(who.meleedef * whopercent) + wholuck
        """33 backstabber ignore def when atk rear, 55 Oblivious To Unexpected can't def from rear"""
        if (33 in target.trait and whoside == 2) or (55 in who.trait and whoside == 2) or (47 in who.trait and targetside in [1,3]): whodefense = 0
        targethit, targetdefense = float(who.attack * targetpercent) + targetluck, float(target.meleedef * targetpercent) + targetluck
        if (33 in who.trait and targetside == 2) or (55 in target.trait and targetside == 2) or (47 in target.trait and whoside in [1,3]): targetdefense = 0
        whodmg, whomoraledmg, wholeaderdmg = self.losscal(who, target, whohit, targetdefense, 0)
        targetdmg, targetmoraledmg, targetleaderdmg = self.losscal(target, who, targethit, whodefense, 0)
        who.unithealth -= round(targetdmg * (dmgeffect / 100))
        who.basemorale -= round(targetmoraledmg * (dmgeffect / 100))
        if who.leader != None and who.leader.health > 0 and random.randint(0, 10) > 5:
            who.leader.health -= targetleaderdmg
            if who.leader.health <= 0 and who.leader.battalion.commander == True and who.leader.armyposition == 0: ## reduce morale to whole army if commander die from the dmg
                print('test1', who.leader.name)
                whicharmy = self.enemyarmy
                if who.battalion.gameid < 2000:
                    whicharmy = self.playerarmy
                for army in whicharmy:
                    for squad in army.squadsprite:
                        squad.basemorale -= 20
        target.unithealth -= round(whodmg * (targetdmgeffect / 100))
        target.basemorale -= round(whomoraledmg * (targetdmgeffect / 100))
        if target.leader != None and target.leader.health > 0 and random.randint(0, 10) > 5:
            target.leader.health -= wholeaderdmg
            if target.leader.health <= 0 and target.leader.battalion.commander == True and target.leader.armyposition == 0: ## reduce morale to whole army if commander die from the dmg
                print('test2', target.leader.name)
                whicharmy = self.enemyarmy
                if target.battalion.gameid < 2000:
                    whicharmy = self.playerarmy
                for army in whicharmy:
                    for squad in army.squadsprite:
                        squad.basemorale -= 30
        if who.corneratk == True:  ##attack corner (side) of self with aoe attack
            listloop = target.nearbysquadlist[2:4]
            if targetside in [0, 2]:
                listloop = target.nearbysquadlist[0:2]
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

    def splitunit(self,who,how):
        """split battalion either by row or column into two seperate battalion"""
        if how == 0: ## split by row
            newarmysquad = np.array_split(who.armysquad, 2)[1]
            newsquadsprite = [squad for squad in who.squadsprite if squad.gameid in newarmysquad]
            # newsquadalive = np.array_split(who.squadalive, 2)[1]
            # newpos = who.allsidepos[3] - (self.imageheight * len(who.armysquad)/2)
            who.armysquad = np.array_split(who.armysquad, 2)[0]
            who.squadalive = np.array_split(who.squadalive, 2)[0]
            newpos = who.allsidepos[3] - ((who.allsidepos[3] - who.pos)/2)
            who.pos = who.allsidepos[0] - ((who.allsidepos[0] - who.pos)/2)
        else: ## split by column
            newarmysquad = np.array_split(who.armysquad, 2, axis=1)[1]
            newsquadsprite = [squad for squad in who.squadsprite if squad.gameid in newarmysquad]
            # newsquadalive = np.array_split(who.squadalive, 2, axis=1)[1]
            who.armysquad = np.array_split(who.armysquad, 2, axis=1)[0]
            who.squadalive = np.array_split(who.squadalive, 2, axis=1)[0]
            newpos = who.allsidepos[2] - ((who.allsidepos[2] - who.pos)/2)
            who.pos = who.allsidepos[1] - ((who.allsidepos[1] - who.pos)/2)
        who.squadsprite = [squad for squad in who.squadsprite if squad.gameid in who.armysquad]
        newleader = [who.leader[1],gameleader.leader(0,0,1,who, self.allleader),gameleader.leader(0,0,2,who, self.allleader),gameleader.leader(0,0,3,who, self.allleader)]
        who.leader = [who.leader[0],who.leader[2],who.leader[3],gameleader.leader(0,0,3,who, self.allleader)]
        for index, leader in enumerate(who.leader):  ## also change army position of all leader in that battalion
            leader.armyposition = index  ## change army position to new one
            leader.imgposition = leader.baseimgposition[leader.armyposition]
            leader.rect = leader.image.get_rect(center=leader.imgposition)
        coa = who.coa
        who.recreatesprite()
        who.makeallsidepos()
        who.setuparmy()
        who.setupfrontline()
        for thishitbox in who.hitbox: thishitbox.kill()
        who.hitbox = [gamebattalion.hitbox(who, 0, who.rect.width, 5),
                       gamebattalion.hitbox(who, 1, 5, who.rect.height - 5),
                       gamebattalion.hitbox(who, 2, 5, who.rect.height - 5),
                       gamebattalion.hitbox(who, 3, who.rect.width, 5)]
        who.rotate()
        who.newangle = who.angle - 1
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
            newgameid = self.playerarmy[-1].gameid+1
            colour =  (144, 167, 255)
            army = gamebattalion.unitarmy(startposition=newpos, gameid=newgameid,
                                          squadlist=newarmysquad, imgsize=(self.imagewidth, self.imageheight),
                                          colour=colour, control=playercommand, coa=coa, commander=False)
            self.playerarmy.append(army)
            self.playerarmynum[newgameid] = list(self.playerarmynum.items())[-1][1] + 1
        else:
            playercommand = self.enactment
            newgameid = self.enemyarmy[-1].gameid + 1
            colour = (255, 114, 114)
            army = gamebattalion.unitarmy(startposition=newpos, gameid=newgameid,
                                          squadlist=newarmysquad, imgsize=(self.imagewidth, self.imageheight),
                                          colour=colour, control=playercommand, coa=coa, commander=False, startangle = who.angle)
            self.enemyarmy.append(army)
            self.enemyarmynum[newgameid] = list(self.enemyarmynum.items())[-1][1] + 1
        army.leader = newleader
        army.squadsprite = newsquadsprite
        for squad in army.squadsprite:
            squad.battalion = army
        for index, leader in enumerate(army.leader):  ## change army position of all leader in new battalion
            if how == 0:
                leader.squadpos -= newarmysquad.size ## just minus the row gone to find new position
            else:
                for index, squad in enumerate(army.squadsprite): ## loop to find new squad pos based on new squadsprite list
                    if squad.gameid == leader.squad.gameid:
                        leader.squadpos = index
                    break
            leader.battalion = army ## set leader battalion to new one
            leader.armyposition = index  ## change army position to new one
            leader.imgposition = leader.baseimgposition[leader.armyposition] ## change image pos
            leader.rect = leader.image.get_rect(center=leader.imgposition)
            leader.poschangestat(leader) ## change stat based on new army position
            print(leader.name, leader.battalion.gameid)
        army.commandbuff = [(army.leader[0].meleecommand - 5) * 0.1, (army.leader[0].rangecommand - 5) * 0.1, (army.leader[0].cavcommand - 5) * 0.1]
        army.leadersocial = army.leader[0].social
        army.authrecal()
        self.allunitlist.append(army)
        army.newangle = army.angle - 1
        army.hitbox = [gamebattalion.hitbox(army, 0, army.rect.width, 5),
                   gamebattalion.hitbox(army, 1, 5, army.rect.height - 5),
                   gamebattalion.hitbox(army, 2, 5, army.rect.height - 5),
                   gamebattalion.hitbox(army, 3, army.rect.width, 5)]
        army.rotate()
        army.makeallsidepos()
        army.autosquadplace = False

    def die(self, who, group, deadgroup, rendergroup, hitboxgroup):
        self.deadarmynum[who.gameid] = self.deadindex
        self.deadindex += 1
        for hitbox in who.hitbox:
            rendergroup.remove(hitbox)
            hitboxgroup.remove(hitbox)
        group.remove(who)
        deadgroup.add(who)
        rendergroup.change_layer(sprite=who, new_layer=0)
        who.gotkilled = 1

    def checksplit(self,whoinput):
        if np.array_split(whoinput.armysquad, 2, axis=1)[0].size >= 10 and np.array_split(whoinput.armysquad, 2, axis=1)[1].size >= 10 and \
                whoinput.leader[1].name != "None":
            self.all.add(self.buttonui[4])
        elif self.buttonui[4] in self.all:
            self.buttonui[4].kill()
        if np.array_split(whoinput.armysquad, 2)[0].size >= 10 and np.array_split(whoinput.armysquad, 2)[1].size >= 10 and whoinput.leader[1].name != "None":
            self.all.add(self.buttonui[5])
        elif self.buttonui[5] in self.all:
            self.buttonui[5].kill()

    def rungame(self):
        self.gamestate = 1
        self.check = 0  ## For checking if unit or ui is clicked
        self.check2 = 0  ##  For checking if another unit is clicked when inspect ui open"
        self.inspectui = 0
        self.lastselected = 0
        self.squadlastselected = None
        self.beforeselected = None
        self.squadbeforeselected = None
        self.splithappen = False
        self.splitbutton = False
        self.leadernow = []
        while True:
            self.fpscount.fpsshow(self.clock)
            keystate = pygame.key.get_pressed()
            self.mousepos = pygame.mouse.get_pos()
            mouse_up = False
            mouse_right = False
            double_mouse_right = False
            for event in pygame.event.get():  ## get event input
                if event.type == QUIT or \
                        (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.all.clear(self.screen, self.background)
                    return
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1: ## left click
                    mouse_up = True
                if event.type == pygame.MOUSEBUTTONUP and event.button == 3:  ## Right Click
                    mouse_right = True
                    if self.timer == 0:
                        self.timer = 0.001  ##Start timer after first mouse click
                    elif self.timer < 0.3:
                        double_mouse_right = True
                        self.timer = 0
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        if self.unitviewmode == 1:
                            self.unitviewmode = 0
                        else:
                            self.unitviewmode = 1
                    if event.key == pygame.K_SPACE:  ## Pause Button
                        if self.gamestate == 1:
                            self.gamestate = 0
                        else:
                            self.gamestate = 1
                    if event.key == pygame.K_s and self.lastselected != 0:
                        whoinput.command(pygame.mouse.get_pos(), mouse_up, mouse_right, double_mouse_right,
                                         self.lastselected, self.lastmouseover, self.enemyposlist, keystate, othercommand = 1)
                # if keystate[K_s]:
                #     scroll_view(screen, background, DIR_DOWN, view_rect)
                # elif keystate[K_w]:
                #     scroll_view(screen, background, DIR_UP, view_rect)
                # elif keystate[K_a]:
                #     scroll_view(screen, background, DIR_LEFT, view_rect)
                # elif keystate[K_d]:
                #     scroll_view(screen, background, DIR_RIGHT, view_rect)
                if event.type == self.SONG_END:
                    # pygame.mixer.music.unload()
                    self.pickmusic = random.randint(1, 1)
                    pygame.mixer.music.load(self.musiclist[self.pickmusic])
                    pygame.mixer.music.play(0)
            if self.timer != 0:
                self.timer += self.dt
                if self.timer >= 0.5:
                    self.timer = 0
            self.all.clear(self.screen, self.background)  ##clear sprite before update new one
            self.uiupdater.update()  # update ui outside of combat loop so it update even when game pause
            # directionX = keystate[K_RIGHT] - keystate[K_LEFT]
            # directionY = keystate[K_DOWN] - keystate[K_UP]
            self.lastmouseover = 0
            if mouse_up == True:
                self.check = 0
                self.check2 = 0
                self.uicheck = 0
            for army in self.allunitlist:
                if army.gameid < 2000:
                    self.playerposlist[army.gameid] = army.pos
                else:
                    self.enemyposlist[army.gameid] = army.pos
                posmask = self.mousepos[0] - army.rect.x, self.mousepos[1] - army.rect.y
                #     army.mouse_over = True
                # except: self.mouse_over = False
                for ui in self.gameui:
                    if ui.rect.collidepoint(self.mousepos) and mouse_up:
                        if ui.uitype not in ["unitcard", 'armybox']:
                            self.check = 1
                            self.uicheck = 1 ## for avoiding clicking unit under ui
                        else:
                            if self.inspectui == 1:
                                self.check = 1
                                self.uicheck = 1
                if army.rect.collidepoint(self.mousepos):
                    try:
                        if army.mask.get_at(posmask) == 1:
                            army.mouse_over = True
                            self.lastmouseover = army
                            if mouse_up and self.uicheck == 0:
                                self.lastselected = army.gameid
                                self.check = 1
                    except:
                        army.mouse_over = False
                else:
                    army.mouse_over = False
                if army.state == 100 and army.gotkilled == 0:
                    if army.gameid < 2000:
                        self.die(army, self.playerarmy, self.deadunit, self.all, self.hitboxs)
                        for army in self.enemyarmy:
                            army.authority += 5
                    else:
                        self.die(army, self.enemyarmy, self.deadunit, self.all, self.hitboxs)
                        for army in self.playerarmy:
                            army.authority += 5
                # pygame.draw.aaline(screen, (100, 0, 0), army.pos, army.target, 10)
            if self.lastselected != 0:
                if self.lastselected < 2000:
                    """if not found in army class then it is in dead class"""
                    try:
                        whoinput = self.playerarmy[self.playerarmynum[self.lastselected]]
                    except:
                        lastselected = 0  # whoinput = self.deadunit[self.deadarmynum[self.lastselected]]
                else:
                    try:
                        whoinput = self.enemyarmy[self.enemyarmynum[self.lastselected]]
                    except:
                        lastselected = 0  # whoinput = self.deadunit[self.deadarmynum[self.lastselected]]
                if mouse_up or mouse_right:
                    whoinput.command(pygame.mouse.get_pos(), mouse_up, mouse_right, double_mouse_right,
                                     self.lastselected, self.lastmouseover, self.enemyposlist, keystate)
                    if whoinput.target != whoinput.pos and whoinput.rotateonly == False and whoinput.directionarrow == False:
                        gamebattalion.directionarrow(whoinput)
                if self.beforeselected == 0: ## add back the pop up ui to group so it get shown when click unit with none selected before
                    self.gameui = self.popgameui
                    self.all.add(*self.gameui[0:2])
                    self.all.add(self.buttonui[3])
                    self.leadernow = whoinput.leader
                    self.all.add(*self.leadernow)
                    if np.array_split(whoinput.armysquad, 2, axis=1)[0].size >= 10 and np.array_split(whoinput.armysquad, 2, axis=1)[1].size >= 10 and whoinput.leader[0].name != "None":
                        self.all.add(self.buttonui[4])
                    if np.array_split(whoinput.armysquad, 2)[0].size >= 10 and np.array_split(whoinput.armysquad, 2)[1].size >= 10 and whoinput.leader[0].name != "None":
                        self.all.add(self.buttonui[5])
                elif self.beforeselected != self.lastselected:
                    if self.inspectui == 1:
                        self.check2 = 1
                        self.all.remove(*self.showingsquad)
                        self.showingsquad = []
                    self.checksplit(whoinput)
                    self.all.remove(*self.leadernow)
                    self.leadernow = whoinput.leader
                    self.all.add(*self.leadernow)
                self.gameui[0].valueinput(who=whoinput, leader=self.allleader,splithappen=self.splithappen)
                self.gameui[1].valueinput(who=whoinput, leader=self.allleader,splithappen=self.splithappen)
                self.splithappen = False
                if (self.buttonui[3].rect.collidepoint(pygame.mouse.get_pos()) and mouse_up == True and self.inspectui == 0) or (
                        mouse_up == True and self.inspectui == 1 and self.check2 == 1):
                    """Add army inspect ui when left click at ui button)"""
                    self.inspectui = 1
                    self.all.add(*self.gameui[2:4])
                    self.all.add(*self.buttonui[0:3])
                    self.check = 1
                    self.showingsquad = whoinput.squadsprite
                    self.squadlastselected = self.showingsquad[0]
                elif self.buttonui[3].rect.collidepoint(pygame.mouse.get_pos()) and mouse_up == True and self.inspectui == 1:
                    """remove when click again and the ui already open"""
                    self.all.remove(*self.showingsquad)
                    self.showingsquad = []
                    for ui in self.gameui[2:4]: ui.kill()
                    for button in self.buttonui[0:3]: button.kill()
                    self.inspectui = 0
                    self.check = 1
                    self.check2 = 0
                if self.buttonui[4] in self.all and self.buttonui[4].rect.collidepoint(pygame.mouse.get_pos()) and mouse_up == True:
                    if whoinput.pos.distance_to(list(whoinput.neartarget.values())[0]) > 500:
                        self.splitunit(whoinput,1)
                        self.splithappen = True
                        self.checksplit(whoinput)
                        self.all.remove(*self.leadernow)
                        self.leadernow = whoinput.leader
                        self.all.add(*self.leadernow)
                elif self.buttonui[5] in self.all and self.buttonui[5].rect.collidepoint(pygame.mouse.get_pos()) and mouse_up == True:
                    if whoinput.pos.distance_to(list(whoinput.neartarget.values())[0]) > 500:
                        self.splitunit(whoinput, 0)
                        self.splithappen = True
                        self.checksplit(whoinput)
                        self.all.remove(*self.leadernow)
                        self.leadernow = whoinput.leader
                        self.all.add(*self.leadernow)
                if self.inspectui == 1:
                    if self.splithappen == True: ## change showing squad in inspectui if split happen
                        self.all.remove(*self.showingsquad)
                        self.showingsquad = whoinput.squadsprite
                        self.all.add(*self.showingsquad)
                    self.all.add(*self.showingsquad)
                    """Update value of the clicked squad"""
                    if self.squadlastselected != None:
                        self.gameui[2].valueinput(who=self.squadlastselected, leader=self.allleader, gameunitstat=self.gameunitstat,splithappen=self.splithappen)
                    """Change showing stat to the clicked squad one"""
                    if mouse_up == True:
                        for squad in self.showingsquad:
                            if squad.rect.collidepoint(pygame.mouse.get_pos()) == True:
                                self.check = 1
                                squad.command(pygame.mouse.get_pos(), mouse_up, mouse_right, self.squadlastselected.wholastselect)
                                self.squadlastselected = squad
                                self.gameui[2].valueinput(who=squad, leader=self.allleader, gameunitstat=self.gameunitstat,splithappen=self.splithappen)
                            """Change unit card option based on button clicking"""
                            for button in self.buttonui:
                                if button.rect.collidepoint(pygame.mouse.get_pos()):
                                    self.check = 1
                                    if self.gameui[2].option != button.event:
                                        self.gameui[2].option = button.event
                                        self.gameui[2].valueinput(who=squad, leader=self.allleader, changeoption=1, gameunitstat=self.gameunitstat,splithappen=self.splithappen)
                    self.squadbeforeselected = self.squadlastselected
                self.beforeselected = self.lastselected
            """remove the pop up ui when click at no group"""
            if self.check != 1:
                self.lastselected = 0
                for ui in self.gameui: ui.kill()
                for button in self.buttonui: button.kill()
                self.all.remove(*self.showingsquad)
                self.showingsquad = []
                self.inspectui = 0
                self.squadbeforeselected = 0
                self.beforeselected = 0
                self.all.remove(*self.leadernow)
                self.leadernow = {}
            if self.gamestate == 1:
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
                                if hitbox.side == 0 and hitbox.who.state in [1, 2, 3, 4, 5, 6]:
                                    hitbox.who.combatprepare(hitbox2)
                                    hitbox.who.preparetimer = 0
                                elif hitbox2.side == 0 and hitbox2.who.state in [1, 2, 3, 4, 5, 6]:
                                    hitbox2.who.combatprepare(hitbox)
                                    hitbox2.who.preparetimer = 0
                                for battle in hitbox.who.battleside:
                                    if battle != 0:
                                        self.squadcombatcal(hitbox.who, hitbox2.who, hitbox.who.battleside.index(battle),
                                                            hitbox2.who.battleside.index(hitbox.who.gameid))
                            """Rotate army side to the enemyside"""
                            if hitbox.who.combatpreparestate == 1:
                                if hitbox.who.preparetimer == 0: hitbox.who.preparetimer = 0.1
                                if hitbox.who.preparetimer not in [0,5]:
                                    hitbox.who.preparetimer += self.dt
                                    if hitbox.who.preparetimer < 5:
                                        hitbox.who.setrotate(settarget=hitbox2.who.pos, instant=True)
                                    else:
                                        hitbox.who.preparetimer = 5
                            if hitbox2.who.combatpreparestate == 1:
                                if hitbox2.who.preparetimer == 0: hitbox2.who.preparetimer = 0.1
                                if hitbox2.who.preparetimer not in [0,5]:
                                    hitbox2.who.preparetimer += self.dt
                                    if hitbox2.who.preparetimer < 5:
                                        hitbox2.who.setrotate(settarget=hitbox.who.pos, instant=True)
                                    else:
                                        hitbox.who.preparetimer = 5
                        elif hitbox.who.gameid != hitbox2.who.gameid and ((hitbox.who.gameid < 2000 and hitbox2.who.gameid < 2000)
                                                                          or (
                                                                                  hitbox.who.gameid >= 2000 and hitbox2.who.gameid >= 2000)):  ##colide battalion in same faction
                            hitbox.collide, hitbox2.collide = hitbox2.who.gameid, hitbox.who.gameid
                """Calculate squad combat dmg"""
                if self.combattimer >= 1:
                    for thissquad in self.squad:
                        if any(battle > 1 for battle in thissquad.battleside) == True:
                            for index, combat in enumerate(thissquad.battleside):
                                if combat > 1:
                                    if thissquad.gameid not in self.squad[np.where(self.squadindexlist == combat)[0][0]].battleside:
                                        thissquad.battleside[index] = -1
                                    else:
                                        self.dmgcal(thissquad, self.squad[np.where(self.squadindexlist == combat)[0][0]], index,
                                                    self.squad[np.where(self.squadindexlist == combat)[0][0]].battleside.index(thissquad.gameid))
                        if thissquad.state in [11,12,13] and thissquad.attacktarget != 0:
                            if type(thissquad.attacktarget) == int: thissquad.attacktarget = self.allunitlist[self.allunitindex.index(thissquad.attacktarget)]
                            if thissquad.reloadtime >= thissquad.reload and thissquad.attacktarget.state != 100:
                                rangeattack.arrow(thissquad, thissquad.attackpos.distance_to(thissquad.combatpos), thissquad.range)
                                thissquad.ammo -= 1
                                thissquad.reloadtime = 0
                            elif thissquad.attacktarget.state == 100:
                                thissquad.battalion.rangecombatcheck, thissquad.battalion.attacktarget = 0, 0
                        self.combattimer = 0
                self.combattimer += self.dt
                self.unitupdater.update(self.gameunitstat.statuslist, self.squad, self.dt, self.unitviewmode, self.playerposlist, self.enemyposlist)
                self.effectupdater.update(self.playerarmy, self.enemyarmy, self.hitboxs, self.squad, self.squadindexlist, self.dt)
            elif self.gamestate == 0:
                self.screen.blit(self.pause_text, (600, 600))
            self.clock.tick(60)
            self.dt = self.clock.tick(60) / 1000
            dirty = self.all.draw(self.screen)  # draw the scene
            pygame.display.update(dirty)
        if pygame.mixer:
            pygame.mixer.music.fadeout(1000)
        pygame.time.wait(1000)
        pygame.quit()


if __name__ == '__main__':
    main = battle()
    main.rungame()
