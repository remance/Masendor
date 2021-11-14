import csv
import datetime
import glob
import os
import random
import sys

import pygame
import pygame.freetype
from gamescript import camera, map, weather, battleui, commonscript, menu, escmenu
from gamescript.arcade import subunit, unit, leader, longscript
from pygame.locals import *
from scipy.spatial import KDTree

load_image = commonscript.load_image
load_images = commonscript.load_images
csv_read = commonscript.csv_read
load_sound = commonscript.load_sound
editconfig = commonscript.edit_config


class Battle:
    traitskillblit = commonscript.trait_skill_blit
    effecticonblit = commonscript.effect_icon_blit
    countdownskillicon = commonscript.countdown_skill_icon
    kill_effect_icon = commonscript.kill_effect_icon
    popout_lorebook = commonscript.popout_lorebook
    popuplist_newopen = commonscript.popuplist_newopen
    setuplist = commonscript.setuplist
    camerascale = 4
    escmenu_process = escmenu.escmenu_process

    def __init__(self, main, winstyle):
        # v Get game object/variable from gamestart
        self.mode = None  # battle map mode can be "uniteditor" for unit editor or "battle" for game battle
        self.main = main
        self.genre = main.genre
        self.config = main.config
        self.SoundVolume = main.Soundvolume
        self.SCREENRECT = main.SCREENRECT
        self.teamcolour = main.teamcolour
        self.main_dir = main.main_dir
        self.width_adjust = main.width_adjust
        self.height_adjust = main.height_adjust
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
        self.directionarrows = main.direction_arrows

        self.gameui = main.gameui
        self.popgameui = main.gameui  # saving list of gameui that will pop out when parentunit is selected

        self.battlemap_base = main.battlemap_base
        self.battlemap_feature = main.battlemap_feature
        self.battlemap_height = main.battlemap_height
        self.showmap = main.showmap

        self.minimap = main.minimap
        self.eventlog = main.eventlog
        self.logscroll = main.logscroll
        self.buttonui = main.buttonui

        self.fpscount = main.fpscount

        self.terraincheck = main.terraincheck
        self.button_name_popup = main.button_name_popup
        self.leaderpopup = main.leader_popup
        self.effectpopup = main.effect_popup
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
        self.unit_build_slot = main.unit_build_slot
        self.uniteditborder = main.unit_edit_border
        self.previewleader = main.preview_leader
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

        self.timeui = main.timeui
        self.timenumber = main.timenumber

        self.scaleui = main.scaleui

        self.weathermatter = main.weathermatter
        self.weathereffect = main.weathereffect

        self.lorebook = main.lorebook
        self.lorenamelist = main.lorenamelist
        self.lorebuttonui = main.lorebuttonui
        self.lorescroll = main.lorescroll
        self.subsection_name = main.subsection_name
        self.pagebutton = main.pagebutton

        self.allweather = main.allweather
        self.weather_matter_imgs = main.weather_matter_imgs
        self.weather_effect_imgs = main.weather_effect_imgs

        self.featuremod = main.featuremod

        self.allfaction = main.allfaction
        self.coa = main.coa

        self.allweapon = main.allweapon
        self.allarmour = main.allarmour

        self.status_imgs = main.status_imgs
        self.role_imgs = main.role_imgs
        self.trait_imgs = main.trait_imgs
        self.skill_imgs = main.skill_imgs

        self.troop_data = main.troop_data
        self.leader_stat = main.leader_stat

        self.statetext = main.statetext

        self.sprite_width = main.sprite_width
        self.sprite_height = main.sprite_height
        self.collide_distance = self.sprite_height / 10  # distance to check collision
        self.front_distance = self.sprite_height / 20  # distance from front side
        self.full_distance = self.front_distance / 2  # distance for sprite merge check

        self.combatpathqueue = []  # queue of sub-unit to run melee combat pathfiding

        self.escslidermenu = main.escslidermenu
        self.escvaluebox = main.escvaluebox

        self.troopcard_ui = main.troopcard_ui
        self.troopcard_button = main.troopcard_button
        self.unitstat_ui = main.unitstat_ui

        self.battledone_box = main.battledone_box
        self.gamedone_button = main.gamedone_button
        # ^ End load from gamestart

        self.gamespeed = 0
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

        self.unitsetup_stuff = (self.unit_build_slot, self.uniteditborder, self.troopcard_ui,
                                self.teamcoa, self.troopcard_button, self.troop_listbox, self.troop_scroll,
                                self.troop_namegroup, self.unit_listbox, self.presetselectborder,
                                self.unitpreset_namegroup, self.unit_save_button, self.unit_delete_button,
                                self.unit_presetname_scroll)
        self.filter_stuff = (self.filterbox, self.slotdisplay_button, self.teamchange_button, self.deploy_button, self.terrain_change_button,
                             self.feature_change_button, self.weather_change_button, self.tickbox_filter)

        self.bestdepth = pygame.display.mode_ok(self.SCREENRECT.size, winstyle, 32)  # Set the display mode
        self.screen = pygame.display.set_mode(self.SCREENRECT.size, winstyle | pygame.RESIZABLE, self.bestdepth)  # set up game screen

        # v Assign default variable to some class
        unit.Unit.gamebattle = self
        unit.Unit.imgsize = (self.sprite_width, self.sprite_height)
        subunit.Subunit.gamebattle = self
        leader.Leader.gamebattle = self
        # ^ End assign default

        self.background = pygame.Surface(self.SCREENRECT.size)  # Create background image
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

    def preparenewgame(self, ruleset, ruleset_folder, teamselected, enactment, mapselected, source, unitscale, mode):

        self.ruleset = ruleset  # current ruleset used
        self.ruleset_folder = ruleset_folder  # the folder of rulseset used
        self.mapselected = mapselected  # map folder name
        self.source = str(source)
        self.unitscale = unitscale
        self.playerteam = teamselected  # player selected team
        self.enactment = enactment

        # v load the sound effects
        # boom_sound = load_sound("boom.wav")
        # shoot_sound = load_sound("car_door.wav")
        # ^ End load sound effect

        # v Load weather schedule
        try:
            self.weather_event = csv_read(self.main_dir, "weather.csv",
                                          ["data", "ruleset", self.ruleset_folder, "map", self.mapselected, self.source], 1)
            self.weather_event = self.weather_event[1:]
            commonscript.convert_str_time(self.weather_event)
        except Exception:  # If no weather found use default light sunny weather start at 9.00
            newtime = datetime.datetime.strptime("09:00:00", "%H:%M:%S").time()
            newtime = datetime.timedelta(hours=newtime.hour, minutes=newtime.minute, seconds=newtime.second)
            self.weather_event = [[4, newtime, 0]]  # default weather light sunny all day
        self.weather_current = self.weather_event[0][1]  # weather_current here is used as the reference for map starting time
        # ^ End weather schedule

        # v Random music played from list
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer = None
        if pygame.mixer:
            self.SONG_END = pygame.USEREVENT + 1
            self.musiclist = glob.glob(os.path.join(self.main_dir, "data", "sound", "music", "*.ogg"))
            try:
                self.music_event = csv_read(self.main_dir, "musicevent.csv",
                                            ["data", "ruleset", self.ruleset_folder, "map", self.mapselected], 1)
                self.music_event = self.music_event[1:]
                if len(self.music_event) > 0:
                    commonscript.convert_str_time(self.music_event)
                    self.music_schedule = list(dict.fromkeys([item[1] for item in self.music_event]))
                    newlist = []
                    for time in self.music_schedule:
                        neweventlist = []
                        for event in self.music_event:
                            if time == event[1]:
                                neweventlist.append(event[0])
                        newlist.append(neweventlist)
                    self.music_event = newlist
                else:
                    self.music_schedule = [self.weather_current]
                    self.music_event = [[5]]
            except:  # any reading error will play random custom music instead
                self.music_schedule = [self.weather_current]
                self.music_event = [[5]]  # TODO change later when has custom playlist
        # ^ End music play

        try:  # get new map event for event log
            mapevent = csv_read("eventlog.csv",
                                [self.main_dir, "data", "ruleset", self.ruleset_folder, "map", self.mapselected, self.source], 0)
            battleui.EventLog.mapevent = mapevent
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

        self.timenumber.startsetup(self.weather_current)

        # v Create the battle map
        self.camerapos = pygame.Vector2(500, 500)  # Camera pos at the current zoom, start at center of map
        self.basecamerapos = pygame.Vector2(500, 500)  # Camera pos at furthest zoom for recalculate sprite pos after zoom
        camera.Camera.SCREENRECT = self.SCREENRECT
        self.camera = camera.Camera(self.camerapos, self.camerascale)

        if mapselected is not None:
            imgs = load_images(self.main_dir, ["ruleset", self.ruleset_folder, "map", self.mapselected], loadorder=False)
            self.battlemap_base.drawimage(imgs[0])
            self.battlemap_feature.drawimage(imgs[1])
            self.battlemap_height.drawimage(imgs[2])

            try:  # placename map layer is optional, if not existed in folder then assign None
                placenamemap = imgs[3]
            except Exception:
                placenamemap = None
            self.showmap.drawimage(self.battlemap_base, self.battlemap_feature, self.battlemap_height, placenamemap, self, False)
            self.showmap.changescale(self.camerascale)
        else:  # for unit editor mode, create empty temperate glass map
            self.editor_map_change((166, 255, 107), (181, 230, 29))
        # ^ End create battle map

        self.clock = pygame.time.Clock()  # Game clock to keep track of realtime pass

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
            longscript.unitsetup(self)
        # ^ End start subunit sprite

    def save_preset(self):
        with open(os.path.join("profile", "unitpreset", str(self.ruleset), "custom_unitpreset.csv"), "w", encoding='utf-8', newline='') as csvfile:
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
        for slot in self.unit_build_slot:  # add subunit troop id
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
                    for slotindex, slot in enumerate(self.unit_build_slot):  # add subunit troop id
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
        bigunitsize = len([slot for slot in self.unit_build_slot if slot.armyid == armyid and slot.name != "None"])
        if bigunitsize > 20:  # army size larger than 20 will reduce gamestart leader authority
            authority = int(leaderlist[0].authority +
                            (leaderlist[0].authority / 2 * (100 - bigunitsize) / 100) +
                            leaderlist[1].authority / 2 + leaderlist[2].authority / 2 +
                            leaderlist[3].authority / 4)

        for slot in self.unit_build_slot:
            if slot.armyid == armyid:
                slot.authority = authority

        # ^ End cal authority

    def ui_mouseover(self):
        """mouse over ui that is not subunit card and unitbox (topbar and commandbar)"""
        for this_ui in self.gameui:
            if this_ui in self.battleui and this_ui.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True
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
                checkvalue = self.troopcard_ui.value2[icon.icontype]
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
            if self.row_split_button in self.battleui:
                self.row_split_button.kill()
            if self.col_split_button in self.battleui:
                self.col_split_button.kill()
            self.battleui.remove(self.buttonui[7])  # remove decimation button
            self.battleui.remove(*self.switch_button[0:7])  # remove parentunit behaviour change button

        self.leadernow = whoinput.leader
        self.battleui.add(*self.leadernow)  # add leader portrait to draw
        # self.gameui[0].valueinput(who=whoinput)

    def unitcardbutton_click(self, who):
        for button in self.troopcard_button:  # Change subunit card option based on button clicking
            if button.rect.collidepoint(self.mousepos):
                self.clickany = True
                self.uiclick = True
                if self.troopcard_ui.option != button.event:
                    self.troopcard_ui.option = button.event
                    self.troopcard_ui.valueinput(who=who, weaponlist=self.allweapon,
                                                 armourlist=self.allarmour,
                                                 changeoption=1, splithappen=self.splithappen)

                    if self.troopcard_ui.option == 2:
                        self.traitskillblit()
                        self.effecticonblit()
                        self.countdownskillicon()
                    else:
                        self.kill_effect_icon()
                break

    def filtertrooplist(self):
        """Filter troop list based on faction picked and type filter"""
        if self.factionpick != 0:
            self.troop_list = [item[1][0] for item in self.troop_data.troop_list.items()
                               if item[1][0] == "None" or
                               item[0] in self.allfaction.faction_list[self.factionpick][1]]
            self.troop_index_list = [0] + self.allfaction.faction_list[self.factionpick][1]

        else:  # pick all faction
            self.troop_list = [item[0] for item in self.troop_data.troop_list.values()][1:]
            self.troop_index_list = list(range(0, len(self.troop_list)))

        for unit in self.troop_index_list[::-1]:
            if unit != 0:
                if self.filtertroop[0] is False:  # filter out melee infantry
                    if self.troop_data.troop_list[unit][8] > self.troop_data.troop_list[unit][12] and \
                            self.troop_data.troop_list[unit][29] == [1, 0, 1]:
                        self.troop_list.pop(self.troop_index_list.index(unit))
                        self.troop_index_list.remove(unit)

                if self.filtertroop[1] is False:  # filter out range infantry
                    if self.troop_data.troop_list[unit][22] != [1, 0] and \
                            self.troop_data.troop_list[unit][8] < self.troop_data.troop_list[unit][12] and \
                            self.troop_data.troop_list[unit][29] == [1, 0, 1]:
                        self.troop_list.pop(self.troop_index_list.index(unit))
                        self.troop_index_list.remove(unit)

                if self.filtertroop[2] is False:  # filter out melee cav
                    if self.troop_data.troop_list[unit][8] > self.troop_data.troop_list[unit][12] and \
                            self.troop_data.troop_list[unit][29] != [1, 0, 1]:
                        self.troop_list.pop(self.troop_index_list.index(unit))
                        self.troop_index_list.remove(unit)

                if self.filtertroop[3] is False:  # filter out range cav
                    if self.troop_data.troop_list[unit][22] != [1, 0] and \
                            self.troop_data.troop_list[unit][8] < self.troop_data.troop_list[unit][12] and \
                            self.troop_data.troop_list[unit][29] != [1, 0, 1]:
                        self.troop_list.pop(self.troop_index_list.index(unit))
                        self.troop_index_list.remove(unit)

    def changestate(self):
        self.previous_gamestate = self.gamestate
        if self.gamestate == 1:  # change to battle state
            self.minimap.drawimage(self.showmap.trueimage, self.camera)

            if self.last_selected is not None:  # any parentunit is selected
                self.last_selected = None  # reset last_selected
                self.before_selected = None  # reset before selected parentunit after remove last selected

            self.troopcard_ui.rect = self.troopcard_ui.image.get_rect(
                center=(self.troopcard_ui.x, self.troopcard_ui.y))  # change subunit card position back
            self.buttonui[0].rect = self.buttonui[0].image.get_rect(center=(self.troopcard_ui.x - 152, self.troopcard_ui.y + 10))
            self.buttonui[1].rect = self.buttonui[1].image.get_rect(center=(self.troopcard_ui.x - 152, self.troopcard_ui.y - 70))
            self.buttonui[2].rect = self.buttonui[2].image.get_rect(center=(self.troopcard_ui.x - 152, self.troopcard_ui.y - 30))
            self.buttonui[3].rect = self.buttonui[3].image.get_rect(center=(self.troopcard_ui.x - 152, self.troopcard_ui.y + 50))

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
            self.minimap.drawimage(self.showmap.trueimage, self.camera)  # reset minimap
            for arrow in self.arrows:  # remove all range attack
                arrow.kill()
                del arrow

            for unit in self.allunitlist:  # reset all unit state
                unit.command(self.battle_mouse_pos[0], False, False, self.last_mouseover, None, othercommand=2)
            self.troopcard_ui.rect = self.troopcard_ui.image.get_rect(bottomright=(self.SCREENRECT.width,
                                                                                   self.SCREENRECT.height))  # troop info card ui
            self.buttonui[0].rect = self.buttonui[0].image.get_rect(topleft=(self.troopcard_ui.rect.topleft[0],  # description button
                                                                             self.troopcard_ui.rect.topleft[1] + 120))
            self.buttonui[1].rect = self.buttonui[1].image.get_rect(topleft=(self.troopcard_ui.rect.topleft[0],  # stat button
                                                                             self.troopcard_ui.rect.topleft[1]))
            self.buttonui[2].rect = self.buttonui[2].image.get_rect(topleft=(self.troopcard_ui.rect.topleft[0],  # skill button
                                                                             self.troopcard_ui.rect.topleft[1] + 40))
            self.buttonui[3].rect = self.buttonui[3].image.get_rect(topleft=(self.troopcard_ui.rect.topleft[0],  # equipment button
                                                                             self.troopcard_ui.rect.topleft[1] + 80))

            self.battleui.remove(self.eventlog, self.logscroll)  # self.gameui[0]

            self.leadernow = [leader for leader in self.previewleader]  # reset leader in command ui

            self.battleui.add(self.filter_stuff, self.unitsetup_stuff, self.test_button, self.gameui[1:3], self.leadernow, self.buttonui[14:17])
            self.slotdisplay_button.event = 0  # reset display editor ui button to show
            self.gamespeed = 0  # pause battle

    def exitbattle(self):
        self.battleui.clear(self.screen, self.background)  # remove all sprite
        self.battlecamera.clear(self.screen, self.background)  # remove all sprite

        self.battleui.remove(self.battle_menu, *self.battle_menu_button, *self.escslidermenu,
                             *self.escvaluebox, self.battledone_box, self.gamedone_button)  # remove menu

        for group in (self.subunit, self.armyleader, self.team0unit, self.team1unit, self.team2unit):  # remove all reference from battle object
            for stuff in group:
                stuff.delete()
                stuff.kill()

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
                                 self.slotdisplay_button, self.test_button, self.deploy_button, self.troopcard_button,
                                 self.terrain_change_button, self.feature_change_button, self.weather_change_button,
                                 self.unit_build_slot, self.leadernow, self.presetselectborder,
                                 self.popup_listbox, self.popup_listscroll, *self.popup_namegroup)

            for group in self.troop_namegroup, self.uniteditborder, self.unitpreset_namegroup:
                for item in group:  # remove name list
                    item.kill()
                    del item

            for slot in self.unit_build_slot:  # reset all sub-subunit slot
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
            self.troop_list = [item[0] for item in self.troop_data.troop_list.values()][
                              1:]  # reset troop filter back to all faction
            self.troop_index_list = list(range(0, len(self.troop_list) + 1))

            self.leader_list = [item[0] for item in self.leader_stat.leader_list.values()][
                               1:]  # generate leader name list)

            self.leadernow = []

    def rungame(self):
        # v Create Starting Values
        self.mixervolume = self.SoundVolume
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

            self.full_troop_list = [item[0] for item in self.troop_data.troop_list.values()][1:]

            self.troop_list = self.full_troop_list  # generate troop name list
            self.troop_index_list = list(range(0, len(self.troop_list) + 1))

            self.leader_list = [item[0] for item in self.leader_stat.leader_list.values()][1:]  # generate leader name list

            self.setuplist(menu.NameList, self.current_unit_row, list(self.customunitpresetlist.keys()),
                           self.unitpreset_namegroup, self.unit_listbox, self.battleui)  # setup preset army list
            self.setuplist(menu.NameList, self.current_troop_row, self.troop_list,
                           self.troop_namegroup, self.troop_listbox, self.battleui)  # setup troop name list

            self.current_list_show = "troop"
            self.unitpresetname = ""
            self.preparestate = True
            self.baseterrain = 0
            self.featureterrain = 0
            self.weathertype = 4
            self.weatherstrength = 0
            self.currentweather = weather.Weather(self.timeui, self.weathertype, self.weatherstrength, self.allweather)
            self.showincard = None  # current sub-subunit showing in subunit card

            self.main.maketeamcoa([0], uiclass=self.battleui, oneteam=True,
                                  team1setpos=(self.troop_listbox.rect.midleft[0] - int((200 * self.width_adjust) / 2),
                                               self.troop_listbox.rect.midleft[1]))  # default faction select as all faction

            self.troop_scroll.changeimage(newrow=self.current_troop_row, logsize=len(self.troop_list))  # change troop scroll image

            for index, slot in enumerate(self.unit_build_slot):  # start with the first player subunit slot selected when enter
                if index == 0:
                    slot.selected = True
                    for border in self.uniteditborder:
                        border.kill()
                        del border
                    self.uniteditborder.add(battleui.SelectedSquad(slot.inspposition))
                    self.battleui.add(*self.uniteditborder)
                else:  # reset all other slot
                    slot.selected = False

            self.weather_current = None  # remove weather schedule from editor test

            self.changestate()

            for name in self.unitpreset_namegroup:  # loop to change selected border position to the first in preset list
                self.presetselectborder.changepos(name.rect.topleft)
                break

        else:  # normal battle
            self.changestate()

        self.mousetimer = 0  # This is timer for checking double mouse click, use realtime
        self.ui_timer = 0  # This is timer for ui update function, use realtime
        self.drama_timer = 0  # This is timer for combat related function, use game time (realtime * gamespeed)
        self.dt = 0  # Realtime used for in game calculation
        self.uidt = 0  # Realtime used for ui timer
        self.combattimer = 0  # This is timer for combat related function, use game time (realtime * gamespeed)
        self.uiclick = False  # for checking if mouse click is on ui
        self.clickany = False  # For checking if mouse click on anything, if not close ui related to parentunit
        self.last_selected = None  # Which unit is last selected
        self.mapviewmode = 0  # default, another one show height map
        self.splithappen = False  # Check if parentunit get split in that loop
        self.showtroopnumber = True  # for toggle troop number on/off
        self.weatherscreenadjust = self.SCREENRECT.width / self.SCREENRECT.height  # for weather sprite spawn position
        self.rightcorner = self.SCREENRECT.width - 5
        self.bottomcorner = self.SCREENRECT.height - 5
        self.centerscreen = [self.SCREENRECT.width / 2, self.SCREENRECT.height / 2]  # center position of the screen
        self.battle_mouse_pos = [[0, 0],
                                 [0, 0]]  # mouse position list in game not screen, the first without zoom and the second with camera zoom adjust
        # ^ End start value

        self.effect_updater.update(self.allunitlist, self.dt, self.camerascale)

        # self.mapdefarray = []
        # self.mapunitarray = [[x[random.randint(0, 1)] if i != j else 0 for i in range(1000)] for j in range(1000)]
        pygame.mixer.music.set_endevent(self.SONG_END)  # End current music before battle start

        while True:  # game running
            self.fpscount.fps_show(self.clock)
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
                    pygame.mixer.music.unload()
                    self.pickmusic = random.randint(0, len(self.music_current) - 1)
                    pygame.mixer.music.load(self.musiclist[self.music_current[self.pickmusic]])
                    pygame.mixer.music.play(fade_ms=100)

                elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:  # open/close menu
                    esc_press = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # left click
                        mouse_up = True
                    elif event.button == 3:  # Right Click
                        mouse_right = True
                        # if self.mousetimer == 0:
                        #     self.mousetimer = 0.001  # Start timer after first mouse click
                        # elif self.mousetimer < 0.3:  # if click again within 0.3 second for it to be considered double click
                        #     double_mouse_right = True  # double right click
                        #     self.mousetimer = 0
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
                        self.battleui.add(self.battle_menu, *self.battle_menu_button)  # add menu and its buttons to drawer

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

                    # ^ End mouse scroll input

                    # keyboard input
                    if keypress == pygame.K_TAB:
                        if self.mapviewmode == 0:  # Currently in normal map mode
                            self.mapviewmode = 1
                            self.showmap.changemode(self.mapviewmode)
                        else:  # Currently in height mode
                            self.mapviewmode = 0
                            self.showmap.changemode(self.mapviewmode)

                    elif keypress == pygame.K_p:  # Speed Pause/unpause Button
                        if self.gamespeed > 0:  #
                            self.gamespeed = 0  # pause game speed
                        else:  # speed currently pause
                            self.gamespeed = 1  # unpause game and set to speed 1

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

                    elif keypress == pygame.K_LALT:  # draw terrain popup ui when right click at map with no selected parentunit
                        if self.terraincheck in self.battleui:
                            if 0 <= self.battle_mouse_pos[1][0] <= 999 and \
                                    0 <= self.battle_mouse_pos[1][1] <= 999:  # not draw if pos is off the map
                                terrainpop, featurepop = self.battlemap_feature.getfeature(self.battle_mouse_pos[1], self.battlemap_base)
                                featurepop = self.battlemap_feature.featuremod[featurepop]
                                heightpop = self.battlemap_height.getheight(self.battle_mouse_pos[1])
                                self.terraincheck.pop(self.mousepos, featurepop, heightpop)
                                self.battleui.add(self.terraincheck)
                        else:
                            self.battleui.remove(self.terraincheck)

                    # vv FOR DEVELOPMENT DELETE LATER
                    # elif keypress == pygame.K_1:
                    #     self.textdrama.queue.append("Hello and Welcome to update video")
                    # elif keypress == pygame.K_2:
                    #     self.textdrama.queue.append("Showcase: Just simple clarity update")
                    # elif keypress == pygame.K_3:
                    #     self.textdrama.queue.append("Before")
                    # elif keypress == pygame.K_4:
                    #     self.textdrama.queue.append("Where the hell is blue team, can only see red")
                    # elif keypress == pygame.K_5:
                    #     self.textdrama.queue.append("After")
                    # elif keypress == pygame.K_6:
                    #     self.textdrama.queue.append("Now much more clear")
                    # elif keypress == pygame.K_n and self.last_selected is not None:
                    #     if self.last_selected.team == 1:
                    #         self.last_selected.switchfaction(self.team1unit, self.team2unit, self.team1poslist, self.enactment)
                    #     else:
                    #         self.last_selected.switchfaction(self.team2unit, self.team1unit, self.team2poslist, self.enactment)
                    # elif keypress == pygame.K_l and self.last_selected is not None:
                    #     for subunit in self.last_selected.subunit_sprite:
                    #         subunit.base_morale = 0
                    # elif keypress == pygame.K_k and self.last_selected is not None:
                    #     # for index, subunit in enumerate(self.last_selected.subunit_sprite):
                    #     #     subunit.unit_health -= subunit.unit_health
                    #     self.subunit_selected.who.unit_health -= self.subunit_selected.who.unit_health
                    # elif keypress == pygame.K_m and self.last_selected is not None:
                    #     # self.last_selected.leader[0].health -= 1000
                    #     self.subunit_selected.who.leader.health -= 1000
                    #     # self.subunit_selected.who.base_morale -= 1000
                    #     # self.subunit_selected.who.brokenlimit = 80
                    #     # self.subunit_selected.who.state = 99
                    # elif keypress == pygame.K_COMMA and self.last_selected is not None:
                    #     for index, subunit in enumerate(self.last_selected.subunit_sprite):
                    #         subunit.stamina -= subunit.stamina
                    # ^^ End For development test
                    # ^ End register input

                    # v Camera movement
                    if self.mode == "uniteditor":
                        if keystate[K_s] or self.mousepos[1] >= self.bottomcorner:  # Camera move down
                            self.basecamerapos[1] += 4 * (
                                    11 - self.camerascale)  # need "11 -" for converting cameral scale so the further zoom camera move faster
                            self.camerapos[1] = self.basecamerapos[1] * self.camerascale  # resize camera pos
                            self.camerafix()

                        elif keystate[K_w] or self.mousepos[1] <= 5:  # Camera move up
                            self.basecamerapos[1] -= 4 * (11 - self.camerascale)
                            self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                            self.camerafix()

                        if keystate[K_a] or self.mousepos[0] <= 5:  # Camera move left
                            self.basecamerapos[0] -= 4 * (11 - self.camerascale)
                            self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                            self.camerafix()

                        elif keystate[K_d] or self.mousepos[0] >= self.rightcorner:  # Camera move right
                            self.basecamerapos[0] += 4 * (11 - self.camerascale)
                            self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                            self.camerafix()

                        self.cameraupcorner = (self.camerapos[0] - self.centerscreen[0],
                                               self.camerapos[1] - self.centerscreen[1])  # calculate top left corner of camera position
                    # ^ End camera movement

                    # if self.mousetimer != 0:  # player click mouse once before
                    #     self.mousetimer += self.uidt  # increase timer for mouse click using real time
                    #     if self.mousetimer >= 0.3:  # time pass 0.3 second no longer count as double click
                    #         self.mousetimer = 0

                    self.battle_mouse_pos[0] = pygame.Vector2((self.mousepos[0] - self.centerscreen[0]) + self.camerapos[0],
                                                              self.mousepos[1] - self.centerscreen[1] + self.camerapos[
                                                                  1])  # mouse pos on the map based on camera position
                    self.battle_mouse_pos[1] = self.battle_mouse_pos[0] / self.camerascale  # mouse pos on the map at current camera zoom scale

                    if mouse_up or mouse_right or mouse_leftdown or mouse_rightdown:
                        if mouse_up:
                            self.clickany = False
                            self.newunitclick = False

                        if self.minimap.rect.collidepoint(self.mousepos):  # mouse position on mini map
                            self.uiclick = True

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

                            else:
                                for index, button in enumerate(self.eventlog_button):  # Event log button and timer button click
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
                                        break

                            # v code that only run when any unit is selected
                            self.battleui.remove(self.leaderpopup)  # remove leader name popup if no mouseover on any button
                            self.battleui.remove(self.button_name_popup)  # remove popup if no mouseover on any button

                            if mouse_right and self.uiclick is False:  # Unit command
                                self.last_selected.command(self.battle_mouse_pos[1], mouse_right, double_mouse_right,
                                                           self.last_mouseover, keystate)

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
                                            self.troopcard_ui.valueinput(who=self.showincard, weaponlist=self.allweapon, armourlist=self.allarmour,
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
                                                for slot in self.unit_build_slot:
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
                                                for slot in self.unit_build_slot:  # can't use gameid here as none subunit not count in position check
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
                                            self.troopcard_ui.valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                         armourlist=self.allarmour)  # update subunit card on selected subunit
                                            if self.troopcard_ui.option == 2:
                                                self.traitskillblit()
                                                self.effecticonblit()
                                                self.countdownskillicon()
                                            # self.previewauthority(self.preview_leader, 0)  # calculate authority

                                        else:  # new preset
                                            self.unitpresetname = ""
                                            for slot in self.unit_build_slot:  # reset all sub-subunit slot
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

                                            # self.troopcard_ui.valueinput(attacker=self.showincard, weapon_list=self.allweapon, armour_list=self.allarmour,
                                            #                       changeoption=1)

                            # elif self.gameui[1] in self.battleui and self.gameui[1].rect.collidepoint(self.mousepos):
                            #     self.uiclick = True
                            #     for leaderindex, leader in enumerate(self.leadernow):  # loop mouse pos on leader portrait
                            #         if leader.rect.collidepoint(self.mousepos):
                            #             armyposition = self.leaderposname[leader.armyposition + 4]
                            # 
                            #             self.leaderpopup.pop(self.mousepos, armyposition + ": " + leader.name)  # popup leader name when mouse over
                            #             self.battleui.add(self.leaderpopup)
                            # 
                            #             if mouse_up:  # open list of leader to change leader in that slot
                            #                 self.selectleader = leaderindex
                            #                 self.popuplist_newopen(leader.rect.midright, self.leader_list, "leader")
                            # 
                            #             elif mouse_right:
                            #                 self.popout_lorebook(8, leader.leaderid)
                            #             break

                            elif self.troopcard_ui.rect.collidepoint(self.mousepos):
                                self.uiclick = True
                                if self.showincard is not None and mouse_up:
                                    self.unitcardbutton_click(self.showincard)

                                if self.troopcard_ui.option == 2:
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
                                                        self.editor_map_change(map.terraincolour[self.baseterrain],
                                                                               map.featurecolour[self.featureterrain])

                                                    elif self.popup_listbox.type == "feature":
                                                        self.feature_change_button.changetext(self.battlemap_feature.featurelist[index])
                                                        self.featureterrain = index
                                                        self.editor_map_change(map.terraincolour[self.baseterrain],
                                                                               map.featurecolour[self.featureterrain])

                                                    elif self.popup_listbox.type == "weather":
                                                        self.weathertype = int(index / 3)
                                                        self.weatherstrength = index - (self.weathertype * 3)
                                                        self.weather_change_button.changetext(self.weather_list[index])
                                                        del self.currentweather
                                                        self.currentweather = weather.Weather(self.timeui, self.weathertype + 1,
                                                                                              self.weatherstrength, self.allweather)

                                                    for slot in self.unit_build_slot:  # reset all troop stat
                                                        slot.changetroop(slot.troopid, self.baseterrain,
                                                                         self.baseterrain * len(
                                                                             self.battlemap_feature.featurelist) + self.featureterrain,
                                                                         self.currentweather)
                                                    if self.showincard is not None:  # reset subunit card as well
                                                        self.troopcard_ui.valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                                     armourlist=self.allarmour,
                                                                                     changeoption=1)
                                                        if self.troopcard_ui.option == 2:
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
                                                self.setuplist(menu.NameList, self.currentpopuprow, self.battlemap_base.terrainlist,
                                                               self.popup_namegroup, self.popup_listbox, self.battleui, layer=17)
                                            elif self.popup_listbox.type == "feature":
                                                self.setuplist(menu.NameList, self.currentpopuprow, self.battlemap_feature.featurelist,
                                                               self.popup_namegroup, self.popup_listbox, self.battleui, layer=17)
                                            elif self.popup_listbox.type == "weather":
                                                self.setuplist(menu.NameList, self.currentpopuprow, self.weather_list,
                                                               self.popup_namegroup,
                                                               self.popup_listbox, self.battleui, layer=17)
                                            elif self.popup_listbox.type == "leader":
                                                self.setuplist(menu.NameList, self.currentpopuprow, self.leader_list,
                                                               self.popup_namegroup,
                                                               self.popup_listbox, self.battleui, layer=19)

                                        else:
                                            self.battleui.remove(self.popup_listbox, self.popup_listscroll, *self.popup_namegroup)

                                    elif self.troop_scroll.rect.collidepoint(self.mousepos):  # click on subsection list scroller
                                        self.uiclick = True
                                        self.current_troop_row = self.troop_scroll.update(
                                            self.mousepos)  # update the scroller and get new current subsection
                                        if self.current_list_show == "troop":
                                            self.setuplist(menu.NameList, self.current_troop_row, self.troop_list, self.troop_namegroup,
                                                           self.troop_listbox, self.battleui)
                                        elif self.current_list_show == "faction":
                                            self.setuplist(menu.NameList, self.current_troop_row, self.faction_list, self.troop_namegroup,
                                                           self.troop_listbox, self.battleui)

                                    elif self.unit_presetname_scroll.rect.collidepoint(self.mousepos):
                                        self.uiclick = True
                                        self.current_unit_row = self.unit_presetname_scroll.update(
                                            self.mousepos)  # update the scroller and get new current subsection
                                        self.setuplist(menu.NameList, self.current_unit_row, list(self.customunitpresetlist.keys()),
                                                       self.unitpreset_namegroup, self.unit_listbox, self.battleui)  # setup preset army list

                                    elif self.unit_build_slot in self.battleui:
                                        slotclick = None
                                        for slot in self.unit_build_slot:  # left click on any sub-subunit slot
                                            if slot.rect.collidepoint(self.mousepos):
                                                self.uiclick = True
                                                slotclick = slot
                                                break

                                        if slotclick is not None:
                                            if keystate[pygame.K_LSHIFT] or keystate[pygame.K_RSHIFT]:  # add all sub-subunit from the first selected
                                                firstone = None
                                                for newslot in self.unit_build_slot:
                                                    if newslot.armyid == slotclick.armyid and newslot.gameid <= slotclick.gameid:
                                                        if firstone is None and newslot.selected:  # found the previous selected sub-subunit
                                                            firstone = newslot.gameid
                                                            if slotclick.gameid <= firstone:  # cannot go backward, stop loop
                                                                break
                                                            elif slotclick.selected is False:  # forward select, acceptable
                                                                slotclick.selected = True
                                                                self.uniteditborder.add(battleui.SelectedSquad(slotclick.inspposition, 5))
                                                                self.battleui.add(*self.uniteditborder)
                                                        elif firstone is not None and newslot.gameid > firstone and newslot.selected is False:  # select from first select to clicked
                                                            newslot.selected = True
                                                            self.uniteditborder.add(battleui.SelectedSquad(newslot.inspposition, 5))
                                                            self.battleui.add(*self.uniteditborder)

                                            elif keystate[pygame.K_LCTRL] or keystate[
                                                pygame.K_RCTRL]:  # add another selected sub-subunit with left ctrl + left mouse button
                                                if slotclick.selected is False:
                                                    slotclick.selected = True
                                                    self.uniteditborder.add(battleui.SelectedSquad(slotclick.inspposition, 5))
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
                                                for newslot in self.unit_build_slot:
                                                    newslot.selected = False
                                                slotclick.selected = True
                                                self.uniteditborder.add(battleui.SelectedSquad(slotclick.inspposition, 5))
                                                self.battleui.add(*self.uniteditborder)

                                                if slotclick.name != "None":
                                                    self.battleui.remove(*self.leadernow)
                                                    self.leadernow = [leader for leader in self.previewleader]
                                                    self.battleui.add(*self.leadernow)  # add leader portrait to draw
                                                    self.showincard = slot
                                                    self.troopcard_ui.valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                                 armourlist=self.allarmour)  # update subunit card on selected subunit
                                                    if self.troopcard_ui.option == 2:
                                                        self.traitskillblit()
                                                        self.effecticonblit()
                                                        self.countdownskillicon()

                                if mouse_up or mouse_right:
                                    if self.unit_build_slot in self.battleui and self.troop_listbox.rect.collidepoint(self.mousepos):
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

                                                        self.setuplist(menu.NameList, self.current_troop_row, self.troop_list,
                                                                       self.troop_namegroup,
                                                                       self.troop_listbox, self.battleui)  # setup troop name list
                                                        self.troop_scroll.changeimage(newrow=self.current_troop_row,
                                                                                      logsize=len(self.troop_list))  # change troop scroll image

                                                        self.main.maketeamcoa([index], uiclass=self.battleui, oneteam=True,
                                                                              team1setpos=(
                                                                                  self.troop_listbox.rect.midleft[0] - int(
                                                                                      (200 * self.width_adjust) / 2),
                                                                                  self.troop_listbox.rect.midleft[1]))  # change team coa

                                                        self.current_list_show = "troop"

                                                    elif mouse_right:
                                                        self.popout_lorebook(2, index)

                                                elif self.current_list_show == "troop":
                                                    if mouse_up:
                                                        for slot in self.unit_build_slot:
                                                            if slot.selected:
                                                                if keystate[pygame.K_LSHIFT]:  # change all sub-subunit in army
                                                                    for newslot in self.unit_build_slot:
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
                                                                    self.troopcard_ui.valueinput(who=self.showincard, weaponlist=self.allweapon,
                                                                                                 armourlist=self.allarmour)  # update subunit card on selected subunit
                                                                    if self.troopcard_ui.option == 2:
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

                                                for slot in self.unit_build_slot:
                                                    slot.team = self.teamchange_button.event + 1
                                                    slot.changeteam(True)

                                            elif self.slotdisplay_button.rect.collidepoint(self.mousepos):
                                                if self.slotdisplay_button.event == 0:  # hide
                                                    self.slotdisplay_button.event = 1
                                                    self.battleui.remove(self.unitsetup_stuff, self.leadernow)

                                                elif self.slotdisplay_button.event == 1:  # show
                                                    self.slotdisplay_button.event = 0
                                                    self.battleui.add(self.unitsetup_stuff, self.leadernow)

                                            elif self.deploy_button.rect.collidepoint(self.mousepos) and self.unit_build_slot in self.battleui:
                                                candeploy = True
                                                subunitcount = 0
                                                warninglist = []
                                                for slot in self.unit_build_slot:
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
                                                    for slot in self.unit_build_slot:  # just for grabing current selected team
                                                        currentpreset[self.unitpresetname] += (0, 100, 100, slot.team)
                                                        longscript.convertedit_unit(self,
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
                                                            self.setuplist(menu.NameList, self.current_troop_row, self.troop_list,
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
                                                    self.setuplist(menu.NameList, self.current_troop_row, self.faction_list,
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
                                    self.troopcard_ui.valueinput(who=self.subunit_selected.who, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                                 splithappen=self.splithappen)
                                self.battleui.remove(*self.leadernow)

                                self.addbehaviourui(self.last_selected, elsecheck=True)

                                if self.splithappen:  # end split check
                                    self.splithappen = False

                            # else:  # Update topbar and command ui value every 1.1 seconds
                            #     if self.ui_timer >= 1.1:
                            #         self.gameui[0].valueinput(who=self.last_selected, splithappen=self.splithappen)

                        elif self.gamestate == 2 and self.unit_build_slot not in self.battleui:
                            if (mouse_right or mouse_rightdown) and self.uiclick is False:  # Unit placement
                                self.last_selected.placement(self.battle_mouse_pos[1], mouse_right, mouse_rightdown, double_mouse_right)

                            if keystate[pygame.K_DELETE]:
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
                    if self.gamestate == 1 and self.inspectui and ((self.ui_timer >= 1.1 and self.troopcard_ui.option != 0) or
                                                                   self.before_selected != self.last_selected):
                        self.troopcard_ui.valueinput(who=self.subunit_selected.who, weaponlist=self.allweapon, armourlist=self.allarmour,
                                                     splithappen=self.splithappen)
                        if self.troopcard_ui.option == 2:  # skill and status effect card
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
                        if self.weather_current is not None and self.timenumber.timenum >= self.weather_current:
                            del self.currentweather
                            this_weather = self.weather_event[0]

                            if this_weather[0] != 0:
                                self.currentweather = weather.Weather(self.timeui, this_weather[0], this_weather[2], self.allweather)
                            else:  # Random weather
                                self.currentweather = weather.Weather(self.timeui, random.randint(0, 11), random.randint(0, 2),
                                                                      self.allweather)
                            self.weather_event.pop(0)
                            self.showmap.addeffect(self.battlemap_height,
                                                   self.weather_effect_imgs[self.currentweather.weathertype][self.currentweather.level])

                            if len(self.weather_event) > 0:  # Get end time of next event which is now index 0
                                self.weather_current = self.weather_event[0][1]
                            else:
                                self.weather_current = None

                        if self.currentweather.spawnrate > 0 and len(self.weathermatter) < self.currentweather.speed:
                            spawnnum = range(0,
                                             int(self.currentweather.spawnrate * self.dt * random.randint(0,
                                                                                                          10)))  # number of sprite to spawn at this time
                            for spawn in spawnnum:  # spawn each weather sprite
                                truepos = (random.randint(10, self.SCREENRECT.width), 0)  # starting pos
                                target = (truepos[0], self.SCREENRECT.height)  # final base_target pos

                                if self.currentweather.spawnangle == 225:  # top right to bottom left movement
                                    startpos = random.randint(10, self.SCREENRECT.width * 2)  # starting x pos that can be higher than screen width
                                    truepos = (startpos, 0)
                                    if startpos >= self.SCREENRECT.width:  # x higher than screen width will spawn on the right corner of screen but not at top
                                        startpos = self.SCREENRECT.width  # revert x back to screen width
                                        truepos = (startpos, random.randint(0, self.SCREENRECT.height))

                                    if truepos[1] > 0:  # start position simulate from beyond top right of screen
                                        target = (truepos[1] * self.weatherscreenadjust, self.SCREENRECT.height)
                                    elif truepos[0] < self.SCREENRECT.width:  # start position inside screen width
                                        target = (0, truepos[0] / self.weatherscreenadjust)

                                elif self.currentweather.spawnangle == 270:  # right to left movement
                                    truepos = (self.SCREENRECT.width, random.randint(0, self.SCREENRECT.height))
                                    target = (0, truepos[1])

                                randompic = random.randint(0, len(self.weather_matter_imgs[self.currentweather.weathertype]) - 1)
                                self.weathermatter.add(weather.Mattersprite(truepos, target,
                                                                            self.currentweather.speed,
                                                                            self.weather_matter_imgs[self.currentweather.weathertype][
                                                                                randompic]))
                        # ^ End weather system

                        # v Music System
                        if len(self.music_schedule) > 0 and self.timenumber.timenum >= self.music_schedule[0]:
                            pygame.mixer.music.unload()
                            self.music_current = self.music_event[0].copy()
                            self.pickmusic = random.randint(0, len(self.music_current) - 1)
                            pygame.mixer.music.load(self.musiclist[self.music_current[self.pickmusic]])
                            pygame.mixer.music.play(fade_ms=100)
                            self.music_schedule = self.music_schedule[1:]
                            self.music_event = self.music_event[1:]
                        # ^ End music system

                        for unit in self.allunitlist:
                            unit.collide = False  # reset collide

                        if len(self.allsubunitlist) > 1:
                            tree = KDTree(
                                [sprite.base_pos for sprite in self.allsubunitlist])  # collision loop check, much faster than pygame collide check
                            collisions = tree.query_pairs(self.collide_distance)
                            for one, two in collisions:
                                spriteone = self.allsubunitlist[one]
                                spritetwo = self.allsubunitlist[two]
                                if spriteone.parentunit != spritetwo.parentunit:  # collide with subunit in other unit
                                    if spriteone.base_pos.distance_to(spriteone.base_pos) < self.full_distance:
                                        spriteone.fullmerge.append(spritetwo)
                                        spritetwo.fullmerge.append(spriteone)

                                    if spriteone.front_pos.distance_to(spritetwo.base_pos) < self.front_distance:  # first subunit collision
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
                                    if spritetwo.front_pos.distance_to(spriteone.base_pos) < self.front_distance:  # second subunit
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
                                    if spriteone.front_pos.distance_to(spritetwo.base_pos) < self.front_distance:  # first subunit collision
                                        if spriteone.base_pos.distance_to(spriteone.base_pos) < self.full_distance:
                                            spriteone.fullmerge.append(spritetwo)
                                            spritetwo.fullmerge.append(spriteone)

                                        if spriteone.state in (2, 4, 6, 10, 11, 12, 13, 99) or \
                                                spritetwo.state in (2, 4, 6, 10, 11, 12, 13):
                                            spriteone.same_front.append(spritetwo)
                                    if spritetwo.front_pos.distance_to(spriteone.base_pos) < self.front_distance:  # second subunit
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
                    command = self.escmenu_process(mouse_up, mouse_leftdown, esc_press, mouse_scrollup, mouse_scrolldown, self.battleui)
                    if command == "end_battle":
                        return

            elif self.textinputpopup != (None, None):  # currently have input text pop up on screen, stop everything else until done
                for button in self.input_button:
                    button.update(self.mousepos, mouse_up, mouse_leftdown, "any")

                if self.input_ok_button.event:
                    self.input_ok_button.event = False

                    if self.textinputpopup[1] == "save_unit":
                        currentpreset = self.convertslot_dict(self.input_box.text)
                        if currentpreset is not None:
                            self.customunitpresetlist.update(currentpreset)

                            self.unitpresetname = self.input_box.text
                            self.setuplist(menu.NameList, self.current_unit_row, list(self.customunitpresetlist.keys()),
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
                        self.setuplist(menu.NameList, self.current_unit_row, list(self.customunitpresetlist.keys()),
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
