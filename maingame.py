"""next goal: dynamic authority and leader function(0.2.4), skill usage limit option (0.3.3), menu in main game(0.3.1), proper broken retreat after map function (0.4), enactment mode (0.9)
FIX
recheck melee combat cal (still problem when 2 or more unit attack and squad not register being attack on all side)
add state change based on previous command (unit resume attacking if move to attack but get caught in combat with another unit)
"""
import random, os, os.path, glob, csv, math
import pygame
from pygame.transform import scale
from pygame.locals import *
import pygame.freetype
from RTS import mainmenu, gamearmy, gameui
import ast
from collections import defaultdict
import numpy as np

SCREENRECT = mainmenu.SCREENRECT
main_dir = mainmenu.main_dir

def load_image(file, subfolder=""):
    """loads an image, prepares it for play"""
    file = os.path.join(main_dir, 'data', subfolder, file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert_alpha()

def load_images(subfolder1="", subfolder2="", subfolder3="", loadorder = True):
    """loads all images(files) in folder using loadorder list file use only png file"""
    imgs = []
    if subfolder1 != "":
        dirpath = os.path.join(main_dir, 'data', subfolder1)
        if subfolder2 != "":
            dirpath = os.path.join(dirpath, subfolder2)
            if subfolder3 != "":
                dirpath = os.path.join(dirpath, subfolder3)
    if loadorder == True:
        loadorder = open(dirpath+"/load_order.txt","r")
        loadorder = ast.literal_eval(loadorder.read())
        for file in loadorder:
            imgs.append(load_image(dirpath + "/" + file))
    else:
        loadorder = [f for f in os.listdir(dirpath) if f.endswith('.' + "png")] ## read all file
        for file in loadorder:
            imgs.append(load_image(dirpath + "/" + file))
    return imgs

def load_sound(file):
    file = os.path.join(main_dir, 'data/sound/', file)
    sound = pygame.mixer.Sound(file)
    return sound

def addarmy(squadlist, position, gameid,colour,imagesize,leader, leaderstat,unitstat,control,coa,command=False):
    squadlist = squadlist[~np.all(squadlist == 0, axis=1)]
    squadlist = squadlist[:, ~np.all(squadlist == 0, axis=0)]
    army = gamearmy.unitarmy(startposition=position, gameid=gameid,
                                   leaderlist=leaderstat, statlist=unitstat, leader=leader,
                                   squadlist=squadlist, imgsize=imagesize,
                                   colour=colour,control=control,coa=coa,commander=command)
    army.hitbox = [gamearmy.hitbox(army, 0, army.rect.width, 5),
                          gamearmy.hitbox(army, 1, 5, army.rect.height-5),
                          gamearmy.hitbox(army, 2, 5, army.rect.height-5),
                          gamearmy.hitbox(army, 3, army.rect.width, 5)]
    return army

def unitsetup(playerarmy,enemyarmy,battle,imagewidth, imageheight,allweapon,allleader,gameunitstat,coa,squad,enactment=False):
    """squadindexlist is list of every squad index in the game for indexing the squad group"""
    # defaultarmy = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
    squadindexlist = []
    unitlist = []
    playercolour = (144, 167, 255)
    enemycolour = (255,114,114)
    """army num is list index for battalion in either player or enemy group"""
    playerarmynum, enemyarmynum,playerstart,enemystart = {}, {}, 0, 0
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
                if n in range(1, 11):
                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
            if row[0] < 2000:
                if row[0] == 1:
                    """First player battalion as commander"""
                    army = addarmy(np.array([row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]]), (row[9][0], row[9][1]), row[0], playercolour, (imagewidth, imageheight), row[10], allleader,gameunitstat, True, coa[row[11]],True)
                else:
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   playercolour, (imagewidth, imageheight), row[10], allleader, gameunitstat, True, coa[row[11]])
                playerarmy.append(army)
                playerarmynum[row[0]] = playerstart
                playerstart += 1
            elif row[0] >= 2000:
                if row[0] == 2000:
                    """First enemy battalion as commander"""
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0], enemycolour,
                                   (imagewidth, imageheight), row[10], allleader, gameunitstat, enactment, coa[row[11]], True)
                elif row[0] > 2000:
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   enemycolour,
                                   (imagewidth, imageheight), row[10], allleader, gameunitstat, enactment, coa[row[11]])
                enemyarmy.append(army)
                enemyarmynum[row[0]] = enemystart
                enemystart+=1
            """armysquadindex is list index for squad list in a specific army"""
            armysquadindex = 0
            """Setup squad in army to squad group"""
            for squadnum in np.nditer(army.armysquad, op_flags=['readwrite'], order='C'):
                if squadnum != 0:
                    addsquad = gamearmy.unitsquad(unitid=squadnum, gameid=squadgameid, weaponlist=allweapon, statlist=gameunitstat,
                                               battalion=army, position=army.squadpositionlist[armysquadindex])
                    squad.append(addsquad)
                    squadnum[...] = squadgameid
                    army.groupsquadindex.append(squadindex)
                    army.squadsprite.append(addsquad)
                    squadindexlist.append(squadgameid)
                    squadgameid += 1
                    squadindex += 1
                armysquadindex += 1
    unitfile.close()
    return playerarmynum, enemyarmynum, squadindexlist

