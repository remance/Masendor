import pygame
import pygame.freetype
import datetime


class Uibutton(pygame.sprite.Sprite):
    def __init__(self, X, Y, image, event, newlayer=10):
        self._layer = newlayer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = (X, Y)
        self.image = image
        self.event = event
        self.rect = self.image.get_rect(center=self.pos)
        self.mouse_over = False
    #
    # def draw(self, gamescreen):
    #     gamescreen.blit(self.image, self.rect)

class Switchuibutton(pygame.sprite.Sprite):
    def __init__(self, X, Y, image):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = (X, Y)
        self.images = image
        self.image = self.images[0]
        self.event = 0
        self.rect = self.image.get_rect(center=self.pos)
        self.mouse_over = False
        self.lastevent = 0

    def update(self):
        if self.event != self.lastevent:
            self.image = self.images[self.event]
            self.rect = self.image.get_rect(center=self.pos)
            self.lastevent = self.event


class Popupicon(pygame.sprite.Sprite):
    def __init__(self, X, Y, image, event, gameui, itemid=""):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.X, self.Y = X, Y
        self.image = image
        self.event = 0
        self.rect = self.image.get_rect(center=(self.X, self.Y))
        self.mouse_over = False
        self.itemid = itemid
    #
    # def draw(self, gamescreen):
    #     gamescreen.blit(self.image, self.rect)


