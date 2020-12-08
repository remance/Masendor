"""
## Known problem
Hitbox still behave weirdly in melee combat (sometimes combatprepare is call for side before front)
autoplacement of 2 units somehow allow the other unit that stop from retreat to auto place to the enemy side already occupied
Optimise list
melee combat need to be optimised more
change all percentage calculation to float instead of int/100 if possible. Especially number from csv file
remove index and change call to the sprite itself
"""

import datetime
import glob
import random
import csv
import numpy as np
import pygame
import sys
import pygame.freetype
from pygame.locals import *
from pygame.transform import scale
import main
from gamescript import gamesquad, gamebattalion, gameui, gameleader, gamemap, gamecamera, rangeattack, gamepopup, gamedrama, gamemenu, gamelongscript, \
    gamelorebook, gameweather, gamefaction, gameunitstat

config = main.config
SoundVolume = main.Soundvolume
SCREENRECT = main.SCREENRECT
main_dir = main.main_dir

load_image = gamelongscript.load_image
load_images = gamelongscript.load_images
csv_read = gamelongscript.csv_read
load_sound = gamelongscript.load_sound


class Battle():
    def __init__(self, winstyle, ruleset, rulesetfolder):
        pygame.init()  # Initialize pygame
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer = None
        self.bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32) # Set the display mode
        self.screen = pygame.display.set_mode(SCREENRECT.size, winstyle | pygame.RESIZABLE, self.bestdepth) # set up game screen
        self.ruleset = ruleset # current ruleset used
        self.rulesetfolder = rulesetfolder # the folder of rulseset used

        #v create game map objects and their default variables
        featurelist = []
        with open(main_dir + "/data/map" + '/unit_terrainbonus.csv', 'r') as unitfile:
            rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
            for row in rd:
                featurelist.append(row[1]) # get terrain feature combination name for folder
        unitfile.close()
        featurelist = featurelist[1:]
        self.mapselected = "hastings" # map folder name
        imgs = load_images(['ruleset', self.rulesetfolder.strip("/"), 'map', self.mapselected], loadorder=False)
        gamemap.Basemap.images = [imgs[0]]
        gamemap.Mapfeature.images = [imgs[1]]
        gamemap.Mapfeature.main_dir = main_dir
        gamemap.Mapheight.images = [imgs[2]]
        gamemap.Beautifulmap.placename = imgs[3]
        gamemap.Beautifulmap.main_dir = main_dir
        img = load_image('effect.png', 'map') # map special effect image
        gamemap.Beautifulmap.effectimage = img
        emptyimage = load_image('empty.png', 'map/texture') # empty texture image
        maptexture = []
        loadtexturefolder = []
        for feature in featurelist:
            loadtexturefolder.append(feature.replace(" ", "").lower()) # convert terrain feature list to lower case with no space
        loadtexturefolder = list(set(loadtexturefolder)) # list of terrian folder to load
        loadtexturefolder = [item for item in loadtexturefolder if item != ""]  # For now remove terrain with no planned name/folder yet
        for index, texturefolder in enumerate(loadtexturefolder):
            imgs = load_images(['map', 'texture', texturefolder], loadorder=False)
            maptexture.append(imgs)
        gamemap.Beautifulmap.textureimages = maptexture
        gamemap.Beautifulmap.loadtexturelist = loadtexturefolder
        gamemap.Beautifulmap.emptyimage = emptyimage
        #^ End game map

        #v Faction class
        gamefaction.Factiondata.main_dir = main_dir
        self.allfaction = gamefaction.Factiondata(option=self.rulesetfolder)
        imgsold = load_images(['ruleset', self.rulesetfolder.strip("/"), 'faction', 'coa'])  # coa imagelist
        imgs = []
        for img in imgsold:
            imgs.append(img)
        self.coa = imgs
        #^ End faction

        #v create unit related class
        imgs = load_images(['war', 'unit_ui'])
        gamesquad.Unitsquad.images = imgs
        self.imagewidth, self.imageheight = imgs[0].get_width(), imgs[0].get_height()
        imgs = []
        imgsold = load_images(['war', 'unit_ui', 'battalion'])
        for img in imgsold:
            imgs.append(img)
        gamebattalion.Unitarmy.images = imgs
        imgsold = load_images(['war', 'unit_ui', 'weapon'])
        imgs = []
        for img in imgsold:
            x, y = img.get_width(), img.get_height()
            img = pygame.transform.scale(img, (int(x / 1.7), int(y / 1.7))) # scale 1.7 seem to be most fitting as a placeholder
            imgs.append(img)
        self.allweapon = gameunitstat.Weaponstat(main_dir, imgs, self.ruleset)  # Create weapon class
        imgs = load_images(['ui', 'battlemenu_ui'], loadorder=False)
        gamemenu.Menubox.images = imgs  # Create ESC Menu box
        gamemenu.Menubox.SCREENRECT = SCREENRECT
        imgs = load_images(['war', 'unit_ui', 'armour'])
        self.allarmour = gameunitstat.Armourstat(main_dir, imgs, self.ruleset)  # Create armour class
        self.statusimgs = load_images(['ui', 'status_icon'], loadorder=False)
        self.roleimgs = load_images(['ui', 'role_icon'], loadorder=False)
        self.traitimgs = load_images(['ui', 'trait_icon'], loadorder=False)
        self.skillimgs = load_images(['ui', 'skill_icon'], loadorder=False)
        cooldown = pygame.Surface((self.skillimgs[0].get_width(), self.skillimgs[0].get_height()), pygame.SRCALPHA)
        cooldown.fill((230, 70, 80, 200)) # red colour filter for skill cooldown timer
        activeskill = pygame.Surface((self.skillimgs[0].get_width(), self.skillimgs[0].get_height()), pygame.SRCALPHA)
        activeskill.fill((170, 220, 77, 200)) # green colour filter for skill active timer
        gameui.Skillcardicon.activeskill = activeskill
        gameui.Skillcardicon.cooldown = cooldown
        self.gameunitstat = gameunitstat.Unitstat(main_dir, self.ruleset, self.rulesetfolder)
        #^ End unit class

        #v create leader list
        imgs, order = load_images(['ruleset', self.rulesetfolder.strip("/"), 'leader', 'portrait'], loadorder=False, returnorder=True)
        self.allleader = gameunitstat.Leaderstat(main_dir, imgs, order, option=self.rulesetfolder)
        #^ End leader

        #v Create weather related class
        self.allweather = csv_read('weather.csv', ['data', 'map', 'weather'])
        self.weathermatterimgs = []
        for weather in ('0', '1', '2', '3'):  # Load weather matter sprite image
            imgs = load_images(['map', 'weather', weather], loadorder=False)
            self.weathermatterimgs.append(imgs)
        self.weathereffectimgs = []
        for weather in ('0', '1', '2', '3'):  # Load weather effect sprite image
            imgsold = load_images(['map', 'weather', 'effect', weather], loadorder=False)
            imgs = []
            for img in imgsold:
                img = pygame.transform.scale(img, (SCREENRECT.width, SCREENRECT.height))
                imgs.append(img)
            self.weathereffectimgs.append(imgs)
        imgs = load_images(['map', 'weather', 'icon'], loadorder=False)  # Load weather icon
        gameweather.Weather.images = imgs
        #^ End weather

        #v Game Effect related class
        imgs = load_images(['effect'])
        # imgs = []
        # for img in imgsold:
        # x, y = img.get_width(), img.get_height()
        # img = pygame.transform.scale(img, (int(x ), int(y / 2)))
        # imgs.append(img)
        self.gameeffect = imgs
        rangeattack.Rangearrow.images = [self.gameeffect[0]]
        #^ End game effect

        #v Popup Ui
        imgs = load_images(['ui', 'popup_ui', 'terraincheck'], loadorder=False)
        gamepopup.Terrainpopup.images = imgs
        gamepopup.Terrainpopup.SCREENRECT = SCREENRECT
        imgs = load_images(['ui', 'popup_ui', 'dramatext'], loadorder=False)
        gamedrama.Textdrama.images = imgs
        #^ End popup ui

        #v Decorate the game window
        # icon = load_image('sword.jpg')
        # icon = pygame.transform.scale(icon, (32, 32))
        # pygame.display.set_icon(icon)
        #^ End decorate

        pygame.display.set_caption('Masendor RTS')
        pygame.mouse.set_visible(True)

        #v load the sound effects
        # boom_sound = load_sound('boom.wav')
        # shoot_sound = load_sound('car_door.wav')
        #^ End load sound effect

        #v Random music played from list
        if pygame.mixer:
            self.SONG_END = pygame.USEREVENT + 1
            # musiclist = os.path.join(main_dir, 'data/sound/')
            self.musiclist = glob.glob(main_dir + '/data/sound/*.mp3')
            self.pickmusic = random.randint(1, 1)
            pygame.mixer.music.set_endevent(self.SONG_END)
            pygame.mixer.music.load(self.musiclist[self.pickmusic])
            pygame.mixer.music.play(0)
        #^ End music play

        #v Initialise Game Groups
        self.allcamera = pygame.sprite.LayeredUpdates() # this is layer drawer game camera, all image pos should be based on the map not screen
        ## the camera layer is as followed 0 = terrain map, 1 = dead army, 2 = map special feature, 3 = hitbox, 4 = direction arrow,
        ## 5 = battalion, 6 = flying battalion, 7 = arrow/range, 8 = weather, 9 = weather matter, 10 = ui/button, 11 = squad inspect, 12 pop up
        self.allui = pygame.sprite.LayeredUpdates() # this is layer drawer for ui, all image pos should be based on the screen
        self.battalionupdater = pygame.sprite.Group() # updater for battalion objects
        self.hitboxupdater = pygame.sprite.Group() # updater for hitbox objects
        self.squadupdater = pygame.sprite.Group() # updater for squad objects
        self.leaderupdater = pygame.sprite.Group() # updater for leader objects
        self.uiupdater = pygame.sprite.Group() # updater for ui objects
        self.weatherupdater = pygame.sprite.Group() # updater for weather objects
        self.effectupdater = pygame.sprite.Group() # updater for in-game effect objects (e.g. range attack sprite)
        self.battlemap = pygame.sprite.Group() # base terrain map object
        self.battlemapfeature = pygame.sprite.Group() # terrain feature map object
        self.battlemapheight = pygame.sprite.Group() # height map object
        self.showmap = pygame.sprite.Group() # beautiful map object that is shown in gameplay
        self.team1army = pygame.sprite.Group() # taem 1 battalions group
        self.team2army = pygame.sprite.Group() # team 2 battalions group
        self.squad = pygame.sprite.Group() # all squads group
        self.armyleader = pygame.sprite.Group() # all leaders group
        self.hitboxes = pygame.sprite.Group() # all hitboxes group
        self.arrows = pygame.sprite.Group() # all arrows group and maybe other range effect stuff later
        self.directionarrows = pygame.sprite.Group()
        self.deadunit = pygame.sprite.Group() # dead unit group
        self.gameui = pygame.sprite.Group() # various game ui group
        self.minimap = pygame.sprite.Group() # minimap ui
        self.eventlog = pygame.sprite.Group() # event log ui
        self.logscroll = pygame.sprite.Group() # scroller fro event log ui
        self.buttonui = pygame.sprite.Group() # buttons for various ui group
        self.lorebuttonui = pygame.sprite.Group() # buttons for enclycopedia group
        self.squadselectedborder = pygame.sprite.Group() # squad selected border in inspect ui army box
        self.fpscount = pygame.sprite.Group() # fps number counter
        self.switchbuttonui = pygame.sprite.Group() # button that switch image based on current setting (e.g. battalion behaviour setting)
        self.terraincheck = pygame.sprite.Group() # terrain information pop up ui
        self.buttonnamepopup = pygame.sprite.Group() # button name pop up ui when mouse over button
        self.leaderpopup = pygame.sprite.Group() # leader name pop up ui when mouse over leader image in command ui
        self.effectpopup = pygame.sprite.Group() # effect name pop up ui when mouse over status effect icon
        self.skillicon = pygame.sprite.Group() # skill and trait icon objects
        self.effecticon = pygame.sprite.Group() # status effect icon objects
        self.textdrama = pygame.sprite.Group() # dramatic text effect (announcement) object
        self.battlemenu = pygame.sprite.Group() # esc menu object
        self.battlemenubutton = pygame.sprite.Group() # buttons for esc menu object group
        self.optionmenubutton = pygame.sprite.Group() # buttons for esc menu option object group
        self.lorebook = pygame.sprite.Group() # encyclopedia object
        self.slidermenu = pygame.sprite.Group()
        self.valuebox = pygame.sprite.Group() # value number and box in esc menu option
        self.armyselector = pygame.sprite.Group() # army selector ui
        self.armyicon = pygame.sprite.Group() # army icon object group in army selector ui
        self.selectscroll = pygame.sprite.Group() # scoller object in army selector ui
        self.timeui = pygame.sprite.Group() # time bar ui
        self.timenumber = pygame.sprite.Group() # number text of in-game time
        self.speednumber = pygame.sprite.Group() # number text of current game speed
        self.lorenamelist = pygame.sprite.Group() # box sprite for showing subsection name list in encyclopedia
        self.lorescroll = pygame.sprite.Group() # scroller for subsection name list in encyclopedia
        self.subsectionname = pygame.sprite.Group() # subsection name objects group in encyclopedia blit on lorenamelist
        self.weathermatter = pygame.sprite.Group() # sprite of weather effect group such as rain sprite
        self.weathereffect = pygame.sprite.Group() # sprite of special weather effect group such as fog that cover whole screen
        #^ End initialise

        #v Assign default groups
        gamemap.Basemap.containers = self.battlemap
        gamemap.Mapfeature.containers = self.battlemapfeature
        gamemap.Mapheight.containers = self.battlemapheight
        gamemap.Beautifulmap.containers = self.showmap, self.allcamera
        gamebattalion.Unitarmy.containers = self.team1army, self.team2army, self.battalionupdater, self.squad, self.allcamera
        gamesquad.Unitsquad.containers = self.team1army, self.team2army, self.squadupdater, self.squad
        gamebattalion.Deadarmy.containers = self.deadunit, self.battalionupdater, self.allcamera
        gamebattalion.Hitbox.containers = self.hitboxes, self.hitboxupdater, self.allcamera
        gameleader.Leader.containers = self.armyleader, self.leaderupdater
        rangeattack.Rangearrow.containers = self.arrows, self.effectupdater, self.allcamera
        gamebattalion.Directionarrow.containers = self.directionarrows, self.effectupdater, self.allcamera
        gameui.Gameui.containers = self.gameui, self.uiupdater
        gameui.Minimap.containers = self.minimap, self.allui
        gameui.FPScount.containers = self.allui
        gameui.Uibutton.containers = self.buttonui, self.lorebuttonui
        gameui.Switchuibutton.containers = self.switchbuttonui, self.uiupdater
        gameui.Selectedsquad.containers = self.squadselectedborder
        gameui.Skillcardicon.containers = self.skillicon, self.allui
        gameui.Effectcardicon.containers = self.effecticon, self.allui
        gameui.Eventlog.containers = self.eventlog, self.allui
        gameui.Uiscroller.containers = self.logscroll, self.selectscroll, self.lorescroll, self.allui
        gameui.Armyselect.containers = self.armyselector, self.allui
        gameui.Armyicon.containers = self.armyicon, self.allui
        gameui.Timeui.containers = self.timeui, self.allui
        gameui.Timer.containers = self.timenumber, self.allui
        gameui.Speednumber.containers = self.speednumber, self.allui
        gamepopup.Terrainpopup.containers = self.terraincheck
        gamepopup.Onelinepopup.containers = self.buttonnamepopup, self.leaderpopup
        gamepopup.Effecticonpopup.containers = self.effectpopup
        gamedrama.Textdrama.containers = self.textdrama
        gamemenu.Menubox.containers = self.battlemenu
        gamemenu.Menubutton.containers = self.battlemenubutton, self.optionmenubutton
        gamemenu.Slidermenu.containers = self.slidermenu
        gamemenu.Valuebox.containers = self.valuebox
        gamelorebook.Lorebook.containers = self.lorebook
        gamelorebook.Subsectionlist.containers = self.lorenamelist
        gamelorebook.Subsectionname.containers = self.subsectionname, self.allui
        gameweather.Mattersprite.containers = self.weathermatter, self.allui, self.weatherupdater
        gameweather.Specialeffect.containers = self.weathereffect, self.allui, self.weatherupdater
        #^ End assign

        #v Create the battle map
        self.camerapos = pygame.Vector2(500, 500)  # Camera pos at the current zoom, start at center of map
        self.basecamerapos = pygame.Vector2(500, 500)  # Camera pos at furthest zoom for recalculate sprite pos after zoom
        self.camerascale = 1  # Camera zoom
        self.battlemap = gamemap.Basemap(self.camerascale) # create base terrain map
        self.battlemapfeature = gamemap.Mapfeature(self.camerascale) # create terrain feature map
        self.battlemapheight = gamemap.Mapheight(self.camerascale) # create height map
        self.showmap = gamemap.Beautifulmap(self.camerascale, self.battlemap, self.battlemapfeature, self.battlemapheight)
        del gamemap.Beautifulmap.textureimages  # remove texture image list to clear memory
        #^ End create battle map

        #v Assign default variable to some class
        gamebattalion.Unitarmy.gamemap = self.battlemap  # add battle map to all battalion class
        gamebattalion.Unitarmy.gamemapfeature = self.battlemapfeature  # add battle map to all battalion class
        gamebattalion.Unitarmy.gamemapheight = self.battlemapheight
        gamebattalion.Unitarmy.statuslist = self.gameunitstat.statuslist
        gamebattalion.Unitarmy.maingame = self
        rangeattack.Rangearrow.gamemapheight = self.battlemapheight
        gamesquad.Unitsquad.maingame = self
        gameleader.Leader.maingame = self
        gamecamera.Camera.SCREENRECT = SCREENRECT
        self.camera = gamecamera.Camera(self.camerapos, self.camerascale)
        #^ End assign default

        self.background = pygame.Surface(SCREENRECT.size) # Create background image
        self.background.fill((255, 255, 255)) # fill background image with black colour

        #v Create Starting Values
        self.mixervolume = SoundVolume
        self.leaderposname = ("Commander","Sub-General","Sub-General","Sub-Commander","General","Sub-General","Sub-General","Advisor") # Name of leader position in battalion, the first 4 is for commander battalion
        self.playerteam = 1 # player selected team
        self.enactment = True # enactment mod, control both team
        self.gamestate = 1
        self.mousetimer = 0 # This is timer for checking double mouse click, use realtime
        self.uitimer = 0 # This is timer for ui update function, use realtime
        self.dramatimer = 0 # This is timer for combat related function, use game time (realtime * gamespeed)
        self.dt = 0  # Realtime used for in game calculation
        self.uidt = 0  # Realtime used for ui timer
        self.combattimer = 0 # This is timer for combat related function, use game time (realtime * gamespeed)
        self.clock = pygame.time.Clock() # Game clock to keep track of realtime pass
        self.lastmouseover = 0 # Which unit last mouse over
        self.gamespeed = 1 # Current game speed
        self.gamespeedset = (0, 0.5, 1, 2, 4, 6) # availabe game speed
        self.uiclick = False # for checking if mouse click is on ui
        self.clickany = False  # For checking if mouse click on anything, if not close ui related to battalion
        self.newarmyclick = False  #  For checking if another unit is clicked when inspect ui open
        self.inspectui = False # For checking if inspect ui is currently open or not
        self.lastselected = None # Which army is currently selected
        self.mapviewmode = 0 # default, another one show height map
        self.mapshown = self.showmap
        self.squadlastselected = None
        self.beforeselected = None # Which army is selected before
        self.splithappen = False # Check if battalion get split in that loop
        self.currentweather = None
        self.weatherscreenadjust = SCREENRECT.width / SCREENRECT.height
        self.splitunit = gamelongscript.splitunit
        self.losscal = gamelongscript.losscal
        self.leadernow = []
        self.rightcorner = SCREENRECT.width - 5
        self.bottomcorner = SCREENRECT.height - 5
        self.centerscreen = [SCREENRECT.width / 2, SCREENRECT.height / 2]
        self.battlemousepos = [0, 0]
        #^ End start value

        #v Load weather schedule
        try:
            self.weatherevent = csv_read('weather.csv', ["data", 'ruleset', self.rulesetfolder.strip("/"), 'map', self.mapselected], 1)
            self.weatherevent = self.weatherevent[1:]
            gamelongscript.convertweathertime(self.weatherevent)
        except:  # If no weather found use default light sunny weather start at 9.00
            newtime = datetime.datetime.strptime("09:00:00", "%H:%M:%S").time()
            newtime = datetime.timedelta(hours=newtime.hour, minutes=newtime.minute, seconds=newtime.second)
            self.weatherevent = [[4, newtime, 0]] # default weather light sunny all day
        self.weatherschedule = self.weatherevent[0][1]
        #^ End weather schedule

        #v Create game ui objects
        self.minimap = gameui.Minimap(SCREENRECT.width, SCREENRECT.height, self.showmap.trueimage, self.camera)
        topimage = load_images(['ui', 'battle_ui'])
        iconimage = load_images(['ui', 'battle_ui', 'topbar_icon'])
        self.armyselector = gameui.Armyselect((0, 0), topimage[30]) # army select list ui
        self.selectscroll = gameui.Uiscroller(self.armyselector.rect.topright, topimage[30].get_height(), self.armyselector.maxrowshow) # scroller for army select ui
        self.gameui = [
            gameui.Gameui(X=SCREENRECT.width - topimage[0].get_size()[0] / 2, Y=topimage[0].get_size()[1] / 2, image=topimage[0],
                          icon=iconimage, uitype="topbar")]
        iconimage = load_images(['ui', 'battle_ui', 'commandbar_icon'])
        self.gameui.append(
            gameui.Gameui(X=topimage[1].get_size()[0] / 2, Y=(topimage[1].get_size()[1] / 2) + self.armyselector.image.get_height(),
                          image=topimage[1], icon=iconimage, uitype="commandbar"))
        self.gameui.append(
            gameui.Gameui(X=SCREENRECT.width - topimage[2].get_size()[0] / 2, Y=(topimage[0].get_size()[1]*2.5) + topimage[5].get_size()[1], image=topimage[2],
                          icon="", uitype="unitcard"))
        self.gameui[2].featurelist = featurelist
        self.gameui.append(
            gameui.Gameui(X=SCREENRECT.width - topimage[5].get_size()[0] / 2, Y=topimage[0].get_size()[1]*4,
                          image=topimage[5], icon="", uitype="armybox"))
        self.popgameui = self.gameui
        self.timeui = gameui.Timeui(self.armyselector.rect.topright, topimage[31])
        self.timenumber = gameui.Timer(self.timeui.rect.topleft, self.weatherschedule)  # time number on time ui
        self.speednumber = gameui.Speednumber((self.timeui.rect.center[0] + 40, self.timeui.rect.center[1]),
                                              self.gamespeed)  # game speed number on the time ui
        self.buttonui = [gameui.Uibutton(self.gameui[2].X - 152, self.gameui[2].Y + 10, topimage[3], 0),  # unit card description button
                         gameui.Uibutton(self.gameui[2].X - 152, self.gameui[2].Y - 70, topimage[4], 1),  # unit card stat button
                         gameui.Uibutton(self.gameui[2].X - 152, self.gameui[2].Y - 30, topimage[7], 2),  # unit card skill button
                         gameui.Uibutton(self.gameui[2].X - 152, self.gameui[2].Y + 50, topimage[22], 3),  # unit card equipment button
                         gameui.Uibutton(self.gameui[0].X - 206, self.gameui[0].Y - 1, topimage[6], 1),  # army inspect open/close button
                         gameui.Uibutton(self.gameui[1].X - 115, self.gameui[1].Y + 26, topimage[8], 0),  # split by coloumn button
                         gameui.Uibutton(self.gameui[1].X - 115, self.gameui[1].Y + 56, topimage[9], 1),  # split by row button
                         gameui.Uibutton(self.gameui[1].X + 100, self.gameui[1].Y + 56, topimage[14], 1)]  # decimation button
        self.switchbuttonui = [gameui.Switchuibutton(self.gameui[1].X - 30, self.gameui[1].Y + 96, topimage[10:14]),  # skill condition button
                               gameui.Switchuibutton(self.gameui[1].X - 70, self.gameui[1].Y + 96, topimage[15:17]),  # fire at will button
                               gameui.Switchuibutton(self.gameui[1].X, self.gameui[1].Y + 96, topimage[17:20]),  # behaviour button
                               gameui.Switchuibutton(self.gameui[1].X + 40, self.gameui[1].Y + 96, topimage[20:22]),  # shoot range button
                               gameui.Switchuibutton(self.gameui[1].X - 115, self.gameui[1].Y + 96, topimage[35:38]),  # arcshot button
                               gameui.Switchuibutton(self.gameui[1].X + 80, self.gameui[1].Y + 96, topimage[38:40])]  # toggle run button
        #^ End game ui

        try: # get map event for event log
            mapevent = csv_read('eventlog.csv', ["data", 'ruleset', self.rulesetfolder.strip("/"), 'map', self.mapselected], 0)
            gameui.Eventlog.mapevent = mapevent
        except: # can't find any event file
            mapevent = {} # create empty list
        self.eventlog = gameui.Eventlog(topimage[23], (0, SCREENRECT.height))
        self.eventschedule = None
        self.eventlist = []
        for index, event in enumerate(self.eventlog.mapevent):
            if self.eventlog.mapevent[event][3] is not None:
                if index == 0:
                    self.eventmapid = event
                    self.eventschedule = self.eventlog.mapevent[event][3]
                self.eventlist.append(event)
        self.logscroll = gameui.Uiscroller(self.eventlog.rect.topright, topimage[23].get_height(), self.eventlog.maxrowshow) # event log scroller
        self.eventlog.logscroll = self.logscroll  # Link scroller to ui since it is easier to do here with the current order
        gamesquad.Unitsquad.eventlog = self.eventlog # Assign eventlog to unit class to broadcast event to the log
        self.buttonui.append(gameui.Uibutton(self.eventlog.pos[0] + (topimage[24].get_width() / 2),
                                             self.eventlog.pos[1] - self.eventlog.image.get_height() - (topimage[24].get_height() / 2), topimage[24],
                                             0)) # war tab log button
        self.buttonui += [gameui.Uibutton(self.buttonui[8].pos[0] + topimage[24].get_width(), self.buttonui[8].pos[1], topimage[25], 1), # army tab log button
                          gameui.Uibutton(self.buttonui[8].pos[0] + (topimage[24].get_width() * 2), self.buttonui[8].pos[1], topimage[26], 2), # leader tab log button
                          gameui.Uibutton(self.buttonui[8].pos[0] + (topimage[24].get_width() * 3), self.buttonui[8].pos[1], topimage[27], 3), # unit tab log button
                          gameui.Uibutton(self.buttonui[8].pos[0] + (topimage[24].get_width() * 5), self.buttonui[8].pos[1], topimage[28], 4), # delete current tab log button
                          gameui.Uibutton(self.buttonui[8].pos[0] + (topimage[24].get_width() * 6), self.buttonui[8].pos[1], topimage[29], 5), # delete all log button
                          gameui.Uibutton(self.timeui.rect.center[0] - 30, self.timeui.rect.center[1], topimage[32], 0), # time pause button
                          gameui.Uibutton(self.timeui.rect.center[0], self.timeui.rect.center[1], topimage[33], 1), # time decrease button
                          gameui.Uibutton(self.timeui.rect.midright[0] - 60, self.timeui.rect.center[1], topimage[34], 2)] # time increase button
        self.allui.add(self.buttonui[8:17])
        self.screenbuttonlist = self.buttonui[8:17]  # List of button always on screen (for now just eventlog)
        self.unitcardbutton = self.buttonui[0:4]
        self.inspectbutton = self.buttonui[4]
        self.colsplitbutton = self.buttonui[5] # battalion split by column button
        self.rowsplitbutton = self.buttonui[6] # battalion split by row button
        self.squadselectedborder = gameui.Selectedsquad(topimage[-1])
        self.terraincheck = gamepopup.Terrainpopup()
        self.buttonnamepopup = gamepopup.Onelinepopup()
        self.leaderpopup = gamepopup.Onelinepopup()
        self.effectpopup = gamepopup.Effecticonpopup()
        gamedrama.Textdrama.SCREENRECT = SCREENRECT
        self.textdrama = gamedrama.Textdrama()
        self.fpscount = gameui.FPScount()
        self.battlemenu = gamemenu.Menubox()

        #v Encyclopedia related objects
        gamelorebook.Lorebook.conceptstat = csv_read('concept_stat.csv', ['data', 'ruleset', self.rulesetfolder.strip("/"), 'lore'])
        gamelorebook.Lorebook.conceptlore = csv_read('concept_lore.csv', ['data', 'ruleset', self.rulesetfolder.strip("/"), 'lore'])
        gamelorebook.Lorebook.historystat = csv_read('history_stat.csv', ['data', 'ruleset', self.rulesetfolder.strip("/"), 'lore'])
        gamelorebook.Lorebook.historylore = csv_read('history_lore.csv', ['data', 'ruleset', self.rulesetfolder.strip("/"), 'lore'])
        gamelorebook.Lorebook.factionlore = self.allfaction.factionlist
        gamelorebook.Lorebook.unitstat = self.gameunitstat.unitlist
        gamelorebook.Lorebook.unitlore = self.gameunitstat.unitlore
        gamelorebook.Lorebook.armourstat = self.allarmour.armourlist
        gamelorebook.Lorebook.weaponstat = self.allweapon.weaponlist
        gamelorebook.Lorebook.mountstat = self.gameunitstat.mountlist
        gamelorebook.Lorebook.statusstat = self.gameunitstat.statuslist
        gamelorebook.Lorebook.skillstat = self.gameunitstat.abilitylist
        gamelorebook.Lorebook.traitstat = self.gameunitstat.traitlist
        gamelorebook.Lorebook.leader = self.allleader
        gamelorebook.Lorebook.leaderlore = None
        gamelorebook.Lorebook.terrainstat = self.battlemapfeature.featuremod
        gamelorebook.Lorebook.weatherstat = self.allweather
        gamelorebook.Lorebook.landmarkstat = None
        gamelorebook.Lorebook.unitgradestat = self.gameunitstat.gradelist
        gamelorebook.Lorebook.unitclasslist = self.gameunitstat.role
        gamelorebook.Lorebook.leaderclasslist = self.allleader.leaderclass
        gamelorebook.Lorebook.racelist = self.gameunitstat.racelist
        gamelorebook.Lorebook.SCREENRECT = SCREENRECT
        gamelorebook.Lorebook.main_dir = main_dir
        imgs = load_images(['ui', 'lorebook_ui'], loadorder=False)
        self.lorebook = gamelorebook.Lorebook(imgs[0])
        self.lorenamelist = gamelorebook.Subsectionlist(self.lorebook.rect.topleft, imgs[1])
        imgs = load_images(['ui', 'lorebook_ui', 'button'], loadorder=False)
        self.lorebuttonui = [
            gameui.Uibutton(self.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5), self.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                            imgs[0], 0, 13),
            gameui.Uibutton(self.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 2, self.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                            imgs[1], 1, 13),
            gameui.Uibutton(self.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 3, self.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                            imgs[2], 2, 13),
            gameui.Uibutton(self.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 4, self.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                            imgs[3], 3, 13),
            gameui.Uibutton(self.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 5, self.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                            imgs[4], 4, 13),
            gameui.Uibutton(self.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 6, self.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                            imgs[5], 5, 13),
            gameui.Uibutton(self.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 7, self.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                            imgs[6], 6, 13),
            gameui.Uibutton(self.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 8, self.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                            imgs[7], 7, 13),
            gameui.Uibutton(self.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 9, self.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2),
                            imgs[8], 8, 13),
            gameui.Uibutton(self.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 10,
                            self.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2), imgs[9], 9, 13),
            gameui.Uibutton(self.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 11,
                            self.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2), imgs[10], 10, 13),
            gameui.Uibutton(self.lorebook.rect.topleft[0] + (imgs[0].get_width() + 5) * 13,
                            self.lorebook.rect.topleft[1] - (imgs[0].get_height() / 2), imgs[12], 19, 13),
            gameui.Uibutton(self.lorebook.rect.bottomleft[0] + (imgs[13].get_width()), self.lorebook.rect.bottomleft[1] - imgs[13].get_height(),
                            imgs[13], 20, 13),
            gameui.Uibutton(self.lorebook.rect.bottomright[0] - (imgs[14].get_width()), self.lorebook.rect.bottomright[1] - imgs[14].get_height(),
                            imgs[14], 21, 13)]
        #^ End encyclopedia objects

        #v Esc menu related objects
        buttonimage = load_images(['ui', 'battlemenu_ui', 'button'], loadorder=False)
        menurectcenter0 = self.battlemenu.rect.center[0]
        menurectcenter1 = self.battlemenu.rect.center[1]
        self.battlemenubutton = [
            gamemenu.Menubutton(buttonimage, (menurectcenter0, menurectcenter1 - 100), text="Resume", size=14),
            gamemenu.Menubutton(buttonimage, (menurectcenter0, menurectcenter1 - 50), text="Encyclopedia", size=14),
            gamemenu.Menubutton(buttonimage, (menurectcenter0, menurectcenter1), text="Option", size=14),
            gamemenu.Menubutton(buttonimage, (menurectcenter0, menurectcenter1 + 50), text="Main Menu", size=14),
            gamemenu.Menubutton(buttonimage, (menurectcenter0, menurectcenter1 + 100), text="Desktop", size=14)]
        self.optionmenubutton = [
            gamemenu.Menubutton(buttonimage, (menurectcenter0 - 50, menurectcenter1 + 70), text="Confirm", size=14),
            gamemenu.Menubutton(buttonimage, (menurectcenter0 + 50, menurectcenter1 + 70), text="Apply", size=14),
            gamemenu.Menubutton(buttonimage, (menurectcenter0 + 150, menurectcenter1 + 70), text="Cancel", size=14)]
        sliderimage = load_images(['ui', 'battlemenu_ui', 'slider'], loadorder=False)
        self.slidermenu = [
            gamemenu.Slidermenu(sliderimage[0], sliderimage[1:3], (menurectcenter0 * 1.1, menurectcenter1), SoundVolume,
                                0)]
        self.valuebox = [gamemenu.Valuebox(sliderimage[3], (self.battlemenu.rect.topright[0] * 1.2, menurectcenter1), SoundVolume)]
        #^ End esc menu objects

        #v initialise starting unit sprites
        self.team1army, self.team2army, self.squad = [], [], []
        self.inspectuipos = [self.gameui[0].rect.bottomleft[0] - self.imagewidth / 1.25,
                             self.gameui[0].rect.bottomleft[1] - self.imageheight / 3]
        self.squadindexlist = gamelongscript.unitsetup(self, self.playerteam)
        self.allunitlist = self.team1army.copy()
        self.allunitlist = self.allunitlist + self.team2army
        self.allunitindex = [army.gameid for army in self.allunitlist]
        self.team1poslist = {}
        self.team2poslist = {}
        self.showingsquad = []
        #^ End start unit sprite

    def setuparmyicon(self):
        """Setup army selection list in army selector ui top left of screen"""
        row = 30
        startcolumn = 25
        column = startcolumn
        list = self.team1army
        if self.enactment == True:
            list = self.allunitlist
        currentindex = int(self.armyselector.currentrow * self.armyselector.maxcolumnshow)
        self.armyselector.logsize = len(list) / self.armyselector.maxcolumnshow
        if self.armyselector.logsize.is_integer() == False:
            self.armyselector.logsize = int(self.armyselector.logsize) + 1
        if self.armyselector.currentrow > self.armyselector.logsize - 1:
            self.armyselector.currentrow = self.armyselector.logsize - 1
            currentindex = int(self.armyselector.currentrow * self.armyselector.maxcolumnshow)
            self.selectscroll.changeimage(newrow=self.armyselector.currentrow)
        if len(self.armyicon) > 0:  # Remove all old icon first before making new list
            for icon in self.armyicon:
                icon.kill()
                del icon
        for index, army in enumerate(list[currentindex:]):
            self.armyicon.add(gameui.Armyicon((column, row), army))
            column += 40
            if column > 250:
                row += 50
                column = startcolumn
            if row > 100: break
        self.selectscroll.changeimage(logsize=self.armyselector.logsize)

    def checksplit(self, whoinput):
        """Check if army can be splitted, if not remove splitting button"""
        if np.array_split(whoinput.armysquad, 2, axis=1)[0].size >= 10 and np.array_split(whoinput.armysquad, 2, axis=1)[1].size >= 10 and \
                whoinput.leader[1].name != "None": # can only split if both battalion size will be larger than 10 and second leader exist
            self.allui.add(self.colsplitbutton)
        elif self.colsplitbutton in self.allui:
            self.colsplitbutton.kill()
        if np.array_split(whoinput.armysquad, 2)[0].size >= 10 and np.array_split(whoinput.armysquad, 2)[1].size >= 10 and whoinput.leader[
            1].name != "None":
            self.allui.add(self.rowsplitbutton)
        elif self.rowsplitbutton in self.allui:
            self.rowsplitbutton.kill()

    def traitskillblit(self):
        """For blitting skill and trait icon into squad info ui"""
        position = self.gameui[2].rect.topleft
        position = [position[0] + 70, position[1] + 60] # start position
        startrow = position[0]
        for icon in self.skillicon.sprites(): icon.kill()
        for trait in self.gameui[2].value2[0]:
            self.skillicon.add(gameui.Skillcardicon(self.traitimgs[0], (position[0], position[1]), 0, id=trait))  # For now use placeholder image 0
            position[0] += 40
            if position[0] >= SCREENRECT.width:
                position[1] += 30
                position[0] = startrow
        position = self.gameui[2].rect.topleft
        position = [position[0] + 70, position[1] + 100]
        startrow = position[0]
        for skill in self.gameui[2].value2[1]:
            self.skillicon.add(gameui.Skillcardicon(self.skillimgs[0], (position[0], position[1]), 1, id=skill))  # For now use placeholder image 0
            position[0] += 40
            if position[0] >= SCREENRECT.width:
                position[1] += 30
                position[0] = startrow

    def effecticonblit(self):
        """For blitting all status effect icon"""
        position = self.gameui[2].rect.topleft
        position = [position[0] + 70, position[1] + 140]
        startrow = position[0]
        for icon in self.effecticon.sprites(): icon.kill()
        for status in self.gameui[2].value2[4]:
            self.effecticon.add(gameui.Skillcardicon(self.statusimgs[0], (position[0], position[1]), 4, id=status))
            position[0] += 40
            if position[0] >= SCREENRECT.width:
                position[1] += 30
                position[0] = startrow

    def countdownskillicon(self):
        for skill in self.skillicon:
            if skill.type == 1: # only do skill icon not trait
                cd = 0
                activetime = 0
                if skill.gameid in self.gameui[2].value2[2]:
                    cd = int(self.gameui[2].value2[2][skill.gameid])
                if skill.gameid in self.gameui[2].value2[3]:
                    activetime = int(self.gameui[2].value2[3][skill.gameid][3])
                skill.iconchange(cd, activetime)
        # for effect in self.effecticon:
        #     cd = 0
        #     if effect.id in self.gameui[2].value2[4]:
        #         cd = int(self.gameui[2].value2[4][effect.id][3])
        #     effect.iconchange(cd, 0)

    def popoutlorebook(self, section, gameid):
        self.gamestate = 0
        self.battlemenu.mode = 2
        self.allui.add(self.lorebook, self.lorenamelist, *self.lorebuttonui)
        self.lorescroll = gameui.Uiscroller(self.lorenamelist.rect.topright, self.lorenamelist.image.get_height(),
                                            self.lorebook.maxsubsectionshow, layer=14)
        self.lorebook.changesection(section, self.lorenamelist, self.subsectionname, self.lorescroll)
        self.lorebook.changesubsection(gameid)
        self.lorescroll.changeimage(newrow=self.lorebook.currentsubsectionrow)

    def uimouseover(self):
        """mouse over ui that is not unit card and armybox (topbar and commandbar)"""
        for ui in self.gameui:
            if ui in self.allui and ui.rect.collidepoint(self.mousepos):
                if ui.uitype not in ("unitcard", 'armybox'):
                    self.clickany = True
                    self.uiclick = True  # for avoiding clicking unit under ui
                    break
        return self.clickany

    def armyiconmouseover(self, mouseup, mouseright):
        for icon in self.armyicon:
            if icon.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True
                if mouseup:
                    self.lastselected = icon.army
                    for hitbox in self.lastselected.hitbox:
                        hitbox.clicked()
                    if self.beforeselected is not None and self.beforeselected != self.lastselected:
                        for hitbox in self.beforeselected.hitbox:
                            hitbox.release()
                elif mouseright:
                    self.basecamerapos = pygame.Vector2(icon.army.basepos[0], icon.army.basepos[1])
                    self.camerapos = self.basecamerapos * self.camerascale
                break
        return self.clickany

    def buttonmouseover(self, mouseright):
        for button in self.buttonui:
            if button in self.allui and button.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True  # for avoiding clicking unit under ui
                break
        return self.clickany

    def leadermouseover(self, mouseright):
        leadermouseover = False
        for leader in self.leadernow:
            if leader.rect.collidepoint(self.mousepos):
                if leader.battalion.commander:
                    armyposition = self.leaderposname[leader.armyposition]
                else:
                    armyposition = self.leaderposname[leader.armyposition+4]
                self.leaderpopup.pop(self.mousepos, armyposition + ": " + leader.name)
                self.allui.add(self.leaderpopup)
                leadermouseover = True
                if mouseright:
                    self.popoutlorebook(8, leader.gameid)
                break
        return leadermouseover

    def effecticonmouseover(self, iconlist, mouseright):
        effectmouseover = False
        for icon in iconlist:
            if icon.rect.collidepoint(self.mousepos):
                checkvalue = self.gameui[2].value2[icon.type]
                self.effectpopup.pop(self.mousepos, checkvalue[icon.gameid])
                self.allui.add(self.effectpopup)
                effectmouseover = True
                if mouseright:
                    if icon.type == 0:  # Trait
                        section = 7
                    elif icon.type == 1:  # Skill
                        section = 6
                    else:
                        section = 5  # Status effect
                    self.popoutlorebook(section, icon.gameid)
                break
        return effectmouseover

    def camerafix(self):
        if self.camerapos[0] > self.mapshown.image.get_width():
            self.camerapos[0] = self.mapshown.image.get_width()
        elif self.camerapos[0] < 0:
            self.camerapos[0] = 0
        if self.camerapos[1] > self.mapshown.image.get_height():
            self.camerapos[1] = self.mapshown.image.get_height()
        elif self.camerapos[1] < 0:
            self.camerapos[1] = 0
        if self.basecamerapos[0] > 999: # camera cannot go further than 999 x
            self.basecamerapos[0] = 999
        elif self.basecamerapos[0] < 0: # camera cannot go less than 0 x
            self.basecamerapos[0] = 0
        if self.basecamerapos[1] > 999:  # same for y
            self.basecamerapos[1] = 999
        elif self.basecamerapos[1] < 0:
            self.basecamerapos[1] = 0

    def rungame(self):
        self.setuparmyicon()
        while True: # game running
            self.fpscount.fpsshow(self.clock)
            keypress = None
            self.mousepos = pygame.mouse.get_pos() # current mouse pos based on screen
            mouse_up = False # left click
            mouse_down = False # hold left click
            mouse_right = False # right click
            double_mouse_right = False # double right click
            keystate = pygame.key.get_pressed()
            for event in pygame.event.get():  # get event that happen
                if event.type == QUIT: # quit game
                    self.allui.clear(self.screen, self.background)
                    self.allcamera.clear(self.screen, self.background)
                    pygame.quit()
                    sys.exit()
                elif event.type == self.SONG_END: # change music track
                    # pygame.mixer.music.unload()
                    self.pickmusic = random.randint(1, 1)
                    pygame.mixer.music.load(self.musiclist[self.pickmusic])
                    pygame.mixer.music.play(0)
                elif event.type == KEYDOWN and event.key == K_ESCAPE: # open/close menu
                    if self.gamestate == 1: # in battle
                        self.gamestate = 0 # open munu
                        self.allui.add(self.battlemenu) # add menu to drawer
                        self.allui.add(*self.battlemenubutton) # add menu button to drawer
                    else: # in menu
                        if self.battlemenu.mode in (0,1):  # in menu or option
                            if self.battlemenu.mode == 1: # option menu
                                self.mixervolume = self.oldsetting
                                pygame.mixer.music.set_volume(self.mixervolume)
                                self.slidermenu[0].update(self.mixervolume, self.valuebox[0], forcedvalue=True)
                                self.battlemenu.changemode(0)
                            self.allui.remove(self.battlemenu)
                            self.allui.remove(*self.battlemenubutton)
                            self.allui.remove(*self.optionmenubutton)
                            self.allui.remove(*self.slidermenu)
                            self.allui.remove(*self.valuebox)
                            self.gamestate = 1
                        elif self.battlemenu.mode == 2: # encyclopedia
                            self.allui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll, self.lorenamelist)
                            for name in self.subsectionname:
                                name.kill()
                                del name
                            self.battlemenu.changemode(0)
                            if self.battlemenu not in self.allui:
                                self.gamestate = 1
                if pygame.mouse.get_pressed()[0]:  # Hold left click
                    mouse_down = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # left click
                        mouse_up = True
                    elif event.button == 4: # Mouse scroll down
                        if self.gamestate == 0 and self.battlemenu.mode == 2:  # Scrolling at lore book subsection list
                            if self.lorenamelist.rect.collidepoint(self.mousepos):
                                self.lorebook.currentsubsectionrow -= 1
                                if self.lorebook.currentsubsectionrow < 0:
                                    self.lorebook.currentsubsectionrow = 0
                                else:
                                    self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname)
                                    self.lorescroll.changeimage(newrow=self.lorebook.currentsubsectionrow)
                    elif event.button == 5: # Mouse scroll up
                        if self.gamestate == 0 and self.battlemenu.mode == 2:  # Scrolling at lore book subsection list
                            if self.lorenamelist.rect.collidepoint(self.mousepos):
                                self.lorebook.currentsubsectionrow += 1
                                if self.lorebook.currentsubsectionrow + self.lorebook.maxsubsectionshow - 1 < self.lorebook.logsize:
                                    self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname)
                                    self.lorescroll.changeimage(newrow=self.lorebook.currentsubsectionrow)
                                else:
                                    self.lorebook.currentsubsectionrow -= 1

                #v register user input during gameplay
                if self.gamestate == 1: # game in battle state
                    #v Mouse input
                    if event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 3:  # Right Click
                            mouse_right = True
                            if self.mousetimer == 0:
                                self.mousetimer = 0.001  # Start timer after first mouse click
                            elif self.mousetimer < 0.3: # if click again within 0.3 second for it to be considered double click
                                double_mouse_right = True # double right click
                                self.mousetimer = 0
                        elif event.button == 4: # Mouse scroll up
                            if self.eventlog.rect.collidepoint(self.mousepos):  # Scrolling when mouse at event log
                                self.eventlog.currentstartrow -= 1
                                if self.eventlog.currentstartrow < 0: # can go no further than the first log
                                    self.eventlog.currentstartrow = 0
                                else:
                                    self.eventlog.recreateimage() # recreate eventlog image
                                    self.logscroll.changeimage(newrow=self.eventlog.currentstartrow)
                            elif self.armyselector.rect.collidepoint(self.mousepos):  # Scrolling when mouse at army selector
                                self.armyselector.currentrow -= 1
                                if self.armyselector.currentrow < 0:
                                    self.armyselector.currentrow = 0
                                else:
                                    self.setuparmyicon()
                                    self.selectscroll.changeimage(newrow=self.armyselector.currentrow)
                            else:  # Scrolling in game map to zoom
                                self.camerascale += 1
                                if self.camerascale > 10:
                                    self.camerascale = 10
                                else:
                                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                                    self.mapshown.changescale(self.camerascale)
                        elif event.button == 5: # Mouse scroll down
                            if self.eventlog.rect.collidepoint(self.mousepos):  # Scrolling when mouse at event log
                                self.eventlog.currentstartrow += 1
                                if self.eventlog.currentstartrow + self.eventlog.maxrowshow - 1 < self.eventlog.lencheck and self.eventlog.lencheck > 9:
                                    self.eventlog.recreateimage()
                                    self.logscroll.changeimage(newrow=self.eventlog.currentstartrow)
                                else:
                                    self.eventlog.currentstartrow -= 1
                            elif self.armyselector.rect.collidepoint(self.mousepos):  # Scrolling when mouse at army selector ui
                                self.armyselector.currentrow += 1
                                if self.armyselector.currentrow < self.armyselector.logsize:
                                    self.setuparmyicon()
                                    self.selectscroll.changeimage(newrow=self.armyselector.currentrow)
                                else:
                                    self.armyselector.currentrow -= 1
                                    if self.armyselector.currentrow < 0:
                                        self.armyselector.currentrow = 0
                            else:  # Scrolling in game map to zoom
                                self.camerascale -= 1
                                if self.camerascale < 1:
                                    self.camerascale = 1
                                else:
                                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                                    self.mapshown.changescale(self.camerascale)
                    #^ End mouse input

                    #v keyboard input
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_TAB:
                            if self.mapviewmode == 0:  # Currently in normal mode
                                self.mapviewmode = 1
                                self.showmap.changemode(self.mapviewmode)
                            else:  # Currently in height mode
                                self.mapviewmode = 0
                                self.showmap.changemode(self.mapviewmode)
                            self.mapshown.changescale(self.camerascale)
                        elif event.key == pygame.K_p:  # Speed Pause/unpause Button
                            if self.gamespeed >= 0.5: #
                                self.gamespeed = 0 # pause game speed
                            else: # speed currently pause
                                self.gamespeed = 1 # unpause game and set to speed 1
                            self.speednumber.speedupdate(self.gamespeed)
                        elif event.key == pygame.K_KP_MINUS: # reduce game speed
                            newindex = self.gamespeedset.index(self.gamespeed) - 1
                            if newindex >= 0: # cannot reduce game speed than what is available
                                self.gamespeed = self.gamespeedset[newindex]
                            self.speednumber.speedupdate(self.gamespeed)
                        elif event.key == pygame.K_KP_PLUS: # increase game speed
                            newindex = self.gamespeedset.index(self.gamespeed) + 1
                            if newindex < len(self.gamespeedset):  # cannot increase game speed than what is available
                                self.gamespeed = self.gamespeedset[newindex]
                            self.speednumber.speedupdate(self.gamespeed)
                        elif event.key == pygame.K_PAGEUP:  # Go to top of event log
                            self.eventlog.currentstartrow = 0
                            self.eventlog.recreateimage()
                            self.logscroll.changeimage(newrow=self.eventlog.currentstartrow)
                        elif event.key == pygame.K_PAGEDOWN:  # Go to bottom of event log
                            if self.eventlog.lencheck > self.eventlog.maxrowshow:
                                self.eventlog.currentstartrow = self.eventlog.lencheck - self.eventlog.maxrowshow
                                self.eventlog.recreateimage()
                                self.logscroll.changeimage(newrow=self.eventlog.currentstartrow)
                        elif event.key == pygame.K_SPACE and self.lastselected is not None:
                            whoinput.command(self.battlemousepos, mouse_right, double_mouse_right,
                                             self.lastmouseover, keystate, othercommand=1)

                        #v FOR DEVELOPMENT DELETE LATER
                        elif event.key == pygame.K_1:
                            self.textdrama.queue.append('Hello and Welcome to update video')
                        elif event.key == pygame.K_2:
                            self.textdrama.queue.append('Showcase: Changes made since the previous update')
                        elif event.key == pygame.K_3:
                            self.textdrama.queue.append('Not yet balanced for completely historical enactment')
                        elif event.key == pygame.K_4:
                            self.textdrama.queue.append('The larger the battalion the harder it is to controlled')
                        elif event.key == pygame.K_5:
                            self.textdrama.queue.append('Weather effect affect the unit in many ways')
                        elif event.key == pygame.K_6:
                            self.textdrama.queue.append('Current special effect still need rework')
                        elif event.key == pygame.K_n and self.lastselected is not None:
                            if whoinput.team == 1:
                                self.allunitindex = whoinput.switchfaction(self.team1army, self.team2army, self.team1poslist, self.allunitindex,
                                                                           self.enactment)
                            else:
                                self.allunitindex = whoinput.switchfaction(self.team2army, self.team1army, self.team2poslist, self.allunitindex,
                                                                           self.enactment)
                        elif event.key == pygame.K_l and self.lastselected is not None:
                            for squad in whoinput.squadsprite:
                                squad.basemorale = 0
                        elif event.key == pygame.K_k and self.lastselected is not None:
                            for index, squad in enumerate(self.lastselected.squadsprite):
                                if index != 11:
                                    squad.unithealth -= squad.unithealth
                        elif event.key == pygame.K_m and self.lastselected is not None:
                            self.lastselected.leader[0].health -= 1000
                        #^ End For development test

                        else: # holding other keys
                            keypress = event.key
                    #^ End keyboard input
                #^ End register input

            self.allui.clear(self.screen, self.background)  # Clear sprite before update new one
            if self.gamestate == 1: # game in battle state
                self.uiupdater.update()  # update ui

                #v Camera movement
                if keystate[K_s] or self.mousepos[1] >= self.bottomcorner:  # Camera move down
                    self.basecamerapos[1] += 5 * (11 - self.camerascale) # need "11 -" for converting cameral scale so the further zoom camera move faster
                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale # resize camera pos
                    self.camerafix()
                elif keystate[K_w] or self.mousepos[1] <= 5:  # Camera move up
                    self.basecamerapos[1] -= 5 * (11 - self.camerascale)
                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                    self.camerafix()
                if keystate[K_a] or self.mousepos[0] <= 5:  # Camera move left
                    self.basecamerapos[0] -= 5 * (11 - self.camerascale)
                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                    self.camerafix()
                elif keystate[K_d] or self.mousepos[0] >= self.rightcorner:  # Camera move right
                    self.basecamerapos[0] += 5 * (11 - self.camerascale)
                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                    self.camerafix()
                self.cameraupcorner = (self.camerapos[0] - self.centerscreen[0], self.camerapos[1] - self.centerscreen[1]) # calculate top left corner of camera position
                #^ End camera movement

                self.battlemousepos[0] = pygame.Vector2((self.mousepos[0] - self.centerscreen[0]) + self.camerapos[0],
                                                        self.mousepos[1] - self.centerscreen[1] + self.camerapos[1]) # mouse pos on the map based on camare position
                self.battlemousepos[1] = self.battlemousepos[0] / self.camerascale # mouse pos on the map at current camera zoom scale
                if self.mousetimer != 0: # player click mouse once before
                    self.mousetimer += self.uidt # increase timer for mouse click using real time
                    if self.mousetimer >= 0.3: # time pass 0.3 second no longer count as double click
                        self.mousetimer = 0
                if self.terraincheck in self.allui and (
                        self.terraincheck.pos != self.mousepos or keystate[K_s] or keystate[K_w] or keystate[K_a] or keystate[K_d]):
                    self.allui.remove(self.terraincheck) # remove terrain popup when move mouse or camera
                if mouse_up or mouse_right or mouse_down:
                    self.uiclick = False # reset mouse check on ui, if stay false it mean mouse click is not on any ui
                    if mouse_up:
                        self.clickany = False
                        self.newarmyclick = False
                    if self.minimap.rect.collidepoint(self.mousepos):
                        if mouse_up:
                            posmask = pygame.Vector2(int(self.mousepos[0] - self.minimap.rect.x), int(self.mousepos[1] - self.minimap.rect.y))
                            self.basecamerapos = posmask * 5
                            self.camerapos = self.basecamerapos * self.camerascale
                            self.clickany = True
                        elif mouse_right:
                            if self.lastselected is not None:
                                self.uiclick = True
                    elif self.logscroll.rect.collidepoint(self.mousepos):  # Must check mouse collide for scroller before event log ui
                        self.clickany = True
                        self.uiclick = True
                        if mouse_down or mouse_up:
                            newrow = self.logscroll.update(self.mousepos)
                            if self.eventlog.currentstartrow != newrow:
                                self.eventlog.currentstartrow = newrow
                                self.eventlog.recreateimage()
                    elif self.selectscroll.rect.collidepoint(self.mousepos):  # Must check mouse collide for scroller before army select ui
                        self.clickany = True
                        self.uiclick = True
                        if mouse_down or mouse_up:
                            newrow = self.selectscroll.update(self.mousepos)
                            if self.armyselector.currentrow != newrow:
                                self.armyselector.currentrow = newrow
                                self.setuparmyicon()
                    elif self.eventlog.rect.collidepoint(self.mousepos): # check mouse collide for event log ui
                        self.clickany = True
                        self.uiclick = True
                    elif self.timeui.rect.collidepoint(self.mousepos): # check mouse collide for time bar ui
                        self.clickany = True
                        self.uiclick = True
                    elif self.armyselector.rect.collidepoint(self.mousepos): # check mouse collide for army selector ui
                        self.armyiconmouseover(mouse_up, mouse_right)
                    elif self.uimouseover(): # check mouse collide for other ui
                        pass
                    elif self.buttonmouseover(mouse_right): # check mouse collide for button
                        pass
                    elif mouse_right and self.lastselected is None and self.uiclick == False: # draw terrain popup ui when right click at map with no selected battalion
                        if self.battlemousepos[1][0] >= 0 and self.battlemousepos[1][0] <= 999 and self.battlemousepos[1][1] >= 0 and \
                                self.battlemousepos[1][1] <= 999: # not draw if pos is off the map
                            terrainpop, featurepop = self.battlemapfeature.getfeature(self.battlemousepos[1], self.battlemap)
                            featurepop = self.battlemapfeature.featuremod[featurepop]
                            heightpop = self.battlemapheight.getheight(self.battlemousepos[1])
                            self.terraincheck.pop(self.mousepos, featurepop, heightpop)
                            self.allui.add(self.terraincheck)
                    for index, button in enumerate(self.screenbuttonlist):  # Event log button and timer button click
                        if button.rect.collidepoint(self.mousepos):
                            if index in (0, 1, 2, 3, 4, 5):  # eventlog button
                                self.uiclick = True
                                if mouse_up:
                                    if button.event in (0, 1, 2, 3): # change tab mode
                                        self.eventlog.changemode(button.event)
                                    elif button.event == 4: # delete tab log button
                                        self.eventlog.cleartab()
                                    elif button.event == 5: # delete all tab log button
                                        self.eventlog.cleartab(alltab=True)
                            elif index in (6, 7, 8):  # timer button
                                self.uiclick = True
                                if mouse_up:
                                    if button.event == 0: # pause button
                                        self.gamespeed = 0
                                    elif button.event == 1: # reduce speed button
                                        newindex = self.gamespeedset.index(self.gamespeed) - 1
                                        if newindex >= 0:
                                            self.gamespeed = self.gamespeedset[newindex]
                                    elif button.event == 2: # increase speed button
                                        newindex = self.gamespeedset.index(self.gamespeed) + 1
                                        if newindex < len(self.gamespeedset):
                                            self.gamespeed = self.gamespeedset[newindex]
                                    self.speednumber.speedupdate(self.gamespeed)
                            break

                #v Event log timer
                if self.eventschedule is not None and self.eventlist != [] and self.timenumber.timenum >= self.eventschedule:
                    self.eventlog.addlog(None,None,eventmapid=self.eventmapid)
                    for event in self.eventlog.mapevent:
                        if self.eventlog.mapevent[event][3] is not None and self.eventlog.mapevent[event][3] > self.timenumber.timenum:
                            self.eventmapid = event
                            self.eventschedule = self.eventlog.mapevent[event][3]
                            break
                    self.eventlist = self.eventlist[1:]
                #^ End event log timer

                #v Weather system
                if self.weatherschedule is not None and self.timenumber.timenum >= self.weatherschedule:
                    del self.currentweather
                    weather = self.weatherevent[0]
                    if weather[0] != 0:
                        self.currentweather = gameweather.Weather(self.timeui, weather[0], weather[2], self.allweather)
                    else: # Random weather
                        self.currentweather = gameweather.Weather(self.timeui, random.randint(0, 11), random.randint(0, 2), self.allweather)
                    self.weatherevent.pop(0)
                    try: # Get end time of next event which is now index 0
                        self.weatherschedule = self.weatherevent[0][1]
                    except:
                        self.weatherschedule = None
                if self.currentweather.spawnrate > 0 and len(self.weathermatter) < self.currentweather.speed:
                    spawnnum = range(0, int(self.currentweather.spawnrate * self.dt * random.randint(0, 10))) # number of sprite to spawn at this time
                    for spawn in spawnnum: # spawn each weather sprite
                        truepos = (random.randint(10, SCREENRECT.width), 0) # starting pos
                        target = (truepos[0], SCREENRECT.height) # final target pos
                        if self.currentweather.spawnangle == 225: # top right to bottom left movement
                            startpos = random.randint(10, SCREENRECT.width * 2) # starting x pos that can be higher than screen width
                            truepos = (startpos, 0)
                            if startpos >= SCREENRECT.width: # x higher than screen width will spawn on the right corner of screen but not at top
                                startpos = SCREENRECT.width # revert x back to screen width
                                truepos = (startpos, random.randint(0, SCREENRECT.height))
                            if truepos[1] > 0:  # start position simulate from beyond top right of screen
                                target = (truepos[1] * self.weatherscreenadjust, SCREENRECT.height)
                            elif truepos[0] < SCREENRECT.width:  # start position inside screen width
                                target = (0, truepos[0] / self.weatherscreenadjust)
                        elif self.currentweather.spawnangle == 270: # right to left movement
                            truepos = (SCREENRECT.width, random.randint(0, SCREENRECT.height))
                            target = (0, truepos[1])
                        randompic = random.randint(0, len(self.weathermatterimgs[self.currentweather.type]) - 1)
                        self.weathermatter.add(gameweather.Mattersprite(truepos, target,
                                                                        self.currentweather.speed,
                                                                        self.weathermatterimgs[self.currentweather.type][randompic]))
                if self.currentweather.specialeffect > 0: # weather has special effect to draw
                    if len(self.weathereffect) == 0: # spawn effect (only one)
                        truepos = (SCREENRECT.width, SCREENRECT.height / 2)
                        target = (-SCREENRECT.width, SCREENRECT.height / 2)
                        self.weathereffect.add(gameweather.Specialeffect(truepos, target, self.currentweather.speed,
                                                                         self.weathereffectimgs[self.currentweather.type][self.currentweather.level],
                                                                         self.weatherschedule))
                    # elif len(self.weathereffect) == 1:
                    #     for weathereffect in self.weathereffect:
                    #         if weathereffect.rect.center[0] <= SCREENRECT.width+100:
                    #             truepos = (weathereffect.rect.midright[0], SCREENRECT.height / 2)
                    #             target = (-SCREENRECT.width, SCREENRECT.height / 2)
                    #             self.weathereffect.add(gameweather.Specialeffect(truepos, target, self.currentweather.speed,
                    #                                                              self.weathereffectimgs[self.currentweather.type][
                    #                                                                  self.currentweather.level]))
                #^ End weather system

                #v code that only run when any unit is selected
                if self.lastselected is not None and self.lastselected.state != 100:
                    whoinput = self.lastselected
                    if self.beforeselected is None:  # add back the pop up ui to group so it get shown when click unit with none selected before
                        self.gameui = self.popgameui
                        self.allui.add(*self.gameui[0:2])  # add leader and top ui
                        self.allui.add(self.inspectbutton)  # add inspection ui open/close button
                        self.allui.add(self.buttonui[7])  # add decimation button
                        self.allui.add(*self.switchbuttonui[0:6])  # add battalion behaviour change button
                        self.switchbuttonui[0].event = whoinput.useskillcond
                        self.switchbuttonui[1].event = whoinput.fireatwill
                        self.switchbuttonui[2].event = whoinput.hold
                        self.switchbuttonui[3].event = whoinput.useminrange
                        self.switchbuttonui[4].event = whoinput.shoothow
                        self.switchbuttonui[5].event = whoinput.runtoggle
                        self.leadernow = whoinput.leader
                        self.allui.add(*self.leadernow)
                        self.checksplit(whoinput)
                        self.gameui[0].valueinput(who=whoinput, splithappen=self.splithappen)
                        self.gameui[1].valueinput(who=whoinput, splithappen=self.splithappen)
                    elif self.beforeselected != self.lastselected:  # change ui when click other battalion
                        if self.inspectui == True:
                            self.newarmyclick = True
                            self.allui.remove(*self.showingsquad)
                            self.showingsquad = whoinput.squadsprite
                            self.squadlastselected = self.showingsquad[0]
                            self.squadselectedborder.pop(self.squadlastselected.inspposition)
                            self.allui.add(self.squadselectedborder)
                            self.gameui[2].valueinput(who=self.squadlastselected, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                      splithappen=self.splithappen)
                        self.checksplit(whoinput)
                        self.allui.remove(*self.leadernow)
                        self.switchbuttonui[0].event = whoinput.useskillcond
                        self.switchbuttonui[1].event = whoinput.fireatwill
                        self.switchbuttonui[2].event = whoinput.hold
                        self.switchbuttonui[3].event = whoinput.useminrange
                        self.switchbuttonui[4].event = whoinput.shoothow
                        self.switchbuttonui[5].event = whoinput.runtoggle
                        self.leadernow = whoinput.leader
                        self.allui.add(*self.leadernow)
                        self.gameui[0].valueinput(who=whoinput, splithappen=self.splithappen)
                        self.gameui[1].valueinput(who=whoinput, splithappen=self.splithappen)
                    else: # Update topbar and command ui value every 1.1 seconds
                        if self.uitimer >= 1.1:
                            self.gameui[0].valueinput(who=whoinput, splithappen=self.splithappen)
                            self.gameui[1].valueinput(who=whoinput, splithappen=self.splithappen)
                    if self.inspectbutton.rect.collidepoint(self.mousepos) or (
                            mouse_up and self.inspectui and self.newarmyclick):
                        if self.inspectbutton.rect.collidepoint(self.mousepos):
                            self.buttonnamepopup.pop(self.mousepos, "Inspect Squad")
                            self.allui.add(self.buttonnamepopup)
                        if mouse_up:
                            if self.inspectui == False:  # Add army inspect ui when left click at ui button or when change unit with inspect open
                                self.inspectui = True
                                self.allui.add(*self.gameui[2:4])
                                self.allui.add(*self.unitcardbutton)
                                self.showingsquad = whoinput.squadsprite
                                self.squadlastselected = self.showingsquad[0]
                                self.squadselectedborder.pop(self.squadlastselected.inspposition)
                                self.allui.add(self.squadselectedborder)
                                self.gameui[2].valueinput(who=self.squadlastselected, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                            splithappen=self.splithappen)
                            elif self.inspectui:  # Remove when click again and the ui already open
                                self.allui.remove(*self.showingsquad)
                                self.allui.remove(self.squadselectedborder)
                                self.showingsquad = []
                                for ui in self.gameui[2:4]: ui.kill()
                                for button in self.unitcardbutton: button.kill()
                                self.inspectui = False
                                self.newarmyclick = False
                    elif self.gameui[1] in self.allui and self.gameui[1].rect.collidepoint(self.mousepos):
                        if self.switchbuttonui[0].rect.collidepoint(self.mousepos) or keypress == pygame.K_g:
                            if mouse_up or keypress == pygame.K_g:  # rotate skill condition when clicked
                                whoinput.useskillcond += 1
                                if whoinput.useskillcond > 3:
                                    whoinput.useskillcond = 0
                                self.switchbuttonui[0].event = whoinput.useskillcond
                            if self.switchbuttonui[0].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                poptext = ("Free Skill Use", "Conserve 50% Stamina", "Conserve 25% stamina", "Forbid Skill")
                                self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[0].event])
                                self.allui.add(self.buttonnamepopup)
                        elif self.switchbuttonui[1].rect.collidepoint(self.mousepos) or keypress == pygame.K_f:
                            if mouse_up or keypress == pygame.K_f:  # rotate fire at will condition when clicked
                                whoinput.fireatwill += 1
                                if whoinput.fireatwill > 1:
                                    whoinput.fireatwill = 0
                                self.switchbuttonui[1].event = whoinput.fireatwill
                            if self.switchbuttonui[1].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                poptext = ("Fire at will", "Hold fire until order")
                                self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[1].event])
                                self.allui.add(self.buttonnamepopup)
                        elif self.switchbuttonui[2].rect.collidepoint(self.mousepos) or keypress == pygame.K_h:
                            if mouse_up or keypress == pygame.K_h:  # rotate hold condition when clicked
                                whoinput.hold += 1
                                if whoinput.hold > 2:
                                    whoinput.hold = 0
                                self.switchbuttonui[2].event = whoinput.hold
                            if self.switchbuttonui[2].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                poptext = ("Aggressive", "Skirmish/Scout", "Hold Ground")
                                self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[2].event])
                                self.allui.add(self.buttonnamepopup)
                        elif self.switchbuttonui[3].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                            if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                whoinput.useminrange += 1
                                if whoinput.useminrange > 1:
                                    whoinput.useminrange = 0
                                self.switchbuttonui[3].event = whoinput.useminrange
                            if self.switchbuttonui[3].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                poptext = ("Shoot from min range", "Shoot from max range")
                                self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[3].event])
                                self.allui.add(self.buttonnamepopup)
                        elif self.switchbuttonui[4].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                            if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                whoinput.shoothow += 1
                                if whoinput.shoothow > 2:
                                    whoinput.shoothow = 0
                                self.switchbuttonui[4].event = whoinput.shoothow
                            if self.switchbuttonui[4].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                poptext = ("Allow both arc and direct shot", "Allow only arc shot", "Allow only direct shot")
                                self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[4].event])
                                self.allui.add(self.buttonnamepopup)
                        elif self.switchbuttonui[5].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                            if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                whoinput.runtoggle += 1
                                if whoinput.runtoggle > 1:
                                    whoinput.runtoggle = 0
                                self.switchbuttonui[5].event = whoinput.runtoggle
                            if self.switchbuttonui[5].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                poptext = ("Toggle walk", "Toggle run")
                                self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[5].event])
                                self.allui.add(self.buttonnamepopup)
                        elif self.colsplitbutton in self.allui and self.colsplitbutton.rect.collidepoint(self.mousepos):
                            self.buttonnamepopup.pop(self.mousepos, "Split by middle column")
                            self.allui.add(self.buttonnamepopup)
                            if mouse_up and whoinput.basepos.distance_to(list(whoinput.neartarget.values())[0]) > 50:
                                self.splitunit(self, whoinput, 1)
                                self.splithappen = True
                                self.checksplit(whoinput)
                                self.allui.remove(*self.leadernow)
                                self.leadernow = whoinput.leader
                                self.allui.add(*self.leadernow)
                                self.setuparmyicon()
                        elif self.rowsplitbutton in self.allui and self.rowsplitbutton.rect.collidepoint(self.mousepos):
                            self.buttonnamepopup.pop(self.mousepos, "Split by middle row")
                            self.allui.add(self.buttonnamepopup)
                            if mouse_up and whoinput.basepos.distance_to(list(whoinput.neartarget.values())[0]) > 50:
                                self.splitunit(self, whoinput, 0)
                                self.splithappen = True
                                self.checksplit(whoinput)
                                self.allui.remove(*self.leadernow)
                                self.leadernow = whoinput.leader
                                self.allui.add(*self.leadernow)
                                self.setuparmyicon()
                        elif self.buttonui[7].rect.collidepoint(self.mousepos):  # decimation effect
                            self.buttonnamepopup.pop(self.mousepos, "Decimation")
                            self.allui.add(self.buttonnamepopup)
                            if mouse_up and whoinput.state == 0:
                                for squad in whoinput.squadsprite:
                                    squad.statuseffect[98] = self.gameunitstat.statuslist[98].copy()
                                    squad.unithealth -= round(squad.unithealth * 0.1)
                        elif self.leadermouseover(mouse_right):
                            self.allui.remove(self.buttonnamepopup)
                            pass
                    else:
                        self.allui.remove(self.leaderpopup) # remove leader name popup if no mouseover on any button
                        self.allui.remove(self.buttonnamepopup)  # remove popup if no mouseover on any button
                    if self.inspectui: # if inspect ui is openned
                        self.allui.add(*self.showingsquad)
                        if mouse_up or mouse_right:
                            if self.gameui[3].rect.collidepoint(self.mousepos): # if mouse pos inside armybox ui when click
                                self.clickany = True # for avoding right click or  unit
                                self.uiclick = True  # for avoiding clicking unit under ui
                                for squad in self.showingsquad:
                                    if squad.rect.collidepoint(self.mousepos):  # Change showing stat to the clicked squad one
                                        if mouse_up:
                                            squad.command(self.battlemousepos, mouse_up, mouse_right, self.squadlastselected.wholastselect)
                                            self.squadlastselected = squad
                                            self.squadselectedborder.pop(squad.inspposition)
                                            self.eventlog.addlog(
                                                [0, str(self.squadlastselected.boardpos) + " " + str(self.squadlastselected.name) + " in " +
                                                 self.squadlastselected.battalion.leader[0].name + "'s battalion is clicked"], [3])
                                            self.allui.add(self.squadselectedborder)
                                            self.gameui[2].valueinput(who=squad, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                                      splithappen=self.splithappen)
                                            if self.gameui[2].option == 2:
                                                self.traitskillblit()
                                                self.effecticonblit()
                                                self.countdownskillicon()
                                            else:
                                                for icon in self.skillicon.sprites(): icon.kill()
                                                for icon in self.effecticon.sprites(): icon.kill()
                                        elif mouse_right:
                                            self.popoutlorebook(3, squad.unitid)
                                        break
                            elif self.gameui[2].rect.collidepoint(self.mousepos):
                                self.clickany = True
                                self.uiclick = True  # for avoiding clicking unit under ui
                                for button in self.unitcardbutton:  # Change unit card option based on button clicking
                                    if button.rect.collidepoint(self.mousepos):
                                        self.clickany = True
                                        self.uiclick = True
                                        if self.gameui[2].option != button.event:
                                            self.gameui[2].option = button.event
                                            self.gameui[2].valueinput(who=self.squadlastselected, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                                      changeoption=1, splithappen=self.splithappen)
                                            if self.gameui[2].option == 2:
                                                self.traitskillblit()
                                                self.effecticonblit()
                                                self.countdownskillicon()
                                            else:
                                                for icon in self.skillicon.sprites(): icon.kill()
                                                for icon in self.effecticon.sprites(): icon.kill()
                                        break
                        if (self.uitimer >= 1.1 and self.gameui[2].option != 0) or \
                                self.beforeselected != self.lastselected:  # Update value of the clicked squad
                            self.gameui[2].valueinput(who=self.squadlastselected, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                    splithappen=self.splithappen)
                            if self.gameui[2].option == 2:
                                self.countdownskillicon()
                                self.effecticonblit()
                                if self.beforeselected != self.lastselected:
                                    self.traitskillblit()
                                    self.countdownskillicon()
                            else:
                                for icon in self.skillicon.sprites(): icon.kill()
                                for icon in self.effecticon.sprites(): icon.kill()
                        if self.gameui[2].option == 2:
                            if self.effecticonmouseover(self.skillicon, mouse_right):
                                pass
                            elif self.effecticonmouseover(self.effecticon, mouse_right):
                                pass
                            else:
                                self.allui.remove(self.effectpopup)
                        if self.splithappen:  # change showing squad in inspectui if split happen
                            self.allui.remove(*self.showingsquad)
                            self.showingsquad = whoinput.squadsprite
                            self.allui.add(*self.showingsquad)
                            self.splithappen = False
                    else:
                        for icon in self.skillicon.sprites(): icon.kill()
                        for icon in self.effecticon.sprites(): icon.kill()
                    if (mouse_up or mouse_right) and self.uiclick == False: # Unit command
                        whoinput.command(self.battlemousepos, mouse_right, double_mouse_right,
                                         self.lastmouseover, keystate)
                    self.beforeselected = self.lastselected
                    if self.uitimer >= 1.1: # reset ui timer every 1.1 seconds
                        self.uitimer -= 1.1
                #^ End unit selected code

                self.lastmouseover = 0  # reset last battalion mouse over
                # fight_sound.play()

                #v Drama text function
                if self.dramatimer == 0 and len(self.textdrama.queue) != 0:  # Start timer and add to allui If there is event queue
                    self.allui.add(self.textdrama)
                    self.textdrama.processqueue()
                    self.dramatimer = 0.1
                elif self.dramatimer > 0:
                    self.textdrama.playanimation()
                    self.dramatimer += self.uidt
                    if self.dramatimer > 3:
                        self.dramatimer = 0
                        self.allui.remove(self.textdrama)
                #^ End drama

                #v Updater
                self.battalionupdater.update(self.currentweather, self.squad, self.dt, self.camerascale,
                                             self.battlemousepos[0], mouse_up)
                self.hitboxupdater.update(self.camerascale)
                self.leaderupdater.update()
                self.squadupdater.update(self.currentweather, self.dt, self.camerascale, self.combattimer)
                if self.combattimer >= 0.5: # reset combat timer every 0.5 seconds
                    self.combattimer -= 0.5 # not reset to 0 because higher speed can cause inconsistency in update timing
                    for squad in self.squad: # Reset every squad battleside after updater since doing it in updater cause bug for defender
                        squad.battleside = [None, None, None, None]  # Reset battleside to defualt
                        squad.battlesideid = [0, 0, 0, 0]
                for battalion in self.allunitlist: # same as squad battleside
                    battalion.battleside = [None, None, None, None]
                    battalion.battlesideid = [0, 0, 0, 0]
                    for hitbox in battalion.hitbox:
                        hitbox.collide = 0 # reset hitbox collision detection
                self.effectupdater.update(self.allunitlist, self.hitboxes, self.squad, self.squadindexlist, self.dt, self.camerascale)
                self.weatherupdater.update(self.dt, self.timenumber.timenum)
                self.camera.update(self.camerapos, self.allcamera)
                self.minimap.update(self.camerascale, [self.camerapos, self.cameraupcorner], self.team1poslist, self.team2poslist)
                #^ End updater

                #v Remove the unit ui when click at no group
                if self.clickany == False: # not click at any battalion
                    if self.lastselected is not None: # any battalion is selected
                        for hitbox in self.lastselected.hitbox:
                            hitbox.release() # change hitbox colour to non-selected one
                        self.lastselected = None # reset lastselected
                    self.gameui[2].option = 1 # reset unit card option
                    for ui in self.gameui: ui.kill() # remove ui
                    for button in self.buttonui[0:8]: button.kill() # remove button
                    for icon in self.skillicon.sprites(): icon.kill() # remove skill and trait icon
                    for icon in self.effecticon.sprites(): icon.kill() # remove effect icon
                    self.allui.remove(*self.switchbuttonui) # remove change battalion behaviour button
                    self.allui.remove(*self.showingsquad) # remove squad sprite in army inspect ui
                    self.showingsquad = [] # clear squad list in army inspect ui
                    self.inspectui = False # inspect ui close
                    self.beforeselected = None # reset before selected battalion after remove last selected
                    self.allui.remove(*self.leadernow) # remove leader image from command ui
                    self.squadlastselected = None # reset squad selected
                    self.allui.remove(self.squadselectedborder) # remove squad selected border sprite
                    self.leadernow = [] # clear leader list in command ui
                #^ End remove

                #v Update game time
                self.dt = self.clock.get_time() / 1000 # dt before gamespeed
                self.uitimer += self.dt # ui update by real time instead of game time to reduce workload
                self.uidt = self.dt # get ui timer before apply game speed
                self.dt = self.dt * self.gamespeed # apply dt with gamespeed for ingame calculation
                self.combattimer += self.dt # update combat timer
                self.timenumber.timerupdate(self.dt*5) # update ingame time with 5x speed
                #^ End update game time

            else: # Complete game pause either menu or enclycopedia
                if self.battlemenu.mode == 0: # main esc menu
                    for button in self.battlemenubutton:
                        if button.rect.collidepoint(self.mousepos):
                            button.image = button.images[1] # change button image to mouse over one
                            if mouse_up: # click on button
                                button.image = button.images[2] # change button image to clicked one
                                if button.text == "Resume": # resume game
                                    self.gamestate = 1 # resume battle gameplay state
                                    self.allui.remove(self.battlemenu, *self.battlemenubutton, *self.slidermenu, *self.valuebox) # remove menu sprite
                                elif button.text == "Encyclopedia": # open encyclopedia
                                    self.battlemenu.mode = 2 # change to enclycopedia mode
                                    self.allui.add(self.lorebook, self.lorenamelist, *self.lorebuttonui) # add sprite related to encyclopedia
                                    self.lorescroll = gameui.Uiscroller(self.lorenamelist.rect.topright, self.lorenamelist.image.get_height(),
                                                                        self.lorebook.maxsubsectionshow, layer=14) # add subsection list scroller
                                    self.lorebook.changesection(0, self.lorenamelist, self.subsectionname, self.lorescroll)
                                    # self.lorebook.setupsubsectionlist(self.lorenamelist, listgroup)
                                elif button.text == "Option": # open option menu
                                    self.battlemenu.changemode(1) # change to option menu mode
                                    self.allui.remove(*self.battlemenubutton) # remove main esc menu button
                                    self.allui.add(*self.optionmenubutton, *self.slidermenu, *self.valuebox)
                                    self.oldsetting = self.slidermenu[0].value  # Save previous setting for in case of cancel
                                elif button.text == "Main Menu": # back to main menu
                                    self.allui.clear(self.screen, self.background) # remove all sprite
                                    self.allcamera.clear(self.screen, self.background) # remove all sprite
                                    return # end battle game loop
                                elif button.text == "Desktop": # quit game
                                    self.allui.clear(self.screen, self.background) # remove all sprite
                                    self.allcamera.clear(self.screen, self.background) # remove all sprite
                                    sys.exit() # quit
                                break # found clicked button, break loop
                        else:
                            button.image = button.images[0]
                elif self.battlemenu.mode == 1: # option menu
                    for button in self.optionmenubutton: # check if any button get collided with mouse or clicked
                        if button.rect.collidepoint(self.mousepos):
                            button.image = button.images[1] # change button image to mouse over one
                            if mouse_up: # click on button
                                button.image = button.images[2] # change button image to clicked one
                                if button.text == "Confirm": # confirm button, save the setting and close option menu
                                    self.oldsetting = self.mixervolume # save mixer volume
                                    pygame.mixer.music.set_volume(self.mixervolume) # set new music player volume
                                    main.editconfig('DEFAULT', 'SoundVolume', str(slider.value), 'configuration.ini', config) # save to config file
                                    self.battlemenu.changemode(0) # go back to main esc menu
                                    self.allui.remove(*self.optionmenubutton, *self.slidermenu, *self.valuebox) # remove option menu sprite
                                    self.allui.add(*self.battlemenubutton) # add main esc menu buttons back
                                elif button.text == "Apply": # apply button, save the setting
                                    self.oldsetting = self.mixervolume # save mixer volume
                                    pygame.mixer.music.set_volume(self.mixervolume) # set new music player volume
                                    main.editconfig('DEFAULT', 'SoundVolume', str(slider.value), 'configuration.ini', config) # save to config file
                                elif button.text == "Cancel": # cancel button, revert the setting to the last saved one
                                    self.mixervolume = self.oldsetting # revert to old setting
                                    pygame.mixer.music.set_volume(self.mixervolume)  # set new music player volume
                                    self.slidermenu[0].update(self.mixervolume, self.valuebox[0], forcedvalue=True) # update slider bar
                                    self.battlemenu.changemode(0) # go back to main esc menu
                                    self.allui.remove(*self.optionmenubutton, *self.slidermenu, *self.valuebox) # remove option menu sprite
                                    self.allui.add(*self.battlemenubutton) # add main esc menu buttons back
                        else: # no button currently collided with mouse
                            button.image = button.images[0] # revert button image back to the idle one
                    for slider in self.slidermenu:
                        if slider.rect.collidepoint(self.mousepos) and (mouse_down or mouse_up): # mouse click on slider bar
                            slider.update(self.mousepos, self.valuebox[0]) # update slider button based on mouse value
                            self.mixervolume = float(slider.value / 100) # for now only music volume slider exist
                elif self.battlemenu.mode == 2:  # Encyclopedia mode
                    if mouse_up or mouse_down: # mouse down (hold click) only for subsection listscroller
                        if mouse_up:
                            for button in self.lorebuttonui:
                                if button.rect.collidepoint(self.mousepos): # click button
                                    if button.event in range(0, 11): # section button
                                        self.lorebook.changesection(button.event, self.lorenamelist, self.subsectionname, self.lorescroll) # change to section of that button
                                    elif button.event == 19:  # Close button
                                        self.allui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll, self.lorenamelist) # remove enclycopedia related sprites
                                        for name in self.subsectionname: # remove subsection name
                                            name.kill()
                                            del name
                                        self.battlemenu.changemode(0) # change menu back to default 0
                                        if self.battlemenu not in self.allui: # in case open encyclopedia via right click on icon or other way
                                            self.gamestate = 1 # resume gameplay
                                    elif button.event == 20:  # Previous page button
                                        if self.lorebook.page == 0: # cannot go pass the first page
                                            pass
                                        else:
                                            self.lorebook.changepage(self.lorebook.page - 1) # go back 1 page
                                    elif button.event == 21:  # Next page button
                                        if self.lorebook.page == self.lorebook.maxpage: # cannot go pass max page
                                            pass
                                        else:
                                            self.lorebook.changepage(self.lorebook.page + 1) # go forward 1 page
                                    break # found clicked button, break loop
                            for name in self.subsectionname: # too lazy to include break for button found to avoid subsection loop since not much optimisation is needed here
                                if name.rect.collidepoint(self.mousepos): # click on subsection name
                                    self.lorebook.changesubsection(name.subsection) # change subsection
                                    break # found clicked subsection, break loop
                        if self.lorescroll.rect.collidepoint(self.mousepos): # click on subsection list scroller
                            self.lorebook.currentsubsectionrow = self.lorescroll.update(self.mousepos) # update the scroller and get new current subsection
                            self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname) # update subsection name list
            self.screen.blit(self.camera.image, (0, 0))  # Draw the game in camera
            self.allui.draw(self.screen)  # Draw the UI
            # dirty = self.allui.draw(self.screen)
            pygame.display.update() # update game display, draw everything
            self.clock.tick(60) # clock update even if game pause
        if pygame.mixer: # close music player
            pygame.mixer.music.fadeout(1000)
        pygame.time.wait(1000) # wait a bit before closing
        pygame.quit()
