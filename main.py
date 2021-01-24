try: # for printing error log when error exception happen
    import configparser
    import glob
    import os.path
    import sys
    import traceback
    import gc

    # import basic pygame modules
    import pygame
    import pygame.freetype
    from pygame.locals import *

    from gamescript import maingame, gameleader, gamemap, gamelongscript, gamelorebook, gameweather, gamedrama, \
        gamefaction, gameunitstat, gameui, gameprepare, gamemenu, gamebattalion, gamesquad,rangeattack, gamepopup

    if not os.path.exists('profile'): # make profile folder if not existed
        os.makedirs('profile')
        os.makedirs('profile/armypreset')

    # if not os.path.exists('\customunit'): # make custom unit folder if not existed


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
    Profilename = str(config['DEFAULT']['playername'])

    SCREENRECT = Rect(0, 0, ScreenWidth, ScreenHeight)
    widthadjust = SCREENRECT.width / 1366
    heightadjust = SCREENRECT.height / 768

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
            bar = gameprepare.Menubutton(images=barimage, pos=(menuimage.pos[0], menuimage.pos[1] + img.get_height() * (index + 1)), text=bar)
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

    class Mainmenu():
        def __init__(self):
            pygame.init() # Initialize pygame

            self.rulesetlist = maingame.csv_read("ruleset_list.csv", ['data', 'ruleset']) # get ruleset list
            self.ruleset = 1 # for now default historical ruleset only
            self.rulesetfolder = "/" + str(self.rulesetlist[self.ruleset][1])
            self.enactment = True
            self.mapsource = 0 # current selected map source
            self.teamselected = 1

            #v Set the display mode
            self.winstyle = 0  # FULLSCREEN
            if FULLSCREEN == 1:
                self.winstyle = pygame.FULLSCREEN
            self.bestdepth = pygame.display.mode_ok(SCREENRECT.size, self.winstyle, 32)
            self.screen = pygame.display.set_mode(SCREENRECT.size, self.winstyle | pygame.RESIZABLE, self.bestdepth)
            #^ End set display

            # v Decorate the game window
            # icon = load_image('sword.jpg')
            # icon = pygame.transform.scale(icon, (32, 32))
            # pygame.display.set_icon(icon)
            # ^ End decorate

            # v Initialise Game Groups
            # main menu object group
            self.mainui = pygame.sprite.LayeredUpdates()
            self.menubutton = pygame.sprite.Group()  # group of menu buttons that are currently get shown and update
            self.menuicon = pygame.sprite.Group()

            self.inputui = pygame.sprite.Group()
            self.inputbox = pygame.sprite.Group()

            self.profilebox = pygame.sprite.Group()

            self.menuslider = pygame.sprite.Group()
            self.maplistbox = pygame.sprite.Group()
            self.mapscroll = pygame.sprite.Group()
            self.mapnamegroup = pygame.sprite.Group()
            self.mapshow = pygame.sprite.Group()
            self.teamcoa = pygame.sprite.Group()
            self.maptitle = pygame.sprite.Group()
            self.mapdescription = pygame.sprite.Group()
            self.sourcedescription = pygame.sprite.Group()
            self.armystat = pygame.sprite.Group()

            self.sourcescroll = pygame.sprite.Group()
            self.sourcelistbox = pygame.sprite.Group()
            self.sourcenamegroup = pygame.sprite.Group()

            self.mapoptionbox = pygame.sprite.Group()
            self.tickbox = pygame.sprite.Group()

            self.lorebuttonui = pygame.sprite.Group()  # buttons for enclycopedia group
            self.lorebook = pygame.sprite.Group()  # encyclopedia object
            self.slidermenu = pygame.sprite.Group()
            self.valuebox = pygame.sprite.Group()  # value number and box in esc menu option
            self.lorenamelist = pygame.sprite.Group()  # box sprite for showing subsection name list in encyclopedia
            self.lorescroll = pygame.sprite.Group()  # scroller for subsection name list in encyclopedia
            self.subsectionname = pygame.sprite.Group()  # subsection name objects group in encyclopedia blit on lorenamelist

            # battle object group
            self.battlecamera = pygame.sprite.LayeredUpdates()  # this is layer drawer game camera, all image pos should be based on the map not screen
            ## the camera layer is as followed 0 = terrain map, 1 = dead army, 2 = map special feature, 3 = hitbox, 4 = direction arrow,
            ## 5 = battalion, 6 = flying battalion, 7 = arrow/range, 8 = weather, 9 = weather matter, 10 = ui/button, 11 = squad inspect, 12 pop up
            self.battleui = pygame.sprite.LayeredUpdates()  # this is layer drawer for ui, all image pos should be based on the screen

            self.battalionupdater = pygame.sprite.Group()  # updater for battalion objects
            self.hitboxupdater = pygame.sprite.Group()  # updater for hitbox objects
            self.squadupdater = pygame.sprite.Group()  # updater for squad objects
            self.leaderupdater = pygame.sprite.Group()  # updater for leader objects
            self.uiupdater = pygame.sprite.Group()  # updater for ui objects
            self.weatherupdater = pygame.sprite.Group()  # updater for weather objects
            self.effectupdater = pygame.sprite.Group()  # updater for in-game effect objects (e.g. range attack sprite)

            self.battlemapbase = pygame.sprite.Group()  # base terrain map object
            self.battlemapfeature = pygame.sprite.Group()  # terrain feature map object
            self.battlemapheight = pygame.sprite.Group()  # height map object
            self.showmap = pygame.sprite.Group()  # beautiful map object that is shown in gameplay

            self.team0army = pygame.sprite.Group()  # taem 0 battalions group
            self.team1army = pygame.sprite.Group()  # taem 1 battalions group
            self.team2army = pygame.sprite.Group()  # team 2 battalions group

            self.squad = pygame.sprite.Group()  # all squads group

            self.armyleader = pygame.sprite.Group()  # all leaders group

            self.hitboxes = pygame.sprite.Group()  # all hitboxes group
            self.arrows = pygame.sprite.Group()  # all arrows group and maybe other range effect stuff later
            self.directionarrows = pygame.sprite.Group()

            self.deadunit = pygame.sprite.Group()  # dead unit group

            self.gameui = pygame.sprite.Group()  # various game ui group
            self.minimap = pygame.sprite.Group()  # minimap ui
            self.eventlog = pygame.sprite.Group()  # event log ui
            self.logscroll = pygame.sprite.Group()  # scroller fro event log ui
            self.buttonui = pygame.sprite.Group()  # buttons for various ui group
            self.squadselectedborder = pygame.sprite.Group()  # squad selected border in inspect ui army box
            self.fpscount = pygame.sprite.Group()  # fps number counter
            self.switchbuttonui = pygame.sprite.Group()  # button that switch image based on current setting (e.g. battalion behaviour setting)

            self.terraincheck = pygame.sprite.Group()  # terrain information pop up ui
            self.buttonnamepopup = pygame.sprite.Group()  # button name pop up ui when mouse over button
            self.leaderpopup = pygame.sprite.Group()  # leader name pop up ui when mouse over leader image in command ui
            self.effectpopup = pygame.sprite.Group()  # effect name pop up ui when mouse over status effect icon
            self.textdrama = pygame.sprite.Group()  # dramatic text effect (announcement) object

            self.skillicon = pygame.sprite.Group()  # skill and trait icon objects
            self.effecticon = pygame.sprite.Group()  # status effect icon objects

            self.battlemenu = pygame.sprite.Group()  # esc menu object
            self.battlemenubutton = pygame.sprite.Group()  # buttons for esc menu object group
            self.escoptionmenubutton = pygame.sprite.Group()  # buttons for esc menu option object group
            self.slidermenu = pygame.sprite.Group()

            self.armyselector = pygame.sprite.Group()  # army selector ui
            self.armyicon = pygame.sprite.Group()  # army icon object group in army selector ui
            self.selectscroll = pygame.sprite.Group()  # scoller object in army selector ui

            self.timeui = pygame.sprite.Group()  # time bar ui
            self.timenumber = pygame.sprite.Group()  # number text of in-game time
            self.speednumber = pygame.sprite.Group()  # number text of current game speed

            self.scaleui = pygame.sprite.Group()

            self.weathermatter = pygame.sprite.Group()  # sprite of weather effect group such as rain sprite
            self.weathereffect = pygame.sprite.Group()  # sprite of special weather effect group such as fog that cover whole screen
            # ^ End initialise

            # v Assign default groups
            # main menu containers
            gameprepare.Inputbox.containers = self.inputbox
            gameprepare.Inputui.containers = self.inputui

            gameprepare.Profilebox.containers = self.profilebox

            gameprepare.Menubutton.containers = self.menubutton
            gameprepare.Menuicon.containers = self.menuicon
            gameprepare.Slidermenu.containers = self.menuslider
            gameprepare.Valuebox.containers = self.valuebox

            gameprepare.Maplistbox.containers = self.maplistbox
            gameprepare.Mapname.containers = self.mapnamegroup, self.mainui
            gameprepare.Mapshow.containers = self.mapshow
            gameprepare.Teamcoa.containers = self.teamcoa
            gameprepare.Maptitle.containers = self.maptitle
            gameprepare.Mapdescription.containers = self.mapdescription
            gameprepare.Sourcedescription.containers = self.sourcedescription
            gameprepare.Armystat.containers = self.armystat

            gameprepare.Sourcelistbox.containers = self.sourcelistbox
            gameprepare.Sourcename.containers = self.sourcenamegroup, self.mainui

            gameprepare.Mapoptionbox.containers = self.mapoptionbox
            gameprepare.Tickbox.containers = self.tickbox

            gamelorebook.Lorebook.containers = self.lorebook
            gamelorebook.Subsectionlist.containers = self.lorenamelist
            gamelorebook.Subsectionname.containers = self.subsectionname, self.mainui, self.battleui

            gameui.Uibutton.containers = self.lorebuttonui
            gameui.Uiscroller.containers = self.mapscroll, self.sourcescroll, self.lorescroll, self.logscroll, self.selectscroll

            # battle containers
            gamemap.Basemap.containers = self.battlemapbase
            gamemap.Mapfeature.containers = self.battlemapfeature
            gamemap.Mapheight.containers = self.battlemapheight
            gamemap.Beautifulmap.containers = self.showmap, self.battlecamera

            gamebattalion.Unitarmy.containers = self.battalionupdater, self.battlecamera
            gamesquad.Unitsquad.containers = self.squadupdater, self.squad
            gamebattalion.Deadarmy.containers = self.deadunit, self.battalionupdater, self.battlecamera
            gamebattalion.Hitbox.containers = self.hitboxes, self.hitboxupdater
            gameleader.Leader.containers = self.armyleader, self.leaderupdater

            rangeattack.Rangearrow.containers = self.arrows, self.effectupdater, self.battlecamera
            gamebattalion.Directionarrow.containers = self.directionarrows, self.effectupdater, self.battlecamera

            gameui.Gameui.containers = self.gameui, self.uiupdater
            gameui.Minimap.containers = self.minimap, self.battleui
            gameui.FPScount.containers = self.battleui
            gameui.Uibutton.containers = self.buttonui, self.lorebuttonui
            gameui.Switchuibutton.containers = self.switchbuttonui, self.uiupdater
            gameui.Selectedsquad.containers = self.squadselectedborder
            gameui.Skillcardicon.containers = self.skillicon, self.battleui
            gameui.Effectcardicon.containers = self.effecticon, self.battleui
            gameui.Eventlog.containers = self.eventlog, self.battleui
            gameui.Armyselect.containers = self.armyselector, self.battleui
            gameui.Armyicon.containers = self.armyicon, self.battleui
            gameui.Timeui.containers = self.timeui, self.battleui
            gameui.Timer.containers = self.timenumber, self.battleui
            gameui.Scaleui.containers = self.scaleui, self.battleui
            gameui.Speednumber.containers = self.speednumber, self.battleui

            gamepopup.Terrainpopup.containers = self.terraincheck
            gamepopup.Onelinepopup.containers = self.buttonnamepopup, self.leaderpopup
            gamepopup.Effecticonpopup.containers = self.effectpopup

            gamedrama.Textdrama.containers = self.textdrama

            gamemenu.Escbox.containers = self.battlemenu
            gamemenu.Escbutton.containers = self.battlemenubutton, self.escoptionmenubutton
            gamemenu.Escslidermenu.containers = self.slidermenu
            gamemenu.Escvaluebox.containers = self.valuebox

            gameweather.Mattersprite.containers = self.weathermatter, self.battleui, self.weatherupdater
            gameweather.Specialeffect.containers = self.weathereffect, self.battleui, self.weatherupdater
            # ^ End assign

            gamelongscript.loadgamedata(self) # obtain game stat data and create lore book object

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
            for index, image in enumerate(imagelist):
                imagelist[index] = pygame.transform.scale(image, (int(image.get_width() * widthadjust),
                                                       int(image.get_height() * heightadjust)))
            self.presetmapbutton = gameprepare.Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 8.5)),
                                          text="Preset Map")
            self.custommapbutton = gameprepare.Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 7)),
                                          text="Custom Map")
            self.uniteditbutton = gameprepare.Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 5.5)), text="Unit Editor")
            self.lorebutton = gameprepare.Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 4)), text="Encyclopedia")
            self.optionbutton = gameprepare.Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 2.5)), text="Option")
            self.quitbutton = gameprepare.Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height())), text="Quit")
            self.mainmenubutton = (self.presetmapbutton, self.custommapbutton, self.uniteditbutton, self.lorebutton, self.optionbutton, self.quitbutton)
            #^ End main menu button

            #v Create battle map menu button
            bottomheight = SCREENRECT.height - imagelist[0].get_height()
            self.selectbutton = gameprepare.Menubutton(images=imagelist, pos=(SCREENRECT.width - imagelist[0].get_width(), bottomheight),
                                          text="Select")
            self.startbutton = gameprepare.Menubutton(images=imagelist, pos=(SCREENRECT.width - imagelist[0].get_width(), bottomheight),
                                          text="Start")
            self.mapbackbutton = gameprepare.Menubutton(images=imagelist, pos=(SCREENRECT.width - (SCREENRECT.width - imagelist[0].get_width()), bottomheight),
                                         text="Back")
            self.mapselectbutton = (self.selectbutton, self.mapbackbutton)
            self.battlesetupbutton = (self.startbutton, self.mapbackbutton)

            imgs = load_images(['ui', 'mapselect_ui'], loadorder=False)
            self.maplistbox = gameprepare.Maplistbox((SCREENRECT.width/25, SCREENRECT.height/20), imgs[0])
            self.sourcelistbox = gameprepare.Sourcelistbox((0, 0), imgs[1])
            self.mapoptionbox = gameprepare.Mapoptionbox((SCREENRECT.width, 0), imgs[1], 0)

            self.tickboxenactment = gameprepare.Tickbox((self.mapoptionbox.rect.bottomright[0] / 1.2, self.mapoptionbox.rect.bottomright[1] / 4),
                                                        imgs[5], imgs[6], "enactment")
            self.tickbox.add(self.tickboxenactment)
            if self.enactment:
                self.tickboxenactment.changetick(True)

            gameprepare.Mapdescription.image = imgs[2]
            gameprepare.Sourcedescription.image = imgs[3]
            gameprepare.Armystat.image = imgs[4]

            self.currentmaprow = 0
            self.currentmapselect = 0

            self.currentsourcerow = 0

            #^ End battle map menu button

            #v Create unit editor button and ui

            self.armyeditbutton = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 4)),
                                          text="Army Editor")
            self.troopcreatetbutton = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 2.5)),
                                          text="Troop Creator")
            self.editorbackbutton = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height - imagelist[0].get_height()),
                                         text="Back")
            self.editorbutton = (self.armyeditbutton, self.troopcreatetbutton, self.editorbackbutton)

            # v Input box popup
            inputuiimg = load_image('inputui.png', 'ui')
            self.inputui = gameprepare.Inputui(inputuiimg, (SCREENRECT.width / 2, SCREENRECT.height / 2))
            self.inputokbutton = gameprepare.Menubutton(images=imagelist,
                                                        pos=(self.inputui.rect.midleft[0] + imagelist[0].get_width(),
                                                             self.inputui.rect.midleft[1] + imagelist[0].get_height()),
                                                        text="Done")
            self.inputcancelbutton = gameprepare.Menubutton(images=imagelist,
                                                            pos=(self.inputui.rect.midright[0] - imagelist[0].get_width(),
                                                                 self.inputui.rect.midright[1] + imagelist[0].get_height()),
                                                            text="Cancel")
            self.inputbutton = (self.inputokbutton, self.inputcancelbutton)
            self.inputbox = gameprepare.Inputbox((self.inputui.rect.center), self.inputui.image.get_width())

            self.inputuipop = (self.inputui, self.inputbox, self.inputokbutton, self.inputcancelbutton)
            # ^ End input box popup

            #^ End unit editor

            #v profile box
            self.profilename = Profilename
            img = load_image('profilebox.png', 'ui')
            self.profilebox = gameprepare.Profilebox(img, (ScreenWidth, 0), self.profilename)
            #^ End profile box

            #v Create option menu button and icon
            self.backbutton = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height / 1.2), text="BACK")

            # Resolution changing bar that fold out the list when clicked
            img = load_image('scroll_normal.jpg', 'ui')
            img2 = img
            img3 = load_image('scroll_click.jpg', 'ui')
            imagelist = [img, img2, img3]
            self.resolutionscroll = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height / 2.3),
                                               text=str(ScreenWidth) + " x " + str(ScreenHeight), size=16)
            resolutionlist = ['1920 x 1080', '1600 x 900', '1366 x 768', '1280 x 720', '1024 x 768', ]
            self.resolutionbar = makebarlist(listtodo=resolutionlist, menuimage=self.resolutionscroll)
            img = load_image('resolution_icon.png', 'ui')
            self.resolutionicon = gameprepare.Menuicon([img], (self.resolutionscroll.pos[0] - (self.resolutionscroll.pos[0] / 4.5), self.resolutionscroll.pos[1]), imageresize=50)
            # End resolution

            # Volume change scroller bar
            img = load_image('scroller.png', 'ui')
            img2 = load_image('scoll_button_normal.png', 'ui')
            img3 = load_image('scoll_button_click.png', 'ui')
            img4 = load_image('numbervalue_icon.jpg', 'ui')
            self.volumeslider = gameprepare.Slidermenu(barimage=img, buttonimage=[img2, img3], pos=(SCREENRECT.width / 2, SCREENRECT.height / 3),
                                           value=Soundvolume)
            self.valuebox = [gameprepare.Valuebox(img4, (self.volumeslider.rect.topright[0] * 1.1, self.volumeslider.rect.topright[1]), Soundvolume)]
            img = load_image('volume_icon.png', 'ui')
            self.volumeicon = gameprepare.Menuicon([img], (self.volumeslider.pos[0] - (self.volumeslider.pos[0] / 4.5), self.volumeslider.pos[1]), imageresize=50)
            # End volume change

            self.optioniconlist = (self.resolutionicon,self.volumeicon)
            self.optionmenubutton = (self.backbutton,self.resolutionscroll)
            self.optionmenuslider = (self.volumeslider)
            #^ End option menu button

            pygame.display.set_caption('Dream Decision') # set the game name on program border/tab
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

            self.mainui.remove(*self.menubutton)  # remove all button from drawing
            self.menubutton.remove(*self.menubutton) # remove all button at the start and add later depending on menustate
            self.menubutton.add(*self.mainmenubutton) # add only main menu button back
            self.mainui.add(*self.menubutton, self.profilebox)
            self.menustate = "mainmenu"
            self.textinputpopup = None

            self.battlegame = maingame.Battle(self, self.winstyle)

        def backtomainmenu(self):
            self.menustate = "mainmenu"

            self.mainui.remove(*self.menubutton)

            self.menubutton.remove(*self.menubutton)
            self.menubutton.add(*self.mainmenubutton)

            self.mainui.add(*self.menubutton, self.profilebox)

        def setuplist(self, itemclass, currentrow, showlist, itemgroup, box):
            """generate list of subsection of the left side of encyclopedia"""
            row = 5
            column = 5
            pos = box.rect.topleft
            if currentrow > len(showlist) - box.maxshowlist:
                currentrow = len(showlist) - box.maxshowlist

            if len(itemgroup) > 0:  # remove previous sprite in the group before generate new one
                for stuff in itemgroup:
                    stuff.kill()
                    del stuff

            for index, item in enumerate(showlist):
                if index >= currentrow:
                    itemgroup.add(itemclass(box, (pos[0] + column, pos[1] + row), item))  # add new subsection sprite to group
                    row += 30  # next row
                    if len(itemgroup) > box.maxshowlist: break  # will not generate more than space allowed

        def readmapdata(self, maplist, file):
            if self.menustate == "presetselect" or self.lastselect == "presetselect":
                data = csv_read(file,['data', 'ruleset', self.rulesetfolder.strip("/"), 'map', maplist[self.currentmapselect]])
            else:
                data = csv_read(file, ['data', 'ruleset', self.rulesetfolder.strip("/"), 'map/custom',  maplist[self.currentmapselect]])
            return data

        def maketeamcoa(self, data):
            for team in self.teamcoa:
                team.kill()
                del team

            # position = self.mapshow[0].get_rect()
            team1index = list(data.values())[1][2]
            team2index = list(data.values())[1][3]
            self.teamcoa.add(gameprepare.Teamcoa((SCREENRECT.width/2 - (300 * widthadjust),SCREENRECT.height/3), self.coa[team1index],
                                                 1, self.allfaction.factionlist[team1index][0])) # team 1

            self.teamcoa.add(gameprepare.Teamcoa((SCREENRECT.width/2 + (300 * widthadjust),SCREENRECT.height/3), self.coa[team2index],
                                                 2, self.allfaction.factionlist[team2index][0])) # team 2
            self.mainui.add(self.teamcoa)

        def makemap(self, mapfolderlist, maplist):
            #v Create map preview image
            for thismap in self.mapshow:
                thismap.kill()
                del thismap
            if self.menustate == "presetselect":
                imgs = load_images(['ruleset', self.rulesetfolder.strip("/"), 'map', mapfolderlist[self.currentmapselect]], loadorder=False)
            else:
                imgs = load_images(['ruleset', self.rulesetfolder.strip("/"), 'map/custom', mapfolderlist[self.currentmapselect]], loadorder=False)
            self.mapshow.add(gameprepare.Mapshow((SCREENRECT.width/2, SCREENRECT.height/3), imgs[0], imgs[1]))
            self.mainui.add(self.mapshow)
            #^ End map preview

            #v Create map title at the top
            for name in self.maptitle:
                name.kill()
                del name
            self.maptitle.add(gameprepare.Maptitle(maplist[self.currentmapselect], (SCREENRECT.width / 2, 0)))
            self.mainui.add(self.maptitle)
            #^ End map title

            #v Create map description
            data = self.readmapdata(mapfolderlist, 'info.csv')
            description = [list(data.values())[1][0], list(data.values())[1][1]]
            for desc in self.mapdescription:
                desc.kill()
                del desc
            self.mapdescription.add(gameprepare.Mapdescription((SCREENRECT.width / 2, SCREENRECT.height / 1.3), description))
            self.mainui.add(self.mapdescription)
            #^ End map description

            self.maketeamcoa(data)

        def changesource(self, descriptiontext, scalevalue):
            """Change source description, add new unit dot, change army stat when select new source"""
            for desc in self.sourcedescription:
                desc.kill()
                del desc
            self.sourcedescription.add(gameprepare.Sourcedescription((SCREENRECT.width / 2, SCREENRECT.height / 1.3), descriptiontext))
            self.mainui.add(self.sourcedescription)

            openfolder = self.mapfoldername
            if self.lastselect == "customselect":
                openfolder = self.mapcustomfoldername
            unitmapinfo = self.readmapdata(openfolder, 'unit_pos' + str(self.mapsource) + '.csv')

            team1pos = {row[8]:[int(item) for item in row[8].split(',')] for row in list(unitmapinfo.values()) if row[15] == 1}
            team2pos = {row[8]:[int(item) for item in row[8].split(',')] for row in list(unitmapinfo.values()) if row[15] == 2}
            for thismap in self.mapshow:
                thismap.changemode(1, team1poslist = team1pos, team2poslist = team2pos)

            team1army = []
            team2army = []
            team1commander = []
            team2commander = []
            for index, row in enumerate(list(unitmapinfo.values())):
                if row[15] == 1:
                    listadd = team1army
                elif row[15] == 2:
                    listadd = team2army
                for smallrow in row[0:7]:
                    for item in smallrow.split(','):
                        listadd.append(int(item))

                for item in row[9].split(','):
                    if row[15] == 1:
                        team1commander.append(int(item))
                    elif row[15] == 2:
                        team2commander.append(int(item))

            teamtotal = [0,0] # total troop number in army
            trooptypelist = [[0,0,0,0],[0,0,0,0]] # total number of each troop type
            leadernamelist = (team1commander, team2commander)
            armyteamlist = (team1pos,team2pos) # for finding how many unit in each team

            armylooplist = (team1army, team2army)
            for index, team in enumerate(armylooplist):
                for unit in team:
                    if unit != 0:
                        teamtotal[index] += int(self.gameunitstat.unitlist[unit][27] * scalevalue[index])
                        trooptype = 0
                        if self.gameunitstat.unitlist[unit][22] != [1,0] \
                                and self.gameunitstat.unitlist[unit][8] < self.gameunitstat.unitlist[unit][12]: # range weapon and accuracy higher than melee attack
                            trooptype += 1
                        if self.gameunitstat.unitlist[unit][29] != [1,0,1]: # cavalry
                            trooptype += 2
                        trooptypelist[index][trooptype] += int(self.gameunitstat.unitlist[unit][27] * scalevalue[index])
                trooptypelist[index].append(len(armyteamlist[index]))

            armylooplist = ["{:,}".format(troop) + " Troops" for troop in teamtotal]
            armylooplist = [self.leaderstat.leaderlist[leadernamelist[index][0]][0] + ": " + troop for index, troop in enumerate(armylooplist)]

            for index, army in enumerate(self.armystat):
                army.addstat(trooptypelist[index], armylooplist[index])

        def run(self):
            while True:
                #v Get user input
                mouse_up = False
                mouse_down = False
                esc_press = False
                for event in pygame.event.get():
                    if self.textinputpopup is not None: # event update to input box
                        self.inputbox.userinput(event)

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

                    elif event.type == KEYDOWN and event.key == K_ESCAPE:
                        esc_press = True

                    if event.type == QUIT or self.quitbutton.event == True or (esc_press and self.menustate == "mainmenu"):
                        return

                # keystate = pygame.key.get_pressed()
                self.mousepos = pygame.mouse.get_pos()
                #^ End user input

                self.screen.blit(self.background, (0, 0))  # blit blackground over instead of clear() to reset screen


                if self.textinputpopup is not None: # currently have input text pop up on screen, stop everything else until done
                    for button in self.inputbutton:
                        button.update(self.mousepos, mouse_up, mouse_down)

                    if self.inputokbutton.event:
                        self.inputokbutton.event = False

                        if self.textinputpopup == "profilename":
                            self.profilename = self.inputbox.text
                            self.profilebox.changename(self.profilename)

                            editconfig('DEFAULT', 'playername', self.profilename, 'configuration.ini', config)

                        self.inputbox.textstart("")
                        self.textinputpopup = None
                        self.mainui.remove(*self.inputuipop)

                    elif self.inputcancelbutton.event or esc_press:
                        self.inputcancelbutton.event = False
                        self.inputbox.textstart("")
                        self.textinputpopup = None
                        self.mainui.remove(*self.inputuipop)

                elif self.textinputpopup is None:
                    self.menubutton.update(self.mousepos, mouse_up, mouse_down)
                    if self.menustate == "mainmenu":

                        if self.presetmapbutton.event: # preset map list menu
                            self.menustate = "presetselect"
                            self.lastselect = self.menustate
                            self.presetmapbutton.event = False
                            self.mainui.remove(*self.menubutton, self.profilebox)
                            self.menubutton.remove(*self.menubutton)

                            self.setuplist(gameprepare.Mapname, self.currentmaprow, self.maplist, self.mapnamegroup, self.maplistbox)
                            self.makemap(self.mapfoldername, self.maplist)

                            self.mapscroll = gameui.Uiscroller(self.maplistbox.rect.topright, self.maplistbox.image.get_height(),
                                                               self.maplistbox.maxshowlist, layer=14)

                            self.menubutton.add(*self.mapselectbutton)
                            self.mainui.add(*self.mapselectbutton, self.maplistbox, self.maptitle, self.mapscroll)


                        elif self.custommapbutton.event: # custom map list menu
                            self.menustate = "customselect"
                            self.lastselect = self.menustate
                            self.custommapbutton.event = False
                            self.mainui.remove(*self.menubutton, self.profilebox)
                            self.menubutton.remove(*self.menubutton)

                            self.setuplist(gameprepare.Mapname, self.currentmaprow, self.mapcustomlist, self.mapnamegroup, self.maplistbox)
                            self.makemap(self.mapcustomfoldername, self.mapcustomlist)

                            self.mapscroll = gameui.Uiscroller(self.maplistbox.rect.topright, self.maplistbox.image.get_height(),
                                                               self.maplistbox.maxshowlist, layer=14)

                            self.menubutton.add(*self.mapselectbutton)
                            self.mainui.add(*self.mapselectbutton, self.maplistbox, self.maptitle, self.mapscroll)

                        elif self.uniteditbutton.event: # custom unit/sub-unit editor menu
                            self.menustate = "uniteditor"
                            self.uniteditbutton.event = False
                            self.mainui.remove(*self.menubutton, self.profilebox)
                            self.menubutton.remove(*self.menubutton)

                            self.menubutton.add(*self.editorbutton)
                            self.mainui.add(*self.editorbutton)

                        elif self.optionbutton.event: # change main menu to option menu
                            self.menustate = "option"
                            self.optionbutton.event = False
                            self.mainui.remove(*self.menubutton, self.profilebox)
                            self.menubutton.remove(*self.menubutton)

                            self.menubutton.add(*self.optionmenubutton)
                            self.mainui.add(*self.menubutton, self.optionmenuslider, self.valuebox)
                            self.mainui.add(*self.optioniconlist)

                        elif self.lorebutton.event: # open encyclopedia
                            self.lorescroll = gameui.Uiscroller(self.lorenamelist.rect.topright, self.lorenamelist.image.get_height(),
                                                                self.lorebook.maxsubsectionshow, layer=14)  # add subsection list scroller

                            #v Seem like encyclopedia in battle cause container to change allui in main to maingame one, change back with this
                            gamelorebook.Subsectionname.containers = self.subsectionname, self.mainui
                            #^ End container change

                            self.menustate = "encyclopedia"
                            self.mainui.add(self.lorebook, self.lorenamelist, *self.lorebuttonui, self.lorescroll)  # add sprite related to encyclopedia
                            self.lorebook.changesection(0, self.lorenamelist, self.subsectionname, self.lorescroll, self.pagebutton, self.mainui)
                            self.lorebutton.event = False

                        elif mouse_up and self.profilebox.rect.collidepoint(self.mousepos):
                            self.textinputpopup = "profilename"
                            self.inputbox.textstart(self.profilename)
                            self.inputui.changeinstruction("Profile Name:")
                            self.mainui.add(self.inputuipop)

                    elif self.menustate == "presetselect" or self.menustate == "customselect":
                        if mouse_up:
                            for index, name in enumerate(self.mapnamegroup): # user click on map name, change map
                                if name.rect.collidepoint(self.mousepos):
                                    self.currentmapselect = index
                                    if self.menustate == "presetselect": # make new map image
                                        self.makemap(self.mapfoldername, self.maplist)
                                    else:
                                        self.makemap(self.mapcustomfoldername, self.mapcustomlist)
                                    break

                        if self.mapbackbutton.event or esc_press:
                            self.mapbackbutton.event = False
                            self.currentmaprow = 0
                            self.currentmapselect = 0

                            self.mainui.remove(self.maplistbox, self.mapshow, self.mapscroll, self.mapdescription,
                                               self.teamcoa, self.maptitle)

                            for group in (self.mapshow, self.mapnamegroup, self.teamcoa): # remove no longer related sprites in group
                                for stuff in group:
                                    stuff.kill()
                                    del stuff

                            self.backtomainmenu()

                        elif self.selectbutton.event: # select this map, go to prepare setup
                            self.currentsourcerow = 0
                            self.menustate = "battlemapset"
                            self.selectbutton.event = False

                            self.mainui.remove(*self.mapselectbutton, self.maplistbox, self.mapscroll, self.mapdescription)
                            self.menubutton.remove(*self.mapselectbutton)

                            for stuff in self.mapnamegroup:  # remove map name item
                                stuff.kill()
                                del stuff

                            for team in self.teamcoa:
                                if self.teamselected == team.team:
                                    team.selected = True
                                    team.changeselect()

                            openfolder = self.mapfoldername
                            if self.lastselect == "customselect":
                                openfolder = self.mapcustomfoldername
                            try:
                                self.sourcelist = self.readmapdata(openfolder, 'source.csv')
                                self.sourcenamelist = [value[0] for value in list(self.sourcelist.values())[1:]]
                                self.sourcescaletext = [value[1] for value in list(self.sourcelist.values())[1:]]
                                self.sourcescale = [(float(value[2]), float(value[3]), float(value[4]), float(value[5])) for value in
                                                    list(self.sourcelist.values())[1:]]
                                self.sourcetext = [value[-1] for value in list(self.sourcelist.values())[1:]]
                            except: # no source.csv make empty list
                                self.sourcenamelist = ['']
                                self.sourcescaletext = ['']
                                self.sourcescale = ['']
                                self.sourcetext = ['']


                            self.setuplist(gameprepare.Sourcename, self.currentsourcerow, self.sourcenamelist, self.sourcenamegroup, self.sourcelistbox)

                            self.sourcescroll = gameui.Uiscroller(self.sourcelistbox.rect.topright, self.sourcelistbox.image.get_height(),
                                                                  self.sourcelistbox.maxshowlist, layer=14)

                            for index, team in enumerate(self.teamcoa):
                                if index == 0:
                                    self.armystat.add(gameprepare.Armystat((team.rect.bottomleft[0], SCREENRECT.height/1.5))) # left army stat
                                else:
                                    self.armystat.add(gameprepare.Armystat((team.rect.bottomright[0], SCREENRECT.height / 1.5)))  # right army stat

                            self.changesource([self.sourcescaletext[self.mapsource] , self.sourcetext[self.mapsource]], self.sourcescale[self.mapsource])

                            self.menubutton.add(*self.battlesetupbutton)
                            self.mainui.add(*self.battlesetupbutton, self.mapoptionbox, self.tickboxenactment, self.sourcelistbox, self.sourcescroll, self.armystat)

                    elif self.menustate == "battlemapset":
                        #v User input
                        if mouse_up:
                            for team in self.teamcoa: # User select any team by clicking on coat of arm
                                if team.rect.collidepoint(self.mousepos):
                                    self.teamselected = team.team
                                    team.selected = True
                                    team.changeselect()

                                    # Reset team selected on team user not currently selected
                                    for team in self.teamcoa:
                                        if self.teamselected != team.team and team.selected:
                                            team.selected = False
                                            team.changeselect()

                                    break

                            for index, name in enumerate(self.sourcenamegroup):  # user select source
                                if name.rect.collidepoint(self.mousepos):  # click on source name
                                    self.mapsource = index
                                    self.changesource([self.sourcescaletext[self.mapsource] , self.sourcetext[self.mapsource]], self.sourcescale[self.mapsource])
                                    break

                            for box in self.tickbox:
                                if box.rect.collidepoint(self.mousepos):
                                    if box.tick == False:
                                        box.changetick(True)
                                    else:
                                        box.changetick(False)
                                    if box.option == "enactment":
                                        self.enactment = box.tick

                        #^ End user input

                        if self.mapbackbutton.event or esc_press:
                            self.menustate = self.lastselect
                            self.mapbackbutton.event = False
                            self.mainui.remove(*self.menubutton, self.maplistbox, self.mapoptionbox, self.tickboxenactment,
                                               self.sourcelistbox, self.sourcescroll, self.sourcedescription)
                            self.menubutton.remove(*self.menubutton)

                            #v Reset selected team
                            for team in self.teamcoa:
                                team.selected = False
                                team.changeselect()
                            self.teamselected = 1
                            #^ End reset selected team

                            self.mapsource = 0
                            for thismap in self.mapshow:
                                thismap.changemode(0) # revert map preview back to without army dot

                            for group in (self.sourcenamegroup, self.armystat):
                                for stuff in group:  # remove map name item
                                    stuff.kill()
                                    del stuff

                            if self.menustate == "presetselect": # regenerate map name list
                                self.setuplist(gameprepare.Mapname, self.currentmaprow, self.maplist, self.mapnamegroup, self.maplistbox)
                            else:
                                self.setuplist(gameprepare.Mapname, self.currentmaprow, self.mapcustomlist, self.mapnamegroup, self.maplistbox)

                            self.menubutton.add(*self.mapselectbutton)
                            self.mainui.add(*self.mapselectbutton, self.maplistbox, self.mapscroll, self.mapdescription)

                        elif self.startbutton.event: # start game button
                            self.battlegame.preparenew(self.ruleset, self.rulesetfolder, self.teamselected, self.enactment,
                                                       self.mapfoldername[self.currentmapselect], self.mapsource, self.sourcescale[self.mapsource])
                            self.battlegame.rungame()
                            gc.collect() # collect no longer used object in previous battle from memory
                            self.startbutton.event = False

                    elif self.menustate == "uniteditor":
                        if self.editorbackbutton.event or esc_press:
                            self.editorbackbutton.event = False

                            self.backtomainmenu()

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

                        if self.backbutton.event or esc_press: # back to main menu
                            self.backbutton.event = False

                            self.mainui.remove(*self.optioniconlist, self.optionmenuslider, self.valuebox)

                            self.backtomainmenu()

                        if mouse_up or mouse_down:
                            self.mainui.remove(self.resolutionbar)

                            if self.resolutionscroll.rect.collidepoint(self.mousepos): # click on resolution bar
                                if self.resolutionbar in self.mainui: # remove the bar list if click again
                                    self.mainui.remove(self.resolutionbar)
                                    self.menubutton.remove(self.resolutionbar)
                                else: # add bar list
                                    self.mainui.add(self.resolutionbar)
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
                                    if button in self.mainui and button.rect.collidepoint(self.mousepos): # click button
                                        if button.event in range(0, 11): # section button
                                            self.lorebook.changesection(button.event, self.lorenamelist, self.subsectionname, self.lorescroll, self.pagebutton, self.mainui) # change to section of that button

                                        elif button.event == 19:  # Close button
                                            self.mainui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll, self.lorenamelist) # remove enclycopedia related sprites
                                            for name in self.subsectionname: # remove subsection name
                                                name.kill()
                                                del name
                                            self.menustate = "mainmenu" # change menu back to default 0

                                        elif button.event == 20:  # Previous page button
                                            self.lorebook.changepage(self.lorebook.page - 1, self.pagebutton, self.mainui) # go back 1 page

                                        elif button.event == 21:  # Next page button
                                            self.lorebook.changepage(self.lorebook.page + 1, self.pagebutton, self.mainui) # go forward 1 page

                                        break # found clicked button, break loop

                                for name in self.subsectionname: # too lazy to include break for button found to avoid subsection loop since not much optimisation is needed here
                                    if name.rect.collidepoint(self.mousepos): # click on subsection name
                                        self.lorebook.changesubsection(name.subsection, self.pagebutton, self.mainui) # change subsection
                                        break # found clicked subsection, break loop

                            if self.lorescroll.rect.collidepoint(self.mousepos): # click on subsection list scroller
                                self.lorebook.currentsubsectionrow = self.lorescroll.update(self.mousepos) # update the scroller and get new current subsection
                                self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname) # update subsection name list

                        elif esc_press:
                            self.mainui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll,
                                               self.lorenamelist)  # remove enclycopedia related sprites
                            for name in self.subsectionname:  # remove subsection name
                                name.kill()
                                del name
                            self.menustate = "mainmenu"  # change menu back to default 0

                self.mainui.draw(self.screen)
                pygame.display.update()
                self.clock.tick(60)

            if pygame.mixer:
                pygame.mixer.music.fadeout(1000)

            pygame.time.wait(1000)
            pygame.quit()
            sys.exit()

    if __name__ == '__main__':
        runmenu = Mainmenu()
        runmenu.run()

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
