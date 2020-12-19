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

    from gamescript import maingame, gamelorebook, gamelongscript

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

    class Menubutton(pygame.sprite.Sprite):
        def __init__(self, images, pos, text="", size=16):
            pygame.sprite.Sprite.__init__(self, self.containers)
            self.pos = pos
            self.images = [image.copy() for image in images]
            self.text = text
            self.font = pygame.font.SysFont("timesnewroman", size)
            if text != "":
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
                if self.mouse_value < self.minvalue:
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

    # def encyclopedia(screen):
    #     gamearmy.leader
    #     gamearmy.weaponstat
    #     gamearmy.unitstat

    class Mainmenu():
        def __init__(self):
            pygame.init() # Initialize pygame
            self.allui = pygame.sprite.RenderUpdates()
            self.menubutton = pygame.sprite.Group() # group of menu buttons that are currently get shown and update
            self.menuicon = pygame.sprite.Group()
            self.menuslider = pygame.sprite.Group()
            self.valuebox = pygame.sprite.Group() # value box of slider bar
            Menubutton.containers = self.menubutton
            Menuicon.containers = self.menuicon
            Slidermenu.containers = self.menuslider
            Valuebox.containers = self.valuebox

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

            #v Create main menu button
            imagelist = load_base_button()
            self.startbutton = Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 5.5)), text="START")
            self.lorebutton = Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 4)), text="Encyclopedia")
            self.optionbutton = Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 2.5)), text="OPTION")
            self.quitbutton = Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height())), text="QUIT")
            self.mainmenubutton = (self.startbutton,self.quitbutton,self.optionbutton, self.lorebutton)
            #^ End main menu button

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
            self.rulesetlist = maingame.csv_read("ruleset_list.csv", ['data', 'ruleset'])
            self.ruleset = 1
            self.rulesetfolder = "/" + str(self.rulesetlist[self.ruleset][1])

        def run(self, maingamefunc):
            while True:
                #v Get user input
                mouse_up = False
                mouse_down = False
                for event in pygame.event.get():
                    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE) or self.quitbutton.event == True:
                        return
                    if pygame.mouse.get_pressed()[0]: # Hold left click
                        mouse_down = True
                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # left click
                        mouse_up = True
                keystate = pygame.key.get_pressed()
                mouse_pos = pygame.mouse.get_pos()
                #^ End user

                self.screen.blit(self.background, (0, 0))  # blit blackground over instead of clear() to reset screen
                self.menubutton.update(mouse_pos, mouse_up, mouse_down)

                if self.menustate == "mainmenu":
                    if self.startbutton.event: # start game button
                        self.battlegame = maingamefunc.Battle(self.winstyle, self.ruleset, self.rulesetfolder)
                        self.battlegame.rungame()
                        self.startbutton.event = False
                    elif self.optionbutton.event:
                        self.menustate = "option"
                        self.optionbutton.event = False
                        self.allui.remove(*self.menubutton)
                        self.menubutton.remove(*self.menubutton)
                        self.menubutton.add(*self.optionmenubutton)
                        self.allui.add(*self.menubutton,self.optionmenuslider,self.valuebox)
                        self.allui.add(*self.optioniconlist)
                    elif self.lorebutton.event:
                        # self.menustate = "encyclopedia"
                        self.lorebutton.event = False
                elif self.menustate == "option":
                    for bar in self.resolutionbar:
                        if bar.event:
                            self.resolutionscroll.changestate(bar.text)  # change button value based on selected
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
                        elif self.resolutionscroll.rect.collidepoint(mouse_pos): # resolution bar
                            if self.resolutionbar in self.allui:
                                self.allui.remove(self.resolutionbar)
                                self.menubutton.remove(self.resolutionbar)
                            else:
                                self.allui.add(self.resolutionbar)
                                self.menubutton.add(self.resolutionbar)
                        elif self.volumeslider.rect.collidepoint(mouse_pos) and (mouse_down or mouse_up):  # mouse click on slider bar
                            self.volumeslider.update(mouse_pos, self.valuebox[0])  # update slider button based on mouse value
                            self.mixervolume = float(self.volumeslider.value / 100)  # for now only music volume slider exist
                            pygame.mixer.music.set_volume(self.mixervolume)
                            editconfig('DEFAULT', 'SoundVolume', str(self.volumeslider.value), 'configuration.ini', config)

                elif self.menustate == "enclycopedia":
                    pass

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

except NameError:  # Save error output to txt file
    f = open("error_report.txt", 'w')
    sys.stdout = f
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    print(''.join('!! ' + line for line in lines))  # Log it or whatever here
    f.close()
