import pygame
import pygame.freetype


class uibutton(pygame.sprite.Sprite):
    def __init__(self, X, Y, image, event):
        self._layer = 8
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.X, self.Y = X, Y
        self.image = image
        self.event = event
        self.rect = self.image.get_rect(center=(self.X, self.Y))
        self.mouse_over = False
    #
    # def draw(self, gamescreen):
    #     gamescreen.blit(self.image, self.rect)

class switchuibutton(pygame.sprite.Sprite):
    def __init__(self, X, Y, image):
        self._layer = 8
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.X, self.Y = X, Y
        self.images = image
        self.image = self.images[0]
        self.event = 0
        self.rect = self.image.get_rect(center=(self.X, self.Y))
        self.mouse_over = False
        self.lastevent = 0

    def update(self):
        if self.event != self.lastevent:
            self.image = self.images[self.event]
            self.rect = self.image.get_rect(center=(self.X, self.Y))
            self.lastevent = self.event


class iconpopup(pygame.sprite.Sprite):
    def __init__(self, X, Y, image, event, gameui, itemid=""):
        self._layer = 8
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
        self._layer = 8
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.X, self.Y = X, Y
        self.text = text
        self.image = image
        self.icon = icon
        self.uitype = uitype
        self.value = [-1, -1]
        self.lastvalue = 0
        self.lastvalue2 = 0
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
                             10: "Fighting", 11: "shooting", 68: "Dancing", 69: "Partying", 96: "Retreating", 97: "Collapse", 98: "Retreating",
                             99: "Broken", 100: "Destroyed"}
            self.options2 = {0: "Broken", 1: "Retreating", 2: "Breaking", 3: "Poor", 4: "Wavering", 5: "Balanced",
                             6: "Steady", 7: "Fine", 8: "Confident", 9: "Eager", 10: "Ready"}
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
                              "Melee Defence: ", 'Range Defence: ', 'Armour: ', 'Speed: ', "Accuracy: ",
                              "Range: ", "Ammunition: ", "Reload Speed: ", "Charge Power: ", "Charge Defence:"]
            self.qualitytext = ["Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect"]
            self.terrainlist = ["Temperate", "Tropical", "Volcanic", "Desert", "Arctic", "Blight", "Void", "Demonic", "Death", "Shallow water", "Deep water"]
            self.featurelist = ["Grassland", "Draught", "Bushland", "Forest", "Inland Water", "Road", "Building", "Farm", "Wall", "Mana Flux",
                                "Creeping Rot", "", "Savanna", "Draught", "Tropical Shrubland", "Jungle", "Inland Water", "Road", "Building", "Farm",
                                "Wall", "Heat Mana", "Creeping Rot", "", "Volcanic Soil", "", "", "", "", "Road", "", "Fertile Farm", "Wall",
                                "Fire Mana", "Creeping Rot", "", "Desert Plain", "Desert Sand", "Desert Shrubland", "Desert Forest", "Oasis",
                                "Sand Road", "Desert Dwelling", "Desert Farm", "Wall", "Earth Mana", "Creeping Rot", "", "Snow", "Tundra",
                                "Arctic Shrubland", "Arctic Forest", "Frozen Water", "Snow Road", "Warm Shelter", "Arctic Farm", "Wall", "Ice Mana",
                                "Creeping Rot", "", "", "", "", "", "Poisoned Water", "", "", "", "Wall", "Poisoned Mana", "Creeping Rot", "", "",
                                "Void", "", "", "", "", "", "", "", "Leyline", "Creeping Rot", "", "", "", "", "", "", "", "", "", "Demonic Wall", "",
                                "Creeping Rot", "", "", "", "", "", "", "", "", "", "Death Wall", "", "Rotten Land", "", "", "", "Marsh", "Swamp",
                                "Water", "", "", "", "", "Cold Mana", "Creeping Rot", "", "Fresh Water", "Salt Water", "Coral Reef",
                                "Underwater Forest", "", "Sunken Road", "Undercity", "", "", "Water Mana", "Creeping Rot", "", ""]
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
            self.value = who.valuefortopbar
            if self.value[3] in self.options1:
                self.value[3] = self.options1[self.value[3]]
            # if type(self.value[2]) != str:
            self.value[2] = round(self.value[2] / 10)
            if self.value[2] in self.options2:
                self.value[2] = self.options2[self.value[2]]
            self.value[1] = round(self.value[1] / 10)
            if self.value[1] in self.options3:
                self.value[1] = self.options3[self.value[1]]
            if self.value != self.lastvalue or splithappen == True:
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
            if who.gameid != self.lastwho or splithappen == True:  ## only redraw leader circle when change unit (will add condition if leader die or changed later)
                usecolour = self.white
                self.leaderpiclist = []
                self.image = self.image_original.copy()
                if who.gameid >= 2000:
                    usecolour = self.black
                if who.commander == True:
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
            if self.lastauth != who.authority or who.gameid != self.lastwho or splithappen == True:  ## authority number
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
                          int(who.range), who.ammo, str(int(who.reloadtime)) + " (" + str(who.reload) + ")", who.charge, who.chargedef,
                          who.description]
            self.value2 = [who.trait, who.skill, who.skillcooldown, who.skilleffect, who.statuseffect]
            self.description = self.value[-1]
            if type(self.description) == list: self.description = self.description[0]
            if self.value != self.lastvalue or changeoption == 1 or who.gameid != self.lastwho:
                self.image = self.image_original.copy()
                row = 0
                self.name = self.value[0]
                leadertext = ""
                if who.leader != None:
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
                    self.value, text = self.value[0:-1], self.fronttext[1:]
                    for n, value in enumerate(self.value[1:]):
                        self.textsurface = self.font.render(text[n] + str(value), 1, (0, 0, 0))
                        self.textrect = self.textsurface.get_rect(
                            midleft=(self.image.get_rect()[0] + positionx, self.image.get_rect()[1] + position))
                        self.image.blit(self.textsurface, self.textrect)
                        position += 20
                        row += 1
                        if row == 9: positionx, position = 200, 35
                elif self.option == 0:  ## description card
                    self.blit_text(self.image, self.description, (42, 25), self.fontlong)
                elif self.option == 2:  ## unit card
                    position2 = positionx + 20
                    for trait in self.value2[0]:  ## property list
                        # if trait in self.value2[2] : cd = int(self.value2[2][trait])
                        # self.textsurface = self.font.render("--Unit Properties--", 1, (0, 0, 0))
                        if trait != 0:
                            self.textsurface = self.font.render(str(self.value2[0][trait][0]), 1, (0, 0, 0))
                            self.textrect = self.textsurface.get_rect(
                                midleft=(self.image.get_rect()[0] + position2, self.image.get_rect()[1] + position))
                            self.image.blit(self.textsurface, self.textrect)
                            position += 20
                    for skill in self.value2[1]:  ## skill cooldown
                        if skill in self.value2[2]:
                            cd = int(self.value2[2][skill])
                        else:
                            cd = 0
                        self.textsurface = self.font.render(str(self.value2[1][skill][0]) + ":" + str(cd), 1, (0, 0, 0))
                        self.textrect = self.textsurface.get_rect(
                            midleft=(self.image.get_rect()[0] + position2, self.image.get_rect()[1] + position))
                        self.image.blit(self.textsurface, self.textrect)
                        # position2 += 25
                        # if position2 >= 90:
                        #     position2 = positionx + 20
                        position += 20
                    # position += 20
                    position2 = positionx + 20
                    for status in self.value2[3]:  ## skill effect list
                        self.textsurface = self.font.render(str(self.value2[3][status][0]) + ": " + str(int(self.value2[3][status][3])), 1, (0, 0, 0))
                        self.textrect = self.textsurface.get_rect(
                            midleft=(self.image.get_rect()[0] + position2, self.image.get_rect()[1] + position))
                        self.image.blit(self.textsurface, self.textrect)
                        # position2 += 25
                        # if position2 >= 90:
                        #     position2 = positionx + 20
                        position += 20
                    # position += 20
                    position2 = positionx + 20
                    for status in self.value2[4]:  ## status list
                        self.textsurface = self.font.render(str(self.value2[4][status][0]) + ": " + str(int(self.value2[4][status][3])), 1, (0, 0, 0))
                        self.textrect = self.textsurface.get_rect(
                            midleft=(self.image.get_rect()[0] + position2, self.image.get_rect()[1] + position))
                        self.image.blit(self.textsurface, self.textrect)
                        # position2 += 25
                        # if position2 >= 90:
                        #     position2 = positionx + 20
                        position += 20
                elif self.option == 3:  ## equipment and terrain
                    terrain = self.terrainlist[who.battalion.terrain]
                    if who.battalion.feature != None: terrain += "/" + self.featurelist[who.battalion.feature]
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
                    for text in textvalue:
                        self.textsurface = self.font.render(str(text), 1, (0, 0, 0))
                        self.textrect = self.textsurface.get_rect(
                            midleft=(self.image.get_rect()[0] + positionx, self.image.get_rect()[1] + position))
                        self.image.blit(self.textsurface, self.textrect)
                        position += 20
                self.lastvalue = self.value
                self.lastvalue2 != self.value2
        self.lastwho = who.gameid


