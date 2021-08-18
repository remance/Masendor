import ast
import csv

import pygame
import pygame.freetype
from gamescript import gamemap

terraincolour = gamemap.terraincolour
featurecolour = gamemap.featurecolour


class Inputui(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = 30
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(image, (int(image.get_width() * self.widthadjust),
                                                    int(image.get_height() * self.heightadjust)))

        self.image_original = self.image.copy()

        self.font = pygame.font.SysFont("timesnewroman", int(30 * self.heightadjust))

        self.rect = self.image.get_rect(center=pos)

    def changeinstruction(self, text):
        self.image = self.image_original.copy()
        self.text = text
        self.textsurface = self.font.render(text, True, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 4))
        self.image.blit(self.textsurface, self.textrect)


class Inputbox(pygame.sprite.Sprite):
    def __init__(self, pos, width, text="", clickinput=False):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        pygame.sprite.Sprite.__init__(self)
        self._layer = 31
        self.font = pygame.font.SysFont("timesnewroman", int(20 * self.heightadjust))
        self.image = pygame.Surface((width - 10, int(26 * self.heightadjust)))  # already scale from input ui
        self.image.fill((255, 255, 255))

        self.image_original = self.image.copy()

        self.text = text
        self.textsurface = self.font.render(text, True, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))

        self.active = True
        self.clickinput = False
        if clickinput:
            self.active = False
            self.clickinput = clickinput

        self.rect = self.image.get_rect(center=pos)

    def textstart(self, text):
        """Add starting text to input box"""
        self.image = self.image_original.copy()
        self.text = text
        self.textsurface = self.font.render(text, True, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(self.textsurface, self.textrect)

    def userinput(self, event):
        """register user keyboard and mouse input"""
        if self.clickinput and event.type == pygame.MOUSEBUTTONDOWN:  # only for text box that require click will activate
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
        if event.type == pygame.KEYDOWN:  # text input
            if self.active:
                self.image = self.image_original.copy()
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.textsurface = self.font.render(self.text, True, (0, 0, 0))
                self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
                self.image.blit(self.textsurface, self.textrect)


class Profilebox(pygame.sprite.Sprite):
    def __init__(self, image, pos, name):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        pygame.sprite.Sprite.__init__(self)

        self.font = pygame.font.SysFont("helvetica", int(16 * self.heightadjust))
        self.image = pygame.transform.scale(image, (int(image.get_width() * self.widthadjust),
                                                    int(image.get_height() * self.heightadjust)))
        self.image_original = self.image.copy()

        self.textsurface = self.font.render(name, True, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.textsurface, self.textrect)

        self.rect = self.image.get_rect(topright=pos)

    def changename(self, name):
        self.image = self.image_original.copy()

        self.textsurface = self.font.render(name, True, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.textsurface, self.textrect)


class Menubutton(pygame.sprite.Sprite):
    def __init__(self, images, pos, text="", size=16, layer=15):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.images = [image.copy() for image in images]
        self.text = text
        self.font = pygame.font.SysFont("timesnewroman", int(size * self.heightadjust))
        self.image_original0 = self.images[0].copy()
        self.image_original1 = self.images[1].copy()
        self.image_original2 = self.images[2].copy()

        if text != "":  # draw text into the button images
            # self.imagescopy = self.images
            self.textsurface = self.font.render(self.text, True, (0, 0, 0))
            self.textrect = self.textsurface.get_rect(center=self.images[0].get_rect().center)
            self.images[0].blit(self.textsurface, self.textrect)
            self.images[1].blit(self.textsurface, self.textrect)
            self.images[2].blit(self.textsurface, self.textrect)

        self.image = self.images[0]
        self.rect = self.images[0].get_rect(center=self.pos)
        self.event = False

    def update(self, mouse_pos, mouse_up, mouse_down):
        self.mouse_over = False
        self.image = self.images[0]
        if self.rect.collidepoint(mouse_pos):
            self.mouse_over = True
            self.image = self.images[1]
            if mouse_up:
                self.event = True
                self.image = self.images[2]

    def changestate(self, text):
        if text != "":
            img0 = self.image_original0.copy()
            img1 = self.image_original1.copy()
            img2 = self.image_original2.copy()
            self.images = [img0, img1, img2]
            self.textsurface = self.font.render(text, True, (0, 0, 0))
            self.textrect = self.textsurface.get_rect(center=self.images[0].get_rect().center)
            self.images[0].blit(self.textsurface, self.textrect)
            self.images[1].blit(self.textsurface, self.textrect)
            self.images[2].blit(self.textsurface, self.textrect)
        self.rect = self.images[0].get_rect(center=self.pos)
        self.event = False


class Menuicon(pygame.sprite.Sprite):
    def __init__(self, images, pos, text="", imageresize=0):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.images = images
        self.image = self.images[0]
        if imageresize != 0:
            self.image = pygame.transform.scale(self.image, (imageresize, imageresize))
        self.text = text
        self.font = pygame.font.SysFont("timesnewroman", 16)
        if text != "":
            self.textsurface = self.font.render(self.text, True, (0, 0, 0))
            self.textrect = self.textsurface.get_rect(center=self.image.get_rect().center)
        self.rect = self.image.get_rect(center=self.pos)
        self.event = False


class Slidermenu(pygame.sprite.Sprite):
    def __init__(self, barimage, buttonimage, pos, value):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.image = barimage
        self.buttonimagelist = buttonimage
        self.buttonimage = self.buttonimagelist[0]
        self.slidersize = self.image.get_size()[0] - 20
        self.minvalue = self.pos[0] - (self.image.get_width() / 2) + 10.5  # min value position of the scroll bar
        self.maxvalue = self.pos[0] + (self.image.get_width() / 2) - 10.5  # max value position
        self.value = value
        self.mouse_value = (self.slidersize * value / 100) + 10.5  # mouse position on the scroll bar convert to value
        self.image_original = self.image.copy()
        self.buttonrect = self.buttonimagelist[1].get_rect(center=(self.mouse_value, self.image.get_height() / 2))
        self.image.blit(self.buttonimage, self.buttonrect)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, mouse_pos, valuebox, forcedvalue=False):
        """Update slider value and position"""
        if forcedvalue is False:
            self.mouse_value = mouse_pos[0]
            if self.mouse_value > self.maxvalue:
                self.mouse_value = self.maxvalue
            elif self.mouse_value < self.minvalue:
                self.mouse_value = self.minvalue
            self.value = (self.mouse_value - self.minvalue) / 2
            self.mouse_value = (self.slidersize * self.value / 100) + 10.5
        else:  # for revert, cancel or esc in the option menu
            self.value = mouse_pos
            self.mouse_value = (self.slidersize * self.value / 100) + 10.5
        self.image = self.image_original.copy()
        self.buttonrect = self.buttonimagelist[1].get_rect(center=(self.mouse_value, self.image.get_height() / 2))
        self.image.blit(self.buttonimage, self.buttonrect)
        valuebox.update(self.value)


