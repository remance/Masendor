try: # for printing error log when error exception happen
    import configparser
    import glob
    import os.path
    import sys
    import traceback
    import gc
    import numpy as np
    import csv

    # for getting screen info
    import screeninfo

    # import basic pygame modules
    import pygame
    import pygame.freetype
    from pygame.locals import *

    from gamescript import maingame, gameleader, gamemap, gamelongscript, gamelorebook, gameweather, gamedrama, \
        gamefaction, gameunitstat, gameui, gameprepare, gamemenu, gameunit, gamesubunit,rangeattack, gamepopup, gameunitedit

    screen = screeninfo.get_monitors()[0]

    screenWidth = int(screen.width)
    screenHeight = int(screen.height)

    config = configparser.ConfigParser()
    try:
        config.read_file(open('configuration.ini')) # read config file
    except: # Create config file if not found with the default
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'screenwidth': screenWidth,'screenheight': screenHeight, 'fullscreen': '0',
                             'playername': 'Noname', 'soundvolume': '100.0', 'musicvolume': '0.0',
                             'voicevolume': '0.0', 'maxfps': '60', 'ruleset': '1'}
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
        teamcolour = ((255, 255, 255), (144, 167, 255), (255, 114, 114)) # team colour
        leaderposname = ("Commander", "Sub-General", "Sub-General", "Sub-Commander", "General", "Sub-General", "Sub-General",
                              "Advisor")  # Name of leader position in parentunit, the first 4 is for commander parentunit
        traitskillblit = gamelongscript.traitskillblit
        effecticonblit = gamelongscript.effecticonblit
        countdownskillicon = gamelongscript.countdownskillicon
        def __init__(self):
            pygame.init() # Initialize pygame

            self.rulesetlist = maingame.csv_read("ruleset_list.csv", ["data", "ruleset"]) # get ruleset list
            self.ruleset = 1 # for now default historical ruleset only
            self.rulesetfolder = "/" + str(self.rulesetlist[self.ruleset][1])

            if not os.path.exists("profile"):  # make profile folder if not existed
                os.makedirs("profile")
                os.makedirs("profile/armypreset")
            if not os.path.exists("profile/armypreset/"+str(self.ruleset)): # create armypreset folder for ruleset
                os.makedirs("profile/armypreset/" + str(self.ruleset))
            try:
                customarmypresetlist = csv_read("custom_unitpreset.csv",["profile", "armypreset", str(self.ruleset)])
                del customarmypresetlist["presetname"]
                self.customarmypresetlist =  {"New Preset":0, **customarmypresetlist}
            except:
                with open("profile/armypreset/"+str(self.ruleset)+"/custom_unitpreset.csv", "w") as csvfile:
                     filewriter = csv.writer(csvfile, delimiter=',',
                                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
                     filewriter.writerow(["presetname", "armyline2", "armyline3", "armyline4", "armyline15", "armyline6", "armyline7", "armyline8",
                                          "leader", "leaderposition", "faction"]) # create header
                     csvfile.close()

                self.customarmypresetlist = {}

            # if not os.path.exists('\customunit'): # make custom subunit folder if not existed

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

            self.menuslider = pygame.sprite.Group()
            self.maplistbox = pygame.sprite.Group() # ui box for map list
            self.mapnamegroup = pygame.sprite.Group() # map name list group
            self.mapshow = pygame.sprite.Group() # preview image of selected map
            self.teamcoa = pygame.sprite.Group() # team coat of arm that also act as team selection icon
            self.maptitle = pygame.sprite.Group() # map title box
            self.mapdescription = pygame.sprite.Group() # map description box in map select screen
            self.sourcedescription = pygame.sprite.Group() # map source description box in preset battle preparation screen
            self.armystat = pygame.sprite.Group() # ui box that show army stat in preset battle preparation screen

            self.sourcenamegroup = pygame.sprite.Group() # source name list group

            self.tickbox = pygame.sprite.Group() # option tick box

            self.lorebuttonui = pygame.sprite.Group()  # buttons for enclycopedia group
            self.valuebox = pygame.sprite.Group()  # value number and box in esc menu option
            self.lorenamelist = pygame.sprite.Group()  # box sprite for showing subsection name list in encyclopedia
            self.subsectionname = pygame.sprite.Group()  # subsection name objects group in encyclopedia blit on lorenamelist

            self.battlepreview = pygame.sprite.Group() # preview of subunit battle in army editor
            self.trooplistbox = pygame.sprite.Group() # ui box for troop name list
            self.troopnamegroup = pygame.sprite.Group() # troop name list group
            self.filterbox = pygame.sprite.Group()
            self.popuplistbox = pygame.sprite.Group()
            self.popupnamegroup = pygame.sprite.Group()
            self.terrainchangebutton = pygame.sprite.Group() # button to change preview map base terrain
            self.featurechangebutton = pygame.sprite.Group() # button to change preview map terrain feature
            self.weatherchangebutton = pygame.sprite.Group() # button to change preview map weather
            self.armybuildslot = pygame.sprite.Group() # slot for putting troop into army preset during preparation mode
            self.uniteditborder = pygame.sprite.Group() # border that appear when selected sub-subunit
            self.team1previewleader = pygame.sprite.Group() # just to make preview leader class has containers
            self.armypresetnamegroup = pygame.sprite.Group() # preset name list

            # battle object group
            self.battlecamera = pygame.sprite.LayeredUpdates()  # this is layer drawer game camera, all image pos should be based on the map not screen
            ## the camera layer is as followed 0 = terrain map, 1 = dead army, 2 = map special feature, 3 = , 4 = subunit,
            ## 5 = sub-subunit, 6 = flying parentunit, 7 = arrow/range, 8 = weather, 9 = weather matter, 10 = ui/button, 11 = subunit inspect, 12 pop up
            self.battleui = pygame.sprite.LayeredUpdates()  # this is layer drawer for ui, all image pos should be based on the screen

            self.unitupdater = pygame.sprite.Group()  # updater for parentunit objects
            self.subunitupdater = pygame.sprite.Group()  # updater for subunit objects
            self.leaderupdater = pygame.sprite.Group()  # updater for leader objects
            self.uiupdater = pygame.sprite.Group()  # updater for ui objects
            self.weatherupdater = pygame.sprite.Group()  # updater for weather objects
            self.effectupdater = pygame.sprite.Group()  # updater for in-game effect objects (e.g. range attack sprite)

            self.battlemapbase = pygame.sprite.Group()  # base terrain map object
            self.battlemapfeature = pygame.sprite.Group()  # terrain feature map object
            self.battlemapheight = pygame.sprite.Group()  # height map object
            self.showmap = pygame.sprite.Group()  # beautiful map object that is shown in gameplay

            self.team0army = pygame.sprite.Group()  # taem 0 units group
            self.team1army = pygame.sprite.Group()  # taem 1 units group
            self.team2army = pygame.sprite.Group()  # team 2 units group

            self.team0subunit = pygame.sprite.Group()  # taem 0 units group
            self.team1subunit = pygame.sprite.Group()  # taem 1 units group
            self.team2subunit = pygame.sprite.Group()  # team 2 units group

            self.subunit = pygame.sprite.Group()  # all subunits group

            self.armyleader = pygame.sprite.Group()  # all leaders group

            self.arrows = pygame.sprite.Group()  # all arrows group and maybe other range effect stuff later
            self.directionarrows = pygame.sprite.Group()
            self.troopnumbersprite = pygame.sprite.Group() # troop text number that appear next to parentunit sprite

            self.deadunit = pygame.sprite.Group()  # dead subunit group

            self.gameui = pygame.sprite.Group()  # various game ui group
            self.minimap = pygame.sprite.Group()  # minimap ui
            self.eventlog = pygame.sprite.Group()  # event log ui
            self.buttonui = pygame.sprite.Group()  # buttons for various ui group
            self.inspectselectedborder = pygame.sprite.Group()  # subunit selected border in inspect ui army box
            self.fpscount = pygame.sprite.Group()  # fps number counter
            self.switchbuttonui = pygame.sprite.Group()  # button that switch image based on current setting (e.g. parentunit behaviour setting)

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

            self.timeui = pygame.sprite.Group()  # time bar ui
            self.timenumber = pygame.sprite.Group()  # number text of in-game time
            self.speednumber = pygame.sprite.Group()  # number text of current game speed

            self.scaleui = pygame.sprite.Group() # battle scale bar

            self.weathermatter = pygame.sprite.Group()  # sprite of weather effect group such as rain sprite
            self.weathereffect = pygame.sprite.Group()  # sprite of special weather effect group such as fog that cover whole screen
            # ^ End initialise

            # v Assign default groups
            # main menu containers
            gameprepare.Menubutton.containers = self.menubutton
            gameprepare.Menuicon.containers = self.menuicon
            gameprepare.Slidermenu.containers = self.menuslider
            gameprepare.Valuebox.containers = self.valuebox

            gameprepare.Listbox.containers = self.maplistbox, self.trooplistbox, self.popuplistbox
            gameprepare.Namelist.containers = self.mapnamegroup
            gameprepare.Mapshow.containers = self.mapshow
            gameprepare.Teamcoa.containers = self.teamcoa
            gameprepare.Maptitle.containers = self.maptitle
            gameprepare.Mapdescription.containers = self.mapdescription
            gameprepare.Sourcedescription.containers = self.sourcedescription
            gameprepare.Armystat.containers = self.armystat

            gameprepare.Sourcename.containers = self.sourcenamegroup, self.mainui

            gameprepare.Tickbox.containers = self.tickbox

            gamelorebook.Subsectionlist.containers = self.lorenamelist
            gamelorebook.Subsectionname.containers = self.subsectionname, self.mainui, self.battleui

            gameui.Uibutton.containers = self.lorebuttonui

            gameunitedit.Previewbox.main_dir = main_dir
            img = load_image('effect.png', 'map')  # map special effect image
            gameunitedit.Previewbox.effectimage = img
            gameunitedit.Previewbox.containers = self.battlepreview
            gameunitedit.Filterbox.containers = self.filterbox
            gameunitedit.Previewchangebutton.containers = self.terrainchangebutton, self.weatherchangebutton, self.featurechangebutton
            gameunitedit.Armybuildslot.containers = self.armybuildslot
            gameunitedit.Previewleader.containers = self.team1previewleader

            # battle containers
            gamemap.Basemap.containers = self.battlemapbase
            gamemap.Mapfeature.containers = self.battlemapfeature
            gamemap.Mapheight.containers = self.battlemapheight
            gamemap.Beautifulmap.containers = self.showmap, self.battlecamera

            gameunit.Unitarmy.containers = self.unitupdater
            gamesubunit.Subunit.containers = self.subunitupdater, self.subunit, self.battlecamera
            gameleader.Leader.containers = self.armyleader, self.leaderupdater
            gameunit.Troopnumber.containers = self.troopnumbersprite, self.effectupdater, self.battlecamera

            rangeattack.Rangearrow.containers = self.arrows, self.effectupdater, self.battlecamera
            gameunit.Directionarrow.containers = self.directionarrows, self.effectupdater, self.battlecamera

            gameui.Gameui.containers = self.gameui, self.uiupdater
            gameui.Minimap.containers = self.minimap, self.battleui
            gameui.FPScount.containers = self.battleui
            gameui.Uibutton.containers = self.buttonui, self.lorebuttonui
            gameui.Switchuibutton.containers = self.switchbuttonui, self.uiupdater
            gameui.Selectedsquad.containers = self.inspectselectedborder, self.uniteditborder, self.mainui
            gameui.Skillcardicon.containers = self.skillicon, self.battleui, self.mainui
            gameui.Effectcardicon.containers = self.effecticon, self.battleui, self.mainui
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
            self.mapscroll = gameui.Uiscroller(self.maplistbox.rect.topright, self.maplistbox.image.get_height(),
                                               self.maplistbox.maxshowlist, layer=14)  # scroller bar for map list

            self.sourcelistbox = gameprepare.Sourcelistbox((0, 0), imgs[1]) # source list ui box
            self.mapoptionbox = gameprepare.Mapoptionbox((SCREENRECT.width, 0), imgs[1], 0) # ui box for battle option during preparation screen

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
            self.currentarmyrow = 0

            #^ End battle map menu button

            #v Create subunit editor button and ui

            self.armyeditbutton = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 4)),
                                          text="Army Editor")
            self.troopcreatetbutton = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 2.5)),
                                          text="Troop Creator")
            self.editorbackbutton = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height - imagelist[0].get_height()),
                                         text="Back")
            self.editorbutton = (self.armyeditbutton, self.troopcreatetbutton, self.editorbackbutton)
            # ^ End subunit editor

            #v Army editor
            boximg = load_image('army_presetbox.png', 'ui').convert()
            self.armylistbox = gameprepare.Listbox((0, SCREENRECT.height/3), boximg) # box for showing army preset list
            self.armypresetnamescroll = gameui.Uiscroller(self.armylistbox.rect.topright, self.armylistbox.image.get_height(),
                                                 self.armylistbox.maxshowlist, layer=14) # preset name scroll

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

            self.popuplistbox = gameprepare.Listbox((0, 0), boximg, 15) # popup listbox need to be in higher layer
            self.popuplistbox.maxshowlist = 12 # box is smaller than usual
            self.popuplistscroll = gameui.Uiscroller(self.popuplistbox.rect.topright,
                                                     self.popuplistbox.image.get_height(),
                                                     self.popuplistbox.maxshowlist,
                                                     layer=14)

            boximg = load_image('mapchange.png', 'ui').convert()
            self.terrainchangebutton = gameunitedit.Previewchangebutton((SCREENRECT.width/3, SCREENRECT.height), boximg, "Temperate") # start with temperate terrain
            self.featurechangebutton = gameunitedit.Previewchangebutton((SCREENRECT.width/2, SCREENRECT.height), boximg, "Plain") # start with plain feature
            self.weatherchangebutton = gameunitedit.Previewchangebutton((SCREENRECT.width/1.5, SCREENRECT.height), boximg, "Light Sunny") # start with light sunny


            gameunitedit.Armybuildslot.squadwidth = self.squadwidth
            gameunitedit.Armybuildslot.squadheight = self.squadheight
            startpos = [(SCREENRECT.width / 2) - (self.squadwidth * 5),
                            (SCREENRECT.height / 2) - (self.squadheight * 4)]
            gameid = 0
            armyid = 0
            gameid = self.makearmyslot(gameid, 1, armyid, self.teamcolour[1], range(0, 64), startpos) # make player army slot

            #v Make front and rear enemy slot row
            enemystartpos = ((startpos[0], startpos[1] - (self.squadheight + 10)), (startpos[0], startpos[1] + (self.squadheight*8) + 10))
            for pos in enemystartpos:
                armyid += 1
                gameid = self.makearmyslot(gameid, 2, armyid, self.teamcolour[2], range(0, 8), pos)
            #^ End front and rear enemy

            #v Make left and right enemy slot row
            enemystartpos = ((startpos[0] - 10, startpos[1] - self.squadheight), (startpos[0] + (self.squadwidth * 9) + 10, startpos[1] - self.squadheight))
            for pos in enemystartpos:
                armyid += 1
                gameid = self.makearmyslot(gameid, 2, armyid, self.teamcolour[2], range(0, 8), pos, columnonly = True)
            #^ End left and right enemy

            self.team1previewarmy = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],
                                              [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]) # player teat army subunit list
            self.team1previewleader = [gameunitedit.Previewleader(1, 0, 0, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 1, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 2, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 3, self.leaderstat)]
            self.leaderupdater.remove(*self.team1previewleader)
            self.team2testfrontarmy = np.array([0,0,0,0,0,0,0,0]) # front enemy line subunit list
            self.team2testfrontaleader = [gameunitedit.Previewleader(1, 0, 0, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 1, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 2, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 3, self.leaderstat)]
            self.team2testleftarmy = np.array([0,0,0,0,0,0,0,0]) # left enemy line subunit list
            self.team2testleftleader = [gameunitedit.Previewleader(1, 0, 0, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 1, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 2, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 3, self.leaderstat)]
            self.team2testrightarmy = np.array([0,0,0,0,0,0,0,0]) # right enemy line subunit list
            self.team2testrightleader = [gameunitedit.Previewleader(1, 0, 0, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 1, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 2, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 3, self.leaderstat)]
            self.team2testreararmy = np.array([0,0,0,0,0,0,0,0]) # rear enemy line subunit list
            self.team2testrearleader = [gameunitedit.Previewleader(1, 0, 0, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 1, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 2, self.leaderstat),
                               gameunitedit.Previewleader(1, 0, 3, self.leaderstat)]
            self.previewleaderlist = [self.team1previewleader, self.team2testfrontaleader, self.team2testleftleader,
                                      self.team2testrightleader,self.team2testrearleader]

            boximg = load_image('filterbox.png', 'ui').convert()
            self.filterbox = gameunitedit.Filterbox((SCREENRECT.width / 2.5, 0), boximg)

            self.armyeditorbutton = (self.armybackbutton, self.armysavebutton)

            #^ End army editor

            # v Input box popup
            inputuiimg = load_image('inputui.png', 'ui')
            self.inputui = gameprepare.Inputui(inputuiimg, (SCREENRECT.width / 2, SCREENRECT.height / 2)) # user text input ui box popup
            self.inputokbutton = gameprepare.Menubutton(images=imagelist,
                                                        pos=(self.inputui.rect.midleft[0] + imagelist[0].get_width(),
                                                             self.inputui.rect.midleft[1] + imagelist[0].get_height()),
                                                        text="Done")
            self.inputcancelbutton = gameprepare.Menubutton(images=imagelist,
                                                            pos=(self.inputui.rect.midright[0] - imagelist[0].get_width(),
                                                                 self.inputui.rect.midright[1] + imagelist[0].get_height()),
                                                            text="Cancel")
            self.inputbutton = (self.inputokbutton, self.inputcancelbutton)
            self.inputbox = gameprepare.Inputbox((self.inputui.rect.center), self.inputui.image.get_width()) # user text input box

            self.inputuipop = (self.inputui, self.inputbox, self.inputokbutton, self.inputcancelbutton)
            # ^ End input box popup

            #v profile box
            self.profilename = Profilename
            img = load_image('profilebox.png', 'ui')
            self.profilebox = gameprepare.Profilebox(img, (ScreenWidth, 0), self.profilename) # profile name box at top right of screen at main menu screen
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
            self.choosingfaction = True # swap list between faction and subunit, always start with choose faction first as true

            self.battlegame = maingame.Battle(self, self.winstyle)

        def backtomainmenu(self):
            self.menustate = "mainmenu"

            self.mainui.remove(*self.menubutton)

            self.menubutton.remove(*self.menubutton)
            self.menubutton.add(*self.mainmenubutton)

            self.mainui.add(*self.menubutton, self.profilebox)

        def setuplist(self, itemclass, currentrow, showlist, itemgroup, box, screenscale=False, layer=15):
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
                    itemgroup.add(itemclass(box, (pos[0] + column, pos[1] + row), item, layer = layer))  # add new subsection sprite to group
                    row += (30*heightadjust)  # next row
                    if len(itemgroup) > box.maxshowlist: break  # will not generate more than space allowed

            self.mainui.add(*itemgroup)

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

            if oneteam is False:
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
            """Change source description, add new subunit dot, change army stat when select new source"""
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
            armyteamlist = (team1pos,team2pos) # for finding how many subunit in each team

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

        def makearmyslot(self, gameid, team, armyid, teamcolour, rangetorun, startpos, columnonly = False):
            width, height = 0, 0
            squadnum = 0  # Number of subunit based on the position in row and column
            for squad in rangetorun: # generate player army slot for filling troop into preview army
                if columnonly is False:
                    width += self.squadwidth
                    self.armybuildslot.add(gameunitedit.Armybuildslot(gameid, team, armyid, teamcolour, (width, height), startpos))
                    squadnum += 1
                    if squadnum == 8:  # Pass the last subunit in the row, go to the next one
                        width = 0
                        height += self.squadheight
                        squadnum = 0
                else:
                    height += self.squadheight
                    self.armybuildslot.add(gameunitedit.Armybuildslot(gameid, team, armyid, teamcolour, (width, height), startpos))
                    squadnum += 1
                gameid += 1
            return gameid

        def previewauthority(self, leaderlist, armyid):
            # vcalculate authority
            authority = int(
                leaderlist[0].authority + (leaderlist[0].authority / 2) +
                (leaderlist[1].authority / 4) + (leaderlist[2].authority / 4) +
                (leaderlist[3].authority / 10))
            bigarmysize = len([slot for slot in self.armybuildslot if slot.armyid == armyid and slot.name != "None"])
            if bigarmysize > 20:  # army size larger than 20 will reduce main leader authority
                authority = int(leaderlist[0].authority +
                                (leaderlist[0].authority / 2 * (100 - (bigarmysize)) / 100) +
                                leaderlist[1].authority / 2 + leaderlist[2].authority / 2 +
                                leaderlist[3].authority / 4)

            for slot in self.armybuildslot:
                if slot.armyid == armyid:
                    slot.authority = authority

            if self.showincard is not None:
                self.gameui[1].valueinput(who=self.showincard)
            # ^ End cal authority

        def popuplistnewopen(self, newrect, newlist, type):
            """Move popuplistbox and scroll sprite to new location and create new name list baesd on type"""
            self.currentpopuprow = 0

            if type == "leader":
                self.popuplistbox.rect = self.popuplistbox.image.get_rect(topleft=(newrect))
            else:
                self.popuplistbox.rect = self.popuplistbox.image.get_rect(midbottom=(newrect))

            self.setuplist(gameprepare.Namelist, 0, newlist, self.popupnamegroup,
                           self.popuplistbox, layer=17)

            self.popuplistscroll.pos = self.popuplistbox.rect.topright # change position variable
            self.popuplistscroll.rect = self.popuplistscroll.image.get_rect(topleft=self.popuplistbox.rect.topright) #
            self.popuplistscroll.changeimage(newrow=0, logsize=len(newlist))

            self.mainui.add(self.popuplistbox, *self.popupnamegroup, self.popuplistscroll)  # add the option list to screen

            self.popuplistbox.type = type

        def popoutlorebook(self, section, gameid):
            # v Seem like encyclopedia in battle cause container to change allui in main to maingame one, change back with this
            gamelorebook.Subsectionname.containers = self.subsectionname, self.mainui
            # ^ End container change

            self.beforelorestate = self.menustate
            self.menustate = "encyclopedia"
            self.mainui.add(self.lorebook, self.lorescroll, self.lorenamelist, *self.lorebuttonui,)  # add sprite related to encyclopedia
            self.lorebook.changesection(section, self.lorenamelist, self.subsectionname, self.lorescroll,
                                        self.pagebutton, self.mainui)
            self.lorebook.changesubsection(gameid, self.pagebutton, self.mainui)
            self.lorescroll.changeimage(newrow=self.lorebook.currentsubsectionrow)

        def run(self):
            while True:
                #v Get user input
                mouse_up = False
                mouse_down = False
                mouse_right = False
                mouse_scrolldown = False
                mouse_scrollup = False
                keypress = None
                esc_press = False
                keystate = pygame.key.get_pressed()
                for event in pygame.event.get():
                    if self.textinputpopup is not None: # event update to input box
                        self.inputbox.userinput(event)

                    if pygame.mouse.get_pressed()[0]:  # Hold left click
                        mouse_down = True

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:  # left click
                            mouse_up = True
                        elif event.button == 3:
                            mouse_right = True
                        elif event.button == 4:  # Mouse scroll down
                            mouse_scrollup = True

                        elif event.button == 5:  # Mouse scroll up
                            mouse_scrolldown = True

                    elif event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            esc_press = True
                        else:  # holding other keys
                            keypress = event.key

                    if event.type == QUIT or self.quitbutton.event == True or (esc_press and self.menustate == "mainmenu"):
                        return

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

                            self.menubutton.add(*self.mapselectbutton)
                            self.mainui.add(*self.mapselectbutton, self.maplistbox, self.maptitle, self.mapscroll)

                        elif self.uniteditbutton.event: # custom subunit/sub-subunit editor menu
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
                            #v Seem like encyclopedia in battle cause container to change allui in main to maingame one, change back with this
                            gamelorebook.Subsectionname.containers = self.subsectionname, self.mainui
                            #^ End container change

                            self.beforelorestate = self.menustate
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
                                                                  self.sourcelistbox.maxshowlist, layer=14) # scroller bar for source list

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
                                        if box.tick is False:
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
                            self.backtomainmenu()

                        elif self.armyeditbutton.event:
                            self.armyeditbutton.event = False
                            self.menustate = "armyeditor"

                            self.currenttrooprow = 0
                            self.currentarmyrow = 0

                            self.mainui.remove(*self.menubutton)

                            self.menubutton.remove(*self.menubutton)
                            self.menubutton.add(*self.armyeditorbutton)

                            self.fulltrooplist = [item[0] for item in self.gameunitstat.unitlist.values()][1:]

                            self.trooplist = self.fulltrooplist # generate troop name list
                            self.troopindexlist = list(range(0, len(self.trooplist) + 1))

                            self.leaderlist = [item[0] for item in self.leaderstat.leaderlist.values()][1:] # generate leader name list

                            self.setuplist(gameprepare.Namelist, self.currentarmyrow, list(self.customarmypresetlist.keys()),
                                           self.armypresetnamegroup , self.armylistbox) # setup preset army list

                            self.setuplist(gameprepare.Namelist, self.currenttrooprow, self.trooplist,
                                           self.troopnamegroup, self.trooplistbox) # setup troop name list

                            self.currentlistshow = "troop"
                            self.preparestate = True
                            self.baseterrain = 0
                            self.featureterrain = 0
                            self.weathertype = 4
                            self.weatherstrength = 0
                            self.currentweather = gameweather.Weather(self.timeui, self.weathertype, self.weatherstrength, self.allweather)
                            self.showincard = None # current sub-subunit showing in subunit card
                            self.leadernow = []  # list of showing leader in command ui

                            self.gameui[1].rect = self.gameui[1].image.get_rect(center=(self.gameui[1].X,
                                                                                        self.gameui[1].image.get_height()/2)) # leader ui

                            self.gameui[2].rect = self.gameui[2].image.get_rect(bottomright=(SCREENRECT.width,
                                                                                        SCREENRECT.height)) # troop info card ui
                            self.buttonui[0].rect = self.buttonui[0].image.get_rect(topleft=(self.gameui[2].rect.topleft[0], # description button
                                                                                          self.gameui[2].rect.topleft[1]+120))
                            self.buttonui[1].rect = self.buttonui[1].image.get_rect(topleft=(self.gameui[2].rect.topleft[0], # stat button
                                                                                          self.gameui[2].rect.topleft[1]))
                            self.buttonui[2].rect = self.buttonui[2].image.get_rect(topleft=(self.gameui[2].rect.topleft[0], # skill button
                                                                                          self.gameui[2].rect.topleft[1] + 40))
                            self.buttonui[3].rect = self.buttonui[3].image.get_rect(topleft=(self.gameui[2].rect.topleft[0], # equipment button
                                                                                          self.gameui[2].rect.topleft[1] + 80))

                            self.maketeamcoa([0], oneteam=True,team1setpos=(self.trooplistbox.rect.midleft[0] - int((200 * self.widthadjust)/2),
                                                                            self.trooplistbox.rect.midleft[1])) # default faction select as all faction

                            self.troopscroll.changeimage(newrow=self.currenttrooprow, logsize=len(self.trooplist)) # change troop scroll image

                            for index, slot in enumerate(self.armybuildslot):  # start with the first player subunit slot selected when enter
                                if index == 0:
                                    slot.selected = True
                                    for border in self.uniteditborder:
                                        border.kill()
                                        del border
                                    self.uniteditborder.add(gameui.Selectedsquad(slot.inspposition))
                                else: # reset all other slot
                                    slot.selected = False

                            self.mainui.add(*self.menubutton, self.battlepreview, self.trooplistbox, self.troopscroll, self.armylistbox, self.armypresetnamescroll,
                                            self.timeui, *self.timebutton, self.timenumber, self.gameui[1], self.gameui[2], self.filterbox, *self.unitcardbutton,
                                            self.terrainchangebutton, self.featurechangebutton, self.weatherchangebutton, self.timenumber, self.speednumber,
                                            *self.armybuildslot)

                    elif self.menustate == "armyeditor": # custom parentunit preset creator and test

                        if self.armybackbutton.event or esc_press: # or self.armysavebutton.event
                            self.armybackbutton.event = False
                            self.showincard = None
                            self.menustate = "uniteditor"

                            self.gameui[1].rect = self.gameui[1].image.get_rect(center=(self.gameui[1].X, self.gameui[1].Y)) # change leader ui position back
                            self.gameui[2].rect = self.gameui[2].image.get_rect(center=(self.gameui[2].X, self.gameui[2].Y)) # change subunit card position back
                            self.buttonui[0].rect = self.buttonui[0].image.get_rect(center=(self.gameui[2].X - 152, self.gameui[2].Y + 10))
                            self.buttonui[1].rect = self.buttonui[1].image.get_rect(center=(self.gameui[2].X - 152, self.gameui[2].Y - 70))
                            self.buttonui[2].rect = self.buttonui[2].image.get_rect(center=(self.gameui[2].X - 152, self.gameui[2].Y - 30))
                            self.buttonui[3].rect = self.buttonui[3].image.get_rect(center=(self.gameui[2].X - 152, self.gameui[2].Y + 50))

                            self.mainui.remove(*self.menubutton, self.battlepreview, self.trooplistbox, self.troopscroll, self.teamcoa, self.armylistbox,
                                               self.armypresetnamescroll, *self.timebutton, self.timeui, self.timenumber, self.gameui[1],
                                               self.gameui[2], self.filterbox, *self.unitcardbutton, self.terrainchangebutton, self.featurechangebutton,
                                               self.weatherchangebutton, self.timenumber, self.speednumber, *self.armybuildslot, *self.leadernow)

                            for group in self.troopnamegroup, self.uniteditborder, self.armypresetnamegroup:
                                for item in group:  # remove name list
                                    item.kill()
                                    del item


                            for slot in self.armybuildslot: # reset all sub-subunit slot
                                slot.changetroop(0, self.baseterrain,
                                                 self.baseterrain * len(self.battlemapfeature.featurelist) + self.featureterrain,
                                                 self.currentweather)
                                slot.leader = None  # remove leader link in

                            for leaderlist in self.previewleaderlist:
                                for leader in leaderlist:
                                    leader.subunit = None  # remove subunit link in leader
                                    leader.changeleader(1, self.leaderstat)


                            del self.currentweather

                            self.trooplist = [item[0] for item in self.gameunitstat.unitlist.values()][1:] # reset troop filter back to all faction
                            self.troopindexlist = list(range(0, len(self.trooplist) + 1))

                            self.leaderlist = [item[0] for item in self.leaderstat.leaderlist.values()][1:]  # generate leader name list)

                            self.leadernow = []

                            self.menubutton.remove(*self.menubutton)
                            self.menubutton.add(*self.editorbutton)

                            self.mainui.add(*self.editorbutton)

                        elif self.popuplistbox in self.mainui and self.popuplistbox.type == "leader" \
                                and self.popuplistbox.rect.collidepoint(self.mousepos): # this need to be at the top here to prioritise popup click
                            self.mainui.remove(self.leaderpopup)
                            for index, name in enumerate(self.popupnamegroup): # change leader with the new selected one
                                if name.rect.collidepoint(self.mousepos):
                                    if mouse_up and self.showincard.name != "None":
                                        if self.leadernow[self.selectleader].name != "None":  # remove leader from previous slot first
                                            self.leadernow[self.selectleader].leader = None
                                            self.leadernow[self.selectleader].squad.leader = None

                                        trueindex = [index for index, value in enumerate(list(self.leaderstat.leaderlist.values())) if value[0] == name.name][0]
                                        trueindex = list(self.leaderstat.leaderlist.keys())[trueindex]
                                        self.leadernow[self.selectleader].changeleader(trueindex, self.leaderstat)
                                        self.leadernow[self.selectleader].squad = self.showincard
                                        self.showincard.leader = self.leadernow[self.selectleader]
                                        self.previewauthority(self.leadernow, self.leadernow[self.selectleader].squad.armyid)
                                        self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                                  changeoption=1)
                                    elif mouse_right:
                                        self.popoutlorebook(8, self.currentpopuprow + index + 1)

                        elif self.armylistbox.rect.collidepoint(self.mousepos):
                            for index, name in enumerate(self.armypresetnamegroup):
                                if name.rect.collidepoint(self.mousepos) and mouse_up:
                                    if list(self.customarmypresetlist.keys())[index] != "New Preset":
                                        armylist = []
                                        arraylist = list(self.customarmypresetlist[list(self.customarmypresetlist.keys())[index]])
                                        for listnum in (0,1,2,3,4,5,6,7):
                                            armylist += [int(item) if item.isdigit() else item
                                                         for item in arraylist[listnum].split(',')]
                                        leaderwholist = [int(item) if item.isdigit() else item
                                                         for item in arraylist[8].split(',')]
                                        leaderposlist = [int(item) if item.isdigit() else item
                                                         for item in arraylist[9].split(',')]


                                        for index, item in enumerate(armylist): # change all slot to whatever save in the selected preset
                                            for slot in self.armybuildslot:
                                                if slot.gameid == index:
                                                    slot.changetroop(item, self.baseterrain,
                                                                self.baseterrain * len(self.battlemapfeature.featurelist)
                                                                + self.featureterrain, self.currentweather)
                                                    break

                                        for index, item in enumerate(leaderwholist):
                                            self.team1previewleader[index].leader = None
                                            if self.team1previewleader[index].subunit is not None:
                                                self.team1previewleader[index].subunit.leader = None

                                            self.team1previewleader[index].changeleader(item, self.leaderstat)

                                            posindex = 0
                                            for slot in self.armybuildslot: # can't use gameid here as none subunit not count in position check
                                                if posindex == leaderposlist[index]:
                                                    self.team1previewleader[index].subunit = slot
                                                    slot.leader = self.team1previewleader[index]
                                                    break
                                                else:
                                                    if slot.name != "None":
                                                        posindex+=1

                                        self.previewauthority(self.team1previewleader, 0) #calculate authority

                                    else: # new preset
                                        for slot in self.armybuildslot:  # reset all sub-subunit slot
                                            slot.changetroop(0, self.baseterrain,
                                                             self.baseterrain * len(self.battlemapfeature.featurelist) + self.featureterrain,
                                                             self.currentweather)
                                            slot.leader = None  # remove leader link in

                                        for leaderlist in self.previewleaderlist:
                                            for leader in leaderlist:
                                                leader.subunit = None  # remove subunit link in leader
                                                leader.changeleader(1, self.leaderstat)


                                        # self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon, armourlist=self.allarmour,
                                        #                       changeoption=1)

                        elif self.gameui[1].rect.collidepoint(self.mousepos):
                            for index, leader in enumerate(self.leadernow): # loop mouse pos on leader portrait
                                if leader.rect.collidepoint(self.mousepos):
                                    armyposition = self.leaderposname[leader.armyposition + 4]

                                    self.leaderpopup.pop(self.mousepos, armyposition + ": " + leader.name)  # popup leader name when mouse over
                                    self.mainui.add(self.leaderpopup)

                                    if mouse_up: # open list of leader to change leader in that slot
                                        self.selectleader = index
                                        self.popuplistnewopen(leader.rect.midright, self.leaderlist, "leader")

                                    elif mouse_right:
                                        self.popoutlorebook(8, leader.gameid)
                                    break
                                else:
                                    self.mainui.remove(self.leaderpopup)

                        elif self.gameui[2].rect.collidepoint(self.mousepos):
                            if self.showincard is not None:
                                for button in self.unitcardbutton:
                                    if button.rect.collidepoint(self.mousepos) and mouse_up:
                                        if self.gameui[2].option != button.event:
                                            self.gameui[2].option = button.event
                                            self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                                      changeoption=1)

                                            if self.gameui[2].option == 2:
                                                self.traitskillblit()
                                                self.effecticonblit()
                                                self.countdownskillicon()
                                            else:
                                                for icon in self.skillicon.sprites(): icon.kill()
                                                for icon in self.effecticon.sprites(): icon.kill()
                                        break

                            if self.gameui[2].option == 2:
                                for iconlist in (self.effecticon, self.skillicon):
                                    for icon in iconlist:
                                        if icon.rect.collidepoint(self.mousepos):
                                            checkvalue = self.gameui[2].value2[icon.type]
                                            self.effectpopup.pop(self.mousepos, checkvalue[icon.gameid])
                                            self.mainui.add(self.effectpopup)
                                            if mouse_right:
                                                if icon.type == 0:  # Trait
                                                    section = 7
                                                elif icon.type == 1:  # Skill
                                                    section = 6
                                                else:
                                                    section = 5  # Status effect
                                                self.popoutlorebook(section, icon.gameid)
                                            break
                                        else:
                                            self.mainui.remove(self.effectpopup)

                        elif mouse_up or mouse_down or mouse_right: # accept both click and hold left mouse button
                            if mouse_up or mouse_down:
                                if self.popuplistbox in self.mainui:
                                    if self.popuplistbox.rect.collidepoint(self.mousepos):
                                        for index, name in enumerate(self.popupnamegroup):
                                            if name.rect.collidepoint(self.mousepos) and mouse_up:
                                                if self.popuplistbox.type == "terrain":
                                                    self.terrainchangebutton.changetext(self.battlemapbase.terrainlist[index])
                                                    self.baseterrain = index
                                                    self.battlepreview.changeterrain(self.battlepreview.newcolourlist[(self.baseterrain * len(
                                                        self.battlemapfeature.featurelist)) + self.featureterrain])

                                                elif self.popuplistbox.type == "feature":
                                                    self.featurechangebutton.changetext(self.battlemapfeature.featurelist[index])
                                                    self.featureterrain = index
                                                    self.battlepreview.changeterrain(self.battlepreview.newcolourlist[(self.baseterrain * len(
                                                        self.battlemapfeature.featurelist)) + self.featureterrain])

                                                elif self.popuplistbox.type == "weather":
                                                    self.weathertype = int(index / 3)
                                                    self.weatherstrength = index - (self.weathertype * 3)
                                                    self.weatherchangebutton.changetext(self.weatherlist[self.currentmapselect + index])
                                                    del self.currentweather
                                                    self.currentweather = gameweather.Weather(self.timeui, self.weathertype+1, self.weatherstrength,
                                                                                              self.allweather)

                                                for slot in self.armybuildslot:  # reset all troop stat
                                                    slot.changetroop(slot.troopindex, self.baseterrain,
                                                                     self.baseterrain * len(
                                                                     self.battlemapfeature.featurelist) + self.featureterrain,
                                                                     self.currentweather)
                                                    if slot.selected and slot.name != "None": # reset subunit card as well
                                                        self.gameui[1].valueinput(who=self.showincard)
                                                        self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                                  armourlist=self.allarmour,
                                                                                  changeoption=1)
                                                        if self.gameui[2].option == 2:
                                                            self.traitskillblit()
                                                            self.effecticonblit()
                                                            self.countdownskillicon()

                                                for name in self.popupnamegroup:  # remove troop name list
                                                    name.kill()
                                                    del name

                                                self.mainui.remove(self.popuplistbox, self.popuplistscroll)
                                                break

                                    elif self.popuplistscroll.rect.collidepoint(self.mousepos):
                                        self.currentpopuprow = self.popuplistscroll.update(
                                            self.mousepos)  # update the scroller and get new current subsection
                                        if self.popuplistbox.type == "terrain":
                                            self.setuplist(gameprepare.Namelist, self.currentpopuprow, self.battlemapbase.terrainlist, self.popupnamegroup,
                                                           self.popuplistbox, layer=17)
                                        elif self.popuplistbox.type == "feature":
                                            self.setuplist(gameprepare.Namelist, self.currentpopuprow, self.battlemapfeature.featurelist, self.popupnamegroup,
                                                           self.popuplistbox, layer=17)
                                        elif self.popuplistbox.type == "weather":
                                            self.setuplist(gameprepare.Namelist, self.currentpopuprow, self.weatherlist, self.popupnamegroup,
                                                           self.popuplistbox, layer=17)
                                        elif self.popuplistbox.type == "leader":
                                            self.setuplist(gameprepare.Namelist, self.currentpopuprow, self.leaderlist, self.popupnamegroup,
                                                           self.popuplistbox, layer=17)

                                    else:
                                        self.mainui.remove(self.popuplistbox, self.popuplistscroll, *self.popupnamegroup)

                                elif self.battlepreview.rect.collidepoint(self.mousepos):
                                    for slot in self.armybuildslot: # left click on any sub-subunit slot
                                        if slot.rect.collidepoint(self.mousepos):

                                            if keystate[pygame.K_LSHIFT]: # add all sub-subunit from the first selected
                                                firstone = None
                                                for newslot in self.armybuildslot:
                                                    if newslot.armyid == slot.armyid and newslot.gameid <= slot.gameid:
                                                        if firstone is None and newslot.selected: # found the previous selected sub-subunit
                                                            firstone = newslot.gameid
                                                            if slot.gameid <= firstone: # cannot go backward, stop loop
                                                                break
                                                            else: # forward select, acceptable
                                                                slot.selected = True
                                                                self.uniteditborder.add(gameui.Selectedsquad(slot.inspposition, 5))
                                                        elif firstone is not None and newslot.gameid > firstone and newslot.selected is False: # select from first select to clicked
                                                            newslot.selected = True
                                                            self.uniteditborder.add(gameui.Selectedsquad(newslot.inspposition, 5))

                                            elif keystate[pygame.K_LCTRL]: # add another selected sub-subunit with left ctrl + left mouse button
                                                slot.selected = True
                                                self.uniteditborder.add(gameui.Selectedsquad(slot.inspposition, 5))
                                            else: # select one sub-subunit by normal left click
                                                for border in self.uniteditborder: # remove all other border
                                                    border.kill()
                                                    del border
                                                slot.selected = True
                                                self.uniteditborder.add(gameui.Selectedsquad(slot.inspposition, 5))

                                            if slot.name != "None":
                                                self.mainui.remove(*self.leadernow)
                                                self.leadernow = self.previewleaderlist[slot.armyid]
                                                self.mainui.add(*self.leadernow)  # add leader portrait to draw
                                                self.showincard = slot
                                                self.gameui[1].valueinput(who=self.showincard)
                                                self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                          armourlist=self.allarmour) # update subunit card on selected subunit
                                                if self.gameui[2].option == 2:
                                                    self.traitskillblit()
                                                    self.effecticonblit()
                                                    self.countdownskillicon()

                                        elif keystate[pygame.K_LCTRL] == 0 and keystate[pygame.K_LSHIFT] == 0: # normal left click select remove all other
                                            slot.selected = False

                                elif self.troopscroll.rect.collidepoint(self.mousepos):  # click on subsection list scroller
                                    self.currenttrooprow = self.troopscroll.update(
                                        self.mousepos)  # update the scroller and get new current subsection
                                    if self.currentlistshow == "troop":
                                        self.setuplist(gameprepare.Namelist, self.currenttrooprow, self.trooplist, self.troopnamegroup,
                                                       self.trooplistbox)
                                    elif self.currentlistshow == "faction":
                                        self.setuplist(gameprepare.Namelist, self.currenttrooprow, self.factionlist, self.troopnamegroup,
                                                       self.trooplistbox)

                                elif self.armypresetnamescroll.rect.collidepoint(self.mousepos):
                                    self.currentarmyrow = self.armypresetnamescroll.update(
                                        self.mousepos)  # update the scroller and get new current subsection
                                    self.setuplist(gameprepare.Namelist, self.currentarmyrow, list(self.customarmypresetlist.keys()),
                                                   self.armypresetnamegroup, self.armylistbox)  # setup preset army list

                            if mouse_up or mouse_right:
                                if self.trooplistbox.rect.collidepoint(self.mousepos):
                                    for index, name in enumerate(self.troopnamegroup):
                                        if name.rect.collidepoint(self.mousepos):
                                            if self.currentlistshow == "faction":
                                                self.currenttrooprow = 0

                                                if mouse_up:
                                                    if index != 0: # pick faction
                                                            self.trooplist = [item[1][0] for item in self.gameunitstat.unitlist.items()
                                                                                     if item[1][0] == "None" or
                                                                                     item[0] in self.allfaction.factionlist[index][1]]
                                                            self.troopindexlist = [0] + self.allfaction.factionlist[index][1]

                                                            self.leaderlist = [item[1][0] for thisindex, item in enumerate(self.leaderstat.leaderlist.items())
                                                                                     if thisindex > 0 and (item[1][0] == "None" or (item[0] >= 10000 and item[1][8] in (0, index)) or
                                                                                     item[0] in self.allfaction.factionlist[index][2])]


                                                    else: # pick all faction
                                                        self.trooplist = [item[0] for item in self.gameunitstat.unitlist.values()][1:]
                                                        self.troopindexlist = list(range(0, len(self.trooplist) + 1))

                                                        self.leaderlist = self.leaderlist = [item[0] for item in self.leaderstat.leaderlist.values()][1:]

                                                    self.setuplist(gameprepare.Namelist, self.currenttrooprow, self.trooplist, self.troopnamegroup,
                                                                   self.trooplistbox) # setup troop name list
                                                    self.troopscroll.changeimage(newrow=self.currenttrooprow,
                                                                                 logsize=len(self.trooplist))  # change troop scroll image

                                                    self.maketeamcoa([index], oneteam=True,
                                                                     team1setpos=(self.trooplistbox.rect.midleft[0] - int((200 * self.widthadjust) / 2),
                                                                                  self.trooplistbox.rect.midleft[1]))  # change team coa

                                                    self.currentlistshow = "troop"

                                                elif mouse_right:
                                                        self.popoutlorebook(2, index)

                                            elif self.currentlistshow == "troop":
                                                if mouse_up:
                                                    for slot in self.armybuildslot:
                                                        if slot.selected:
                                                            if keystate[pygame.K_LSHIFT]: # change all sub-subunit in army
                                                                for newslot in self.armybuildslot:
                                                                    if newslot.armyid == slot.armyid:
                                                                        newslot.changetroop(self.troopindexlist[index + self.currenttrooprow],
                                                                                            self.baseterrain,
                                                                                            self.baseterrain * len(self.battlemapfeature.featurelist)
                                                                                            + self.featureterrain, self.currentweather)

                                                            else:
                                                                slot.changetroop(self.troopindexlist[index + self.currenttrooprow], self.baseterrain,
                                                                     self.baseterrain * len(self.battlemapfeature.featurelist)+self.featureterrain,
                                                                     self.currentweather)

                                                            if slot.name != "None": #update information of subunit that just got changed
                                                                self.mainui.remove(*self.leadernow)
                                                                self.leadernow = self.previewleaderlist[slot.armyid]
                                                                self.mainui.add(*self.leadernow)  # add leader portrait to draw
                                                                self.showincard = slot
                                                                self.previewauthority(self.leadernow, slot.armyid)
                                                                self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                                          armourlist=self.allarmour)  # update subunit card on selected subunit
                                                                if self.gameui[2].option == 2:
                                                                    self.traitskillblit()
                                                                    self.effecticonblit()
                                                                    self.countdownskillicon()
                                                            elif slot.name == "None" and slot.leader is not None: #remove leader from none subunit if any
                                                                slot.leader.changeleader(1, self.leaderstat)
                                                                slot.leader.subunit = None # remove subunit link in leader
                                                                slot.leader = None # remove leader link in subunit
                                                                self.previewauthority(self.leadernow, slot.armyid)

                                                elif mouse_right: # upen encyclopedia
                                                    self.popoutlorebook(3, self.troopindexlist[index + self.currenttrooprow])
                                            break

                                elif mouse_up:
                                    if self.terrainchangebutton.rect.collidepoint(self.mousepos): # change map terrain button
                                        self.popuplistnewopen(self.terrainchangebutton.rect.midtop, self.battlemapbase.terrainlist, "terrain")

                                    elif self.featurechangebutton.rect.collidepoint(self.mousepos): # change map feature button
                                        self.popuplistnewopen(self.featurechangebutton.rect.midtop, self.battlemapfeature.featurelist, "feature")

                                    elif self.weatherchangebutton.rect.collidepoint(self.mousepos): # change map weather button
                                        self.popuplistnewopen(self.weatherchangebutton.rect.midtop, self.weatherlist, "weather")

                                    for team in self.teamcoa:
                                        if team.rect.collidepoint(self.mousepos):
                                            if self.currentlistshow == "troop":
                                                self.currenttrooprow = 0
                                                self.setuplist(gameprepare.Namelist, self.currenttrooprow, self.factionlist, self.troopnamegroup,
                                                               self.trooplistbox)
                                                self.troopscroll.changeimage(newrow=self.currenttrooprow,
                                                                             logsize=len(self.factionlist))  # change troop scroll image
                                                self.currentlistshow = "faction"

                        if self.popuplistbox in self.mainui: # mouse scroll on popup list
                            if self.popuplistbox.type == "terrain":
                                self.currentpopuprow = self.listscroll(mouse_scrollup, mouse_scrolldown, self.popuplistscroll, self.popuplistbox,
                                                                       self.currentpopuprow, self.battlemapbase.terrainlist, self.popupnamegroup)
                            elif self.popuplistbox.type == "feature":
                                self.currentpopuprow = self.listscroll(mouse_scrollup, mouse_scrolldown, self.popuplistscroll, self.popuplistbox,
                                                                       self.currentpopuprow, self.battlemapfeature.featurelist, self.popupnamegroup)
                            elif self.popuplistbox.type == "weather":
                                self.currentpopuprow = self.listscroll(mouse_scrollup, mouse_scrolldown, self.popuplistscroll, self.popuplistbox,
                                                                       self.currentpopuprow, self.weatherlist, self.popupnamegroup)
                            elif self.popuplistbox.type == "leader":
                                self.currentpopuprow = self.listscroll(mouse_scrollup, mouse_scrolldown, self.popuplistscroll, self.popuplistbox,
                                                                   self.currentpopuprow, self.leaderlist, self.popupnamegroup)

                        else: # mouse scroll on army preset list
                            self.currentarmyrow = self.listscroll(mouse_scrollup, mouse_scrolldown, self.armypresetnamescroll, self.armylistbox,
                                                                   self.currentarmyrow, list(self.customarmypresetlist.keys()), self.armypresetnamegroup)

                        if self.currentlistshow == "troop": # mouse scroll on troop list
                            self.currenttrooprow = self.listscroll(mouse_scrollup, mouse_scrolldown, self.troopscroll, self.trooplistbox,
                                                                self.currenttrooprow, self.trooplist, self.troopnamegroup)
                        elif self.currentlistshow == "faction": # mouse scroll on faction list
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
                                            self.menustate = self.beforelorestate # change menu back to default 0

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