class Gameui(pygame.sprite.Sprite):
    def __init__(self, X, Y, screen, image, icon, uitype, text="", textsize=16):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.X, self.Y = X, Y
        self.text = text
        self.image = image
        self.icon = icon
        self.uitype = uitype
        self.value = [-1, -1]
        self.lastvalue = 0
        self.option = 0
        self.rect = self.image.get_rect(center=(self.X, self.Y))
        self.lastwho = 0
        if self.uitype == "topbar":
            position = 10
            for ic in self.icon:
                self.iconimagerect = ic.get_rect(
                    topleft=(self.image.get_rect()[0] + position, self.image.get_rect()[1]))
                self.image.blit(ic, self.iconimagerect)
                position += 90
            self.options1 = {0: "Idle", 1: "Walking", 2: "Running", 3: "Walk(Melee)", 4: "Run(Melee)", 5: "Walk(Range)", 6: "Run(Range)",
                             7: "Forced Walk", 8: "Forced Run",
                             10: "Fighting", 11: "shooting",65:"Sleeping", 66: "Camping",67:"Resting", 68: "Dancing",
                             69: "Partying", 96: "Retreating", 97: "Collapse", 98: "Retreating",99: "Broken", 100: "Destroyed"}
            self.options2 = {0: "Broken", 1: "Retreating", 2: "Breaking", 3: "Poor", 4: "Wavering", 5: "Balanced",
                             6: "Steady", 7: "Fine", 8: "Confident", 9: "Eager", 10: "Ready", 11: "Merry", 12: "Elated", 13: "Ecstatic",
                             14: "Inspired", 15: "Fervent"}
            self.options3 = {0: "Collapse", 1: "Exhausted", 2: "Severed", 3: "Very Tired", 4: "Tired", 5: "Winded", 6: "Moderate",
                             7: "Alert", 8: "Warmed Up", 9: "Active", 10: "Fresh"}
        elif self.uitype == "commandbar":
            self.iconimagerect = self.icon[6].get_rect(
                center=(self.image.get_rect()[0] + self.image.get_size()[0] / 1.1, self.image.get_rect()[1] + 40))
            self.image.blit(self.icon[6], self.iconimagerect)
            self.white = [self.icon[0], self.icon[1], self.icon[2], self.icon[3], self.icon[4], self.icon[5]]
            self.black = [self.icon[7], self.icon[8], self.icon[9], self.icon[10], self.icon[11], self.icon[12]]
            self.lastauth = 0
        elif self.uitype == "unitcard":
            self.fonthead = pygame.font.SysFont("curlz", textsize + 4)
            self.fonthead.set_italic(1)
            self.fontlong = pygame.font.SysFont("helvetica", textsize - 2)
            self.fronttext = ["", "Troop: ", "Stamina: ", "Morale: ", "Discipline: ", "Melee Attack: ",
                              "Melee Defense: ", 'Range Defense: ', 'Armour: ', 'Speed: ', "Accuracy: ",
                              "Range: ", "Ammunition: ", "Reload Speed: ", "Charge Power: ", "Charge Defense:"]
            self.qualitytext = ("Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect")
            self.terrainlist = ["Temperate", "Tropical", "Volcanic", "Desert", "Arctic", "Blight", "Void", "Demonic", "Death", "Shallow water", "Deep water"]
        #     self.iconimagerect = self.icon[0].get_rect(
        #         center=(
        #             self.image.get_rect()[0] + self.image.get_size()[0] - 20, self.image.get_rect()[1] + 40))
        self.image_original = self.image.copy()

    def blit_text(self, surface, text, pos, font, color=pygame.Color('black')):
        words = [word.split(' ') for word in text.splitlines()]  ## 2D array where each row is a list of words
        space = font.size(' ')[0]  ## the width of a space
        max_width, max_height = surface.get_size()
        x, y = pos
        for line in words:
            for word in line:
                word_surface = font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  ## reset x
                    y += word_height  ## start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  ## reset x
            y += word_height  ## start on new row

    def valueinput(self, who, weaponlist="", armourlist="", leader="", button="", changeoption=0, gameunitstat="", splithappen=False):
        for thisbutton in button:
            thisbutton.draw(self.image)
        position = 65
        if self.uitype == "topbar":
            self.value = [str(who.troopnumber) + " (" + str(who.maxhealth) + ")", who.staminastate, who.moralestate, who.state]
            if self.value[3] in self.options1:
                self.value[3] = self.options1[self.value[3]]
            # if type(self.value[2]) != str:
            self.value[2] = round(self.value[2] / 10)
            if self.value[2] in self.options2:
                self.value[2] = self.options2[self.value[2]]
            else: self.value[2] = self.options2[15]
            self.value[1] = round(self.value[1] / 10)
            if self.value[1] in self.options3:
                self.value[1] = self.options3[self.value[1]]
            if self.value != self.lastvalue or splithappen:
                self.image = self.image_original.copy()
                for value in self.value:
                    self.textsurface = self.font.render(str(value), 1, (0, 0, 0))
                    self.textrect = self.textsurface.get_rect(
                        center=(self.image.get_rect()[0] + position, self.image.get_rect()[1] + 25))
                    self.image.blit(self.textsurface, self.textrect)
                    if position >= 200:
                        position += 50
                    else:
                        position += 95
                self.lastvalue = self.value
        # for line in range(len(label)):
        #     surface.blit(label(line), (position[0], position[1] + (line * fontsize) + (15 * line)))
        elif self.uitype == "commandbar":
            if who.gameid != self.lastwho or splithappen:  ## only redraw leader circle when change unit (will add condition if leader die or changed later)
                usecolour = self.white
                self.leaderpiclist = []
                self.image = self.image_original.copy()
                if who.gameid >= 2000:
                    usecolour = self.black
                if who.commander:
                    ## main general
                    self.iconimagerect = usecolour[0].get_rect(
                        center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2.1, self.image.get_rect()[1] + 45))
                    self.image.blit(usecolour[0], self.iconimagerect)
                    ## special role
                    self.iconimagerect = usecolour[1].get_rect(
                        center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2.1, self.image.get_rect()[1] + 140))
                    self.image.blit(usecolour[1], self.iconimagerect)
                else:
                    ## left sub general
                    self.iconimagerect = usecolour[2].get_rect(
                        center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2.1, self.image.get_rect()[1] + 45))
                    self.image.blit(usecolour[2], self.iconimagerect)
                    ## right sub general
                    self.iconimagerect = usecolour[5].get_rect(
                        center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2.1, self.image.get_rect()[1] + 140))
                    self.image.blit(usecolour[5], self.iconimagerect)
                self.iconimagerect = usecolour[3].get_rect(center=(
                    self.image.get_rect()[0] - 10 + self.image.get_size()[0] / 3.1,
                    self.image.get_rect()[1] - 10 + self.image.get_size()[1] / 2.2))
                self.image.blit(usecolour[3], self.iconimagerect)
                self.iconimagerect = usecolour[0].get_rect(center=(
                    self.image.get_rect()[0] - 10 + self.image.get_size()[0] / 1.4,
                    self.image.get_rect()[1] - 10 + self.image.get_size()[1] / 2.2))
                self.image.blit(usecolour[4], self.iconimagerect)
                self.image_original2 = self.image.copy()
                # for thisleader in who.leaderwho:
                #     self.leaderpiclist.append(thisleader[1])
            if self.lastauth != who.authority or who.gameid != self.lastwho or splithappen:  ## authority number
                self.image = self.image_original2.copy()
                self.textsurface = self.font.render(str(who.authority), 1, (0, 0, 0))
                self.textrect = self.textsurface.get_rect(
                    center=(self.image.get_rect()[0] + self.image.get_size()[0] / 1.12, self.image.get_rect()[1] + 83))
                self.image.blit(self.textsurface, self.textrect)
                self.lastauth = who.authority
        elif self.uitype == "unitcard":
            position = 15
            positionx = 45
            self.value = [who.name, str(who.troopnumber) + " (" + str(who.maxtroop) + ")", int(who.stamina), int(who.morale),
                          int(who.discipline), int(who.attack), int(who.meleedef), int(who.rangedef), int(who.armour), int(who.speed),
                          int(who.accuracy),
                          int(who.shootrange), who.ammo, str(int(who.reloadtime)) + " (" + str(who.reload) + ")", who.charge, who.chargedef,
                          who.tempcount]
            self.value2 = [who.trait, who.skill, who.skillcooldown, who.skilleffect, who.statuseffect]
            self.description = who.description
            if type(self.description) == list: self.description = self.description[0]
            if self.value != self.lastvalue or changeoption == 1 or who.gameid != self.lastwho:
                self.image = self.image_original.copy()
                row = 0
                self.name = self.value[0]
                leadertext = ""
                if who.leader is not None:
                    leadertext = "/" + str(who.leader.name)
                    if who.leader.state == 100: leadertext += " (Dead)"
                self.textsurface = self.fonthead.render(self.name + leadertext, 1, (0, 0, 0))  ##unit and leader name at the top
                self.textrect = self.textsurface.get_rect(
                    midleft=(self.image.get_rect()[0] + positionx, self.image.get_rect()[1] + position))
                self.image.blit(self.textsurface, self.textrect)
                row += 1
                position += 20
                if self.option == 1:  ## Stat card
                    # self.iconimagerect = self.icon[0].get_rect(
                    #     center=(
                    #     self.image.get_rect()[0] + self.image.get_size()[0] -20, self.image.get_rect()[1] + 40))
                    # deletelist = [i for i,x in enumerate(self.value) if x == 0]
                    # if len(deletelist) != 0:
                    #     for i in sorted(deletelist, reverse = True):
                    #         self.value.pop(i)
                    #         text.pop(i)
                    newvalue, text = self.value[0:-1], self.fronttext[1:]
                    for n, value in enumerate(newvalue[1:]):
                        self.textsurface = self.font.render(text[n] + str(value), 1, (0, 0, 0))
                        self.textrect = self.textsurface.get_rect(
                            midleft=(self.image.get_rect()[0] + positionx, self.image.get_rect()[1] + position))
                        self.image.blit(self.textsurface, self.textrect)
                        position += 20
                        row += 1
                        if row == 9: positionx, position = 200, 35
                elif self.option == 0:  ## description card
                    self.blit_text(self.image, self.description, (42, 25), self.fontlong)
                elif self.option == 3:  ## equipment and terrain
                    terrain = self.terrainlist[who.battalion.terrain]
                    if who.battalion.feature is not None: terrain += "/" + self.featurelist[who.battalion.feature]
                    textvalue = [self.qualitytext[who.meleeweapon[1]] + " " + str(weaponlist.weaponlist[who.meleeweapon[0]][0]) + ": " + str(
                        weaponlist.weaponlist[who.meleeweapon[0]][1]) + ", " + str(weaponlist.weaponlist[who.meleeweapon[0]][2]) + ", " + str(
                        weaponlist.weaponlist[who.meleeweapon[0]][3]),
                                 self.qualitytext[who.armourgear[1]] + " " + str(armourlist.armourlist[who.armourgear[0]][0]) + ": " + str(
                                     armourlist.armourlist[who.armourgear[0]][1]) + ", " + str(armourlist.armourlist[who.armourgear[0]][2]),
                                 "Total Weight:" + str(who.weight), "Terrain:" + terrain, "Height:" + str(who.battalion.height), "Temperature:" + str(int(who.tempcount))]
                    if who.rangeweapon[0] != 0:
                        textvalue.insert(1,
                                         self.qualitytext[who.rangeweapon[1]] + " " + str(weaponlist.weaponlist[who.rangeweapon[0]][0]) + ": " + str(
                                             weaponlist.weaponlist[who.rangeweapon[0]][1]) + ", " + str(
                                             weaponlist.weaponlist[who.rangeweapon[0]][2]) + ", " + str(weaponlist.weaponlist[who.rangeweapon[0]][3]))
                    if 0 not in who.mount:
                        textvalue.insert(3, str(who.mount[0]))
                    for text in textvalue:
                        self.textsurface = self.font.render(str(text), 1, (0, 0, 0))
                        self.textrect = self.textsurface.get_rect(
                            midleft=(self.image.get_rect()[0] + positionx, self.image.get_rect()[1] + position))
                        self.image.blit(self.textsurface, self.textrect)
                        position += 20
                self.lastvalue = self.value
        self.lastwho = who.gameid