class Valuebox(pygame.sprite.Sprite):
    def __init__(self, textimage, pos, value, textsize=16):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("timesnewroman", textsize)
        self.pos = pos
        self.image = pygame.transform.scale(textimage, (int(textimage.get_size()[0] / 2), int(textimage.get_size()[1] / 2)))
        self.image_original = self.image.copy()
        self.value = value
        self.textsurface = self.font.render(str(self.value), True, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center=self.image.get_rect().center)
        self.image.blit(self.textsurface, self.textrect)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, value):
        self.value = value
        self.image = self.image_original.copy()
        self.textsurface = self.font.render(str(self.value), True, (0, 0, 0))
        self.image.blit(self.textsurface, self.textrect)


class Maptitle(pygame.sprite.Sprite):
    def __init__(self, name, pos):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.font = pygame.font.SysFont("oldenglishtext", int(70 * self.heightadjust))
        self.textsurface = self.font.render(str(name), True, (0, 0, 0))

        self.image = pygame.Surface((int(self.textsurface.get_width() + (20 * self.widthadjust)),
                                     int(self.textsurface.get_height() + (20 * self.heightadjust))))
        self.image.fill((0, 0, 0))

        whitebody = pygame.Surface((self.textsurface.get_width(), self.textsurface.get_height()))
        whitebody.fill((239, 228, 176))
        whiterect = whitebody.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(whitebody, whiterect)

        self.textrect = self.textsurface.get_rect(center=(self.image.get_width() / 2, self.image.get_height() / 2))
        self.image.blit(self.textsurface, self.textrect)
        self.rect = self.image.get_rect(midtop=pos)


