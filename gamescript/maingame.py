"""
## Known problem
another rare bug where squad easily get killed for some reason, can't seem to repricate it
autoplacement of 2 units somehow allow the other unit that stop from retreat to auto place to the enemy side already occupied
Optimise list
melee combat need to be optimised more
change all percentage calculation to float instead of int/100 if possible. Especially number from csv file
remove index and change call to the sprite itself
"""

import datetime
import glob
import random
import gc
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
    def __init__(self, main, winstyle):
        # pygame.init()  # Initialize pygame

        # v Get game object from main

        self.eventlog = main.eventlog
        self.battlecamera = main.battlecamera
        self.battlelui = main.battleui

        self.battalionupdater = main.battalionupdater
        self.hitboxupdater = main.hitboxupdater
        self.squadupdater = main.squadupdater
        self.leaderupdater = main.leaderupdater
        self.uiupdater = main.uiupdater
        self.weatherupdater = main.weatherupdater
        self.effectupdater = main.effectupdater

        self.battlemapbase = main.battlemapbase
        self.battlemapfeature = main.battlemapfeature
        self.battlemapheight = main.battlemapheight
        self.showmap = main.showmap

        self.team0army = main.team0army
        self.team1army = main.team1army
        self.team2army = main.team2army
        self.squad = main.squad
        self.armyleader = main.armyleader
        self.deadunit = main.deadunit

        self.hitboxes = main.hitboxes
        self.arrows = main.arrows
        self.directionarrows = main.directionarrows

        self.gameui = main.gameui
        self.popgameui = main.gameui  # saving list of gameui that will pop out when battalion is selected

        self.battlemapbase = main.battlemapbase
        self.battlemapfeature = main.battlemapfeature
        self.battlemapheight = main.battlemapheight
        self.showmap = main.showmap

        self.minimap = main.minimap
        self.eventlog = main.eventlog
        self.logscroll = main.logscroll
        self.buttonui = main.buttonui
        self.squadselectedborder = main.squadselectedborder
        self.switchbuttonui = main.switchbuttonui

        self.fpscount = main.fpscount

        self.terraincheck = main.terraincheck
        self.buttonnamepopup = main.buttonnamepopup
        self.leaderpopup = main.leaderpopup
        self.effectpopup = main.effectpopup
        self.textdrama = main.textdrama

        self.skillicon = main.skillicon
        self.effecticon = main.effecticon

        self.battlemenu = main.battlemenu
        self.battlemenubutton = main.battlemenubutton
        self.escoptionmenubutton = main.escoptionmenubutton

        self.armyselector = main.armyselector
        self.armyselector.currentrow = 0
        self.armyicon = main.armyicon
        self.selectscroll = main.selectscroll

        self.timeui = main.timeui
        self.timenumber = main.timenumber

        self.speednumber = main.speednumber

        self.weathermatter = main.weathermatter
        self.weathereffect = main.weathereffect

        self.lorebook = main.lorebook
        self.lorenamelist = main.lorenamelist
        self.lorebuttonui = main.lorebuttonui
        self.subsectionname = main.subsectionname
        self.pagebutton = main.pagebutton

        self.allweather = main.allweather
        self.weathermatterimgs = main.weathermatterimgs
        self.weathereffectimgs = main.weathereffectimgs

        self.featuremod = main.featuremod

        self.allfaction = main.allfaction
        self.coa = main.coa

        self.allweapon = main.allweapon
        self.allarmour = main.allarmour

        self.statusimgs = main.statusimgs
        self.roleimgs = main.roleimgs
        self.traitimgs = main.traitimgs
        self.skillimgs = main.skillimgs

        self.gameunitstat = main.gameunitstat
        self.leaderstat = main.leaderstat

        self.statetext = main.statetext

        self.squadwidth = main.squadwidth
        self.squadheight = main.squadheight

        self.escslidermenu = main.escslidermenu
        self.escvaluebox = main.escvaluebox
        # ^ End load from main

        self.bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)  # Set the display mode
        self.screen = pygame.display.set_mode(SCREENRECT.size, winstyle | pygame.RESIZABLE, self.bestdepth)  # set up game screen

        #v Assign default variable to some class
        gamebattalion.Unitarmy.maingame = self
        gamesquad.Unitsquad.maingame = self
        gameleader.Leader.maingame = self

        self.screenbuttonlist = main.buttonui[8:17]  # List of button always on screen (for now just eventlog)
        self.unitcardbutton = main.buttonui[0:4]
        self.inspectbutton = main.buttonui[4]
        self.colsplitbutton = main.buttonui[5]  # battalion split by column button
        self.rowsplitbutton = main.buttonui[6]  # battalion split by row button
        #^ End assign default

        self.background = pygame.Surface(SCREENRECT.size) # Create background image
        self.background.fill((255, 255, 255)) # fill background image with black colour

    def preparenew(self, ruleset, rulesetfolder, teamselected, enactment, mapselected, source, unitscale):

        self.ruleset = ruleset # current ruleset used
        self.rulesetfolder = rulesetfolder # the folder of rulseset used
        self.mapselected = mapselected # map folder name
        self.source = str(source)
        self.unitscale = unitscale
        self.playerteam = teamselected # player selected team

        #v load the sound effects
        # boom_sound = load_sound('boom.wav')
        # shoot_sound = load_sound('car_door.wav')
        #^ End load sound effect

        #v Random music played from list
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer = None
        if pygame.mixer:
            self.SONG_END = pygame.USEREVENT + 1
            # musiclist = os.path.join(main_dir, 'data/sound/')
            self.musiclist = glob.glob(main_dir + '/data/sound/music/*.mp3')
            self.pickmusic = random.randint(1, 1)
            pygame.mixer.music.set_endevent(self.SONG_END)
            pygame.mixer.music.load(self.musiclist[self.pickmusic])
            pygame.mixer.music.play(0)
        #^ End music play

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

        try:  # get new map event for event log
            mapevent = csv_read('eventlog.csv', ["data", 'ruleset', self.rulesetfolder.strip("/"), 'map', self.mapselected], 0)
            gameui.Eventlog.mapevent = mapevent
        except:  # can't find any event file
            mapevent = {}  # create empty list

        self.eventlog.makenew() # reset old event log

        self.eventlog.addeventlog(mapevent)

        self.eventschedule = None
        self.eventlist = []
        for index, event in enumerate(self.eventlog.mapevent):
            if self.eventlog.mapevent[event][3] is not None:
                if index == 0:
                    self.eventmapid = event
                    self.eventschedule = self.eventlog.mapevent[event][3]
                self.eventlist.append(event)

        self.timenumber.startsetup(self.weatherschedule)

        #v Create the battle map
        self.camerapos = pygame.Vector2(500, 500)  # Camera pos at the current zoom, start at center of map
        self.basecamerapos = pygame.Vector2(500, 500)  # Camera pos at furthest zoom for recalculate sprite pos after zoom
        self.camerascale = 1  # Camera zoom
        gamecamera.Camera.SCREENRECT = SCREENRECT
        self.camera = gamecamera.Camera(self.camerapos, self.camerascale)

        imgs = load_images(['ruleset', self.rulesetfolder.strip("/"), 'map', self.mapselected], loadorder=False)
        self.battlemapbase.drawimage(imgs[0])
        self.battlemapfeature.drawimage(imgs[1])
        self.battlemapheight.drawimage(imgs[2])
        self.showmap.drawimage(self.battlemapbase, self.battlemapfeature, self.battlemapheight, imgs[3])
        #^ End create battle map

        self.minimap.drawimage(self.showmap.trueimage, self.camera)

        #v Create Starting Values
        self.mixervolume = SoundVolume
        self.leaderposname = ("Commander","Sub-General","Sub-General","Sub-Commander","General","Sub-General","Sub-General","Advisor") # Name of leader position in battalion, the first 4 is for commander battalion
        self.enactment = enactment # enactment mod, control both team
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
        self.leadernow = [] # list of showing leader in command ui
        self.uiclick = False # for checking if mouse click is on ui
        self.clickany = False  # For checking if mouse click on anything, if not close ui related to battalion
        self.newarmyclick = False  #  For checking if another unit is clicked when inspect ui open
        self.inspectui = False # For checking if inspect ui is currently open or not
        self.lastselected = None # Which army is selected last update loop
        self.mapviewmode = 0 # default, another one show height map
        self.mapshown = self.showmap
        self.squadlastselected = None # which squad in inspect ui is selected in last update loop
        self.beforeselected = None # Which army is selected before
        self.splithappen = False # Check if battalion get split in that loop
        self.currentweather = None
        self.weatherscreenadjust = SCREENRECT.width / SCREENRECT.height # for weather sprite spawn position
        self.splitunit = gamelongscript.splitunit
        self.losscal = gamelongscript.losscal
        self.rightcorner = SCREENRECT.width - 5
        self.bottomcorner = SCREENRECT.height - 5
        self.centerscreen = [SCREENRECT.width / 2, SCREENRECT.height / 2] # center position of the screen
        self.battlemousepos = [0, 0] # mouse position list in game not screen, the first without zoom and the second with camera zoom adjust
        #^ End start value

        #v initialise starting unit sprites
        self.inspectuipos = [self.gameui[0].rect.bottomleft[0] - self.squadwidth / 1.25,
                             self.gameui[0].rect.bottomleft[1] - self.squadheight / 3]
        gamelongscript.unitsetup(self)

        self.allunitlist = []
        for group in (self.team0army, self.team1army, self.team2army):
            for army in group:
                self.allunitlist.append(army) # list of every battalion in game alive
        print(len(self.allunitlist), len(self.team0army), len(self.team1army),len(self.team2army))
        self.allunitindex = [army.gameid for army in self.allunitlist] # list of every battalion index alive

        self.team0poslist = {} # team 0 battalion position
        self.team1poslist = {} # team 1 battalion position
        self.team2poslist = {} # same for team 2
        self.showingsquad = [] # list of squads in selected battalion showing on inspect ui
        #^ End start unit sprite

    def setuparmyicon(self):
        """Setup army selection list in army selector ui top left of screen"""
        row = 30
        startcolumn = 25
        column = startcolumn
        armylist = self.team1army
        if self.enactment == True: # include another team army icon as well in enactment mode
            armylist = self.allunitlist
        currentindex = int(self.armyselector.currentrow * self.armyselector.maxcolumnshow) # the first index of current row
        self.armyselector.logsize = len(armylist) / self.armyselector.maxcolumnshow

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

        for index, army in enumerate(armylist): # add army icon for drawing according to appopriate current row
            if index >= currentindex:
                self.armyicon.add(gameui.Armyicon((column, row), army))
                column += 40
                if column > 250:
                    row += 50
                    column = startcolumn
                if row > 100: break # do not draw for the third row
        self.selectscroll.changeimage(logsize=self.armyselector.logsize)

    def checksplit(self, whoinput):
        """Check if army can be splitted, if not remove splitting button"""
        #v split by middle collumn
        if np.array_split(whoinput.armysquad, 2, axis=1)[0].size >= 10 and np.array_split(whoinput.armysquad, 2, axis=1)[1].size >= 10 and \
                whoinput.leader[1].name != "None": # can only split if both battalion size will be larger than 10 and second leader exist
            self.battlelui.add(self.colsplitbutton)
        elif self.colsplitbutton in self.battlelui:
            self.colsplitbutton.kill()
        #^ End col

        #v split by middle row
        if np.array_split(whoinput.armysquad, 2)[0].size >= 10 and np.array_split(whoinput.armysquad, 2)[1].size >= 10 and whoinput.leader[
            1].name != "None":
            self.battlelui.add(self.rowsplitbutton)
        elif self.rowsplitbutton in self.battlelui:
            self.rowsplitbutton.kill()

    def traitskillblit(self):
        """For blitting skill and trait icon into squad info ui"""
        position = self.gameui[2].rect.topleft
        position = [position[0] + 70, position[1] + 60] # start position
        startrow = position[0]

        for icon in self.skillicon.sprites():
            icon.kill()

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

        for icon in self.effecticon.sprites():
            icon.kill()

        for status in self.gameui[2].value2[4]:
            self.effecticon.add(gameui.Skillcardicon(self.statusimgs[0], (position[0], position[1]), 4, id=status))
            position[0] += 40
            if position[0] >= SCREENRECT.width:
                position[1] += 30
                position[0] = startrow

    def countdownskillicon(self):
        """count down timer on skill icon for activate and cooldown time"""
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
        """open and draw enclycopedia at the specified subsection, used for when user right click at icon that has encyclopedia section"""
        self.gamestate = 0
        self.battlemenu.mode = 2
        self.battlelui.add(self.lorebook, self.lorenamelist, *self.lorebuttonui)
        self.lorescroll = gameui.Uiscroller(self.lorenamelist.rect.topright, self.lorenamelist.image.get_height(),
                                            self.lorebook.maxsubsectionshow, layer=14)
        self.battlelui.add(self.lorescroll)
        self.lorebook.changesection(section, self.lorenamelist, self.subsectionname, self.lorescroll, self.pagebutton, self.battlelui)
        self.lorebook.changesubsection(gameid, self.pagebutton, self.battlelui)
        self.lorescroll.changeimage(newrow=self.lorebook.currentsubsectionrow)

    def uimouseover(self):
        """mouse over ui that is not unit card and armybox (topbar and commandbar)"""
        for ui in self.gameui:
            if ui in self.battlelui and ui.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True
                break
        return self.clickany

    def armyiconmouseover(self, mouseup, mouseright):
        """process user mouse input on army icon, left click = select, right click = go to battalion position on map"""
        self.clickany = True
        self.uiclick = True
        for icon in self.armyicon:
            if icon.rect.collidepoint(self.mousepos):
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
        """process user mouse input on various ui buttons"""
        for button in self.buttonui:
            if button in self.battlelui and button.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True  # for avoiding selecting unit under ui
                break
        return self.clickany

    def leadermouseover(self, mouseright):
        """process user mouse input on leader portrait in command ui"""
        leadermouseover = False
        for leader in self.leadernow:
            if leader.rect.collidepoint(self.mousepos):
                if leader.battalion.commander:
                    armyposition = self.leaderposname[leader.armyposition]
                else:
                    armyposition = self.leaderposname[leader.armyposition+4]

                self.leaderpopup.pop(self.mousepos, armyposition + ": " + leader.name) # popup leader name when mouse over
                self.battlelui.add(self.leaderpopup)
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
                self.battlelui.add(self.effectpopup)
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
                    self.battlelui.clear(self.screen, self.background)
                    self.battlecamera.clear(self.screen, self.background)
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
                        self.battlelui.add(self.battlemenu) # add menu to drawer
                        self.battlelui.add(*self.battlemenubutton) # add menu button to

                    else: # in menu
                        if self.battlemenu.mode in (0,1):  # in menu or option
                            if self.battlemenu.mode == 1: # option menu
                                self.mixervolume = self.oldsetting
                                pygame.mixer.music.set_volume(self.mixervolume)
                                self.escslidermenu[0].update(self.mixervolume, self.escvaluebox[0], forcedvalue=True)
                                self.battlemenu.changemode(0)

                            self.battlelui.remove(self.battlemenu)
                            self.battlelui.remove(*self.battlemenubutton)
                            self.battlelui.remove(*self.escoptionmenubutton)
                            self.battlelui.remove(*self.escslidermenu)
                            self.battlelui.remove(*self.escvaluebox)
                            self.gamestate = 1

                        elif self.battlemenu.mode == 2: # encyclopedia
                            self.battlelui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll, self.lorenamelist)

                            for name in self.subsectionname:
                                name.kill()
                                del name
                            self.battlemenu.changemode(0)

                            if self.battlemenu not in self.battlelui:
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
                                squad.unithealth -= squad.unithealth
                        elif event.key == pygame.K_m and self.lastselected is not None:
                            self.lastselected.leader[0].health -= 1000
                        #^ End For development test

                        else: # holding other keys
                            keypress = event.key
                    #^ End keyboard input
                #^ End register input

            self.battlelui.clear(self.screen, self.background)  # Clear sprite before update new one
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

                if self.terraincheck in self.battlelui and (
                        self.terraincheck.pos != self.mousepos or keystate[K_s] or keystate[K_w] or keystate[K_a] or keystate[K_d]):
                    self.battlelui.remove(self.terraincheck) # remove terrain popup when move mouse or camera

                if mouse_up or mouse_right or mouse_down:
                    self.uiclick = False # reset mouse check on ui, if stay false it mean mouse click is not on any ui
                    if mouse_up:
                        self.clickany = False
                        self.newarmyclick = False
                    if self.minimap.rect.collidepoint(self.mousepos): # mouse position on mini map
                        if mouse_up: # move game camera to position clicked on mini map
                            posmask = pygame.Vector2(int(self.mousepos[0] - self.minimap.rect.x), int(self.mousepos[1] - self.minimap.rect.y))
                            self.basecamerapos = posmask * 5
                            self.camerapos = self.basecamerapos * self.camerascale
                            self.clickany = True
                            self.uiclick = True
                        elif mouse_right: # nothing happen with mouse right
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
                            terrainpop, featurepop = self.battlemapfeature.getfeature(self.battlemousepos[1], self.battlemapbase)
                            featurepop = self.battlemapfeature.featuremod[featurepop]
                            heightpop = self.battlemapheight.getheight(self.battlemousepos[1])
                            self.terraincheck.pop(self.mousepos, featurepop, heightpop)
                            self.battlelui.add(self.terraincheck)

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
                        self.battlelui.add(*self.gameui[0:2])  # add leader and top ui
                        self.battlelui.add(self.inspectbutton)  # add inspection ui open/close button
                        self.battlelui.add(self.buttonui[7])  # add decimation button
                        self.battlelui.add(*self.switchbuttonui[0:6])  # add battalion behaviour change button
                        self.switchbuttonui[0].event = whoinput.useskillcond
                        self.switchbuttonui[1].event = whoinput.fireatwill
                        self.switchbuttonui[2].event = whoinput.hold
                        self.switchbuttonui[3].event = whoinput.useminrange
                        self.switchbuttonui[4].event = whoinput.shoothow
                        self.switchbuttonui[5].event = whoinput.runtoggle
                        self.leadernow = whoinput.leader
                        self.battlelui.add(*self.leadernow) # add leader portrait to draw
                        self.checksplit(whoinput) # check if selected battalion can split, if yes draw button
                        self.gameui[0].valueinput(who=whoinput, splithappen=self.splithappen)
                        self.gameui[1].valueinput(who=whoinput, splithappen=self.splithappen)

                    elif self.beforeselected != self.lastselected:  # change unit information on ui when select other battalion
                        if self.inspectui == True: # change inspect ui
                            self.newarmyclick = True
                            self.battlelui.remove(*self.showingsquad)
                            self.showingsquad = whoinput.squadsprite
                            self.squadlastselected = self.showingsquad[0]
                            self.squadselectedborder.pop(self.squadlastselected.inspposition)
                            self.battlelui.add(self.squadselectedborder)
                            self.gameui[2].valueinput(who=self.squadlastselected, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                      splithappen=self.splithappen)
                        self.battlelui.remove(*self.leadernow)
                        self.switchbuttonui[0].event = whoinput.useskillcond
                        self.switchbuttonui[1].event = whoinput.fireatwill
                        self.switchbuttonui[2].event = whoinput.hold
                        self.switchbuttonui[3].event = whoinput.useminrange
                        self.switchbuttonui[4].event = whoinput.shoothow
                        self.switchbuttonui[5].event = whoinput.runtoggle
                        self.leadernow = whoinput.leader
                        self.battlelui.add(*self.leadernow)
                        self.checksplit(whoinput)
                        self.gameui[0].valueinput(who=whoinput, splithappen=self.splithappen)
                        self.gameui[1].valueinput(who=whoinput, splithappen=self.splithappen)

                    else: # Update topbar and command ui value every 1.1 seconds
                        if self.uitimer >= 1.1:
                            self.gameui[0].valueinput(who=whoinput, splithappen=self.splithappen)
                            self.gameui[1].valueinput(who=whoinput, splithappen=self.splithappen)
                    if self.inspectbutton.rect.collidepoint(self.mousepos) or (
                            mouse_up and self.inspectui and self.newarmyclick): # mouse on inspect ui open/close button
                        if self.inspectbutton.rect.collidepoint(self.mousepos):
                            self.buttonnamepopup.pop(self.mousepos, "Inspect Squad")
                            self.battlelui.add(self.buttonnamepopup)
                            if mouse_right:
                                self.uiclick = True # for some reason the loop mouse check above does not work for inspect button, so it here instead
                        if mouse_up:
                            if self.inspectui == False:  # Add army inspect ui when left click at ui button or when change unit with inspect open
                                self.inspectui = True
                                self.battlelui.add(*self.gameui[2:4])
                                self.battlelui.add(*self.unitcardbutton)
                                self.showingsquad = whoinput.squadsprite
                                self.squadlastselected = self.showingsquad[0]
                                self.squadselectedborder.pop(self.squadlastselected.inspposition)
                                self.battlelui.add(self.squadselectedborder)
                                self.gameui[2].valueinput(who=self.squadlastselected, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                            splithappen=self.splithappen)
                            elif self.inspectui:  # Remove when click again and the ui already open
                                self.battlelui.remove(*self.showingsquad)
                                self.battlelui.remove(self.squadselectedborder)
                                self.showingsquad = []
                                for ui in self.gameui[2:4]: ui.kill()
                                for button in self.unitcardbutton: button.kill()
                                self.inspectui = False
                                self.newarmyclick = False

                    elif self.gameui[1] in self.battlelui and self.gameui[1].rect.collidepoint(self.mousepos): # mouse position on command ui
                        if self.switchbuttonui[0].rect.collidepoint(self.mousepos) or keypress == pygame.K_g:
                            if mouse_up or keypress == pygame.K_g:  # rotate skill condition when clicked
                                whoinput.useskillcond += 1
                                if whoinput.useskillcond > 3:
                                    whoinput.useskillcond = 0
                                self.switchbuttonui[0].event = whoinput.useskillcond
                            if self.switchbuttonui[0].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                poptext = ("Free Skill Use", "Conserve 50% Stamina", "Conserve 25% stamina", "Forbid Skill")
                                self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[0].event])
                                self.battlelui.add(self.buttonnamepopup)

                        elif self.switchbuttonui[1].rect.collidepoint(self.mousepos) or keypress == pygame.K_f:
                            if mouse_up or keypress == pygame.K_f:  # rotate fire at will condition when clicked
                                whoinput.fireatwill += 1
                                if whoinput.fireatwill > 1:
                                    whoinput.fireatwill = 0
                                self.switchbuttonui[1].event = whoinput.fireatwill
                            if self.switchbuttonui[1].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                poptext = ("Fire at will", "Hold fire until order")
                                self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[1].event])
                                self.battlelui.add(self.buttonnamepopup)

                        elif self.switchbuttonui[2].rect.collidepoint(self.mousepos) or keypress == pygame.K_h:
                            if mouse_up or keypress == pygame.K_h:  # rotate hold condition when clicked
                                whoinput.hold += 1
                                if whoinput.hold > 2:
                                    whoinput.hold = 0
                                self.switchbuttonui[2].event = whoinput.hold
                            if self.switchbuttonui[2].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                poptext = ("Aggressive", "Skirmish/Scout", "Hold Ground")
                                self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[2].event])
                                self.battlelui.add(self.buttonnamepopup)

                        elif self.switchbuttonui[3].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                            if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                whoinput.useminrange += 1
                                if whoinput.useminrange > 1:
                                    whoinput.useminrange = 0
                                self.switchbuttonui[3].event = whoinput.useminrange
                            if self.switchbuttonui[3].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                poptext = ("Shoot from min range", "Shoot from max range")
                                self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[3].event])
                                self.battlelui.add(self.buttonnamepopup)

                        elif self.switchbuttonui[4].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                            if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                whoinput.shoothow += 1
                                if whoinput.shoothow > 2:
                                    whoinput.shoothow = 0
                                self.switchbuttonui[4].event = whoinput.shoothow
                            if self.switchbuttonui[4].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                poptext = ("Allow both arc and direct shot", "Allow only arc shot", "Allow only direct shot")
                                self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[4].event])
                                self.battlelui.add(self.buttonnamepopup)

                        elif self.switchbuttonui[5].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                            if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                whoinput.runtoggle += 1
                                if whoinput.runtoggle > 1:
                                    whoinput.runtoggle = 0
                                self.switchbuttonui[5].event = whoinput.runtoggle
                            if self.switchbuttonui[5].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                poptext = ("Toggle walk", "Toggle run")
                                self.buttonnamepopup.pop(self.mousepos, poptext[self.switchbuttonui[5].event])
                                self.battlelui.add(self.buttonnamepopup)

                        elif self.colsplitbutton in self.battlelui and self.colsplitbutton.rect.collidepoint(self.mousepos):
                            self.buttonnamepopup.pop(self.mousepos, "Split by middle column")
                            self.battlelui.add(self.buttonnamepopup)
                            if mouse_up and whoinput.basepos.distance_to(list(whoinput.neartarget.values())[0]) > 50:
                                self.splitunit(self, whoinput, 1)
                                self.splithappen = True
                                self.checksplit(whoinput)
                                self.battlelui.remove(*self.leadernow)
                                self.leadernow = whoinput.leader
                                self.battlelui.add(*self.leadernow)
                                self.setuparmyicon()

                        elif self.rowsplitbutton in self.battlelui and self.rowsplitbutton.rect.collidepoint(self.mousepos):
                            self.buttonnamepopup.pop(self.mousepos, "Split by middle row")
                            self.battlelui.add(self.buttonnamepopup)
                            if mouse_up and whoinput.basepos.distance_to(list(whoinput.neartarget.values())[0]) > 50:
                                self.splitunit(self, whoinput, 0)
                                self.splithappen = True
                                self.checksplit(whoinput)
                                self.battlelui.remove(*self.leadernow)
                                self.leadernow = whoinput.leader
                                self.battlelui.add(*self.leadernow)
                                self.setuparmyicon()

                        elif self.buttonui[7].rect.collidepoint(self.mousepos):  # decimation effect
                            self.buttonnamepopup.pop(self.mousepos, "Decimation")
                            self.battlelui.add(self.buttonnamepopup)
                            if mouse_up and whoinput.state == 0:
                                for squad in whoinput.squadsprite:
                                    squad.statuseffect[98] = self.gameunitstat.statuslist[98].copy()
                                    squad.unithealth -= round(squad.unithealth * 0.1)
                        elif self.leadermouseover(mouse_right):
                            self.battlelui.remove(self.buttonnamepopup)
                            pass
                    else:
                        self.battlelui.remove(self.leaderpopup) # remove leader name popup if no mouseover on any button
                        self.battlelui.remove(self.buttonnamepopup)  # remove popup if no mouseover on any button

                    if self.inspectui: # if inspect ui is openned
                        self.battlelui.add(*self.showingsquad)
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
                                            self.battlelui.add(self.squadselectedborder)
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

                            elif self.gameui[2].rect.collidepoint(self.mousepos): # mouse position in unit card
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
                                self.beforeselected != self.lastselected:  # Update value of the clicked squad every 1.1 second
                            self.gameui[2].valueinput(who=self.squadlastselected, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                    splithappen=self.splithappen)
                            if self.gameui[2].option == 2: # skill and status effect card
                                self.countdownskillicon()
                                self.effecticonblit()
                                if self.beforeselected != self.lastselected: # change unit, reset trait icon as well
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
                                self.battlelui.remove(self.effectpopup)

                        if self.splithappen:  # change showing squad in inspectui if split happen
                            self.battlelui.remove(*self.showingsquad)
                            self.showingsquad = whoinput.squadsprite
                            self.battlelui.add(*self.showingsquad)
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
                    self.battlelui.add(self.textdrama)
                    self.textdrama.processqueue()
                    self.dramatimer = 0.1
                elif self.dramatimer > 0:
                    self.textdrama.playanimation()
                    self.dramatimer += self.uidt
                    if self.dramatimer > 3:
                        self.dramatimer = 0
                        self.battlelui.remove(self.textdrama)
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

                self.effectupdater.update(self.allunitlist, self.hitboxes, self.dt, self.camerascale)
                self.weatherupdater.update(self.dt, self.timenumber.timenum)
                self.camera.update(self.camerapos, self.battlecamera)
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
                    self.battlelui.remove(*self.switchbuttonui) # remove change battalion behaviour button
                    self.battlelui.remove(*self.showingsquad) # remove squad sprite in army inspect ui
                    self.showingsquad = [] # clear squad list in army inspect ui
                    self.inspectui = False # inspect ui close
                    self.beforeselected = None # reset before selected battalion after remove last selected
                    self.battlelui.remove(*self.leadernow) # remove leader image from command ui
                    self.squadlastselected = None # reset squad selected
                    self.battlelui.remove(self.squadselectedborder) # remove squad selected border sprite
                    self.leadernow = [] # clear leader list in command ui
                #^ End remove

                #v Update game time
                self.dt = self.clock.get_time() / 1000 # dt before gamespeed
                self.uitimer += self.dt # ui update by real time instead of game time to reduce workload
                self.uidt = self.dt # get ui timer before apply game speed
                self.dt = self.dt * self.gamespeed # apply dt with gamespeed for ingame calculation
                self.combattimer += self.dt # update combat timer
                self.timenumber.timerupdate(self.dt*10) # update ingame time with 5x speed
                #^ End update game time

            else: # Complete game pause when open either esc menu or enclycopedia
                if self.battlemenu.mode == 0: # main esc menu
                    for button in self.battlemenubutton:
                        if button.rect.collidepoint(self.mousepos):
                            button.image = button.images[1] # change button image to mouse over one
                            if mouse_up: # click on button
                                button.image = button.images[2] # change button image to clicked one
                                if button.text == "Resume": # resume game
                                    self.gamestate = 1 # resume battle gameplay state
                                    self.battlelui.remove(self.battlemenu, *self.battlemenubutton, *self.escslidermenu, *self.escvaluebox) # remove menu sprite

                                elif button.text == "Encyclopedia": # open encyclopedia
                                    self.battlemenu.mode = 2 # change to enclycopedia mode
                                    self.battlelui.add(self.lorebook, self.lorenamelist, *self.lorebuttonui) # add sprite related to encyclopedia
                                    self.lorescroll = gameui.Uiscroller(self.lorenamelist.rect.topright, self.lorenamelist.image.get_height(),
                                                                        self.lorebook.maxsubsectionshow, layer=14) # add subsection list scroller
                                    self.battlelui.add(self.lorescroll)
                                    self.lorebook.changesection(0, self.lorenamelist, self.subsectionname, self.lorescroll, self.pagebutton, self.battlelui)
                                    # self.lorebook.setupsubsectionlist(self.lorenamelist, listgroup)

                                elif button.text == "Option": # open option menu
                                    self.battlemenu.changemode(1) # change to option menu mode
                                    self.battlelui.remove(*self.battlemenubutton) # remove main esc menu button
                                    self.battlelui.add(*self.escoptionmenubutton, *self.escslidermenu, *self.escvaluebox)
                                    self.oldsetting = self.escslidermenu[0].value  # Save previous setting for in case of cancel

                                elif button.text == "Main Menu": # back to main menu
                                    self.battlelui.clear(self.screen, self.background) # remove all sprite
                                    self.battlecamera.clear(self.screen, self.background) # remove all sprite

                                    self.battlelui.remove(self.battlemenu, *self.battlemenubutton, *self.escslidermenu,
                                                          *self.escvaluebox)  # remove menu sprite
                                    # for index, stuff in enumerate(self.allunitlist):
                                    #     del stuff.squadsprite
                                    #     del stuff.hitboxs
                                    #     del stuff.leaders
                                    #     if index == 0:
                                    #         print(sys.getrefcount(stuff))
                                    #         print(gc.get_referrers(stuff))
                                    for group in (self.squad, self.armyleader, self.hitboxes, self.team0army, self.team1army, self.team2army, self.armyicon):
                                        for stuff in group:
                                            stuff.delete()
                                            stuff.kill()
                                            del stuff
                                    self.squadlastselected = None
                                    self.allunitlist = []
                                    self.showingsquad = []
                                    self.team0poslist, self.team1poslist, self.team2poslist = {}, {}, {}
                                    self.beforeselected = None

                                    # print(locals())
                                    return # end battle game loop

                                elif button.text == "Desktop": # quit game
                                    self.battlelui.clear(self.screen, self.background) # remove all sprite
                                    self.battlecamera.clear(self.screen, self.background) # remove all sprite
                                    sys.exit() # quit
                                break # found clicked button, break loop
                        else:
                            button.image = button.images[0]

                elif self.battlemenu.mode == 1: # option menu
                    for button in self.escoptionmenubutton: # check if any button get collided with mouse or clicked
                        if button.rect.collidepoint(self.mousepos):
                            button.image = button.images[1] # change button image to mouse over one
                            if mouse_up: # click on button
                                button.image = button.images[2] # change button image to clicked one
                                if button.text == "Confirm": # confirm button, save the setting and close option menu
                                    self.oldsetting = self.mixervolume # save mixer volume
                                    pygame.mixer.music.set_volume(self.mixervolume) # set new music player volume
                                    main.editconfig('DEFAULT', 'SoundVolume', str(slider.value), 'configuration.ini', config) # save to config file
                                    self.battlemenu.changemode(0) # go back to main esc menu
                                    self.battlelui.remove(*self.escoptionmenubutton, *self.escslidermenu, *self.escvaluebox) # remove option menu sprite
                                    self.battlelui.add(*self.battlemenubutton) # add main esc menu buttons back

                                elif button.text == "Apply": # apply button, save the setting
                                    self.oldsetting = self.mixervolume # save mixer volume
                                    pygame.mixer.music.set_volume(self.mixervolume) # set new music player volume
                                    main.editconfig('DEFAULT', 'SoundVolume', str(slider.value), 'configuration.ini', config) # save to config file

                                elif button.text == "Cancel": # cancel button, revert the setting to the last saved one
                                    self.mixervolume = self.oldsetting # revert to old setting
                                    pygame.mixer.music.set_volume(self.mixervolume)  # set new music player volume
                                    self.escslidermenu[0].update(self.mixervolume, self.escvaluebox[0], forcedvalue=True) # update slider bar
                                    self.battlemenu.changemode(0) # go back to main esc menu
                                    self.battlelui.remove(*self.escoptionmenubutton, *self.escslidermenu, *self.escvaluebox) # remove option menu sprite
                                    self.battlelui.add(*self.battlemenubutton) # add main esc menu buttons back

                        else: # no button currently collided with mouse
                            button.image = button.images[0] # revert button image back to the idle one

                    for slider in self.escslidermenu:
                        if slider.rect.collidepoint(self.mousepos) and (mouse_down or mouse_up): # mouse click on slider bar
                            slider.update(self.mousepos, self.escvaluebox[0]) # update slider button based on mouse value
                            self.mixervolume = float(slider.value / 100) # for now only music volume slider exist

                elif self.battlemenu.mode == 2:  # Encyclopedia mode
                    if mouse_up or mouse_down: # mouse down (hold click) only for subsection listscroller
                        if mouse_up:
                            for button in self.lorebuttonui:
                                if button in self.battlelui and button.rect.collidepoint(self.mousepos): # click button
                                    if button.event in range(0, 11): # section button
                                        self.lorebook.changesection(button.event, self.lorenamelist, self.subsectionname, self.lorescroll, self.pagebutton, self.battlelui) # change to section of that button
                                    elif button.event == 19:  # Close button
                                        self.battlelui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll, self.lorenamelist) # remove enclycopedia related sprites
                                        for name in self.subsectionname: # remove subsection name
                                            name.kill()
                                            del name
                                        self.battlemenu.changemode(0) # change menu back to default 0
                                        if self.battlemenu not in self.battlelui: # in case open encyclopedia via right click on icon or other way
                                            self.gamestate = 1 # resume gameplay
                                    elif button.event == 20:  # Previous page button
                                        self.lorebook.changepage(self.lorebook.page - 1, self.pagebutton, self.battlelui) # go back 1 page
                                    elif button.event == 21:  # Next page button
                                        self.lorebook.changepage(self.lorebook.page + 1, self.pagebutton, self.battlelui) # go forward 1 page
                                    break # found clicked button, break loop

                            for name in self.subsectionname: # too lazy to include break for button found to avoid subsection loop since not much optimisation is needed here
                                if name.rect.collidepoint(self.mousepos): # click on subsection name
                                    self.lorebook.changesubsection(name.subsection, self.pagebutton, self.battlelui) # change subsection
                                    break # found clicked subsection, break loop

                        if self.lorescroll.rect.collidepoint(self.mousepos): # click on subsection list scroller
                            self.lorebook.currentsubsectionrow = self.lorescroll.update(self.mousepos) # update the scroller and get new current subsection
                            self.lorebook.setupsubsectionlist(self.lorenamelist, self.subsectionname) # update subsection name list

            self.screen.blit(self.camera.image, (0, 0))  # Draw the game camera and everything that appear in it
            self.battlelui.draw(self.screen)  # Draw the UI
            pygame.display.update() # update game display, draw everything
            self.clock.tick(60) # clock update even if game pause

        if pygame.mixer: # close music player
            pygame.mixer.music.fadeout(1000)

        pygame.time.wait(1000) # wait a bit before closing
        pygame.quit()
