import datetime

import pygame
import pygame.freetype


class Uibutton(pygame.sprite.Sprite):
    def __init__(self, x, y, image, event, newlayer=10):
        self._layer = newlayer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = (x, y)
        self.image = image
        self.event = event
        self.rect = self.image.get_rect(center=self.pos)
        self.mouse_over = False
    #
    # def draw(self, gamescreen):
    #     gamescreen.blit(self.image, self.rect)


class Switchuibutton(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = (x, y)
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
    def __init__(self, x, y, image, event, gameui, itemid=""):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.x, self.y = x, y
        self.image = image
        self.event = 0
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.mouse_over = False
        self.itemid = itemid
    #
    # def draw(self, gamescreen):
    #     gamescreen.blit(self.image, self.rect)


class Gameui(pygame.sprite.Sprite):
    def __init__(self, x, y, image, icon, uitype, text="", textsize=16):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.x, self.y = x, y
        self.text = text
        self.image = image
        self.icon = icon
        self.ui_type = uitype
        self.value = [-1, -1]
        self.last_value = 0
        self.option = 0
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.lastwho = -1  # parentunit last showed, start with -1 which mean any new clicked will show up at start
        if self.ui_type == "topbar":  # setup variable for topbar ui
            position = 10
            for ic in self.icon:  # Blit icon into topbar ui
                self.icon_rect = ic.get_rect(
                    topleft=(self.image.get_rect()[0] + position, self.image.get_rect()[1]))
                self.image.blit(ic, self.icon_rect)
                position += 90
            self.options2 = {0: "Broken", 1: "Fleeing", 2: "Breaking", 3: "Poor", 4: "Wavering", 5: "Balanced",
                             6: "Steady", 7: "Fine", 8: "Confident", 9: "Eager", 10: "Ready", 11: "Merry", 12: "Elated", 13: "Ecstatic",
                             14: "Inspired", 15: "Fervent"}  # parentunit morale state name
            self.options3 = {0: "Collapse", 1: "Exhausted", 2: "Severed", 3: "Very Tired", 4: "Tired", 5: "Winded", 6: "Moderate",
                             7: "Alert", 8: "Warmed Up", 9: "Active", 10: "Fresh"}  # parentunit stamina state name

        elif self.ui_type == "commandbar":  # setup variable for command bar ui
            self.icon_rect = self.icon[6].get_rect(
                center=(self.image.get_rect()[0] + self.image.get_size()[0] / 1.1, self.image.get_rect()[1] + 40))
            self.image.blit(self.icon[6], self.icon_rect)
            self.white = [self.icon[0], self.icon[1], self.icon[2], self.icon[3], self.icon[4], self.icon[5]]  # team 1 white chess head
            self.black = [self.icon[7], self.icon[8], self.icon[9], self.icon[10], self.icon[11], self.icon[12]]  # team 2 black chess head
            self.lastauth = 0

        elif self.ui_type == "unitcard":  # setup variable for subunit card ui
            self.fonthead = pygame.font.SysFont("curlz", textsize + 4)
            self.fonthead.set_italic(True)
            self.fontlong = pygame.font.SysFont("helvetica", textsize - 2)
            self.front_text = ["", "Troop: ", "Stamina: ", "Morale: ", "Discipline: ", "Melee Attack: ",
                               "Melee Defense: ", "Range Defense: ", "Armour: ", "Speed: ", "Accuracy: ",
                               "Range: ", "Ammunition: ", "Reload: ", "Charge Power: ", "Charge Defense: ", "Mental: "]  # stat name
            self.subunit_state = {0: "Idle", 1: "Walk", 2: "Run", 3: "Walk (M)", 4: "Run (M)", 5: "Walk (R)", 6: "Run (R)", 10: "Melee", 11: "Shoot",
                                  12: "Walk (S)", 13: "Run (S)", 95: "Disobey", 96: "Flee", 97: "Rest", 98: "Flee", 99: "Broken", 100: "Dead"}
            self.quality_text = ("Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect")  # item quality name
            self.leader_state_text = {96: "Flee", 97: "POW", 98: "MIA", 99: "WIA", 100: "KIA"}  # leader state name
            self.terrain_list = ["Temperate", "Tropical", "Volcanic", "Desert", "Arctic", "Blight", "Void", "Demonic", "Death", "Shallow water",
                                 "Deep water"]  # terrain climate name
        self.image_original = self.image.copy()

    def longtext(self, surface, text, pos, font, color=pygame.Color("black")):
        """Blit long text into seperate row of text"""
        words = [word.split(" ") for word in text.splitlines()]  # 2D array where each row is a list of words
        space = font.size(" ")[0]  # the width of a space
        maxwidth, maxheight = surface.get_size()
        x, y = pos
        for line in words:
            for word in line:
                word_surface = font.render(word, 0, color)
                wordwidth, wordheight = word_surface.get_size()
                if x + wordwidth >= maxwidth:
                    x = pos[0]  # reset x
                    y += wordheight  # start on new row.
                surface.blit(word_surface, (x, y))
                x += wordwidth + space
            x = pos[0]  # reset x
            y += wordheight  # start on new row

    def valueinput(self, who, weaponlist="", armourlist="", button="", changeoption=0, splithappen=False):
        for thisbutton in button:
            thisbutton.draw(self.image)
        position = 65
        if self.ui_type == "topbar":
            self.value = ["{:,}".format(who.troopnumber) + " (" + "{:,}".format(who.maxhealth) + ")", who.staminastate, who.moralestate, who.state]
            if self.value[3] in self.options1:  # Check subunit state and blit name
                self.value[3] = self.options1[self.value[3]]
            # if type(self.value[2]) != str:

            self.value[2] = round(self.value[2] / 10)  # morale state
            if self.value[2] in self.options2:  # Check if morale state in the list and blit the name
                self.value[2] = self.options2[self.value[2]]
            elif self.value[2] > 15:  # if morale somehow too high use the highest morale state one
                self.value[2] = self.options2[15]

            self.value[1] = round(self.value[1] / 10)  # stamina state
            if self.value[1] in self.options3:  # Check if stamina state and blit the name
                self.value[1] = self.options3[self.value[1]]

            if self.value != self.last_value or splithappen:  # only blit new text when value change or subunit split
                self.image = self.image_original.copy()
                for value in self.value:  # blit value text
                    self.textsurface = self.font.render(str(value), True, (0, 0, 0))
                    self.textrect = self.textsurface.get_rect(
                        center=(self.image.get_rect()[0] + position, self.image.get_rect()[1] + 25))
                    self.image.blit(self.textsurface, self.textrect)
                    if position >= 200:
                        position += 50
                    else:
                        position += 95
                self.last_value = self.value
        # for line in range(len(label)):
        #     surface.blit(label(line), (position[0], position[1] + (line * fontsize) + (15 * line)))

        elif self.ui_type == "commandbar":
            if who.gameid != self.lastwho or splithappen:  # only redraw leader circle when change subunit
                usecolour = self.white  # colour of the chess icon for leader, white for team 1
                if who.team == 2:  # black for team 2
                    usecolour = self.black
                self.image = self.image_original.copy()
                self.image.blit(who.coa, who.coa.get_rect(topleft=self.image.get_rect().topleft))  # blit coa

                if who.commander:  # commander parentunit use king and queen icon
                    # main general
                    self.icon_rect = usecolour[0].get_rect(
                        center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2.1, self.image.get_rect()[1] + 45))
                    self.image.blit(usecolour[0], self.icon_rect)

                    # sub commander/strategist role
                    self.icon_rect = usecolour[1].get_rect(
                        center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2.1, self.image.get_rect()[1] + 140))
                    self.image.blit(usecolour[1], self.icon_rect)

                else:  # the rest use rook and bishop
                    # general
                    self.icon_rect = usecolour[2].get_rect(
                        center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2.1, self.image.get_rect()[1] + 45))
                    self.image.blit(usecolour[2], self.icon_rect)

                    # sub general/special advisor role
                    self.icon_rect = usecolour[5].get_rect(
                        center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2.1, self.image.get_rect()[1] + 140))
                    self.image.blit(usecolour[5], self.icon_rect)

                self.icon_rect = usecolour[3].get_rect(center=(  # left sub general
                    self.image.get_rect()[0] - 10 + self.image.get_size()[0] / 3.1,
                    self.image.get_rect()[1] - 10 + self.image.get_size()[1] / 2.2))
                self.image.blit(usecolour[3], self.icon_rect)
                self.icon_rect = usecolour[0].get_rect(center=(  # right sub general
                    self.image.get_rect()[0] - 10 + self.image.get_size()[0] / 1.4,
                    self.image.get_rect()[1] - 10 + self.image.get_size()[1] / 2.2))
                self.image.blit(usecolour[4], self.icon_rect)

                self.image_original2 = self.image.copy()
            if self.lastauth != who.authority or who.gameid != self.lastwho or splithappen:  # authority number change only when not same as last
                self.image = self.image_original2.copy()
                self.textsurface = self.font.render(str(who.authority), True, (0, 0, 0))
                self.textrect = self.textsurface.get_rect(
                    center=(self.image.get_rect()[0] + self.image.get_size()[0] / 1.12, self.image.get_rect()[1] + 83))
                self.image.blit(self.textsurface, self.textrect)
                self.lastauth = who.authority

        elif self.ui_type == "unitcard":
            position = 15  # starting row
            positionx = 45  # starting point of text
            self.value = [who.name, "{:,}".format(who.troopnumber) + " (" + "{:,}".format(who.maxtroop) + ")",
                          str(int(who.stamina)) + ", " + self.subunit_state[who.state], int(who.morale),
                          int(who.discipline), int(who.attack), int(who.meleedef), int(who.rangedef), int(who.armour), int(who.speed),
                          int(who.accuracy), int(who.shootrange), who.magazine_left,
                          str(int(who.reload_time)) + "/" + str(int(who.reload)) + ": " + str(who.ammo_now),
                          int(who.charge), int(who.chargedef), who.mentaltext, int(who.temp_count)]
            self.value2 = [who.trait, who.skill, who.skill_cooldown, who.skill_effect, who.status_effect]
            self.description = who.description
            if type(self.description) == list:
                self.description = self.description[0]
            if self.value != self.last_value or changeoption == 1 or who.gameid != self.lastwho:
                self.image = self.image_original.copy()
                row = 0
                self.name = self.value[0]
                leadertext = ""
                if who.leader is not None:
                    leadertext = "/" + str(who.leader.name)
                    if who.leader.state in self.leader_state_text:
                        leadertext += " " + "(" + self.leader_state_text[who.leader.state] + ")"
                self.textsurface = self.fonthead.render(self.name + leadertext, True, (0, 0, 0))  # subunit and leader name at the top
                self.textrect = self.textsurface.get_rect(
                    midleft=(self.image.get_rect()[0] + positionx, self.image.get_rect()[1] + position))
                self.image.blit(self.textsurface, self.textrect)
                row += 1
                position += 20
                if self.option == 1:  # stat card
                    # self.icon_rect = self.icon[0].get_rect(
                    #     center=(
                    #     self.image.get_rect()[0] + self.image.get_size()[0] -20, self.image.get_rect()[1] + 40))
                    # deletelist = [i for i,x in enumerate(self.value) if x == 0]
                    # if len(deletelist) != 0:
                    #     for i in sorted(deletelist, reverse = True):
                    #         self.value.pop(i)
                    #         text.pop(i)
                    newvalue, text = self.value[0:-1], self.front_text[1:]
                    for n, value in enumerate(newvalue[1:]):
                        self.textsurface = self.font.render(text[n] + str(value), True, (0, 0, 0))
                        self.textrect = self.textsurface.get_rect(
                            midleft=(self.image.get_rect()[0] + positionx, self.image.get_rect()[1] + position))
                        self.image.blit(self.textsurface, self.textrect)
                        position += 20
                        row += 1
                        if row == 9:
                            positionx, position = 200, 35
                elif self.option == 0:  # description card
                    self.longtext(self.image, self.description, (42, 25), self.fontlong)  # blit long description
                elif self.option == 3:  # equipment and terrain
                    # v Terrain text
                    terrain = self.terrain_list[who.terrain]
                    if who.feature is not None:
                        terrain += "/" + self.featurelist[who.feature]
                    # ^ End terrain text

                    # v Equipment text
                    textvalue = [
                        self.quality_text[who.meleeweapon[1]] + " " + str(weaponlist.weapon_list[who.meleeweapon[0]][0]) + ": D " + str(who.dmg)
                        + ", P " + str(int((1 - who.melee_penetrate) * 100)) + "%, W " + str(weaponlist.weapon_list[who.meleeweapon[0]][3]),
                        self.quality_text[who.armourgear[1]] + " " + str(armourlist.armour_list[who.armourgear[0]][0]) + ": A "
                        + str(int(who.armour)) + ", W " + str(armourlist.armour_list[who.armourgear[0]][2]),
                        "Total Weight:" + str(who.weight), "Terrain:" + terrain, "Height:" + str(who.height),
                        "Temperature:" + str(int(who.temp_count))]

                    if who.rangeweapon[0] != 1:  # only add range weapon if it is not none
                        textvalue.insert(1,
                                         self.quality_text[who.rangeweapon[1]] + " " + str(weaponlist.weapon_list[who.rangeweapon[0]][0] + ": D "
                                                                                           + str(who.rangedmg) + ", P " + str(
                                             int((1 - who.range_penetrate) * 100)) + "%, W "
                                                                                           + str(weaponlist.weapon_list[who.rangeweapon[0]][3])))

                    if "None" not in who.mount:  # if mount is not the None mount id 1
                        armourtext = "//" + who.mountarmour[0]
                        if "None" in who.mountarmour[0]:
                            armourtext = ""
                        textvalue.insert(3, "Mount:" + who.mountgrade[0] + " " + who.mount[0] + armourtext)
                    # ^ End equipment text

                    for text in textvalue:
                        self.textsurface = self.font.render(str(text), 1, (0, 0, 0))
                        self.textrect = self.textsurface.get_rect(
                            midleft=(self.image.get_rect()[0] + positionx, self.image.get_rect()[1] + position))
                        self.image.blit(self.textsurface, self.textrect)
                        position += 20
                self.last_value = self.value
        self.lastwho = who.gameid


