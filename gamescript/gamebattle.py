import csv
import datetime
import glob
import random
import sys

import main
import numpy as np
import pygame
import pygame.freetype
from gamescript import gamesubunit, gameunit, gameui, gameleader, gamecamera, gamelongscript, gameweather, gameprepare, gamemap
from pygame.locals import *
from scipy.spatial import KDTree

config = main.config
SoundVolume = main.Soundvolume
SCREENRECT = main.SCREENRECT
main_dir = main.main_dir

load_image = gamelongscript.load_image
load_images = gamelongscript.load_images
csv_read = gamelongscript.csv_read
load_sound = gamelongscript.load_sound


class Battle:
    splitunit = gamelongscript.splitunit
    traitskillblit = gamelongscript.traitskillblit
    effecticonblit = gamelongscript.effecticonblit
    countdownskillicon = gamelongscript.countdownskillicon
    teamcolour = main.teamcolour

    def __init__(self, main, winstyle):
        # v Get game object/variable from main
        self.mode = None  # battle map mode can be "uniteditor" for unit editor or "battle" for game battle
        self.main = main
        self.widthadjust = main.widthadjust
        self.heightadjust = main.heightadjust
        self.eventlog = main.eventlog
        self.battlecamera = main.battlecamera
        self.battleui = main.battleui

        self.unit_updater = main.unit_updater
        self.subunit_updater = main.subunit_updater
        self.leader_updater = main.leader_updater
        self.uiupdater = main.ui_updater
        self.weather_updater = main.weather_updater
        self.effect_updater = main.effect_updater

        self.battlemap_base = main.battlemap_base
        self.battlemap_feature = main.battlemap_feature
        self.battlemap_height = main.battlemap_height
        self.showmap = main.showmap

        self.team0unit = main.team0unit
        self.team1unit = main.team1unit
        self.team2unit = main.team2unit
        self.team0subunit = main.team0subunit
        self.team1subunit = main.team1subunit
        self.team2subunit = main.team2subunit
        self.subunit = main.subunit
        self.armyleader = main.armyleader

        self.arrows = main.arrows
        self.directionarrows = main.directionarrows
        self.troopnumbersprite = main.troopnumbersprite

        self.gameui = main.gameui
        self.inspectuipos = main.inspectuipos
        self.inspectsubunit = main.inspectsubunit
        self.popgameui = main.gameui  # saving list of gameui that will pop out when parentunit is selected

        self.battlemap_base = main.battlemap_base
        self.battlemap_feature = main.battlemap_feature
        self.battlemap_height = main.battlemap_height
        self.showmap = main.showmap

        self.minimap = main.minimap
        self.eventlog = main.eventlog
        self.logscroll = main.logscroll
        self.buttonui = main.buttonui
        self.subunitselectedborder = main.inspectselectedborder
        self.switch_button = main.switch_button

        self.fpscount = main.fpscount

        self.terraincheck = main.terraincheck
        self.button_name_popup = main.button_name_popup
        self.leaderpopup = main.leaderpopup
        self.effectpopup = main.effectpopup
        self.textdrama = main.textdrama

        self.skill_icon = main.skill_icon
        self.effect_icon = main.effect_icon

        self.battle_menu = main.battle_menu
        self.battle_menu_button = main.battle_menu_button
        self.escoptionmenubutton = main.escoption_menu_button

        self.unit_delete_button = self.main.unit_delete_button
        self.unit_save_button = self.main.unit_save_button
        self.troop_listbox = main.troop_listbox
        self.troop_namegroup = main.troop_namegroup
        self.filterbox = main.filterbox
        self.tickbox_filter = main.tickbox_filter
        self.teamchange_button = main.teamchange_button
        self.slotdisplay_button = main.slotdisplay_button
        self.test_button = main.test_button
        self.deploy_button = main.deploy_button
        self.popup_listbox = main.popup_listbox
        self.popup_namegroup = main.popup_namegroup
        self.terrain_change_button = main.terrain_change_button
        self.feature_change_button = main.feature_change_button
        self.weather_change_button = main.weather_change_button
        self.unitbuildslot = main.unitbuildslot
        self.uniteditborder = main.uniteditborder
        self.previewleader = main.previewleader
        self.unitpreset_namegroup = main.unitpreset_namegroup
        self.presetselectborder = main.presetselectborder
        self.customunitpresetlist = main.customunitpresetlist
        self.unit_listbox = main.unit_listbox
        self.troo_scroll = main.troop_scroll
        self.faction_list = main.faction_list
        self.weather_list = main.weather_list
        self.popup_listscroll = main.popup_listscroll
        self.troop_scroll = main.troop_scroll
        self.teamcoa = main.teamcoa
        self.unit_presetname_scroll = main.unit_presetname_scroll
        self.warningmsg = main.warningmsg

        self.input_button = main.input_button
        self.input_box = main.input_box
        self.inputui = main.inputui
        self.input_ok_button = main.input_ok_button
        self.input_cancel_button = main.input_cancel_button
        self.inputui_pop = main.inputui_pop
        self.confirmui = main.confirmui
        self.confirmui_pop = main.confirmui_pop

        self.unitselector = main.unitselector
        self.uniticon = main.uniticon
        self.selectscroll = main.selectscroll

        self.timeui = main.timeui
        self.timenumber = main.timenumber

        self.scaleui = main.scaleui

        self.speednumber = main.speednumber

        self.weathermatter = main.weathermatter
        self.weathereffect = main.weathereffect

        self.lorebook = main.lorebook
        self.lorenamelist = main.lorenamelist
        self.lorebuttonui = main.lorebuttonui
        self.lorescroll = main.lorescroll
        self.subsection_name = main.subsection_name
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
        self.leader_stat = main.leader_stat

        self.statetext = main.statetext

        self.squadwidth = main.squadwidth
        self.squadheight = main.squadheight
        self.collidedistance = self.squadheight / 10  # distance to check collision
        self.frontdistance = self.squadheight / 20  # distance from front side
        self.fulldistance = self.frontdistance / 2  # distance for sprite merge check

        self.combatpathqueue = []  # queue of sub-unit to run melee combat pathfiding

        self.escslidermenu = main.escslidermenu
        self.escvaluebox = main.escvaluebox

        self.screenbuttonlist = main.screenbuttonlist
        self.unitcardbutton = main.unitcardbutton
        self.inspectbutton = main.inspectbutton
        self.col_split_button = main.col_split_button
        self.rowsplitbutton = main.rowsplitbutton

        self.leaderposname = main.leaderposname

        self.battledone_box = main.battledone_box
        self.gamedone_button = main.gamedone_button
        # ^ End load from main

        self.gamespeed = 0
        self.gamespeedset = (0, 0.5, 1, 2, 4, 6)  # availabe game speed
        self.leadernow = []
        self.team_troopnumber = [1, 1, 1]  # list of troop number in each team, minimum at one because percentage can't divide by 0
        self.last_team_troopnumber = [1, 1, 1]
        self.start_troopnumber = [0, 0, 0]
        self.wound_troopnumber = [0, 0, 0]
        self.death_troopnumber = [0, 0, 0]
        self.flee_troopnumber = [0, 0, 0]
        self.capture_troopnumber = [0, 0, 0]
        self.factionpick = 0
        self.filtertroop = [True, True, True, True]
        self.last_selected = None
        self.before_selected = None

        self.unitsetup_stuff = (self.unitbuildslot, self.uniteditborder, self.gameui[1], self.gameui[2],
                                self.teamcoa, self.unitcardbutton, self.troop_listbox, self.troop_scroll,
                                self.troop_namegroup, self.unit_listbox, self.presetselectborder,
                                self.unitpreset_namegroup, self.unit_save_button, self.unit_delete_button,
                                self.unit_presetname_scroll)
        self.filter_stuff = (self.filterbox, self.slotdisplay_button, self.teamchange_button, self.deploy_button, self.terrain_change_button,
                             self.feature_change_button, self.weather_change_button, self.tickbox_filter)

        self.bestdepth = pygame.display.mode_ok(SCREENRECT.size, winstyle, 32)  # Set the display mode
        self.screen = pygame.display.set_mode(SCREENRECT.size, winstyle | pygame.RESIZABLE, self.bestdepth)  # set up game screen

        # v Assign default variable to some class
        gameunit.Unitarmy.gamebattle = self
        gameunit.Unitarmy.imgsize = (self.squadwidth, self.squadheight)
        gamesubunit.Subunit.gamebattle = self
        gameleader.Leader.gamebattle = self
        # ^ End assign default

        self.background = pygame.Surface(SCREENRECT.size)  # Create background image
        self.background.fill((255, 255, 255))  # fill background image with black colour

    def editor_map_change(self, basecolour, featurecolour):
        imgs = (pygame.Surface((1000, 1000)), pygame.Surface((1000, 1000)), pygame.Surface((1000, 1000), pygame.SRCALPHA), None)
        imgs[0].fill(basecolour)  # start with temperate terrain
        imgs[1].fill(featurecolour)  # start with plain feature
        imgs[2].fill((255, 100, 100, 125))  # start with height 100 plain

        self.battlemap_base.drawimage(imgs[0])
        self.battlemap_feature.drawimage(imgs[1])
        self.battlemap_height.drawimage(imgs[2])
        self.showmap.drawimage(self.battlemap_base, self.battlemap_feature, self.battlemap_height, None, self, True)
        self.minimap.drawimage(self.showmap.trueimage, self.camera)
        self.showmap.changescale(self.camerascale)

    def preparenewgame(self, ruleset, rulesetfolder, teamselected, enactment, mapselected, source, unitscale, mode):

        self.ruleset = ruleset  # current ruleset used
        self.rulesetfolder = rulesetfolder  # the folder of rulseset used
        self.mapselected = mapselected  # map folder name
        self.source = str(source)
        self.unitscale = unitscale
        self.playerteam = teamselected  # player selected team

        # v load the sound effects
        # boom_sound = load_sound("boom.wav")
        # shoot_sound = load_sound("car_door.wav")
        # ^ End load sound effect

        # v Random music played from list
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer = None
        if pygame.mixer:
            self.SONG_END = pygame.USEREVENT + 1
            # musiclist = os.path.join(main_dir, "data/sound/")
            self.musiclist = glob.glob(main_dir + "/data/sound/music/*.mp3")
            self.pickmusic = random.randint(1, 1)
            pygame.mixer.music.set_endevent(self.SONG_END)
            pygame.mixer.music.load(self.musiclist[self.pickmusic])
            pygame.mixer.music.play(0)
        # ^ End music play

        # v Load weather schedule
        try:
            self.weatherevent = csv_read("weather.csv", ["data", "ruleset", self.rulesetfolder.strip("/"), "map", self.mapselected, self.source], 1)
            self.weatherevent = self.weatherevent[1:]
            gamelongscript.convert_weather_time(self.weatherevent)
        except Exception:  # If no weather found use default light sunny weather start at 9.00
            newtime = datetime.datetime.strptime("09:00:00", "%H:%M:%S").time()
            newtime = datetime.timedelta(hours=newtime.hour, minutes=newtime.minute, seconds=newtime.second)
            self.weatherevent = [[4, newtime, 0]]  # default weather light sunny all day
        self.weatherschedule = self.weatherevent[0][1]
        # ^ End weather schedule

        try:  # get new map event for event log
            mapevent = csv_read("eventlog.csv", ["data", "ruleset", self.rulesetfolder.strip("/"), "map", self.mapselected, self.source], 0)
            gameui.Eventlog.mapevent = mapevent
        except Exception:  # can't find any event file
            mapevent = {}  # create empty list

        self.eventlog.makenew()  # reset old event log

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

        # v Create the battle map
        self.camerapos = pygame.Vector2(500, 500)  # Camera pos at the current zoom, start at center of map
        self.basecamerapos = pygame.Vector2(500, 500)  # Camera pos at furthest zoom for recalculate sprite pos after zoom
        self.camerascale = 1  # Camera zoom
        gamecamera.Camera.SCREENRECT = SCREENRECT
        self.camera = gamecamera.Camera(self.camerapos, self.camerascale)

        if mapselected is not None:
            imgs = load_images(["ruleset", self.rulesetfolder.strip("/"), "map", self.mapselected], loadorder=False)
            self.battlemap_base.drawimage(imgs[0])
            self.battlemap_feature.drawimage(imgs[1])
            self.battlemap_height.drawimage(imgs[2])

            try:  # placename map layer is optional, if not existed in folder then assign None
                placenamemap = imgs[3]
            except Exception:
                placenamemap = None
            self.showmap.drawimage(self.battlemap_base, self.battlemap_feature, self.battlemap_height, placenamemap, self, False)
        else:  # for unit editor mode, create empty temperate glass map
            self.editor_map_change((166, 255, 107), (181, 230, 29))
        # ^ End create battle map

        self.clock = pygame.time.Clock()  # Game clock to keep track of realtime pass

        self.enactment = enactment  # enactment mod, control both team

        self.team0poslist = {}  # team 0 parentunit position
        self.team1poslist = {}  # team 1 parentunit position
        self.team2poslist = {}  # same for team 2

        self.allunitlist = []  # list of every parentunit in game alive
        self.allunitindex = []  # list of every parentunit index alive

        self.allsubunitlist = []  # list of all subunit alive in game

        # v initialise starting subunit sprites
        self.mode = mode
        if self.mode == "battle":
            self.start_troopnumber = [0, 0, 0]
            self.wound_troopnumber = [0, 0, 0]
            self.death_troopnumber = [0, 0, 0]
            self.flee_troopnumber = [0, 0, 0]
            self.capture_troopnumber = [0, 0, 0]
            gamelongscript.unitsetup(self)
        # ^ End start subunit sprite

    def save_preset(self):
        with open("profile/unitpreset/" + str(self.ruleset) + "/custom_unitpreset.csv", "w", encoding='utf-8', newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
            savelist = self.customunitpresetlist.copy()
            del savelist["New Preset"]
            finalsave = [["presetname", "subunitline1", "subunitline2", "subunitline3", "subunitline4", "subunitline5", "subunitline6",
                          "subunitline7", "subunitline8", "leader", "leaderposition", "faction"]]
            for item in list(savelist.items()):
                subitem = [smallitem for smallitem in item[1]]
                item = [item[0]] + subitem
                finalsave.append(item)
            for row in finalsave:
                filewriter.writerow(row)
            csvfile.close()

    def convertslot_dict(self, name, pos=None, addid=None):
        currentpreset = [[], [], [], [], [], [], [], []]
        startitem = 0
        subunitcount = 0
        for slot in self.unitbuildslot:  # add subunit troop id
            currentpreset[int(startitem / 8)].append(str(slot.troopid))
            startitem += 1
            if slot.troopid != 0:
                subunitcount += 1
        if pos is not None:
            currentpreset.append(pos)

        if subunitcount > 0:
            leaderlist = []
            leaderposlist = []
            for leader in self.previewleader:  # add leader id
                countzero = 0
                if leader.leaderid != 1:
                    subunitcount += 1
                    for slotindex, slot in enumerate(self.unitbuildslot):  # add subunit troop id
                        if slot.troopid == 0:
                            countzero += 1
                        if slotindex == leader.subunitpos:
                            break

                leaderlist.append(str(leader.leaderid))
                leaderposlist.append(str(leader.subunitpos - countzero))
            currentpreset.append(leaderlist)
            currentpreset.append(leaderposlist)

            faction = []  # generate faction list that can use this unit
            factionlist = self.allfaction.faction_list.copy()
            del factionlist["ID"]
            del factionlist[0]
            factioncount = dict.fromkeys(factionlist.keys(), 0)  # dict of faction occurence count

            for index, item in enumerate(currentpreset):
                for thisitem in item:
                    if index in range(0, 8):  # subunit
                        for factionitem in factionlist.items():
                            if int(thisitem) in factionitem[1][1]:
                                factioncount[factionitem[0]] += 1
                    elif index == 8:  # leader
                        for factionitem in factionlist.items():
                            if int(thisitem) < 10000 and int(thisitem) in factionitem[1][2]:
                                factioncount[factionitem[0]] += 1
                            elif int(thisitem) >= 10000:
                                if factionitem[0] == self.leader_stat.leader_list[int(thisitem)][-2] or \
                                        self.leader_stat.leader_list[int(thisitem)][-2] == 0:
                                    factioncount[factionitem[0]] += 1

            for item in factioncount.items():  # find faction of this unit
                if item[1] == factioncount[max(factioncount, key=factioncount.get)]:
                    if factioncount[max(factioncount, key=factioncount.get)] == subunitcount:
                        faction.append(item[0])
                    else:  # units from various factions, counted as multi-faction unit
                        faction = [0]
                        break
            currentpreset.append(faction)

            for itemindex, item in enumerate(currentpreset):  # convert list to string
                if type(item) == list:
                    if len(item) > 1:
                        currentpreset[itemindex] = ",".join(item)
                    else:  # still type list because only one item in list
                        currentpreset[itemindex] = str(currentpreset[itemindex][0])
            if addid is not None:
                currentpreset = [addid] + currentpreset
            currentpreset = {name: currentpreset}
        else:
            currentpreset = None

        return currentpreset

    def previewauthority(self, leaderlist, armyid):
        """Calculate authority of editted unit"""
        authority = int(
            leaderlist[0].authority + (leaderlist[0].authority / 2) +
            (leaderlist[1].authority / 4) + (leaderlist[2].authority / 4) +
            (leaderlist[3].authority / 10))
        bigunitsize = len([slot for slot in self.unitbuildslot if slot.armyid == armyid and slot.name != "None"])
        if bigunitsize > 20:  # army size larger than 20 will reduce main leader authority
            authority = int(leaderlist[0].authority +
                            (leaderlist[0].authority / 2 * (100 - bigunitsize) / 100) +
                            leaderlist[1].authority / 2 + leaderlist[2].authority / 2 +
                            leaderlist[3].authority / 4)

        for slot in self.unitbuildslot:
            if slot.armyid == armyid:
                slot.authority = authority

        if self.showincard is not None:
            self.gameui[1].valueinput(who=self.showincard)
        # ^ End cal authority

    def setup_uniticon(self):
        """Setup unit selection list in unit selector ui top left of screen"""
        row = 30
        startcolumn = 25
        column = startcolumn
        unitlist = self.team1unit
        if self.playerteam == 2:
            unitlist = self.team2unit
        if self.enactment:  # include another team unit icon as well in enactment mode
            unitlist = self.allunitlist
        currentindex = int(self.unitselector.current_row * self.unitselector.max_column_show)  # the first index of current row
        self.unitselector.logsize = len(unitlist) / self.unitselector.max_column_show

        if self.unitselector.logsize.is_integer() is False:
            self.unitselector.logsize = int(self.unitselector.logsize) + 1

        if self.unitselector.current_row > self.unitselector.logsize - 1:
            self.unitselector.current_row = self.unitselector.logsize - 1
            currentindex = int(self.unitselector.current_row * self.unitselector.max_column_show)
            self.selectscroll.changeimage(newrow=self.unitselector.current_row)

        if len(self.uniticon) > 0:  # Remove all old icon first before making new list
            for icon in self.uniticon:
                icon.kill()
                del icon

        for index, unit in enumerate(unitlist):  # add unit icon for drawing according to appopriate current row
            if index >= currentindex:
                self.uniticon.add(gameui.Armyicon((column, row), unit))
                column += 40
                if column > 250:
                    row += 50
                    column = startcolumn
                if row > 100:
                    break  # do not draw for the third row
        self.selectscroll.changeimage(logsize=self.unitselector.logsize)

    def checksplit(self, whoinput):
        """Check if unit can be splitted, if not remove splitting button"""
        # v split by middle collumn
        if np.array_split(whoinput.armysubunit, 2, axis=1)[0].size >= 10 and np.array_split(whoinput.armysubunit, 2, axis=1)[1].size >= 10 and \
                whoinput.leader[1].name != "None":  # can only split if both parentunit size will be larger than 10 and second leader exist
            self.battleui.add(self.col_split_button)
        elif self.col_split_button in self.battleui:
            self.col_split_button.kill()
        # ^ End col

        # v split by middle row
        if np.array_split(whoinput.armysubunit, 2)[0].size >= 10 and np.array_split(whoinput.armysubunit, 2)[1].size >= 10 and \
                whoinput.leader[1].name != "None":
            self.battleui.add(self.rowsplitbutton)
        elif self.rowsplitbutton in self.battleui:
            self.rowsplitbutton.kill()

    def popout_lorebook(self, section, gameid):
        """open and draw enclycopedia at the specified subsection, used for when user right click at icon that has encyclopedia section"""
        self.gamestate = 0
        self.battle_menu.mode = 2
        self.battleui.add(self.lorebook, self.lorenamelist, self.lorescroll, *self.lorebuttonui)

        self.lorebook.change_section(section, self.lorenamelist, self.subsection_name, self.lorescroll, self.pagebutton, self.battleui)
        self.lorebook.change_subsection(gameid, self.pagebutton, self.battleui)
        self.lorescroll.changeimage(newrow=self.lorebook.current_subsection_row)

    def popuplist_newopen(self, newrect, newlist, uitype):
        """Move popup_listbox and scroll sprite to new location and create new name list baesd on type"""
        self.currentpopuprow = 0

        if uitype == "leader":
            self.popup_listbox.rect = self.popup_listbox.image.get_rect(topleft=newrect)
        else:
            self.popup_listbox.rect = self.popup_listbox.image.get_rect(midbottom=newrect)

        self.main.setuplist(gameprepare.Namelist, 0, newlist, self.popup_namegroup,
                            self.popup_listbox, self.battleui, layer=19)

        self.popup_listscroll.pos = self.popup_listbox.rect.topright  # change position variable
        self.popup_listscroll.rect = self.popup_listscroll.image.get_rect(topleft=self.popup_listbox.rect.topright)  #
        self.popup_listscroll.changeimage(newrow=0, logsize=len(newlist))

        self.battleui.add(self.popup_listbox, *self.popup_namegroup, self.popup_listscroll)  # add the option list to screen

        self.popup_listbox.type = uitype

    def ui_mouseover(self):
        """mouse over ui that is not subunit card and unitbox (topbar and commandbar)"""
        for ui in self.gameui:
            if ui in self.battleui and ui.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True
                break
        return self.clickany

    def uniticon_mouseover(self, mouseup, mouseright):
        """process user mouse input on unit icon, left click = select, right click = go to parentunit position on map"""
        self.clickany = True
        self.uiclick = True
        for icon in self.uniticon:
            if icon.rect.collidepoint(self.mousepos):
                if mouseup:
                    self.last_selected = icon.army
                    self.last_selected.justselected = True
                    self.last_selected.selected = True

                elif mouseright:
                    self.basecamerapos = pygame.Vector2(icon.army.base_pos[0], icon.army.base_pos[1])
                    self.camerapos = self.basecamerapos * self.camerascale
                break
        return self.clickany

    def button_mouseover(self, mouseright):
        """process user mouse input on various ui buttons"""
        for button in self.buttonui:
            if button in self.battleui and button.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True  # for avoiding selecting subunit under ui
                break
        return self.clickany

    def leader_mouseover(self, mouseright):  # TODO make it so button and leader popup not show at same time
        """process user mouse input on leader portrait in command ui"""
        leadermouseover = False
        for leader in self.leadernow:
            if leader.rect.collidepoint(self.mousepos):
                if leader.parentunit.commander:
                    armyposition = self.leaderposname[leader.armyposition]
                else:
                    armyposition = self.leaderposname[leader.armyposition + 4]

                self.leaderpopup.pop(self.mousepos, armyposition + ": " + leader.name)  # popup leader name when mouse over
                self.battleui.add(self.leaderpopup)
                leadermouseover = True

                if mouseright:
                    self.popout_lorebook(8, leader.leaderid)
                break
        return leadermouseover

    def effecticon_mouseover(self, iconlist, mouseright):
        effectmouseover = False
        for icon in iconlist:
            if icon.rect.collidepoint(self.mousepos):
                checkvalue = self.gameui[2].value2[icon.icontype]
                self.effectpopup.pop(self.mousepos, checkvalue[icon.gameid])
                self.battleui.add(self.effectpopup)
                effectmouseover = True
                if mouseright:
                    if icon.icontype == 0:  # Trait
                        section = 7
                    elif icon.icontype == 1:  # Skill
                        section = 6
                    else:
                        section = 5  # Status effect
                    self.popout_lorebook(section, icon.gameid)
                break
        return effectmouseover

    def removeunitui(self):
        self.gameui[2].option = 1  # reset subunit card option
        for ui in self.gameui:
            ui.kill()  # remove ui
        for button in self.buttonui[0:8]:
            button.kill()  # remove button
        for icon in self.skill_icon.sprites():
            icon.kill()  # remove skill and trait icon
        for icon in self.effect_icon.sprites():
            icon.kill()  # remove effect icon
        self.battleui.remove(*self.switch_button, *self.inspectsubunit)  # remove change behaviour button and inspect ui subunit
        self.inspectui = False  # inspect ui close
        self.battleui.remove(*self.leadernow)  # remove leader image from command ui
        self.subunit_selected = None  # reset subunit selected
        self.battleui.remove(self.subunitselectedborder)  # remove subunit selected border sprite
        self.leadernow = []  # clear leader list in command ui

    def camerafix(self):
        if self.basecamerapos[0] > 999:  # camera cannot go further than 999 x
            self.basecamerapos[0] = 999
        elif self.basecamerapos[0] < 0:  # camera cannot go less than 0 x
            self.basecamerapos[0] = 0

        if self.basecamerapos[1] > 999:  # same for y
            self.basecamerapos[1] = 999
        elif self.basecamerapos[1] < 0:
            self.basecamerapos[1] = 0

    def addbehaviourui(self, whoinput, elsecheck=False):
        if whoinput.control:
            self.battleui.add(self.buttonui[7])  # add decimation button
            self.battleui.add(*self.switch_button[0:7])  # add parentunit behaviour change button
            self.switch_button[0].event = whoinput.skill_cond
            self.switch_button[1].event = whoinput.fireatwill
            self.switch_button[2].event = whoinput.hold
            self.switch_button[3].event = whoinput.use_min_range
            self.switch_button[4].event = whoinput.shoothow
            self.switch_button[5].event = whoinput.runtoggle
            self.switch_button[6].event = whoinput.attackmode
            self.checksplit(whoinput)  # check if selected parentunit can split, if yes draw button
        elif elsecheck:
            if self.rowsplitbutton in self.battleui:
                self.rowsplitbutton.kill()
            if self.col_split_button in self.battleui:
                self.col_split_button.kill()
            self.battleui.remove(self.buttonui[7])  # remove decimation button
            self.battleui.remove(*self.switch_button[0:7])  # remove parentunit behaviour change button

        self.leadernow = whoinput.leader
        self.battleui.add(*self.leadernow)  # add leader portrait to draw
        self.gameui[0].valueinput(who=whoinput, splithappen=self.splithappen)
        self.gameui[1].valueinput(who=whoinput, splithappen=self.splithappen)

    def unitcardbutton_click(self, who):
        for button in self.unitcardbutton:  # Change subunit card option based on button clicking
            if button.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True
                if self.gameui[2].option != button.event:
                    self.gameui[2].option = button.event
                    self.gameui[2].valueinput(who=who, weaponlist=self.allweapon,
                                              armourlist=self.allarmour,
                                              changeoption=1, splithappen=self.splithappen)

                    if self.gameui[2].option == 2:
                        self.traitskillblit()
                        self.effecticonblit()
                        self.countdownskillicon()
                    else:
                        for icon in self.skill_icon.sprites():
                            icon.kill()
                            del icon
                        for icon in self.effect_icon.sprites():
                            icon.kill()
                            del icon
                break

    def filtertrooplist(self):
        """Filter troop list based on faction picked and type filter"""
        if self.factionpick != 0:
            self.troop_list = [item[1][0] for item in self.gameunitstat.unit_list.items()
                               if item[1][0] == "None" or
                               item[0] in self.allfaction.faction_list[self.factionpick][1]]
            self.troop_index_list = [0] + self.allfaction.faction_list[self.factionpick][1]

        else:  # pick all faction
            self.troop_list = [item[0] for item in self.gameunitstat.unit_list.values()][1:]
            self.troop_index_list = list(range(0, len(self.troop_list)))

        for unit in self.troop_index_list[::-1]:
            if unit != 0:
                if self.filtertroop[0] is False:  # filter out melee infantry
                    if self.gameunitstat.unit_list[unit][8] > self.gameunitstat.unit_list[unit][12] and \
                            self.gameunitstat.unit_list[unit][29] == [1, 0, 1]:
                        self.troop_list.pop(self.troop_index_list.index(unit))
                        self.troop_index_list.remove(unit)

                if self.filtertroop[1] is False:  # filter out range infantry
                    if self.gameunitstat.unit_list[unit][22] != [1, 0] and \
                            self.gameunitstat.unit_list[unit][8] < self.gameunitstat.unit_list[unit][12] and \
                            self.gameunitstat.unit_list[unit][29] == [1, 0, 1]:
                        self.troop_list.pop(self.troop_index_list.index(unit))
                        self.troop_index_list.remove(unit)

                if self.filtertroop[2] is False:  # filter out melee cav
                    if self.gameunitstat.unit_list[unit][8] > self.gameunitstat.unit_list[unit][12] and \
                            self.gameunitstat.unit_list[unit][29] != [1, 0, 1]:
                        self.troop_list.pop(self.troop_index_list.index(unit))
                        self.troop_index_list.remove(unit)

                if self.filtertroop[3] is False:  # filter out range cav
                    if self.gameunitstat.unit_list[unit][22] != [1, 0] and \
                            self.gameunitstat.unit_list[unit][8] < self.gameunitstat.unit_list[unit][12] and \
                            self.gameunitstat.unit_list[unit][29] != [1, 0, 1]:
                        self.troop_list.pop(self.troop_index_list.index(unit))
                        self.troop_index_list.remove(unit)

    def changestate(self):
        self.previous_gamestate = self.gamestate
        if self.gamestate == 1:  # change to battle state
            self.minimap.drawimage(self.showmap.trueimage, self.camera)

            if self.last_selected is not None:  # any parentunit is selected
                self.last_selected = None  # reset last_selected
                self.before_selected = None  # reset before selected parentunit after remove last selected

            self.gameui[1].rect = self.gameui[1].image.get_rect(
                center=(self.gameui[1].x, self.gameui[1].y))  # change leader ui position back
            self.gameui[2].rect = self.gameui[2].image.get_rect(
                center=(self.gameui[2].x, self.gameui[2].y))  # change subunit card position back
            self.buttonui[0].rect = self.buttonui[0].image.get_rect(center=(self.gameui[2].x - 152, self.gameui[2].y + 10))
            self.buttonui[1].rect = self.buttonui[1].image.get_rect(center=(self.gameui[2].x - 152, self.gameui[2].y - 70))
            self.buttonui[2].rect = self.buttonui[2].image.get_rect(center=(self.gameui[2].x - 152, self.gameui[2].y - 30))
            self.buttonui[3].rect = self.buttonui[3].image.get_rect(center=(self.gameui[2].x - 152, self.gameui[2].y + 50))

            self.battleui.remove(self.filter_stuff, self.unitsetup_stuff, self.leadernow, self.buttonui, self.warningmsg)
            self.battleui.add(self.eventlog, self.logscroll, self.buttonui[8:17])

            self.gamespeed = 1

            # v Run starting function
            for unit in self.allunitlist:
                unit.startset(self.subunit)
            for subunit in self.subunit:
                subunit.gamestart(self.camerascale)
            for leader in self.leader_updater:
                leader.gamestart()
            # ^ End starting

        elif self.gamestate == 2:  # change to editor state
            self.inspectui = False  # reset inspect ui
            self.minimap.drawimage(self.showmap.trueimage, self.camera)  # reset minimap
            for arrow in self.arrows:  # remove all range attack
                arrow.kill()
                del arrow

            for unit in self.allunitlist:  # reset all unit state
                unit.command(self.battle_mouse_pos[0], False, False, self.last_mouseover, None, othercommand=2)
            self.gameui[2].rect = self.gameui[2].image.get_rect(bottomright=(SCREENRECT.width,
                                                                             SCREENRECT.height))  # troop info card ui
            self.buttonui[0].rect = self.buttonui[0].image.get_rect(topleft=(self.gameui[2].rect.topleft[0],  # description button
                                                                             self.gameui[2].rect.topleft[1] + 120))
            self.buttonui[1].rect = self.buttonui[1].image.get_rect(topleft=(self.gameui[2].rect.topleft[0],  # stat button
                                                                             self.gameui[2].rect.topleft[1]))
            self.buttonui[2].rect = self.buttonui[2].image.get_rect(topleft=(self.gameui[2].rect.topleft[0],  # skill button
                                                                             self.gameui[2].rect.topleft[1] + 40))
            self.buttonui[3].rect = self.buttonui[3].image.get_rect(topleft=(self.gameui[2].rect.topleft[0],  # equipment button
                                                                             self.gameui[2].rect.topleft[1] + 80))

            self.battleui.remove(self.eventlog, self.logscroll, self.buttonui[0:14], self.gameui[0], self.gameui[3], self.leadernow,
                                 *self.inspectsubunit, self.subunitselectedborder, self.inspectbutton, *self.switch_button)

            self.leadernow = [leader for leader in self.previewleader]  # reset leader in command ui

            self.battleui.add(self.filter_stuff, self.unitsetup_stuff, self.test_button, self.gameui[1:3], self.leadernow, self.buttonui[14:17])
            self.slotdisplay_button.event = 0  # reset display editor ui button to show
            self.gamespeed = 0  # pause battle

            for slot in self.unitbuildslot:
                if slot.troopid != 0:
                    self.gameui[1].valueinput(who=slot)
                    break

        self.speednumber.speedupdate(self.gamespeed)

    def exitbattle(self):
        self.battleui.clear(self.screen, self.background)  # remove all sprite
        self.battlecamera.clear(self.screen, self.background)  # remove all sprite

        self.battleui.remove(self.battle_menu, *self.battle_menu_button, *self.escslidermenu,
                             *self.escvaluebox, self.battledone_box, self.gamedone_button)  # remove menu

        for group in (self.subunit, self.armyleader, self.team0unit, self.team1unit, self.team2unit,
                      self.uniticon, self.troopnumbersprite,
                      self.inspectsubunit):  # remove all reference from battle object
            for stuff in group:
                stuff.delete()
                stuff.kill()
                del stuff

        self.removeunitui()

        for arrow in self.arrows:  # remove all range attack
            arrow.kill()
            del arrow

        self.subunit_selected = None
        self.allunitlist = []
        self.allunitindex = []
        self.combatpathqueue = []
        self.team0poslist, self.team1poslist, self.team2poslist = {}, {}, {}
        self.before_selected = None

        self.drama_timer = 0  # reset drama text popup
        self.battleui.remove(self.textdrama)

        if self.mode == "uniteditor":
            self.showincard = None

            self.battleui.remove(self.unit_delete_button, self.unit_save_button, self.troop_listbox,
                                 self.teamchange_button, self.troop_scroll, self.teamcoa, self.unit_listbox,
                                 self.unit_presetname_scroll, self.filterbox, self.teamchange_button,
                                 self.slotdisplay_button, self.test_button, self.deploy_button, *self.unitcardbutton,
                                 self.terrain_change_button, self.feature_change_button, self.weather_change_button,
                                 *self.unitbuildslot, *self.leadernow, self.presetselectborder,
                                 self.popup_listbox, self.popup_listscroll, *self.popup_namegroup)

            for group in self.troop_namegroup, self.uniteditborder, self.unitpreset_namegroup:
                for item in group:  # remove name list
                    item.kill()
                    del item

            for slot in self.unitbuildslot:  # reset all sub-subunit slot
                slot.changetroop(0, self.baseterrain,
                                 self.baseterrain * len(self.battlemap_feature.featurelist) + self.featureterrain,
                                 self.currentweather)
                slot.leader = None  # remove leader link in

            for leader in self.previewleader:
                leader.change_subunit(None)  # remove subunit link in leader
                leader.change_leader(1, self.leader_stat)

            del self.currentweather

            self.factionpick = 0
            self.filtertroop = [True, True, True, True]
            self.troop_list = [item[0] for item in self.gameunitstat.unit_list.values()][
                              1:]  # reset troop filter back to all faction
            self.troop_index_list = list(range(0, len(self.troop_list) + 1))

            self.leader_list = [item[0] for item in self.leader_stat.leader_list.values()][
                               1:]  # generate leader name list)

            self.leadernow = []

    def rungame(self):
        # v Create Starting Values
        self.mixervolume = SoundVolume
        self.gamestate = 1  # battle mode
        self.current_unit_row = 0
        self.current_troop_row = 0
        self.textinputpopup = (None, None)  # no popup asking for user text input state
        self.leadernow = []  # list of showing leader in command ui
        self.currentweather = None
        self.team_troopnumber = [1, 1, 1]  # reset list of troop number in each team
        self.last_team_troopnumber = [1, 1, 1]
        self.textdrama.queue = []  # reset drama text popup queue
        if self.mode == "uniteditor":
            self.gamestate = 2  # editor mode

            self.full_troop_list = [item[0] for item in self.gameunitstat.unit_list.values()][1:]

            self.troop_list = self.full_troop_list  # generate troop name list
            self.troop_index_list = list(range(0, len(self.troop_list) + 1))

            self.leader_list = [item[0] for item in self.leader_stat.leader_list.values()][1:]  # generate leader name list

            self.main.setuplist(gameprepare.Namelist, self.current_unit_row, list(self.customunitpresetlist.keys()),
                                self.unitpreset_namegroup, self.unit_listbox, self.battleui)  # setup preset army list
            self.main.setuplist(gameprepare.Namelist, self.current_troop_row, self.troop_list,
                                self.troop_namegroup, self.troop_listbox, self.battleui)  # setup troop name list

            self.current_list_show = "troop"
            self.unitpresetname = ""
            self.preparestate = True
            self.baseterrain = 0
            self.featureterrain = 0
            self.weathertype = 4
            self.weatherstrength = 0
            self.currentweather = gameweather.Weather(self.timeui, self.weathertype, self.weatherstrength, self.allweather)
            self.showincard = None  # current sub-subunit showing in subunit card

            self.main.maketeamcoa([0], uiclass=self.battleui, oneteam=True,
                                  team1setpos=(self.troop_listbox.rect.midleft[0] - int((200 * self.widthadjust) / 2),
                                               self.troop_listbox.rect.midleft[1]))  # default faction select as all faction

            self.troop_scroll.changeimage(newrow=self.current_troop_row, logsize=len(self.troop_list))  # change troop scroll image

            for index, slot in enumerate(self.unitbuildslot):  # start with the first player subunit slot selected when enter
                if index == 0:
                    slot.selected = True
                    for border in self.uniteditborder:
                        border.kill()
                        del border
                    self.uniteditborder.add(gameui.Selectedsquad(slot.inspposition))
                    self.battleui.add(*self.uniteditborder)
                else:  # reset all other slot
                    slot.selected = False

            self.weatherschedule = None  # remove weather schedule from editor test

            self.changestate()

            for name in self.unitpreset_namegroup:  # loop to change selected border position to the first in preset list
                self.presetselectborder.changepos(name.rect.topleft)
                break

        else:  # normal battle
            self.changestate()

        self.mapscaledelay = 0  # delay for map zoom input
        self.mousetimer = 0  # This is timer for checking double mouse click, use realtime
        self.ui_timer = 0  # This is timer for ui update function, use realtime
        self.drama_timer = 0  # This is timer for combat related function, use game time (realtime * gamespeed)
        self.dt = 0  # Realtime used for in game calculation
        self.uidt = 0  # Realtime used for ui timer
        self.combattimer = 0  # This is timer for combat related function, use game time (realtime * gamespeed)
        self.last_mouseover = None  # Which subunit last mouse over
        self.speednumber.speedupdate(self.gamespeed)
        self.uiclick = False  # for checking if mouse click is on ui
        self.clickany = False  # For checking if mouse click on anything, if not close ui related to parentunit
        self.newunitclick = False  # For checking if another subunit is clicked when inspect ui open
        self.inspectui = False  # For checking if inspect ui is currently open or not
        self.last_selected = None  # Which unit is last selected
        self.mapviewmode = 0  # default, another one show height map
        self.subunit_selected = None  # which subunit in inspect ui is selected in last update loop
        self.before_selected = None  # Which unit is selected before
        self.splithappen = False  # Check if parentunit get split in that loop
        self.showtroopnumber = True  # for toggle troop number on/off
        self.weatherscreenadjust = SCREENRECT.width / SCREENRECT.height  # for weather sprite spawn position
        self.rightcorner = SCREENRECT.width - 5
        self.bottomcorner = SCREENRECT.height - 5
        self.centerscreen = [SCREENRECT.width / 2, SCREENRECT.height / 2]  # center position of the screen
        self.battle_mouse_pos = [[0, 0],
                                 [0, 0]]  # mouse position list in game not screen, the first without zoom and the second with camera zoom adjust
        self.unitselector.current_row = 0
        # ^ End start value

        self.setup_uniticon()
        self.selectscroll.changeimage(newrow=self.unitselector.current_row)

        self.effect_updater.update(self.allunitlist, self.dt, self.camerascale)

        # self.mapdefarray = []
        # self.mapunitarray = [[x[random.randint(0, 1)] if i != j else 0 for i in range(1000)] for j in range(1000)]

        while True:  # game running
            self.fpscount.fpsshow(self.clock)
            keypress = None
            self.mousepos = pygame.mouse.get_pos()  # current mouse pos based on screen
            mouse_up = False  # left click
            mouse_leftdown = False  # hold left click
            mouse_right = False  # right click
            mouse_rightdown = False  # hold right click
            double_mouse_right = False  # double right click
            mouse_scrolldown = False
            mouse_scrollup = False
            currentui_mouseover = None
            keystate = pygame.key.get_pressed()
            esc_press = False
            self.uiclick = False  # reset mouse check on ui, if stay false it mean mouse click is not on any ui

            self.battleui.clear(self.screen, self.background)  # Clear sprite before update new one

            for event in pygame.event.get():  # get event that happen
                if event.type == QUIT:  # quit game
                    self.textinputpopup = ("confirm_input", "quit")
                    self.confirmui.changeinstruction("Quit Game?")
                    self.battleui.add(*self.confirmui_pop)

                elif event.type == self.SONG_END:  # change music track
                    # pygame.mixer.music.unload()
                    self.pickmusic = random.randint(1, 1)
                    pygame.mixer.music.load(self.musiclist[self.pickmusic])
                    pygame.mixer.music.play(0)

                elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:  # open/close menu
                    esc_press = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # left click
                        mouse_up = True
                    elif event.button == 3:  # Right Click
                        mouse_right = True
                        if self.mousetimer == 0:
                            self.mousetimer = 0.001  # Start timer after first mouse click
                        elif self.mousetimer < 0.3:  # if click again within 0.3 second for it to be considered double click
                            double_mouse_right = True  # double right click
                            self.mousetimer = 0
                    elif event.button == 4:  # Mouse scroll up
                        mouse_scrollup = True
                        rowchange = -1
                    elif event.button == 5:  # Mouse scroll down
                        mouse_scrolldown = True
                        rowchange = 1

                elif event.type == pygame.KEYDOWN:
                    if self.textinputpopup[0] == "text_input":  # event update to input box
                        self.input_box.userinput(event)
                    else:
                        keypress = event.key

                if pygame.mouse.get_pressed()[0]:  # Hold left click
                    mouse_leftdown = True
                elif pygame.mouse.get_pressed()[2]:  # Hold left click
                    mouse_rightdown = True

            if self.textinputpopup == (None, None):
                if esc_press:  # open/close menu
                    if self.gamestate in (1, 2):  # in battle
                        self.gamestate = 0  # open munu
                        self.battleui.add(self.battle_menu)  # add menu to drawer
                        self.battleui.add(*self.battle_menu_button)  # add menu button to

                    elif self.gamestate == 0:  # in menu
                        if self.battle_menu.mode in (0, 1):  # in menu or option
                            if self.battle_menu.mode == 1:  # option menu
                                self.mixervolume = self.oldsetting
                                pygame.mixer.music.set_volume(self.mixervolume)
                                self.escslidermenu[0].update(self.mixervolume, self.escvaluebox[0], forcedvalue=True)
                                self.battle_menu.changemode(0)

                            self.battleui.remove(self.battle_menu, *self.battle_menu_button, *self.escoptionmenubutton,
                                                 *self.escslidermenu, *self.escvaluebox)
                            self.gamestate = self.previous_gamestate

                        elif self.battle_menu.mode == 2:  # encyclopedia
                            self.battleui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll, self.lorenamelist)

                            for name in self.subsection_name:
                                name.kill()
                                del name
                            self.battle_menu.changemode(0)

                            if self.battle_menu not in self.battleui:
                                self.gamestate = self.previous_gamestate
                    elif self.gamestate == 3:
                        self.exitbattle()
                        return  # end battle game loop


                elif mouse_scrollup:  # Mouse scroll up
                    if self.gamestate == 0 and self.battle_menu.mode == 2:  # Scrolling at lore book subsection list
                        if self.lorenamelist.rect.collidepoint(self.mousepos):
                            self.lorebook.current_subsection_row -= 1
                            if self.lorebook.current_subsection_row < 0:
                                self.lorebook.current_subsection_row = 0
                            else:
                                self.lorebook.setup_subsection_list(self.lorenamelist, self.subsection_name)
                                self.lorescroll.changeimage(newrow=self.lorebook.current_subsection_row)

                elif mouse_scrolldown:  # Mouse scroll down
                    if self.gamestate == 0 and self.battle_menu.mode == 2:  # Scrolling at lore book subsection list
                        if self.lorenamelist.rect.collidepoint(self.mousepos):
                            self.lorebook.current_subsection_row += 1
                            if self.lorebook.current_subsection_row + self.lorebook.max_subsection_show - 1 < self.lorebook.logsize:
                                self.lorebook.setup_subsection_list(self.lorenamelist, self.subsection_name)
                                self.lorescroll.changeimage(newrow=self.lorebook.current_subsection_row)
                            else:
                                self.lorebook.current_subsection_row -= 1

                if self.gamestate in (1, 2):  # game in battle state
                    # v register user input during gameplay
                    if mouse_scrollup or mouse_scrolldown:  # Mouse scroll
                        if self.eventlog.rect.collidepoint(self.mousepos):  # Scrolling when mouse at event log
                            self.eventlog.current_start_row += rowchange
                            if mouse_scrollup:
                                if self.eventlog.current_start_row < 0:  # can go no further than the first log
                                    self.eventlog.current_start_row = 0
                                else:
                                    self.eventlog.recreateimage()  # recreate eventlog image
                                    self.logscroll.changeimage(newrow=self.eventlog.current_start_row)
                            elif mouse_scrolldown:
                                if self.eventlog.current_start_row + self.eventlog.max_row_show - 1 < self.eventlog.lencheck and \
                                        self.eventlog.lencheck > 9:
                                    self.eventlog.recreateimage()
                                    self.logscroll.changeimage(newrow=self.eventlog.current_start_row)
                                else:
                                    self.eventlog.current_start_row -= 1

                        elif self.unitselector.rect.collidepoint(self.mousepos):  # Scrolling when mouse at unit selector ui
                            self.unitselector.current_row += rowchange
                            if mouse_scrollup:
                                if self.unitselector.current_row < 0:
                                    self.unitselector.current_row = 0
                                else:
                                    self.setup_uniticon()
                                    self.selectscroll.changeimage(newrow=self.unitselector.current_row)
                            elif mouse_scrolldown:
                                if self.unitselector.current_row < self.unitselector.logsize:
                                    self.setup_uniticon()
                                    self.selectscroll.changeimage(newrow=self.unitselector.current_row)
                                else:
                                    self.unitselector.current_row -= 1
                                    if self.unitselector.current_row < 0:
                                        self.unitselector.current_row = 0

                        elif self.popup_listbox in self.battleui:  # mouse scroll on popup list
                            if self.popup_listbox.type == "terrain":
                                self.currentpopuprow = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.popup_listscroll,
                                                                            self.popup_listbox,
                                                                            self.currentpopuprow, self.battlemap_base.terrainlist,
                                                                            self.popup_namegroup, self.battleui)
                            elif self.popup_listbox.type == "feature":
                                self.currentpopuprow = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.popup_listscroll,
                                                                            self.popup_listbox,
                                                                            self.currentpopuprow, self.battlemap_feature.featurelist,
                                                                            self.popup_namegroup, self.battleui)
                            elif self.popup_listbox.type == "weather":
                                self.currentpopuprow = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.popup_listscroll,
                                                                            self.popup_listbox, self.currentpopuprow, self.weather_list,
                                                                            self.popup_namegroup, self.battleui)
                            elif self.popup_listbox.type == "leader":
                                self.currentpopuprow = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.popup_listscroll,
                                                                            self.popup_listbox, self.currentpopuprow, self.leader_list,
                                                                            self.popup_namegroup, self.battleui, layer=19)

                        elif self.unit_listbox.rect.collidepoint(self.mousepos):  # mouse scroll on unit preset list
                            self.current_unit_row = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.unit_presetname_scroll,
                                                                         self.unit_listbox,
                                                                         self.current_unit_row, list(self.customunitpresetlist.keys()),
                                                                         self.unitpreset_namegroup, self.battleui)
                        elif self.troop_listbox.rect.collidepoint(self.mousepos):
                            if self.current_list_show == "troop":  # mouse scroll on troop list
                                self.current_troop_row = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.troop_scroll, self.troop_listbox,
                                                                              self.current_troop_row, self.troop_list,
                                                                              self.troop_namegroup, self.battleui)
                            elif self.current_list_show == "faction":  # mouse scroll on faction list
                                self.current_troop_row = self.main.listscroll(mouse_scrollup, mouse_scrolldown, self.troop_scroll, self.troop_listbox,
                                                                              self.current_troop_row, self.faction_list,
                                                                              self.troop_namegroup, self.battleui)

                        elif self.mapscaledelay == 0:  # Scrolling in game map to zoom
                            if mouse_scrollup:
                                self.camerascale += 1
                                if self.camerascale > 10:
                                    self.camerascale = 10
                                else:
                                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                                    self.showmap.changescale(self.camerascale)
                                    if self.gamestate == 1:  # only have delay in battle mode
                                        self.mapscaledelay = 0.001

                            elif mouse_scrolldown:
                                self.camerascale -= 1
                                if self.camerascale < 1:
                                    self.camerascale = 1
                                else:
                                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                                    self.showmap.changescale(self.camerascale)
                                    if self.gamestate == 1:  # only have delay in battle mode
                                        self.mapscaledelay = 0.001
                    # ^ End mouse scroll input

                    # keyboard input
                    if keypress == pygame.K_TAB:
                        if self.mapviewmode == 0:  # Currently in normal map mode
                            self.mapviewmode = 1
                            self.showmap.changemode(self.mapviewmode)
                        else:  # Currently in height mode
                            self.mapviewmode = 0
                            self.showmap.changemode(self.mapviewmode)
                        self.showmap.changescale(self.camerascale)

                    elif keypress == pygame.K_o:  # Speed Pause/unpause Button
                        if self.showtroopnumber:
                            self.showtroopnumber = False
                            self.effect_updater.remove(*self.troopnumbersprite)
                            self.battlecamera.remove(*self.troopnumbersprite)
                        else:  # speed currently pause
                            self.showtroopnumber = True
                            self.effect_updater.add(*self.troopnumbersprite)
                            self.battlecamera.add(*self.troopnumbersprite)

                    elif keypress == pygame.K_p:  # Speed Pause/unpause Button
                        if self.gamespeed >= 0.5:  #
                            self.gamespeed = 0  # pause game speed
                        else:  # speed currently pause
                            self.gamespeed = 1  # unpause game and set to speed 1
                        self.speednumber.speedupdate(self.gamespeed)

                    elif keypress == pygame.K_KP_MINUS:  # reduce game speed
                        newindex = self.gamespeedset.index(self.gamespeed) - 1
                        if newindex >= 0:  # cannot reduce game speed than what is available
                            self.gamespeed = self.gamespeedset[newindex]
                        self.speednumber.speedupdate(self.gamespeed)

                    elif keypress == pygame.K_KP_PLUS:  # increase game speed
                        newindex = self.gamespeedset.index(self.gamespeed) + 1
                        if newindex < len(self.gamespeedset):  # cannot increase game speed than what is available
                            self.gamespeed = self.gamespeedset[newindex]
                        self.speednumber.speedupdate(self.gamespeed)

                    elif keypress == pygame.K_PAGEUP:  # Go to top of event log
                        self.eventlog.current_start_row = 0
                        self.eventlog.recreateimage()
                        self.logscroll.changeimage(newrow=self.eventlog.current_start_row)

                    elif keypress == pygame.K_PAGEDOWN:  # Go to bottom of event log
                        if self.eventlog.lencheck > self.eventlog.max_row_show:
                            self.eventlog.current_start_row = self.eventlog.lencheck - self.eventlog.max_row_show
                            self.eventlog.recreateimage()
                            self.logscroll.changeimage(newrow=self.eventlog.current_start_row)

                    elif keypress == pygame.K_SPACE and self.last_selected is not None:
                        self.last_selected.command(self.battle_mouse_pos[0], False, False, self.last_mouseover, None, othercommand=2)

                    # vv FOR DEVELOPMENT DELETE LATER
                    elif keypress == pygame.K_1:
                        self.textdrama.queue.append("Hello and Welcome to update video")
                    elif keypress == pygame.K_2:
                        self.textdrama.queue.append("Showcase: New melee combat test")
                    elif keypress == pygame.K_3:
                        self.textdrama.queue.append("Also add pathfind algorithm for melee combat")
                    elif keypress == pygame.K_4:
                        self.textdrama.queue.append("The combat mechanic will be much more dynamic")
                    elif keypress == pygame.K_5:
                        self.textdrama.queue.append("Will take a while for everything to work again")
                    elif keypress == pygame.K_6:
                        self.textdrama.queue.append("Current special effect still need rework")
                    elif keypress == pygame.K_n and self.last_selected is not None:
                        if self.last_selected.team == 1:
                            self.last_selected.switchfaction(self.team1unit, self.team2unit, self.team1poslist, self.enactment)
                        else:
                            self.last_selected.switchfaction(self.team2unit, self.team1unit, self.team2poslist, self.enactment)
                    elif keypress == pygame.K_l and self.last_selected is not None:
                        for subunit in self.last_selected.subunit_sprite:
                            subunit.base_morale = 0
                    elif keypress == pygame.K_k and self.last_selected is not None:
                        # for index, subunit in enumerate(self.last_selected.subunit_sprite):
                        #     subunit.unit_health -= subunit.unit_health
                        self.subunit_selected.who.unit_health -= self.subunit_selected.who.unit_health
                    elif keypress == pygame.K_m and self.last_selected is not None:
                        # self.last_selected.leader[0].health -= 1000
                        self.subunit_selected.who.leader.health -= 1000
                        # self.subunit_selected.who.base_morale -= 1000
                        # self.subunit_selected.who.brokenlimit = 80
                        # self.subunit_selected.who.state = 99
                    elif keypress == pygame.K_COMMA and self.last_selected is not None:
                        for index, subunit in enumerate(self.last_selected.subunit_sprite):
                            subunit.stamina -= subunit.stamina
                    # ^^ End For development test
                    # ^ End register input

                    # v Camera movement
                    if keystate[K_s] or self.mousepos[1] >= self.bottomcorner:  # Camera move down
                        self.basecamerapos[1] += 5 * (
                                11 - self.camerascale)  # need "11 -" for converting cameral scale so the further zoom camera move faster
                        self.camerapos[1] = self.basecamerapos[1] * self.camerascale  # resize camera pos
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

                    self.cameraupcorner = (self.camerapos[0] - self.centerscreen[0],
                                           self.camerapos[1] - self.centerscreen[1])  # calculate top left corner of camera position
                    # ^ End camera movement

                    if self.mousetimer != 0:  # player click mouse once before
                        self.mousetimer += self.uidt  # increase timer for mouse click using real time
                        if self.mousetimer >= 0.3:  # time pass 0.3 second no longer count as double click
                            self.mousetimer = 0

                    if self.mapscaledelay > 0:  # player change map scale once before
                        self.mapscaledelay += self.uidt
                        if self.mapscaledelay >= 0.1:  # delay for 1 second until user can change scale again
                            self.mapscaledelay = 0

                    self.battle_mouse_pos[0] = pygame.Vector2((self.mousepos[0] - self.centerscreen[0]) + self.camerapos[0],
                                                              self.mousepos[1] - self.centerscreen[1] + self.camerapos[
                                                                  1])  # mouse pos on the map based on camera position
                    self.battle_mouse_pos[1] = self.battle_mouse_pos[0] / self.camerascale  # mouse pos on the map at current camera zoom scale

                    if self.terraincheck in self.battleui and (
                            self.terraincheck.pos != self.mousepos or keystate[K_s] or keystate[K_w] or keystate[K_a] or keystate[K_d]):
                        self.battleui.remove(self.terraincheck)  # remove terrain popup when move mouse or camera

                    if mouse_up or mouse_right or mouse_leftdown or mouse_rightdown:
                        if mouse_up:
                            self.clickany = False
                            self.newunitclick = False

                        if self.minimap.rect.collidepoint(self.mousepos):  # mouse position on mini map
                            self.uiclick = True
                            if mouse_up:  # move game camera to position clicked on mini map
                                self.clickany = True
                                posmask = pygame.Vector2(int(self.mousepos[0] - self.minimap.rect.x), int(self.mousepos[1] - self.minimap.rect.y))
                                self.basecamerapos = posmask * 5
                                self.camerapos = self.basecamerapos * self.camerascale
                            elif mouse_right:  # nothing happen with mouse right
                                if self.last_selected is not None:
                                    self.uiclick = True
                        elif self.selectscroll.rect.collidepoint(self.mousepos):  # Must check mouse collide for scroller before unit select ui
                            self.uiclick = True
                            if mouse_leftdown or mouse_up:
                                self.clickany = True
                                newrow = self.selectscroll.update(self.mousepos)
                                if self.unitselector.current_row != newrow:
                                    self.unitselector.current_row = newrow
                                    self.setup_uniticon()

                        elif self.unitselector.rect.collidepoint(self.mousepos):  # check mouse collide for unit selector ui
                            if mouse_up:
                                self.clickany = True
                            self.uiclick = True
                            self.uniticon_mouseover(mouse_up, mouse_right)

                        elif self.test_button.rect.collidepoint(self.mousepos) and self.test_button in self.battleui:
                            self.uiclick = True
                            if mouse_up:
                                self.clickany = True
                                if self.test_button.event == 0:
                                    self.test_button.event = 1
                                    newmode = 1

                                elif self.test_button.event == 1:
                                    self.test_button.event = 0
                                    newmode = 2
                                self.gamestate = newmode
                                self.changestate()

                        if self.gamestate == 1:
                            if self.logscroll.rect.collidepoint(self.mousepos):  # Must check mouse collide for scroller before event log ui
                                self.uiclick = True
                                if mouse_leftdown or mouse_up:
                                    self.clickany = True
                                    newrow = self.logscroll.update(self.mousepos)
                                    if self.eventlog.current_start_row != newrow:
                                        self.eventlog.current_start_row = newrow
                                        self.eventlog.recreateimage()

                            elif self.eventlog.rect.collidepoint(self.mousepos):  # check mouse collide for event log ui
                                if mouse_up:
                                    self.clickany = True
                                self.uiclick = True

                            elif self.timeui.rect.collidepoint(self.mousepos):  # check mouse collide for time bar ui
                                if mouse_up:
                                    self.clickany = True
                                self.uiclick = True

                            elif self.ui_mouseover():  # check mouse collide for other ui
                                pass

                            elif self.button_mouseover(mouse_right):  # check mouse collide for button
                                pass

                            elif mouse_right and self.last_selected is None and self.uiclick is False:  # draw terrain popup ui when right click at map with no selected parentunit
                                if 0 <= self.battle_mouse_pos[1][0] <= 999 and \
                                        0 <= self.battle_mouse_pos[1][1] <= 999:  # not draw if pos is off the map
                                    terrainpop, featurepop = self.battlemap_feature.getfeature(self.battle_mouse_pos[1], self.battlemap_base)
                                    featurepop = self.battlemap_feature.featuremod[featurepop]
                                    heightpop = self.battlemap_height.getheight(self.battle_mouse_pos[1])
                                    self.terraincheck.pop(self.mousepos, featurepop, heightpop)
                                    self.battleui.add(self.terraincheck)

                            for index, button in enumerate(self.screenbuttonlist):  # Event log button and timer button click
                                if button.rect.collidepoint(self.mousepos):
                                    if index in (0, 1, 2, 3, 4, 5):  # eventlog button
                                        self.uiclick = True
                                        if mouse_up:
                                            if button.event in (0, 1, 2, 3):  # change tab mode
                                                self.eventlog.changemode(button.event)
                                            elif button.event == 4:  # delete tab log button
                                                self.eventlog.cleartab()
                                            elif button.event == 5:  # delete all tab log button
                                                self.eventlog.cleartab(alltab=True)

                                    elif index in (6, 7, 8):  # timer button
                                        self.uiclick = True
                                        if mouse_up:
                                            if button.event == 0:  # pause button
                                                self.gamespeed = 0
                                            elif button.event == 1:  # reduce speed button
                                                newindex = self.gamespeedset.index(self.gamespeed) - 1
                                                if newindex >= 0:
                                                    self.gamespeed = self.gamespeedset[newindex]
                                            elif button.event == 2:  # increase speed button
                                                newindex = self.gamespeedset.index(self.gamespeed) + 1
                                                if newindex < len(self.gamespeedset):
                                                    self.gamespeed = self.gamespeedset[newindex]
                                            self.speednumber.speedupdate(self.gamespeed)
                                    break

                            # v code that only run when any unit is selected
                            if self.last_selected is not None and self.last_selected.state != 100:
                                if self.inspectbutton.rect.collidepoint(self.mousepos) or (
                                        mouse_up and self.inspectui and self.newunitclick):  # click on inspect ui open/close button
                                    if self.inspectbutton.rect.collidepoint(self.mousepos):
                                        self.button_name_popup.pop(self.mousepos, "Inspect Subunit")
                                        self.battleui.add(self.button_name_popup)
                                        if mouse_right:
                                            self.uiclick = True  # for some reason the loop mouse check above does not work for inspect button, so it here instead
                                    if mouse_up:
                                        if self.inspectui is False:  # Add unit inspect ui when left click at ui button or when change subunit with inspect open
                                            self.inspectui = True
                                            self.battleui.add(*self.gameui[2:4])
                                            self.battleui.add(*self.unitcardbutton)
                                            self.subunit_selected = None

                                            for index, subunit in enumerate(self.last_selected.subunit_sprite_array.flat):
                                                if subunit is not None:
                                                    self.inspectsubunit[index].addsubunit(subunit)
                                                    self.battleui.add(self.inspectsubunit[index])
                                                    if self.subunit_selected is None:
                                                        self.subunit_selected = self.inspectsubunit[index]

                                            self.subunitselectedborder.pop(self.subunit_selected.pos)
                                            self.battleui.add(self.subunitselectedborder)
                                            self.gameui[2].valueinput(who=self.subunit_selected.who, weaponlist=self.allweapon,
                                                                      armourlist=self.allarmour,
                                                                      splithappen=self.splithappen)

                                            if self.gameui[2].option == 2:  # blit skill icon is previous mode is skill
                                                self.traitskillblit()
                                                self.effecticonblit()
                                                self.countdownskillicon()

                                        elif self.inspectui:  # Remove when click again and the ui already open
                                            self.battleui.remove(*self.inspectsubunit, self.subunitselectedborder)
                                            for ui in self.gameui[2:4]:
                                                ui.kill()
                                            for button in self.unitcardbutton:
                                                button.kill()
                                            self.inspectui = False
                                            self.newunitclick = False

                                elif self.gameui[1] in self.battleui and (
                                        self.gameui[1].rect.collidepoint(self.mousepos) or keypress is not None):  # mouse position on command ui
                                    if self.last_selected.control:
                                        if self.switch_button[0].rect.collidepoint(self.mousepos) or keypress == pygame.K_g:
                                            if mouse_up or keypress == pygame.K_g:  # rotate skill condition when clicked
                                                self.last_selected.skill_cond += 1
                                                if self.last_selected.skill_cond > 3:
                                                    self.last_selected.skill_cond = 0
                                                self.switch_button[0].event = self.last_selected.skill_cond
                                            if self.switch_button[0].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                                poptext = ("Free Skill Use", "Conserve 50% Stamina", "Conserve 25% stamina", "Forbid Skill")
                                                self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[0].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.switch_button[1].rect.collidepoint(self.mousepos) or keypress == pygame.K_f:
                                            if mouse_up or keypress == pygame.K_f:  # rotate fire at will condition when clicked
                                                self.last_selected.fireatwill += 1
                                                if self.last_selected.fireatwill > 1:
                                                    self.last_selected.fireatwill = 0
                                                self.switch_button[1].event = self.last_selected.fireatwill
                                            if self.switch_button[1].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                                poptext = ("Fire at will", "Hold fire until order")
                                                self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[1].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.switch_button[2].rect.collidepoint(self.mousepos) or keypress == pygame.K_h:
                                            if mouse_up or keypress == pygame.K_h:  # rotate hold condition when clicked
                                                self.last_selected.hold += 1
                                                if self.last_selected.hold > 2:
                                                    self.last_selected.hold = 0
                                                self.switch_button[2].event = self.last_selected.hold
                                            if self.switch_button[2].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                                poptext = ("Aggressive", "Skirmish/Scout", "Hold Ground")
                                                self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[2].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.switch_button[3].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                                            if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                                self.last_selected.use_min_range += 1
                                                if self.last_selected.use_min_range > 1:
                                                    self.last_selected.use_min_range = 0
                                                self.switch_button[3].event = self.last_selected.use_min_range
                                            if self.switch_button[3].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                                poptext = ("Minimum Shoot Range", "Maximum Shoot range")
                                                self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[3].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.switch_button[4].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                                            if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                                self.last_selected.shoothow += 1
                                                if self.last_selected.shoothow > 2:
                                                    self.last_selected.shoothow = 0
                                                self.switch_button[4].event = self.last_selected.shoothow
                                            if self.switch_button[4].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                                poptext = ("Both Arc and Direct Shot", "Only Arc Shot", "Only Direct Shot")
                                                self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[4].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.switch_button[5].rect.collidepoint(self.mousepos) or keypress == pygame.K_j:
                                            if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                                self.last_selected.runtoggle += 1
                                                if self.last_selected.runtoggle > 1:
                                                    self.last_selected.runtoggle = 0
                                                self.switch_button[5].event = self.last_selected.runtoggle
                                            if self.switch_button[5].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                                poptext = ("Toggle Walk", "Toggle Run")
                                                self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[5].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.switch_button[6].rect.collidepoint(self.mousepos):  # or keypress == pygame.K_j
                                            if mouse_up:  # or keypress == pygame.K_j  # rotate min range condition when clicked
                                                self.last_selected.attackmode += 1
                                                if self.last_selected.attackmode > 2:
                                                    self.last_selected.attackmode = 0
                                                self.switch_button[6].event = self.last_selected.attackmode
                                            if self.switch_button[6].rect.collidepoint(self.mousepos):  # popup name when mouse over
                                                poptext = ("Frontline Attack Only", "Keep Formation", "All Out Attack")
                                                self.button_name_popup.pop(self.mousepos, poptext[self.switch_button[6].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.col_split_button in self.battleui and self.col_split_button.rect.collidepoint(self.mousepos):
                                            self.button_name_popup.pop(self.mousepos, "Split By Middle Column")
                                            self.battleui.add(self.button_name_popup)
                                            if mouse_up and self.last_selected.state != 10:
                                                self.splitunit(self.last_selected, 1)
                                                self.splithappen = True
                                                self.checksplit(self.last_selected)
                                                self.battleui.remove(*self.leadernow)
                                                self.leadernow = self.last_selected.leader
                                                self.battleui.add(*self.leadernow)
                                                self.setup_uniticon()

                                        elif self.rowsplitbutton in self.battleui and self.rowsplitbutton.rect.collidepoint(self.mousepos):
                                            self.button_name_popup.pop(self.mousepos, "Split by Middle Row")
                                            self.battleui.add(self.button_name_popup)
                                            if mouse_up and self.last_selected.state != 10:
                                                self.splitunit(self.last_selected, 0)
                                                self.splithappen = True
                                                self.checksplit(self.last_selected)
                                                self.battleui.remove(*self.leadernow)
                                                self.leadernow = self.last_selected.leader
                                                self.battleui.add(*self.leadernow)
                                                self.setup_uniticon()

                                        elif self.buttonui[7].rect.collidepoint(self.mousepos):  # decimation effect
                                            self.button_name_popup.pop(self.mousepos, "Decimation")
                                            self.battleui.add(self.button_name_popup)
                                            if mouse_up and self.last_selected.state == 0:
                                                for subunit in self.last_selected.subunit_sprite:
                                                    subunit.status_effect[98] = self.gameunitstat.status_list[98].copy()
                                                    subunit.unit_health -= round(subunit.unit_health * 0.1)
                                    if self.leader_mouseover(mouse_right):
                                        self.battleui.remove(self.button_name_popup)
                                        pass
                                else:
                                    self.battleui.remove(self.leaderpopup)  # remove leader name popup if no mouseover on any button
                                    self.battleui.remove(self.button_name_popup)  # remove popup if no mouseover on any button

                                if self.inspectui:  # if inspect ui is openned
                                    if mouse_up or mouse_right:
                                        if self.gameui[3].rect.collidepoint(self.mousepos):  # if mouse pos inside unit ui when click
                                            self.clickany = True  # for avoding right click or  subunit
                                            self.uiclick = True  # for avoiding clicking subunit under ui
                                            for subunit in self.inspectsubunit:
                                                if subunit.rect.collidepoint(
                                                        self.mousepos) and subunit in self.battleui:  # Change showing stat to the clicked subunit one
                                                    if mouse_up:
                                                        self.subunit_selected = subunit
                                                        self.subunitselectedborder.pop(self.subunit_selected.pos)
                                                        self.eventlog.addlog(
                                                            [0, str(self.subunit_selected.who.board_pos) + " " + str(
                                                                self.subunit_selected.who.name) + " in " +
                                                             self.subunit_selected.who.parentunit.leader[0].name + "'s parentunit is selected"], [3])
                                                        self.battleui.add(self.subunitselectedborder)
                                                        self.gameui[2].valueinput(who=self.subunit_selected.who, weaponlist=self.allweapon,
                                                                                  armourlist=self.allarmour, splithappen=self.splithappen)

                                                        if self.gameui[2].option == 2:
                                                            self.traitskillblit()
                                                            self.effecticonblit()
                                                            self.countdownskillicon()
                                                        else:
                                                            for icon in self.skill_icon.sprites():
                                                                icon.kill()
                                                                del icon
                                                            for icon in self.effect_icon.sprites():
                                                                icon.kill()
                                                                del icon

                                                    elif mouse_right:
                                                        self.popout_lorebook(3, subunit.who.troopid)
                                                    break

                                        elif self.gameui[2].rect.collidepoint(self.mousepos):  # mouse position in subunit card
                                            self.clickany = True
                                            self.uiclick = True  # for avoiding clicking subunit under ui
                                            self.unitcardbutton_click(self.subunit_selected.who)

                                    if self.gameui[2].option == 2:
                                        if self.effecticon_mouseover(self.skill_icon, mouse_right):
                                            pass
                                        elif self.effecticon_mouseover(self.effect_icon, mouse_right):
                                            pass
                                        else:
                                            self.battleui.remove(self.effectpopup)

                                else:
                                    for icon in self.skill_icon.sprites():
                                        icon.kill()
                                        del icon
                                    for icon in self.effect_icon.sprites():
                                        icon.kill()
                                        del icon

                                if mouse_right and self.uiclick is False:  # Unit command
                                    self.last_selected.command(self.battle_mouse_pos[1], mouse_right, double_mouse_right,
                                                               self.last_mouseover, keystate)

                                self.before_selected = self.last_selected

                            # ^ End subunit selected code

                        elif self.gamestate == 2:  # uniteditor state
                            self.battleui.remove(self.leaderpopup)
                            if self.popup_listbox in self.battleui and self.popup_listbox.type == "leader" \
                                    and self.popup_listbox.rect.collidepoint(
                                self.mousepos):  # this need to be at the top here to prioritise popup click
                                self.uiclick = True
                                for index, name in enumerate(self.popup_namegroup):  # change leader with the new selected one
                                    if name.rect.collidepoint(self.mousepos):
                                        if mouse_up and (self.showincard is not None and self.showincard.name != "None"):
                                            if self.showincard.leader is not None and \
                                                    self.leadernow[self.showincard.leader.armyposition].name != "None":  # remove old leader
                                                self.leadernow[self.showincard.leader.armyposition].change_leader(1, self.leader_stat)
                                                self.leadernow[self.showincard.leader.armyposition].change_subunit(None)

                                            trueindex = [index for index, value in
                                                         enumerate(list(self.leader_stat.leader_list.values())) if value[0] == name.name][0]
                                            trueindex = list(self.leader_stat.leader_list.keys())[trueindex]
                                            self.leadernow[self.selectleader].change_leader(trueindex, self.leader_stat)
                                            self.leadernow[self.selectleader].change_subunit(self.showincard)
                                            self.showincard.leader = self.leadernow[self.selectleader]
                                            self.previewauthority(self.leadernow, self.leadernow[self.selectleader].subunit.armyid)
                                            self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                                      changeoption=1)
                                            unitdict = self.convertslot_dict("test")
                                            if unitdict is not None:
                                                warnlist = []
                                                leaderlist = [int(item) for item in unitdict['test'][-3].split(",")]
                                                leaderlist = [item for item in leaderlist if 1 < item < 10000]
                                                leaderlistset = set(leaderlist)
                                                if len(leaderlist) != len(leaderlistset):  # unit has duplicate unique leader
                                                    warnlist.append(self.warningmsg.duplicateleader_warn)
                                                if unitdict['test'][-1] == "0":  # unit has leader/unit of multi faction
                                                    warnlist.append(self.warningmsg.multifaction_warn)
                                                if len(warnlist) > 0:
                                                    self.warningmsg.warning(warnlist)
                                                    self.battleui.add(self.warningmsg)

                                        elif mouse_right:
                                            self.popout_lorebook(8, self.currentpopuprow + index + 1)

                            elif self.unit_listbox.rect.collidepoint(self.mousepos) and self.unit_listbox in self.battleui:
                                self.uiclick = True
                                for index, name in enumerate(self.unitpreset_namegroup):
                                    if name.rect.collidepoint(self.mousepos) and mouse_up:
                                        self.presetselectborder.changepos(name.rect.topleft)  # change border to one selected
                                        if list(self.customunitpresetlist.keys())[index] != "New Preset":
                                            self.unitpresetname = name.name
                                            unitlist = []
                                            arraylist = list(self.customunitpresetlist[list(self.customunitpresetlist.keys())[index]])
                                            for listnum in (0, 1, 2, 3, 4, 5, 6, 7):
                                                unitlist += [int(item) if item.isdigit() else item
                                                             for item in arraylist[listnum].split(",")]
                                            leaderwholist = [int(item) if item.isdigit() else item
                                                             for item in arraylist[8].split(",")]
                                            leaderposlist = [int(item) if item.isdigit() else item
                                                             for item in arraylist[9].split(",")]

                                            for unitindex, item in enumerate(unitlist):  # change all slot to whatever save in the selected preset
                                                for slot in self.unitbuildslot:
                                                    if slot.gameid == unitindex:
                                                        slot.changetroop(item, self.baseterrain,
                                                                         self.baseterrain * len(self.battlemap_feature.featurelist)
                                                                         + self.featureterrain, self.currentweather)
                                                        break

                                            for leaderindex, item in enumerate(leaderwholist):
                                                self.previewleader[leaderindex].leader = None
                                                if self.previewleader[leaderindex].subunit is not None:
                                                    self.previewleader[leaderindex].subunit.leader = None

                                                self.previewleader[leaderindex].change_leader(item, self.leader_stat)

                                                posindex = 0
                                                for slot in self.unitbuildslot:  # can't use gameid here as none subunit not count in position check
                                                    if posindex == leaderposlist[leaderindex]:
                                                        self.previewleader[leaderindex].change_subunit(slot)
                                                        slot.leader = self.previewleader[leaderindex]
                                                        break
                                                    else:
                                                        if slot.name != "None":
                                                            posindex += 1

                                            self.leadernow = [leader for leader in self.previewleader]
                                            self.battleui.add(*self.leadernow)  # add leader portrait to draw
                                            self.showincard = slot
                                            self.gameui[1].valueinput(who=self.showincard)
                                            self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                      armourlist=self.allarmour)  # update subunit card on selected subunit
                                            if self.gameui[2].option == 2:
                                                self.traitskillblit()
                                                self.effecticonblit()
                                                self.countdownskillicon()
                                            # self.previewauthority(self.previewleader, 0)  # calculate authority

                                        else:  # new preset
                                            self.unitpresetname = ""
                                            for slot in self.unitbuildslot:  # reset all sub-subunit slot
                                                slot.changetroop(0, self.baseterrain,
                                                                 self.baseterrain * len(self.battlemap_feature.featurelist) + self.featureterrain,
                                                                 self.currentweather)
                                                slot.leader = None  # remove leader link in

                                            for leader in self.previewleader:
                                                leader.change_subunit(None)  # remove subunit link in leader
                                                leader.change_leader(1, self.leader_stat)

                                            self.leadernow = [leader for leader in self.previewleader]
                                            self.battleui.add(*self.leadernow)  # add leader portrait to draw
                                            self.showincard = slot
                                            self.gameui[1].valueinput(who=self.showincard)

                                            # self.gameui[2].valueinput(attacker=self.showincard, weapon_list=self.allweapon, armour_list=self.allarmour,
                                            #                       changeoption=1)

                            elif self.gameui[1] in self.battleui and self.gameui[1].rect.collidepoint(self.mousepos):
                                self.uiclick = True
                                for leaderindex, leader in enumerate(self.leadernow):  # loop mouse pos on leader portrait
                                    if leader.rect.collidepoint(self.mousepos):
                                        armyposition = self.leaderposname[leader.armyposition + 4]

                                        self.leaderpopup.pop(self.mousepos, armyposition + ": " + leader.name)  # popup leader name when mouse over
                                        self.battleui.add(self.leaderpopup)

                                        if mouse_up:  # open list of leader to change leader in that slot
                                            self.selectleader = leaderindex
                                            self.popuplist_newopen(leader.rect.midright, self.leader_list, "leader")

                                        elif mouse_right:
                                            self.popout_lorebook(8, leader.leaderid)
                                        break

                            elif self.gameui[2].rect.collidepoint(self.mousepos):
                                self.uiclick = True
                                if self.showincard is not None and mouse_up:
                                    self.unitcardbutton_click(self.showincard)

                                if self.gameui[2].option == 2:
                                    for iconlist in (self.effect_icon, self.skill_icon):
                                        if self.effecticon_mouseover(self.skill_icon, mouse_right):
                                            pass
                                        elif self.effecticon_mouseover(self.effect_icon, mouse_right):
                                            pass
                                        else:
                                            self.battleui.remove(self.effectpopup)

                            elif mouse_up or mouse_leftdown or mouse_right:  # left click for select, hold left mouse for scrolling, right click for encyclopedia
                                if mouse_up or mouse_leftdown:
                                    if self.popup_listbox in self.battleui:
                                        if self.popup_listbox.rect.collidepoint(self.mousepos):
                                            self.uiclick = True
                                            for index, name in enumerate(self.popup_namegroup):
                                                if name.rect.collidepoint(self.mousepos) and mouse_up:  # click on name in list
                                                    if self.popup_listbox.type == "terrain":
                                                        self.terrain_change_button.changetext(self.battlemap_base.terrainlist[index])
                                                        self.baseterrain = index
                                                        self.editor_map_change(gamemap.terraincolour[self.baseterrain],
                                                                               gamemap.featurecolour[self.featureterrain])

                                                    elif self.popup_listbox.type == "feature":
                                                        self.feature_change_button.changetext(self.battlemap_feature.featurelist[index])
                                                        self.featureterrain = index
                                                        self.editor_map_change(gamemap.terraincolour[self.baseterrain],
                                                                               gamemap.featurecolour[self.featureterrain])

                                                    elif self.popup_listbox.type == "weather":
                                                        self.weathertype = int(index / 3)
                                                        self.weatherstrength = index - (self.weathertype * 3)
                                                        self.weather_change_button.changetext(self.weather_list[index])
                                                        del self.currentweather
                                                        self.currentweather = gameweather.Weather(self.timeui, self.weathertype + 1,
                                                                                                  self.weatherstrength, self.allweather)

                                                    for slot in self.unitbuildslot:  # reset all troop stat
                                                        slot.changetroop(slot.troopid, self.baseterrain,
                                                                         self.baseterrain * len(
                                                                             self.battlemap_feature.featurelist) + self.featureterrain,
                                                                         self.currentweather)
                                                    if self.showincard is not None:  # reset subunit card as well
                                                        self.gameui[1].valueinput(who=self.showincard)
                                                        self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                                  armourlist=self.allarmour,
                                                                                  changeoption=1)
                                                        if self.gameui[2].option == 2:
                                                            self.traitskillblit()
                                                            self.effecticonblit()
                                                            self.countdownskillicon()

                                                    for thisname in self.popup_namegroup:  # remove troop name list
                                                        thisname.kill()
                                                        del thisname

                                                    self.battleui.remove(self.popup_listbox, self.popup_listscroll)
                                                    break

                                        elif self.popup_listscroll.rect.collidepoint(self.mousepos):  # scrolling on list
                                            self.uiclick = True
                                            self.currentpopuprow = self.popup_listscroll.update(
                                                self.mousepos)  # update the scroller and get new current subsection
                                            if self.popup_listbox.type == "terrain":
                                                self.main.setuplist(gameprepare.Namelist, self.currentpopuprow, self.battlemap_base.terrainlist,
                                                                    self.popup_namegroup, self.popup_listbox, self.battleui, layer=17)
                                            elif self.popup_listbox.type == "feature":
                                                self.main.setuplist(gameprepare.Namelist, self.currentpopuprow, self.battlemap_feature.featurelist,
                                                                    self.popup_namegroup, self.popup_listbox, self.battleui, layer=17)
                                            elif self.popup_listbox.type == "weather":
                                                self.main.setuplist(gameprepare.Namelist, self.currentpopuprow, self.weather_list,
                                                                    self.popup_namegroup,
                                                                    self.popup_listbox, self.battleui, layer=17)
                                            elif self.popup_listbox.type == "leader":
                                                self.main.setuplist(gameprepare.Namelist, self.currentpopuprow, self.leader_list,
                                                                    self.popup_namegroup,
                                                                    self.popup_listbox, self.battleui, layer=19)

                                        else:
                                            self.battleui.remove(self.popup_listbox, self.popup_listscroll, *self.popup_namegroup)

                                    elif self.troop_scroll.rect.collidepoint(self.mousepos):  # click on subsection list scroller
                                        self.uiclick = True
                                        self.current_troop_row = self.troop_scroll.update(
                                            self.mousepos)  # update the scroller and get new current subsection
                                        if self.current_list_show == "troop":
                                            self.main.setuplist(gameprepare.Namelist, self.current_troop_row, self.troop_list, self.troop_namegroup,
                                                                self.troop_listbox, self.battleui)
                                        elif self.current_list_show == "faction":
                                            self.main.setuplist(gameprepare.Namelist, self.current_troop_row, self.faction_list, self.troop_namegroup,
                                                                self.troop_listbox, self.battleui)

                                    elif self.unit_presetname_scroll.rect.collidepoint(self.mousepos):
                                        self.uiclick = True
                                        self.current_unit_row = self.unit_presetname_scroll.update(
                                            self.mousepos)  # update the scroller and get new current subsection
                                        self.main.setuplist(gameprepare.Namelist, self.current_unit_row, list(self.customunitpresetlist.keys()),
                                                            self.unitpreset_namegroup, self.unit_listbox, self.battleui)  # setup preset army list

                                    elif self.unitbuildslot in self.battleui:
                                        slotclick = None
                                        for slot in self.unitbuildslot:  # left click on any sub-subunit slot
                                            if slot.rect.collidepoint(self.mousepos):
                                                self.uiclick = True
                                                slotclick = slot
                                                break

                                        if slotclick is not None:
                                            if keystate[pygame.K_LSHIFT] or keystate[pygame.K_RSHIFT]:  # add all sub-subunit from the first selected
                                                firstone = None
                                                for newslot in self.unitbuildslot:
                                                    if newslot.armyid == slotclick.armyid and newslot.gameid <= slotclick.gameid:
                                                        if firstone is None and newslot.selected:  # found the previous selected sub-subunit
                                                            firstone = newslot.gameid
                                                            if slotclick.gameid <= firstone:  # cannot go backward, stop loop
                                                                break
                                                            elif slotclick.selected is False:  # forward select, acceptable
                                                                slotclick.selected = True
                                                                self.uniteditborder.add(gameui.Selectedsquad(slotclick.inspposition, 5))
                                                                self.battleui.add(*self.uniteditborder)
                                                        elif firstone is not None and newslot.gameid > firstone and newslot.selected is False:  # select from first select to clicked
                                                            newslot.selected = True
                                                            self.uniteditborder.add(gameui.Selectedsquad(newslot.inspposition, 5))
                                                            self.battleui.add(*self.uniteditborder)

                                            elif keystate[pygame.K_LCTRL] or keystate[
                                                pygame.K_RCTRL]:  # add another selected sub-subunit with left ctrl + left mouse button
                                                if slotclick.selected is False:
                                                    slotclick.selected = True
                                                    self.uniteditborder.add(gameui.Selectedsquad(slotclick.inspposition, 5))
                                                    self.battleui.add(*self.uniteditborder)

                                            elif keystate[pygame.K_LALT] or keystate[pygame.K_RALT]:
                                                if slotclick.selected and len(self.uniteditborder) > 1:
                                                    slotclick.selected = False
                                                    for border in self.uniteditborder:
                                                        if border.pos == slotclick.inspposition:
                                                            border.kill()
                                                            del border
                                                            break

                                            else:  # select one sub-subunit by normal left click
                                                for border in self.uniteditborder:  # remove all other border
                                                    border.kill()
                                                    del border
                                                for newslot in self.unitbuildslot:
                                                    newslot.selected = False
                                                slotclick.selected = True
                                                self.uniteditborder.add(gameui.Selectedsquad(slotclick.inspposition, 5))
                                                self.battleui.add(*self.uniteditborder)

                                                if slotclick.name != "None":
                                                    self.battleui.remove(*self.leadernow)
                                                    self.leadernow = [leader for leader in self.previewleader]
                                                    self.battleui.add(*self.leadernow)  # add leader portrait to draw
                                                    self.showincard = slot
                                                    self.gameui[1].valueinput(who=self.showincard)
                                                    self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                              armourlist=self.allarmour)  # update subunit card on selected subunit
                                                    if self.gameui[2].option == 2:
                                                        self.traitskillblit()
                                                        self.effecticonblit()
                                                        self.countdownskillicon()

                                if mouse_up or mouse_right:
                                    if self.unitbuildslot in self.battleui and self.troop_listbox.rect.collidepoint(self.mousepos):
                                        self.uiclick = True
                                        for index, name in enumerate(self.troop_namegroup):
                                            if name.rect.collidepoint(self.mousepos):
                                                if self.current_list_show == "faction":
                                                    self.current_troop_row = 0

                                                    if mouse_up:
                                                        self.factionpick = index
                                                        self.filtertrooplist()
                                                        if index != 0:  # pick faction
                                                            self.leader_list = [item[1][0] for thisindex, item in
                                                                                enumerate(self.leader_stat.leader_list.items())
                                                                                if thisindex > 0 and (item[1][0] == "None" or
                                                                                                      (item[0] >= 10000 and item[1][8] in (
                                                                                                      0, index)) or
                                                                                                      item[0] in self.allfaction.faction_list[index][
                                                                                                          2])]

                                                        else:  # pick all faction
                                                            self.leader_list = self.leader_list = [item[0] for item in
                                                                                                   self.leader_stat.leader_list.values()][1:]

                                                        self.main.setuplist(gameprepare.Namelist, self.current_troop_row, self.troop_list,
                                                                            self.troop_namegroup,
                                                                            self.troop_listbox, self.battleui)  # setup troop name list
                                                        self.troop_scroll.changeimage(newrow=self.current_troop_row,
                                                                                      logsize=len(self.troop_list))  # change troop scroll image

                                                        self.main.maketeamcoa([index], uiclass=self.battleui, oneteam=True,
                                                                              team1setpos=(
                                                                                  self.troop_listbox.rect.midleft[0] - int(
                                                                                      (200 * self.widthadjust) / 2),
                                                                                  self.troop_listbox.rect.midleft[1]))  # change team coa

                                                        self.current_list_show = "troop"

                                                    elif mouse_right:
                                                        self.popout_lorebook(2, index)

                                                elif self.current_list_show == "troop":
                                                    if mouse_up:
                                                        for slot in self.unitbuildslot:
                                                            if slot.selected:
                                                                if keystate[pygame.K_LSHIFT]:  # change all sub-subunit in army
                                                                    for newslot in self.unitbuildslot:
                                                                        if newslot.armyid == slot.armyid:
                                                                            newslot.changetroop(self.troop_index_list[index + self.current_troop_row],
                                                                                                self.baseterrain,
                                                                                                self.baseterrain * len(
                                                                                                    self.battlemap_feature.featurelist)
                                                                                                + self.featureterrain, self.currentweather)

                                                                else:
                                                                    slot.changetroop(self.troop_index_list[index + self.current_troop_row],
                                                                                     self.baseterrain,
                                                                                     self.baseterrain * len(
                                                                                         self.battlemap_feature.featurelist) + self.featureterrain,
                                                                                     self.currentweather)

                                                                if slot.name != "None":  # update information of subunit that just got changed
                                                                    self.battleui.remove(*self.leadernow)
                                                                    self.leadernow = [leader for leader in self.previewleader]
                                                                    self.battleui.add(*self.leadernow)  # add leader portrait to draw
                                                                    self.showincard = slot
                                                                    self.previewauthority(self.leadernow, slot.armyid)
                                                                    self.gameui[2].valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                                              armourlist=self.allarmour)  # update subunit card on selected subunit
                                                                    if self.gameui[2].option == 2:
                                                                        self.traitskillblit()
                                                                        self.effecticonblit()
                                                                        self.countdownskillicon()
                                                                elif slot.name == "None" and slot.leader is not None:  # remove leader from none subunit if any
                                                                    slot.leader.change_leader(1, self.leader_stat)
                                                                    slot.leader.change_subunit(None)  # remove subunit link in leader
                                                                    slot.leader = None  # remove leader link in subunit
                                                                    self.previewauthority(self.leadernow, slot.armyid)
                                                        unitdict = self.convertslot_dict("test")
                                                        if unitdict is not None and unitdict['test'][-1] == "0":
                                                            self.warningmsg.warning([self.warningmsg.multifaction_warn])
                                                            self.battleui.add(self.warningmsg)

                                                    elif mouse_right:  # upen encyclopedia
                                                        self.popout_lorebook(3, self.troop_index_list[index + self.current_troop_row])
                                                break

                                    elif self.filterbox.rect.collidepoint(self.mousepos):
                                        self.uiclick = True
                                        if mouse_up:
                                            if self.teamchange_button.rect.collidepoint(self.mousepos):
                                                if self.teamchange_button.event == 0:
                                                    self.teamchange_button.event = 1

                                                elif self.teamchange_button.event == 1:
                                                    self.teamchange_button.event = 0

                                                for slot in self.unitbuildslot:
                                                    slot.team = self.teamchange_button.event + 1
                                                    slot.changeteam(True)
                                                    self.gameui[1].valueinput(who=slot)  # loop valueinput so it change team correctly

                                            elif self.slotdisplay_button.rect.collidepoint(self.mousepos):
                                                if self.slotdisplay_button.event == 0:  # hide
                                                    self.slotdisplay_button.event = 1
                                                    self.battleui.remove(self.unitsetup_stuff, self.leadernow)

                                                elif self.slotdisplay_button.event == 1:  # show
                                                    self.slotdisplay_button.event = 0
                                                    self.battleui.add(self.unitsetup_stuff, self.leadernow)

                                            elif self.deploy_button.rect.collidepoint(self.mousepos) and self.unitbuildslot in self.battleui:
                                                candeploy = True
                                                subunitcount = 0
                                                warninglist = []
                                                for slot in self.unitbuildslot:
                                                    if slot.troopid != 0:
                                                        subunitcount += 1
                                                if subunitcount < 8:
                                                    candeploy = False
                                                    warninglist.append(self.warningmsg.eightsubunit_warn)
                                                if self.leadernow == [] or self.previewleader[0].name == "None":
                                                    candeploy = False
                                                    warninglist.append(self.warningmsg.mainleader_warn)

                                                if candeploy:
                                                    unit_gameid = 0
                                                    if len(self.allunitindex) > 0:
                                                        unit_gameid = self.allunitindex[-1] + 1
                                                    currentpreset = self.convertslot_dict(self.unitpresetname, [str(int(self.basecamerapos[0])),
                                                                                                                str(int(self.basecamerapos[1]))],
                                                                                          unit_gameid)
                                                    subunit_gameid = 0
                                                    if len(self.subunit) > 0:
                                                        for subunit in self.subunit:
                                                            subunit_gameid = subunit.gameid
                                                        subunit_gameid = subunit_gameid + 1
                                                    for slot in self.unitbuildslot:  # just for grabing current selected team
                                                        currentpreset[self.unitpresetname] += (0, 100, 100, slot.team)
                                                        gamelongscript.convertedit_unit(self,
                                                                                        (self.team0unit, self.team1unit, self.team2unit)[slot.team],
                                                                                        currentpreset[self.unitpresetname],
                                                                                        self.teamcolour[slot.team],
                                                                                        pygame.transform.scale(
                                                                                            self.coa[int(currentpreset[self.unitpresetname][-1])],
                                                                                            (60, 60)), subunit_gameid)
                                                        break
                                                    self.slotdisplay_button.event = 1
                                                    self.setup_uniticon()
                                                    self.battleui.remove(self.unitsetup_stuff, self.leadernow)
                                                    for unit in self.allunitlist:
                                                        unit.startset(self.subunit)
                                                    for subunit in self.subunit:
                                                        subunit.gamestart(self.camerascale)
                                                    for leader in self.leader_updater:
                                                        leader.gamestart()

                                                    for unit in self.allunitlist:
                                                        unit.command(self.battle_mouse_pos[0], False, False, self.last_mouseover, None,
                                                                     othercommand=1)
                                                else:
                                                    self.warningmsg.warning(warninglist)
                                                    self.battleui.add(self.warningmsg)
                                            else:
                                                for box in self.tickbox_filter:
                                                    if box in self.battleui and box.rect.collidepoint(self.mousepos):
                                                        if box.tick is False:
                                                            box.changetick(True)
                                                        else:
                                                            box.changetick(False)
                                                        if box.option == "meleeinf":
                                                            self.filtertroop[0] = box.tick
                                                        elif box.option == "rangeinf":
                                                            self.filtertroop[1] = box.tick
                                                        elif box.option == "meleecav":
                                                            self.filtertroop[2] = box.tick
                                                        elif box.option == "rangecav":
                                                            self.filtertroop[3] = box.tick
                                                        if self.current_list_show == "troop":
                                                            self.current_troop_row = 0
                                                            self.filtertrooplist()
                                                            self.main.setuplist(gameprepare.Namelist, self.current_troop_row, self.troop_list,
                                                                                self.troop_namegroup,
                                                                                self.troop_listbox, self.battleui)  # setup troop name list
                                    elif self.terrain_change_button.rect.collidepoint(self.mousepos) and mouse_up:  # change map terrain button
                                        self.uiclick = True
                                        self.popuplist_newopen(self.terrain_change_button.rect.midtop, self.battlemap_base.terrainlist, "terrain")

                                    elif self.feature_change_button.rect.collidepoint(self.mousepos) and mouse_up:  # change map feature button
                                        self.uiclick = True
                                        self.popuplist_newopen(self.feature_change_button.rect.midtop, self.battlemap_feature.featurelist, "feature")

                                    elif self.weather_change_button.rect.collidepoint(self.mousepos) and mouse_up:  # change map weather button
                                        self.uiclick = True
                                        self.popuplist_newopen(self.weather_change_button.rect.midtop, self.weather_list, "weather")

                                    elif self.unit_delete_button.rect.collidepoint(self.mousepos) and mouse_up and \
                                            self.unit_delete_button in self.battleui:  # delete preset button
                                        self.uiclick = True
                                        if self.unitpresetname == "":
                                            pass
                                        else:
                                            self.textinputpopup = ("confirm_input", "delete_preset")
                                            self.confirmui.changeinstruction("Delete Selected Preset?")
                                            self.battleui.add(*self.confirmui_pop)

                                    elif self.unit_save_button.rect.collidepoint(self.mousepos) and mouse_up and \
                                            self.unit_save_button in self.battleui:  # save preset button
                                        self.uiclick = True
                                        self.textinputpopup = ("text_input", "save_unit")

                                        if self.unitpresetname == "":
                                            self.input_box.textstart("")
                                        else:
                                            self.input_box.textstart(self.unitpresetname)

                                        self.inputui.changeinstruction("Preset Name:")
                                        self.battleui.add(*self.inputui_pop)

                                    elif self.warningmsg in self.battleui and self.warningmsg.rect.collidepoint(self.mousepos):
                                        self.battleui.remove(self.warningmsg)

                                    elif self.teamcoa in self.battleui:
                                        for team in self.teamcoa:
                                            if team.rect.collidepoint(self.mousepos) and mouse_up:
                                                self.uiclick = True
                                                if self.current_list_show == "troop":
                                                    self.current_troop_row = 0
                                                    self.main.setuplist(gameprepare.Namelist, self.current_troop_row, self.faction_list,
                                                                        self.troop_namegroup,
                                                                        self.troop_listbox, self.battleui)
                                                    self.troop_scroll.changeimage(newrow=self.current_troop_row,
                                                                                  logsize=len(self.faction_list))  # change troop scroll image
                                                    self.current_list_show = "faction"

                    if self.last_selected is not None:
                        if self.gamestate == 1 and self.last_selected.state != 100:
                            if self.before_selected is None:  # add back the pop up ui so it get shown when click subunit with none selected before
                                self.gameui = self.popgameui
                                self.battleui.add(*self.gameui[0:2])  # add leader and top ui
                                self.battleui.add(self.inspectbutton)  # add inspection ui open/close button

                                self.addbehaviourui(self.last_selected)

                            elif self.before_selected != self.last_selected or self.splithappen:  # change subunit information when select other unit
                                if self.inspectui:  # change inspect ui
                                    self.newunitclick = True
                                    self.battleui.remove(*self.inspectsubunit)

                                    self.subunit_selected = None
                                    for index, subunit in enumerate(self.last_selected.subunit_sprite_array.flat):
                                        if subunit is not None:
                                            self.inspectsubunit[index].addsubunit(subunit)
                                            self.battleui.add(self.inspectsubunit[index])
                                            if self.subunit_selected is None:
                                                self.subunit_selected = self.inspectsubunit[index]

                                    self.subunitselectedborder.pop(self.subunit_selected.pos)
                                    self.battleui.add(self.subunitselectedborder)
                                    self.gameui[2].valueinput(who=self.subunit_selected.who, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                              splithappen=self.splithappen)
                                self.battleui.remove(*self.leadernow)

                                self.addbehaviourui(self.last_selected, elsecheck=True)

                                if self.splithappen:  # end split check
                                    self.splithappen = False

                            else:  # Update topbar and command ui value every 1.1 seconds
                                if self.ui_timer >= 1.1:
                                    self.gameui[0].valueinput(who=self.last_selected, splithappen=self.splithappen)
                                    self.gameui[1].valueinput(who=self.last_selected, splithappen=self.splithappen)

                        elif self.gamestate == 2 and self.unitbuildslot not in self.battleui:
                            if (mouse_right or mouse_rightdown) and self.uiclick is False:  # Unit placement
                                self.last_selected.placement(self.battle_mouse_pos[1], mouse_right, mouse_rightdown, double_mouse_right)

                            if keystate[pygame.K_DELETE]:
                                for unit in self.troopnumbersprite:
                                    if unit.who == self.last_selected:
                                        unit.delete()
                                        unit.kill()
                                        del unit
                                for subunit in self.last_selected.subunit_sprite:
                                    subunit.delete()
                                    self.allsubunitlist.remove(subunit)
                                    subunit.kill()
                                    del subunit
                                for leader in self.last_selected.leader:
                                    leader.delete()
                                    leader.kill()
                                    del leader
                                del [self.team0poslist, self.team1poslist, self.team2poslist][self.last_selected.team][self.last_selected.gameid]
                                self.last_selected.delete()
                                self.last_selected.kill()
                                self.allunitlist.remove(self.last_selected)
                                self.allunitindex.remove(self.last_selected.gameid)
                                self.setup_uniticon()
                                self.last_selected = None

                    # v Update value of the clicked subunit every 1.1 second
                    if self.gamestate == 1 and self.inspectui and ((self.ui_timer >= 1.1 and self.gameui[2].option != 0) or
                                                                   self.before_selected != self.last_selected):
                        self.gameui[2].valueinput(who=self.subunit_selected.who, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                  splithappen=self.splithappen)
                        if self.gameui[2].option == 2:  # skill and status effect card
                            self.countdownskillicon()
                            self.effecticonblit()
                            if self.before_selected != self.last_selected:  # change subunit, reset trait icon as well
                                self.traitskillblit()
                                self.countdownskillicon()
                        else:
                            for icon in self.skill_icon.sprites():
                                icon.kill()
                                del icon
                            for icon in self.effect_icon.sprites():
                                icon.kill()
                                del icon
                    # ^ End update value

                    # v Drama text function
                    if self.drama_timer == 0 and len(self.textdrama.queue) != 0:  # Start timer and add to allui If there is event queue
                        self.battleui.add(self.textdrama)
                        self.textdrama.processqueue()
                        self.drama_timer = 0.1
                    elif self.drama_timer > 0:
                        self.textdrama.playanimation()
                        self.drama_timer += self.uidt
                        if self.drama_timer > 3:
                            self.drama_timer = 0
                            self.battleui.remove(self.textdrama)
                    # ^ End drama

                    if self.dt > 0:
                        self.team_troopnumber = [1, 1, 1]  # reset troop count

                        # v Event log timer
                        if self.eventschedule is not None and self.eventlist != [] and self.timenumber.timenum >= self.eventschedule:
                            self.eventlog.addlog(None, None, eventmapid=self.eventmapid)
                            for event in self.eventlog.mapevent:
                                if self.eventlog.mapevent[event][3] is not None and self.eventlog.mapevent[event][3] > self.timenumber.timenum:
                                    self.eventmapid = event
                                    self.eventschedule = self.eventlog.mapevent[event][3]
                                    break
                            self.eventlist = self.eventlist[1:]
                        # ^ End event log timer

                        # v Weather system
                        if self.weatherschedule is not None and self.timenumber.timenum >= self.weatherschedule:
                            del self.currentweather
                            weather = self.weatherevent[0]

                            if weather[0] != 0:
                                self.currentweather = gameweather.Weather(self.timeui, weather[0], weather[2], self.allweather)
                            else:  # Random weather
                                self.currentweather = gameweather.Weather(self.timeui, random.randint(0, 11), random.randint(0, 2),
                                                                          self.allweather)
                            self.weatherevent.pop(0)
                            self.showmap.addeffect(self.battlemap_height,
                                                   self.weathereffectimgs[self.currentweather.weathertype][self.currentweather.level])

                            try:  # Get end time of next event which is now index 0
                                self.weatherschedule = self.weatherevent[0][1]
                            except Exception:
                                self.weatherschedule = None

                        if self.currentweather.spawnrate > 0 and len(self.weathermatter) < self.currentweather.speed:
                            spawnnum = range(0,
                                             int(self.currentweather.spawnrate * self.dt * random.randint(0,
                                                                                                          10)))  # number of sprite to spawn at this time
                            for spawn in spawnnum:  # spawn each weather sprite
                                truepos = (random.randint(10, SCREENRECT.width), 0)  # starting pos
                                target = (truepos[0], SCREENRECT.height)  # final base_target pos

                                if self.currentweather.spawnangle == 225:  # top right to bottom left movement
                                    startpos = random.randint(10, SCREENRECT.width * 2)  # starting x pos that can be higher than screen width
                                    truepos = (startpos, 0)
                                    if startpos >= SCREENRECT.width:  # x higher than screen width will spawn on the right corner of screen but not at top
                                        startpos = SCREENRECT.width  # revert x back to screen width
                                        truepos = (startpos, random.randint(0, SCREENRECT.height))

                                    if truepos[1] > 0:  # start position simulate from beyond top right of screen
                                        target = (truepos[1] * self.weatherscreenadjust, SCREENRECT.height)
                                    elif truepos[0] < SCREENRECT.width:  # start position inside screen width
                                        target = (0, truepos[0] / self.weatherscreenadjust)

                                elif self.currentweather.spawnangle == 270:  # right to left movement
                                    truepos = (SCREENRECT.width, random.randint(0, SCREENRECT.height))
                                    target = (0, truepos[1])

                                randompic = random.randint(0, len(self.weathermatterimgs[self.currentweather.weathertype]) - 1)
                                self.weathermatter.add(gameweather.Mattersprite(truepos, target,
                                                                                self.currentweather.speed,
                                                                                self.weathermatterimgs[self.currentweather.weathertype][
                                                                                    randompic]))

                        for unit in self.allunitlist:
                            unit.collide = False  # reset collide

                        if len(self.allsubunitlist) > 1:
                            tree = KDTree(
                                [sprite.base_pos for sprite in self.allsubunitlist])  # collision loop check, much faster than pygame collide check
                            collisions = tree.query_pairs(self.collidedistance)
                            for one, two in collisions:
                                spriteone = self.allsubunitlist[one]
                                spritetwo = self.allsubunitlist[two]
                                if spriteone.parentunit != spritetwo.parentunit:  # collide with subunit in other unit
                                    if spriteone.base_pos.distance_to(spriteone.base_pos) < self.fulldistance:
                                        spriteone.fullmerge.append(spritetwo)
                                        spritetwo.fullmerge.append(spriteone)

                                    if spriteone.front_pos.distance_to(spritetwo.base_pos) < self.frontdistance:  # first subunit collision
                                        if spriteone.team != spritetwo.team:  # enemy team
                                            spriteone.enemy_front.append(spritetwo)
                                            spriteone.parentunit.collide = True
                                        elif spriteone.state in (2, 4, 6, 10, 11, 13) or \
                                                spritetwo.state in (2, 4, 6, 10, 11, 13):  # cannot run pass other unit if either run or in combat
                                            spriteone.friend_front.append(spritetwo)
                                            spriteone.parentunit.collide = True
                                        spriteone.collide_penalty = True
                                    else:
                                        if spriteone.team != spritetwo.team:  # enemy team
                                            spriteone.enemy_side.append(spritetwo)
                                    if spritetwo.front_pos.distance_to(spriteone.base_pos) < self.frontdistance:  # second subunit
                                        if spriteone.team != spritetwo.team:  # enemy team
                                            spritetwo.enemy_front.append(spriteone)
                                            spritetwo.parentunit.collide = True
                                        elif spriteone.state in (2, 4, 6, 10, 11, 13) or \
                                                spritetwo.state in (2, 4, 6, 10, 11, 13):
                                            spritetwo.friend_front.append(spriteone)
                                            spritetwo.parentunit.collide = True
                                        spritetwo.collide_penalty = True
                                    else:
                                        if spriteone.team != spritetwo.team:  # enemy team
                                            spritetwo.enemy_side.append(spriteone)

                                else:  # collide with subunit in same unit
                                    if spriteone.front_pos.distance_to(spritetwo.base_pos) < self.frontdistance:  # first subunit collision
                                        if spriteone.base_pos.distance_to(spriteone.base_pos) < self.fulldistance:
                                            spriteone.fullmerge.append(spritetwo)
                                            spritetwo.fullmerge.append(spriteone)

                                        if spriteone.state in (2, 4, 6, 10, 11, 12, 13, 99) or \
                                                spritetwo.state in (2, 4, 6, 10, 11, 12, 13):
                                            spriteone.same_front.append(spritetwo)
                                    if spritetwo.front_pos.distance_to(spriteone.base_pos) < self.frontdistance:  # second subunit
                                        # if spriteone.frontline:
                                        if spriteone.state in (2, 4, 6, 10, 11, 12, 13, 99) or \
                                                spritetwo.state in (2, 4, 6, 10, 11, 12, 13):
                                            spritetwo.same_front.append(spriteone)

                        self.subunitposarray = self.mapmovearray.copy()
                        for subunit in self.allsubunitlist:
                            for y in subunit.posrange[0]:
                                for x in subunit.posrange[1]:
                                    self.subunitposarray[x][y] = 0

                    # v Updater
                    self.unit_updater.update(self.currentweather, self.subunit, self.dt, self.camerascale,
                                             self.battle_mouse_pos[0], mouse_up)
                    self.last_mouseover = None  # reset last parentunit mouse over

                    self.leader_updater.update()
                    self.subunit_updater.update(self.currentweather, self.dt, self.camerascale, self.combattimer,
                                                self.battle_mouse_pos[0], mouse_up)

                    # v Run pathfinding for melee combat no more than limit number of sub-unit per update to prevent stutter
                    if len(self.combatpathqueue) > 0:
                        run = 0
                        while len(self.combatpathqueue) > 0 and run < 5:
                            self.combatpathqueue[0].combat_pathfind()
                            self.combatpathqueue = self.combatpathqueue[1:]
                            run += 1
                    # ^ End melee pathfinding

                    # v Remove the subunit ui when click at empyty space
                    if mouse_up and self.clickany is False:  # not click at any parentunit
                        if self.last_selected is not None:  # any parentunit is selected
                            self.last_selected = None  # reset last_selected
                            self.before_selected = None  # reset before selected parentunit after remove last selected
                            self.removeunitui()
                    # ^ End remove

                    if self.ui_timer > 1:
                        self.scaleui.changefightscale(self.team_troopnumber)  # change fight colour scale on timeui bar
                        self.last_team_troopnumber = self.team_troopnumber

                    if self.combattimer >= 0.5:  # reset combat timer every 0.5 seconds
                        self.combattimer -= 0.5  # not reset to 0 because higher speed can cause inconsistency in update timing

                    self.effect_updater.update(self.subunit, self.dt, self.camerascale)
                    self.weather_updater.update(self.dt, self.timenumber.timenum)
                    self.minimap.update(self.camerascale, [self.camerapos, self.cameraupcorner], self.team1poslist, self.team2poslist)

                    self.uiupdater.update()  # update ui
                    self.camera.update(self.camerapos, self.battlecamera, self.camerascale)
                    # ^ End battle updater

                    # v Update game time
                    self.dt = self.clock.get_time() / 1000  # dt before gamespeed
                    if self.ui_timer >= 1.1:  # reset ui timer every 1.1 seconds
                        self.ui_timer -= 1.1
                    self.ui_timer += self.dt  # ui update by real time instead of game time to reduce workload
                    self.uidt = self.dt  # get ui timer before apply game

                    self.dt = self.dt * self.gamespeed  # apply dt with gamespeed for ingame calculation
                    if self.dt > 0.1:
                        self.dt = 0.1  # make it so stutter does not cause sprite to clip other sprite especially when zoom change

                    self.combattimer += self.dt  # update combat timer
                    self.timenumber.timerupdate(self.dt * 10)  # update ingame time with 5x speed

                    if self.mode == "battle" and (len(self.team1unit) <= 0 or len(self.team2unit) <= 0):
                        if self.battledone_box not in self.battleui:
                            if len(self.team1unit) <= 0 and len(self.team2unit) <= 0:
                                teamwin = 0  # draw
                            elif len(self.team2unit) <= 0:
                                teamwin = 1
                            else:
                                teamwin = 2
                            if teamwin != 0:
                                for index, coa in enumerate(self.teamcoa):
                                    if index == teamwin - 1:
                                        self.battledone_box.popout(coa.name)
                                        break
                            else:
                                self.battledone_box.popout("Draw")
                            self.gamedone_button.rect = self.gamedone_button.image.get_rect(midtop=self.gamedone_button.pos)
                            self.battleui.add(self.battledone_box, self.gamedone_button)
                        else:
                            if mouse_up and self.gamedone_button.rect.collidepoint(self.mousepos):
                                self.gamestate = 3  # end battle mode, result screen
                                self.gamespeed = 0
                                coalist = [None, None]
                                for index, coa in enumerate(self.teamcoa):
                                    coalist[index] = coa.image
                                self.battledone_box.showresult(coalist[0], coalist[1], [self.start_troopnumber, self.team_troopnumber,
                                                                                        self.wound_troopnumber, self.death_troopnumber,
                                                                                        self.flee_troopnumber, self.capture_troopnumber])
                                self.gamedone_button.rect = self.gamedone_button.image.get_rect(center=(self.battledone_box.rect.midbottom[0],
                                                                                                        self.battledone_box.rect.midbottom[1] / 1.3))

                        # print('end', self.team_troopnumber, self.last_team_troopnumber, self.start_troopnumber, self.wound_troopnumber,
                        #       self.death_troopnumber, self.flee_troopnumber, self.capture_troopnumber)
                    # ^ End update game time

                elif self.gamestate == 0:  # Complete game pause when open either esc menu or enclycopedia
                    if self.battle_menu.mode == 0:  # main esc menu
                        for button in self.battle_menu_button:
                            if button.rect.collidepoint(self.mousepos):
                                button.image = button.images[1]  # change button image to mouse over one
                                if mouse_up:  # click on button
                                    button.image = button.images[2]  # change button image to clicked one
                                    if button.text == "Resume":  # resume game
                                        self.gamestate = self.previous_gamestate  # resume battle gameplay state
                                        self.battleui.remove(self.battle_menu, *self.battle_menu_button, *self.escslidermenu,
                                                             *self.escvaluebox)  # remove menu sprite

                                    elif button.text == "Encyclopedia":  # open encyclopedia
                                        self.battle_menu.mode = 2  # change to enclycopedia mode
                                        self.battleui.add(self.lorebook, self.lorenamelist, self.lorescroll,
                                                          *self.lorebuttonui)  # add sprite related to encyclopedia
                                        self.lorebook.change_section(0, self.lorenamelist, self.subsection_name, self.lorescroll, self.pagebutton,
                                                                     self.battleui)
                                        # self.lorebook.setupsubsectionlist(self.lorenamelist, listgroup)

                                    elif button.text == "Option":  # open option menu
                                        self.battle_menu.changemode(1)  # change to option menu mode
                                        self.battleui.remove(*self.battle_menu_button)  # remove main esc menu button
                                        self.battleui.add(*self.escoptionmenubutton, *self.escslidermenu, *self.escvaluebox)
                                        self.oldsetting = self.escslidermenu[0].value  # Save previous setting for in case of cancel

                                    elif button.text == "End Battle":  # back to main menu
                                        self.exitbattle()
                                        return  # end battle game loop

                                    elif button.text == "Desktop":  # quit game
                                        self.textinputpopup = ("confirm_input", "quit")
                                        self.confirmui.changeinstruction("Quit Game?")
                                        self.battleui.add(*self.confirmui_pop)
                                    break  # found clicked button, break loop
                            else:
                                button.image = button.images[0]

                    elif self.battle_menu.mode == 1:  # option menu
                        for button in self.escoptionmenubutton:  # check if any button get collided with mouse or clicked
                            if button.rect.collidepoint(self.mousepos):
                                button.image = button.images[1]  # change button image to mouse over one
                                if mouse_up:  # click on button
                                    button.image = button.images[2]  # change button image to clicked one
                                    if button.text == "Confirm":  # confirm button, save the setting and close option menu
                                        self.oldsetting = self.mixervolume  # save mixer volume
                                        pygame.mixer.music.set_volume(self.mixervolume)  # set new music player volume
                                        main.editconfig("DEFAULT", "SoundVolume", str(slider.value), "configuration.ini",
                                                        config)  # save to config file
                                        self.battle_menu.changemode(0)  # go back to main esc menu
                                        self.battleui.remove(*self.escoptionmenubutton, *self.escslidermenu,
                                                             *self.escvaluebox)  # remove option menu sprite
                                        self.battleui.add(*self.battle_menu_button)  # add main esc menu buttons back

                                    elif button.text == "Apply":  # apply button, save the setting
                                        self.oldsetting = self.mixervolume  # save mixer volume
                                        pygame.mixer.music.set_volume(self.mixervolume)  # set new music player volume
                                        main.editconfig("DEFAULT", "SoundVolume", str(slider.value), "configuration.ini",
                                                        config)  # save to config file

                                    elif button.text == "Cancel":  # cancel button, revert the setting to the last saved one
                                        self.mixervolume = self.oldsetting  # revert to old setting
                                        pygame.mixer.music.set_volume(self.mixervolume)  # set new music player volume
                                        self.escslidermenu[0].update(self.mixervolume, self.escvaluebox[0], forcedvalue=True)  # update slider bar
                                        self.battle_menu.changemode(0)  # go back to main esc menu
                                        self.battleui.remove(*self.escoptionmenubutton, *self.escslidermenu,
                                                             *self.escvaluebox)  # remove option menu sprite
                                        self.battleui.add(*self.battle_menu_button)  # add main esc menu buttons back

                            else:  # no button currently collided with mouse
                                button.image = button.images[0]  # revert button image back to the idle one

                        for slider in self.escslidermenu:
                            if slider.rect.collidepoint(self.mousepos) and (mouse_leftdown or mouse_up):  # mouse click on slider bar
                                slider.update(self.mousepos, self.escvaluebox[0])  # update slider button based on mouse value
                                self.mixervolume = float(slider.value / 100)  # for now only music volume slider exist

                    elif self.battle_menu.mode == 2:  # Encyclopedia mode
                        if mouse_up or mouse_leftdown:  # mouse down (hold click) only for subsection listscroller
                            if mouse_up:
                                for button in self.lorebuttonui:
                                    if button in self.battleui and button.rect.collidepoint(self.mousepos):  # click button
                                        if button.event in range(0, 11):  # section button
                                            self.lorebook.change_section(button.event, self.lorenamelist, self.subsection_name, self.lorescroll,
                                                                         self.pagebutton, self.battleui)  # change to section of that button
                                        elif button.event == 19:  # Close button
                                            self.battleui.remove(self.lorebook, *self.lorebuttonui, self.lorescroll,
                                                                 self.lorenamelist)  # remove enclycopedia related sprites
                                            for name in self.subsection_name:  # remove subsection name
                                                name.kill()
                                                del name
                                            self.battle_menu.changemode(0)  # change menu back to default 0
                                            if self.battle_menu not in self.battleui:  # in case open encyclopedia via right click on icon or other way
                                                self.gamestate = self.previous_gamestate  # resume gameplay
                                        elif button.event == 20:  # Previous page button
                                            self.lorebook.change_page(self.lorebook.page - 1, self.pagebutton, self.battleui)  # go back 1 page
                                        elif button.event == 21:  # Next page button
                                            self.lorebook.change_page(self.lorebook.page + 1, self.pagebutton, self.battleui)  # go forward 1 page
                                        break  # found clicked button, break loop

                                for name in self.subsection_name:  # too lazy to include break for button found to avoid subsection loop since not much optimisation is needed here
                                    if name.rect.collidepoint(self.mousepos):  # click on subsection name
                                        self.lorebook.change_subsection(name.subsection, self.pagebutton, self.battleui)  # change subsection
                                        break  # found clicked subsection, break loop

                            if self.lorescroll.rect.collidepoint(self.mousepos):  # click on subsection list scroller
                                self.lorebook.current_subsection_row = self.lorescroll.update(
                                    self.mousepos)  # update the scroller and get new current subsection
                                self.lorebook.setup_subsection_list(self.lorenamelist, self.subsection_name)  # update subsection name list

                elif self.gamestate == 3:
                    if mouse_up and self.gamedone_button.rect.collidepoint(self.mousepos):
                        self.exitbattle()
                        return  # end battle game loop

            elif self.textinputpopup != (None, None):  # currently have input text pop up on screen, stop everything else until done
                for button in self.input_button:
                    button.update(self.mousepos, mouse_up, mouse_leftdown)

                if self.input_ok_button.event:
                    self.input_ok_button.event = False

                    if self.textinputpopup[1] == "save_unit":
                        currentpreset = self.convertslot_dict(self.input_box.text)
                        if currentpreset is not None:
                            self.customunitpresetlist.update(currentpreset)

                            self.unitpresetname = self.input_box.text
                            self.main.setuplist(gameprepare.Namelist, self.current_unit_row, list(self.customunitpresetlist.keys()),
                                                self.unitpreset_namegroup, self.unit_listbox, self.battleui)  # setup preset unit list
                            for name in self.unitpreset_namegroup:  # loop to change selected border position to the last in preset list
                                if name.name == self.unitpresetname:
                                    self.presetselectborder.changepos(name.rect.topleft)
                                    break

                            self.save_preset()
                        else:
                            self.warningmsg.warning([self.warningmsg.eightsubunit_warn])
                            self.battleui.add(self.warningmsg)

                    elif self.textinputpopup[1] == "delete_preset":
                        del self.customunitpresetlist[self.unitpresetname]
                        self.unitpresetname = ""
                        self.main.setuplist(gameprepare.Namelist, self.current_unit_row, list(self.customunitpresetlist.keys()),
                                            self.unitpreset_namegroup, self.unit_listbox, self.battleui)  # setup preset unit list
                        for name in self.unitpreset_namegroup:  # loop to change selected border position to the first in preset list
                            self.presetselectborder.changepos(name.rect.topleft)
                            break

                        self.save_preset()

                    elif self.textinputpopup[1] == "quit":
                        self.battleui.clear(self.screen, self.background)
                        self.battlecamera.clear(self.screen, self.background)
                        pygame.quit()
                        sys.exit()

                    self.input_box.textstart("")
                    self.textinputpopup = (None, None)
                    self.battleui.remove(*self.inputui_pop, *self.confirmui_pop)

                elif self.input_cancel_button.event or esc_press:
                    self.input_cancel_button.event = False
                    self.input_box.textstart("")
                    self.textinputpopup = (None, None)
                    self.battleui.remove(*self.inputui_pop, *self.confirmui_pop)

            self.screen.blit(self.camera.image, (0, 0))  # Draw the game camera and everything that appear in it
            self.battleui.draw(self.screen)  # Draw the UI
            pygame.display.update()  # update game display, draw everything
            self.clock.tick(60)  # clock update even if game pause

        if pygame.mixer:  # close music player
            pygame.mixer.music.fadeout(1000)

        pygame.time.wait(1000)  # wait a bit before closing
        pygame.quit()