class Mapdescription(pygame.sprite.Sprite):
    image = None

    def __init__(self, pos, text):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.font = pygame.font.SysFont("timesnewroman", int(16 * self.heightadjust))
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * self.widthadjust),
                                                         int(self.image.get_height() * self.heightadjust)))

        self.image_original = self.image.copy()
        self.image = self.image_original.copy()  # reset self.image to new one from the loaded image

        self.longtext(self.image, text, (int(20 * self.widthadjust), int(20 * self.heightadjust)), self.font)

        self.rect = self.image.get_rect(center=pos)

    def longtext(self, surface, textlist, pos, font, color=pygame.Color("black")):
        """Blit long text into seperate row of text"""
        x, y = pos
        if textlist[0] != "":  # in case no map description in info.csv
            for text in textlist:
                words = [word.split(" ") for word in text.splitlines()]  # 2D array where each row is a list of words
                space = font.size(" ")[0]  # the width of a space
                maxwidth, maxheight = surface.get_size()
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
                x = pos[0]
                y += wordheight
        else:
            self.image = self.image_original.copy()


class Sourcedescription(pygame.sprite.Sprite):
    image = None

    def __init__(self, pos, text):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.font = pygame.font.SysFont("timesnewroman", int(16 * self.heightadjust))
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * self.widthadjust),
                                                         int(self.image.get_height() * self.heightadjust)))

        self.image_original = self.image.copy()
        self.image = self.image_original.copy()  # reset self.image to new one from the loaded image

        self.longtext(self.image, text, (int(15 * self.widthadjust), int(20 * self.heightadjust)), self.font)

        self.rect = self.image.get_rect(center=pos)

    def longtext(self, surface, textlist, pos, font, color=pygame.Color("black")):
        """Blit long text into seperate row of text"""
        x, y = pos
        if textlist[0] != "":  # in case no map description in info.csv
            for text in textlist:
                words = [word.split(" ") for word in text.splitlines()]  # 2D array where each row is a list of words
                space = font.size(" ")[0]  # the width of a space
                maxwidth, maxheight = surface.get_size()
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
                x = pos[0]
                y += wordheight
        else:
            self.image = self.image_original.copy()


class Teamcoa(pygame.sprite.Sprite):
    def __init__(self, pos, image, team, name):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.selectedimage = pygame.Surface((int(200 * self.widthadjust), int(200 * self.heightadjust)))
        self.notselectedimage = self.selectedimage.copy()
        self.notselectedimage.fill((0, 0, 0))  # black border when not selected
        self.selectedimage.fill((230, 200, 15))  # gold border when selected

        whitebody = pygame.Surface((int(196 * self.widthadjust), int(196 * self.heightadjust)))
        whitebody.fill((255, 255, 255))
        whiterect = whitebody.get_rect(topleft=(int(2 * self.widthadjust), int(2 * self.heightadjust)))
        self.notselectedimage.blit(whitebody, whiterect)
        self.selectedimage.blit(whitebody, whiterect)

        # v Coat of arm image to image
        coaimage = pygame.transform.scale(image, (int(100 * self.widthadjust), int(100 * self.heightadjust)))
        coarect = coaimage.get_rect(center=(int(100 * self.widthadjust), int(70 * self.heightadjust)))
        self.notselectedimage.blit(coaimage, coarect)
        self.selectedimage.blit(coaimage, coarect)
        # ^ End Coat of arm

        # v Faction name to image
        self.name = name
        self.font = pygame.font.SysFont("oldenglishtext", int(32 * self.heightadjust))
        self.textsurface = self.font.render(str(self.name), True, (0, 0, 0))
        self.textrect = self.textsurface.get_rect(center=(int(100 * self.widthadjust), int(150 * self.heightadjust)))
        self.notselectedimage.blit(self.textsurface, self.textrect)
        self.selectedimage.blit(self.textsurface, self.textrect)
        # ^ End faction name

        self.image = self.notselectedimage
        self.rect = self.image.get_rect(center=pos)
        self.team = team
        self.selected = False

    def changeselect(self, selected):
        self.selected = selected
        if self.selected:
            self.image = self.selectedimage
        else:
            self.image = self.notselectedimage


class Armystat(pygame.sprite.Sprite):
    image = None

    def __init__(self, pos):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = 1

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.leadfont = pygame.font.SysFont("helvetica", int(self.heightadjust * 30))
        self.font = pygame.font.SysFont("helvetica", int(self.heightadjust * 20))

        self.image_original = self.image.copy()
        self.image = self.image_original.copy()

        self.typenumberpos = ((self.image.get_width() / 5, self.image.get_height() / 3),  # infantry melee
                              (self.image.get_width() / 5, self.image.get_height() / 1.8),  # infantry range
                              (self.image.get_width() / 1.6, self.image.get_height() / 3),  # cav melee
                              (self.image.get_width() / 1.6, self.image.get_height() / 1.8),  # cav range
                              (self.image.get_width() / 5, self.image.get_height() / 1.4))  # total subunit

        self.rect = self.image.get_rect(center=pos)

    def addstat(self, troopnumber, leader):
        """troopnumber need to be in list format as follows:[total,melee infantry, range infantry, cavalry, range cavalry]"""
        self.image = self.image_original.copy()

        textsurface = self.font.render(str(leader), True, (0, 0, 0))
        textrect = textsurface.get_rect(midleft=(self.image.get_width() / 7, self.image.get_height() / 10))
        self.image.blit(textsurface, textrect)

        for index, text in enumerate(troopnumber):
            textsurface = self.font.render("{:,}".format(text), True, (0, 0, 0))
            textrect = textsurface.get_rect(midleft=self.typenumberpos[index])
            self.image.blit(textsurface, textrect)