class Skillcardicon(pygame.sprite.Sprite):
    cooldown = None
    activeskill = None

    def __init__(self, image, pos, type, id = None):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.type = type
        self.gameid = id
        self.pos = pos
        self.font = pygame.font.SysFont("helvetica", 18)
        self.cooldowncheck = 0
        self.activecheck = 0
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.image_original = self.image.copy()
        self.cooldownrect = self.image.get_rect(topleft=(0, 0))

    def numberchange(self, number):
        resultnumber = str(round(number / 1000, 1)) + "K"
        return resultnumber

    def iconchange(self, cooldown, activetimer):
        """Show active effect timer first if none show cooldown"""
        if activetimer != self.activecheck:
            self.activecheck = activetimer
            self.image = self.image_original.copy()
            if self.activecheck > 0:
                rect = self.image.get_rect(topleft=(0,0))
                self.image.blit(self.activeskill,rect)
                outputnumber = str(self.activecheck)
                if self.activecheck >= 1000:
                    outputnumber = self.numberchange(outputnumber)
                self.textsurface = self.font.render(outputnumber, 1, (0, 0, 0))  ## timer number
                self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
                self.image.blit(self.textsurface, self.textrect)

        elif cooldown != self.cooldowncheck and self.activecheck == 0:
            self.cooldowncheck = cooldown
            self.image = self.image_original.copy()
            if self.cooldowncheck > 0:
                self.image.blit(self.cooldown,self.cooldownrect)
                outputnumber = str(self.cooldowncheck)
                if self.cooldowncheck >= 1000:
                    outputnumber = self.numberchange(outputnumber)
                self.textsurface = self.font.render(outputnumber, 1, (0, 0, 0))  ## timer number
                self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
                self.image.blit(self.textsurface, self.textrect)

