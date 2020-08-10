import pygame
import pygame.freetype


class uibutton(pygame.sprite.Sprite):
    def __init__(self, X, Y, image, event):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.X, self.Y = X, Y
        self.image = image
        self.event = event
        self._layer = 5
        self.rect = self.image.get_rect(center=(self.X, self.Y))
        self.mouse_over = False

    def draw(self, gamescreen):
        gamescreen.blit(self.image, self.rect)


class iconpopup(pygame.sprite.Sprite):
    def __init__(self, X, Y, image, event, gameui, itemid=""):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.X, self.Y = X, Y
        self.image = image
        self.event = 0
        self._layer = 5
        self.rect = self.image.get_rect(center=(self.X, self.Y))
        self.mouse_over = False
        self.itemid = itemid

    def draw(self, gamescreen):
        gamescreen.blit(self.image, self.rect)


class Gameui(pygame.sprite.Sprite):
    def __init__(self, X, Y, screen, image, icon, uitype, text="", textsize=16):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", textsize)
        self.X, self.Y = X, Y
        self.text = text
        self.image = image
        self.icon = icon
        self._layer = 5
        self.uitype = uitype
        self.value = [-1, -1]
        self.lastvalue = 0
        self.lastvalue2 = 0
        self.option = 0
        self.rect = self.image.get_rect(center=(self.X, self.Y))
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
        elif self.uitype == "commandbar":
            self.iconimagerect = self.icon[6].get_rect(
                center=(self.image.get_rect()[0] + self.image.get_size()[0] / 1.1, self.image.get_rect()[1] + 40))
            self.image.blit(self.icon[6], self.iconimagerect)
            self.white = [self.icon[0], self.icon[1], self.icon[2], self.icon[3], self.icon[4], self.icon[5]]
            self.black = [self.icon[7], self.icon[8], self.icon[9], self.icon[10], self.icon[11], self.icon[12]]
        elif self.uitype == "unitcard":
            self.fonthead = pygame.font.SysFont("helvetica", textsize + 2)
            self.fonthead.set_italic(1)
            self.fontlong = pygame.font.SysFont("helvetica", textsize - 2)
        #     self.iconimagerect = self.icon[0].get_rect(
        #         center=(
        #             self.image.get_rect()[0] + self.image.get_size()[0] - 20, self.image.get_rect()[1] + 40))
        self.image_original = self.image.copy()

    def blit_text(self, surface, text, pos, font, color=pygame.Color('black')):
        words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
        space = font.size(' ')[0]  # The width of a space.
        max_width, max_height = surface.get_size()
        x, y = pos
        for line in words:
            for word in line:
                word_surface = font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.

    def valueinput(self, who, leader="", button="", changeoption=0, gameunitstat=""):
        for thisbutton in button:
            thisbutton.draw(self.image)
        position = 65
        if self.uitype == "topbar":
            self.value = who.valuefortopbar
            if self.value[3] in self.options1:
                self.value[3] = self.options1[self.value[3]]
            if type(self.value[2]) != str: self.value[2] = round(self.value[2] / 10)
            if self.value[2] in self.options2:
                self.value[2] = self.options2[self.value[2]]
            if self.value != self.lastvalue:
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
            usecolour = self.white
            self.leaderpiclist = []
            self.image = self.image_original.copy()
            if who.gameid >= 2000:
                usecolour = self.black
            if who.commander == True:
                self.iconimagerect = usecolour[0].get_rect(
                    center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2, self.image.get_rect()[1] + 45))
                self.image.blit(usecolour[0], self.iconimagerect)
                self.iconimagerect = usecolour[1].get_rect(
                    center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2, self.image.get_rect()[1] + 150))
                self.image.blit(usecolour[1], self.iconimagerect)
            else:
                self.iconimagerect = usecolour[2].get_rect(
                    center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2, self.image.get_rect()[1] + 45))
                self.image.blit(usecolour[2], self.iconimagerect)
                self.iconimagerect = usecolour[5].get_rect(
                    center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2, self.image.get_rect()[1] + 150))
                self.image.blit(usecolour[5], self.iconimagerect)
            self.iconimagerect = usecolour[3].get_rect(center=(
                self.image.get_rect()[0] + self.image.get_size()[0] / 3.1,
                self.image.get_rect()[1] + self.image.get_size()[1] / 2.2))
            self.image.blit(usecolour[3], self.iconimagerect)
            self.iconimagerect = usecolour[0].get_rect(center=(
                self.image.get_rect()[0] + self.image.get_size()[0] / 1.4,
                self.image.get_rect()[1] + self.image.get_size()[1] / 2.2))
            self.image.blit(usecolour[4], self.iconimagerect)
            for thisleader in who.leaderwho:
                self.leaderpiclist.append(thisleader[1])
            """put leader image into leader slot"""
            self.leaderpiclistrect = leader.imgs[self.leaderpiclist[0]].get_rect(
                center=(self.image.get_rect()[0] + self.image.get_size()[0] / 2, self.image.get_rect()[1] + 65))
            self.image.blit(leader.imgs[self.leaderpiclist[0]], self.leaderpiclistrect)
            self.leaderpiclistrect = leader.imgs[self.leaderpiclist[1]].get_rect(center=(
                self.image.get_rect()[0] + self.image.get_size()[0] / 3.1,
                self.image.get_rect()[1] + self.image.get_size()[1] / 2.2 + 22))
            self.image.blit(leader.imgs[self.leaderpiclist[1]], self.leaderpiclistrect)
            self.leaderpiclistrect = leader.imgs[self.leaderpiclist[2]].get_rect(center=(
                self.image.get_rect()[0] + self.image.get_size()[0] / 1.4,
                self.image.get_rect()[1] + self.image.get_size()[1] / 2.2 + 22))
            self.image.blit(leader.imgs[self.leaderpiclist[2]], self.leaderpiclistrect)
            self.leaderpiclistrect = leader.imgs[self.leaderpiclist[3]].get_rect(
                center=(self.image.get_size()[0] / 2, self.image.get_rect()[1] + 172))
            self.image.blit(leader.imgs[self.leaderpiclist[3]], self.leaderpiclistrect)
            self.textsurface = self.font.render(str(who.authority), 1, (0, 0, 0))
            self.textrect = self.textsurface.get_rect(
                midleft=(self.image.get_rect()[0] + self.image.get_size()[0] / 1.3 + 20, self.image.get_rect()[1] + 40))
            self.image.blit(self.textsurface, self.textrect)

        elif self.uitype == "unitcard":
            position = 15
            positionx = 45
            self.value = who.unitcardvalue
            self.value2 = who.unitcardvalue2
            self.description = self.value[-1]
            if type(self.description) == list: self.description = self.description[0]
            # options = {2: "Skirmish is a light infantry that served as harassment or flanking unit. They can move fast and often carry range weapon. They can be good in melee combat but their lack of heavy armour mean that they cannot withstand more overwhelming force.",
            #            5: "Support is unit that can be essential in drawn out war. They can offer spiritual help to the other squad in the battalion, perform first aids or post battle surgery. In other words, support unit help other unit fight and survive better in this hell that people often refer as field of glory.",
            # 10:"This is command unit for this battalion. Do not let them get destroyed or your battalion will receive huge penalty to morale and all other undesirable status penalty. However putting this unit on frontline will also provide large bonus to the entire battalion, so use consider this option carefully."}
            text = ["", "Troop: ", "Stamina: ", "Morale: ", "Discipline: ", 'Melee Attack: ',
                    'Melee Defence: ', 'Range Defence: ', 'Armour: ', 'Speed: ', "Accuracy: ",
                    "Range: ", "Ammunition: ", "Reload Speed: ", "Charge Power: ", "Charge Defence:"]
            if self.value != self.lastvalue or self.value2 != self.lastvalue2 or changeoption == 1:
                self.image = self.image_original.copy()
                """Stat card"""
                if self.option == 1:
                    row = 0
                    # self.iconimagerect = self.icon[0].get_rect(
                    #     center=(
                    #     self.image.get_rect()[0] + self.image.get_size()[0] -20, self.image.get_rect()[1] + 40))
                    # deletelist = [i for i,x in enumerate(self.value) if x == 0]
                    # if len(deletelist) != 0:
                    #     for i in sorted(deletelist, reverse = True):
                    #         self.value.pop(i)
                    #         text.pop(i)
                    self.value, text = self.value[0:-1], text[1:]
                    self.textsurface = self.fonthead.render(self.value[0], 1, (0, 0, 0))
                    self.textrect = self.textsurface.get_rect(
                        midleft=(self.image.get_rect()[0] + positionx, self.image.get_rect()[1] + position))
                    self.image.blit(self.textsurface, self.textrect)
                    position += 20
                    row += 1
                    for n, value in enumerate(self.value[1:]):
                        self.textsurface = self.font.render(text[n] + str(value), 1, (0, 0, 0))
                        self.textrect = self.textsurface.get_rect(
                            midleft=(self.image.get_rect()[0] + positionx, self.image.get_rect()[1] + position))
                        self.image.blit(self.textsurface, self.textrect)
                        position += 20
                        row += 1
                        if row == 9: positionx, position = 200, 35
                elif self.option == 0:
                    """Description card"""
                    # self.iconimagerect = self.icon[0].get_rect(
                    #     center=(
                    #     self.image.get_rect()[0] + self.image.get_size()[0] -20, self.image.get_rect()[1] + 40))
                    # self.image.blit(self.icon[0], self.iconimagerect)
                    self.textsurface = self.fonthead.render(self.value[0], 1, (0, 0, 0))
                    self.textrect = self.textsurface.get_rect(
                        midleft=(self.image.get_rect()[0] + 42, self.image.get_rect()[1] + position))
                    self.image.blit(self.textsurface, self.textrect)
                    self.blit_text(self.image, self.description, (42, 25), self.fontlong)
                elif self.option == 2:
                    """unit name at the top"""
                    self.textsurface = self.fonthead.render(self.value[0], 1, (0, 0, 0))
                    self.textrect = self.textsurface.get_rect(
                        midleft=(self.image.get_rect()[0] + 42, self.image.get_rect()[1] + position))
                    self.image.blit(self.textsurface, self.textrect)
                    position += 20
                    position2 = positionx + 20
                    """property list"""
                    for trait in self.value2[0]:
                        # if trait in self.value2[2] : cd = int(self.value2[2][trait])
                        # self.textsurface = self.font.render("--Unit Properties--", 1, (0, 0, 0))
                        if trait != 0:
                            self.textsurface = self.font.render(str(self.value2[0][trait][0]), 1, (0, 0, 0))
                            self.textrect = self.textsurface.get_rect(
                                midleft=(self.image.get_rect()[0] + position2, self.image.get_rect()[1] + position))
                            self.image.blit(self.textsurface, self.textrect)
                            position += 20
                    """skill cooldown"""
                    for skill in self.value2[1]:
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
                    """skill effect list"""
                    position2 = positionx + 20
                    for status in self.value2[3]:
                        self.textsurface = self.font.render(str(self.value2[3][status][0]) + ": " + str(int(self.value2[3][status][3])), 1, (0, 0, 0))
                        self.textrect = self.textsurface.get_rect(
                            midleft=(self.image.get_rect()[0] + position2, self.image.get_rect()[1] + position))
                        self.image.blit(self.textsurface, self.textrect)
                        # position2 += 25
                        # if position2 >= 90:
                        #     position2 = positionx + 20
                        position += 20
                    # position += 20
                    """status list"""
                    position2 = positionx + 20
                    for status in self.value2[4]:
                        self.textsurface = self.font.render(str(self.value2[4][status][0]) + ": " + str(int(self.value2[4][status][3])), 1, (0, 0, 0))
                        self.textrect = self.textsurface.get_rect(
                            midleft=(self.image.get_rect()[0] + position2, self.image.get_rect()[1] + position))
                        self.image.blit(self.textsurface, self.textrect)
                        # position2 += 25
                        # if position2 >= 90:
                        #     position2 = positionx + 20
                        position += 20
                self.lastvalue = self.value
                self.lastvalue2 != self.value2


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