class Skillcardicon(pygame.sprite.Sprite):
    cooldown = None
    activeskill = None

    def __init__(self, image, pos, icontype, gameid=None):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.icontype = icontype  # type 0 is trait 1 is kill
        self.gameid = gameid  # ID of the skill
        self.pos = pos  # pos of the skill on ui
        self.font = pygame.font.SysFont("helvetica", 18)
        self.cooldown_check = 0  # cooldown number
        self.active_check = 0  # active timer number
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.image_original = self.image.copy()  # keep original image without number
        self.cooldown_rect = self.image.get_rect(topleft=(0, 0))

    def numberchange(self, number):
        """Change number more than thousand to K digit e.g. 1k = 1000"""
        return str(round(number / 1000, 1)) + "K"

    def iconchange(self, cooldown, activetimer):
        """Show active effect timer first if none show cooldown"""
        if activetimer != self.active_check:
            self.active_check = activetimer  # renew number
            self.image = self.image_original.copy()
            if self.active_check > 0:
                rect = self.image.get_rect(topleft=(0, 0))
                self.image.blit(self.activeskill, rect)
                outputnumber = str(self.active_check)
                if self.active_check >= 1000:
                    outputnumber = self.numberchange(outputnumber)
                self.textsurface = self.font.render(outputnumber, 1, (0, 0, 0))  # timer number
                self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
                self.image.blit(self.textsurface, self.textrect)

        elif cooldown != self.cooldown_check and self.active_check == 0:  # Cooldown only get blit when skill is not active
            self.cooldown_check = cooldown
            self.image = self.image_original.copy()
            if self.cooldown_check > 0:
                self.image.blit(self.cooldown, self.cooldown_rect)
                outputnumber = str(self.cooldown_check)
                if self.cooldown_check >= 1000:  # change thousand number into k (1k,2k)
                    outputnumber = self.numberchange(outputnumber)
                self.textsurface = self.font.render(outputnumber, 1, (0, 0, 0))
                self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
                self.image.blit(self.textsurface, self.textrect)