class Listbox(pygame.sprite.Sprite):
    def __init__(self, pos, image, layer=14):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = pygame.transform.scale(image, (int(image.get_width() * self.widthadjust),
                                                    int(image.get_height() * self.heightadjust)))
        self.rect = self.image.get_rect(topleft=pos)

        self.listimageheight = int(25 * self.heightadjust)
        self.maxshowlist = int(self.image.get_height() / (self.listimageheight + (6 * self.heightadjust)))  # max number of map on list can be shown


class Namelist(pygame.sprite.Sprite):
    def __init__(self, box, pos, name, textsize=16, layer=15):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(self.heightadjust * textsize))
        self.name = str(name)

        self.image = pygame.Surface((box.image.get_width() - int(15 * self.widthadjust), int(25 * self.heightadjust)))  # black corner
        self.image.fill((0, 0, 0))

        # v White body square
        smallimage = pygame.Surface((box.image.get_width() - int(17 * self.widthadjust), int(23 * self.heightadjust)))
        smallimage.fill((255, 255, 255))
        smallrect = smallimage.get_rect(topleft=(int(1 * self.widthadjust), int(1 * self.heightadjust)))
        self.image.blit(smallimage, smallrect)
        # ^ End white body

        # v Map name text
        textsurface = self.font.render(self.name, True, (0, 0, 0))
        textrect = textsurface.get_rect(midleft=(int(3 * self.widthadjust), self.image.get_height() / 2))
        self.image.blit(textsurface, textrect)
        # ^ End map name

        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)


class Tickbox(pygame.sprite.Sprite):
    def __init__(self, pos, image, tickimage, option):
        """option is in str text for identifying what kind of tickbox it is"""
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = 14
        pygame.sprite.Sprite.__init__(self, self.containers)

        self.option = option

        self.notickimage = image
        self.tickimage = tickimage
        self.tick = False

        self.notickimage = pygame.transform.scale(image, (int(image.get_width() * self.widthadjust),
                                                          int(image.get_height() * self.heightadjust)))
        self.tickimage = pygame.transform.scale(tickimage, (int(tickimage.get_width() * self.widthadjust),
                                                            int(tickimage.get_height() * self.heightadjust)))

        self.image = self.notickimage

        self.rect = self.image.get_rect(topright=pos)

    def changetick(self, tick):
        self.tick = tick
        if self.tick:
            self.image = self.tickimage
        else:
            self.image = self.notickimage


class Mapoptionbox(pygame.sprite.Sprite):
    def __init__(self, pos, image, mode):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768
        self.font = pygame.font.SysFont("helvetica", int(16 * self.heightadjust))

        self._layer = 13
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(image, (int(image.get_width() * self.widthadjust),
                                                    int(image.get_height() * self.heightadjust)))

        # v enactment option text
        textsurface = self.font.render("Enactment Mode", True, (0, 0, 0))
        textrect = textsurface.get_rect(midleft=(self.image.get_width() / 3.5, self.image.get_height() / 4))
        self.image.blit(textsurface, textrect)
        # ^ end enactment

        if mode == 0:  # preset map option
            pass
        elif mode == 1:  # custom map option
            # v enactment option text
            textsurface = self.font.render("No Duplicated Leader", True, (0, 0, 0))
            textrect = textsurface.get_rect(midleft=(self.image.get_width() / 3.5, self.image.get_height() / 3))
            self.image.blit(textsurface, textrect)
            # ^ end enactment

            # v enactment option text
            textsurface = self.font.render("Restrict Faction Troop Only", True, (0, 0, 0))
            textrect = textsurface.get_rect(midleft=(self.image.get_width() / 3.5, self.image.get_height() / 2))
            self.image.blit(textsurface, textrect)
            # ^ end enactment

        self.rect = self.image.get_rect(topright=pos)