class Effectcardicon(pygame.sprite.Sprite):

    def __init__(self, image, pos, type, id = None):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.type = type
        self.gameid = id
        self.pos = pos
        self.cooldowncheck = 0
        self.activecheck = 0
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.image_original = self.image.copy()

class FPScount(pygame.sprite.Sprite):
    def __init__(self):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.image_original = self.image.copy()
        self.font = pygame.font.SysFont("Arial", 18)
        self.rect = self.image.get_rect(center=(30, 30))

    def fpsshow(self, clock):
        self.image = self.image_original.copy()
        fps = str(int(clock.get_fps()))
        fps_text = self.font.render(fps, 1, pygame.Color("black"))
        self.textrect = fps_text.get_rect(center=(25, 25))
        self.image.blit(fps_text, self.textrect)

class Selectedsquad(pygame.sprite.Sprite):
    def __init__(self,image):
        self._layer = 12
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image

    def pop(self, pos):
        self.rect = self.image.get_rect(topleft=pos)

class Minimap(pygame.sprite.Sprite):
    def __init__(self, X, Y,image, camera):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.X = X
        self.Y = Y
        self.image = image
        scalewidth = self.image.get_width() / 5
        scaleheight = self.image.get_height() / 5
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image = pygame.transform.scale(self.image, (int(self.dim[0]), int(self.dim[1])))
        self.image_original = self.image.copy()
        self.enemydot = pygame.Surface((8,8))
        self.enemydot.fill((0, 0, 0))
        self.playerdot = pygame.Surface((8,8))
        self.playerdot.fill((0, 0, 0))
        enemy = pygame.Surface((6,6))
        enemy.fill((255, 0, 0))
        player = pygame.Surface((6,6))
        player.fill((0, 0, 255))
        rect = self.enemydot.get_rect(topleft=(1,1))
        self.enemydot.blit(enemy,rect)
        self.playerdot.blit(player,rect)
        self.playerpos = []
        self.enemypos = []
        self.cameraborder = [camera.image.get_width(), camera.image.get_height()]
        self.camerapos = camera.pos
        self.lastscale = 10
        self.rect = self.image.get_rect(bottomright=(self.X, self.Y))

    def update(self, viewmode, camerapos, playerposlist, enemyposlist):
        if self.playerpos != playerposlist.values() or self.enemypos != enemyposlist.values() or self.camerapos != camerapos or self.lastscale != viewmode:
            self.playerpos = playerposlist.values()
            self.enemypos = enemyposlist.values()
            self.camerapos = camerapos
            self.image = self.image_original.copy()
            for player in playerposlist.values():
                scaledpos = player / 5
                rect = self.playerdot.get_rect(center=scaledpos)
                self.image.blit(self.playerdot, rect)
            for enemy in enemyposlist.values():
                scaledpos = enemy / 5
                rect = self.enemydot.get_rect(center=scaledpos)
                self.image.blit(self.enemydot, rect)
            pygame.draw.rect(self.image, (0, 0, 0), (camerapos[1][0] / 5 / viewmode, camerapos[1][1] / 5 / viewmode,
                self.cameraborder[0] * 10 / viewmode / 50, self.cameraborder[1] * 10 / viewmode  / 50), 2)