class Effectcardicon(pygame.sprite.Sprite):

    def __init__(self, image, pos, icontype, gameid=None):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.icontype = icontype
        self.gameid = gameid
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
        self.rect = self.image.get_rect(center=(30, 110))
        fps = "60"
        fps_text = self.font.render(fps, True, pygame.Color("blue"))
        self.textrect = fps_text.get_rect(center=(25, 25))

    def fpsshow(self, clock):
        """Update current fps"""
        self.image = self.image_original.copy()
        fps = str(int(clock.get_fps()))
        fps_text = self.font.render(fps, True, pygame.Color("blue"))
        self.image.blit(fps_text, self.textrect)


class Selectedsquad(pygame.sprite.Sprite):
    image = None

    def __init__(self, pos, layer=20):
        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect(topleft=pos)

    def pop(self, pos):
        """pop out at the selected subunit in inspect uo"""
        self.rect = self.image.get_rect(topleft=pos)


class Minimap(pygame.sprite.Sprite):
    def __init__(self, pos):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos

        self.team2dot = pygame.Surface((8, 8))  # dot for team2 subunit
        self.team2dot.fill((0, 0, 0))  # black corner
        self.team1dot = pygame.Surface((8, 8))  # dot for team1 subunit
        self.team1dot.fill((0, 0, 0))  # black corner
        team2 = pygame.Surface((6, 6))  # size 6x6
        team2.fill((255, 0, 0))  # red rect
        team1 = pygame.Surface((6, 6))
        team1.fill((0, 0, 255))  # blue rect
        rect = self.team2dot.get_rect(topleft=(1, 1))
        self.team2dot.blit(team2, rect)
        self.team1dot.blit(team1, rect)
        self.team1pos = []
        self.team2pos = []

        self.lastscale = 10

    def drawimage(self, image, camera):
        self.image = image
        scalewidth = self.image.get_width() / 5
        scaleheight = self.image.get_height() / 5
        self.dim = pygame.Vector2(scalewidth, scaleheight)
        self.image = pygame.transform.scale(self.image, (int(self.dim[0]), int(self.dim[1])))
        self.image_original = self.image.copy()
        self.cameraborder = [camera.image.get_width(), camera.image.get_height()]
        self.camerapos = camera.pos
        self.rect = self.image.get_rect(bottomright=self.pos)

    def update(self, viewmode, camerapos, team1poslist, team2poslist):
        """update parentunit dot on map"""
        if self.team1pos != team1poslist.values() or self.team2pos != team2poslist.values() or \
                self.camerapos != camerapos or self.lastscale != viewmode:
            self.team1pos = team1poslist.values()
            self.team2pos = team2poslist.values()
            self.camerapos = camerapos
            self.image = self.image_original.copy()
            for team1 in team1poslist.values():
                scaledpos = team1 / 5
                rect = self.team1dot.get_rect(center=scaledpos)
                self.image.blit(self.team1dot, rect)
            for team2 in team2poslist.values():
                scaledpos = team2 / 5
                rect = self.team2dot.get_rect(center=scaledpos)
                self.image.blit(self.team2dot, rect)
            pygame.draw.rect(self.image, (0, 0, 0), (camerapos[1][0] / 5 / viewmode, camerapos[1][1] / 5 / viewmode,
                                                     self.cameraborder[0] * 10 / viewmode / 50, self.cameraborder[1] * 10 / viewmode / 50), 2)


