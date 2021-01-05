try: # for printing error log when error exception happen
    import configparser
    import glob
    import os.path
    import sys
    import traceback

    # import basic pygame modules
    import pygame
    import pygame.freetype
    from pygame.locals import *

    from gamescript import maingame, gameleader, gamemap, gamelongscript, gamelorebook, gameweather, gamefaction, gameunitstat, gameui, gameprepare

    config = configparser.ConfigParser()
    try:
        config.read_file(open('configuration.ini')) # read config file
    except: # Create config file if not found with the default
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'screenwidth': '1600','screenheight': '900', 'fullscreen': '0',
                             'playername': 'Noname', 'soundvolume': '100.0', 'musicvolume': '0.0',
                             'voicevolume': '0.0', 'maxfps': '60'}
        with open('configuration.ini', 'w') as cf:
            config.write(cf)
        config.read_file(open('configuration.ini'))
    ScreenHeight = int(config['DEFAULT']['ScreenHeight'])
    ScreenWidth = int(config['DEFAULT']['ScreenWidth'])
    FULLSCREEN = int(config['DEFAULT']['Fullscreen'])
    Soundvolume = float(config['DEFAULT']['SoundVolume'])

    SCREENRECT = Rect(0, 0, ScreenWidth, ScreenHeight)
    main_dir = os.path.split(os.path.abspath(__file__))[0]

    load_image = gamelongscript.load_image
    load_images = gamelongscript.load_images
    csv_read = gamelongscript.csv_read
    load_sound = gamelongscript.load_sound
    editconfig = gamelongscript.editconfig

    def makebarlist(listtodo, menuimage):
        """Make a drop down bar list option button"""
        barlist = []
        img = load_image('bar_normal.jpg', 'ui')
        img2 = load_image('bar_mouse.jpg', 'ui')
        img3 = img2
        for index, bar in enumerate(listtodo):
            barimage = (img.copy(), img2.copy(), img3.copy())
            bar = Menubutton(images=barimage, pos=(menuimage.pos[0], menuimage.pos[1] + img.get_height() * (index + 1)), text=bar)
            barlist.append(bar)
        return barlist

    def load_base_button():
        img = load_image('idle_button.png', 'ui')
        img2 = load_image('mouse_button.png', 'ui')
        img3 = load_image('click_button.png', 'ui')
        return [img, img2, img3]

    def text_objects(text, font):
        textSurface = font.render(text, True, (200, 200, 200))
        return textSurface, textSurface.get_rect()

    def game_intro(screen, clock, introoption):
        intro = introoption
        if introoption == True:
            intro = True
        timer = 0
        # quote = ["Those who fail to learn from the mistakes of their predecessors are destined to repeat them. George Santayana", "It is more important to outhink your enemy, than to outfight him, Sun Tzu"]
        while intro:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    intro = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            largeText = pygame.font.Font('freesansbold.ttf', 115)
            TextSurf, TextRect = text_objects("Test Intro", largeText)
            TextRect.center = (700, 600)
            screen.blit(TextSurf, TextRect)
            pygame.display.update()
            clock.tick(60)
            timer += 1
            if timer == 1000: intro = False


    class Maplistbox(pygame.sprite.Sprite):
        def __init__(self, pos, image):
            self._layer = 13
            pygame.sprite.Sprite.__init__(self, self.containers)
            self.image = image
            self.rect = self.image.get_rect(topleft=pos)


    class Mapname(pygame.sprite.Sprite):
        def __init__(self, pos, name, textsize=16):
            self._layer = 14
            pygame.sprite.Sprite.__init__(self, self.containers)
            self.font = pygame.font.SysFont("helvetica", textsize)
            self.image = pygame.Surface((180, 25))  # black corner
            self.image.fill((0, 0, 0))

            # v White body square
            smallimage = pygame.Surface((178, 23))
            smallimage.fill((255, 255, 255))
            smallrect = smallimage.get_rect(topleft=(1, 1))
            self.image.blit(smallimage, smallrect)
            # ^ End white body

            # v Subsection name text
            textsurface = self.font.render(str(name), 1, (0, 0, 0))
            textrect = textsurface.get_rect(midleft=(3, self.image.get_height() / 2))
            self.image.blit(textsurface, textrect)
            # ^ End subsection name

            self.pos = pos
            self.rect = self.image.get_rect(topleft=self.pos)

    class Menubutton(pygame.sprite.Sprite):
        def __init__(self, images, pos, text="", size=16):
            pygame.sprite.Sprite.__init__(self, self.containers)
            self.pos = pos
            self.images = [image.copy() for image in images]
            self.text = text
            self.font = pygame.font.SysFont("timesnewroman", size)

            if text != "": # draw text into the button images
                # self.imagescopy = self.images
                self.textsurface = self.font.render(self.text, 1, (0, 0, 0))
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
                img = load_image('scroll_normal.jpg', 'ui')
                img2 = img
                img3 = load_image('scroll_click.jpg', 'ui')
                self.images = [img, img2, img3]
                self.textsurface = self.font.render(text, 1, (0, 0, 0))
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
                self.textsurface = self.font.render(self.text, 1, (0, 0, 0))
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
            if forcedvalue == False:
                self.mouse_value = mouse_pos[0]
                if self.mouse_value > self.maxvalue:
                    self.mouse_value = self.maxvalue
                elif self.mouse_value < self.minvalue:
                    self.mouse_value = self.minvalue
                self.value = (self.mouse_value - self.minvalue) / 2
                self.mouse_value = (self.slidersize * self.value / 100) + 10.5
            else:  ## For revert, cancel or esc in the option menu
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
            self.textsurface = self.font.render(str(self.value), 1, (0, 0, 0))
            self.textrect = self.textsurface.get_rect(center=self.image.get_rect().center)
            self.image.blit(self.textsurface, self.textrect)
            self.rect = self.image.get_rect(center=self.pos)

        def update(self, value):
            self.value = value
            self.image = self.image_original.copy()
            self.textsurface = self.font.render(str(self.value), 1, (0, 0, 0))
            self.image.blit(self.textsurface, self.textrect)

    class Mainmenu():
        def __init__(self):
            pygame.init() # Initialize pygame

            self.rulesetlist = maingame.csv_read("ruleset_list.csv", ['data', 'ruleset']) # get ruleset list
            self.ruleset = 1 # for now default historical ruleset only
            self.rulesetfolder = "/" + str(self.rulesetlist[self.ruleset][1])
            self.enactment = True
            self.mapsource = 0 # current selected map source
            self.teamselected = 1

            self.allui = pygame.sprite.LayeredUpdates()
            self.menubutton = pygame.sprite.Group() # group of menu buttons that are currently get shown and update
            self.menuicon = pygame.sprite.Group()
            self.menuslider = pygame.sprite.Group()
            self.valuebox = pygame.sprite.Group() # value box of slider bar
            self.lorebook = pygame.sprite.Group()  # encyclopedia object
            self.lorenamelist = pygame.sprite.Group()  # box sprite for showing subsection name list in encyclopedia
            self.lorescroll = pygame.sprite.Group()  # scroller for subsection name list in encyclopedia
            self.lorebuttonui = pygame.sprite.Group()
            self.subsectionname = pygame.sprite.Group()  # subsection name objects group in encyclopedia blit on lorenamelist
            self.maplistbox = pygame.sprite.Group()
            self.mapname = pygame.sprite.Group()
            self.mapshow = pygame.sprite.Group()
            self.teamcoa = pygame.sprite.Group()

            #v Add group to containers
            Menubutton.containers = self.menubutton
            Menuicon.containers = self.menuicon
            Slidermenu.containers = self.menuslider
            Valuebox.containers = self.valuebox
            Maplistbox.containers = self.maplistbox
            Mapname.containers = self.mapname, self.allui
            gamelorebook.Lorebook.containers = self.lorebook
            gamelorebook.Subsectionlist.containers = self.lorenamelist
            gamelorebook.Subsectionname.containers = self.subsectionname, self.allui
            gameui.Uibutton.containers = self.lorebuttonui
            gameui.Uiscroller.containers = self.lorescroll, self.allui
            gameprepare.Mapshow.containers = self.mapshow
            gameprepare.Teamcoa.containers = self.teamcoa
            #^ End containers

            #v Set the display mode
            self.winstyle = 0  # FULLSCREEN
            if FULLSCREEN == 1:
                self.winstyle = pygame.FULLSCREEN
            self.bestdepth = pygame.display.mode_ok(SCREENRECT.size, self.winstyle, 32)
            self.screen = pygame.display.set_mode(SCREENRECT.size, self.winstyle | pygame.RESIZABLE, self.bestdepth)
            #^ End set display

            self.clock = pygame.time.Clock()
            game_intro(self.screen, self.clock, False) # run game intro

            #v Background image
            bgdtile = load_image('background.jpg', 'ui').convert()
            bgdtile = pygame.transform.scale(bgdtile, SCREENRECT.size)
            self.background = pygame.Surface(SCREENRECT.size)
            self.background.blit(bgdtile,(0,0))
            #^ End background

            gamelongscript.creategamelorestat(self, maplistload=True) # obtain game stat data and create lore book object

            #v Create main menu button
            imagelist = load_base_button()
            self.presetmapbutton = Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 7)),
                                          text="PRESET MAP")
            self.custommapbutton = Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 5.5)),
                                          text="CUSTOM MAP")
            self.lorebutton = Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 4)), text="Encyclopedia")
            self.optionbutton = Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 2.5)), text="OPTION")
            self.quitbutton = Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height())), text="QUIT")
            self.mainmenubutton = (self.presetmapbutton,self.custommapbutton,self.quitbutton,self.optionbutton, self.lorebutton)
            #^ End main menu button

            #v Create battle map menu button
            bottomheight = SCREENRECT.height - imagelist[0].get_height()
            self.selectbutton = Menubutton(images=imagelist, pos=(SCREENRECT.width - imagelist[0].get_width(), bottomheight),
                                          text="SELECT")
            self.startbutton = Menubutton(images=imagelist, pos=(SCREENRECT.width - imagelist[0].get_width(), bottomheight),
                                          text="START")
            self.mapbackbutton = Menubutton(images=imagelist, pos=(SCREENRECT.width - (SCREENRECT.width - imagelist[0].get_width()), bottomheight),
                                         text="BACK")
            self.mapselectbutton = (self.selectbutton, self.mapbackbutton)
            self.battlesetupbutton = (self.startbutton, self.mapbackbutton)

            imgs = load_images(['ui', 'mapselect_ui'], loadorder=False)
            self.maplistbox = Maplistbox((SCREENRECT.width/25, SCREENRECT.height/20), imgs[0])

            self.currentmaprow = 0
            self.currentmapselect = 0
            self.maxmaplist = 20 # max number of map on list can be shown at once

            #^ End battle map menu button

            # Create option menu button and icon
            self.backbutton = Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height / 1.2), text="BACK")

            #v Resolution changing bar that fold out the list when clicked
            img = load_image('scroll_normal.jpg', 'ui')
            img2 = img
            img3 = load_image('scroll_click.jpg', 'ui')
            imagelist = [img, img2, img3]
            self.resolutionscroll = Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height / 2.3),
                                               text=str(ScreenWidth) + " x " + str(ScreenHeight), size=16)
            resolutionlist = ['1920 x 1080', '1600 x 900', '1366 x 768', '1280 x 720', '1024 x 768', ]
            self.resolutionbar = makebarlist(listtodo=resolutionlist, menuimage=self.resolutionscroll)
            img = load_image('resolution_icon.png', 'ui')
            self.resolutionicon = Menuicon(images=[img], pos=(self.resolutionscroll.pos[0] - (self.resolutionscroll.pos[0] / 4.5), self.resolutionscroll.pos[1]), imageresize=50)
            #^ End resolution

            #v Volume change scroller bar
            img = load_image('scroller.png', 'ui')
            img2 = load_image('scoll_button_normal.png', 'ui')
            img3 = load_image('scoll_button_click.png', 'ui')
            img4 = load_image('numbervalue_icon.jpg', 'ui')
            self.volumeslider = Slidermenu(barimage=img, buttonimage=[img2, img3], pos=(SCREENRECT.width / 2, SCREENRECT.height / 3),
                                           value=Soundvolume)
            self.valuebox = [Valuebox(img4, (self.volumeslider.rect.topright[0] * 1.1, self.volumeslider.rect.topright[1]), Soundvolume)]
            img = load_image('volume_icon.png', 'ui')
            self.volumeicon = Menuicon(images=[img], pos=(self.volumeslider.pos[0] - (self.volumeslider.pos[0] / 4.5), self.volumeslider.pos[1]), imageresize=50)
            #^ End volume change

            self.optioniconlist = (self.resolutionicon,self.volumeicon)
            self.optionmenubutton = (self.backbutton,self.resolutionscroll)
            self.optionmenuslider = (self.volumeslider)
            # End option menu button

            pygame.display.set_caption('Preparation for Chaos') # set the game name on program border/tab
            pygame.mouse.set_visible(1) # set mouse as visible

            #v Music player
            if pygame.mixer:
                self.mixervolume = float(Soundvolume / 100)
                pygame.mixer.music.set_volume(self.mixervolume)
                self.SONG_END = pygame.USEREVENT + 1
                self.musiclist = glob.glob(main_dir + '/data/sound/music/*.mp3')
                pygame.mixer.music.load(self.musiclist[0])
                pygame.mixer.music.play(-1)
            #^ End music

            self.allui.remove(*self.menubutton)  # remove all button from drawing
            self.menubutton.remove(*self.menubutton) # remove all button at the start and add later depending on menustate
            self.menubutton.add(*self.mainmenubutton) # add only main menu button back
            self.allui.add(*self.menubutton)
            self.menustate = "mainmenu"

        def setupmaplist(self, maplist):
            """generate list of subsection of the left side of encyclopedia"""
            row = 15
            column = 15
            pos = self.maplistbox.rect.topleft
            if self.currentmaprow > len(maplist) - self.maxmaplist:
                self.currentmaprow = len(maplist) - self.maxmaplist

            if len(self.mapname) > 0:  # remove previous subsection in the group before generate new one
                for stuff in self.mapname:
                    stuff.kill()
                    del stuff

            for index, item in enumerate(maplist):
                if index >= self.currentmaprow:
                    self.mapname.add(Mapname((pos[0] + column, pos[1] + row), item))  # add new subsection sprite to group
                    row += 30  # next row
                    if len(self.mapname) > self.maxmaplist: break  # will not generate more than space allowed

        def maketeamcoa(self, maplist):
            for team in self.teamcoa:
                team.kill()
                del team

            if self.menustate == "presetselect":
                data = csv_read('info.csv',['data', 'ruleset', self.rulesetfolder.strip("/"), 'map', maplist[self.currentmapselect].split("\\")[-1]])
            else:
                data = csv_read('info.csv', ['data', 'ruleset', self.rulesetfolder.strip("/"), 'map/custom',  maplist[self.currentmapselect].split("\\")[-1]])

            # position = self.mapshow[0].get_rect()
            team1index = list(data.values())[1][2]
            team2index = list(data.values())[1][3]
            self.teamcoa.add(gameprepare.Teamcoa((SCREENRECT.width/2 - 300,SCREENRECT.height/3), self.coa[team1index],
                                                 1, self.allfaction.factionlist[team1index][0])) # team 1

            self.teamcoa.add(gameprepare.Teamcoa((SCREENRECT.width/2 + 300,SCREENRECT.height/3), self.coa[team2index],
                                                 2, self.allfaction.factionlist[team2index][0])) # team 2
            self.allui.add(self.teamcoa)

        def makemap(self, maplist):
            # self.allui.remove(self.mapshow)
            for thismap in self.mapshow:
                thismap.kill()
                del thismap
            if self.menustate == "presetselect":
                imgs = load_images(['ruleset', self.rulesetfolder.strip("/"), 'map', maplist[self.currentmapselect]], loadorder=False)
            else:
                imgs = load_images(['ruleset', self.rulesetfolder.strip("/"), 'map/custom', maplist[self.currentmapselect]], loadorder=False)
            self.mapshow.add(gameprepare.Mapshow((SCREENRECT.width/2, SCREENRECT.height/3), imgs[0], imgs[1]))
            self.allui.add(self.mapshow)

        def run(self, maingamefunc):
            while True:
                #v Get user input
                mouse_up = False
                mouse_down = False
                for event in pygame.event.get():
                    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE) or self.quitbutton.event == True:
                        if self.menustate == "encyclopedia" and (event.type == KEYDOWN and event.key == K_ESCAPE):
                            self.allui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll, self.lorenamelist)
                            for name in self.subsectionname:
                                name.kill()
                                del name
                            self.menustate = "mainmenu"
                        else:
                            return

                    if pygame.mouse.get_pressed()[0]:  # Hold left click
                        mouse_down = True

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:  # left click
                            mouse_up = True
                        elif event.button == 4 and self.menustate == "encyclopedia":  # Mouse scroll down, Scrolling at lore book subsection list
                            if self.lorenamelist.rect.collidepoint(self.mousepos):
                                self.lorebook.currentsubsectionrow -= 1
                                if self.lorebook.currentsubsectionrow < 0:
                                    self.lorebook.currentsubsectionrow = 0
                                else:
                                    self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname)
                                    self.lorescroll.changeimage(newrow=self.lorebook.currentsubsectionrow)

                        elif event.button == 5 and self.menustate == "encyclopedia":  # Mouse scroll up, Scrolling at lore book subsection list
                            if self.lorenamelist.rect.collidepoint(self.mousepos):
                                self.lorebook.currentsubsectionrow += 1
                                if self.lorebook.currentsubsectionrow + self.lorebook.maxsubsectionshow - 1 < self.lorebook.logsize:
                                    self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname)
                                    self.lorescroll.changeimage(newrow=self.lorebook.currentsubsectionrow)
                                else:
                                    self.lorebook.currentsubsectionrow -= 1

                keystate = pygame.key.get_pressed()
                self.mousepos = pygame.mouse.get_pos()
                #^ End user input

                self.screen.blit(self.background, (0, 0))  # blit blackground over instead of clear() to reset screen
                self.menubutton.update(self.mousepos, mouse_up, mouse_down)

                if self.menustate == "mainmenu":

                    if self.presetmapbutton.event: # preset map list menu
                        self.menustate = "presetselect"
                        self.lastselect = self.menustate
                        self.presetmapbutton.event = False
                        self.allui.remove(*self.menubutton)
                        self.menubutton.remove(*self.menubutton)

                        self.setupmaplist(self.maplist)
                        self.makemap(self.mapfoldername)
                        self.maketeamcoa(self.mapfoldername)

                        self.menubutton.add(*self.mapselectbutton)
                        self.allui.add(*self.mapselectbutton, self.maplistbox)

                    elif self.custommapbutton.event: # custom map list menu
                        self.menustate = "customselect"
                        self.lastselect = self.menustate
                        self.custommapbutton.event = False
                        self.allui.remove(*self.menubutton)
                        self.menubutton.remove(*self.menubutton)

                        self.setupmaplist(self.mapcustomlist)
                        self.makemap(self.mapcustomfoldername)
                        self.maketeamcoa(self.mapcustomfoldername)

                        self.menubutton.add(*self.mapselectbutton)
                        self.allui.add(*self.mapselectbutton, self.maplistbox)

                    elif self.optionbutton.event: # change main menu to option menu
                        self.menustate = "option"
                        self.optionbutton.event = False
                        self.allui.remove(*self.menubutton)
                        self.menubutton.remove(*self.menubutton)

                        self.menubutton.add(*self.optionmenubutton)
                        self.allui.add(*self.menubutton,self.optionmenuslider,self.valuebox)
                        self.allui.add(*self.optioniconlist)

                    elif self.lorebutton.event: # open encyclopedia
                        self.lorescroll = gameui.Uiscroller(self.lorenamelist.rect.topright, self.lorenamelist.image.get_height(),
                                                            self.lorebook.maxsubsectionshow, layer=14)  # add subsection list scroller

                        #v Seem like encyclopedia in battle cause container to change allui in main to maingame one, change back with this
                        gamelorebook.Subsectionname.containers = self.subsectionname, self.allui
                        #^ End container change

                        self.menustate = "encyclopedia"
                        self.allui.add(self.lorebook, self.lorenamelist, *self.lorebuttonui, self.lorescroll)  # add sprite related to encyclopedia
                        self.lorebook.changesection(0, self.lorenamelist, self.subsectionname, self.lorescroll, self.pagebutton, self.allui)
                        self.lorebutton.event = False

                elif self.menustate == "presetselect" or self.menustate == "customselect":
                    if mouse_up:
                        for index, name in enumerate(self.mapname):  # too lazy to include break for button found to avoid subsection loop since not much optimisation is needed here
                            if name.rect.collidepoint(self.mousepos):  # click on subsection name
                                self.currentmapselect = index  # change selected map index
                                if self.menustate == "presetselect": # make new map image
                                    self.makemap(self.mapfoldername)
                                    self.maketeamcoa(self.mapfoldername)
                                else:
                                    self.makemap(self.mapcustomfoldername)
                                    self.maketeamcoa(self.mapcustomfoldername)
                                break  # found clicked subsection, break loop


                    if self.mapbackbutton.event:
                        self.menustate = "mainmenu"
                        self.mapbackbutton.event = False
                        self.currentmaprow = 0
                        self.currentmapselect = 0

                        self.allui.remove(*self.menubutton, self.maplistbox, self.mapshow, self.teamcoa)
                        self.menubutton.remove(*self.menubutton)

                        for group in (self.mapshow, self.mapname, self.teamcoa): # remove map image
                            for stuff in group:
                                stuff.kill()
                                del stuff

                        self.menubutton.add(*self.mainmenubutton)
                        self.allui.add(*self.menubutton)

                    elif self.selectbutton.event: # select this map, go to prepare setup
                        self.menustate = "battlemapset"
                        self.selectbutton.event = False

                        self.allui.remove(*self.mapselectbutton, self.maplistbox)
                        self.menubutton.remove(*self.mapselectbutton)
                        for name in self.mapname:  # remove map name list
                            name.kill()
                            del name

                        for team in self.teamcoa:
                            if self.teamselected == team.team:
                                team.selected = True
                                team.changeselect()

                        self.menubutton.add(*self.battlesetupbutton)
                        self.allui.add(*self.battlesetupbutton)

                elif self.menustate == "battlemapset":
                    if mouse_up:
                        for team in self.teamcoa:
                            if team.rect.collidepoint(self.mousepos):
                                self.teamselected = team.team
                                team.selected = True
                                team.changeselect()
                                break

                    for team in self.teamcoa:
                        if self.teamselected != team.team and team.selected:
                            team.selected = False
                            team.changeselect()

                    if self.mapbackbutton.event:
                        self.menustate = self.lastselect
                        self.mapbackbutton.event = False
                        self.allui.remove(*self.menubutton, self.maplistbox)
                        self.menubutton.remove(*self.menubutton)

                        #v Reset selected team
                        for team in self.teamcoa:
                            team.selected = False
                            team.changeselect()
                        self.teamselected = 1
                        #^ End reset selected team

                        if self.menustate == "presetselect": # regenerate map name list
                            self.setupmaplist(self.maplist)
                        else:
                            self.setupmaplist(self.mapcustomlist)

                        self.menubutton.add(*self.mapselectbutton)
                        self.allui.add(*self.mapselectbutton, self.maplistbox)

                    elif self.startbutton.event: # start game button
                        self.battlegame = maingamefunc.Battle(self.winstyle, self.ruleset, self.rulesetfolder, self.teamselected, self.enactment)
                        self.battlegame.rungame()
                        self.startbutton.event = False

                elif self.menustate == "option":
                    for bar in self.resolutionbar: # loop to find which resolution bar is selected, this happen outside of clicking check below
                        if bar.event:
                            self.resolutionscroll.changestate(bar.text)  # change button value based on new selected value
                            resolutionchange = bar.text.split()
                            self.newScreenWidth = resolutionchange[0]
                            self.newScreenHeight = resolutionchange[2]

                            editconfig('DEFAULT', 'ScreenWidth', self.newScreenWidth, 'configuration.ini', config)
                            editconfig('DEFAULT', 'ScreenHeight', self.newScreenHeight, 'configuration.ini', config)
                            self.screen = pygame.display.set_mode(SCREENRECT.size, self.winstyle | pygame.RESIZABLE, self.bestdepth)

                            bar.event = False
                            self.menubutton.remove(self.resolutionbar)

                            break

                    if mouse_up or mouse_down:
                        self.allui.remove(self.resolutionbar)
                        if self.backbutton.event: # back to main menu
                            self.menustate = "mainmenu"
                            self.backbutton.event = False
                            self.allui.remove(*self.menubutton)

                            self.menubutton.remove(*self.menubutton)
                            self.menubutton.add(*self.mainmenubutton)

                            self.allui.remove(*self.optioniconlist,self.optionmenuslider,self.valuebox)
                            self.allui.add(*self.menubutton)

                        elif self.resolutionscroll.rect.collidepoint(self.mousepos): # click on resolution bar
                            if self.resolutionbar in self.allui: # remove the bar list if click again
                                self.allui.remove(self.resolutionbar)
                                self.menubutton.remove(self.resolutionbar)
                            else: # add bar list
                                self.allui.add(self.resolutionbar)
                                self.menubutton.add(self.resolutionbar)

                        elif self.volumeslider.rect.collidepoint(self.mousepos) and (mouse_down or mouse_up):  # mouse click on slider bar
                            self.volumeslider.update(self.mousepos, self.valuebox[0])  # update slider button based on mouse value
                            self.mixervolume = float(self.volumeslider.value / 100)  # for now only music volume slider exist
                            editconfig('DEFAULT', 'SoundVolume', str(self.volumeslider.value), 'configuration.ini', config)
                            pygame.mixer.music.set_volume(self.mixervolume)

                elif self.menustate == "encyclopedia":
                    if mouse_up or mouse_down: # mouse down (hold click) only for subsection listscroller
                        if mouse_up:
                            for button in self.lorebuttonui:
                                if button in self.allui and button.rect.collidepoint(self.mousepos): # click button
                                    if button.event in range(0, 11): # section button
                                        self.lorebook.changesection(button.event, self.lorenamelist, self.subsectionname, self.lorescroll, self.pagebutton, self.allui) # change to section of that button

                                    elif button.event == 19:  # Close button
                                        self.allui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll, self.lorenamelist) # remove enclycopedia related sprites
                                        for name in self.subsectionname: # remove subsection name
                                            name.kill()
                                            del name
                                        self.menustate = "mainmenu" # change menu back to default 0

                                    elif button.event == 20:  # Previous page button
                                        self.lorebook.changepage(self.lorebook.page - 1, self.pagebutton, self.allui) # go back 1 page

                                    elif button.event == 21:  # Next page button
                                        self.lorebook.changepage(self.lorebook.page + 1, self.pagebutton, self.allui) # go forward 1 page

                                    break # found clicked button, break loop

                            for name in self.subsectionname: # too lazy to include break for button found to avoid subsection loop since not much optimisation is needed here
                                if name.rect.collidepoint(self.mousepos): # click on subsection name
                                    self.lorebook.changesubsection(name.subsection, self.pagebutton, self.allui) # change subsection
                                    break # found clicked subsection, break loop

                        if self.lorescroll.rect.collidepoint(self.mousepos): # click on subsection list scroller
                            self.lorebook.currentsubsectionrow = self.lorescroll.update(self.mousepos) # update the scroller and get new current subsection
                            self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname) # update subsection name list

                self.allui.draw(self.screen)
                pygame.display.update()
                self.clock.tick(60)

            if pygame.mixer:
                pygame.mixer.music.fadeout(1000)

            pygame.time.wait(1000)
            pygame.quit()
            sys.exit()

    if __name__ == '__main__':
        runmenu = Mainmenu()
        runmenu.run(maingame)

except Exception:  # Save error output to txt file
    traceback.print_exc()
    f = open("error_report.txt", 'w')
    sys.stdout = f
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    print(''.join('!! ' + line for line in lines))  # Log it or whatever here
    f.close()
    # try: # seem like printing error when quit game to desktop during battle cause error
    # except:
    #     pass