class battle():
    def __init__(self):
        # Initialize pygame
        pygame.init()
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer = None
        # Set the display mode
        winstyle = 0
        bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)
        self.screen = pygame.display.set_mode(SCREENRECT.size, winstyle, bestdepth)
        # for when implement game and map camera
        # self.battle_surf = pygame.surface.Surface(width, height)
        # in your main loop
        # or however you draw your sprites
        # your_sprite_group.draw(game_surf)
        # then blit to screen
        # self.screen.blit(self.battle_surf, the_position)
    #Load images, assign to sprite classes
    #(do this before the classes are used, after screen setup)

    #create unit
        imgsold = load_images('unit', 'unit_ui')
        imgs=[]
        for img in imgsold:
            x, y = img.get_width(), img.get_height()
            # img = pygame.transform.scale(img, (int(x),int(y/2)))
            imgs.append(img)
        gamearmy.unitsquad.images = imgs
        self.imagewidth, self.imageheight = imgs[0].get_width(), imgs[0].get_height()
        imgs=[]
        imgsold = load_images('unit', 'unit_ui','battalion')
        for img in imgsold:
            imgs.append(img)
        gamearmy.unitarmy.images = imgs
    #create weapon icon
        imgsold = load_images('unit', 'unit_ui', 'weapon')
        imgs=[]
        for img in imgsold:
            x, y = img.get_width(), img.get_height()
            img = pygame.transform.scale(img, (int(x/1.7),int(y/1.7)))
            imgs.append(img)
        self.allweapon = gamearmy.weaponstat(imgs)
        imgsold = load_images('ui', 'skill_icon',loadorder=False)
        imgs = []
        for img in imgsold:
            imgs.append(img)
        self.gameunitstat = gamearmy.unitstat(imgs,imgs,imgs,imgs)
        #create leader list
        imgsold = load_images('leader','historic')
        imgs=[]
        for img in imgsold:
            x, y = img.get_width(), img.get_height()
            img = pygame.transform.scale(img, (int(x/2),int(y/2)))
            imgs.append(img)
        self.allleader = gamearmy.leader(imgs,option="\historic")
        #coa imagelist
        imgsold = load_images('leader', 'historic','coa')
        imgs = []
        for img in imgsold:
            imgs.append(img)
        self.coa = imgs
        """Game Effect"""
        imgsold = load_images('effect')
        imgs = []
        for img in imgsold:
            x, y = img.get_width(), img.get_height()
            # img = pygame.transform.scale(img, (int(x ), int(y / 2)))
            imgs.append(img)
        self.gameeffect = imgs
        gamearmy.arrow.images = [self.gameeffect[0]]
        #decorate the game window
        # icon = load_image('sword.jpg')
        # icon = pygame.transform.scale(icon, (32, 32))
        # pygame.display.set_icon(icon)
        pygame.display.set_caption('Masendor RTS')
        pygame.mouse.set_visible(1)

        #create the background, tile the bgd image
        bgdtile = load_image('background_tile.png', 'ui')
        self.background = pygame.Surface(SCREENRECT.size)
        # for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        for x in range(0, SCREENRECT.width, bgdtile.get_width()):
            for y in range(0, SCREENRECT.height, bgdtile.get_height()):
                self.background.blit(bgdtile, (x, 0))
                self.background.blit(bgdtile, (x, y))
        self.screen.blit(self.background, (0,0))
        pygame.display.flip()

        # #load the sound effects
        # boom_sound = load_sound('boom.wav')
        # shoot_sound = load_sound('car_door.wav')
        if pygame.mixer:
            self.SONG_END = pygame.USEREVENT + 1
            # musiclist = os.path.join(main_dir, 'data/sound/')
            self.musiclist = glob.glob(main_dir + '/data/sound/*.mp3')
            self.pickmusic=random.randint(1,4)
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
        self.hitboxs = pygame.sprite.Group()
        self.arrows = pygame.sprite.Group()
        self.directionarrows = pygame.sprite.Group()
        self.deadunit = pygame.sprite.Group()
        self.gameui = pygame.sprite.Group()
        self.buttonui = pygame.sprite.Group()
        """assign default groups"""
        gamearmy.unitarmy.containers = self.playerarmy, self.enemyarmy, self.unitupdater, self.all, self.squad
        gamearmy.unitsquad.containers = self.playerarmy, self.enemyarmy, self.unitupdater, self.squad
        gamearmy.deadarmy.containers = self.deadunit, self.unitupdater, self.all
        gamearmy.hitbox.containers = self.hitboxs, self.unitupdater, self.all
        gamearmy.arrow.containers = self.arrows, self.all, self.effectupdater
        gamearmy.directionarrow.containers = self.directionarrows, self.all, self.effectupdater
        gameui.Gameui.containers = self.gameui, self.uiupdater
        gameui.uibutton.containers = self.buttonui, self.uiupdater
        """Create Starting Values"""
        self.timer = 0
        self.dt=0
        self.combattimer = 0
        self.clock = pygame.time.Clock()
        self.lastmouseover = 0
        """use same position as squad front index 0 = front, 1 = left, 2 = rear, 3 = right"""
        self.battlesidecal = [1,0.8,0.6,0.8]
        """initialize starting unit sprites"""
        self.playerarmy, self.enemyarmy, self.squad = [],[],[]
        self.playerarmynum, self.enemyarmynum, self.squadindexlist = unitsetup(self.playerarmy,self.enemyarmy,'\\test', self.imagewidth, self.imageheight, self.allweapon, self.allleader, self.gameunitstat, self.coa, self.squad,enactment=True)
        self.deadarmynum = {}
        self.deadindex = 0
        """create game ui"""
        topimage = load_images('ui', 'battle_ui')
        iconimage = load_images('ui', 'battle_ui', 'topbar_icon')
        self.gameui = [gameui.Gameui(screen=self.screen, X=SCREENRECT.width-topimage[0].get_size()[0]/2, Y=topimage[0].get_size()[1]/2, image=topimage[0], icon=iconimage, uitype="topbar")]
        iconimage = load_images('ui', 'battle_ui', 'commandbar_icon')
        self.gameui.append(gameui.Gameui(screen=self.screen, X=topimage[1].get_size()[0]/2, Y=topimage[1].get_size()[1]/2, image=topimage[1], icon=iconimage, uitype="commandbar"))
        iconimage = load_images('ui', 'battle_ui', 'unitcard_icon')
        self.gameui.append(gameui.Gameui(screen=self.screen, X=SCREENRECT.width-topimage[2].get_size()[0]/2, Y=SCREENRECT.height-310, image=topimage[2], icon="", uitype="unitcard"))
        self.gameui.append(
            gameui.Gameui(screen=self.screen, X=SCREENRECT.width - topimage[5].get_size()[0] / 2, Y= topimage[0].get_size()[1]+150,
                   image=topimage[5], icon="", uitype="armybox"))
        self.popgameui = self.gameui
        self.buttonui = [gameui.uibutton(self.gameui[2].X-170, self.gameui[2].Y+41,topimage[3],0), gameui.uibutton(self.gameui[2].X-170, self.gameui[2].Y-65, topimage[4],1),
                         gameui.uibutton(self.gameui[2].X-170, self.gameui[2].Y-12, topimage[7],2) ,gameui.uibutton(self.gameui[0].X-206, self.gameui[0].Y, topimage[6],1)]
        self.pause_text = pygame.font.SysFont("helvetica", 100).render("PAUSE", 1,(0,0,0))
        self.unitposlist = {}
        self.enemyposlist = {}
        self.showingsquad = []
        self.removesquadlist = []
        self.unitviewmode = 0

    def squadselectside(self,targetside,side,position):
        """side 0 is left 1 is right"""
        thisposition = position
        if side == 0:
            max = 0
            while targetside[thisposition] == 0 and thisposition != max:
                thisposition -= 1
        else:
            max = 7
            while targetside[thisposition] == 0 and thisposition != max:
                thisposition += 1
        if thisposition < 0: thisposition = 0
        elif thisposition > 7: thisposition = 7
        # if thisposition != max:
        if targetside[thisposition] != 0:
            fronttarget = targetside[thisposition]
        else: fronttarget = 0
        return fronttarget

    def changeside(self,side,position):
        """position is attacker position against defender 0 = front 1 = left 2 = rear 3 = right"""
        """side is side of attack for rotating to find the correct side the defender got attack accordingly (e.g. left attack on right side is front)"""
        subposition = position
        if subposition == 2: subposition = 3
        elif subposition == 3: subposition = 2
        finalposition = subposition + 1
        if side == 0: finalposition = subposition - 1
        if finalposition == -1: finalposition = 3
        elif finalposition == 4: finalposition = 0
        return finalposition

    def squadcombatcal(self,who, target, whoside, targetside):
        """calculate squad engagement using information after battalionengage who is player battalion, target is enemy battalion"""
        # print(target.frontline)
        squadwhoside = [2 if whoside == 3 else 3 if whoside == 2 else 1 if whoside == 1 else 0][0]
        squadtargetside = [2 if targetside==3 else 3 if targetside == 2 else 1 if targetside == 1 else 0][0]
        sortmidfront = [who.frontline[whoside][3],who.frontline[whoside][4],who.frontline[whoside][2],who.frontline[whoside][5],who.frontline[whoside][1],who.frontline[whoside][6],who.frontline[whoside][0],who.frontline[whoside][7]]
        # print(who.frontline,target.frontline)
        for squad in self.squad[who.groupsquadindex[0]:who.groupsquadindex[-1]+1]:
            squad.battleside = [-1 if i in self.removesquadlist else i for i in squad.battleside]
        for squad in self.squad[target.groupsquadindex[0]:target.groupsquadindex[-1] + 1]:
            squad.battleside = [-1 if i in self.removesquadlist else i for i in squad.battleside]
        """only calculate if the attack is attack with the front side"""
        if whoside == 0:
            for thiswho in sortmidfront:
                if thiswho > 1:
                    position = np.where(who.frontline[whoside] == thiswho)[0][0]
                    fronttarget = target.frontline[targetside][position]
                    """check if squad not already fighting if true skip picking new enemy """
                    if any(battle > 1 for battle in self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside) == False:
                        """get front of another battalion frontline to assign front combat if it 0 squad will find another unit on the left or right"""
                        if fronttarget > 1:
                            """only attack if the side is already free else just wait until it free"""
                            if self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[squadtargetside] in [-1, 0]:
                                self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[whoside] = fronttarget
                                self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[squadtargetside] = thiswho
                                # print('front', self.squad[np.where(self.squadindexlist == thiswho)[0][0]].gameid,
                                #       self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside, fronttarget)
                                # print('front', self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].gameid,
                                #       self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside, fronttarget)
                        else:
                            """pick flank attack if no enemy already fighting and not already fighting"""
                            chance = random.randint(0, 1)
                            secondpick = 0
                            if chance == 0: secondpick = 1
                            """attack left array side of the squad if get random 0, right if 1"""
                            truetargetside = self.changeside(chance, targetside)
                            fronttarget = self.squadselectside(target.frontline[targetside],chance,position)
                            """attack if the found defender at that side is free if not check other side"""
                            if fronttarget > 1:
                                if self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] in [-1, 0]:
                                    self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[whoside] = fronttarget
                                    self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] = thiswho
                                    # print('side', self.squad[np.where(self.squadindexlist == thiswho)[0][0]].gameid,
                                    #       self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside, fronttarget)
                                    # print('side', self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].gameid,
                                    #       self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside, fronttarget)
                            else:
                                """Switch to another side if above not found"""
                                truetargetside = self.changeside(secondpick, targetside)
                                fronttarget = self.squadselectside(target.frontline[targetside],secondpick,position)
                                if fronttarget > 1:
                                    if self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] in [-1,0]:
                                        self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[whoside] = fronttarget
                                        self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] = thiswho
                                    # print('side2', self.squad[np.where(self.squadindexlist == thiswho)[0][0]].gameid, self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside, fronttarget)
                                    # print('side2', self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].gameid, self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside, fronttarget)
                                else:
                                    self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[
                                        targetside] = 0
        """only calculate if the target is attacked on the front side"""
        if targetside == 0:
            sortmidfront = [target.frontline[targetside][3], target.frontline[targetside][4],
                            target.frontline[targetside][2],
                            target.frontline[targetside][5], target.frontline[targetside][1],
                            target.frontline[targetside][6],
                            target.frontline[targetside][0], target.frontline[targetside][7]]
            for thiswho in sortmidfront:
                if thiswho > 1:
                    position = np.where(target.frontline[targetside] == thiswho)[0][0]
                    fronttarget = who.frontline[whoside][position]
                    """check if squad not already fighting if true skip picking new enemy """
                    if any(battle > 1 for battle in
                           self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside) == False:
                        """get front of another battalion frontline to assign front combat if it 0 squad will find another unit on the left or right"""
                        if fronttarget > 1:
                            if self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[squadwhoside] in [-1, 0]:
                                self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[targetside] = fronttarget
                                self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[
                                    squadwhoside] = thiswho
                        else:
                            """pick flank attack if no enemy already fighting and not already fighting"""
                            chance = random.randint(0, 1)
                            secondpick = 0
                            if chance == 0: secondpick = 1
                            """attack left array side of the squad if get random 0, right if 1"""
                            truetargetside = self.changeside(chance, whoside)
                            fronttarget = self.squadselectside(who.frontline[whoside], chance, position)
                            """attack if the found defender side is free if not check other side"""
                            if fronttarget > 1:
                                if self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[
                                    truetargetside] in [-1, 0]:
                                    self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[
                                        targetside] = fronttarget
                                    self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[
                                        truetargetside] = thiswho
                            else:
                                """Switch to another side if above not found"""
                                truetargetside = self.changeside(secondpick, whoside)
                                fronttarget = self.squadselectside(who.frontline[whoside], secondpick, position)
                                if fronttarget > 1:
                                    if self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] in [-1, 0]:
                                        self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[targetside] = fronttarget
                                        self.squad[np.where(self.squadindexlist == fronttarget)[0][0]].battleside[truetargetside] = thiswho
                                else:
                                    self.squad[np.where(self.squadindexlist == thiswho)[0][0]].battleside[whoside] = 0
        self.removesquadlist = []
        # print('endhere')

    def losscal(self, who, target, hit, defense, type):
        if hit < 0: hit = 0
        if defense < 0: defense = 0
        hitchance = hit - defense
        if hitchance <= 10:
            finalchance = random.randint(0, 100)
            if finalchance > 97: combatscore = 0.1
            else: combatscore = 0
        elif hitchance > 10 and hitchance <= 20:combatscore = 0.1
        elif hitchance > 20 and hitchance <= 40:combatscore = 0.5
        elif hitchance > 40 and hitchance <= 80:combatscore = 1
        elif hitchance > 80: combatscore = 1.5
        if type == "melee":
            dmg = who.dmg
            if who.charging == True: dmg = round(dmg + (who.charge/10) - (who.chargedef/10))
            if target.charging == True: dmg =  round(dmg + (who.chargedef/10) - (target.charge/10))
            dmg = round(((who.dmg * who.troopnumber) - ((target.armour * who.penetrate) / 100)) * combatscore * (who.dmgeffect/100))
        elif type == "range": dmg = round(((who.rangedmg * who.troopnumber) - ((target.armour * who.rangepenetrate) / 100)) * combatscore)
        if dmg > target.unithealth: dmg = target.unithealth
        elif dmg < 0 : dmg = 0
        moraledmg = round(dmg / 100)
        return dmg, moraledmg

    def dmgcal(self, who, target, whoside, targetside):
        """target position 0 = Front, 1 = Side, 3 = Rear"""
        # print(target.gameid, target.battleside)
        wholuck, wholuck2 = random.randint(0, 50), random.randint(0, 50)
        targetluck, targetluck2 = random.randint(0, 50), random.randint(0, 50)
        whopercent = self.battlesidecal[whoside]
        targetpercent = self.battlesidecal[targetside]
        whohit, whodefense = float(who.attack*whopercent) - wholuck + wholuck2, float(who.meleedef*whopercent) - wholuck + wholuck2
        targethit, targetdefense = float(who.attack*targetpercent) - targetluck + targetluck2, float(target.meleedef*targetpercent) - targetluck + targetluck2
        whodmg, whomoraledmg = self.losscal(who,target,whohit,targetdefense,'melee')
        targetdmg, targetmoraledmg = self.losscal(target,who,targethit, whodefense,'melee')
        who.unithealth -= targetdmg
        who.basemorale -= targetmoraledmg
        target.unithealth -= whodmg
        target.basemorale -= whomoraledmg

    def die(self, who, group, deadgroup, rendergroup, hitboxgroup):
        self.deadarmynum[who.gameid] = self.deadindex
        self.deadindex+=1
        for hitbox in who.hitbox:
            rendergroup.remove(hitbox)
            hitboxgroup.remove(hitbox)
        group.remove(who)
        deadgroup.add(who)
        rendergroup.change_layer(sprite=who, new_layer=0)
        who.gotkilled = 1

    def rungame(self):
        self.gamestate = 1
        self.check = 0 ## For checking if unit or ui is clicked
        self.check2 = 0 ##  For checking if another unit is clicked when inspect ui open"
        self.inspectui = 0
        self.lastselected = 0
        self.squadlastselected = None
        self.beforeselected = None
        self.squadbeforeselected = None
        while True:
            keystate = pygame.key.get_pressed()
            self.mousepos = pygame.mouse.get_pos()
            mouse_up = False
            mouse_right = False
            double_mouse_right = False
            for event in pygame.event.get(): ## get event input
                if event.type == QUIT or \
                    (event.type == KEYDOWN and event.key == K_ESCAPE):
                        self.all.clear(self.screen, self.background)
                        return
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    mouse_up = True
                if event.type == pygame.MOUSEBUTTONUP and event.button == 3: ## Right Click
                    mouse_right = True
                    if self.timer == 0: self.timer = 0.001 ##Start timer after first mouse click
                    elif self.timer < 0.3:
                        double_mouse_right = True
                        self.timer = 0
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        if self.unitviewmode == 1: self.unitviewmode = 0
                        else: self.unitviewmode = 1
                    if event.key == pygame.K_SPACE: ## Pause Button
                        if self.gamestate == 1: self.gamestate = 0
                        else:self.gamestate = 1

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
                    self.pickmusic = random.randint(0, 4)
                    pygame.mixer.music.load(self.musiclist[self.pickmusic])
                    pygame.mixer.music.play(0)
            if self.timer != 0:
                self.timer += self.dt
                if self.timer >= 0.5:
                    self.timer = 0
            self.all.clear(self.screen, self.background) ##clear sprite before update new one
            self.uiupdater.update() #update ui outside of combat loop so it update even when game pause
            # directionX = keystate[K_RIGHT] - keystate[K_LEFT]
            # directionY = keystate[K_DOWN] - keystate[K_UP]
            self.lastmouseover = 0
            if mouse_up == True:
                self.check = 0
                self.check2 = 0
            for thisenemy in self.enemyarmy:
                self.enemyposlist[thisenemy.gameid] = thisenemy.pos
                posmask = self.mousepos[0] - thisenemy.rect.x, self.mousepos[1] - thisenemy.rect.y
                if thisenemy.rect.collidepoint(self.mousepos):
                    try:
                        if thisenemy.mask.get_at(posmask) == 1:
                            thisenemy.mouse_over = True
                            self.lastmouseover = thisenemy
                            if mouse_up:
                                self.lastselected = thisenemy.gameid
                                self.check = 1
                    except:thisenemy.mouse_over = False
                if thisenemy.state == 100 and thisenemy.gotkilled == 0:
                    self.die(thisenemy, self.enemyarmy, self.deadunit, self.all, self.hitboxs)
            for army in self.playerarmy:
                self.unitposlist[army.gameid] = army.pos
                posmask = self.mousepos[0] - army.rect.x, self.mousepos[1] - army.rect.y
                #     army.mouse_over = True
                # except: self.mouse_over = False
                if army.rect.collidepoint(self.mousepos):
                    try:
                        if army.mask.get_at(posmask) == 1:
                            army.mouse_over = True
                            self.lastmouseover = army
                            if mouse_up:
                                self.lastselected = army.gameid
                                self.check = 1
                    except: army.mouse_over = False
                else: army.mouse_over = False
                if army.state == 100 and army.gotkilled == 0:
                    self.die(army, self.playerarmy, self.deadunit, self.all)
                # pygame.draw.aaline(screen, (100, 0, 0), army.pos, army.target, 10)
            if self.lastselected != 0:
                if self.lastselected < 2000:
                    """if not found in army class then it is in dead class"""
                    try: whoinput = self.playerarmy[self.playerarmynum[self.lastselected]]
                    except: lastselected = 0 #whoinput = self.deadunit[self.deadarmynum[self.lastselected]]
                else:
                    try: whoinput = self.enemyarmy[self.enemyarmynum[self.lastselected]]
                    except: lastselected = 0 #whoinput = self.deadunit[self.deadarmynum[self.lastselected]]
                if (mouse_up or mouse_right):
                    whoinput.command(pygame.mouse.get_pos(), mouse_up, mouse_right, double_mouse_right,
                                             self.lastselected,self.lastmouseover, self.enemyposlist,keystate)
                    if whoinput.target != whoinput.pos and whoinput.rotateonly == False and whoinput.directionarrow == False:
                        gamearmy.directionarrow(whoinput)
                """add back the pop up ui to group so it get shown"""
                if self.beforeselected == 0:
                    self.gameui = self.popgameui
                    self.all.add(*self.gameui[0:2])
                    self.all.add(self.buttonui[3])
                elif self.beforeselected != self.lastselected and self.inspectui == 1:
                    self.check2 = 1
                    self.all.remove(*self.showingsquad)
                    self.showingsquad = []
                self.gameui[0].valueinput(who=whoinput, leader=self.allleader)
                self.gameui[1].valueinput(who=whoinput, leader=self.allleader)
                if (self.buttonui[3].rect.collidepoint(pygame.mouse.get_pos()) and mouse_up==True and self.inspectui == 0) or (mouse_up == True and self.inspectui == 1 and self.check2 == 1):
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
                if self.inspectui == 1:
                    # if self.showingsquad[0] not in self.all:
                    self.all.add(*self.showingsquad)
                    """Update value of the clicked squad"""
                    if self.squadlastselected != None:
                        self.gameui[2].valueinput(who=self.squadlastselected, leader=self.allleader, gameunitstat=self.gameunitstat)
                    """Change showing stat to the clicked squad one"""
                    if mouse_up==True:
                        for squad in self.showingsquad:
                            if squad.rect.collidepoint(pygame.mouse.get_pos()) == True:
                                self.check = 1
                                squad.command(pygame.mouse.get_pos(), mouse_up, mouse_right, self.squadlastselected.wholastselect)
                                self.squadlastselected = squad
                                self.gameui[2].valueinput(who=squad, leader=self.allleader, gameunitstat=self.gameunitstat)
                            """Change unit card option based on button clicking"""
                            for button in self.buttonui:
                                if button.rect.collidepoint(pygame.mouse.get_pos()):
                                    self.check = 1
                                    if self.gameui[2].option != button.event:
                                        self.gameui[2].option = button.event
                                        self.gameui[2].valueinput(who=squad, leader=self.allleader, changeoption=1, gameunitstat=self.gameunitstat)
                    self.squadbeforeselected = self.squadlastselected
                self.beforeselected = self.lastselected
            """remove the pop up ui when click at no group"""
            if self.check != 1:
                self.lastselected = 0
                for ui in self.gameui: ui.kill()
                for button in self.buttonui: button.kill()
                self.all.remove(*self.showingsquad)
                self.showingsquad = []
                self.showingsquadindex = []
                self.inspectui = 0
                self.squadbeforeselected = 0
                self.beforeselected = 0
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
                                if hitbox.side == 0 and hitbox.who.state not in [95, 96, 97, 98, 99, 100] and hitbox.who.combatpreparestate == 0 and hitbox2.who.combatpreparestate != 1:
                                    hitbox.who.combatprepare(hitbox2)
                                    hitbox.who.preparetimer = 0
                                elif hitbox2.side == 0 and hitbox2.who.state not in [95, 96, 97, 98, 99, 100] and hitbox2.who.combatpreparestate == 0 and hitbox.who.combatpreparestate != 1:
                                    hitbox2.who.combatprepare(hitbox)
                                    hitbox2.who.preparetimer = 0
                                for battle in hitbox.who.battleside:
                                    if battle != 0:
                                        self.squadcombatcal(hitbox.who, hitbox2.who, hitbox.who.battleside.index(battle),
                                                            hitbox2.who.battleside.index(hitbox.who.gameid))
                            """Rotate army side to the enemyside"""
                            if hitbox.who.combatpreparestate == 1:
                                if hitbox.who.preparetimer == 0: hitbox.who.preparetimer = 0.1
                                if hitbox.who.preparetimer != 0:
                                    hitbox.who.preparetimer += self.dt
                                    if hitbox.who.preparetimer < 4: hitbox.who.setrotate(settarget=hitbox2.who.pos, instant=True)
                                    else: hitbox.who.preparetimer = 4
                            if hitbox2.who.combatpreparestate == 1:
                                if hitbox2.who.preparetimer == 0: hitbox2.who.preparetimer = 0.1
                                if hitbox2.who.preparetimer != 0:
                                    hitbox2.who.preparetimer += self.dt
                                    if hitbox2.who.preparetimer < 4: hitbox2.who.setrotate(settarget=hitbox.who.pos, instant=True)
                                    else: hitbox.who.preparetimer = 4
                            """calculate battalion and squad if in combat"""
                            if hitbox.who.recalsquadcombat == True or hitbox2.who.recalsquadcombat == True:
                                for battle in hitbox.who.battleside:
                                    if battle != 0:
                                # self.battalionengage(army,thisenemy,army.battleside.index(battle),thisenemy.battleside.index(army.gameid))
                                        self.squadcombatcal(hitbox.who, hitbox2.who, hitbox.who.battleside.index(battle), hitbox2.who.battleside.index(hitbox.who.gameid))
                                hitbox.who.recalsquadcombat, hitbox2.who.recalsquadcombat = False, False
                        elif hitbox.who.gameid != hitbox2.who.gameid and ((hitbox.who.gameid < 2000 and hitbox2.who.gameid < 2000) or (hitbox.who.gameid >= 2000 and hitbox2.who.gameid >= 2000)):
                            # if pygame.sprite.collide_mask(hitbox, hitbox2) is not None:
                            hitbox.collide, hitbox2.collide = hitbox2.who.gameid, hitbox.who.gameid
                """Calculate squad combat dmg"""
                if self.combattimer >= 0.5:
                    for thissquad in self.squad:
                        if any(battle > 1 for battle in thissquad.battleside) == True:
                            for index, combat in enumerate(thissquad.battleside):
                                if combat > 1:
                                    # print(thissquad.gameid, thissquad.battleside, combat, self.squad[np.where(self.squadindexlist == combat)[0][0]].battleside)
                                    if thissquad.gameid not in self.squad[np.where(self.squadindexlist == combat)[0][0]].battleside:
                                        thissquad.battleside[index] = -1
                                    else:
                                        self.dmgcal(thissquad,self.squad[np.where(self.squadindexlist == combat)[0][0]],index,self.squad[np.where(self.squadindexlist == combat)[0][0]].battleside.index(thissquad.gameid))
                                    if thissquad.unithealth <= 0:
                                        self.removesquadlist.append(thissquad.gameid)
                                    if self.squad[np.where(self.squadindexlist == combat)[0][0]].unithealth <= 0:
                                        self.removesquadlist.append(self.squad[np.where(self.squadindexlist == combat)[0][0]].gameid)
                        if thissquad.state == 11 and thissquad.battalion.attacktarget.state != 100:
                            if thissquad.reloadtime >= thissquad.reload:
                                gamearmy.arrow(thissquad, thissquad.attackpos.distance_to(thissquad.combatpos),thissquad.range)
                                thissquad.ammo -= 1
                                thissquad.reloadtime = 0
                        elif thissquad.state == 11 and thissquad.battalion.state == 100:
                            thissquad.battalion.rangecombatcheck, thissquad.battalion.attacktarget = 0, 0
                        self.combattimer = 0
                self.combattimer += self.dt
                self.unitupdater.update(self.gameunitstat.statuslist, self.squad, self.dt, self.unitviewmode)
                self.effectupdater.update(self.playerarmy, self.enemyarmy, self.hitboxs, self.squad, self.squadindexlist, self.dt)
                #cap the framerate
            elif self.gamestate == 0:
                self.screen.blit(self.pause_text, (600, 600))
            self.clock.tick(60)
            self.dt = self.clock.tick(60) / 1000
            # draw the scene
            dirty = self.all.draw(self.screen)
            pygame.display.update(dirty)
        if pygame.mixer:
            pygame.mixer.music.fadeout(1000)
        pygame.time.wait(1000)
        pygame.quit()

if __name__ == '__main__':
    main = battle()
    main.rungame()