class Eventlog(pygame.sprite.Sprite):
    max_row_show = 9  # maximum 9 text rows can appear at once
    logscroll = None  # Link from gamebattle after creation of both object

    def __init__(self, image, pos):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", 16)
        self.pos = pos
        self.image = image
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect(bottomleft=self.pos)

    def makenew(self):
        self.mode = 0  # 0=war,1=army(subunit),2=leader,3=subunit(sub-subunit)
        self.battle_log = []  # 0 war
        self.unit_log = []  # 1 army
        self.leader_log = []  # 2 leader
        self.subunit_log = []  # 3 subunit
        self.current_start_row = 0
        self.lencheck = 0  # total number of row in the current mode

    def addeventlog(self, mapevent):
        self.mapevent = mapevent
        if self.mapevent != {}:  # Edit map based event
            self.mapevent.pop("id")
            for event in self.mapevent:
                if type(self.mapevent[event][2]) == int:
                    self.mapevent[event][2] = [self.mapevent[event][2]]
                elif "," in self.mapevent[event][2]:  # Change mode list to list here since csvread don't have that function
                    self.mapevent[event][2] = [int(item) if item.isdigit() else item for item in self.mapevent[event][2].split(",")]
                if self.mapevent[event][3] != "":  # change time string to time delta same reason as above
                    newtime = datetime.datetime.strptime(self.mapevent[event][3], "%H:%M:%S").time()
                    newtime = datetime.timedelta(hours=newtime.hour, minutes=newtime.minute, seconds=newtime.second)
                    self.mapevent[event][3] = newtime
                else:
                    self.mapevent[event][3] = None

    def changemode(self, mode):
        """Change tab"""
        self.mode = mode
        self.lencheck = len((self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[self.mode])
        self.current_start_row = 0
        if self.lencheck > self.max_row_show:  # go to last row if there are more log than limit
            self.current_start_row = self.lencheck - self.max_row_show
        self.logscroll.current_row = self.current_start_row
        self.logscroll.changeimage(logsize=self.lencheck)
        self.recreateimage()

    def cleartab(self, alltab=False):
        """Clear event from log for that mode"""
        self.lencheck = 0
        self.current_start_row = 0
        currentlog = (self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[self.mode]  # log to edit
        currentlog.clear()
        if alltab:  # Clear event from every mode
            for log in (self.battle_log, self.unit_log, self.leader_log, self.subunit_log):
                log.clear()
        self.logscroll.current_row = self.current_start_row
        self.logscroll.changeimage(logsize=self.lencheck)
        self.recreateimage()

    def recreateimage(self):
        thislog = (self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[self.mode]  # log to edit
        self.image = self.image_original.copy()
        row = 10
        for index, text in enumerate(thislog[self.current_start_row:]):
            if index == self.max_row_show:
                break
            textsurface = self.font.render(text[1], True, (0, 0, 0))
            textrect = textsurface.get_rect(topleft=(40, row))
            self.image.blit(textsurface, textrect)
            row += 20  # Whitespace between text row

    def logtextprocess(self, who, modelist, textoutput):
        """Cut up whole log into seperate sentece based on space"""
        imagechange = False
        for mode in modelist:
            thislog = (self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[mode]  # log to edit
            if len(textoutput) <= 45:  # Eventlog each row cannot have more than 45 characters including space
                thislog.append([who, textoutput])
            else:  # Cut the text log into multiple row if more than 45 char
                cutspace = [index for index, letter in enumerate(textoutput) if letter == " "]
                howmanyloop = len(textoutput) / 45  # number of row
                if howmanyloop.is_integer() is False:  # always round up if there is decimal number
                    howmanyloop = int(howmanyloop) + 1
                startingindex = 0

                for run in range(1, int(howmanyloop) + 1):
                    textcutnumber = [number for number in cutspace if number <= run * 45]
                    cutnumber = textcutnumber[-1]
                    finaltextoutput = textoutput[startingindex:cutnumber]
                    if run == howmanyloop:
                        finaltextoutput = textoutput[startingindex:]
                    if run == 1:
                        thislog.append([who, finaltextoutput])
                    else:
                        thislog.append([-1, finaltextoutput])
                    startingindex = cutnumber + 1

            if len(thislog) > 1000:  # log cannot be more than 1000 length
                logtodel = len(thislog) - 1000
                del thislog[0:logtodel]  # remove the first few so only 1000 left
            if mode == self.mode:
                imagechange = True
        return imagechange

    def addlog(self, log, modelist, eventmapid=None):
        """Add log to appropiate event log, the log must be in list format following this rule [attacker (gameid), logtext]"""
        atlastrow = False
        imagechange = False
        imagechange2 = False
        if self.current_start_row + self.max_row_show >= self.lencheck:
            atlastrow = True
        if log is not None:  # when event map log commentary come in, log will be none
            textoutput = ": " + log[1]
            imagechange = self.logtextprocess(log[0], modelist, textoutput)
        if eventmapid is not None and eventmapid in self.mapevent:  # Process whether there is historical commentary to add to event log
            textoutput = self.mapevent[eventmapid]
            imagechange2 = self.logtextprocess(textoutput[0], textoutput[2], str(textoutput[3]) + ": " + textoutput[1])
        if imagechange or imagechange2:
            self.lencheck = len((self.battle_log, self.unit_log, self.leader_log, self.subunit_log)[self.mode])
            if atlastrow and self.lencheck > 9:
                self.current_start_row = self.lencheck - self.max_row_show
                self.logscroll.current_row = self.current_start_row
            self.logscroll.changeimage(logsize=self.lencheck)
            self.recreateimage()


class Uiscroller(pygame.sprite.Sprite):
    def __init__(self, pos, uiheight, max_row_show, layer=11):
        self._layer = layer
        pygame.sprite.Sprite.__init__(self)
        self.uiheight = uiheight
        self.pos = pos
        self.image = pygame.Surface((10, self.uiheight))
        self.image.fill((255, 255, 255))
        self.image_original = self.image.copy()
        self.button_colour = (100, 100, 100)
        pygame.draw.rect(self.image, self.button_colour, (0, 0, self.image.get_width(), self.uiheight))
        self.rect = self.image.get_rect(topright=self.pos)
        self.currentrow = 0
        self.max_row_show = max_row_show
        self.logsize = 0

    def newimagecreate(self):
        percentrow = 0
        maxrow = 100
        self.image = self.image_original.copy()
        if self.logsize > 0:
            percentrow = self.currentrow * 100 / self.logsize
        # if self.current_row + self.max_row_show < self.logsize:
        if self.logsize > 0:
            maxrow = (self.currentrow + self.max_row_show) * 100 / self.logsize
        maxrow = maxrow - percentrow
        pygame.draw.rect(self.image, self.button_colour,
                         (0, int(self.uiheight * percentrow / 100), self.image.get_width(), int(self.uiheight * maxrow / 100)))

    def changeimage(self, newrow=None, logsize=None):
        """New row is input of scrolling by user to new row, logsize is changing based on adding more log or clear"""
        if logsize is not None and self.logsize != logsize:
            self.logsize = logsize
            self.newimagecreate()
        if newrow is not None and self.currentrow != newrow:  # accept from both wheeling scroll and drag scroll bar
            self.currentrow = newrow
            self.newimagecreate()

    def update(self, mouse_pos):
        """User input update"""
        self.mouse_value = (mouse_pos[1] - self.pos[
            1]) * 100 / self.uiheight  # find what percentage of mouse_pos at the scroll bar (0 = top, 100 = bottom)
        if self.mouse_value > 100:
            self.mouse_value = 100
        if self.mouse_value < 0:
            self.mouse_value = 0
        newrow = int(self.logsize * self.mouse_value / 100)
        if self.logsize > self.max_row_show and newrow > self.logsize - self.max_row_show:
            newrow = self.logsize - self.max_row_show
        self.changeimage(newrow)
        return self.currentrow


class Armyselect(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = image
        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)
        self.current_row = 0
        self.max_row_show = 2
        self.max_column_show = 6
        self.logsize = 0


class Armyicon(pygame.sprite.Sprite):
    def __init__(self, pos, army):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.army = army  # link army object so when click can correctly select or go to position
        army.icon = self  # link this icon to army object, mostly for when it get killed so can easily remove from list
        self.pos = pos  # position on army selector ui
        self.leaderimage = self.army.leader[0].image.copy()  # get main leader image
        self.leaderimage = pygame.transform.scale(self.leaderimage, (int(self.leaderimage.get_width() / 1.5),
                                                                     int(self.leaderimage.get_height() / 1.5)))  # scale leader image to fit the icon
        self.image = pygame.Surface((self.leaderimage.get_width() + 4, self.leaderimage.get_height() + 4))  # create image black corner block
        self.image.fill((0, 0, 0))  # fill black corner
        centerimage = pygame.Surface((self.leaderimage.get_width() + 2, self.leaderimage.get_height() + 2))  # create image block
        centerimage.fill((144, 167, 255))  # fill colour according to team, blue for team 1
        if self.army.team == 2:
            centerimage.fill((255, 114, 114))  # red colour for team 2
        imagerect = centerimage.get_rect(topleft=(1, 1))
        self.image.blit(centerimage, imagerect)  # blit colour block into border image
        self.leaderrect = self.leaderimage.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(self.leaderimage, self.leaderrect)  # blit leader image
        self.rect = self.image.get_rect(center=self.pos)

    def changepos(self, pos):
        """change position of icon to new one"""
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)

    def changeimage(self, newimage=None, changeside=False):
        """For changing side"""
        if changeside:
            self.image.fill((144, 167, 255))
            if self.army.team == 2:
                self.image.fill((255, 114, 114))
            self.image.blit(self.leaderimage, self.leaderrect)
        if newimage is not None:
            self.leaderimage = newimage
            self.image.blit(self.leaderimage, self.leaderrect)

    def delete(self, local=False):
        """delete reference when del is called"""
        if local:
            print(locals())
        else:
            del self.army


class Timer(pygame.sprite.Sprite):
    def __init__(self, pos, textsize=20):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.pos = pos
        self.image = pygame.Surface((100, 30), pygame.SRCALPHA)
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)

    def startsetup(self, timestart):
        self.timer = timestart.total_seconds()
        self.oldtimer = self.timer
        self.timenum = timestart  # datetime.timedelta(seconds=self.timer)
        self.timersurface = self.font.render(str(self.timer), True, (0, 0, 0))
        self.timerrect = self.timersurface.get_rect(topleft=(5, 5))
        self.image.blit(self.timersurface, self.timerrect)

    def timerupdate(self, dt):
        """Update in-game timer number"""
        if dt > 0:
            self.timer += dt
            if self.timer - self.oldtimer > 1:
                self.oldtimer = self.timer
                if self.timer >= 86400:  # Time pass midnight
                    self.timer -= 86400  # Restart clock to 0
                    self.oldtimer = self.timer
                self.image = self.image_original.copy()
                self.timenum = datetime.timedelta(seconds=self.timer)
                timenum = str(self.timenum).split(".")[0]
                self.timersurface = self.font.render(timenum, True, (0, 0, 0))
                self.image.blit(self.timersurface, self.timerrect)


class Timeui(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.image = image.copy()
        self.image_original = self.image.copy()
        self.rect = self.image.get_rect(topleft=pos)


class Scaleui(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.percentscale = -100
        self.team1colour = (144, 167, 255)
        self.team2colour = (255, 114, 114)
        self.font = pygame.font.SysFont("helvetica", 12)
        self.pos = pos
        self.image = image
        self.imagewidth = self.image.get_width()
        self.imageheight = self.image.get_height()
        self.rect = self.image.get_rect(topleft=pos)

    def changefightscale(self, troopnumberlist):
        newpercent = round(troopnumberlist[1] / (troopnumberlist[1] + troopnumberlist[2]), 4)
        if self.percentscale != newpercent:
            self.percentscale = newpercent
            self.image.fill(self.team1colour, (0, 0, self.imagewidth, self.imageheight))
            self.image.fill(self.team2colour, (self.imagewidth * self.percentscale, 0, self.imagewidth, self.imageheight))

            team1text = self.font.render("{:,}".format(troopnumberlist[1] - 1), True, (0, 0, 0))  # add troop number text
            team1textrect = team1text.get_rect(topleft=(0, 0))
            self.image.blit(team1text, team1textrect)
            team2text = self.font.render("{:,}".format(troopnumberlist[2] - 1), True, (0, 0, 0))
            team2textrect = team2text.get_rect(topright=(self.imagewidth, 0))
            self.image.blit(team2text, team2textrect)


class Speednumber(pygame.sprite.Sprite):
    def __init__(self, pos, speed, textsize=20):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.pos = pos
        self.image = pygame.Surface((50, 30), pygame.SRCALPHA)
        self.image_original = self.image.copy()
        self.speed = speed
        self.timersurface = self.font.render(str(self.speed), True, (0, 0, 0))
        self.timerrect = self.timersurface.get_rect(topleft=(3, 3))
        self.image.blit(self.timersurface, self.timerrect)
        self.rect = self.image.get_rect(center=pos)

    def speedupdate(self, newspeed):
        """change speed number text"""
        self.image = self.image_original.copy()
        self.speed = newspeed
        self.timersurface = self.font.render(str(self.speed), True, (0, 0, 0))
        self.image.blit(self.timersurface, self.timerrect)


class Inspectsubunit(pygame.sprite.Sprite):
    def __init__(self, pos):
        self._layer = 11
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.who = None
        self.image = pygame.Surface((1, 1))
        self.rect = self.image.get_rect(topleft=self.pos)

    def addsubunit(self, who):
        self.who = who
        self.image = self.who.imageblock
        self.rect = self.image.get_rect(topleft=self.pos)

    def delete(self):
        self.who = None
