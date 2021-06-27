try:  # for printing error log when error exception happen
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

    from gamescript import gamebattle, gameleader, gamemap, gamelongscript, gamelorebook, gameweather, gamedrama, \
        gamefaction, gameunitstat, gameui, gameprepare, gamemenu, gameunit, gamesubunit, gamerangeattack, gamepopup, gameunitedit

    screen = screeninfo.get_monitors()[0]

    screenWidth = int(screen.width)
    screenHeight = int(screen.height)

    config = configparser.ConfigParser()
    try:
        config.read_file(open("configuration.ini"))  # read config file
    except Exception:  # Create config file if not found with the default
        config = configparser.ConfigParser()
        config["DEFAULT"] = {"screenwidth": screenWidth, "screenheight": screenHeight, "fullscreen": "0",
                             "playername": "Noname", "soundvolume": "100.0", "musicvolume": "0.0",
                             "voicevolume": "0.0", "maxfps": "60", "ruleset": "1"}
        with open("configuration.ini", "w") as cf:
            config.write(cf)
        config.read_file(open("configuration.ini"))
    ScreenHeight = int(config["DEFAULT"]["ScreenHeight"])
    ScreenWidth = int(config["DEFAULT"]["ScreenWidth"])
    FULLSCREEN = int(config["DEFAULT"]["Fullscreen"])
    Soundvolume = float(config["DEFAULT"]["SoundVolume"])
    Profilename = str(config["DEFAULT"]["playername"])

    SCREENRECT = Rect(0, 0, ScreenWidth, ScreenHeight)
    widthadjust = SCREENRECT.width / 1366
    heightadjust = SCREENRECT.height / 768

    main_dir = os.path.split(os.path.abspath(__file__))[0]

    load_image = gamelongscript.load_image
    load_images = gamelongscript.load_images
    csv_read = gamelongscript.csv_read
    load_sound = gamelongscript.load_sound
    editconfig = gamelongscript.editconfig
    makebarlist = gamelongscript.makebarlist
    load_base_button = gamelongscript.load_base_button
    text_objects = gamelongscript.text_objects
    game_intro = gamelongscript.game_intro
    teamcolour = ((255, 255, 255), (144, 167, 255), (255, 114, 114))  # team colour, Neutral, 1, 2

    class Mainmenu:
        leaderposname = ("Commander", "Sub-General", "Sub-General", "Sub-Commander", "General", "Sub-General", "Sub-General",
                         "Advisor")  # Name of leader position in parentunit, the first 4 is for commander parentunit
        traitskillblit = gamelongscript.traitskillblit
        effecticonblit = gamelongscript.effecticonblit
        countdownskillicon = gamelongscript.countdownskillicon

        def __init__(self):
            pygame.init()  # Initialize pygame

            self.rulesetlist = gamebattle.csv_read("ruleset_list.csv", ["data", "ruleset"])  # get ruleset list
            self.ruleset = 1  # for now default historical ruleset only
            self.rulesetfolder = "/" + str(self.rulesetlist[self.ruleset][1])

            if not os.path.exists("profile"):  # make profile folder if not existed
                os.makedirs("profile")
                os.makedirs("profile/armypreset")
            if not os.path.exists("profile/armypreset/" + str(self.ruleset)):  # create armypreset folder for ruleset
                os.makedirs("profile/armypreset/" + str(self.ruleset))
            try:
                customarmypresetlist = csv_read("custom_unitpreset.csv", ["profile", "armypreset", str(self.ruleset)])
                del customarmypresetlist["presetname"]
                self.customarmypresetlist = {"New Preset": 0, **customarmypresetlist}
            except Exception:
                with open("profile/armypreset/" + str(self.ruleset) + "/custom_unitpreset.csv", "w") as csvfile:
                    filewriter = csv.writer(csvfile, delimiter=",",
                                            quotechar="|", quoting=csv.QUOTE_MINIMAL)
                    filewriter.writerow(["presetname", "armyline2", "armyline3", "armyline4", "armyline15", "armyline6", "armyline7", "armyline8",
                                         "leader", "leaderposition", "faction"])  # create header
                    csvfile.close()

                self.customarmypresetlist = {}

            # if not os.path.exists("\customunit"): # make custom subunit folder if not existed

            self.enactment = True
            self.mapsource = 0  # current selected map source
            self.teamselected = 1

            # v Set the display mode
            self.winstyle = 0  # FULLSCREEN
            if FULLSCREEN == 1:
                self.winstyle = pygame.FULLSCREEN
            self.bestdepth = pygame.display.mode_ok(SCREENRECT.size, self.winstyle, 32)
            self.screen = pygame.display.set_mode(SCREENRECT.size, self.winstyle | pygame.RESIZABLE, self.bestdepth)
            self.widthadjust = SCREENRECT.width / 1366
            self.heightadjust = SCREENRECT.height / 768
            # ^ End set display

            # v Decorate the game window
            # icon = load_image("sword.jpg")
            # icon = pygame.transform.scale(icon, (32, 32))
            # pygame.display.set_icon(icon)
            # ^ End decorate

            # v Initialise Game Groups
            # main menu object group
            self.mainui = pygame.sprite.LayeredUpdates()  # sprite drawer group
            self.menu_button = pygame.sprite.Group()  # group of menu buttons that are currently get shown and update
            self.menuicon = pygame.sprite.Group()  # mostly for option icon like volumne or scren resolution

            self.menuslider = pygame.sprite.Group()
            self.map_listbox = pygame.sprite.Group()  # ui box for map list
            self.mapnamegroup = pygame.sprite.Group()  # map name list group
            self.mapshow = pygame.sprite.Group()  # preview image of selected map
            self.teamcoa = pygame.sprite.Group()  # team coat of arm that also act as team selection icon
            self.maptitle = pygame.sprite.Group()  # map title box
            self.mapdescription = pygame.sprite.Group()  # map description box in map select screen
            self.sourcedescription = pygame.sprite.Group()  # map source description box in preset battle preparation screen
            self.armystat = pygame.sprite.Group()  # ui box that show army stat in preset battle preparation screen

            self.sourcenamegroup = pygame.sprite.Group()  # source name list group

            self.tickbox = pygame.sprite.Group()  # option tick box

            self.lorebuttonui = pygame.sprite.Group()  # buttons for enclycopedia group
            self.valuebox = pygame.sprite.Group()  # value number and box in esc menu option
            self.lorenamelist = pygame.sprite.Group()  # box sprite for showing subsection name list in encyclopedia
            self.subsection_name = pygame.sprite.Group()  # subsection name objects group in encyclopedia blit on lorenamelist

            self.troop_listbox = pygame.sprite.Group()  # ui box for troop name list
            self.troopnamegroup = pygame.sprite.Group()  # troop name list group
            self.filterbox = pygame.sprite.Group()
            self.popup_listbox = pygame.sprite.Group()
            self.popupnamegroup = pygame.sprite.Group()
            self.terrain_change_button = pygame.sprite.Group()  # button to change preview map base terrain
            self.feature_change_button = pygame.sprite.Group()  # button to change preview map terrain feature
            self.weather_change_button = pygame.sprite.Group()  # button to change preview map weather
            self.armybuildslot = pygame.sprite.Group()  # slot for putting troop into army preset during preparation mode
            self.uniteditborder = pygame.sprite.Group()  # border that appear when selected sub-subunit
            self.previewleader = pygame.sprite.Group()  # just to make preview leader class has containers
            self.armypresetnamegroup = pygame.sprite.Group()  # preset name list

            # battle object group
            self.battlecamera = pygame.sprite.LayeredUpdates()  # layer drawer game camera, all image pos should be based on the map not screen
            # the camera layer is as followed 0 = terrain map, 1 = dead army, 2 = map special feature, 3 = , 4 = subunit, 5 = sub-subunit,
            # 6 = flying parentunit, 7 = arrow/range, 8 = weather, 9 = weather matter, 10 = ui/button, 11 = subunit inspect, 12 pop up
            self.battleui = pygame.sprite.LayeredUpdates()  # this is layer drawer for ui, all image pos should be based on the screen

            self.unit_updater = pygame.sprite.Group()  # updater for parentunit objects
            self.subunit_updater = pygame.sprite.Group()  # updater for subunit objects
            self.leader_updater = pygame.sprite.Group()  # updater for leader objects
            self.ui_updater = pygame.sprite.Group()  # updater for ui objects
            self.weather_updater = pygame.sprite.Group()  # updater for weather objects
            self.effect_updater = pygame.sprite.Group()  # updater for in-game effect objects (e.g. range attack sprite)

            self.battlemap_base = pygame.sprite.Group()  # base terrain map object
            self.battlemap_feature = pygame.sprite.Group()  # terrain feature map object
            self.battlemap_height = pygame.sprite.Group()  # height map object
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
            self.troopnumbersprite = pygame.sprite.Group()  # troop text number that appear next to parentunit sprite

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

            self.skill_icon = pygame.sprite.Group()  # skill and trait icon objects
            self.effect_icon = pygame.sprite.Group()  # status effect icon objects

            self.battle_menu = pygame.sprite.Group()  # esc menu object
            self.battle_menu_button = pygame.sprite.Group()  # buttons for esc menu object group
            self.escoption_menu_button = pygame.sprite.Group()  # buttons for esc menu option object group
            self.slidermenu = pygame.sprite.Group()  # volume slider in esc option menu

            self.armyselector = pygame.sprite.Group()  # army selector ui
            self.armyicon = pygame.sprite.Group()  # army icon object group in army selector ui

            self.timeui = pygame.sprite.Group()  # time bar ui
            self.timenumber = pygame.sprite.Group()  # number text of in-game time
            self.speednumber = pygame.sprite.Group()  # number text of current game speed

            self.scaleui = pygame.sprite.Group()  # battle scale bar

            self.weathermatter = pygame.sprite.Group()  # sprite of weather effect group such as rain sprite
            self.weathereffect = pygame.sprite.Group()  # sprite of special weather effect group such as fog that cover whole screen
            # ^ End initialise

            # v Assign default groups
            # main menu containers
            gameprepare.Menubutton.containers = self.menu_button
            gameprepare.Menuicon.containers = self.menuicon
            gameprepare.Slidermenu.containers = self.menuslider
            gameprepare.Valuebox.containers = self.valuebox

            gameprepare.Listbox.containers = self.map_listbox, self.troop_listbox, self.popup_listbox
            gameprepare.Namelist.containers = self.mapnamegroup
            gameprepare.Mapshow.containers = self.mapshow
            gameprepare.Teamcoa.containers = self.teamcoa
            gameprepare.Maptitle.containers = self.maptitle
            gameprepare.Mapdescription.containers = self.mapdescription
            gameprepare.Sourcedescription.containers = self.sourcedescription
            gameprepare.Armystat.containers = self.armystat

            gameprepare.Sourcename.containers = self.sourcenamegroup, self.mainui

            gameprepare.Tickbox.containers = self.tickbox

            gamelorebook.SubsectionList.containers = self.lorenamelist
            gamelorebook.SubsectionName.containers = self.subsection_name, self.mainui, self.battleui

            gameui.Uibutton.containers = self.lorebuttonui

            gameunitedit.Previewbox.main_dir = main_dir
            img = load_image("effect.png", "map")  # map special effect image
            gameunitedit.Previewbox.effectimage = img
            gameunitedit.Filterbox.containers = self.filterbox
            gameunitedit.Previewchangebutton.containers = self.terrain_change_button, self.weather_change_button, self.feature_change_button
            gameunitedit.Armybuildslot.containers = self.armybuildslot
            gameunitedit.Previewleader.containers = self.previewleader

            # battle containers
            gamemap.Basemap.containers = self.battlemap_base
            gamemap.Mapfeature.containers = self.battlemap_feature
            gamemap.Mapheight.containers = self.battlemap_height
            gamemap.Beautifulmap.containers = self.showmap, self.battlecamera

            gameunit.Unitarmy.containers = self.unit_updater
            gamesubunit.Subunit.containers = self.subunit_updater, self.subunit, self.battlecamera
            gameleader.Leader.containers = self.armyleader, self.leader_updater
            gameunit.Troopnumber.containers = self.troopnumbersprite, self.effect_updater, self.battlecamera

            gamerangeattack.Rangearrow.containers = self.arrows, self.effect_updater, self.battlecamera
            gameunit.Directionarrow.containers = self.directionarrows, self.effect_updater, self.battlecamera

            gameui.Gameui.containers = self.gameui, self.ui_updater
            gameui.Minimap.containers = self.minimap, self.battleui
            gameui.FPScount.containers = self.battleui
            gameui.Uibutton.containers = self.buttonui, self.lorebuttonui
            gameui.Switchuibutton.containers = self.switchbuttonui, self.ui_updater
            gameui.Selectedsquad.containers = self.inspectselectedborder, self.uniteditborder, self.mainui, self.battleui
            gameui.Skillcardicon.containers = self.skill_icon, self.battleui, self.mainui
            gameui.Effectcardicon.containers = self.effect_icon, self.battleui, self.mainui
            gameui.Eventlog.containers = self.eventlog
            gameui.Armyselect.containers = self.armyselector, self.battleui
            gameui.Armyicon.containers = self.armyicon, self.battleui
            gameui.Timeui.containers = self.timeui, self.battleui
            gameui.Timer.containers = self.timenumber, self.battleui
            gameui.Scaleui.containers = self.scaleui, self.battleui
            gameui.Speednumber.containers = self.speednumber, self.battleui

            gamepopup.TerrainPopup.containers = self.terraincheck
            gamepopup.OnelinePopup.containers = self.buttonnamepopup, self.leaderpopup
            gamepopup.EffecticonPopup.containers = self.effectpopup

            gamedrama.Textdrama.containers = self.textdrama

            gamemenu.Escbox.containers = self.battle_menu
            gamemenu.Escbutton.containers = self.battle_menu_button, self.escoption_menu_button
            gamemenu.Escslider.containers = self.slidermenu
            gamemenu.Escvaluebox.containers = self.valuebox

            gameweather.Mattersprite.containers = self.weathermatter, self.battleui, self.weather_updater
            gameweather.Specialeffect.containers = self.weathereffect, self.battleui, self.weather_updater
            # ^ End assign

            gamelongscript.load_game_data(self)  # obtain game stat data and create lore book object

            self.clock = pygame.time.Clock()
            game_intro(self.screen, self.clock, False)  # run game intro

            # v Background image
            bgdtile = load_image("background.jpg", "ui\\mainmenu_ui").convert()
            bgdtile = pygame.transform.scale(bgdtile, SCREENRECT.size)
            self.background = pygame.Surface(SCREENRECT.size)
            self.background.blit(bgdtile, (0, 0))
            # ^ End background

            # v Create main menu button
            imagelist = load_base_button()
            for index, image in enumerate(imagelist):
                imagelist[index] = pygame.transform.scale(image, (int(image.get_width() * widthadjust),
                                                                  int(image.get_height() * heightadjust)))
            self.preset_map_button = gameprepare.Menubutton(images=imagelist,
                                                            pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 8.5)),
                                                            text="Preset Map")
            self.custom_map_button = gameprepare.Menubutton(images=imagelist,
                                                            pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 7)),
                                                            text="Custom Map")
            self.game_edit_button = gameprepare.Menubutton(images=imagelist,
                                                           pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 5.5)),
                                                           text="Unit Editor")
            self.lore_button = gameprepare.Menubutton(images=imagelist,
                                                      pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 4)),
                                                      text="Encyclopedia")
            self.option_button = gameprepare.Menubutton(images=imagelist,
                                                        pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 2.5)),
                                                        text="Option")
            self.quit_button = gameprepare.Menubutton(images=imagelist, pos=(SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height())),
                                                      text="Quit")
            self.mainmenu_button = (self.preset_map_button, self.custom_map_button, self.game_edit_button,
                                    self.lore_button, self.option_button, self.quit_button)
            # ^ End main menu button

            # v Create battle map menu button
            bottomheight = SCREENRECT.height - imagelist[0].get_height()
            self.select_button = gameprepare.Menubutton(images=imagelist, pos=(SCREENRECT.width - imagelist[0].get_width(), bottomheight),
                                                        text="Select")
            self.start_button = gameprepare.Menubutton(images=imagelist, pos=(SCREENRECT.width - imagelist[0].get_width(), bottomheight),
                                                       text="Start")
            self.map_back_button = gameprepare.Menubutton(images=imagelist,
                                                          pos=(SCREENRECT.width - (SCREENRECT.width - imagelist[0].get_width()), bottomheight),
                                                          text="Back")
            self.map_select_button = (self.select_button, self.map_back_button)
            self.battle_setup_button = (self.start_button, self.map_back_button)

            imgs = load_images(["ui", "mapselect_ui"], loadorder=False)
            self.map_listbox = gameprepare.Listbox((SCREENRECT.width / 25, SCREENRECT.height / 20), imgs[0])
            self.map_scroll = gameui.Uiscroller(self.map_listbox.rect.topright, self.map_listbox.image.get_height(),
                                                self.map_listbox.maxshowlist, layer=14)  # scroller bar for map list

            self.source_listbox = gameprepare.Sourcelistbox((0, 0), imgs[1])  # source list ui box
            self.map_optionbox = gameprepare.Mapoptionbox((SCREENRECT.width, 0), imgs[1], 0)  # ui box for battle option during preparation screen

            self.tickbox_enactment = gameprepare.Tickbox((self.map_optionbox.rect.bottomright[0] / 1.2, self.map_optionbox.rect.bottomright[1] / 4),
                                                         imgs[5], imgs[6], "enactment")
            self.tickbox.add(self.tickbox_enactment)
            if self.enactment:
                self.tickbox_enactment.changetick(True)

            gameprepare.Mapdescription.image = imgs[2]
            gameprepare.Sourcedescription.image = imgs[3]
            gameprepare.Armystat.image = imgs[4]

            self.current_map_row = 0
            self.current_map_select = 0

            self.current_source_row = 0

            self.current_troop_row = 0
            self.current_army_row = 0

            # ^ End battle map menu button

            # v Create subunit editor button and ui

            self.unit_edit_button = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 4)),
                                                           text="Army Editor")
            self.subunit_create_button = gameprepare.Menubutton(imagelist,
                                                                (SCREENRECT.width / 2, SCREENRECT.height - (imagelist[0].get_height() * 2.5)),
                                                                text="Troop Creator")
            self.editor_back_button = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height - imagelist[0].get_height()),
                                                             text="Back")
            self.editor_button = (self.unit_edit_button, self.subunit_create_button, self.editor_back_button)
            # ^ End subunit editor

            # v Army editor
            boximg = load_image("army_presetbox.png", "ui\\mainmenu_ui").convert()
            self.army_listbox = gameprepare.Listbox((0, SCREENRECT.height / 2.2), boximg)  # box for showing army preset list
            self.army_presetname_scroll = gameui.Uiscroller(self.army_listbox.rect.topright, self.army_listbox.image.get_height(),
                                                            self.army_listbox.maxshowlist, layer=14)  # preset name scroll

            self.troop_listbox = gameprepare.Listbox((SCREENRECT.width / 1.19, 0), imgs[0])

            self.troop_scroll = gameui.Uiscroller(self.troop_listbox.rect.topright, self.troop_listbox.image.get_height(),
                                                  self.troop_listbox.maxshowlist, layer=14)
            self.army_delete_button = gameprepare.Menubutton(images=imagelist,
                                                           pos=(imagelist[0].get_width() / 2, bottomheight),
                                                           text="Delete")
            self.army_save_button = gameprepare.Menubutton(images=imagelist,
                                                           pos=((SCREENRECT.width - (SCREENRECT.width - (imagelist[0].get_width() * 1.7))),
                                                                bottomheight),
                                                           text="Save")

            self.popup_listbox = gameprepare.Listbox((0, 0), boximg, 15)  # popup listbox need to be in higher layer
            self.popup_listbox.maxshowlist = 9  # box is smaller than usual
            self.popup_listscroll = gameui.Uiscroller(self.popup_listbox.rect.topright,
                                                      self.popup_listbox.image.get_height(),
                                                      self.popup_listbox.maxshowlist,
                                                      layer=14)

            boximg = load_image("mapchange.png", "ui\\mainmenu_ui").convert()
            self.terrain_change_button = gameunitedit.Previewchangebutton((SCREENRECT.width / 3, SCREENRECT.height), boximg,
                                                                          "Temperate")  # start with temperate terrain
            self.feature_change_button = gameunitedit.Previewchangebutton((SCREENRECT.width / 2, SCREENRECT.height), boximg,
                                                                          "Plain")  # start with plain feature
            self.weather_change_button = gameunitedit.Previewchangebutton((SCREENRECT.width / 1.5, SCREENRECT.height), boximg,
                                                                          "Light Sunny")  # start with light sunny

            gameunitedit.Armybuildslot.squadwidth = self.squadwidth
            gameunitedit.Armybuildslot.squadheight = self.squadheight
            startpos = [(SCREENRECT.width / 2) - (self.squadwidth * 5),
                        (SCREENRECT.height / 2) - (self.squadheight * 4)]
            self.armyedit_gameid = 0
            self.armyedit_team1id = 0
            self.armyedit_team2id = 0
            self.makearmyslot(self.armyedit_gameid, 1, self.armyedit_team1id, range(0, 64), startpos)  # make player army slot

            self.team1previewarmy = np.array([[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                                              [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
                                              [0, 0, 0, 0, 0, 0, 0, 0]])  # player teat army subunit list

            self.previewleader = [gameunitedit.Previewleader(1, 0, 0, self.leader_stat),
                                       gameunitedit.Previewleader(1, 0, 1, self.leader_stat),
                                       gameunitedit.Previewleader(1, 0, 2, self.leader_stat),
                                       gameunitedit.Previewleader(1, 0, 3, self.leader_stat)]
            self.leader_updater.remove(*self.previewleader)

            boximg = load_image("filterbox.png", "ui\\mainmenu_ui").convert()
            self.filterbox = gameunitedit.Filterbox((SCREENRECT.width / 2.5, 0), boximg)

            img1 = load_image("team1_button.png", "ui\\mainmenu_ui").convert()
            img2 = load_image("team2_button.png", "ui\\mainmenu_ui").convert()
            self.teamchange_button = gameui.Switchuibutton(self.filterbox.rect.topleft[0] + 220, self.filterbox.rect.topleft[1] + 30, [img1, img2])
            img1 = load_image("show_button.png", "ui\\mainmenu_ui").convert()
            img2 = load_image("hide_button.png", "ui\\mainmenu_ui").convert()
            self.slotdisplay_button = gameui.Switchuibutton(self.filterbox.rect.topleft[0] + 80, self.filterbox.rect.topleft[1] + 30, [img1, img2])
            img1 = load_image("deploy_button.png", "ui\\mainmenu_ui").convert()
            self.deploy_button = gameui.Uibutton(self.filterbox.rect.topleft[0] + 150, self.filterbox.rect.topleft[1] + 90, img1, 0)
            # ^ End army editor

            # v Input box popup
            input_ui_img = load_image("inputui.png", "ui\\mainmenu_ui")
            self.inputui = gameprepare.Inputui(input_ui_img, (SCREENRECT.width / 2, SCREENRECT.height / 2))  # user text input ui box popup
            self.input_ok_button = gameprepare.Menubutton(images=imagelist,
                                                          pos=(self.inputui.rect.midleft[0] + imagelist[0].get_width(),
                                                               self.inputui.rect.midleft[1] + imagelist[0].get_height()),
                                                          text="Done")
            self.input_cancel_button = gameprepare.Menubutton(images=imagelist,
                                                              pos=(self.inputui.rect.midright[0] - imagelist[0].get_width(),
                                                                   self.inputui.rect.midright[1] + imagelist[0].get_height()),
                                                              text="Cancel")
            self.input_button = (self.input_ok_button, self.input_cancel_button)
            self.input_box = gameprepare.Inputbox(self.inputui.rect.center, self.inputui.image.get_width())  # user text input box

            self.inputui_pop = (self.inputui, self.input_box, self.input_ok_button, self.input_cancel_button)
            # ^ End input box popup

            # v profile box
            self.profile_name = Profilename
            img = load_image("profile_box.png", "ui\\mainmenu_ui")
            self.profile_box = gameprepare.Profilebox(img, (ScreenWidth, 0),
                                                      self.profile_name)  # profile name box at top right of screen at main menu screen
            # ^ End profile box

            # v Create option menu button and icon
            self.back_button = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height / 1.2), text="BACK")

            # Resolution changing bar that fold out the list when clicked
            img = load_image("scroll_normal.jpg", "ui\\mainmenu_ui")
            img2 = img
            img3 = load_image("scroll_click.jpg", "ui\\mainmenu_ui")
            imagelist = [img, img2, img3]
            self.resolution_scroll = gameprepare.Menubutton(imagelist, (SCREENRECT.width / 2, SCREENRECT.height / 2.3),
                                                            text=str(ScreenWidth) + " x " + str(ScreenHeight), size=16)
            resolutionlist = ["1920 x 1080", "1600 x 900", "1366 x 768", "1280 x 720", "1024 x 768"]
            self.resolutionbar = makebarlist(listtodo=resolutionlist, menuimage=self.resolution_scroll)
            img = load_image("resolution_icon.png", "ui\\mainmenu_ui")
            self.resolutionicon = gameprepare.Menuicon([img], (self.resolution_scroll.pos[0] - (self.resolution_scroll.pos[0] / 4.5),
                                                               self.resolution_scroll.pos[1]), imageresize=50)
            # End resolution

            # Volume change scroller bar
            img = load_image("scroller.png", "ui\\mainmenu_ui")
            img2 = load_image("scoll_button_normal.png", "ui\\mainmenu_ui")
            img3 = load_image("scoll_button_click.png", "ui\\mainmenu_ui")
            img4 = load_image("numbervalue_icon.jpg", "ui\\mainmenu_ui")
            self.volumeslider = gameprepare.Slidermenu(barimage=img, buttonimage=[img2, img3], pos=(SCREENRECT.width / 2, SCREENRECT.height / 3),
                                                       value=Soundvolume)
            self.valuebox = [gameprepare.Valuebox(img4, (self.volumeslider.rect.topright[0] * 1.1, self.volumeslider.rect.topright[1]), Soundvolume)]
            img = load_image("volume_icon.png", "ui\\mainmenu_ui")
            self.volumeicon = gameprepare.Menuicon([img], (self.volumeslider.pos[0] - (self.volumeslider.pos[0] / 4.5), self.volumeslider.pos[1]),
                                                   imageresize=50)
            # End volume change

            self.optioniconlist = (self.resolutionicon, self.volumeicon)
            self.optionmenu_button = (self.back_button, self.resolution_scroll)
            self.optionmenu_slider = self.volumeslider
            # ^ End option menu button

            pygame.display.set_caption("Dream Decision")  # set the game name on program border/tab
            pygame.mouse.set_visible(1)  # set mouse as visible

            # v Music player
            if pygame.mixer:
                self.mixervolume = float(Soundvolume / 100)
                pygame.mixer.music.set_volume(self.mixervolume)
                self.SONG_END = pygame.USEREVENT + 1
                self.musiclist = glob.glob(main_dir + "/data/sound/music/*.mp3")
                pygame.mixer.music.load(self.musiclist[0])
                pygame.mixer.music.play(-1)
            # ^ End music

            self.mainui.remove(*self.menu_button)  # remove all button from drawing
            self.menu_button.remove(*self.menu_button)  # remove all button at the start and add later depending on menu_state
            self.menu_button.add(*self.mainmenu_button)  # add only main menu button back
            self.mainui.add(*self.menu_button, self.profile_box)
            self.menu_state = "mainmenu"
            self.textinputpopup = None  # popup for texting text input state
            self.choosingfaction = True  # swap list between faction and subunit, always start with choose faction first as true

            self.battlegame = gamebattle.Battle(self, self.winstyle)

        def backtomainmenu(self):
            self.menu_state = "mainmenu"

            self.mainui.remove(*self.menu_button)

            self.menu_button.remove(*self.menu_button)
            self.menu_button.add(*self.mainmenu_button)

            self.mainui.add(*self.menu_button, self.profile_box)

        def setuplist(self, itemclass, currentrow, showlist, itemgroup, box, uiclass, screenscale=False, layer=15):
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
                    itemgroup.add(itemclass(box, (pos[0] + column, pos[1] + row), item, layer=layer))  # add new subsection sprite to group
                    row += (30 * heightadjust)  # next row
                    if len(itemgroup) > box.maxshowlist:
                        break  # will not generate more than space allowed

            uiclass.add(*itemgroup)

        def readmapdata(self, maplist, file):
            if self.menu_state == "presetselect" or self.lastselect == "presetselect":
                data = csv_read(file, ["data", "ruleset", self.rulesetfolder.strip("/"), "map", maplist[self.current_map_select]])
            else:
                data = csv_read(file, ["data", "ruleset", self.rulesetfolder.strip("/"), "map/custom", maplist[self.current_map_select]])
            return data

        def maketeamcoa(self, data, uiclass, oneteam=False, team1setpos=(SCREENRECT.width / 2 - (300 * widthadjust), SCREENRECT.height / 3)):
            for team in self.teamcoa:
                team.kill()
                del team

            # position = self.mapshow[0].get_rect()
            self.teamcoa.add(gameprepare.Teamcoa(team1setpos, self.coa[data[0]],
                                                 1, self.allfaction.faction_list[data[0]][0]))  # team 1

            if oneteam is False:
                self.teamcoa.add(gameprepare.Teamcoa((SCREENRECT.width / 2 + (300 * widthadjust), SCREENRECT.height / 3), self.coa[data[1]],
                                                     2, self.allfaction.faction_list[data[1]][0]))  # team 2
            uiclass.add(self.teamcoa)

        def makemap(self, mapfolderlist, maplist):
            # v Create map preview image
            for thismap in self.mapshow:
                thismap.kill()
                del thismap
            if self.menu_state == "presetselect":
                imgs = load_images(["ruleset", self.rulesetfolder.strip("/"), "map", mapfolderlist[self.current_map_select]], loadorder=False)
            else:
                imgs = load_images(["ruleset", self.rulesetfolder.strip("/"), "map/custom", mapfolderlist[self.current_map_select]], loadorder=False)
            self.mapshow.add(gameprepare.Mapshow((SCREENRECT.width / 2, SCREENRECT.height / 3), imgs[0], imgs[1]))
            self.mainui.add(self.mapshow)
            # ^ End map preview

            # v Create map title at the top
            for name in self.maptitle:
                name.kill()
                del name
            self.maptitle.add(gameprepare.Maptitle(maplist[self.current_map_select], (SCREENRECT.width / 2, 0)))
            self.mainui.add(self.maptitle)
            # ^ End map title

            # v Create map description
            data = self.readmapdata(mapfolderlist, "info.csv")
            description = [list(data.values())[1][0], list(data.values())[1][1]]
            for desc in self.mapdescription:
                desc.kill()
                del desc
            self.mapdescription.add(gameprepare.Mapdescription((SCREENRECT.width / 2, SCREENRECT.height / 1.3), description))
            self.mainui.add(self.mapdescription)
            # ^ End map description

            self.maketeamcoa([list(data.values())[1][2], list(data.values())[1][3]], self.mainui)

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
            unitmapinfo = self.readmapdata(openfolder, "unit_pos" + str(self.mapsource) + ".csv")

            team1pos = {row[8]: [int(item) for item in row[8].split(",")] for row in list(unitmapinfo.values()) if row[15] == 1}
            team2pos = {row[8]: [int(item) for item in row[8].split(",")] for row in list(unitmapinfo.values()) if row[15] == 2}
            for thismap in self.mapshow:
                thismap.changemode(1, team1poslist=team1pos, team2poslist=team2pos)

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
                    for item in smallrow.split(","):
                        listadd.append(int(item))

                for item in row[9].split(","):
                    if row[15] == 1:
                        team1commander.append(int(item))
                    elif row[15] == 2:
                        team2commander.append(int(item))

            teamtotal = [0, 0]  # total troop number in army
            trooptypelist = [[0, 0, 0, 0], [0, 0, 0, 0]]  # total number of each troop type
            leadernamelist = (team1commander, team2commander)
            armyteamlist = (team1pos, team2pos)  # for finding how many subunit in each team

            armylooplist = (team1army, team2army)
            for index, team in enumerate(armylooplist):
                for unit in team:
                    if unit != 0:
                        teamtotal[index] += int(self.gameunitstat.unit_list[unit][27] * scalevalue[index])
                        trooptype = 0
                        if self.gameunitstat.unit_list[unit][22] != [1, 0] \
                                and self.gameunitstat.unit_list[unit][8] < self.gameunitstat.unit_list[unit][12]:  # range sub-unit
                            trooptype += 1  # range weapon and accuracy higher than melee attack
                        if self.gameunitstat.unit_list[unit][29] != [1, 0, 1]:  # cavalry
                            trooptype += 2
                        trooptypelist[index][trooptype] += int(self.gameunitstat.unit_list[unit][27] * scalevalue[index])
                trooptypelist[index].append(len(armyteamlist[index]))

            armylooplist = ["{:,}".format(troop) + " Troops" for troop in teamtotal]
            armylooplist = [self.leader_stat.leader_list[leadernamelist[index][0]][0] + ": " + troop for index, troop in enumerate(armylooplist)]

            for index, army in enumerate(self.armystat):
                army.addstat(trooptypelist[index], armylooplist[index])

        def listscroll(self, mouse_scrollup, mouse_scrolldown, scroll, listbox, currentrow, namelist, namegroup, uiclass):
            if mouse_scrollup:
                currentrow -= 1
                if currentrow < 0:
                    currentrow = 0
                else:
                    self.setuplist(gameprepare.Namelist, currentrow, namelist, namegroup, listbox, uiclass)
                    scroll.changeimage(newrow=currentrow, logsize=len(namelist))

            elif mouse_scrolldown:
                currentrow += 1
                if currentrow + listbox.maxshowlist - 1 < len(namelist):
                    self.setuplist(gameprepare.Namelist, currentrow, namelist, namegroup, listbox, uiclass)
                    scroll.changeimage(newrow=currentrow, logsize=len(namelist))
                else:
                    currentrow -= 1
            return currentrow

        def makearmyslot(self, gameid, team, armyid, rangetorun, startpos, columnonly=False):
            width, height = 0, 0
            squadnum = 0  # Number of subunit based on the position in row and column
            for squad in rangetorun:  # generate player army slot for filling troop into preview army
                if columnonly is False:
                    width += self.squadwidth
                    self.armybuildslot.add(gameunitedit.Armybuildslot(gameid, team, armyid, (width, height), startpos))
                    squadnum += 1
                    if squadnum == 8:  # Pass the last subunit in the row, go to the next one
                        width = 0
                        height += self.squadheight
                        squadnum = 0
                else:
                    height += self.squadheight
                    self.armybuildslot.add(gameunitedit.Armybuildslot(gameid, team, armyid, (width, height), startpos))
                    squadnum += 1
                gameid += 1
            return gameid

        def popout_lorebook(self, section, gameid):
            # v Seem like encyclopedia in battle cause container to change allui in main to gamebattle one, change back with this
            gamelorebook.SubsectionName.containers = self.subsection_name, self.mainui
            # ^ End container change

            self.beforelorestate = self.menu_state
            self.menu_state = "encyclopedia"
            self.mainui.add(self.lorebook, self.lorescroll, self.lorenamelist, *self.lorebuttonui)  # add sprite related to encyclopedia
            self.lorebook.change_section(section, self.lorenamelist, self.subsection_name, self.lorescroll,
                                         self.pagebutton, self.mainui)
            self.lorebook.change_subsection(gameid, self.pagebutton, self.mainui)
            self.lorescroll.changeimage(newrow=self.lorebook.current_subsection_row)

        def run(self):
            while True:
                # v Get user input
                mouse_up = False
                mouse_down = False
                mouse_right = False
                mouse_scrolldown = False
                mouse_scrollup = False
                keypress = None
                esc_press = False
                keystate = pygame.key.get_pressed()
                for event in pygame.event.get():
                    if self.textinputpopup is not None:  # event update to input box
                        self.input_box.userinput(event)

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

                    if event.type == QUIT or self.quit_button.event or (esc_press and self.menu_state == "mainmenu"):
                        return

                self.mousepos = pygame.mouse.get_pos()
                # ^ End user input

                self.screen.blit(self.background, (0, 0))  # blit blackground over instead of clear() to reset screen

                if self.textinputpopup is not None:  # currently have input text pop up on screen, stop everything else until done
                    for button in self.input_button:
                        button.update(self.mousepos, mouse_up, mouse_down)

                    if self.input_ok_button.event:
                        self.input_ok_button.event = False

                        if self.textinputpopup == "profile_name":
                            self.profile_name = self.input_box.text
                            self.profile_box.changename(self.profile_name)

                            editconfig("DEFAULT", "playername", self.profile_name, "configuration.ini", config)

                        self.input_box.textstart("")
                        self.textinputpopup = None
                        self.mainui.remove(*self.inputui_pop)

                    elif self.input_cancel_button.event or esc_press:
                        self.input_cancel_button.event = False
                        self.input_box.textstart("")
                        self.textinputpopup = None
                        self.mainui.remove(*self.inputui_pop)

                elif self.textinputpopup is None:
                    self.menu_button.update(self.mousepos, mouse_up, mouse_down)
                    if self.menu_state == "mainmenu":

                        if self.preset_map_button.event:  # preset map list menu
                            self.menu_state = "presetselect"
                            self.lastselect = self.menu_state
                            self.preset_map_button.event = False
                            self.mainui.remove(*self.menu_button, self.profile_box)
                            self.menu_button.remove(*self.menu_button)

                            self.setuplist(gameprepare.Namelist, self.current_map_row, self.maplist, self.mapnamegroup, self.map_listbox, self.mainui)
                            self.makemap(self.mapfoldername, self.maplist)

                            self.menu_button.add(*self.map_select_button)
                            self.mainui.add(*self.map_select_button, self.map_listbox, self.maptitle, self.map_scroll)

                        elif self.custom_map_button.event:  # custom map list menu
                            self.menu_state = "customselect"
                            self.lastselect = self.menu_state
                            self.custom_map_button.event = False
                            self.mainui.remove(*self.menu_button, self.profile_box)
                            self.menu_button.remove(*self.menu_button)

                            self.setuplist(gameprepare.Namelist, self.current_map_row, self.mapcustomlist, self.mapnamegroup, self.map_listbox, self.mainui)
                            self.makemap(self.mapcustomfoldername, self.mapcustomlist)

                            self.menu_button.add(*self.map_select_button)
                            self.mainui.add(*self.map_select_button, self.map_listbox, self.maptitle, self.map_scroll)

                        elif self.game_edit_button.event:  # custom subunit/sub-subunit editor menu
                            self.menu_state = "gamecreator"
                            self.game_edit_button.event = False
                            self.mainui.remove(*self.menu_button, self.profile_box)
                            self.menu_button.remove(*self.menu_button)

                            self.menu_button.add(*self.editor_button)
                            self.mainui.add(*self.editor_button)

                        elif self.option_button.event:  # change main menu to option menu
                            self.menu_state = "option"
                            self.option_button.event = False
                            self.mainui.remove(*self.menu_button, self.profile_box)
                            self.menu_button.remove(*self.menu_button)

                            self.menu_button.add(*self.optionmenu_button)
                            self.mainui.add(*self.menu_button, self.optionmenu_slider, self.valuebox)
                            self.mainui.add(*self.optioniconlist)

                        elif self.lore_button.event:  # open encyclopedia
                            # v Seem like encyclopedia in battle cause container to change allui in main to gamebattle one, change back with this
                            gamelorebook.SubsectionName.containers = self.subsection_name, self.mainui
                            # ^ End container change

                            self.beforelorestate = self.menu_state
                            self.menu_state = "encyclopedia"
                            self.mainui.add(self.lorebook, self.lorenamelist, *self.lorebuttonui,
                                            self.lorescroll)  # add sprite related to encyclopedia
                            self.lorebook.change_section(0, self.lorenamelist, self.subsection_name, self.lorescroll, self.pagebutton, self.mainui)
                            self.lore_button.event = False

                        elif mouse_up and self.profile_box.rect.collidepoint(self.mousepos):
                            self.textinputpopup = "profile_name"
                            self.input_box.textstart(self.profile_name)
                            self.inputui.changeinstruction("Profile Name:")
                            self.mainui.add(self.inputui_pop)

                    elif self.menu_state == "presetselect" or self.menu_state == "customselect":
                        if mouse_up or mouse_down:
                            if mouse_up:
                                for index, name in enumerate(self.mapnamegroup):  # user click on map name, change map
                                    if name.rect.collidepoint(self.mousepos):
                                        self.current_map_select = index
                                        if self.menu_state == "presetselect":  # make new map image
                                            self.makemap(self.mapfoldername, self.maplist)
                                        else:
                                            self.makemap(self.mapcustomfoldername, self.mapcustomlist)
                                        break

                            if self.map_scroll.rect.collidepoint(self.mousepos):  # click on subsection list scroller
                                self.current_map_row = self.map_scroll.update(
                                    self.mousepos)  # update the scroller and get new current subsection
                                self.setuplist(gameprepare.Namelist, self.current_map_row, self.maplist, self.mapnamegroup, self.map_listbox, self.mainui)

                        if self.map_listbox.rect.collidepoint(self.mousepos):
                            self.current_map_row = self.listscroll(mouse_scrollup, mouse_scrolldown, self.map_scroll, self.map_listbox,
                                                                   self.current_map_row, self.maplist, self.mapnamegroup, self.mainui)

                        if self.map_back_button.event or esc_press:
                            self.map_back_button.event = False
                            self.current_map_row = 0
                            self.current_map_select = 0

                            self.mainui.remove(self.map_listbox, self.mapshow, self.map_scroll, self.mapdescription,
                                               self.teamcoa, self.maptitle)

                            for group in (self.mapshow, self.mapnamegroup, self.teamcoa):  # remove no longer related sprites in group
                                for stuff in group:
                                    stuff.kill()
                                    del stuff

                            self.backtomainmenu()

                        elif self.select_button.event:  # select this map, go to prepare setup
                            self.current_source_row = 0
                            self.menu_state = "battlemapset"
                            self.select_button.event = False

                            self.mainui.remove(*self.map_select_button, self.map_listbox, self.map_scroll, self.mapdescription)
                            self.menu_button.remove(*self.map_select_button)

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
                                self.sourcelist = self.readmapdata(openfolder, "source.csv")
                                self.sourcenamelist = [value[0] for value in list(self.sourcelist.values())[1:]]
                                self.sourcescaletext = [value[1] for value in list(self.sourcelist.values())[1:]]
                                self.sourcescale = [(float(value[2]), float(value[3]), float(value[4]), float(value[5])) for value in
                                                    list(self.sourcelist.values())[1:]]
                                self.sourcetext = [value[-1] for value in list(self.sourcelist.values())[1:]]
                            except Exception:  # no source.csv make empty list
                                self.sourcenamelist = [""]
                                self.sourcescaletext = [""]
                                self.sourcescale = [""]
                                self.sourcetext = [""]

                            self.setuplist(gameprepare.Sourcename, self.current_source_row, self.sourcenamelist, self.sourcenamegroup,
                                           self.source_listbox, self.mainui)

                            self.sourcescroll = gameui.Uiscroller(self.source_listbox.rect.topright, self.source_listbox.image.get_height(),
                                                                  self.source_listbox.maxshowlist, layer=14)  # scroller bar for source list

                            for index, team in enumerate(self.teamcoa):
                                if index == 0:
                                    self.armystat.add(gameprepare.Armystat((team.rect.bottomleft[0], SCREENRECT.height / 1.5)))  # left army stat
                                else:
                                    self.armystat.add(gameprepare.Armystat((team.rect.bottomright[0], SCREENRECT.height / 1.5)))  # right army stat

                            self.changesource([self.sourcescaletext[self.mapsource], self.sourcetext[self.mapsource]],
                                              self.sourcescale[self.mapsource])

                            self.menu_button.add(*self.battle_setup_button)
                            self.mainui.add(*self.battle_setup_button, self.map_optionbox, self.tickbox_enactment, self.source_listbox,
                                            self.sourcescroll, self.armystat)

                    elif self.menu_state == "battlemapset":
                        if mouse_up or mouse_down:
                            if mouse_up:
                                for thisteam in self.teamcoa:  # User select any team by clicking on coat of arm
                                    if thisteam.rect.collidepoint(self.mousepos):
                                        self.teamselected = thisteam.team
                                        thisteam.selected = True
                                        thisteam.changeselect()

                                        # Reset team selected on team user not currently selected
                                        for thisteam2 in self.teamcoa:
                                            if self.teamselected != thisteam2.team and thisteam2.selected:
                                                team.selected = False
                                                team.changeselect()

                                        break

                                for index, name in enumerate(self.sourcenamegroup):  # user select source
                                    if name.rect.collidepoint(self.mousepos):  # click on source name
                                        self.mapsource = index
                                        self.changesource([self.sourcescaletext[self.mapsource], self.sourcetext[self.mapsource]],
                                                          self.sourcescale[self.mapsource])
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
                                self.current_source_row = self.sourcescroll.update(
                                    self.mousepos)  # update the scroller and get new current subsection
                                self.setuplist(gameprepare.Namelist, self.current_source_row, self.sourcelist, self.sourcenamegroup,
                                               self.source_listbox, self.mainui)
                        if self.source_listbox.rect.collidepoint(self.mousepos):
                            self.current_source_row = self.listscroll(mouse_scrollup, mouse_scrolldown, self.sourcescroll, self.source_listbox,
                                                                      self.current_source_row, self.sourcelist, self.sourcenamegroup, self.mainui)

                        if self.map_back_button.event or esc_press:
                            self.menu_state = self.lastselect
                            self.map_back_button.event = False
                            self.mainui.remove(*self.menu_button, self.map_listbox, self.map_optionbox, self.tickbox_enactment,
                                               self.source_listbox, self.sourcescroll, self.sourcedescription)
                            self.menu_button.remove(*self.menu_button)

                            # v Reset selected team
                            for team in self.teamcoa:
                                team.selected = False
                                team.changeselect()
                            self.teamselected = 1
                            # ^ End reset selected team

                            self.mapsource = 0
                            for thismap in self.mapshow:
                                thismap.changemode(0)  # revert map preview back to without army dot

                            for group in (self.sourcenamegroup, self.armystat):
                                for stuff in group:  # remove map name item
                                    stuff.kill()
                                    del stuff

                            if self.menu_state == "presetselect":  # regenerate map name list
                                self.setuplist(gameprepare.Namelist, self.current_map_row, self.maplist, self.mapnamegroup, self.map_listbox, self.mainui)
                            else:
                                self.setuplist(gameprepare.Namelist, self.current_map_row, self.mapcustomlist, self.mapnamegroup, self.map_listbox, self.mainui)

                            self.menu_button.add(*self.map_select_button)
                            self.mainui.add(*self.map_select_button, self.map_listbox, self.map_scroll, self.mapdescription)

                        elif self.start_button.event:  # start game button
                            self.start_button.event = False
                            self.battlegame.preparenewgame(self.ruleset, self.rulesetfolder, self.teamselected, self.enactment,
                                                           self.mapfoldername[self.current_map_select], self.mapsource,
                                                           self.sourcescale[self.mapsource], "battle")
                            self.battlegame.rungame()
                            gc.collect()  # collect no longer used object in previous battle from memory

                    elif self.menu_state == "gamecreator":
                        if self.editor_back_button.event or esc_press:
                            self.editor_back_button.event = False
                            self.backtomainmenu()

                        elif self.unit_edit_button.event:
                            self.unit_edit_button.event = False
                            self.battlegame.preparenewgame(self.ruleset, self.rulesetfolder, 1, True, None, 1, (1,1,1,1), "uniteditor")
                            self.battlegame.rungame()

                    elif self.menu_state == "option":
                        for bar in self.resolutionbar:  # loop to find which resolution bar is selected, this happen outside of clicking check below
                            if bar.event:
                                bar.event = False

                                self.resolution_scroll.changestate(bar.text)  # change button value based on new selected value
                                resolutionchange = bar.text.split()
                                self.new_screen_width = resolutionchange[0]
                                self.new_screen_height = resolutionchange[2]

                                editconfig("DEFAULT", "ScreenWidth", self.new_screen_width, "configuration.ini", config)
                                editconfig("DEFAULT", "ScreenHeight", self.new_screen_height, "configuration.ini", config)
                                self.screen = pygame.display.set_mode(SCREENRECT.size, self.winstyle | pygame.RESIZABLE, self.bestdepth)

                                self.menu_button.remove(self.resolutionbar)

                                break

                        if self.back_button.event or esc_press:  # back to main menu
                            self.back_button.event = False

                            self.mainui.remove(*self.optioniconlist, self.optionmenu_slider, self.valuebox)

                            self.backtomainmenu()

                        if mouse_up or mouse_down:
                            self.mainui.remove(self.resolutionbar)

                            if self.resolution_scroll.rect.collidepoint(self.mousepos):  # click on resolution bar
                                if self.resolutionbar in self.mainui:  # remove the bar list if click again
                                    self.mainui.remove(self.resolutionbar)
                                    self.menu_button.remove(self.resolutionbar)
                                else:  # add bar list
                                    self.mainui.add(self.resolutionbar)
                                    self.menu_button.add(self.resolutionbar)

                            elif self.volumeslider.rect.collidepoint(self.mousepos) and (mouse_down or mouse_up):  # mouse click on slider bar
                                self.volumeslider.update(self.mousepos, self.valuebox[0])  # update slider button based on mouse value
                                self.mixervolume = float(self.volumeslider.value / 100)  # for now only music volume slider exist
                                editconfig("DEFAULT", "SoundVolume", str(self.volumeslider.value), "configuration.ini", config)
                                pygame.mixer.music.set_volume(self.mixervolume)

                    elif self.menu_state == "encyclopedia":
                        if mouse_up or mouse_down:  # mouse down (hold click) only for subsection listscroller
                            if mouse_up:
                                for button in self.lorebuttonui:
                                    if button in self.mainui and button.rect.collidepoint(self.mousepos):  # click button
                                        if button.event in range(0, 11):  # section button
                                            self.lorebook.change_section(button.event, self.lorenamelist, self.subsection_name, self.lorescroll,
                                                                         self.pagebutton, self.mainui)  # change to section of that button

                                        elif button.event == 19:  # Close button
                                            self.mainui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll,
                                                               self.lorenamelist)  # remove enclycopedia related sprites
                                            for name in self.subsection_name:  # remove subsection name
                                                name.kill()
                                                del name
                                            self.menu_state = self.beforelorestate  # change menu back to default 0

                                        elif button.event == 20:  # Previous page button
                                            self.lorebook.change_page(self.lorebook.page - 1, self.pagebutton, self.mainui)  # go back 1 page

                                        elif button.event == 21:  # Next page button
                                            self.lorebook.change_page(self.lorebook.page + 1, self.pagebutton, self.mainui)  # go forward 1 page

                                        break  # found clicked button, break loop

                                for name in self.subsection_name:
                                    if name.rect.collidepoint(self.mousepos):  # click on subsection name
                                        self.lorebook.change_subsection(name.subsection, self.pagebutton, self.mainui)  # change subsection
                                        break  # found clicked subsection, break loop

                            if self.lorescroll.rect.collidepoint(self.mousepos):  # click on subsection list scroller
                                self.lorebook.current_subsection_row = self.lorescroll.update(
                                    self.mousepos)  # update the scroller and get new current subsection
                                self.lorebook.setup_subsection_list(self.lorenamelist, self.subsection_name)  # update subsection name list

                        elif mouse_scrollup:
                            if self.lorenamelist.rect.collidepoint(self.mousepos):  # Scrolling at lore book subsection list
                                self.lorebook.current_subsection_row -= 1
                                if self.lorebook.current_subsection_row < 0:
                                    self.lorebook.current_subsection_row = 0
                                else:
                                    self.lorebook.setup_subsection_list(self.lorenamelist, self.subsection_name)
                                    self.lorescroll.changeimage(newrow=self.lorebook.current_subsection_row)

                        elif mouse_scrolldown:
                            if self.lorenamelist.rect.collidepoint(self.mousepos):  # Scrolling at lore book subsection list
                                self.lorebook.current_subsection_row += 1
                                if self.lorebook.current_subsection_row + self.lorebook.max_subsection_show - 1 < self.lorebook.logsize:
                                    self.lorebook.setup_subsection_list(self.lorenamelist, self.subsection_name)
                                    self.lorescroll.changeimage(newrow=self.lorebook.current_subsection_row)
                                else:
                                    self.lorebook.current_subsection_row -= 1

                        elif esc_press:
                            self.mainui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll,
                                               self.lorenamelist)  # remove enclycopedia related sprites
                            for name in self.subsection_name:  # remove subsection name
                                name.kill()
                                del name
                            self.menu_state = "mainmenu"  # change menu back to default 0

                self.mainui.draw(self.screen)
                pygame.display.update()
                self.clock.tick(60)

            if pygame.mixer:
                pygame.mixer.music.fadeout(1000)

            pygame.time.wait(1000)
            pygame.quit()
            sys.exit()


    if __name__ == "__main__":
        runmenu = Mainmenu()
        runmenu.run()

except Exception:  # Save error output to txt file
    traceback.print_exc()
    f = open("error_report.txt", "w")
    sys.stdout = f
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    print("".join("!! " + line for line in lines))  # Log it or whatever here
    f.close()