class Eventlog(pygame.sprite.Sprite): ## Maybe Add timestamp to eventlog if having it scrollable (probably when implement battle time)

    def __init__(self, image, pos):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", 16)
        self.pos = pos
        self.mode = 0
        self.image = image
        self.image_original = self.image.copy()
        self.battlelog = []
        self.battalionlog = []
        self.leaderlog = []
        self.squadlog = []
        self.rect = self.image.get_rect(bottomleft=self.pos)
        self.currentstartrow = 0
        self.maxrowshow = 9
        self.lencheck = 0
        self.logscroll = None ## Link from maingame after creation of both object

    def changemode(self, mode):
        self.mode = mode
        self.lencheck = len((self.battlelog, self.battalionlog, self.leaderlog, self.squadlog)[self.mode])
        self.currentstartrow = 0
        if self.lencheck > self.maxrowshow:
            self.currentstartrow = self.lencheck - self.maxrowshow
        self.logscroll.currentrow = self.currentstartrow
        self.logscroll.changeimage(logsize=self.lencheck)
        self.recreateimage()

    def cleartab(self, alltab = False):
        self.lencheck = 0
        self.currentstartrow = 0
        currentlog = (self.battlelog, self.battalionlog, self.leaderlog, self.squadlog)[self.mode]
        currentlog.clear()
        if alltab:
            for log in (self.battlelog, self.battalionlog, self.leaderlog, self.squadlog):
                log.clear()
        self.logscroll.currentrow = self.currentstartrow
        self.logscroll.changeimage(logsize=self.lencheck)
        self.recreateimage()

    def recreateimage(self):
        thislog = (self.battlelog, self.battalionlog, self.leaderlog, self.squadlog)[self.mode]
        self.image = self.image_original.copy()
        row = 10
        for index, text in enumerate(thislog[self.currentstartrow:]):
            if index == self.maxrowshow: break
            textsurface = self.font.render(text[1], 1, (0, 0, 0))
            textrect = textsurface.get_rect(topleft=(50, row))
            self.image.blit(textsurface, textrect)
            row += 20

    def addlog(self, log, modelist):
        """Add log to appropiate event log, the log must be in list format following this rule [who (gameid), logtext]"""
        imagechange = False
        atlastrow = False
        if self.currentstartrow + self.maxrowshow >= self.lencheck:
            atlastrow = True
        for mode in modelist:
            thislog = (self.battlelog, self.battalionlog, self.leaderlog, self.squadlog)[mode]
            textoutput = ": " + log[1]
            if len(textoutput) <= 47:
                thislog.append([log[0], textoutput])
            else:  ## Cut the text log into multiple row
                cutspace = [index for index, letter in enumerate(textoutput) if letter == " "]
                howmanyloop = len(textoutput) / 47
                if howmanyloop.is_integer() == False:
                    howmanyloop = int(howmanyloop) + 1
                startingindex = 0
                for run in range(1, howmanyloop + 1):
                    textcutnumber = [number for number in cutspace if number <= run * 47]
                    cutnumber = textcutnumber[-1]
                    finaltextoutput = textoutput[startingindex:cutnumber]
                    if run == howmanyloop:
                        finaltextoutput = textoutput[startingindex:]
                    if run == 1:
                        thislog.append([log[0], finaltextoutput])
                    else: thislog.append([-1, finaltextoutput])
                    startingindex = cutnumber + 1
            if len(thislog) > 1000:
                del thislog[0]
            if mode == self.mode:
                imagechange = True
        if imagechange:
            self.lencheck = len((self.battlelog, self.battalionlog, self.leaderlog, self.squadlog)[self.mode])
            if atlastrow and self.lencheck > 9:
                self.currentstartrow = self.lencheck - self.maxrowshow
                self.logscroll.currentrow = self.currentstartrow
            self.logscroll.changeimage(logsize=self.lencheck)
            self.recreateimage()