class fpscount(pygame.sprite.Sprite):
    def __init__(self):
        self._layer = 10
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


class minimap(pygame.sprite.Sprite):
    def __init__(self, image, camera):
        self._layer = 8
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        scalewidth = self.image.get_width() / 5
        scaleheight = self.image.get_height() / 5
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image = pygame.transform.scale(self.image_original, (int(self.dim[0]), int(self.dim[1])))
        self.image_original = self.image.copy()
        self.enemydot = pygame.Surface(4,4).fill((0, 0, 0))
        self.playerdot = pygame.Surface(4,4).fill((0, 0, 0))
        enemy = pygame.Surface(2,2).fill((255, 0, 0))
        player = pygame.Surface(2,2).fill((0, 0, 255))
        rect = enemy.get_rect(center=self.enemydot.get_rect().center)
        self.enemydot.blit(enemy, rect)
        self.playerdot.blit(player, rect)
        self.playerpos = []
        self.enemypos = []
        self.cameraborder = pygame.Surface((camera.image.get_width(), camera.image.get_height()), pygame.SRCALPHA)
        pygame.draw.rect(self.cameraborder, (0, 0, 0), (0, 0, self.cameraborder.get_width(), self.cameraborder.get_height()), 4)
        self.cameraborder_original = self.cameraborder.copy()
        self.camerapos = camera.pos
        self.lastscale = 10

    def update(self, viewmode, camerapos, playerposlist, enemyposlist):
        if self.playerpos != playerposlist or self.enemypos != enemyposlist or self.camerapos != camerapos or self.lastscale != viewmode:
            self.playerpos = playerposlist
            self.enemypos = enemyposlist
            self.image = self.image_original.copy()
            for player in playerposlist:
                scaledpos = player / 50
                rect = self.playerdot.get_rect(center=scaledpos)
                self.image.blit(self.playerdot, rect)
            for enemy in enemyposlist:
                scaledpos = enemy / 50
                rect = self.enemydot.get_rect(center=scaledpos)
                self.image.blit(self.enemydot, rect)
            if self.lastscale != viewmode:
                self.cameraborder = self.cameraborder_original.copy()
                camerawidth = self.cameraborder.get_width() * 10 / viewmode
                cameraheight = self.cameraborder.get_height() * 10 / viewmode
                cameradim = pygame.Vector2(camerawidth, cameraheight)
                self.cameraborder = pygame.transform.scale(self.image_original, (int(cameradim[0]), int(cameradim[1])))
                self.lastscale = viewmode
            camerarect = self.cameraborder.get_rect(center=camerapos)
            self.image.blit(self.cameraborder, camerarect)
