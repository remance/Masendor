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
        gamefaction, gameunitstat, gameui, gameprepare, gamemenu, gamebattalion, gamesquad,rangeattack, gamepopup, gameunitedit

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
            self.widthadjust = SCREENRECT.width / 1366
            self.heightadjust = SCREENRECT.height / 768
            #^ End set display

            # v Decorate the game window
            # icon = load_image('sword.jpg')
            # icon = pygame.transform.scale(icon, (32, 32))
            # pygame.display.set_icon(icon)
            # ^ End decorate

            # v Initialise Game Groups
            # main menu object group
            self.mainui = pygame.sprite.LayeredUpdates() # sprite drawer group
            self.menubutton = pygame.sprite.Group()  # group of menu buttons that are currently get shown and update
            self.menuicon = pygame.sprite.Group() # mostly for option icon like volumne or scren resolution

            self.inputui = pygame.sprite.Group() # user text input ui box popup
            self.inputbox = pygame.sprite.Group() # user text input box

            self.profilebox = pygame.sprite.Group() # profile name box at top right of screen at main menu screen

            self.menuslider = pygame.sprite.Group()
            self.maplistbox = pygame.sprite.Group() # ui box for map list
            self.mapscroll = pygame.sprite.Group() # scroller bar for map list
            self.mapnamegroup = pygame.sprite.Group() # map name list group
            self.mapshow = pygame.sprite.Group() # preview image of selected map
            self.teamcoa = pygame.sprite.Group() # team coat of arm that also act as team selection icon
            self.maptitle = pygame.sprite.Group() # map title box
            self.mapdescription = pygame.sprite.Group() # map description box in map select screen
            self.sourcedescription = pygame.sprite.Group() # map source description box in preset battle preparation screen
            self.armystat = pygame.sprite.Group() # ui box that show army stat in preset battle preparation screen

            self.sourcescroll = pygame.sprite.Group() # scroller bar for source list
            self.sourcelistbox = pygame.sprite.Group() # source list ui box
            self.sourcenamegroup = pygame.sprite.Group() # source name list group

            self.mapoptionbox = pygame.sprite.Group() # ui box for battle option during preparation screen
            self.tickbox = pygame.sprite.Group() # option tick box

            self.lorebuttonui = pygame.sprite.Group()  # buttons for enclycopedia group
            self.lorebook = pygame.sprite.Group()  # encyclopedia object
            self.valuebox = pygame.sprite.Group()  # value number and box in esc menu option
            self.lorenamelist = pygame.sprite.Group()  # box sprite for showing subsection name list in encyclopedia
            self.lorescroll = pygame.sprite.Group()  # scroller for subsection name list in encyclopedia
            self.subsectionname = pygame.sprite.Group()  # subsection name objects group in encyclopedia blit on lorenamelist

            self.battlepreview = pygame.sprite.Group() # preview of unit battle in army editor
            self.trooplistbox = pygame.sprite.Group() # ui box for troop name list
            self.troopnamegroup = pygame.sprite.Group() # troop name list group
            self.troopscroll = pygame.sprite.Group()
            self.filterbox = pygame.sprite.Group()
            self.mapoptionlistbox = pygame.sprite.Group()
            self.mapoptionnamegroup = pygame.sprite.Group()
            self.mapoptionscroll = pygame.sprite.Group()
            self.terrainchangebutton = pygame.sprite.Group() # button to change preview map base terrain
            self.featurechangebutton = pygame.sprite.Group() # button to change preview map terrain feature
            self.weatherchangebutton = pygame.sprite.Group() # button to change preview map weather


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
            self.slidermenu = pygame.sprite.Group() # volume slider in esc option menu

            self.armyselector = pygame.sprite.Group()  # army selector ui
            self.armyicon = pygame.sprite.Group()  # army icon object group in army selector ui
            self.selectscroll = pygame.sprite.Group()  # scoller object in army selector ui

            self.timeui = pygame.sprite.Group()  # time bar ui
            self.timenumber = pygame.sprite.Group()  # number text of in-game time
            self.speednumber = pygame.sprite.Group()  # number text of current game speed

            self.scaleui = pygame.sprite.Group() # battle scale bar

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

            gameprepare.Listbox.containers = self.maplistbox, self.trooplistbox, self.mapoptionlistbox
            gameprepare.Namelist.containers = self.mapnamegroup, self.troopnamegroup, self.mainui
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
            gameui.Uiscroller.containers = self.mapscroll, self.sourcescroll, self.lorescroll, self.logscroll, \
                                           self.selectscroll, self.troopscroll, self.mapoptionscroll

            gameunitedit.Previewbox.main_dir = main_dir
            img = load_image('effect.png', 'map')  # map special effect image
            gameunitedit.Previewbox.effectimage = img
            gameunitedit.Previewbox.containers = self.battlepreview
            gameunitedit.Filterbox.containers = self.filterbox
            gameunitedit.Previewchangebutton.containers = self.terrainchangebutton, self.weatherchangebutton, self.featurechangebutton

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
            self.maplistbox = gameprepare.Listbox((SCREENRECT.width / 25, SCREENRECT.height / 20), imgs[0])
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

            self.currenttrooprow = 0

            #^ End battle map menu button

            #v Create unit editor button and ui

            self.armyeditbutton = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 4)),
                                          text="Army Editor")
            self.troopcreatetbutton = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 2.5)),
                                          text="Troop Creator")
            self.editorbackbutton = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height - imagelist[0].get_height()),
                                         text="Back")
            self.editorbutton = (self.armyeditbutton, self.troopcreatetbutton, self.editorbackbutton)
            # ^ End unit editor

            #v Army editor
            boximg = load_image('army_presetbox.png', 'ui').convert()
            self.armylistbox = gameprepare.Listbox((0, SCREENRECT.height/3), boximg)
            self.trooplistbox = gameprepare.Listbox((SCREENRECT.width / 1.19, 0), imgs[0])
            self.troopscroll = gameui.Uiscroller(self.trooplistbox.rect.topright, self.trooplistbox.image.get_height(),
                                                 self.trooplistbox.maxshowlist, layer=14)
            self.armybackbutton = gameprepare.Menubutton(images=imagelist,
                                                        pos=(imagelist[0].get_width()/2, bottomheight),
                                                        text="Back")
            self.armysavebutton = gameprepare.Menubutton(images=imagelist,
                                                         pos=((SCREENRECT.width - (SCREENRECT.width - (imagelist[0].get_width()*1.7))), bottomheight),
                                                         text="Save")
            self.battlepreview = gameunitedit.Previewbox((SCREENRECT.width/2, SCREENRECT.height/2))

            self.mapoptionlistbox = gameprepare.Listbox((0, 0), boximg)
            self.mapoptionlistbox.maxshowlist = 12 # box is smaller than usual
            boximg = load_image('mapchange.png', 'ui').convert()
            self.terrainchangebutton = gameunitedit.Previewchangebutton((SCREENRECT.width/3, SCREENRECT.height), boximg, "Temperate") # start with temperate terrain
            self.featurechangebutton = gameunitedit.Previewchangebutton((SCREENRECT.width/2, SCREENRECT.height), boximg, "Plain") # start with plain feature
            self.weatherchangebutton = gameunitedit.Previewchangebutton((SCREENRECT.width/1.5, SCREENRECT.height), boximg, "Light Sunny") # start with light sunny



            boximg = load_image('filterbox.png', 'ui').convert()
            self.filterbox = gameunitedit.Filterbox((SCREENRECT.width / 2.5, 0), boximg)

            self.armyeditorbutton = (self.armybackbutton, self.armysavebutton)

            #^ End army editor

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
            self.textinputpopup = None # popup for texting text input state
            self.choosingfaction = True # swap list between faction and unit, always start with choose faction first as true

            self.battlegame = maingame.Battle(self, self.winstyle)

        def backtomainmenu(self):
            self.menustate = "mainmenu"

            self.mainui.remove(*self.menubutton)

            self.menubutton.remove(*self.menubutton)
            self.menubutton.add(*self.mainmenubutton)

            self.mainui.add(*self.menubutton, self.profilebox)

        def setuplist(self, itemclass, currentrow, showlist, itemgroup, box, screenscale=False):
            """generate list of subsection of the left side of encyclopedia"""
            widthadjust = 1
            heightadjust = 1
            if screenscale:
                widthadjust = self.widthadjust
                heightadjust = self.heightadjust
            row = 5 * heightadjust
            column = 5 * widthadjust
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
                    row += (30*heightadjust)  # next row
                    if len(itemgroup) > box.maxshowlist: break  # will not generate more than space allowed

        def readmapdata(self, maplist, file):
            if self.menustate == "presetselect" or self.lastselect == "presetselect":
                data = csv_read(file,['data', 'ruleset', self.rulesetfolder.strip("/"), 'map', maplist[self.currentmapselect]])
            else:
                data = csv_read(file, ['data', 'ruleset', self.rulesetfolder.strip("/"), 'map/custom',  maplist[self.currentmapselect]])
            return data

        def maketeamcoa(self, data, oneteam=False, team1setpos=(SCREENRECT.width/2 - (300 * widthadjust),SCREENRECT.height/3)):
            for team in self.teamcoa:
                team.kill()
                del team

            # position = self.mapshow[0].get_rect()
            self.teamcoa.add(gameprepare.Teamcoa(team1setpos, self.coa[data[0]],
                                                 1, self.allfaction.factionlist[data[0]][0])) # team 1

            if oneteam == False:
                self.teamcoa.add(gameprepare.Teamcoa((SCREENRECT.width/2 + (300 * widthadjust),SCREENRECT.height/3), self.coa[data[1]],
                                                 2, self.allfaction.factionlist[data[1]][0])) # team 2
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

            self.maketeamcoa([list(data.values())[1][2], list(data.values())[1][3]])

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

        def listscroll(self, mouse_scrollup, mouse_scrolldown, scroll, listbox, currentrow, namelist, namegroup):
            if mouse_scrollup:
                if listbox.rect.collidepoint(self.mousepos):  # Scrolling up at map name list
                    currentrow -= 1
                    if currentrow < 0:
                        currentrow = 0
                    else:
                        self.setuplist(gameprepare.Namelist, currentrow, namelist, namegroup, listbox)
                        scroll.changeimage(newrow=currentrow, logsize=len(namelist))

            elif mouse_scrolldown:
                if listbox.rect.collidepoint(self.mousepos):  # Scrolling down at map name list
                    currentrow += 1
                    if currentrow + listbox.maxshowlist - 1 < len(namelist):
                        self.setuplist(gameprepare.Namelist, currentrow, namelist, namegroup, listbox)
                        scroll.changeimage(newrow=currentrow, logsize=len(namelist))
                    else:
                        currentrow -= 1
            return currentrow

        def run(self):
            while True:
                #v Get user input
                mouse_up = False
                mouse_down = False
                mouse_scrolldown = False
                mouse_scrollup = False
                esc_press = False
                for event in pygame.event.get():
                    if self.textinputpopup is not None: # event update to input box
                        self.inputbox.userinput(event)

                    if pygame.mouse.get_pressed()[0]:  # Hold left click
                        mouse_down = True

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:  # left click
                            mouse_up = True
                        elif event.button == 4:  # Mouse scroll down
                            mouse_scrollup = True

                        elif event.button == 5:  # Mouse scroll up
                            mouse_scrolldown = True

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

                            self.setuplist(gameprepare.Namelist, self.currentmaprow, self.maplist, self.mapnamegroup, self.maplistbox)
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

                            self.setuplist(gameprepare.Namelist, self.currentmaprow, self.mapcustomlist, self.mapnamegroup, self.maplistbox)
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
                        if mouse_up or mouse_down:
                            if mouse_up:
                                for index, name in enumerate(self.mapnamegroup): # user click on map name, change map
                                    if name.rect.collidepoint(self.mousepos):
                                        self.currentmapselect = index
                                        if self.menustate == "presetselect": # make new map image
                                            self.makemap(self.mapfoldername, self.maplist)
                                        else:
                                            self.makemap(self.mapcustomfoldername, self.mapcustomlist)
                                        break

                            if self.mapscroll.rect.collidepoint(self.mousepos):  # click on subsection list scroller
                                self.currentmaprow = self.mapscroll.update(
                                    self.mousepos)  # update the scroller and get new current subsection
                                self.setuplist(gameprepare.Namelist, self.currentmaprow, self.maplist, self.mapnamegroup, self.maplistbox)

                        self.currentmaprow = self.listscroll(mouse_scrollup, mouse_scrolldown, self.mapscroll, self.maplistbox,
                                                                self.currentmaprow, self.maplist, self.mapnamegroup)

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
                        if mouse_up or mouse_down:
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

                            if self.sourcescroll.rect.collidepoint(self.mousepos):  # click on subsection list scroller
                                self.currentsourcerow = self.sourcescroll.update(
                                    self.mousepos)  # update the scroller and get new current subsection
                                self.setuplist(gameprepare.Namelist, self.currentsourcerow, self.sourcelist, self.sourcenamegroup, self.sourcelistbox)

                        self.currentsourcerow = self.listscroll(mouse_scrollup, mouse_scrolldown, self.sourcescroll, self.sourcelistbox,
                                                                self.currentsourcerow, self.sourcelist, self.sourcenamegroup)

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
                                self.setuplist(gameprepare.Namelist, self.currentmaprow, self.maplist, self.mapnamegroup, self.maplistbox)
                            else:
                                self.setuplist(gameprepare.Namelist, self.currentmaprow, self.mapcustomlist, self.mapnamegroup, self.maplistbox)

                            self.menubutton.add(*self.mapselectbutton)
                            self.mainui.add(*self.mapselectbutton, self.maplistbox, self.mapscroll, self.mapdescription)

                        elif self.startbutton.event: # start game button
                            self.startbutton.event = False
                            self.battlegame.preparenew(self.ruleset, self.rulesetfolder, self.teamselected, self.enactment,
                                                       self.mapfoldername[self.currentmapselect], self.mapsource, self.sourcescale[self.mapsource])
                            self.battlegame.rungame()
                            gc.collect() # collect no longer used object in previous battle from memory


                    elif self.menustate == "uniteditor":
                        if self.editorbackbutton.event or esc_press:
                            self.editorbackbutton.event = False
                            self.currenttrooprow = 0

                            self.backtomainmenu()

                        elif self.armyeditbutton.event:
                            self.armyeditbutton.event = False
                            self.menustate = "armyeditor"

                            self.mainui.remove(*self.menubutton)

                            self.menubutton.remove(*self.menubutton)
                            self.menubutton.add(*self.armyeditorbutton)

                            self.trooplist = ['None'] + [item[0] for item in self.gameunitstat.unitlist.values()][1:] #generate troop name list
                            self.setuplist(gameprepare.Namelist, self.currenttrooprow, self.trooplist,
                                           self.troopnamegroup, self.trooplistbox)
                            self.currentlistshow = "troop"
                            self.preparestate = True
                            self.baseterrain = 0
                            self.featureterrain = 0
                            self.weathertype = 0
                            self.weatherstrength = 0

                            self.gameui[1].rect = self.gameui[1].image.get_rect(center=(self.gameui[1].X,
                                                                                        self.gameui[1].image.get_height()/2)) # leader ui

                            self.gameui[2].rect = self.gameui[1].image.get_rect(topright=(self.trooplistbox.rect.bottomright[0],
                                                                                        self.trooplistbox.rect.bottomright[1])) # troop info card ui
                            self.buttonui[0].rect = self.buttonui[0].image.get_rect(topright=(self.gameui[2].rect.topleft[0], # description button
                                                                                          self.gameui[2].rect.topleft[1]+120))
                            self.buttonui[1].rect = self.buttonui[1].image.get_rect(topright=(self.gameui[2].rect.topleft[0], # stat button
                                                                                          self.gameui[2].rect.topleft[1]))
                            self.buttonui[2].rect = self.buttonui[2].image.get_rect(topright=(self.gameui[2].rect.topleft[0], # skill button
                                                                                          self.gameui[2].rect.topleft[1] + 40))
                            self.buttonui[3].rect = self.buttonui[3].image.get_rect(topright=(self.gameui[2].rect.topleft[0], # equipment button
                                                                                          self.gameui[2].rect.topleft[1] + 80))

                            self.maketeamcoa([0], oneteam=True,team1setpos=(self.trooplistbox.rect.midleft[0] - int((200 * self.widthadjust)/2),
                                                                            self.trooplistbox.rect.midleft[1])) # default faction select as all faction

                            self.troopscroll.changeimage(newrow=self.currenttrooprow, logsize=len(self.trooplist)) # change troop scroll image
                            self.mainui.add(*self.menubutton, self.battlepreview, self.trooplistbox, self.troopscroll, self.armylistbox,
                                            self.timeui, self.timenumber, self.gameui[1], self.gameui[2], self.filterbox, *self.buttonui[0:4],
                                            self.terrainchangebutton, self.featurechangebutton, self.weatherchangebutton)

                    elif self.menustate == "armyeditor": # custom battalion preset creator and test
                        if self.armybackbutton.event or esc_press:
                            self.armybackbutton.event = False
                            self.menustate = "uniteditor"

                            self.gameui[1].rect = self.gameui[1].image.get_rect(center=(self.gameui[1].X, self.gameui[1].Y)) # change leader ui position back
                            self.gameui[2].rect = self.gameui[1].image.get_rect(center=(self.gameui[2].X, self.gameui[2].Y)) # change unit card position back
                            self.buttonui[0].rect = self.gameui[2].image.get_rect(center=(self.gameui[2].X - 152, self.gameui[2].Y + 10))
                            self.buttonui[1].rect = self.gameui[2].image.get_rect(center=(self.gameui[2].X - 152, self.gameui[2].Y - 70))
                            self.buttonui[2].rect = self.gameui[2].image.get_rect(center=(self.gameui[2].X - 152, self.gameui[2].Y - 30))
                            self.buttonui[3].rect = self.gameui[2].image.get_rect(center=(self.gameui[2].X - 152, self.gameui[2].Y + 50))

                            self.mainui.remove(*self.menubutton, self.battlepreview, self.trooplistbox, self.troopscroll, self.teamcoa, self.armylistbox,
                                               self.timeui, self.timenumber, self.gameui[1], self.gameui[2], self.filterbox, *self.buttonui[0:4],
                                               self.terrainchangebutton, self.featurechangebutton, self.weatherchangebutton)

                            for name in self.troopnamegroup:  # remove troop name list
                                name.kill()
                                del name

                            self.trooplist = ['None'] + [item[0] for item in self.gameunitstat.unitlist.values()][1:] # reset troop filter back to all faction

                            self.menubutton.remove(*self.menubutton)
                            self.menubutton.add(*self.editorbutton)

                            self.mainui.add(*self.editorbutton)


                        if mouse_up or mouse_down:
                            if mouse_up:
                                if self.terrainchangebutton.rect.collidepoint(self.mousepos):
                                    self.mapoptionlistbox.rect = self.mapoptionlistbox.image.get_rect(midbottom=(self.terrainchangebutton.rect.midtop))
                                    self.mainui.add(self.mapoptionlistbox)
                                    self.setuplist(gameprepare.Namelist, 0, self.battlemapbase.terrainlist, self.mapoptionnamegroup,
                                                   self.mapoptionlistbox)
                                    self.mainui.add(*self.mapoptionnamegroup)
                                    # self.mapoptionscroll = gameui.Uiscroller((0,0), self.maplistbox.image.get_height(),
                                    #                                    self.maplistbox.maxshowlist, layer=14)

                                    self.mapoptionlistbox.type = "terrain"
                                elif self.featurechangebutton.rect.collidepoint(self.mousepos):
                                    self.mapoptionlistbox.rect = self.mapoptionlistbox.image.get_rect(midbottom=(self.featurechangebutton.rect.midtop))
                                    self.mainui.add(self.mapoptionlistbox)
                                    self.setuplist(gameprepare.Namelist, 0, self.battlemapfeature.featurelist, self.mapoptionnamegroup,
                                                   self.mapoptionlistbox)
                                    self.mainui.add(*self.mapoptionnamegroup)
                                    self.mapoptionlistbox.type = "feature"
                                elif self.weatherchangebutton.rect.collidepoint(self.mousepos):
                                    self.mapoptionlistbox.rect = self.mapoptionlistbox.image.get_rect(midbottom=(self.weatherchangebutton.rect.midtop))
                                    self.mainui.add(self.mapoptionlistbox)
                                    self.setuplist(gameprepare.Namelist, 0, self.weatherlist, self.mapoptionnamegroup,
                                                   self.mapoptionlistbox)
                                    self.mainui.add(*self.mapoptionnamegroup)
                                    self.mapoptionlistbox.type = "weather"


                                elif self.trooplistbox.rect.collidepoint(self.mousepos):
                                    for index, name in enumerate(self.troopnamegroup):
                                        if name.rect.collidepoint(self.mousepos):
                                            if self.currentlistshow == "faction":
                                                self.currenttrooprow = 0
                                                self.trooplist = ['None'] + [item[1][0] for item in self.gameunitstat.unitlist.items()
                                                                             if (index == 0 and item[1][0] != "Name") or
                                                                             item[0] in self.allfaction.factionlist[index][1]]
                                                self.setuplist(gameprepare.Namelist, self.currenttrooprow, self.trooplist, self.troopnamegroup,
                                                               self.trooplistbox)
                                                self.troopscroll.changeimage(newrow=self.currenttrooprow,
                                                                             logsize=len(self.trooplist))  # change troop scroll image

                                                self.maketeamcoa([index], oneteam=True,
                                                                 team1setpos=(self.trooplistbox.rect.midleft[0] - int((200 * self.widthadjust) / 2),
                                                                              self.trooplistbox.rect.midleft[1]))  # change team coa

                                                self.currentlistshow = "troop"
                                            break

                                elif self.mapoptionlistbox in self.mainui:
                                    if self.mapoptionlistbox.rect.collidepoint(self.mousepos):
                                        for index, name in enumerate(self.mapoptionnamegroup):
                                            if name.rect.collidepoint(self.mousepos):
                                                if self.mapoptionlistbox.type == "terrain":
                                                    self.terrainchangebutton.changetext(self.battlemapbase.terrainlist[index])
                                                elif self.mapoptionlistbox.type == "feature":
                                                    self.featurechangebutton.changetext(self.battlemapfeature.featurelist[index])
                                                elif self.mapoptionlistbox.type == "weather":
                                                    self.weatherchangebutton.changetext()

                                                for name in self.mapoptionnamegroup:  # remove troop name list
                                                    name.kill()
                                                    del name

                                                self.mainui.remove(self.mapoptionlistbox)
                                                break
                                    else:
                                        self.mainui.remove(self.mapoptionlistbox, *self.mapoptionnamegroup)

                                for team in self.teamcoa:
                                    if team.rect.collidepoint(self.mousepos):
                                        if self.currentlistshow == "troop":
                                            self.currenttrooprow = 0
                                            self.setuplist(gameprepare.Namelist, self.currenttrooprow, self.factionlist, self.troopnamegroup,
                                                           self.trooplistbox)
                                            self.troopscroll.changeimage(newrow=self.currenttrooprow,
                                                                         logsize=len(self.factionlist))  # change troop scroll image
                                            self.currentlistshow = "faction"


                            if self.troopscroll.rect.collidepoint(self.mousepos):  # click on subsection list scroller
                                self.currenttrooprow = self.troopscroll.update(
                                    self.mousepos)  # update the scroller and get new current subsection
                                if self.currentlistshow == "troop":
                                    self.setuplist(gameprepare.Namelist, self.currenttrooprow, self.trooplist, self.troopnamegroup, self.trooplistbox)
                                elif self.currentlistshow == "faction":
                                    self.setuplist(gameprepare.Namelist, self.currenttrooprow, self.factionlist, self.troopnamegroup,
                                                   self.trooplistbox)

                        if self.currentlistshow == "troop":
                            self.currenttrooprow = self.listscroll(mouse_scrollup, mouse_scrolldown, self.troopscroll, self.trooplistbox,
                                                                self.currenttrooprow, self.trooplist, self.troopnamegroup)
                        elif self.currentlistshow == "faction":
                            self.currenttrooprow = self.listscroll(mouse_scrollup, mouse_scrolldown, self.troopscroll, self.trooplistbox,
                                                                   self.currenttrooprow, self.factionlist, self.troopnamegroup)

                    elif self.menustate == "option":
                        for bar in self.resolutionbar: # loop to find which resolution bar is selected, this happen outside of clicking check below
                            if bar.event:
                                bar.event = False

                                self.resolutionscroll.changestate(bar.text)  # change button value based on new selected value
                                resolutionchange = bar.text.split()
                                self.newScreenWidth = resolutionchange[0]
                                self.newScreenHeight = resolutionchange[2]

                                editconfig('DEFAULT', 'ScreenWidth', self.newScreenWidth, 'configuration.ini', config)
                                editconfig('DEFAULT', 'ScreenHeight', self.newScreenHeight, 'configuration.ini', config)
                                self.screen = pygame.display.set_mode(SCREENRECT.size, self.winstyle | pygame.RESIZABLE, self.bestdepth)

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

                                for name in self.subsectionname:
                                    if name.rect.collidepoint(self.mousepos): # click on subsection name
                                        self.lorebook.changesubsection(name.subsection, self.pagebutton, self.mainui) # change subsection
                                        break # found clicked subsection, break loop

                            if self.lorescroll.rect.collidepoint(self.mousepos): # click on subsection list scroller
                                self.lorebook.currentsubsectionrow = self.lorescroll.update(self.mousepos) # update the scroller and get new current subsection
                                self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname) # update subsection name list

                        elif mouse_scrollup:
                            if self.lorenamelist.rect.collidepoint(self.mousepos): #  Scrolling at lore book subsection list
                                self.lorebook.currentsubsectionrow -= 1
                                if self.lorebook.currentsubsectionrow < 0:
                                    self.lorebook.currentsubsectionrow = 0
                                else:
                                    self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname)
                                    self.lorescroll.changeimage(newrow=self.lorebook.currentsubsectionrow)

                        elif mouse_scrolldown:
                            if self.lorenamelist.rect.collidepoint(self.mousepos):  # Scrolling at lore book subsection list
                                self.lorebook.currentsubsectionrow += 1
                                if self.lorebook.currentsubsectionrow + self.lorebook.maxsubsectionshow - 1 < self.lorebook.logsize:
                                    self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname)
                                    self.lorescroll.changeimage(newrow=self.lorebook.currentsubsectionrow)
                                else:
                                    self.lorebook.currentsubsectionrow -= 1

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