class Sourcelistbox(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = 13
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(image, (int(image.get_width() * self.widthadjust),
                                                    int(image.get_height() * self.heightadjust)))
        self.rect = self.image.get_rect(topleft=pos)
        self.maxshowlist = 5  # max number of map on list can be shown at once


class Sourcename(pygame.sprite.Sprite):
    def __init__(self, box, pos, name, textsize=16, layer=14):
        import main
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        self._layer = layer
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.font = pygame.font.SysFont("helvetica", int(textsize * self.heightadjust))
        self.image = pygame.Surface((box.image.get_width(), int(25 * self.heightadjust)))  # black corner
        self.image.fill((0, 0, 0))

        # v White body square
        smallimage = pygame.Surface((box.image.get_width() - int(2 * self.widthadjust), int(23 * self.heightadjust)))
        smallimage.fill((255, 255, 255))
        smallrect = smallimage.get_rect(topleft=(int(1 * self.widthadjust), int(1 * self.heightadjust)))
        self.image.blit(smallimage, smallrect)
        # ^ End white body

        # v Source name text
        textsurface = self.font.render(str(name), True, (0, 0, 0))
        textrect = textsurface.get_rect(midleft=(int(3 * self.widthadjust), self.image.get_height() / 2))
        self.image.blit(textsurface, textrect)
        # ^ End source text

        self.pos = pos
        self.rect = self.image.get_rect(topleft=self.pos)


class Mapshow(pygame.sprite.Sprite):
    def __init__(self, pos, basemap, featuremap):
        import main
        self.main_dir = main.main_dir
        SCREENRECT = main.SCREENRECT
        self.widthadjust = SCREENRECT.width / 1366
        self.heightadjust = SCREENRECT.height / 768

        pygame.sprite.Sprite.__init__(self, self.containers)

        self.pos = pos
        self.imagebefore = pygame.Surface((310, 310))
        self.imagebefore.fill((0, 0, 0))  # draw black colour for black corner
        # pygame.draw.rect(self.image, self.colour, (2, 2, self.widthbox - 3, self.heightbox - 3)) # draw block colour

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

        self.newcolourlist = {}
        with open(self.main_dir + "/data/map" + "/colourchange.csv", encoding="utf-8", mode="r") as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                for n, i in enumerate(row):
                    if i.isdigit():
                        row[n] = int(i)
                    elif "," in i:
                        row[n] = ast.literal_eval(i)
                self.newcolourlist[row[0]] = row[1:]

        self.changemap(basemap, featuremap)
        self.image = pygame.transform.scale(self.imagebefore, (int(self.imagebefore.get_width() * self.widthadjust),
                                                               int(self.imagebefore.get_height() * self.heightadjust)))
        self.rect = self.image.get_rect(center=self.pos)

    def changemap(self, basemap, featuremap):
        newbasemap = pygame.transform.scale(basemap, (300, 300))
        newfeaturemap = pygame.transform.scale(featuremap, (300, 300))

        mapimage = pygame.Surface((300, 300))
        for rowpos in range(0, 300):  # recolour the map
            for colpos in range(0, 300):
                terrain = newbasemap.get_at((rowpos, colpos))  # get colour at pos to obtain the terrain type
                terrainindex = terraincolour.index(terrain)

                feature = newfeaturemap.get_at((rowpos, colpos))  # get colour at pos to obtain the terrain type
                featureindex = None
                if feature in featurecolour:
                    featureindex = featurecolour.index(feature)
                    featureindex = featureindex + (terrainindex * 12)
                newcolour = self.newcolourlist[featureindex][1]
                rect = pygame.Rect(rowpos, colpos, 1, 1)
                mapimage.fill(newcolour, rect)

        imagerect = mapimage.get_rect(topleft=(5, 5))
        self.imagebefore.blit(mapimage, imagerect)
        self.image_original = self.imagebefore.copy()

    def changemode(self, mode, team1poslist=None, team2poslist=None):
        """map mode: 0 = map without army dot, 1 = with army dot"""
        self.imagebefore = self.image_original.copy()
        if mode == 1:
            for team1 in team1poslist.values():
                scaledpos = pygame.Vector2(team1) * 0.3
                rect = self.team1dot.get_rect(center=scaledpos)
                self.imagebefore.blit(self.team1dot, rect)
            for team2 in team2poslist.values():
                scaledpos = pygame.Vector2(team2) * 0.3
                rect = self.team2dot.get_rect(center=scaledpos)
                self.imagebefore.blit(self.team2dot, rect)

        self.image = pygame.transform.scale(self.imagebefore, (int(self.imagebefore.get_width() * self.widthadjust),
                                                               int(self.imagebefore.get_height() * self.heightadjust)))
        self.rect = self.image.get_rect(center=self.pos)