class Uiscroller(pygame.sprite.Sprite):
    def __init__(self, pos, uiheight, maxrowshow, layer=11):
        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.uiheight = uiheight
        self.pos = pos
        self.image = pygame.Surface((15, self.uiheight))
        self.image.fill((255,255,255))
        self.image_original = self.image.copy()
        self.buttoncolour = (100,100,100)
        pygame.draw.rect(self.image, self.buttoncolour, (0, 0, self.image.get_width(), self.uiheight))
        self.rect = self.image.get_rect(topright=self.pos)
        self.currentrow = 0
        self.maxrowshow = maxrowshow
        self.logsize = 0

    def newimagecreate(self):
        percentrow = 0
        maxrow = 100
        self.image = self.image_original.copy()
        if self.logsize > 0:
            percentrow = self.currentrow * 100 / self.logsize
        # if self.currentrow + self.maxrowshow < self.logsize:
        if self.logsize > 0:
            maxrow = (self.currentrow + self.maxrowshow) * 100 / self.logsize
        maxrow = maxrow - percentrow
        pygame.draw.rect(self.image, self.buttoncolour, (0, int(self.uiheight * percentrow / 100), self.image.get_width(), int(self.uiheight * maxrow / 100)))

    def changeimage(self, newrow = None, logsize = None):
        """New row is input of scrolling by user to new row, logsize is changing based on adding more log or clear"""
        if logsize is not None and self.logsize != logsize:
            self.logsize = logsize
            self.newimagecreate()
        elif newrow is not None and self.currentrow != newrow: ## Accept from both wheeling scroll and drag scroll bar
            self.currentrow = newrow
            self.newimagecreate()

    def update(self, mouse_pos):
            """User input update"""
            self.mouse_value = (mouse_pos[1] - self.pos[1]) * 100 / self.uiheight ## Find what percentage of mouse_pos at the scroll bar (0 = top, 100 = bottom)
            if self.mouse_value > 100:
                self.mouse_value = 100
            if self.mouse_value < 0:
                self.mouse_value = 0
            newrow = int(self.logsize * self.mouse_value / 100)
            if self.logsize > self.maxrowshow and newrow > self.logsize - self.maxrowshow:
                newrow = self.logsize - self.maxrowshow
            self.changeimage(newrow)
            return self.currentrow

