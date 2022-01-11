import csv
import datetime
import glob
import os
import random
import sys

import numpy as np
import pygame
import pygame.freetype
from gamescript import camera, map, weather, battleui, commonscript, menu, escmenu
from gamescript.tactical import subunit, unit, leader, longscript
from pygame.locals import *
from scipy.spatial import KDTree

load_image = commonscript.load_image
load_images = commonscript.load_images
csv_read = commonscript.csv_read
load_sound = commonscript.load_sound
editconfig = commonscript.edit_config
setuplist = commonscript.setup_list
list_scroll = commonscript.list_scroll


class Battle:
    splitunit = longscript.splitunit
    traitskillblit = commonscript.trait_skill_blit
    effecticonblit = commonscript.effect_icon_blit
    countdownskillicon = commonscript.countdown_skill_icon
    kill_effect_icon = commonscript.kill_effect_icon
    popout_lorebook = commonscript.popout_lorebook
    popuplist_newopen = commonscript.popup_list_open
    escmenu_process = escmenu.escmenu_process

    def __init__(self, main, winstyle):
        # v Get self object/variable from gamestart
        self.mode = None  # battle map mode can be "uniteditor" for unit editor or "battle" for self battle
        self.main = main
        self.genre = main.genre
        self.config = main.config
        self.SoundVolume = main.Soundvolume
        self.screen_rect = main.screen_rect
        self.teamcolour = main.team_colour
        self.main_dir = main.main_dir
        self.screen_scale = main.screen_scale
        self.eventlog = main.eventlog
        self.battlecamera = main.battle_camera
        self.battleui = main.battle_ui

        self.unit_updater = main.unit_updater
        self.subunit_updater = main.subunit_updater
        self.leader_updater = main.leader_updater
        self.ui_updater = main.ui_updater
        self.weather_updater = main.weather_updater
        self.effect_updater = main.effect_updater

        self.battle_map_base = main.battle_map_base
        self.battle_map_feature = main.battle_map_feature
        self.battle_map_height = main.battle_map_height
        self.showmap = main.show_map

        self.team0_unit = main.team0_unit
        self.team1_unit = main.team1_unit
        self.team2_unit = main.team2_unit
        self.team0_subunit = main.team0_subunit
        self.team1_subunit = main.team1_subunit
        self.team2_subunit = main.team2_subunit
        self.subunit = main.subunit
        self.army_leader = main.army_leader

        self.arrows = main.range_attacks
        self.direction_arrows = main.direction_arrows
        self.troop_number_sprite = main.troop_number_sprite

        self.game_ui = main.game_ui
        self.inspectuipos = main.inspectuipos
        self.inspectsubunit = main.inspectsubunit
        self.popgameui = main.game_ui  # saving list of game_ui that will pop out when parentunit is selected

        self.battle_map_base = main.battle_map_base
        self.battle_map_feature = main.battle_map_feature
        self.battle_map_height = main.battle_map_height
        self.showmap = main.show_map

        self.mini_map = main.mini_map
        self.eventlog = main.eventlog
        self.logscroll = main.log_scroll
        self.button_ui = main.button_ui
        self.subunit_selected_border = main.inspect_selected_border
        self.switch_button = main.switch_button

        self.fps_count = main.fps_count

        self.terrain_check = main.terrain_check
        self.button_name_popup = main.button_name_popup
        self.leader_popup = main.leader_popup
        self.effect_popup = main.effect_popup
        self.drama_text = main.drama_text

        self.skill_icon = main.skill_icon
        self.effect_icon = main.effect_icon

        self.battle_menu = main.battle_menu
        self.battle_menu_button = main.battle_menu_button
        self.escoptionmenubutton = main.esc_option_menu_button

        self.unit_delete_button = self.main.unit_delete_button
        self.unit_save_button = self.main.unit_save_button
        self.troop_listbox = main.troop_listbox
        self.troop_namegroup = main.troop_namegroup
        self.filter_box = main.filter_box
        self.tickbox_filter = main.filter_tick_box
        self.teamchange_button = main.team_change_button
        self.slotdisplay_button = main.slot_display_button
        self.test_button = main.test_button
        self.deploy_button = main.deploy_button
        self.popup_listbox = main.popup_listbox
        self.popup_namegroup = main.popup_namegroup
        self.terrain_change_button = main.terrain_change_button
        self.feature_change_button = main.feature_change_button
        self.weather_change_button = main.weather_change_button
        self.unit_build_slot = main.unit_build_slot
        self.unit_edit_border = main.unit_edit_border
        self.preview_leader = main.preview_leader
        self.unitpreset_namegroup = main.unitpreset_namegroup
        self.presetselectborder = main.preset_select_border
        self.customunitpresetlist = main.custom_unit_preset_list
        self.unit_listbox = main.unit_listbox
        self.troo_scroll = main.troop_scroll
        self.faction_list = main.faction_list
        self.popup_listscroll = main.popup_listscroll
        self.troop_scroll = main.troop_scroll
        self.team_coa = main.team_coa
        self.unit_presetname_scroll = main.unit_preset_name_scroll
        self.warningmsg = main.warning_msg

        self.input_button = main.input_button
        self.input_box = main.input_box
        self.inputui = main.input_ui
        self.input_ok_button = main.input_ok_button
        self.input_cancel_button = main.input_cancel_button
        self.inputui_pop = main.input_ui_popup
        self.confirmui = main.confirm_ui
        self.confirmui_pop = main.confirm_ui_popup

        self.unit_selector = main.unit_selector
        self.unit_icon = main.unit_icon
        self.selectscroll = main.selectscroll

        self.timeui = main.time_ui
        self.timenumber = main.time_number

        self.scaleui = main.scale_ui

        self.speednumber = main.speed_number

        self.weathermatter = main.weather_matter
        self.weathereffect = main.weather_effect

        self.encyclopedia = main.encyclopedia
        self.lorenamelist = main.lore_name_list
        self.lorebuttonui = main.lore_button_ui
        self.lorescroll = main.lore_scroll
        self.subsection_name = main.subsection_name
        self.pagebutton = main.page_button

        self.all_weather = main.all_weather
        self.weather_matter_imgs = main.weather_matter_imgs
        self.weather_effect_imgs = main.weather_effect_imgs
        self.weather_list = main.weather_list

        self.featuremod = main.feature_mod

        self.allfaction = main.all_faction
        self.coa_list = main.coa_list

        self.allweapon = main.allweapon
        self.allarmour = main.allarmour

        self.status_imgs = main.status_imgs
        self.role_imgs = main.role_imgs
        self.trait_imgs = main.trait_imgs
        self.skill_imgs = main.skill_imgs

        self.troop_data = main.troop_data
        self.leader_stat = main.leader_stat

        self.statetext = main.state_text

        self.squadwidth = main.sprite_width
        self.squadheight = main.sprite_height
        self.collide_distance = self.squadheight / 10  # distance to check collision
        self.front_distance = self.squadheight / 20  # distance from front side
        self.full_distance = self.front_distance / 2  # distance for sprite merge check

        self.combatpathqueue = []  # queue of sub-unit to run melee combat pathfiding

        self.escslidermenu = main.esc_slider_menu
        self.escvaluebox = main.esc_value_box

        self.eventlog_button = main.eventlog_button
        self.time_button = main.time_button
        self.command_ui = main.command_ui
        self.troopcard_ui = main.troopcard_ui
        self.troopcard_button = main.troopcard_button
        self.inspect_ui = main.inspect_ui
        self.inspect_button = main.inspect_button
        self.col_split_button = main.col_split_button
        self.row_split_button = main.row_split_button
        self.unitstat_ui = main.unitstat_ui

        self.leaderposname = main.leader_level

        self.battledone_box = main.battledone_box
        self.gamedone_button = main.gamedone_button
        # ^ End load from gamestart

        self.gamespeed = 0
        self.gamespeedset = (0, 0.5, 1, 2, 4, 6)  # availabe self speed
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

        self.unitsetup_stuff = (self.unit_build_slot, self.unit_edit_border, self.command_ui, self.troopcard_ui,
                                self.team_coa, self.troopcard_button, self.troop_listbox, self.troop_scroll,
                                self.troop_namegroup, self.unit_listbox, self.presetselectborder,
                                self.unitpreset_namegroup, self.unit_save_button, self.unit_delete_button,
                                self.unit_presetname_scroll)
        self.filter_stuff = (self.filter_box, self.slotdisplay_button, self.teamchange_button, self.deploy_button, self.terrain_change_button,
                             self.feature_change_button, self.weather_change_button, self.tickbox_filter)

        self.bestdepth = pygame.display.mode_ok(self.screen_rect.size, winstyle, 32)  # Set the display mode
        self.screen = pygame.display.set_mode(self.screen_rect.size, winstyle | pygame.RESIZABLE, self.bestdepth)  # set up self screen

        # v Assign default variable to some class
        unit.Unit.gamebattle = self
        unit.Unit.imgsize = (self.squadwidth, self.squadheight)
        subunit.Subunit.gamebattle = self
        leader.Leader.gamebattle = self
        # ^ End assign default

        self.background = pygame.Surface(self.screen_rect.size)  # Create background image
        self.background.fill((255, 255, 255))  # fill background image with black colour

    def editor_map_change(self, basecolour, featurecolour):
        imgs = (pygame.Surface((1000, 1000)), pygame.Surface((1000, 1000)), pygame.Surface((1000, 1000), pygame.SRCALPHA), None)
        imgs[0].fill(basecolour)  # start with temperate terrain
        imgs[1].fill(featurecolour)  # start with plain feature
        imgs[2].fill((255, 100, 100, 125))  # start with height 100 plain

        self.battle_map_base.draw_image(imgs[0])
        self.battle_map_feature.draw_image(imgs[1])
        self.battle_map_height.draw_image(imgs[2])
        self.showmap.draw_image(self.battle_map_base, self.battle_map_feature, self.battle_map_height, None, self, True)
        self.mini_map.draw_image(self.showmap.true_image, self.camera)
        self.showmap.change_scale(self.camerascale)

    def preparenewgame(self, ruleset, ruleset_folder, teamselected, enactment, mapselected, source, unitscale, mode):

        self.ruleset = ruleset  # current ruleset used
        self.ruleset_folder = ruleset_folder  # the folder of rulseset used
        self.mapselected = mapselected  # map folder name
        self.source = str(source)
        self.unitscale = unitscale
        self.playerteam = teamselected  # player selected team

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
            battleui.EventLog.map_event = mapevent
        except Exception:  # can't find any event file
            mapevent = {}  # create empty list

        self.eventlog.make_new_log()  # reset old event log

        self.eventlog.add_event_log(mapevent)

        self.eventschedule = None
        self.eventlist = []
        for index, event in enumerate(self.eventlog.map_event):
            if self.eventlog.map_event[event][3] is not None:
                if index == 0:
                    self.eventmapid = event
                    self.eventschedule = self.eventlog.map_event[event][3]
                self.eventlist.append(event)

        self.timenumber.start_setup(self.weather_current)

        # v Create the battle map
        self.camerapos = pygame.Vector2(500, 500)  # Camera pos at the current zoom, start at center of map
        self.basecamerapos = pygame.Vector2(500, 500)  # Camera pos at furthest zoom for recalculate sprite pos after zoom
        self.camerascale = 1  # Camera zoom
        camera.Camera.screen_rect = self.screen_rect
        self.camera = camera.Camera(self.camerapos, self.camerascale)

        if mapselected is not None:
            imgs = load_images(self.main_dir, ["ruleset", self.ruleset_folder, "map", self.mapselected], loadorder=False)
            self.battle_map_base.draw_image(imgs[0])
            self.battle_map_feature.draw_image(imgs[1])
            self.battle_map_height.draw_image(imgs[2])

            try:  # place_name map layer is optional, if not existed in folder then assign None
                placenamemap = imgs[3]
            except Exception:
                placenamemap = None
            self.showmap.draw_image(self.battle_map_base, self.battle_map_feature, self.battle_map_height, placenamemap, self, False)
        else:  # for unit editor mode, create empty temperate glass map
            self.editor_map_change((166, 255, 107), (181, 230, 29))
        # ^ End create battle map

        self.clock = pygame.time.Clock()  # Game clock to keep track of realtime pass

        self.enactment = enactment  # enactment mod, control both team

        self.team0poslist = {}  # team 0 parentunit position
        self.team1poslist = {}  # team 1 parentunit position
        self.team2poslist = {}  # same for team 2

        self.allunitlist = []  # list of every parentunit in self alive
        self.allunitindex = []  # list of every parentunit index alive

        self.allsubunitlist = []  # list of all subunit alive in self

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
        with open(os.path.join("profile", "unitpreset", str(self.ruleset), "custom_unitpreset.csv"), "w", encoding='utf-8', newline="") as csvfile:
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
            currentpreset[int(startitem / 8)].append(str(slot.troop_id))
            startitem += 1
            if slot.troop_id != 0:
                subunitcount += 1
        if pos is not None:
            currentpreset.append(pos)

        if subunitcount > 0:
            leaderlist = []
            leaderposlist = []
            for leader in self.preview_leader:  # add leader id
                countzero = 0
                if leader.leader_id != 1:
                    subunitcount += 1
                    for slotindex, slot in enumerate(self.unit_build_slot):  # add subunit troop id
                        if slot.troop_id == 0:
                            countzero += 1
                        if slotindex == leader.subunit_pos:
                            break

                leaderlist.append(str(leader.leader_id))
                leaderposlist.append(str(leader.subunit_pos - countzero))
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
        bigunitsize = len([slot for slot in self.unit_build_slot if slot.army_id == armyid and slot.name != "None"])
        if bigunitsize > 20:  # army size larger than 20 will reduce gamestart leader authority
            authority = int(leaderlist[0].authority +
                            (leaderlist[0].authority / 2 * (100 - bigunitsize) / 100) +
                            leaderlist[1].authority / 2 + leaderlist[2].authority / 2 +
                            leaderlist[3].authority / 4)

        for slot in self.unit_build_slot:
            if slot.army_id == armyid:
                slot.authority = authority

        if self.showincard is not None:
            self.command_ui.value_input(who=self.showincard)
        # ^ End cal authority

    def setup_uniticon(self):
        """Setup unit selection list in unit selector ui top left of screen"""
        row = 30
        startcolumn = 25
        column = startcolumn
        unitlist = self.team1_unit
        if self.playerteam == 2:
            unitlist = self.team2_unit
        if self.enactment:  # include another team unit icon as well in enactment mode
            unitlist = self.allunitlist
        currentindex = int(self.unit_selector.current_row * self.unit_selector.max_column_show)  # the first index of current row
        self.unit_selector.log_size = len(unitlist) / self.unit_selector.max_column_show

        if self.unit_selector.log_size.is_integer() is False:
            self.unit_selector.log_size = int(self.unit_selector.log_size) + 1

        if self.unit_selector.current_row > self.unit_selector.log_size - 1:
            self.unit_selector.current_row = self.unit_selector.log_size - 1
            currentindex = int(self.unit_selector.current_row * self.unit_selector.max_column_show)
            self.selectscroll.change_image(new_row=self.unit_selector.current_row)

        if len(self.unit_icon) > 0:  # Remove all old icon first before making new list
            for icon in self.unit_icon:
                icon.kill()
                del icon

        for index, unit in enumerate(unitlist):  # add unit icon for drawing according to appopriate current row
            if index >= currentindex:
                self.unit_icon.add(battleui.ArmyIcon((column, row), unit))
                column += 40
                if column > 250:
                    row += 50
                    column = startcolumn
                if row > 100:
                    break  # do not draw for the third row
        self.selectscroll.change_image(log_size=self.unit_selector.log_size)

    def checksplit(self, whoinput):
        """Check if unit can be splitted, if not remove splitting button"""
        # v split by middle collumn
        if np.array_split(whoinput.armysubunit, 2, axis=1)[0].size >= 10 and np.array_split(whoinput.armysubunit, 2, axis=1)[1].size >= 10 and \
                whoinput.leader[1].name != "None":  # can only split if both parentunit size will be larger than 10 and second leader exist
            self.battleui.add(self.col_split_button)
        elif self.col_split_button in self.battleui:
            self.battleui.remove(self.col_split_button)
        # ^ End col

        # v split by middle row
        if np.array_split(whoinput.armysubunit, 2)[0].size >= 10 and np.array_split(whoinput.armysubunit, 2)[1].size >= 10 and \
                whoinput.leader[1].name != "None":
            self.battleui.add(self.row_split_button)
        elif self.row_split_button in self.battleui:
            self.battleui.remove(self.row_split_button)

    def ui_mouseover(self):
        """mouse over ui that is not subunit card and unitbox (topbar and commandbar)"""
        for this_ui in self.game_ui:
            if this_ui in self.battleui and this_ui.rect.collidepoint(self.mouse_pos):
                self.clickany = True
                self.uiclick = True
                break
        return self.clickany

    def uniticon_mouseover(self, mouseup, mouseright):
        """process user mouse input on unit icon, left click = select, right click = go to parentunit position on map"""
        self.clickany = True
        self.uiclick = True
        if self.gamestate == 1 or (self.gamestate == 2 and self.unit_build_slot not in self.battleui):
            for icon in self.unit_icon:
                if icon.rect.collidepoint(self.mouse_pos):
                    if mouseup:
                        self.last_selected = icon.army
                        self.last_selected.justselected = True
                        self.last_selected.selected = True

                        if self.before_selected is None:  # add back the pop up ui so it get shown when click subunit with none selected before
                            self.battleui.add(self.unitstat_ui, self.command_ui)  # add leader and top ui
                            self.battleui.add(self.inspect_button)  # add inspection ui open/close button

                            self.addbehaviourui(self.last_selected)

                    elif mouseright:
                        self.basecamerapos = pygame.Vector2(icon.army.base_pos[0], icon.army.base_pos[1])
                        self.camerapos = self.basecamerapos * self.camerascale
                    break
        return self.clickany

    def button_mouseover(self, mouseright):
        """process user mouse input on various ui buttons"""
        for button in self.button_ui:
            if button in self.battleui and button.rect.collidepoint(self.mouse_pos):
                self.clickany = True
                self.uiclick = True  # for avoiding selecting subunit under ui
                break
        return self.clickany

    def leader_mouseover(self, mouseright):  # TODO make it so button and leader popup not show at same time
        """process user mouse input on leader portrait in command ui"""
        leadermouseover = False
        for leader in self.leadernow:
            if leader.rect.collidepoint(self.mouse_pos):
                if leader.parentunit.commander:
                    armyposition = self.leaderposname[leader.army_position]
                else:
                    armyposition = self.leaderposname[leader.army_position + 4]

                self.leader_popup.pop(self.mouse_pos, armyposition + ": " + leader.name)  # popup leader name when mouse over
                self.battleui.add(self.leader_popup)
                leadermouseover = True

                if mouseright:
                    self.popout_lorebook(8, leader.leader_id)
                break
        return leadermouseover

    def effecticon_mouseover(self, iconlist, mouseright):
        effectmouseover = False
        for icon in iconlist:
            if icon.rect.collidepoint(self.mouse_pos):
                checkvalue = self.troopcard_ui.value2[icon.icon_type]
                self.effect_popup.pop(self.mouse_pos, checkvalue[icon.game_id])
                self.battleui.add(self.effect_popup)
                effectmouseover = True
                if mouseright:
                    if icon.icon_type == 0:  # Trait
                        section = 7
                    elif icon.icon_type == 1:  # Skill
                        section = 6
                    else:
                        section = 5  # Status effect
                    self.popout_lorebook(section, icon.game_id)
                break
        return effectmouseover

    def removeunitui(self):
        self.troopcard_ui.option = 1  # reset subunit card option
        self.battleui.remove(*self.game_ui, self.troopcard_button, self.inspect_button, self.col_split_button, self.row_split_button)
        # self.ui_updater.remove(*self.game_ui, self.unitbutton)
        self.kill_effect_icon()
        self.battleui.remove(*self.switch_button, *self.inspectsubunit)  # remove change behaviour button and inspect ui subunit
        self.inspectui = False  # inspect ui close
        self.battleui.remove(*self.leadernow)  # remove leader image from command ui
        self.subunit_selected = None  # reset subunit selected
        self.battleui.remove(self.subunit_selected_border)  # remove subunit selected border sprite
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
            # self.battle_ui.add(self.button_ui[7])  # add decimation button
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
            # self.battle_ui.remove(self.button_ui[7])  # remove decimation button
            self.battleui.remove(*self.switch_button[0:7])  # remove parentunit behaviour change button

        self.leadernow = whoinput.leader
        self.battleui.add(*self.leadernow)  # add leader portrait to draw
        self.unitstat_ui.value_input(who=whoinput, split=self.splithappen)
        self.command_ui.value_input(who=whoinput, split=self.splithappen)

    def unitcardbutton_click(self, who):
        for button in self.troopcard_button:  # Change subunit card option based on button clicking
            if button.rect.collidepoint(self.mouse_pos):
                self.clickany = True
                self.uiclick = True
                if self.troopcard_ui.option != button.event:
                    self.troopcard_ui.option = button.event
                    self.troopcard_ui.value_input(who=who, weapon_list=self.allweapon,
                                                  armour_list=self.allarmour,
                                                  change_option=1, split=self.splithappen)

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
            self.mini_map.draw_image(self.showmap.true_image, self.camera)

            if self.last_selected is not None:  # any parentunit is selected
                self.last_selected = None  # reset last_selected
                self.before_selected = None  # reset before selected parentunit after remove last selected

            self.command_ui.rect = self.command_ui.image.get_rect(
                center=(self.command_ui.x, self.command_ui.y))  # change leader ui position back
            self.troopcard_ui.rect = self.troopcard_ui.image.get_rect(
                center=(self.troopcard_ui.x, self.troopcard_ui.y))  # change subunit card position back
            self.troopcard_button[0].rect = self.troopcard_button[0].image.get_rect(center=(self.troopcard_ui.x - 152, self.troopcard_ui.y + 10))
            self.troopcard_button[1].rect = self.troopcard_button[1].image.get_rect(center=(self.troopcard_ui.x - 152, self.troopcard_ui.y - 70))
            self.troopcard_button[2].rect = self.troopcard_button[2].image.get_rect(center=(self.troopcard_ui.x - 152, self.troopcard_ui.y - 30))
            self.troopcard_button[3].rect = self.troopcard_button[3].image.get_rect(center=(self.troopcard_ui.x - 152, self.troopcard_ui.y + 50))

            self.battleui.remove(self.filter_stuff, self.unitsetup_stuff, self.leadernow, self.button_ui, self.warningmsg)
            self.battleui.add(self.eventlog, self.logscroll, self.eventlog_button, self.time_button)

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
            self.mini_map.draw_image(self.showmap.true_image, self.camera)  # reset mini_map
            for arrow in self.arrows:  # remove all range attack
                arrow.kill()
                del arrow

            for unit in self.allunitlist:  # reset all unit state
                unit.command(self.battle_mouse_pos[0], False, False, self.last_mouseover, None, othercommand=2)

            self.troopcard_ui.rect = self.troopcard_ui.image.get_rect(bottomright=(self.screen_rect.width,
                                                                                   self.screen_rect.height))  # troop info card ui
            self.troopcard_button[0].rect = self.troopcard_button[0].image.get_rect(topleft=(self.troopcard_ui.rect.topleft[0],  # description button
                                                                                             self.troopcard_ui.rect.topleft[1] + 120))
            self.troopcard_button[1].rect = self.troopcard_button[1].image.get_rect(topleft=(self.troopcard_ui.rect.topleft[0],  # stat button
                                                                                             self.troopcard_ui.rect.topleft[1]))
            self.troopcard_button[2].rect = self.troopcard_button[2].image.get_rect(topleft=(self.troopcard_ui.rect.topleft[0],  # skill button
                                                                                             self.troopcard_ui.rect.topleft[1] + 40))
            self.troopcard_button[3].rect = self.troopcard_button[3].image.get_rect(topleft=(self.troopcard_ui.rect.topleft[0],  # equipment button
                                                                                             self.troopcard_ui.rect.topleft[1] + 80))

            self.battleui.remove(self.eventlog, self.logscroll, self.troopcard_button, self.col_split_button, self.row_split_button,
                                 self.eventlog_button, self.time_button, self.unitstat_ui, self.inspect_ui, self.leadernow, self.inspectsubunit,
                                 self.subunit_selected_border, self.inspect_button, self.switch_button)

            self.leadernow = [leader for leader in self.preview_leader]  # reset leader in command ui

            self.battleui.add(self.filter_stuff, self.unitsetup_stuff, self.test_button, self.command_ui, self.troopcard_ui, self.leadernow,
                              self.time_button)
            self.slotdisplay_button.event = 0  # reset display editor ui button to show
            self.gamespeed = 0  # pause battle

            for slot in self.unit_build_slot:
                if slot.troop_id != 0:
                    self.command_ui.value_input(who=slot)
                    break

        self.speednumber.speed_update(self.gamespeed)

    def exitbattle(self):
        self.battleui.clear(self.screen, self.background)  # remove all sprite
        self.battlecamera.clear(self.screen, self.background)  # remove all sprite

        self.battleui.remove(self.battle_menu, *self.battle_menu_button, *self.escslidermenu,
                             *self.escvaluebox, self.battledone_box, self.gamedone_button)  # remove menu

        for group in (self.subunit, self.army_leader, self.team0_unit, self.team1_unit, self.team2_unit,
                      self.unit_icon, self.troop_number_sprite,
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
        self.battleui.remove(self.drama_text)

        if self.mode == "uniteditor":
            self.showincard = None

            self.battleui.remove(self.unit_delete_button, self.unit_save_button, self.troop_listbox,
                                 self.teamchange_button, self.troop_scroll, self.team_coa, self.unit_listbox,
                                 self.unit_presetname_scroll, self.filter_box, self.teamchange_button,
                                 self.slotdisplay_button, self.test_button, self.deploy_button, self.troopcard_button,
                                 self.terrain_change_button, self.feature_change_button, self.weather_change_button,
                                 self.unit_build_slot, self.leadernow, self.presetselectborder,
                                 self.popup_listbox, self.popup_listscroll, *self.popup_namegroup)

            for group in self.troop_namegroup, self.unit_edit_border, self.unitpreset_namegroup:
                for item in group:  # remove name list
                    item.kill()
                    del item

            for slot in self.unit_build_slot:  # reset all sub-subunit slot
                slot.change_troop(0, self.baseterrain,
                                  self.baseterrain * len(self.battle_map_feature.feature_list) + self.featureterrain,
                                  self.currentweather)
                slot.leader = None  # remove leader link in

            for leader in self.preview_leader:
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
        self.drama_text.queue = []  # reset drama text popup queue
        if self.mode == "uniteditor":
            self.gamestate = 2  # editor mode

            self.full_troop_list = [item[0] for item in self.troop_data.troop_list.values()][1:]

            self.troop_list = self.full_troop_list  # generate troop name list
            self.troop_index_list = list(range(0, len(self.troop_list) + 1))

            self.leader_list = [item[0] for item in self.leader_stat.leader_list.values()][1:]  # generate leader name list

            setuplist(self.screen_scale, menu.NameList, self.current_unit_row, list(self.customunitpresetlist.keys()),
                           self.unitpreset_namegroup, self.unit_listbox, self.battleui)  # setup preset army list
            setuplist(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list,
                           self.troop_namegroup, self.troop_listbox, self.battleui)  # setup troop name list

            self.current_list_show = "troop"
            self.unitpresetname = ""
            self.preparestate = True
            self.baseterrain = 0
            self.featureterrain = 0
            self.weathertype = 4
            self.weatherstrength = 0
            self.currentweather = weather.Weather(self.timeui, self.weathertype, self.weatherstrength, self.all_weather)
            self.showincard = None  # current sub-subunit showing in subunit card

            self.main.make_team_coa([0], ui_class=self.battleui, one_team=True,
                                    team1_set_pos=(self.troop_listbox.rect.midleft[0] - int((200 * self.screen_scale[0]) / 2),
                                                   self.troop_listbox.rect.midleft[1]))  # default faction select as all faction

            self.troop_scroll.change_image(new_row=self.current_troop_row, log_size=len(self.troop_list))  # change troop scroll image

            for index, slot in enumerate(self.unit_build_slot):  # start with the first player subunit slot selected when enter
                if index == 0:
                    slot.selected = True
                    for border in self.unit_edit_border:
                        border.kill()
                        del border
                    self.unit_edit_border.add(battleui.SelectedSquad(slot.inspect_pos))
                    self.battleui.add(*self.unit_edit_border)
                else:  # reset all other slot
                    slot.selected = False

            self.weather_current = None  # remove weather schedule from editor test

            self.changestate()

            for name in self.unitpreset_namegroup:  # loop to change selected border position to the first in preset list
                self.presetselectborder.change_pos(name.rect.topleft)
                break

        else:  # normal battle
            self.changestate()

        self.mapscaledelay = 0  # delay for map zoom input
        self.mousetimer = 0  # This is timer for checking double mouse click, use realtime
        self.ui_timer = 0  # This is timer for ui update function, use realtime
        self.drama_timer = 0  # This is timer for combat related function, use self time (realtime * gamespeed)
        self.dt = 0  # Realtime used for in self calculation
        self.uidt = 0  # Realtime used for ui timer
        self.combattimer = 0  # This is timer for combat related function, use self time (realtime * gamespeed)
        self.last_mouseover = None  # Which subunit last mouse over
        self.speednumber.speed_update(self.gamespeed)
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
        self.weatherscreenadjust = self.screen_rect.width / self.screen_rect.height  # for weather sprite spawn position
        self.rightcorner = self.screen_rect.width - 5
        self.bottomcorner = self.screen_rect.height - 5
        self.centerscreen = [self.screen_rect.width / 2, self.screen_rect.height / 2]  # center position of the screen
        self.battle_mouse_pos = [[0, 0],
                                 [0, 0]]  # mouse position list in self not screen, the first without zoom and the second with camera zoom adjust
        self.unit_selector.current_row = 0
        # ^ End start value

        self.setup_uniticon()
        self.selectscroll.change_image(new_row=self.unit_selector.current_row)

        self.effect_updater.update(self.allunitlist, self.dt, self.camerascale)

        # self.map_def_array = []
        # self.mapunitarray = [[x[random.randint(0, 1)] if i != j else 0 for i in range(1000)] for j in range(1000)]
        pygame.mixer.music.set_endevent(self.SONG_END)  # End current music before battle start

        while True:  # self running
            self.fps_count.fps_show(self.clock)
            keypress = None
            self.mouse_pos = pygame.mouse.get_pos()  # current mouse pos based on screen
            mouse_up = False  # left click
            mouse_leftdown = False  # hold left click
            mouse_right = False  # right click
            mouse_rightdown = False  # hold right click
            double_mouse_right = False  # double right click
            mouse_scrolldown = False
            mouse_scrollup = False
            currentui_mouseover = None
            key_state = pygame.key.get_pressed()
            esc_press = False
            self.uiclick = False  # reset mouse check on ui, if stay false it mean mouse click is not on any ui

            self.battleui.clear(self.screen, self.background)  # Clear sprite before update new one

            for event in pygame.event.get():  # get event that happen
                if event.type == QUIT:  # quit self
                    self.textinputpopup = ("confirm_input", "quit")
                    self.confirmui.change_instruction("Quit Game?")
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
                        self.input_box.user_input(event)
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
                        esc_press = False  # reset esc press so it not stop esc menu when open

                if self.gamestate in (1, 2):  # self in battle state
                    # v register user input during gameplay
                    if mouse_scrollup or mouse_scrolldown:  # Mouse scroll
                        if self.eventlog.rect.collidepoint(self.mouse_pos):  # Scrolling when mouse at event log
                            self.eventlog.current_start_row += rowchange
                            if mouse_scrollup:
                                if self.eventlog.current_start_row < 0:  # can go no further than the first log
                                    self.eventlog.current_start_row = 0
                                else:
                                    self.eventlog.recreate_image()  # recreate eventlog image
                                    self.logscroll.change_image(new_row=self.eventlog.current_start_row)
                            elif mouse_scrolldown:
                                if self.eventlog.current_start_row + self.eventlog.max_row_show - 1 < self.eventlog.len_check and \
                                        self.eventlog.len_check > 9:
                                    self.eventlog.recreate_image()
                                    self.logscroll.change_image(new_row=self.eventlog.current_start_row)
                                else:
                                    self.eventlog.current_start_row -= 1

                        elif self.unit_selector.rect.collidepoint(self.mouse_pos):  # Scrolling when mouse at unit selector ui
                            self.unit_selector.current_row += rowchange
                            if mouse_scrollup:
                                if self.unit_selector.current_row < 0:
                                    self.unit_selector.current_row = 0
                                else:
                                    self.setup_uniticon()
                                    self.selectscroll.change_image(new_row=self.unit_selector.current_row)
                            elif mouse_scrolldown:
                                if self.unit_selector.current_row < self.unit_selector.log_size:
                                    self.setup_uniticon()
                                    self.selectscroll.change_image(new_row=self.unit_selector.current_row)
                                else:
                                    self.unit_selector.current_row -= 1
                                    if self.unit_selector.current_row < 0:
                                        self.unit_selector.current_row = 0

                        elif self.popup_listbox in self.battleui:  # mouse scroll on popup list
                            if self.popup_listbox.type == "terrain":
                                self.currentpopuprow = list_scroll(mouse_scrollup, mouse_scrolldown, self.popup_listscroll,
                                                                   self.popup_listbox,
                                                                   self.currentpopuprow, self.battle_map_base.terrain_list,
                                                                   self.popup_namegroup, self.battleui)
                            elif self.popup_listbox.type == "feature":
                                self.currentpopuprow = list_scroll(mouse_scrollup, mouse_scrolldown, self.popup_listscroll,
                                                                   self.popup_listbox,
                                                                   self.currentpopuprow, self.battle_map_feature.feature_list,
                                                                   self.popup_namegroup, self.battleui)
                            elif self.popup_listbox.type == "weather":
                                self.currentpopuprow = (mouse_scrollup, mouse_scrolldown, self.popup_listscroll,
                                                                             self.popup_listbox, self.currentpopuprow, self.weather_list,
                                                                             self.popup_namegroup, self.battleui)
                            elif self.popup_listbox.type == "leader":
                                self.currentpopuprow = list_scroll(mouse_scrollup, mouse_scrolldown, self.popup_listscroll,
                                                                             self.popup_listbox, self.currentpopuprow, self.leader_list,
                                                                             self.popup_namegroup, self.battleui, layer=19)

                        elif self.unit_listbox.rect.collidepoint(self.mouse_pos):  # mouse scroll on unit preset list
                            self.current_unit_row = list_scroll(mouse_scrollup, mouse_scrolldown, self.unit_presetname_scroll,
                                                                          self.unit_listbox,
                                                                          self.current_unit_row, list(self.customunitpresetlist.keys()),
                                                                          self.unitpreset_namegroup, self.battleui)
                        elif self.troop_listbox.rect.collidepoint(self.mouse_pos):
                            if self.current_list_show == "troop":  # mouse scroll on troop list
                                self.current_troop_row = list_scroll(mouse_scrollup, mouse_scrolldown, self.troop_scroll, self.troop_listbox,
                                                                               self.current_troop_row, self.troop_list,
                                                                               self.troop_namegroup, self.battleui)
                            elif self.current_list_show == "faction":  # mouse scroll on faction list
                                self.current_troop_row = list_scroll(mouse_scrollup, mouse_scrolldown, self.troop_scroll, self.troop_listbox,
                                                                               self.current_troop_row, self.faction_list,
                                                                               self.troop_namegroup, self.battleui)

                        elif self.mapscaledelay == 0:  # Scrolling in self map to zoom
                            if mouse_scrollup:
                                self.camerascale += 1
                                if self.camerascale > 10:
                                    self.camerascale = 10
                                else:
                                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                                    self.showmap.change_scale(self.camerascale)
                                    if self.gamestate == 1:  # only have delay in battle mode
                                        self.mapscaledelay = 0.001

                            elif mouse_scrolldown:
                                self.camerascale -= 1
                                if self.camerascale < 1:
                                    self.camerascale = 1
                                else:
                                    self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                                    self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                                    self.showmap.change_scale(self.camerascale)
                                    if self.gamestate == 1:  # only have delay in battle mode
                                        self.mapscaledelay = 0.001
                    # ^ End mouse scroll input

                    # keyboard input
                    if keypress == pygame.K_TAB:
                        self.mapviewmode += 1  # change height map mode
                        if self.mapviewmode > 2:
                            self.mapviewmode = 0
                        self.showmap.change_mode(self.mapviewmode)
                        self.showmap.change_scale(self.camerascale)

                    elif keypress == pygame.K_o:  # Toggle unit number
                        if self.showtroopnumber:
                            self.showtroopnumber = False
                            self.effect_updater.remove(*self.troop_number_sprite)
                            self.battlecamera.remove(*self.troop_number_sprite)
                        else:  # speed currently pause
                            self.showtroopnumber = True
                            self.effect_updater.add(*self.troop_number_sprite)
                            self.battlecamera.add(*self.troop_number_sprite)

                    elif keypress == pygame.K_p:  # Speed Pause/unpause Button
                        if self.gamespeed >= 0.5:  #
                            self.gamespeed = 0  # pause self speed
                        else:  # speed currently pause
                            self.gamespeed = 1  # unpause self and set to speed 1
                        self.speednumber.speed_update(self.gamespeed)

                    elif keypress == pygame.K_KP_MINUS:  # reduce self speed
                        newindex = self.gamespeedset.index(self.gamespeed) - 1
                        if newindex >= 0:  # cannot reduce self speed than what is available
                            self.gamespeed = self.gamespeedset[newindex]
                        self.speednumber.speed_update(self.gamespeed)

                    elif keypress == pygame.K_KP_PLUS:  # increase self speed
                        newindex = self.gamespeedset.index(self.gamespeed) + 1
                        if newindex < len(self.gamespeedset):  # cannot increase self speed than what is available
                            self.gamespeed = self.gamespeedset[newindex]
                        self.speednumber.speed_update(self.gamespeed)

                    elif keypress == pygame.K_PAGEUP:  # Go to top of event log
                        self.eventlog.current_start_row = 0
                        self.eventlog.recreate_image()
                        self.logscroll.change_image(new_row=self.eventlog.current_start_row)

                    elif keypress == pygame.K_PAGEDOWN:  # Go to bottom of event log
                        if self.eventlog.len_check > self.eventlog.max_row_show:
                            self.eventlog.current_start_row = self.eventlog.len_check - self.eventlog.max_row_show
                            self.eventlog.recreate_image()
                            self.logscroll.change_image(new_row=self.eventlog.current_start_row)

                    elif keypress == pygame.K_SPACE and self.last_selected is not None:
                        self.last_selected.command(self.battle_mouse_pos[0], False, False, self.last_mouseover, None, othercommand=2)

                    # vv FOR DEVELOPMENT DELETE LATER
                    # elif keypress == pygame.K_1:
                    #     self.drama_text.queue.append("Hello and Welcome to update video")
                    # elif keypress == pygame.K_2:
                    #     self.drama_text.queue.append("Showcase: Just simple clarity update")
                    # elif keypress == pygame.K_3:
                    #     self.drama_text.queue.append("Before")
                    # elif keypress == pygame.K_4:
                    #     self.drama_text.queue.append("Where the hell is blue team, can only see red")
                    # elif keypress == pygame.K_5:
                    #     self.drama_text.queue.append("After")
                    # elif keypress == pygame.K_6:
                    #     self.drama_text.queue.append("Now much more clear")
                    # elif keypress == pygame.K_n and self.last_selected is not None:
                    #     if self.last_selected.team == 1:
                    #         self.last_selected.switchfaction(self.team1_unit, self.team2_unit, self.team1_pos_list, self.enactment)
                    #     else:
                    #         self.last_selected.switchfaction(self.team2_unit, self.team1_unit, self.team2_pos_list, self.enactment)
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
                    if key_state[K_s] or self.mouse_pos[1] >= self.bottomcorner:  # Camera move down
                        self.basecamerapos[1] += 4 * (
                                11 - self.camerascale)  # need "11 -" for converting cameral scale so the further zoom camera move faster
                        self.camerapos[1] = self.basecamerapos[1] * self.camerascale  # resize camera pos
                        self.camerafix()

                    elif key_state[K_w] or self.mouse_pos[1] <= 5:  # Camera move up
                        self.basecamerapos[1] -= 4 * (11 - self.camerascale)
                        self.camerapos[1] = self.basecamerapos[1] * self.camerascale
                        self.camerafix()

                    if key_state[K_a] or self.mouse_pos[0] <= 5:  # Camera move left
                        self.basecamerapos[0] -= 4 * (11 - self.camerascale)
                        self.camerapos[0] = self.basecamerapos[0] * self.camerascale
                        self.camerafix()

                    elif key_state[K_d] or self.mouse_pos[0] >= self.rightcorner:  # Camera move right
                        self.basecamerapos[0] += 4 * (11 - self.camerascale)
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

                    self.battle_mouse_pos[0] = pygame.Vector2((self.mouse_pos[0] - self.centerscreen[0]) + self.camerapos[0],
                                                              self.mouse_pos[1] - self.centerscreen[1] + self.camerapos[
                                                                  1])  # mouse pos on the map based on camera position
                    self.battle_mouse_pos[1] = self.battle_mouse_pos[0] / self.camerascale  # mouse pos on the map at current camera zoom scale

                    if self.terrain_check in self.battleui and (
                            self.terrain_check.pos != self.mouse_pos or key_state[K_s] or key_state[K_w] or key_state[K_a] or key_state[K_d]):
                        self.battleui.remove(self.terrain_check)  # remove terrain popup when move mouse or camera

                    if mouse_up or mouse_right or mouse_leftdown or mouse_rightdown:
                        if mouse_up:
                            self.clickany = False
                            self.newunitclick = False

                        if self.mini_map.rect.collidepoint(self.mouse_pos):  # mouse position on mini map
                            self.uiclick = True
                            if mouse_up:  # move self camera to position clicked on mini map
                                self.clickany = True
                                posmask = pygame.Vector2(int(self.mouse_pos[0] - self.mini_map.rect.x), int(self.mouse_pos[1] - self.mini_map.rect.y))
                                self.basecamerapos = posmask * 5
                                self.camerapos = self.basecamerapos * self.camerascale
                            elif mouse_right:  # nothing happen with mouse right
                                if self.last_selected is not None:
                                    self.uiclick = True
                        elif self.selectscroll.rect.collidepoint(self.mouse_pos):  # Must check mouse collide for scroller before unit select ui
                            self.uiclick = True
                            if mouse_leftdown or mouse_up:
                                self.clickany = True
                                newrow = self.selectscroll.update(self.mouse_pos)
                                if self.unit_selector.current_row != newrow:
                                    self.unit_selector.current_row = newrow
                                    self.setup_uniticon()

                        elif self.unit_selector.rect.collidepoint(self.mouse_pos):  # check mouse collide for unit selector ui
                            if mouse_up:
                                self.clickany = True
                            self.uiclick = True
                            self.uniticon_mouseover(mouse_up, mouse_right)

                        elif self.test_button.rect.collidepoint(self.mouse_pos) and self.test_button in self.battleui:
                            self.uiclick = True
                            if mouse_up:
                                self.clickany = True
                                if self.test_button.event == 0:
                                    self.test_button.event = 1
                                    new_mode = 1

                                elif self.test_button.event == 1:
                                    self.test_button.event = 0
                                    new_mode = 2
                                self.gamestate = new_mode
                                self.changestate()

                        if self.gamestate == 1:
                            if self.logscroll.rect.collidepoint(self.mouse_pos):  # Must check mouse collide for scroller before event log ui
                                self.uiclick = True
                                if mouse_leftdown or mouse_up:
                                    self.clickany = True
                                    newrow = self.logscroll.update(self.mouse_pos)
                                    if self.eventlog.current_start_row != newrow:
                                        self.eventlog.current_start_row = newrow
                                        self.eventlog.recreate_image()

                            elif self.eventlog.rect.collidepoint(self.mouse_pos):  # check mouse collide for event log ui
                                if mouse_up:
                                    self.clickany = True
                                self.uiclick = True

                            elif self.timeui.rect.collidepoint(self.mouse_pos):  # check mouse collide for time bar ui
                                self.uiclick = True
                                if mouse_up:
                                    self.clickany = True

                                    for index, button in enumerate(self.time_button):  # Event log button and timer button click
                                        if button.rect.collidepoint(self.mouse_pos):
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
                                            self.speednumber.speed_update(self.gamespeed)
                                            break

                            elif self.ui_mouseover():  # check mouse collide for other ui
                                pass

                            elif self.button_mouseover(mouse_right):  # check mouse collide for button
                                pass

                            elif mouse_right and self.last_selected is None and self.uiclick is False:  # draw terrain popup ui when right click at map with no selected parentunit
                                if 0 <= self.battle_mouse_pos[1][0] <= 999 and \
                                        0 <= self.battle_mouse_pos[1][1] <= 999:  # not draw if pos is off the map
                                    terrainpop, featurepop = self.battle_map_feature.get_feature(self.battle_mouse_pos[1], self.battle_map_base)
                                    featurepop = self.battle_map_feature.feature_mod[featurepop]
                                    heightpop = self.battle_map_height.get_height(self.battle_mouse_pos[1])
                                    self.terrain_check.pop(self.mouse_pos, featurepop, heightpop)
                                    self.battleui.add(self.terrain_check)

                            elif self.uiclick is False:
                                for index, button in enumerate(self.eventlog_button):  # Event log button and timer button click
                                    if button.rect.collidepoint(self.mouse_pos):
                                        if index in (0, 1, 2, 3, 4, 5):  # eventlog button
                                            self.uiclick = True
                                            if mouse_up:
                                                if button.event in (0, 1, 2, 3):  # change tab mode
                                                    self.eventlog.change_mode(button.event)
                                                elif button.event == 4:  # delete tab log button
                                                    self.eventlog.clear_tab()
                                                elif button.event == 5:  # delete all tab log button
                                                    self.eventlog.clear_tab(all_tab=True)
                                        break

                            # v code that only run when any unit is selected
                            if self.last_selected is not None and self.last_selected.state != 100:
                                if self.inspect_button.rect.collidepoint(self.mouse_pos) or (
                                        mouse_up and self.inspectui and self.newunitclick):  # click on inspect ui open/close button
                                    if self.inspect_button.rect.collidepoint(self.mouse_pos):
                                        self.button_name_popup.pop(self.mouse_pos, "Inspect Subunit")
                                        self.battleui.add(self.button_name_popup)
                                        if mouse_right:
                                            self.uiclick = True  # for some reason the loop mouse check above does not work for inspect button, so it here instead
                                    if mouse_up:
                                        if self.inspectui is False:  # Add unit inspect ui when left click at ui button or when change subunit with inspect open
                                            self.inspectui = True
                                            self.battleui.add(*self.troopcard_button,
                                                              self.troopcard_ui, self.inspect_ui)
                                            self.subunit_selected = None

                                            for index, subunit in enumerate(self.last_selected.subunit_sprite_array.flat):
                                                if subunit is not None:
                                                    self.inspectsubunit[index].add_subunit(subunit)
                                                    self.battleui.add(self.inspectsubunit[index])
                                                    if self.subunit_selected is None:
                                                        self.subunit_selected = self.inspectsubunit[index]

                                            self.subunit_selected_border.pop(self.subunit_selected.pos)
                                            self.battleui.add(self.subunit_selected_border)
                                            self.troopcard_ui.value_input(who=self.subunit_selected.who, weapon_list=self.allweapon,
                                                                          armour_list=self.allarmour,
                                                                          split=self.splithappen)

                                            if self.troopcard_ui.option == 2:  # blit skill icon is previous mode is skill
                                                self.traitskillblit()
                                                self.effecticonblit()
                                                self.countdownskillicon()

                                        elif self.inspectui:  # Remove when click again and the ui already open
                                            self.battleui.remove(*self.inspectsubunit, self.subunit_selected_border, self.troopcard_button,
                                                                 self.troopcard_ui, self.inspect_ui)
                                            self.inspectui = False
                                            self.newunitclick = False

                                elif self.command_ui in self.battleui and (
                                        self.command_ui.rect.collidepoint(self.mouse_pos) or keypress is not None):  # mouse position on command ui
                                    if self.last_selected.control:
                                        if self.switch_button[0].rect.collidepoint(self.mouse_pos) or keypress == pygame.K_g:
                                            if mouse_up or keypress == pygame.K_g:  # rotate skill condition when clicked
                                                self.last_selected.skill_cond += 1
                                                if self.last_selected.skill_cond > 3:
                                                    self.last_selected.skill_cond = 0
                                                self.switch_button[0].event = self.last_selected.skill_cond
                                            if self.switch_button[0].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                poptext = ("Free Skill Use", "Conserve 50% Stamina", "Conserve 25% stamina", "Forbid Skill")
                                                self.button_name_popup.pop(self.mouse_pos, poptext[self.switch_button[0].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.switch_button[1].rect.collidepoint(self.mouse_pos) or keypress == pygame.K_f:
                                            if mouse_up or keypress == pygame.K_f:  # rotate fire at will condition when clicked
                                                self.last_selected.fireatwill += 1
                                                if self.last_selected.fireatwill > 1:
                                                    self.last_selected.fireatwill = 0
                                                self.switch_button[1].event = self.last_selected.fireatwill
                                            if self.switch_button[1].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                poptext = ("Fire at will", "Hold fire until order")
                                                self.button_name_popup.pop(self.mouse_pos, poptext[self.switch_button[1].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.switch_button[2].rect.collidepoint(self.mouse_pos) or keypress == pygame.K_h:
                                            if mouse_up or keypress == pygame.K_h:  # rotate hold condition when clicked
                                                self.last_selected.hold += 1
                                                if self.last_selected.hold > 2:
                                                    self.last_selected.hold = 0
                                                self.switch_button[2].event = self.last_selected.hold
                                            if self.switch_button[2].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                poptext = ("Aggressive", "Skirmish/Scout", "Hold Ground")
                                                self.button_name_popup.pop(self.mouse_pos, poptext[self.switch_button[2].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.switch_button[3].rect.collidepoint(self.mouse_pos) or keypress == pygame.K_j:
                                            if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                                self.last_selected.use_min_range += 1
                                                if self.last_selected.use_min_range > 1:
                                                    self.last_selected.use_min_range = 0
                                                self.switch_button[3].event = self.last_selected.use_min_range
                                            if self.switch_button[3].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                poptext = ("Minimum Shoot Range", "Maximum Shoot range")
                                                self.button_name_popup.pop(self.mouse_pos, poptext[self.switch_button[3].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.switch_button[4].rect.collidepoint(self.mouse_pos) or keypress == pygame.K_j:
                                            if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                                self.last_selected.shoothow += 1
                                                if self.last_selected.shoothow > 2:
                                                    self.last_selected.shoothow = 0
                                                self.switch_button[4].event = self.last_selected.shoothow
                                            if self.switch_button[4].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                poptext = ("Both Arc and Direct Shot", "Only Arc Shot", "Only Direct Shot")
                                                self.button_name_popup.pop(self.mouse_pos, poptext[self.switch_button[4].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.switch_button[5].rect.collidepoint(self.mouse_pos) or keypress == pygame.K_j:
                                            if mouse_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                                self.last_selected.runtoggle += 1
                                                if self.last_selected.runtoggle > 1:
                                                    self.last_selected.runtoggle = 0
                                                self.switch_button[5].event = self.last_selected.runtoggle
                                            if self.switch_button[5].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                poptext = ("Toggle Walk", "Toggle Run")
                                                self.button_name_popup.pop(self.mouse_pos, poptext[self.switch_button[5].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.switch_button[6].rect.collidepoint(self.mouse_pos):  # or keypress == pygame.K_j
                                            if mouse_up:  # or keypress == pygame.K_j  # rotate min range condition when clicked
                                                self.last_selected.attackmode += 1
                                                if self.last_selected.attackmode > 2:
                                                    self.last_selected.attackmode = 0
                                                self.switch_button[6].event = self.last_selected.attackmode
                                            if self.switch_button[6].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                poptext = ("Frontline Attack Only", "Keep Formation", "All Out Attack")
                                                self.button_name_popup.pop(self.mouse_pos, poptext[self.switch_button[6].event])
                                                self.battleui.add(self.button_name_popup)

                                        elif self.col_split_button in self.battleui and self.col_split_button.rect.collidepoint(self.mouse_pos):
                                            self.button_name_popup.pop(self.mouse_pos, "Split By Middle Column")
                                            self.battleui.add(self.button_name_popup)
                                            if mouse_up and self.last_selected.state != 10:
                                                self.splitunit(self.last_selected, 1)
                                                self.splithappen = True
                                                self.checksplit(self.last_selected)
                                                self.battleui.remove(*self.leadernow)
                                                self.leadernow = self.last_selected.leader
                                                self.battleui.add(*self.leadernow)
                                                self.setup_uniticon()

                                        elif self.row_split_button in self.battleui and self.row_split_button.rect.collidepoint(self.mouse_pos):
                                            self.button_name_popup.pop(self.mouse_pos, "Split by Middle Row")
                                            self.battleui.add(self.button_name_popup)
                                            if mouse_up and self.last_selected.state != 10:
                                                self.splitunit(self.last_selected, 0)
                                                self.splithappen = True
                                                self.checksplit(self.last_selected)
                                                self.battleui.remove(*self.leadernow)
                                                self.leadernow = self.last_selected.leader
                                                self.battleui.add(*self.leadernow)
                                                self.setup_uniticon()

                                        # elif self.button_ui[7].rect.collidepoint(self.mouse_pos):  # decimation effect
                                        #     self.button_name_popup.pop(self.mouse_pos, "Decimation")
                                        #     self.battle_ui.add(self.button_name_popup)
                                        #     if mouse_left_up and self.last_selected.state == 0:
                                        #         for subunit in self.last_selected.subunit_sprite:
                                        #             subunit.status_effect[98] = self.troop_data.status_list[98].copy()
                                        #             subunit.unit_health -= round(subunit.unit_health * 0.1)
                                    if self.leader_mouseover(mouse_right):
                                        self.battleui.remove(self.button_name_popup)
                                        pass
                                else:
                                    self.battleui.remove(self.leader_popup)  # remove leader name popup if no mouseover on any button
                                    self.battleui.remove(self.button_name_popup)  # remove popup if no mouseover on any button

                                if self.inspectui:  # if inspect ui is openned
                                    if mouse_up or mouse_right:
                                        if self.inspect_ui.rect.collidepoint(self.mouse_pos):  # if mouse pos inside unit ui when click
                                            self.clickany = True  # for avoding right click or  subunit
                                            self.uiclick = True  # for avoiding clicking subunit under ui
                                            for subunit in self.inspectsubunit:
                                                if subunit.rect.collidepoint(
                                                        self.mouse_pos) and subunit in self.battleui:  # Change showing stat to the clicked subunit one
                                                    if mouse_up:
                                                        self.subunit_selected = subunit
                                                        self.subunit_selected_border.pop(self.subunit_selected.pos)
                                                        self.eventlog.add_log(
                                                            [0, str(self.subunit_selected.who.board_pos) + " " + str(
                                                                self.subunit_selected.who.name) + " in " +
                                                             self.subunit_selected.who.parentunit.leader[0].name + "'s parentunit is selected"], [3])
                                                        self.battleui.add(self.subunit_selected_border)
                                                        self.troopcard_ui.value_input(who=self.subunit_selected.who, weapon_list=self.allweapon,
                                                                                      armour_list=self.allarmour, split=self.splithappen)

                                                        if self.troopcard_ui.option == 2:
                                                            self.traitskillblit()
                                                            self.effecticonblit()
                                                            self.countdownskillicon()
                                                        else:
                                                            self.kill_effect_icon()

                                                    elif mouse_right:
                                                        self.popout_lorebook(3, subunit.who.troop_id)
                                                    break

                                        elif self.troopcard_ui.rect.collidepoint(self.mouse_pos):  # mouse position in subunit card
                                            self.clickany = True
                                            self.uiclick = True  # for avoiding clicking subunit under ui
                                            self.unitcardbutton_click(self.subunit_selected.who)

                                    if self.troopcard_ui.option == 2:
                                        if self.effecticon_mouseover(self.skill_icon, mouse_right):
                                            pass
                                        elif self.effecticon_mouseover(self.effect_icon, mouse_right):
                                            pass
                                        else:
                                            self.battleui.remove(self.effect_popup)

                                else:
                                    self.kill_effect_icon()

                                if mouse_right and self.uiclick is False:  # Unit command
                                    self.last_selected.command(self.battle_mouse_pos[1], mouse_right, double_mouse_right,
                                                               self.last_mouseover, key_state)

                                self.before_selected = self.last_selected

                            # ^ End subunit selected code

                        elif self.gamestate == 2:  # uniteditor state
                            self.battleui.remove(self.leader_popup)
                            if self.popup_listbox in self.battleui and self.popup_listbox.type == "leader" \
                                    and self.popup_listbox.rect.collidepoint(
                                self.mouse_pos):  # this need to be at the top here to prioritise popup click
                                self.uiclick = True
                                for index, name in enumerate(self.popup_namegroup):  # change leader with the new selected one
                                    if name.rect.collidepoint(self.mouse_pos):
                                        if mouse_up and (self.showincard is not None and self.showincard.name != "None"):
                                            if self.showincard.leader is not None and \
                                                    self.leadernow[
                                                        self.showincard.leader.army_position].name != "None":  # remove old leader
                                                self.leadernow[self.showincard.leader.army_position].change_leader(1,
                                                                                                                   self.leader_stat)
                                                self.leadernow[self.showincard.leader.army_position].change_subunit(
                                                    None)

                                            trueindex = [index for index, value in
                                                         enumerate(list(self.leader_stat.leader_list.values())) if value[0] == name.name][0]
                                            trueindex = list(self.leader_stat.leader_list.keys())[trueindex]
                                            self.leadernow[self.selectleader].change_leader(trueindex, self.leader_stat)
                                            self.leadernow[self.selectleader].change_subunit(self.showincard)
                                            self.showincard.leader = self.leadernow[self.selectleader]
                                            self.previewauthority(self.leadernow,
                                                                  self.leadernow[self.selectleader].subunit.army_id)
                                            self.troopcard_ui.value_input(who=self.showincard,
                                                                          weapon_list=self.allweapon,
                                                                          armour_list=self.allarmour,
                                                                          change_option=1)
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

                            elif self.unit_listbox.rect.collidepoint(self.mouse_pos) and self.unit_listbox in self.battleui:
                                self.uiclick = True
                                for index, name in enumerate(self.unitpreset_namegroup):
                                    if name.rect.collidepoint(self.mouse_pos) and mouse_up:
                                        self.presetselectborder.change_pos(name.rect.topleft)  # change border to one selected
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
                                                    if slot.game_id == unitindex:
                                                        slot.change_troop(item, self.baseterrain,
                                                                          self.baseterrain * len(
                                                                              self.battle_map_feature.feature_list)
                                                                          + self.featureterrain, self.currentweather)
                                                        break

                                            for leaderindex, item in enumerate(leaderwholist):
                                                self.preview_leader[leaderindex].leader = None
                                                if self.preview_leader[leaderindex].subunit is not None:
                                                    self.preview_leader[leaderindex].subunit.leader = None

                                                self.preview_leader[leaderindex].change_leader(item, self.leader_stat)

                                                posindex = 0
                                                for slot in self.unit_build_slot:  # can't use gameid here as none subunit not count in position check
                                                    if posindex == leaderposlist[leaderindex]:
                                                        self.preview_leader[leaderindex].change_subunit(slot)
                                                        slot.leader = self.preview_leader[leaderindex]
                                                        break
                                                    else:
                                                        if slot.name != "None":
                                                            posindex += 1

                                            self.leadernow = [leader for leader in self.preview_leader]
                                            self.battleui.add(*self.leadernow)  # add leader portrait to draw
                                            self.showincard = slot
                                            self.command_ui.value_input(who=self.showincard)
                                            self.troopcard_ui.value_input(who=self.showincard, weapon_list=self.allweapon,
                                                                          armour_list=self.allarmour)  # update subunit card on selected subunit
                                            if self.troopcard_ui.option == 2:
                                                self.traitskillblit()
                                                self.effecticonblit()
                                                self.countdownskillicon()
                                            # self.previewauthority(self.preview_leader, 0)  # calculate authority

                                        else:  # new preset
                                            self.unitpresetname = ""
                                            for slot in self.unit_build_slot:  # reset all sub-subunit slot
                                                slot.change_troop(0, self.baseterrain,
                                                                  self.baseterrain * len(
                                                                      self.battle_map_feature.feature_list) + self.featureterrain,
                                                                  self.currentweather)
                                                slot.leader = None  # remove leader link in

                                            for leader in self.preview_leader:
                                                leader.change_subunit(None)  # remove subunit link in leader
                                                leader.change_leader(1, self.leader_stat)

                                            self.leadernow = [leader for leader in self.preview_leader]
                                            self.battleui.add(*self.leadernow)  # add leader portrait to draw
                                            self.showincard = slot
                                            self.command_ui.value_input(who=self.showincard)

                                            # self.troopcard_ui.valueinput(attacker=self.showincard, weapon_list=self.allweapon, armour_list=self.allarmour,
                                            #                       change_option=1)

                            elif self.command_ui in self.battleui and self.command_ui.rect.collidepoint(self.mouse_pos):
                                self.uiclick = True
                                for leaderindex, leader in enumerate(self.leadernow):  # loop mouse pos on leader portrait
                                    if leader.rect.collidepoint(self.mouse_pos):
                                        armyposition = self.leaderposname[leader.army_position + 4]

                                        self.leader_popup.pop(self.mouse_pos, armyposition + ": " + leader.name)  # popup leader name when mouse over
                                        self.battleui.add(self.leader_popup)

                                        if mouse_up:  # open list of leader to change leader in that slot
                                            self.selectleader = leaderindex
                                            self.popuplist_newopen(leader.rect.midright, self.leader_list, "leader")

                                        elif mouse_right:
                                            self.popout_lorebook(8, leader.leader_id)
                                        break

                            elif self.troopcard_ui.rect.collidepoint(self.mouse_pos):
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
                                            self.battleui.remove(self.effect_popup)

                            elif mouse_up or mouse_leftdown or mouse_right:  # left click for select, hold left mouse for scrolling, right click for encyclopedia
                                if mouse_up or mouse_leftdown:
                                    if self.popup_listbox in self.battleui:
                                        if self.popup_listbox.rect.collidepoint(self.mouse_pos):
                                            self.uiclick = True
                                            for index, name in enumerate(self.popup_namegroup):
                                                if name.rect.collidepoint(self.mouse_pos) and mouse_up:  # click on name in list
                                                    if self.popup_listbox.type == "terrain":
                                                        self.terrain_change_button.changetext(self.battle_map_base.terrain_list[index])
                                                        self.baseterrain = index
                                                        self.editor_map_change(map.terrain_colour[self.baseterrain],
                                                                               map.feature_colour[self.featureterrain])

                                                    elif self.popup_listbox.type == "feature":
                                                        self.feature_change_button.changetext(self.battle_map_feature.feature_list[index])
                                                        self.featureterrain = index
                                                        self.editor_map_change(map.terrain_colour[self.baseterrain],
                                                                               map.feature_colour[self.featureterrain])

                                                    elif self.popup_listbox.type == "weather":
                                                        self.weathertype = int(index / 3)
                                                        self.weatherstrength = index - (self.weathertype * 3)
                                                        self.weather_change_button.changetext(self.weather_list[index])
                                                        del self.currentweather
                                                        self.currentweather = weather.Weather(self.timeui, self.weathertype + 1,
                                                                                              self.weatherstrength, self.all_weather)

                                                    for slot in self.unit_build_slot:  # reset all troop stat
                                                        slot.change_troop(slot.troop_id, self.baseterrain,
                                                                          self.baseterrain * len(
                                                                              self.battle_map_feature.feature_list) + self.featureterrain,
                                                                          self.currentweather)
                                                    if self.showincard is not None:  # reset subunit card as well
                                                        self.command_ui.value_input(who=self.showincard)
                                                        self.troopcard_ui.value_input(who=self.showincard, weapon_list=self.allweapon,
                                                                                      armour_list=self.allarmour,
                                                                                      change_option=1)
                                                        if self.troopcard_ui.option == 2:
                                                            self.traitskillblit()
                                                            self.effecticonblit()
                                                            self.countdownskillicon()

                                                    for thisname in self.popup_namegroup:  # remove troop name list
                                                        thisname.kill()
                                                        del thisname

                                                    self.battleui.remove(self.popup_listbox, self.popup_listscroll)
                                                    break

                                        elif self.popup_listscroll.rect.collidepoint(self.mouse_pos):  # scrolling on list
                                            self.uiclick = True
                                            self.currentpopuprow = self.popup_listscroll.update(
                                                self.mouse_pos)  # update the scroller and get new current subsection
                                            if self.popup_listbox.type == "terrain":
                                                setuplist(self.screen_scale, menu.NameList, self.currentpopuprow, self.battle_map_base.terrain_list,
                                                          self.popup_namegroup, self.popup_listbox, self.battleui, layer=17)
                                            elif self.popup_listbox.type == "feature":
                                                setuplist(self.screen_scale, menu.NameList, self.currentpopuprow, self.battle_map_feature.feature_list,
                                                          self.popup_namegroup, self.popup_listbox, self.battleui, layer=17)
                                            elif self.popup_listbox.type == "weather":
                                                setuplist(self.screen_scale, menu.NameList, self.currentpopuprow, self.weather_list,
                                                               self.popup_namegroup,
                                                               self.popup_listbox, self.battleui, layer=17)
                                            elif self.popup_listbox.type == "leader":
                                                setuplist(self.screen_scale, menu.NameList, self.currentpopuprow, self.leader_list,
                                                               self.popup_namegroup,
                                                               self.popup_listbox, self.battleui, layer=19)

                                        else:
                                            self.battleui.remove(self.popup_listbox, self.popup_listscroll, *self.popup_namegroup)

                                    elif self.troop_scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroller
                                        self.uiclick = True
                                        self.current_troop_row = self.troop_scroll.update(
                                            self.mouse_pos)  # update the scroller and get new current subsection
                                        if self.current_list_show == "troop":
                                            setuplist(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list, self.troop_namegroup,
                                                           self.troop_listbox, self.battleui)
                                        elif self.current_list_show == "faction":
                                            setuplist(self.screen_scale, menu.NameList, self.current_troop_row, self.faction_list, self.troop_namegroup,
                                                           self.troop_listbox, self.battleui)

                                    elif self.unit_presetname_scroll.rect.collidepoint(self.mouse_pos):
                                        self.uiclick = True
                                        self.current_unit_row = self.unit_presetname_scroll.update(
                                            self.mouse_pos)  # update the scroller and get new current subsection
                                        setuplist(self.screen_scale, menu.NameList, self.current_unit_row, list(self.customunitpresetlist.keys()),
                                                       self.unitpreset_namegroup, self.unit_listbox, self.battleui)  # setup preset army list

                                    elif self.unit_build_slot in self.battleui:
                                        slotclick = None
                                        for slot in self.unit_build_slot:  # left click on any sub-subunit slot
                                            if slot.rect.collidepoint(self.mouse_pos):
                                                self.uiclick = True
                                                slotclick = slot
                                                break

                                        if slotclick is not None:
                                            if key_state[pygame.K_LSHIFT] or key_state[pygame.K_RSHIFT]:  # add all sub-subunit from the first selected
                                                firstone = None
                                                for newslot in self.unit_build_slot:
                                                    if newslot.army_id == slotclick.armyid and newslot.game_id <= slotclick.gameid:
                                                        if firstone is None and newslot.selected:  # found the previous selected sub-subunit
                                                            firstone = newslot.game_id
                                                            if slotclick.gameid <= firstone:  # cannot go backward, stop loop
                                                                break
                                                            elif slotclick.selected is False:  # forward select, acceptable
                                                                slotclick.selected = True
                                                                self.unit_edit_border.add(
                                                                    battleui.SelectedSquad(slotclick.inspposition, 5))
                                                                self.battleui.add(*self.unit_edit_border)
                                                        elif firstone is not None and newslot.game_id > firstone and newslot.selected is False:  # select from first select to clicked
                                                            newslot.selected = True
                                                            self.unit_edit_border.add(
                                                                battleui.SelectedSquad(newslot.inspect_pos, 5))
                                                            self.battleui.add(*self.unit_edit_border)

                                            elif key_state[pygame.K_LCTRL] or key_state[
                                                pygame.K_RCTRL]:  # add another selected sub-subunit with left ctrl + left mouse button
                                                if slotclick.selected is False:
                                                    slotclick.selected = True
                                                    self.unit_edit_border.add(battleui.SelectedSquad(slotclick.inspposition, 5))
                                                    self.battleui.add(*self.unit_edit_border)

                                            elif key_state[pygame.K_LALT] or key_state[pygame.K_RALT]:
                                                if slotclick.selected and len(self.unit_edit_border) > 1:
                                                    slotclick.selected = False
                                                    for border in self.unit_edit_border:
                                                        if border.pos == slotclick.inspposition:
                                                            border.kill()
                                                            del border
                                                            break

                                            else:  # select one sub-subunit by normal left click
                                                for border in self.unit_edit_border:  # remove all other border
                                                    border.kill()
                                                    del border
                                                for newslot in self.unit_build_slot:
                                                    newslot.selected = False
                                                slotclick.selected = True
                                                self.unit_edit_border.add(battleui.SelectedSquad(slotclick.inspposition, 5))
                                                self.battleui.add(*self.unit_edit_border)

                                                if slotclick.name != "None":
                                                    self.battleui.remove(*self.leadernow)
                                                    self.leadernow = [leader for leader in self.preview_leader]
                                                    self.battleui.add(*self.leadernow)  # add leader portrait to draw
                                                    self.showincard = slot
                                                    self.command_ui.value_input(who=self.showincard)
                                                    self.troopcard_ui.value_input(who=self.showincard, weapon_list=self.allweapon,
                                                                                  armour_list=self.allarmour)  # update subunit card on selected subunit
                                                    if self.troopcard_ui.option == 2:
                                                        self.traitskillblit()
                                                        self.effecticonblit()
                                                        self.countdownskillicon()

                                if mouse_up or mouse_right:
                                    if self.unit_build_slot in self.battleui and self.troop_listbox.rect.collidepoint(self.mouse_pos):
                                        self.uiclick = True
                                        for index, name in enumerate(self.troop_namegroup):
                                            if name.rect.collidepoint(self.mouse_pos):
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

                                                        setuplist(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list,
                                                                       self.troop_namegroup,
                                                                       self.troop_listbox, self.battleui)  # setup troop name list
                                                        self.troop_scroll.change_image(new_row=self.current_troop_row,
                                                                                       log_size=len(self.troop_list))  # change troop scroll image

                                                        self.main.make_team_coa([index], ui_class=self.battleui, one_team=True,
                                                                                team1_set_pos=(
                                                                                  self.troop_listbox.rect.midleft[0] - int(
                                                                                      (200 * self.screen_scale[0]) / 2),
                                                                                  self.troop_listbox.rect.midleft[1]))  # change team coa_list

                                                        self.current_list_show = "troop"

                                                    elif mouse_right:
                                                        self.popout_lorebook(2, index)

                                                elif self.current_list_show == "troop":
                                                    if mouse_up:
                                                        for slot in self.unit_build_slot:
                                                            if slot.selected:
                                                                if key_state[pygame.K_LSHIFT]:  # change all sub-subunit in army
                                                                    for newslot in self.unit_build_slot:
                                                                        if newslot.army_id == slot.army_id:
                                                                            newslot.change_troop(self.troop_index_list[
                                                                                                     index + self.current_troop_row],
                                                                                                 self.baseterrain,
                                                                                                 self.baseterrain * len(
                                                                                                     self.battle_map_feature.feature_list)
                                                                                                 + self.featureterrain,
                                                                                                 self.currentweather)

                                                                else:
                                                                    slot.change_troop(self.troop_index_list[
                                                                                          index + self.current_troop_row],
                                                                                      self.baseterrain,
                                                                                      self.baseterrain * len(
                                                                                          self.battle_map_feature.feature_list) + self.featureterrain,
                                                                                      self.currentweather)

                                                                if slot.name != "None":  # update information of subunit that just got changed
                                                                    self.battleui.remove(*self.leadernow)
                                                                    self.leadernow = [leader for leader in self.preview_leader]
                                                                    self.battleui.add(*self.leadernow)  # add leader portrait to draw
                                                                    self.showincard = slot
                                                                    self.previewauthority(self.leadernow, slot.army_id)
                                                                    self.troopcard_ui.value_input(who=self.showincard,
                                                                                                  weapon_list=self.allweapon,
                                                                                                  armour_list=self.allarmour)  # update subunit card on selected subunit
                                                                    if self.troopcard_ui.option == 2:
                                                                        self.traitskillblit()
                                                                        self.effecticonblit()
                                                                        self.countdownskillicon()
                                                                elif slot.name == "None" and slot.leader is not None:  # remove leader from none subunit if any
                                                                    slot.leader.change_leader(1, self.leader_stat)
                                                                    slot.leader.change_subunit(None)  # remove subunit link in leader
                                                                    slot.leader = None  # remove leader link in subunit
                                                                    self.previewauthority(self.leadernow, slot.army_id)
                                                        unitdict = self.convertslot_dict("test")
                                                        if unitdict is not None and unitdict['test'][-1] == "0":
                                                            self.warningmsg.warning([self.warningmsg.multifaction_warn])
                                                            self.battleui.add(self.warningmsg)

                                                    elif mouse_right:  # upen encyclopedia
                                                        self.popout_lorebook(3, self.troop_index_list[index + self.current_troop_row])
                                                break

                                    elif self.filter_box.rect.collidepoint(self.mouse_pos):
                                        self.uiclick = True
                                        if mouse_up:
                                            if self.teamchange_button.rect.collidepoint(self.mouse_pos):
                                                if self.teamchange_button.event == 0:
                                                    self.teamchange_button.event = 1

                                                elif self.teamchange_button.event == 1:
                                                    self.teamchange_button.event = 0

                                                for slot in self.unit_build_slot:
                                                    slot.team = self.teamchange_button.event + 1
                                                    slot.change_team(True)
                                                    self.command_ui.value_input(
                                                        who=slot)  # loop valueinput so it change team correctly

                                            elif self.slotdisplay_button.rect.collidepoint(self.mouse_pos):
                                                if self.slotdisplay_button.event == 0:  # hide
                                                    self.slotdisplay_button.event = 1
                                                    self.battleui.remove(self.unitsetup_stuff, self.leadernow)
                                                    self.kill_effect_icon()

                                                elif self.slotdisplay_button.event == 1:  # show
                                                    self.slotdisplay_button.event = 0
                                                    self.battleui.add(self.unitsetup_stuff, self.leadernow)

                                            elif self.deploy_button.rect.collidepoint(self.mouse_pos) and self.unit_build_slot in self.battleui:
                                                candeploy = True
                                                subunitcount = 0
                                                warninglist = []
                                                for slot in self.unit_build_slot:
                                                    if slot.troop_id != 0:
                                                        subunitcount += 1
                                                if subunitcount < 8:
                                                    candeploy = False
                                                    warninglist.append(self.warningmsg.eightsubunit_warn)
                                                if self.leadernow == [] or self.preview_leader[0].name == "None":
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
                                                            subunit_gameid = subunit.game_id
                                                        subunit_gameid = subunit_gameid + 1
                                                    for slot in self.unit_build_slot:  # just for grabing current selected team
                                                        currentpreset[self.unitpresetname] += (0, 100, 100, slot.team)
                                                        longscript.convertedit_unit(self,
                                                                                    (self.team0_unit, self.team1_unit, self.team2_unit)[slot.team],
                                                                                    currentpreset[self.unitpresetname],
                                                                                    self.teamcolour[slot.team],
                                                                                    pygame.transform.scale(
                                                                                        self.coa_list[int(currentpreset[self.unitpresetname][-1])],
                                                                                        (60, 60)), subunit_gameid)
                                                        break
                                                    self.slotdisplay_button.event = 1
                                                    self.kill_effect_icon()
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
                                                    if box in self.battleui and box.rect.collidepoint(self.mouse_pos):
                                                        if box.tick is False:
                                                            box.change_tick(True)
                                                        else:
                                                            box.change_tick(False)
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
                                                            setuplist(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list,
                                                                           self.troop_namegroup,
                                                                           self.troop_listbox, self.battleui)  # setup troop name list
                                    elif self.terrain_change_button.rect.collidepoint(self.mouse_pos) and mouse_up:  # change map terrain button
                                        self.uiclick = True
                                        self.popuplist_newopen(self.terrain_change_button.rect.midtop, self.battle_map_base.terrain_list, "terrain")

                                    elif self.feature_change_button.rect.collidepoint(self.mouse_pos) and mouse_up:  # change map feature button
                                        self.uiclick = True
                                        self.popuplist_newopen(self.feature_change_button.rect.midtop, self.battle_map_feature.feature_list, "feature")

                                    elif self.weather_change_button.rect.collidepoint(self.mouse_pos) and mouse_up:  # change map weather button
                                        self.uiclick = True
                                        self.popuplist_newopen(self.weather_change_button.rect.midtop, self.weather_list, "weather")

                                    elif self.unit_delete_button.rect.collidepoint(self.mouse_pos) and mouse_up and \
                                            self.unit_delete_button in self.battleui:  # delete preset button
                                        self.uiclick = True
                                        if self.unitpresetname == "":
                                            pass
                                        else:
                                            self.textinputpopup = ("confirm_input", "delete_preset")
                                            self.confirmui.change_instruction("Delete Selected Preset?")
                                            self.battleui.add(*self.confirmui_pop)

                                    elif self.unit_save_button.rect.collidepoint(self.mouse_pos) and mouse_up and \
                                            self.unit_save_button in self.battleui:  # save preset button
                                        self.uiclick = True
                                        self.textinputpopup = ("text_input", "save_unit")

                                        if self.unitpresetname == "":
                                            self.input_box.text_start("")
                                        else:
                                            self.input_box.text_start(self.unitpresetname)

                                        self.inputui.change_instruction("Preset Name:")
                                        self.battleui.add(*self.inputui_pop)

                                    elif self.warningmsg in self.battleui and self.warningmsg.rect.collidepoint(self.mouse_pos):
                                        self.battleui.remove(self.warningmsg)

                                    elif self.team_coa in self.battleui:
                                        for team in self.team_coa:
                                            if team.rect.collidepoint(self.mouse_pos) and mouse_up:
                                                self.uiclick = True
                                                if self.current_list_show == "troop":
                                                    self.current_troop_row = 0
                                                    setuplist(self.screen_scale, menu.NameList, self.current_troop_row, self.faction_list,
                                                                   self.troop_namegroup,
                                                                   self.troop_listbox, self.battleui)
                                                    self.troop_scroll.change_image(new_row=self.current_troop_row,
                                                                                   log_size=len(self.faction_list))  # change troop scroll image
                                                    self.current_list_show = "faction"

                    if self.last_selected is not None:
                        if self.gamestate == 1 and self.last_selected.state != 100:
                            if self.before_selected is None:  # add back the pop up ui so it get shown when click subunit with none selected before
                                self.battleui.add(self.unitstat_ui, self.command_ui)  # add leader and top ui
                                self.battleui.add(self.inspect_button)  # add inspection ui open/close button

                                self.addbehaviourui(self.last_selected)

                            elif self.before_selected != self.last_selected or self.splithappen:  # change subunit information when select other unit
                                if self.inspectui:  # change inspect ui
                                    self.newunitclick = True
                                    self.battleui.remove(*self.inspectsubunit)

                                    self.subunit_selected = None
                                    for index, subunit in enumerate(self.last_selected.subunit_sprite_array.flat):
                                        if subunit is not None:
                                            self.inspectsubunit[index].add_subunit(subunit)
                                            self.battleui.add(self.inspectsubunit[index])
                                            if self.subunit_selected is None:
                                                self.subunit_selected = self.inspectsubunit[index]

                                    self.subunit_selected_border.pop(self.subunit_selected.pos)
                                    self.battleui.add(self.subunit_selected_border)
                                    self.troopcard_ui.value_input(who=self.subunit_selected.who, weapon_list=self.allweapon, armour_list=self.allarmour,
                                                                  split=self.splithappen)
                                self.battleui.remove(*self.leadernow)

                                self.addbehaviourui(self.last_selected, elsecheck=True)

                                if self.splithappen:  # end split check
                                    self.splithappen = False

                            else:  # Update topbar and command ui value every 1.1 seconds
                                if self.ui_timer >= 1.1:
                                    self.unitstat_ui.value_input(who=self.last_selected, split=self.splithappen)
                                    self.command_ui.value_input(who=self.last_selected, split=self.splithappen)

                        elif self.gamestate == 2 and self.unit_build_slot not in self.battleui:
                            if (mouse_right or mouse_rightdown) and self.uiclick is False:  # Unit placement
                                self.last_selected.placement(self.battle_mouse_pos[1], mouse_right, mouse_rightdown, double_mouse_right)

                            if key_state[pygame.K_DELETE]:
                                for unit in self.troop_number_sprite:
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
                                del [self.team0poslist, self.team1poslist, self.team2poslist][self.last_selected.team][
                                    self.last_selected.game_id]
                                self.last_selected.delete()
                                self.last_selected.kill()
                                self.allunitlist.remove(self.last_selected)
                                self.allunitindex.remove(self.last_selected.game_id)
                                self.setup_uniticon()
                                self.last_selected = None

                    # v Update value of the clicked subunit every 1.1 second
                    if self.gamestate == 1 and self.inspectui and ((self.ui_timer >= 1.1 and self.troopcard_ui.option != 0) or
                                                                   self.before_selected != self.last_selected):
                        self.troopcard_ui.value_input(who=self.subunit_selected.who, weapon_list=self.allweapon, armour_list=self.allarmour,
                                                      split=self.splithappen)
                        if self.troopcard_ui.option == 2:  # skill and status effect card
                            self.countdownskillicon()
                            self.effecticonblit()
                            if self.before_selected != self.last_selected:  # change subunit, reset trait icon as well
                                self.traitskillblit()
                                self.countdownskillicon()
                        else:
                            self.kill_effect_icon()
                    # ^ End update value

                    # v Drama text function
                    if self.drama_timer == 0 and len(self.drama_text.queue) != 0:  # Start timer and add to allui If there is event queue
                        self.battleui.add(self.drama_text)
                        self.drama_text.process_queue()
                        self.drama_timer = 0.1
                    elif self.drama_timer > 0:
                        self.drama_text.play_animation()
                        self.drama_timer += self.uidt
                        if self.drama_timer > 3:
                            self.drama_timer = 0
                            self.battleui.remove(self.drama_text)
                    # ^ End drama

                    if self.dt > 0:
                        self.team_troopnumber = [1, 1, 1]  # reset troop count

                        # v Event log timer
                        if self.eventschedule is not None and self.eventlist != [] and self.timenumber.time_number >= self.eventschedule:
                            self.eventlog.add_log(None, None, event_id=self.eventmapid)
                            for event in self.eventlog.map_event:
                                if self.eventlog.map_event[event][3] is not None and self.eventlog.map_event[event][3] > self.timenumber.time_number:
                                    self.eventmapid = event
                                    self.eventschedule = self.eventlog.map_event[event][3]
                                    break
                            self.eventlist = self.eventlist[1:]
                        # ^ End event log timer

                        # v Weather system
                        if self.weather_current is not None and self.timenumber.time_number >= self.weather_current:
                            del self.currentweather
                            this_weather = self.weather_event[0]

                            if this_weather[0] != 0:
                                self.currentweather = weather.Weather(self.timeui, this_weather[0], this_weather[2], self.all_weather)
                            else:  # Random weather
                                self.currentweather = weather.Weather(self.timeui, random.randint(0, 11), random.randint(0, 2),
                                                                      self.all_weather)
                            self.weather_event.pop(0)
                            self.showmap.add_effect(self.battle_map_height,
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
                                truepos = (random.randint(10, self.screen_rect.width), 0)  # starting pos
                                target = (truepos[0], self.screen_rect.height)  # final base_target pos

                                if self.currentweather.spawnangle == 225:  # top right to bottom left movement
                                    startpos = random.randint(10, self.screen_rect.width * 2)  # starting x pos that can be higher than screen width
                                    truepos = (startpos, 0)
                                    if startpos >= self.screen_rect.width:  # x higher than screen width will spawn on the right corner of screen but not at top
                                        startpos = self.screen_rect.width  # revert x back to screen width
                                        truepos = (startpos, random.randint(0, self.screen_rect.height))

                                    if truepos[1] > 0:  # start position simulate from beyond top right of screen
                                        target = (truepos[1] * self.weatherscreenadjust, self.screen_rect.height)
                                    elif truepos[0] < self.screen_rect.width:  # start position inside screen width
                                        target = (0, truepos[0] / self.weatherscreenadjust)

                                elif self.currentweather.spawnangle == 270:  # right to left movement
                                    truepos = (self.screen_rect.width, random.randint(0, self.screen_rect.height))
                                    target = (0, truepos[1])

                                randompic = random.randint(0, len(self.weather_matter_imgs[self.currentweather.weathertype]) - 1)
                                self.weathermatter.add(weather.Mattersprite(truepos, target,
                                                                            self.currentweather.speed,
                                                                            self.weather_matter_imgs[self.currentweather.weathertype][
                                                                                randompic]))
                        # ^ End weather system

                        # v Music System
                        if len(self.music_schedule) > 0 and self.timenumber.time_number >= self.music_schedule[0]:
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

                        self.subunitposarray = self.map_move_array.copy()
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
                            if self.gamestate == 2 and self.slotdisplay_button.event == 0:  # add back ui again for when unit editor ui displayed
                                self.battleui.add(self.unitsetup_stuff, self.leadernow)
                    # ^ End remove

                    if self.ui_timer > 1:
                        self.scaleui.change_fight_scale(self.team_troopnumber)  # change fight colour scale on time_ui bar
                        self.last_team_troopnumber = self.team_troopnumber

                    if self.combattimer >= 0.5:  # reset combat timer every 0.5 seconds
                        self.combattimer -= 0.5  # not reset to 0 because higher speed can cause inconsistency in update timing

                    self.effect_updater.update(self.subunit, self.dt, self.camerascale)
                    self.weather_updater.update(self.dt, self.timenumber.time_number)
                    self.mini_map.update(self.camerascale, [self.camerapos, self.cameraupcorner], self.team1poslist, self.team2poslist)

                    self.ui_updater.update()  # update ui
                    self.camera.update(self.camerapos, self.battlecamera, self.camerascale)
                    # ^ End battle updater

                    # v Update self time
                    self.dt = self.clock.get_time() / 1000  # dt before gamespeed
                    if self.ui_timer >= 1.1:  # reset ui timer every 1.1 seconds
                        self.ui_timer -= 1.1
                    self.ui_timer += self.dt  # ui update by real time instead of self time to reduce workload
                    self.uidt = self.dt  # get ui timer before apply self

                    self.dt = self.dt * self.gamespeed  # apply dt with gamespeed for ingame calculation
                    if self.dt > 0.1:
                        self.dt = 0.1  # make it so stutter does not cause sprite to clip other sprite especially when zoom change

                    self.combattimer += self.dt  # update combat timer
                    self.timenumber.timerupdate(self.dt * 10)  # update ingame time with 5x speed

                    if self.mode == "battle" and (len(self.team1_unit) <= 0 or len(self.team2_unit) <= 0):
                        if self.battledone_box not in self.battleui:
                            if len(self.team1_unit) <= 0 and len(self.team2_unit) <= 0:
                                teamwin = 0  # draw
                            elif len(self.team2_unit) <= 0:
                                teamwin = 1
                            else:
                                teamwin = 2
                            if teamwin != 0:
                                for index, coa in enumerate(self.team_coa):
                                    if index == teamwin - 1:
                                        self.battledone_box.pop(coa.name)
                                        break
                            else:
                                self.battledone_box.pop("Draw")
                            self.gamedone_button.rect = self.gamedone_button.image.get_rect(midtop=self.gamedone_button.pos)
                            self.battleui.add(self.battledone_box, self.gamedone_button)
                        else:
                            if mouse_up and self.gamedone_button.rect.collidepoint(self.mouse_pos):
                                self.gamestate = 3  # end battle mode, result screen
                                self.gamespeed = 0
                                coalist = [None, None]
                                for index, coa in enumerate(self.team_coa):
                                    coalist[index] = coa.image
                                self.battledone_box.show_result(coalist[0], coalist[1], [self.start_troopnumber, self.team_troopnumber,
                                                                                         self.wound_troopnumber, self.death_troopnumber,
                                                                                         self.flee_troopnumber, self.capture_troopnumber])
                                self.gamedone_button.rect = self.gamedone_button.image.get_rect(center=(self.battledone_box.rect.midbottom[0],
                                                                                                        self.battledone_box.rect.midbottom[1] / 1.3))

                        # print('end', self.team_troopnumber, self.last_team_troopnumber, self.start_troopnumber, self.wound_troopnumber,
                        #       self.death_troopnumber, self.flee_troopnumber, self.capture_troopnumber)
                    # ^ End update self time

                elif self.gamestate == 0:  # Complete self pause when open either esc menu or enclycopedia
                    command = self.escmenu_process(mouse_up, mouse_leftdown, esc_press, mouse_scrollup, mouse_scrolldown, self.battleui)
                    if command == "end_battle":
                        return

            elif self.textinputpopup != (None, None):  # currently have input text pop up on screen, stop everything else until done
                for button in self.input_button:
                    button.update(self.mouse_pos, mouse_up, mouse_leftdown, "any")

                if self.input_ok_button.event:
                    self.input_ok_button.event = False

                    if self.textinputpopup[1] == "save_unit":
                        currentpreset = self.convertslot_dict(self.input_box.text)
                        if currentpreset is not None:
                            self.customunitpresetlist.update(currentpreset)

                            self.unitpresetname = self.input_box.text
                            setuplist(self.screen_scale, menu.NameList, self.current_unit_row, list(self.customunitpresetlist.keys()),
                                           self.unitpreset_namegroup, self.unit_listbox, self.battleui)  # setup preset unit list
                            for name in self.unitpreset_namegroup:  # loop to change selected border position to the last in preset list
                                if name.name == self.unitpresetname:
                                    self.presetselectborder.change_pos(name.rect.topleft)
                                    break

                            self.save_preset()
                        else:
                            self.warningmsg.warning([self.warningmsg.eightsubunit_warn])
                            self.battleui.add(self.warningmsg)

                    elif self.textinputpopup[1] == "delete_preset":
                        del self.customunitpresetlist[self.unitpresetname]
                        self.unitpresetname = ""
                        setuplist(self.screen_scale, menu.NameList, self.current_unit_row, list(self.customunitpresetlist.keys()),
                                       self.unitpreset_namegroup, self.unit_listbox, self.battleui)  # setup preset unit list
                        for name in self.unitpreset_namegroup:  # loop to change selected border position to the first in preset list
                            self.presetselectborder.change_pos(name.rect.topleft)
                            break

                        self.save_preset()

                    elif self.textinputpopup[1] == "quit":
                        self.battleui.clear(self.screen, self.background)
                        self.battlecamera.clear(self.screen, self.background)
                        pygame.quit()
                        sys.exit()

                    self.input_box.text_start("")
                    self.textinputpopup = (None, None)
                    self.battleui.remove(*self.inputui_pop, *self.confirmui_pop)

                elif self.input_cancel_button.event or esc_press:
                    self.input_cancel_button.event = False
                    self.input_box.text_start("")
                    self.textinputpopup = (None, None)
                    self.battleui.remove(*self.inputui_pop, *self.confirmui_pop)

            self.screen.blit(self.camera.image, (0, 0))  # Draw the self camera and everything that appear in it
            self.battleui.draw(self.screen)  # Draw the UI
            pygame.display.update()  # update self display, draw everything
            self.clock.tick(60)  # clock update even if self pause