class Armyselect(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)
        self.currentrow = 0
        self.maxrowshow = 2
        self.maxcolumnshow = 6
        self.logsize = 0

class Armyicon(pygame.sprite.Sprite):
    def __init__(self, pos, army):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.army = army
        army.icon = self
        self.pos = pos
        self.leaderimage = self.army.leader[0].image.copy()
        self.leaderimage = pygame.transform.scale(self.leaderimage, (int(self.leaderimage.get_width()/1.5), int(self.leaderimage.get_height()/1.5)))
        self.image = pygame.Surface((self.leaderimage.get_width() + 4, self.leaderimage.get_height() + 4))
        self.image.fill((0, 0, 0))
        centerimage = pygame.Surface((self.leaderimage.get_width() + 2, self.leaderimage.get_height() + 2))
        centerimage.fill((144, 167, 255))
        if self.army.gameid >= 2000:
            centerimage.fill((255, 114, 114))
        imagerect = centerimage.get_rect(topleft=(1,1))
        self.image.blit(centerimage, imagerect)
        self.leaderrect = self.leaderimage.get_rect(center=(self.image.get_width()/2, self.image.get_height()/2))
        self.image.blit(self.leaderimage, self.leaderrect)
        self.rect = self.image.get_rect(center=self.pos)

    def changepos(self, pos):
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def changeimage(self, newimage = None, changeside = False):
        if changeside:
            self.image.fill((144, 167, 255))
            if self.army.gameid >= 2000:
                self.image.fill((255, 114, 114))
            self.image.blit(self.leaderimage, self.leaderrect)
        if newimage is not None:
            self.leaderimage = newimage
            self.image.blit(self.leaderimage, self.leaderrect)

class Timer(pygame.sprite.Sprite):
    def __init__(self, pos, textsize = 20):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.pos = pos
        self.timer = 0
        self.oldtimer = 0
        self.timenum = datetime.timedelta(seconds=self.timer)
        self.image = pygame.Surface((100,30), pygame.SRCALPHA)
        self.image_original = self.image.copy()
        self.timersurface = self.font.render(str(round(self.timer,2)), 1, (0, 0, 0))
        self.timerrect = self.timersurface.get_rect(topleft=(5,5))
        self.image.blit(self.timersurface, self.timerrect)
        self.rect = self.image.get_rect(topleft=pos)

    def timerupdate(self, dt):
        if dt > 0:
            self.timer += dt
            if self.timer - self.oldtimer > 1:
                self.oldtimer = self.timer
                self.image = self.image_original.copy()
                self.timenum = datetime.timedelta(seconds=self.timer)
                timenum = str(self.timenum).split(".")[0]
                self.timersurface = self.font.render(timenum, 1, (0, 0, 0))
                self.image.blit(self.timersurface, self.timerrect)

class Timeui(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.image = image.copy()
        self.rect = self.image.get_rect(topleft=pos)

class Speednumber(pygame.sprite.Sprite):
    def __init__(self, pos, speed, textsize = 20):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.pos = pos
        self.image = pygame.Surface((50,30), pygame.SRCALPHA)
        self.image_original = self.image.copy()
        self.speed = speed
        self.timersurface = self.font.render(str(self.speed), 1, (0, 0, 0))
        self.timerrect = self.timersurface.get_rect(topleft=(3,3))
        self.image.blit(self.timersurface, self.timerrect)
        self.rect = self.image.get_rect(center=pos)

    def speedupdate(self, newspeed):
        self.image = self.image_original.copy()
        self.speed = newspeed
        self.timersurface = self.font.render(str(self.speed), 1, (0, 0, 0))
        self.image.blit(self.timersurface, self.timerrect)