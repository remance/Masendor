import csv
import datetime
import glob
import os
import random
import sys

import numpy as np
import pygame
import pygame.freetype
from gamescript import camera, map, weather, battleui, commonscript, menu, escmenu, subunit, unit, leader
from gamescript.tactical import longscript
from pygame.locals import *
from scipy.spatial import KDTree

load_image = commonscript.load_image
load_images = commonscript.load_images
csv_read = commonscript.csv_read
load_sound = commonscript.load_sound
editconfig = commonscript.edit_config
setup_list = commonscript.setup_list
list_scroll = commonscript.list_scroll


class Battle:
    splitunit = longscript.splitunit
    trait_skill_blit = commonscript.trait_skill_blit
    effect_icon_blit = commonscript.effect_icon_blit
    countdown_skill_icon = commonscript.countdown_skill_icon
    kill_effect_icon = commonscript.kill_effect_icon
    popout_lorebook = commonscript.popout_lorebook
    popup_list_newopen = commonscript.popup_list_open
    escmenu_process = escmenu.escmenu_process

    def __init__(self, main, winstyle):
        # v Get self object/variable from gamestart
        self.mode = None  # battle map mode can be "uniteditor" for unit editor or "battle" for self battle
        self.main = main
        self.genre = main.genre
        self.config = main.config
        self.mixer_volume = main.mixer_volume
        self.screen_rect = main.screen_rect
        self.team_colour = main.team_colour
        self.main_dir = main.main_dir
        self.screen_scale = main.screen_scale
        self.eventlog = main.eventlog
        self.battle_camera = main.battle_camera
        self.battle_ui = main.battle_ui

        self.unit_updater = main.unit_updater
        self.subunit_updater = main.subunit_updater
        self.leader_updater = main.leader_updater
        self.ui_updater = main.ui_updater
        self.weather_updater = main.weather_updater
        self.effect_updater = main.effect_updater

        self.battle_map_base = main.battle_base_map
        self.battle_map_feature = main.battle_feature_map
        self.battle_map_height = main.battle_height_map
        self.show_map = main.show_map

        self.team0_unit = main.team0_unit
        self.team1_unit = main.team1_unit
        self.team2_unit = main.team2_unit
        self.team0_subunit = main.team0_subunit
        self.team1_subunit = main.team1_subunit
        self.team2_subunit = main.team2_subunit
        self.subunit = main.subunit
        self.army_leader = main.army_leader

        self.range_attacks = main.range_attacks
        self.direction_arrows = main.direction_arrows
        self.troop_number_sprite = main.troop_number_sprite

        self.game_ui = main.game_ui
        self.inspect_ui_pos = main.inspect_ui_pos
        self.inspect_subunit = main.inspect_subunit

        self.battle_map_base = main.battle_base_map
        self.battle_map_feature = main.battle_feature_map
        self.battle_map_height = main.battle_height_map
        self.show_map = main.show_map

        self.mini_map = main.mini_map
        self.eventlog = main.eventlog
        self.log_scroll = main.log_scroll
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
        self.esc_option_menu_button = main.esc_option_menu_button

        self.unit_delete_button = self.main.unit_delete_button
        self.unit_save_button = self.main.unit_save_button
        self.troop_listbox = main.troop_listbox
        self.troop_namegroup = main.troop_namegroup
        self.filter_box = main.filter_box
        self.filter_tick_box = main.filter_tick_box
        self.team_change_button = main.team_change_button
        self.slot_display_button = main.slot_display_button
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
        self.preset_select_border = main.preset_select_border
        self.custom_unit_preset_list = main.custom_unit_preset_list
        self.unit_listbox = main.unit_listbox
        self.troop_scroll = main.troop_scroll
        self.faction_list = main.faction_list
        self.popup_listscroll = main.popup_listscroll
        self.team_coa = main.team_coa
        self.unit_preset_name_scroll = main.unit_preset_name_scroll
        self.warning_msg = main.warning_msg

        self.input_button = main.input_button
        self.input_box = main.input_box
        self.input_ui = main.input_ui
        self.input_ok_button = main.input_ok_button
        self.input_cancel_button = main.input_cancel_button
        self.input_ui_popup = main.input_ui_popup
        self.confirm_ui = main.confirm_ui
        self.confirm_ui_popup = main.confirm_ui_popup

        self.unit_selector = main.unit_selector
        self.unit_icon = main.unit_icon
        self.select_scroll = main.select_scroll

        self.time_ui = main.time_ui
        self.time_number = main.time_number

        self.scale_ui = main.scale_ui

        self.speed_number = main.speed_number

        self.weather_matter = main.weather_matter
        self.weather_effect = main.weather_effect

        self.encyclopedia = main.encyclopedia
        self.lore_name_list = main.lore_name_list
        self.lore_button_ui = main.lore_button_ui
        self.lore_scroll = main.lore_scroll
        self.subsection_name = main.subsection_name
        self.page_button = main.page_button

        self.all_weather = main.all_weather
        self.weather_matter_imgs = main.weather_matter_images
        self.weather_effect_imgs = main.weather_effect_images
        self.weather_list = main.weather_list

        self.feature_mod = main.feature_mod

        self.all_faction = main.all_faction
        self.coa_list = main.coa_list

        self.all_weapon = main.all_weapon
        self.all_armour = main.all_armour

        self.status_imgs = main.status_imgs
        self.role_imgs = main.role_imgs
        self.trait_imgs = main.trait_imgs
        self.skill_imgs = main.skill_imgs

        self.troop_data = main.troop_data
        self.leader_stat = main.leader_stat

        self.state_text = main.state_text

        self.sprite_width = main.sprite_width
        self.sprite_height = main.sprite_height
        self.collide_distance = self.sprite_height / 10  # distance to check collision
        self.front_distance = self.sprite_height / 20  # distance from front side
        self.full_distance = self.front_distance / 2  # distance for sprite merge check

        self.combat_path_queue = []  # queue of sub-unit to run melee combat pathfiding

        self.esc_slider_menu = main.esc_slider_menu
        self.esc_value_box = main.esc_value_box

        self.eventlog_button = main.eventlog_button
        self.time_button = main.time_button
        self.command_ui = main.command_ui
        self.troop_card_ui = main.troop_card_ui
        self.troop_card_button = main.troop_card_button
        self.inspect_ui = main.inspect_ui
        self.inspect_button = main.inspect_button
        self.col_split_button = main.col_split_button
        self.row_split_button = main.row_split_button
        self.unitstat_ui = main.unitstat_ui

        self.leader_level = main.leader_level

        self.battledone_box = main.battledone_box
        self.gamedone_button = main.gamedone_button
        # ^ End load from gamestart

        self.game_speed = 0
        self.game_speed_list = (0, 0.5, 1, 2, 4, 6)  # availabe self speed
        self.leader_now = []
        self.team_troopnumber = [1, 1, 1]  # list of troop number in each team, minimum at one because percentage can't divide by 0
        self.last_team_troopnumber = [1, 1, 1]
        self.start_troopnumber = [0, 0, 0]
        self.wound_troopnumber = [0, 0, 0]
        self.death_troopnumber = [0, 0, 0]
        self.flee_troopnumber = [0, 0, 0]
        self.capture_troopnumber = [0, 0, 0]
        self.faction_pick = 0
        self.filter_troop = [True, True, True, True]
        self.last_selected = None
        self.before_selected = None

        self.unitsetup_stuff = (self.unit_build_slot, self.unit_edit_border, self.command_ui, self.troop_card_ui,
                                self.team_coa, self.troop_card_button, self.troop_listbox, self.troop_scroll,
                                self.troop_namegroup, self.unit_listbox, self.preset_select_border,
                                self.unitpreset_namegroup, self.unit_save_button, self.unit_delete_button,
                                self.unit_preset_name_scroll)
        self.filter_stuff = (self.filter_box, self.slot_display_button, self.team_change_button, self.deploy_button, self.terrain_change_button,
                             self.feature_change_button, self.weather_change_button, self.filter_tick_box)

        self.best_depth = pygame.display.mode_ok(self.screen_rect.size, winstyle, 32)  # Set the display mode
        self.screen = pygame.display.set_mode(self.screen_rect.size, winstyle | pygame.RESIZABLE, self.best_depth)  # set up self screen

        # v Assign default variable to some class
        unit.Unit.gamebattle = self
        unit.Unit.imgsize = (self.sprite_width, self.sprite_height)
        subunit.Subunit.gamebattle = self
        leader.Leader.gamebattle = self
        # ^ End assign default

        self.background = pygame.Surface(self.screen_rect.size)  # Create background image
        self.background.fill((255, 255, 255))  # fill background image with black colour

    def editor_map_change(self, base_colour, feature_colour):
        imgs = (pygame.Surface((1000, 1000)), pygame.Surface((1000, 1000)), pygame.Surface((1000, 1000), pygame.SRCALPHA), None)
        imgs[0].fill(base_colour)  # start with temperate terrain
        imgs[1].fill(feature_colour)  # start with plain feature
        imgs[2].fill((255, 100, 100, 125))  # start with height 100 plain

        self.battle_map_base.draw_image(imgs[0])
        self.battle_map_feature.draw_image(imgs[1])
        self.battle_map_height.draw_image(imgs[2])
        self.show_map.draw_image(self.battle_map_base, self.battle_map_feature, self.battle_map_height, None, self, True)
        self.mini_map.draw_image(self.show_map.true_image, self.camera)
        self.show_map.change_scale(self.camera_scale)

    def prepare_new_game(self, ruleset, ruleset_folder, team_selected, enactment, map_selected, source, unit_scale, mode):
        """Setup stuff when start new battle"""
        self.ruleset = ruleset  # current ruleset used
        self.ruleset_folder = ruleset_folder  # the folder of rulseset used
        self.mapselected = map_selected  # map folder name
        self.source = str(source)
        self.unitscale = unit_scale
        self.playerteam = team_selected  # player selected team

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
            new_time = datetime.datetime.strptime("09:00:00", "%H:%M:%S").time()
            new_time = datetime.timedelta(hours=new_time.hour, minutes=new_time.minute, seconds=new_time.second)
            self.weather_event = [[4, new_time, 0]]  # default weather light sunny all day
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
                    new_list = []
                    for time in self.music_schedule:
                        new_event_list = []
                        for event in self.music_event:
                            if time == event[1]:
                                new_event_list.append(event[0])
                        new_list.append(new_event_list)
                    self.music_event = new_list
                else:
                    self.music_schedule = [self.weather_current]
                    self.music_event = [[5]]
            except:  # any reading error will play random custom music instead
                self.music_schedule = [self.weather_current]
                self.music_event = [[5]]  # TODO change later when has custom playlist
        # ^ End music play

        try:  # get new map event for event log
            map_event = csv_read("eventlog.csv",
                                [self.main_dir, "data", "ruleset", self.ruleset_folder, "map", self.mapselected, self.source], 0)
            battleui.EventLog.map_event = map_event
        except Exception:  # can't find any event file
            map_event = {}  # create empty list

        self.eventlog.make_new_log()  # reset old event log

        self.eventlog.add_event_log(map_event)

        self.event_schedule = None
        self.event_list = []
        for index, event in enumerate(self.eventlog.map_event):
            if self.eventlog.map_event[event][3] is not None:
                if index == 0:
                    self.event_id = event
                    self.event_schedule = self.eventlog.map_event[event][3]
                self.event_list.append(event)

        self.time_number.start_setup(self.weather_current)

        # v Create the battle map
        self.camera_pos = pygame.Vector2(500, 500)  # Camera pos at the current zoom, start at center of map
        self.base_camera_pos = pygame.Vector2(500, 500)  # Camera pos at furthest zoom for recalculate sprite pos after zoom
        self.camera_scale = 1  # Camera zoom
        camera.Camera.screen_rect = self.screen_rect
        self.camera = camera.Camera(self.camera_pos, self.camera_scale)

        if map_selected is not None:
            imgs = load_images(self.main_dir, ["ruleset", self.ruleset_folder, "map", self.mapselected], load_order=False)
            self.battle_map_base.draw_image(imgs["base.png"])
            self.battle_map_feature.draw_image(imgs["feature.png"])
            self.battle_map_height.draw_image(imgs["height.png"])

            try:  # place_name map layer is optional, if not existed in folder then assign None
                place_name_map = imgs[3]
            except Exception:
                place_name_map = None
            self.show_map.draw_image(self.battle_map_base, self.battle_map_feature, self.battle_map_height, place_name_map, self, False)
        else:  # for unit editor mode, create empty temperate glass map
            self.editor_map_change((166, 255, 107), (181, 230, 29))
        # ^ End create battle map

        self.clock = pygame.time.Clock()  # Game clock to keep track of realtime pass

        self.enactment = enactment  # enactment mod, control both team

        self.team0_pos_list = {}  # team 0 parentunit position
        self.team1_pos_list = {}  # team 1 parentunit position
        self.team2_pos_list = {}  # same for team 2

        self.all_unit_list = []  # list of every parentunit in self alive
        self.all_unit_index = []  # list of every parentunit index alive

        self.all_subunit_list = []  # list of all subunit alive in self

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
            savelist = self.custom_unit_preset_list.copy()
            del savelist["New Preset"]
            final_save = [["presetname", "subunitline1", "subunitline2", "subunitline3", "subunitline4", "subunitline5", "subunitline6",
                          "subunitline7", "subunitline8", "leader", "leaderposition", "faction"]]
            for item in list(savelist.items()):
                subitem = [smallitem for smallitem in item[1]]
                item = [item[0]] + subitem
                final_save.append(item)
            for row in final_save:
                filewriter.writerow(row)
            csvfile.close()

    def convert_slot_dict(self, name, pos=None, addid=None):
        current_preset = [[], [], [], [], [], [], [], []]
        start_item = 0
        subunit_count = 0
        for slot in self.unit_build_slot:  # add subunit troop id
            current_preset[int(start_item / 8)].append(str(slot.troop_id))
            start_item += 1
            if slot.troop_id != 0:
                subunit_count += 1
        if pos is not None:
            current_preset.append(pos)

        if subunit_count > 0:
            leader_list = []
            leader_pos_list = []
            for leader in self.preview_leader:  # add leader id
                count_zero = 0
                if leader.leader_id != 1:
                    subunit_count += 1
                    for slotindex, slot in enumerate(self.unit_build_slot):  # add subunit troop id
                        if slot.troop_id == 0:
                            count_zero += 1
                        if slotindex == leader.subunit_pos:
                            break

                leader_list.append(str(leader.leader_id))
                leader_pos_list.append(str(leader.subunit_pos - count_zero))
            current_preset.append(leader_list)
            current_preset.append(leader_pos_list)

            faction = []  # generate faction list that can use this unit
            faction_list = self.all_faction.faction_list.copy()
            del faction_list["ID"]
            del faction_list[0]
            faction_count = dict.fromkeys(faction_list.keys(), 0)  # dict of faction occurrence count

            for index, item in enumerate(current_preset):
                for this_item in item:
                    if index in range(0, 8):  # subunit
                        for faction_item in faction_list.items():
                            if int(this_item) in faction_item[1][1]:
                                faction_count[faction_item[0]] += 1
                    elif index == 8:  # leader
                        for faction_item in faction_list.items():
                            if int(this_item) < 10000 and int(this_item) in faction_item[1][2]:
                                faction_count[faction_item[0]] += 1
                            elif int(this_item) >= 10000:
                                if faction_item[0] == self.leader_stat.leader_list[int(this_item)][-2] or \
                                        self.leader_stat.leader_list[int(this_item)][-2] == 0:
                                    faction_count[faction_item[0]] += 1

            for item in faction_count.items():  # find faction of this unit
                if item[1] == faction_count[max(faction_count, key=faction_count.get)]:
                    if faction_count[max(faction_count, key=faction_count.get)] == subunit_count:
                        faction.append(item[0])
                    else:  # units from various factions, counted as multi-faction unit
                        faction = [0]
                        break
            current_preset.append(faction)

            for item_index, item in enumerate(current_preset):  # convert list to string
                if type(item) == list:
                    if len(item) > 1:
                        current_preset[item_index] = ",".join(item)
                    else:  # still type list because only one item in list
                        current_preset[item_index] = str(current_preset[item_index][0])
            if addid is not None:
                current_preset = [addid] + current_preset
            current_preset = {name: current_preset}
        else:
            current_preset = None

        return current_preset

    def preview_authority(self, leader_list, army_id):
        """Calculate authority of editted unit"""
        authority = int(
            leader_list[0].authority + (leader_list[0].authority / 2) +
            (leader_list[1].authority / 4) + (leader_list[2].authority / 4) +
            (leader_list[3].authority / 10))
        big_unit_size = len([slot for slot in self.unit_build_slot if slot.army_id == army_id and slot.name != "None"])
        if big_unit_size > 20:  # army size larger than 20 will reduce gamestart leader authority
            authority = int(leader_list[0].authority +
                            (leader_list[0].authority / 2 * (100 - big_unit_size) / 100) +
                            leader_list[1].authority / 2 + leader_list[2].authority / 2 +
                            leader_list[3].authority / 4)

        for slot in self.unit_build_slot:
            if slot.army_id == army_id:
                slot.authority = authority

        if self.show_in_card is not None:
            self.command_ui.value_input(who=self.show_in_card)
        # ^ End cal authority

    def setup_unit_icon(self):
        """Setup unit selection list in unit selector ui top left of screen"""
        row = 30
        start_column = 25
        column = start_column
        unit_list = self.team1_unit
        if self.playerteam == 2:
            unit_list = self.team2_unit
        if self.enactment:  # include another team unit icon as well in enactment mode
            unit_list = self.all_unit_list
        current_index = int(self.unit_selector.current_row * self.unit_selector.max_column_show)  # the first index of current row
        self.unit_selector.log_size = len(unit_list) / self.unit_selector.max_column_show

        if self.unit_selector.log_size.is_integer() is False:
            self.unit_selector.log_size = int(self.unit_selector.log_size) + 1

        if self.unit_selector.current_row > self.unit_selector.log_size - 1:
            self.unit_selector.current_row = self.unit_selector.log_size - 1
            current_index = int(self.unit_selector.current_row * self.unit_selector.max_column_show)
            self.select_scroll.change_image(new_row=self.unit_selector.current_row)

        if len(self.unit_icon) > 0:  # Remove all old icon first before making new list
            for icon in self.unit_icon:
                icon.kill()
                del icon

        for index, unit in enumerate(unit_list):  # add unit icon for drawing according to appopriate current row
            if index >= current_index:
                self.unit_icon.add(battleui.ArmyIcon((column, row), unit))
                column += 40
                if column > 250:
                    row += 50
                    column = start_column
                if row > 100:
                    break  # do not draw for the third row
        self.select_scroll.change_image(log_size=self.unit_selector.log_size)

    def check_split(self, who):
        """Check if unit can be splitted, if not remove splitting button"""
        # v split by middle collumn
        if np.array_split(who.armysubunit, 2, axis=1)[0].size >= 10 and np.array_split(who.armysubunit, 2, axis=1)[1].size >= 10 and \
                who.leader[1].name != "None":  # can only split if both parentunit size will be larger than 10 and second leader exist
            self.battle_ui.add(self.col_split_button)
        elif self.col_split_button in self.battle_ui:
            self.battle_ui.remove(self.col_split_button)
        # ^ End col

        # v split by middle row
        if np.array_split(who.armysubunit, 2)[0].size >= 10 and np.array_split(who.armysubunit, 2)[1].size >= 10 and \
                who.leader[1].name != "None":
            self.battle_ui.add(self.row_split_button)
        elif self.row_split_button in self.battle_ui:
            self.battle_ui.remove(self.row_split_button)

    def ui_mouseover(self):
        """mouse over ui that is not subunit card and unitbox (topbar and commandbar)"""
        for this_ui in self.game_ui:
            if this_ui in self.battle_ui and this_ui.rect.collidepoint(self.mouse_pos):
                self.click_any = True
                self.ui_click = True
                break
        return self.click_any

    def uniticon_mouseover(self, mouse_up, mouse_right):
        """process user mouse input on unit icon, left click = select, right click = go to parentunit position on map"""
        self.click_any = True
        self.ui_click = True
        if self.game_state == 1 or (self.game_state == 2 and self.unit_build_slot not in self.battle_ui):
            for icon in self.unit_icon:
                if icon.rect.collidepoint(self.mouse_pos):
                    if mouse_up:
                        self.last_selected = icon.army
                        self.last_selected.justselected = True
                        self.last_selected.selected = True

                        if self.before_selected is None:  # add back the pop up ui so it get shown when click subunit with none selected before
                            self.battle_ui.add(self.unitstat_ui, self.command_ui)  # add leader and top ui
                            self.battle_ui.add(self.inspect_button)  # add inspection ui open/close button

                            self.add_behaviour_ui(self.last_selected)

                    elif mouse_right:
                        self.base_camera_pos = pygame.Vector2(icon.army.base_pos[0], icon.army.base_pos[1])
                        self.camera_pos = self.base_camera_pos * self.camera_scale
                    break
        return self.click_any

    def button_mouseover(self, mouse_right):
        """process user mouse input on various ui buttons"""
        for button in self.button_ui:
            if button in self.battle_ui and button.rect.collidepoint(self.mouse_pos):
                self.click_any = True
                self.ui_click = True  # for avoiding selecting subunit under ui
                break
        return self.click_any

    def leader_mouseover(self, mouse_right):  # TODO make it so button and leader popup not show at same time
        """process user mouse input on leader portrait in command ui"""
        leader_mouse_over = False
        for leader in self.leader_now:
            if leader.rect.collidepoint(self.mouse_pos):
                if leader.parentunit.commander:
                    army_position = self.leader_level[leader.army_position]
                else:
                    army_position = self.leader_level[leader.army_position + 4]

                self.leader_popup.pop(self.mouse_pos, army_position + ": " + leader.name)  # popup leader name when mouse over
                self.battle_ui.add(self.leader_popup)
                leader_mouse_over = True

                if mouse_right:
                    self.popout_lorebook(8, leader.leader_id)
                break
        return leader_mouse_over

    def effect_icon_mouse_over(self, icon_list, mouse_right):
        effect_mouse_over = False
        for icon in icon_list:
            if icon.rect.collidepoint(self.mouse_pos):
                check_value = self.troop_card_ui.value2[icon.icon_type]
                self.effect_popup.pop(self.mouse_pos, check_value[icon.game_id])
                self.battle_ui.add(self.effect_popup)
                effect_mouse_over = True
                if mouse_right:
                    if icon.icon_type == 0:  # Trait
                        section = 7
                    elif icon.icon_type == 1:  # Skill
                        section = 6
                    else:
                        section = 5  # Status effect
                    self.popout_lorebook(section, icon.game_id)
                break
        return effect_mouse_over

    def remove_unit_ui(self):
        self.troop_card_ui.option = 1  # reset subunit card option
        self.battle_ui.remove(*self.game_ui, self.troop_card_button, self.inspect_button, self.col_split_button, self.row_split_button)
        # self.ui_updater.remove(*self.game_ui, self.unit_button)
        self.kill_effect_icon()
        self.battle_ui.remove(*self.switch_button, *self.inspect_subunit)  # remove change behaviour button and inspect ui subunit
        self.inspect = False  # inspect ui close
        self.battle_ui.remove(*self.leader_now)  # remove leader image from command ui
        self.subunit_selected = None  # reset subunit selected
        self.battle_ui.remove(self.subunit_selected_border)  # remove subunit selected border sprite
        self.leader_now = []  # clear leader list in command ui

    def camera_fix(self):
        if self.base_camera_pos[0] > 999:  # camera cannot go further than 999 x
            self.base_camera_pos[0] = 999
        elif self.base_camera_pos[0] < 0:  # camera cannot go less than 0 x
            self.base_camera_pos[0] = 0

        if self.base_camera_pos[1] > 999:  # same for y
            self.base_camera_pos[1] = 999
        elif self.base_camera_pos[1] < 0:
            self.base_camera_pos[1] = 0

    def add_behaviour_ui(self, who_input, else_check=False):
        if who_input.control:
            # self.battle_ui.add(self.button_ui[7])  # add decimation button
            self.battle_ui.add(*self.switch_button[0:7])  # add parentunit behaviour change button
            self.switch_button[0].event = who_input.skill_cond
            self.switch_button[1].event = who_input.fireatwill
            self.switch_button[2].event = who_input.hold
            self.switch_button[3].event = who_input.use_min_range
            self.switch_button[4].event = who_input.shoothow
            self.switch_button[5].event = who_input.runtoggle
            self.switch_button[6].event = who_input.attackmode
            self.check_split(who_input)  # check if selected parentunit can split, if yes draw button
        elif else_check:
            if self.row_split_button in self.battle_ui:
                self.row_split_button.kill()
            if self.col_split_button in self.battle_ui:
                self.col_split_button.kill()
            # self.battle_ui.remove(self.button_ui[7])  # remove decimation button
            self.battle_ui.remove(*self.switch_button[0:7])  # remove parentunit behaviour change button

        self.leader_now = who_input.leader
        self.battle_ui.add(*self.leader_now)  # add leader portrait to draw
        self.unitstat_ui.value_input(who=who_input, split=self.split_happen)
        self.command_ui.value_input(who=who_input, split=self.split_happen)

    def unitcardbutton_click(self, who):
        for button in self.troop_card_button:  # Change subunit card option based on button clicking
            if button.rect.collidepoint(self.mouse_pos):
                self.click_any = True
                self.ui_click = True
                if self.troop_card_ui.option != button.event:
                    self.troop_card_ui.option = button.event
                    self.troop_card_ui.value_input(who=who, weapon_list=self.all_weapon,
                                                   armour_list=self.all_armour,
                                                   change_option=1, split=self.split_happen)

                    if self.troop_card_ui.option == 2:
                        self.trait_skill_blit()
                        self.effect_icon_blit()
                        self.countdown_skill_icon()
                    else:
                        self.kill_effect_icon()
                break

    def filter_troop_list(self):
        """Filter troop list based on faction picked and type filter"""
        if self.faction_pick != 0:
            self.troop_list = [item[1][0] for item in self.troop_data.troop_list.items()
                               if item[1][0] == "None" or
                               item[0] in self.all_faction.faction_list[self.faction_pick][1]]
            self.troop_index_list = [0] + self.all_faction.faction_list[self.faction_pick][1]

        else:  # pick all faction
            self.troop_list = [item[0] for item in self.troop_data.troop_list.values()][1:]
            self.troop_index_list = list(range(0, len(self.troop_list)))

        for unit in self.troop_index_list[::-1]:
            if unit != 0:
                if self.filter_troop[0] is False:  # filter out melee infantry
                    if self.troop_data.troop_list[unit][8] > self.troop_data.troop_list[unit][12] and \
                            self.troop_data.troop_list[unit][29] == [1, 0, 1]:
                        self.troop_list.pop(self.troop_index_list.index(unit))
                        self.troop_index_list.remove(unit)

                if self.filter_troop[1] is False:  # filter out range infantry
                    if self.troop_data.troop_list[unit][22] != [1, 0] and \
                            self.troop_data.troop_list[unit][8] < self.troop_data.troop_list[unit][12] and \
                            self.troop_data.troop_list[unit][29] == [1, 0, 1]:
                        self.troop_list.pop(self.troop_index_list.index(unit))
                        self.troop_index_list.remove(unit)

                if self.filter_troop[2] is False:  # filter out melee cav
                    if self.troop_data.troop_list[unit][8] > self.troop_data.troop_list[unit][12] and \
                            self.troop_data.troop_list[unit][29] != [1, 0, 1]:
                        self.troop_list.pop(self.troop_index_list.index(unit))
                        self.troop_index_list.remove(unit)

                if self.filter_troop[3] is False:  # filter out range cav
                    if self.troop_data.troop_list[unit][22] != [1, 0] and \
                            self.troop_data.troop_list[unit][8] < self.troop_data.troop_list[unit][12] and \
                            self.troop_data.troop_list[unit][29] != [1, 0, 1]:
                        self.troop_list.pop(self.troop_index_list.index(unit))
                        self.troop_index_list.remove(unit)

    def change_state(self):
        self.previous_gamestate = self.game_state
        if self.game_state == 1:  # change to battle state
            self.mini_map.draw_image(self.show_map.true_image, self.camera)

            if self.last_selected is not None:  # any parentunit is selected
                self.last_selected = None  # reset last_selected
                self.before_selected = None  # reset before selected parentunit after remove last selected

            self.command_ui.rect = self.command_ui.image.get_rect(
                center=self.command_ui.pos)  # change leader ui position back
            self.troop_card_ui.rect = self.troop_card_ui.image.get_rect(
                center=self.troop_card_ui.pos)  # change subunit card position back
            self.troop_card_button[0].rect = self.troop_card_button[0].image.get_rect(center=(self.troop_card_ui.pos[0] - 152, self.troop_card_ui.pos[1] + 10))
            self.troop_card_button[1].rect = self.troop_card_button[1].image.get_rect(center=(self.troop_card_ui.pos[0] - 152, self.troop_card_ui.pos[1] - 70))
            self.troop_card_button[2].rect = self.troop_card_button[2].image.get_rect(center=(self.troop_card_ui.pos[0] - 152, self.troop_card_ui.pos[1] - 30))
            self.troop_card_button[3].rect = self.troop_card_button[3].image.get_rect(center=(self.troop_card_ui.pos[0] - 152, self.troop_card_ui.pos[1] + 50))

            self.battle_ui.remove(self.filter_stuff, self.unitsetup_stuff, self.leader_now, self.button_ui, self.warning_msg)
            self.battle_ui.add(self.eventlog, self.log_scroll, self.eventlog_button, self.time_button)

            self.game_speed = 1

            # v Run starting function
            for unit in self.all_unit_list:
                unit.startset(self.subunit)
            for subunit in self.subunit:
                subunit.gamestart(self.camera_scale)
            for leader in self.leader_updater:
                leader.gamestart()
            # ^ End starting

        elif self.game_state == 2:  # change to editor state
            self.inspect = False  # reset inspect ui
            self.mini_map.draw_image(self.show_map.true_image, self.camera)  # reset mini_map
            for arrow in self.range_attacks:  # remove all range attack
                arrow.kill()
                del arrow

            for unit in self.all_unit_list:  # reset all unit state
                unit.command(self.battle_mouse_pos[0], False, False, self.last_mouseover, None, othercommand=2)

            self.troop_card_ui.rect = self.troop_card_ui.image.get_rect(bottomright=(self.screen_rect.width,
                                                                                     self.screen_rect.height))  # troop info card ui
            self.troop_card_button[0].rect = self.troop_card_button[0].image.get_rect(topleft=(self.troop_card_ui.rect.topleft[0],  # description button
                                                                                               self.troop_card_ui.rect.topleft[1] + 120))
            self.troop_card_button[1].rect = self.troop_card_button[1].image.get_rect(topleft=(self.troop_card_ui.rect.topleft[0],  # stat button
                                                                                               self.troop_card_ui.rect.topleft[1]))
            self.troop_card_button[2].rect = self.troop_card_button[2].image.get_rect(topleft=(self.troop_card_ui.rect.topleft[0],  # skill button
                                                                                               self.troop_card_ui.rect.topleft[1] + 40))
            self.troop_card_button[3].rect = self.troop_card_button[3].image.get_rect(topleft=(self.troop_card_ui.rect.topleft[0],  # equipment button
                                                                                               self.troop_card_ui.rect.topleft[1] + 80))

            self.battle_ui.remove(self.eventlog, self.log_scroll, self.troop_card_button, self.col_split_button, self.row_split_button,
                                  self.eventlog_button, self.time_button, self.unitstat_ui, self.inspect_ui, self.leader_now, self.inspect_subunit,
                                  self.subunit_selected_border, self.inspect_button, self.switch_button)

            self.leader_now = [leader for leader in self.preview_leader]  # reset leader in command ui

            self.battle_ui.add(self.filter_stuff, self.unitsetup_stuff, self.test_button, self.command_ui, self.troop_card_ui, self.leader_now,
                               self.time_button)
            self.slot_display_button.event = 0  # reset display editor ui button to show
            self.game_speed = 0  # pause battle

            for slot in self.unit_build_slot:
                if slot.troop_id != 0:
                    self.command_ui.value_input(who=slot)
                    break

        self.speed_number.speed_update(self.game_speed)

    def exit_battle(self):
        self.battle_ui.clear(self.screen, self.background)  # remove all sprite
        self.battle_camera.clear(self.screen, self.background)  # remove all sprite

        self.battle_ui.remove(self.battle_menu, *self.battle_menu_button, *self.esc_slider_menu,
                              *self.esc_value_box, self.battledone_box, self.gamedone_button)  # remove menu

        for group in (self.subunit, self.army_leader, self.team0_unit, self.team1_unit, self.team2_unit,
                      self.unit_icon, self.troop_number_sprite,
                      self.inspect_subunit):  # remove all reference from battle object
            for stuff in group:
                stuff.delete()
                stuff.kill()
                del stuff

        self.remove_unit_ui()

        for arrow in self.range_attacks:  # remove all range attack
            arrow.kill()
            del arrow

        self.subunit_selected = None
        self.all_unit_list = []
        self.all_unit_index = []
        self.combat_path_queue = []
        self.team0_pos_list, self.team1_pos_list, self.team2_pos_list = {}, {}, {}
        self.before_selected = None

        self.drama_timer = 0  # reset drama text popup
        self.battle_ui.remove(self.drama_text)

        if self.mode == "uniteditor":
            self.show_in_card = None

            self.battle_ui.remove(self.unit_delete_button, self.unit_save_button, self.troop_listbox,
                                  self.team_change_button, self.troop_scroll, self.team_coa, self.unit_listbox,
                                  self.unit_preset_name_scroll, self.filter_box, self.team_change_button,
                                  self.slot_display_button, self.test_button, self.deploy_button, self.troop_card_button,
                                  self.terrain_change_button, self.feature_change_button, self.weather_change_button,
                                  self.unit_build_slot, self.leader_now, self.preset_select_border,
                                  self.popup_listbox, self.popup_listscroll, *self.popup_namegroup)

            for group in self.troop_namegroup, self.unit_edit_border, self.unitpreset_namegroup:
                for item in group:  # remove name list
                    item.kill()
                    del item

            for slot in self.unit_build_slot:  # reset all sub-subunit slot
                slot.change_troop(0, self.base_terrain,
                                  self.base_terrain * len(self.battle_map_feature.feature_list) + self.feature_terrain,
                                  self.current_weather)
                slot.leader = None  # remove leader link in

            for leader in self.preview_leader:
                leader.change_subunit(None)  # remove subunit link in leader
                leader.change_leader(1, self.leader_stat)

            del self.current_weather

            self.faction_pick = 0
            self.filter_troop = [True, True, True, True]
            self.troop_list = [item[0] for item in self.troop_data.troop_list.values()][
                              1:]  # reset troop filter back to all faction
            self.troop_index_list = list(range(0, len(self.troop_list) + 1))

            self.leader_list = [item[0] for item in self.leader_stat.leader_list.values()][
                               1:]  # generate leader name list)

            self.leader_now = []

    def rungame(self):
        # v Create Starting Values
        self.game_state = 1  # battle mode
        self.current_unit_row = 0
        self.current_troop_row = 0
        self.text_input_popup = (None, None)  # no popup asking for user text input state
        self.leader_now = []  # list of showing leader in command ui
        self.current_weather = None
        self.team_troopnumber = [1, 1, 1]  # reset list of troop number in each team
        self.last_team_troopnumber = [1, 1, 1]
        self.drama_text.queue = []  # reset drama text popup queue
        if self.mode == "uniteditor":
            self.game_state = 2  # editor mode

            self.full_troop_list = [item[0] for item in self.troop_data.troop_list.values()][1:]

            self.troop_list = self.full_troop_list  # generate troop name list
            self.troop_index_list = list(range(0, len(self.troop_list) + 1))

            self.leader_list = [item[0] for item in self.leader_stat.leader_list.values()][1:]  # generate leader name list

            setup_list(self.screen_scale, menu.NameList, self.current_unit_row, list(self.custom_unit_preset_list.keys()),
                       self.unitpreset_namegroup, self.unit_listbox, self.battle_ui)  # setup preset army list
            setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list,
                       self.troop_namegroup, self.troop_listbox, self.battle_ui)  # setup troop name list

            self.current_list_show = "troop"
            self.unit_preset_name = ""
            self.prepare_state = True
            self.base_terrain = 0
            self.feature_terrain = 0
            self.weather_type = 4
            self.weather_strength = 0
            self.current_weather = weather.Weather(self.time_ui, self.weather_type, self.weather_strength, self.all_weather)
            self.show_in_card = None  # current sub-subunit showing in subunit card

            self.main.make_team_coa([0], ui_class=self.battle_ui, one_team=True,
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
                    self.battle_ui.add(*self.unit_edit_border)
                else:  # reset all other slot
                    slot.selected = False

            self.weather_current = None  # remove weather schedule from editor test

            self.change_state()

            for name in self.unitpreset_namegroup:  # loop to change selected border position to the first in preset list
                self.preset_select_border.change_pos(name.rect.topleft)
                break

        else:  # normal battle
            self.change_state()

        self.map_scale_delay = 0  # delay for map zoom input
        self.mouse_timer = 0  # This is timer for checking double mouse click, use realtime
        self.ui_timer = 0  # This is timer for ui update function, use realtime
        self.drama_timer = 0  # This is timer for combat related function, use self time (realtime * game_speed)
        self.dt = 0  # Realtime used for in self calculation
        self.ui_dt = 0  # Realtime used for ui timer
        self.combat_timer = 0  # This is timer for combat related function, use self time (realtime * game_speed)
        self.last_mouseover = None  # Which subunit last mouse over
        self.speed_number.speed_update(self.game_speed)
        self.ui_click = False  # for checking if mouse click is on ui
        self.click_any = False  # For checking if mouse click on anything, if not close ui related to parentunit
        self.new_unit_click = False  # For checking if another subunit is clicked when inspect ui open
        self.inspect = False  # For checking if inspect ui is currently open or not
        self.last_selected = None  # Which unit is last selected
        self.map_mode = 0  # default, another one show height map
        self.subunit_selected = None  # which subunit in inspect ui is selected in last update loop
        self.before_selected = None  # Which unit is selected before
        self.split_happen = False  # Check if parentunit get split in that loop
        self.show_troop_number = True  # for toggle troop number on/off
        self.weatherscreenadjust = self.screen_rect.width / self.screen_rect.height  # for weather sprite spawn position
        self.rightcorner = self.screen_rect.width - 5
        self.bottomcorner = self.screen_rect.height - 5
        self.centerscreen = [self.screen_rect.width / 2, self.screen_rect.height / 2]  # center position of the screen
        self.battle_mouse_pos = [[0, 0],
                                 [0, 0]]  # mouse position list in self not screen, the first without zoom and the second with camera zoom adjust
        self.unit_selector.current_row = 0
        # ^ End start value

        self.setup_unit_icon()
        self.select_scroll.change_image(new_row=self.unit_selector.current_row)

        self.effect_updater.update(self.all_unit_list, self.dt, self.camera_scale)

        # self.map_def_array = []
        # self.mapunitarray = [[x[random.randint(0, 1)] if i != j else 0 for i in range(1000)] for j in range(1000)]
        pygame.mixer.music.set_endevent(self.SONG_END)  # End current music before battle start

        while True:  # self running
            self.fps_count.fps_show(self.clock)
            keypress = None
            self.mouse_pos = pygame.mouse.get_pos()  # current mouse pos based on screen
            mouse_left_up = False  # left click
            mouse_left_down = False  # hold left click
            mouse_right_up = False  # right click
            mouse_right_down = False  # hold right click
            double_mouse_right = False  # double right click
            mouse_scroll_down = False
            mouse_scroll_up = False
            key_state = pygame.key.get_pressed()
            esc_press = False
            self.ui_click = False  # reset mouse check on ui, if stay false it mean mouse click is not on any ui

            self.battle_ui.clear(self.screen, self.background)  # Clear sprite before update new one

            for event in pygame.event.get():  # get event that happen
                if event.type == QUIT:  # quit self
                    self.text_input_popup = ("confirm_input", "quit")
                    self.confirm_ui.change_instruction("Quit Game?")
                    self.battle_ui.add(*self.confirm_ui_popup)

                elif event.type == self.SONG_END:  # change music track
                    pygame.mixer.music.unload()
                    self.pickmusic = random.randint(0, len(self.music_current) - 1)
                    pygame.mixer.music.load(self.musiclist[self.music_current[self.pickmusic]])
                    pygame.mixer.music.play(fade_ms=100)

                elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:  # open/close menu
                    esc_press = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # left click
                        mouse_left_up = True
                    elif event.button == 3:  # Right Click
                        mouse_right_up = True
                        if self.mouse_timer == 0:
                            self.mouse_timer = 0.001  # Start timer after first mouse click
                        elif self.mouse_timer < 0.3:  # if click again within 0.3 second for it to be considered double click
                            double_mouse_right = True  # double right click
                            self.mouse_timer = 0
                    elif event.button == 4:  # Mouse scroll up
                        mouse_scroll_up = True
                        row_change = -1
                    elif event.button == 5:  # Mouse scroll down
                        mouse_scroll_down = True
                        row_change = 1

                elif event.type == pygame.KEYDOWN:
                    if self.text_input_popup[0] == "text_input":  # event update to input box
                        self.input_box.user_input(event)
                    else:
                        keypress = event.key

                if pygame.mouse.get_pressed()[0]:  # Hold left click
                    mouse_left_down = True
                elif pygame.mouse.get_pressed()[2]:  # Hold left click
                    mouse_right_down = True

            if self.text_input_popup == (None, None):
                if esc_press:  # open/close menu
                    if self.game_state in (1, 2):  # in battle
                        self.game_state = 0  # open menu
                        self.battle_ui.add(self.battle_menu, *self.battle_menu_button)  # add menu and its buttons to drawer
                        esc_press = False  # reset esc press, so it not stops esc menu when open

                if self.game_state in (1, 2):  # self in battle state
                    # v register user input during gameplay
                    if mouse_scroll_up or mouse_scroll_down:  # Mouse scroll
                        if self.eventlog.rect.collidepoint(self.mouse_pos):  # Scrolling when mouse at event log
                            self.eventlog.current_start_row += row_change
                            if mouse_scroll_up:
                                if self.eventlog.current_start_row < 0:  # can go no further than the first log
                                    self.eventlog.current_start_row = 0
                                else:
                                    self.eventlog.recreate_image()  # recreate eventlog image
                                    self.log_scroll.change_image(new_row=self.eventlog.current_start_row)
                            elif mouse_scroll_down:
                                if self.eventlog.current_start_row + self.eventlog.max_row_show - 1 < self.eventlog.len_check and \
                                        self.eventlog.len_check > 9:
                                    self.eventlog.recreate_image()
                                    self.log_scroll.change_image(new_row=self.eventlog.current_start_row)
                                else:
                                    self.eventlog.current_start_row -= 1

                        elif self.unit_selector.rect.collidepoint(self.mouse_pos):  # Scrolling when mouse at unit selector ui
                            self.unit_selector.current_row += row_change
                            if mouse_scroll_up:
                                if self.unit_selector.current_row < 0:
                                    self.unit_selector.current_row = 0
                                else:
                                    self.setup_unit_icon()
                                    self.select_scroll.change_image(new_row=self.unit_selector.current_row)
                            elif mouse_scroll_down:
                                if self.unit_selector.current_row < self.unit_selector.log_size:
                                    self.setup_unit_icon()
                                    self.select_scroll.change_image(new_row=self.unit_selector.current_row)
                                else:
                                    self.unit_selector.current_row -= 1
                                    if self.unit_selector.current_row < 0:
                                        self.unit_selector.current_row = 0

                        elif self.popup_listbox in self.battle_ui:  # mouse scroll on popup list
                            if self.popup_listbox.type == "terrain":
                                self.current_popu_prow = list_scroll(mouse_scroll_up, mouse_scroll_down, self.popup_listscroll,
                                                                     self.popup_listbox,
                                                                     self.current_popu_prow, self.battle_map_base.terrain_list,
                                                                     self.popup_namegroup, self.battle_ui)
                            elif self.popup_listbox.type == "feature":
                                self.current_popu_prow = list_scroll(mouse_scroll_up, mouse_scroll_down, self.popup_listscroll,
                                                                     self.popup_listbox,
                                                                     self.current_popu_prow, self.battle_map_feature.feature_list,
                                                                     self.popup_namegroup, self.battle_ui)
                            elif self.popup_listbox.type == "weather":
                                self.current_popu_prow = (mouse_scroll_up, mouse_scroll_down, self.popup_listscroll,
                                                          self.popup_listbox, self.current_popu_prow, self.weather_list,
                                                          self.popup_namegroup, self.battle_ui)
                            elif self.popup_listbox.type == "leader":
                                self.current_popu_prow = list_scroll(mouse_scroll_up, mouse_scroll_down, self.popup_listscroll,
                                                                     self.popup_listbox, self.current_popu_prow, self.leader_list,
                                                                     self.popup_namegroup, self.battle_ui, layer=19)

                        elif self.unit_listbox.rect.collidepoint(self.mouse_pos):  # mouse scroll on unit preset list
                            self.current_unit_row = list_scroll(mouse_scroll_up, mouse_scroll_down, self.unit_preset_name_scroll,
                                                                self.unit_listbox,
                                                                self.current_unit_row, list(self.custom_unit_preset_list.keys()),
                                                                self.unitpreset_namegroup, self.battle_ui)
                        elif self.troop_listbox.rect.collidepoint(self.mouse_pos):
                            if self.current_list_show == "troop":  # mouse scroll on troop list
                                self.current_troop_row = list_scroll(mouse_scroll_up, mouse_scroll_down, self.troop_scroll, self.troop_listbox,
                                                                     self.current_troop_row, self.troop_list,
                                                                     self.troop_namegroup, self.battle_ui)
                            elif self.current_list_show == "faction":  # mouse scroll on faction list
                                self.current_troop_row = list_scroll(mouse_scroll_up, mouse_scroll_down, self.troop_scroll, self.troop_listbox,
                                                                     self.current_troop_row, self.faction_list,
                                                                     self.troop_namegroup, self.battle_ui)

                        elif self.map_scale_delay == 0:  # Scrolling in self map to zoom
                            if mouse_scroll_up:
                                self.camera_scale += 1
                                if self.camera_scale > 10:
                                    self.camera_scale = 10
                                else:
                                    self.camera_pos[0] = self.base_camera_pos[0] * self.camera_scale
                                    self.camera_pos[1] = self.base_camera_pos[1] * self.camera_scale
                                    self.show_map.change_scale(self.camera_scale)
                                    if self.game_state == 1:  # only have delay in battle mode
                                        self.map_scale_delay = 0.001

                            elif mouse_scroll_down:
                                self.camera_scale -= 1
                                if self.camera_scale < 1:
                                    self.camera_scale = 1
                                else:
                                    self.camera_pos[0] = self.base_camera_pos[0] * self.camera_scale
                                    self.camera_pos[1] = self.base_camera_pos[1] * self.camera_scale
                                    self.show_map.change_scale(self.camera_scale)
                                    if self.game_state == 1:  # only have delay in battle mode
                                        self.map_scale_delay = 0.001
                    # ^ End mouse scroll input

                    # keyboard input
                    if keypress == pygame.K_TAB:
                        self.map_mode += 1  # change height map mode
                        if self.map_mode > 2:
                            self.map_mode = 0
                        self.show_map.change_mode(self.map_mode)
                        self.show_map.change_scale(self.camera_scale)

                    elif keypress == pygame.K_o:  # Toggle unit number
                        if self.show_troop_number:
                            self.show_troop_number = False
                            self.effect_updater.remove(*self.troop_number_sprite)
                            self.battle_camera.remove(*self.troop_number_sprite)
                        else:  # speed currently pause
                            self.show_troop_number = True
                            self.effect_updater.add(*self.troop_number_sprite)
                            self.battle_camera.add(*self.troop_number_sprite)

                    elif keypress == pygame.K_p:  # Speed Pause/unpause Button
                        if self.game_speed >= 0.5:  #
                            self.game_speed = 0  # pause self speed
                        else:  # speed currently pause
                            self.game_speed = 1  # unpause self and set to speed 1
                        self.speed_number.speed_update(self.game_speed)

                    elif keypress == pygame.K_KP_MINUS:  # reduce self speed
                        new_index = self.game_speed_list.index(self.game_speed) - 1
                        if new_index >= 0:  # cannot reduce self speed than what is available
                            self.game_speed = self.game_speed_list[new_index]
                        self.speed_number.speed_update(self.game_speed)

                    elif keypress == pygame.K_KP_PLUS:  # increase self speed
                        new_index = self.game_speed_list.index(self.game_speed) + 1
                        if new_index < len(self.game_speed_list):  # cannot increase self speed than what is available
                            self.game_speed = self.game_speed_list[new_index]
                        self.speed_number.speed_update(self.game_speed)

                    elif keypress == pygame.K_PAGEUP:  # Go to top of event log
                        self.eventlog.current_start_row = 0
                        self.eventlog.recreate_image()
                        self.log_scroll.change_image(new_row=self.eventlog.current_start_row)

                    elif keypress == pygame.K_PAGEDOWN:  # Go to bottom of event log
                        if self.eventlog.len_check > self.eventlog.max_row_show:
                            self.eventlog.current_start_row = self.eventlog.len_check - self.eventlog.max_row_show
                            self.eventlog.recreate_image()
                            self.log_scroll.change_image(new_row=self.eventlog.current_start_row)

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
                        self.base_camera_pos[1] += 4 * (
                                11 - self.camera_scale)  # need "11 -" for converting cameral scale so the further zoom camera move faster
                        self.camera_pos[1] = self.base_camera_pos[1] * self.camera_scale  # resize camera pos
                        self.camera_fix()

                    elif key_state[K_w] or self.mouse_pos[1] <= 5:  # Camera move up
                        self.base_camera_pos[1] -= 4 * (11 - self.camera_scale)
                        self.camera_pos[1] = self.base_camera_pos[1] * self.camera_scale
                        self.camera_fix()

                    if key_state[K_a] or self.mouse_pos[0] <= 5:  # Camera move left
                        self.base_camera_pos[0] -= 4 * (11 - self.camera_scale)
                        self.camera_pos[0] = self.base_camera_pos[0] * self.camera_scale
                        self.camera_fix()

                    elif key_state[K_d] or self.mouse_pos[0] >= self.rightcorner:  # Camera move right
                        self.base_camera_pos[0] += 4 * (11 - self.camera_scale)
                        self.camera_pos[0] = self.base_camera_pos[0] * self.camera_scale
                        self.camera_fix()

                    self.cameraupcorner = (self.camera_pos[0] - self.centerscreen[0],
                                           self.camera_pos[1] - self.centerscreen[1])  # calculate top left corner of camera position
                    # ^ End camera movement

                    if self.mouse_timer != 0:  # player click mouse once before
                        self.mouse_timer += self.ui_dt  # increase timer for mouse click using real time
                        if self.mouse_timer >= 0.3:  # time pass 0.3 second no longer count as double click
                            self.mouse_timer = 0

                    if self.map_scale_delay > 0:  # player change map scale once before
                        self.map_scale_delay += self.ui_dt
                        if self.map_scale_delay >= 0.1:  # delay for 1 second until user can change scale again
                            self.map_scale_delay = 0

                    self.battle_mouse_pos[0] = pygame.Vector2((self.mouse_pos[0] - self.centerscreen[0]) + self.camera_pos[0],
                                                              self.mouse_pos[1] - self.centerscreen[1] + self.camera_pos[
                                                                  1])  # mouse pos on the map based on camera position
                    self.battle_mouse_pos[1] = self.battle_mouse_pos[0] / self.camera_scale  # mouse pos on the map at current camera zoom scale

                    if self.terrain_check in self.battle_ui and (
                            self.terrain_check.pos != self.mouse_pos or key_state[K_s] or key_state[K_w] or key_state[K_a] or key_state[K_d]):
                        self.battle_ui.remove(self.terrain_check)  # remove terrain popup when move mouse or camera

                    if mouse_left_up or mouse_right_up or mouse_left_down or mouse_right_down:
                        if mouse_left_up:
                            self.click_any = False
                            self.new_unit_click = False

                        if self.mini_map.rect.collidepoint(self.mouse_pos):  # mouse position on mini map
                            self.ui_click = True
                            if mouse_left_up:  # move self camera to position clicked on mini map
                                self.click_any = True
                                pos_mask = pygame.Vector2(int(self.mouse_pos[0] - self.mini_map.rect.x), int(self.mouse_pos[1] - self.mini_map.rect.y))
                                self.base_camera_pos = pos_mask * 5
                                self.camera_pos = self.base_camera_pos * self.camera_scale
                            elif mouse_right_up:  # nothing happen with mouse right
                                if self.last_selected is not None:
                                    self.ui_click = True
                        elif self.select_scroll.rect.collidepoint(self.mouse_pos):  # Must check mouse collide for scroll before unit select ui
                            self.ui_click = True
                            if mouse_left_down or mouse_left_up:
                                self.click_any = True
                                new_row = self.select_scroll.user_input(self.mouse_pos)
                                if self.unit_selector.current_row != new_row:
                                    self.unit_selector.current_row = new_row
                                    self.setup_unit_icon()

                        elif self.unit_selector.rect.collidepoint(self.mouse_pos):  # check mouse collide for unit selector ui
                            if mouse_left_up:
                                self.click_any = True
                            self.ui_click = True
                            self.uniticon_mouseover(mouse_left_up, mouse_right_up)

                        elif self.test_button.rect.collidepoint(self.mouse_pos) and self.test_button in self.battle_ui:
                            self.ui_click = True
                            if mouse_left_up:
                                self.click_any = True
                                if self.test_button.event == 0:
                                    self.test_button.event = 1
                                    new_mode = 1

                                elif self.test_button.event == 1:
                                    self.test_button.event = 0
                                    new_mode = 2
                                self.game_state = new_mode
                                self.change_state()

                        if self.game_state == 1:
                            if self.log_scroll.rect.collidepoint(self.mouse_pos):  # Must check mouse collide for scroll before event log ui
                                self.ui_click = True
                                if mouse_left_down or mouse_left_up:
                                    self.click_any = True
                                    new_row = self.log_scroll.user_input(self.mouse_pos)
                                    if self.eventlog.current_start_row != new_row:
                                        self.eventlog.current_start_row = new_row
                                        self.eventlog.recreate_image()

                            elif self.eventlog.rect.collidepoint(self.mouse_pos):  # check mouse collide for event log ui
                                if mouse_left_up:
                                    self.click_any = True
                                self.ui_click = True

                            elif self.time_ui.rect.collidepoint(self.mouse_pos):  # check mouse collide for time bar ui
                                self.ui_click = True
                                if mouse_left_up:
                                    self.click_any = True

                                    for index, button in enumerate(self.time_button):  # Event log button and timer button click
                                        if button.rect.collidepoint(self.mouse_pos):
                                            if button.event == "pause":  # pause button
                                                self.game_speed = 0
                                            elif button.event == "decrease":  # reduce speed button
                                                new_index = self.game_speed_list.index(self.game_speed) - 1
                                                if new_index >= 0:
                                                    self.game_speed = self.game_speed_list[new_index]
                                            elif button.event == "increase":  # increase speed button
                                                new_index = self.game_speed_list.index(self.game_speed) + 1
                                                if new_index < len(self.game_speed_list):
                                                    self.game_speed = self.game_speed_list[new_index]
                                            self.speed_number.speed_update(self.game_speed)
                                            break

                            elif self.ui_mouseover():  # check mouse collide for other ui
                                pass

                            elif self.button_mouseover(mouse_right_up):  # check mouse collide for button
                                pass

                            elif mouse_right_up and self.last_selected is None and self.ui_click is False:  # draw terrain popup ui when right click at map with no selected parentunit
                                if 0 <= self.battle_mouse_pos[1][0] <= 999 and \
                                        0 <= self.battle_mouse_pos[1][1] <= 999:  # not draw if pos is off the map
                                    terrain_pop, feature_pop = self.battle_map_feature.get_feature(self.battle_mouse_pos[1], self.battle_map_base)
                                    feature_pop = self.battle_map_feature.feature_mod[feature_pop]
                                    height_pop = self.battle_map_height.get_height(self.battle_mouse_pos[1])
                                    self.terrain_check.pop(self.mouse_pos, feature_pop, height_pop)
                                    self.battle_ui.add(self.terrain_check)

                            elif self.ui_click is False:
                                for index, button in enumerate(self.eventlog_button):  # Event log button and timer button click
                                    if button.rect.collidepoint(self.mouse_pos):
                                        if index in (0, 1, 2, 3, 4, 5):  # eventlog button
                                            self.ui_click = True
                                            if mouse_left_up:
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
                                        mouse_left_up and self.inspect and self.new_unit_click):  # click on inspect ui open/close button
                                    if self.inspect_button.rect.collidepoint(self.mouse_pos):
                                        self.button_name_popup.pop(self.mouse_pos, "Inspect Subunit")
                                        self.battle_ui.add(self.button_name_popup)
                                        if mouse_right_up:
                                            self.ui_click = True  # for some reason the loop mouse check above does not work for inspect button, so it here instead
                                    if mouse_left_up:
                                        if self.inspect is False:  # Add unit inspect ui when left click at ui button or when change subunit with inspect open
                                            self.inspect = True
                                            self.battle_ui.add(*self.troop_card_button,
                                                               self.troop_card_ui, self.inspect_ui)
                                            self.subunit_selected = None

                                            for index, subunit in enumerate(self.last_selected.subunit_sprite_array.flat):
                                                if subunit is not None:
                                                    self.inspect_subunit[index].add_subunit(subunit)
                                                    self.battle_ui.add(self.inspect_subunit[index])
                                                    if self.subunit_selected is None:
                                                        self.subunit_selected = self.inspect_subunit[index]

                                            self.subunit_selected_border.pop(self.subunit_selected.pos)
                                            self.battle_ui.add(self.subunit_selected_border)
                                            self.troop_card_ui.value_input(who=self.subunit_selected.who, weapon_list=self.all_weapon,
                                                                           armour_list=self.all_armour,
                                                                           split=self.split_happen)

                                            if self.troop_card_ui.option == 2:  # blit skill icon is previous mode is skill
                                                self.trait_skill_blit()
                                                self.effect_icon_blit()
                                                self.countdown_skill_icon()

                                        elif self.inspect:  # Remove when click again and the ui already open
                                            self.battle_ui.remove(*self.inspect_subunit, self.subunit_selected_border, self.troop_card_button,
                                                                  self.troop_card_ui, self.inspect_ui)
                                            self.inspect = False
                                            self.new_unit_click = False

                                elif self.command_ui in self.battle_ui and (
                                        self.command_ui.rect.collidepoint(self.mouse_pos) or keypress is not None):  # mouse position on command ui
                                    if self.last_selected.control:
                                        if self.switch_button[0].rect.collidepoint(self.mouse_pos) or keypress == pygame.K_g:
                                            if mouse_left_up or keypress == pygame.K_g:  # rotate skill condition when clicked
                                                self.last_selected.skill_cond += 1
                                                if self.last_selected.skill_cond > 3:
                                                    self.last_selected.skill_cond = 0
                                                self.switch_button[0].event = self.last_selected.skill_cond
                                            if self.switch_button[0].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                pop_text = ("Free Skill Use", "Conserve 50% Stamina", "Conserve 25% stamina", "Forbid Skill")
                                                self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[0].event])
                                                self.battle_ui.add(self.button_name_popup)

                                        elif self.switch_button[1].rect.collidepoint(self.mouse_pos) or keypress == pygame.K_f:
                                            if mouse_left_up or keypress == pygame.K_f:  # rotate fire at will condition when clicked
                                                self.last_selected.fireatwill += 1
                                                if self.last_selected.fireatwill > 1:
                                                    self.last_selected.fireatwill = 0
                                                self.switch_button[1].event = self.last_selected.fireatwill
                                            if self.switch_button[1].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                pop_text = ("Fire at will", "Hold fire until order")
                                                self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[1].event])
                                                self.battle_ui.add(self.button_name_popup)

                                        elif self.switch_button[2].rect.collidepoint(self.mouse_pos) or keypress == pygame.K_h:
                                            if mouse_left_up or keypress == pygame.K_h:  # rotate hold condition when clicked
                                                self.last_selected.hold += 1
                                                if self.last_selected.hold > 2:
                                                    self.last_selected.hold = 0
                                                self.switch_button[2].event = self.last_selected.hold
                                            if self.switch_button[2].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                pop_text = ("Aggressive", "Skirmish/Scout", "Hold Ground")
                                                self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[2].event])
                                                self.battle_ui.add(self.button_name_popup)

                                        elif self.switch_button[3].rect.collidepoint(self.mouse_pos) or keypress == pygame.K_j:
                                            if mouse_left_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                                self.last_selected.use_min_range += 1
                                                if self.last_selected.use_min_range > 1:
                                                    self.last_selected.use_min_range = 0
                                                self.switch_button[3].event = self.last_selected.use_min_range
                                            if self.switch_button[3].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                pop_text = ("Minimum Shoot Range", "Maximum Shoot range")
                                                self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[3].event])
                                                self.battle_ui.add(self.button_name_popup)

                                        elif self.switch_button[4].rect.collidepoint(self.mouse_pos) or keypress == pygame.K_j:
                                            if mouse_left_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                                self.last_selected.shoothow += 1
                                                if self.last_selected.shoothow > 2:
                                                    self.last_selected.shoothow = 0
                                                self.switch_button[4].event = self.last_selected.shoothow
                                            if self.switch_button[4].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                pop_text = ("Both Arc and Direct Shot", "Only Arc Shot", "Only Direct Shot")
                                                self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[4].event])
                                                self.battle_ui.add(self.button_name_popup)

                                        elif self.switch_button[5].rect.collidepoint(self.mouse_pos) or keypress == pygame.K_j:
                                            if mouse_left_up or keypress == pygame.K_j:  # rotate min range condition when clicked
                                                self.last_selected.runtoggle += 1
                                                if self.last_selected.runtoggle > 1:
                                                    self.last_selected.runtoggle = 0
                                                self.switch_button[5].event = self.last_selected.runtoggle
                                            if self.switch_button[5].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                pop_text = ("Toggle Walk", "Toggle Run")
                                                self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[5].event])
                                                self.battle_ui.add(self.button_name_popup)

                                        elif self.switch_button[6].rect.collidepoint(self.mouse_pos):  # or keypress == pygame.K_j
                                            if mouse_left_up:  # or keypress == pygame.K_j  # rotate min range condition when clicked
                                                self.last_selected.attackmode += 1
                                                if self.last_selected.attackmode > 2:
                                                    self.last_selected.attackmode = 0
                                                self.switch_button[6].event = self.last_selected.attackmode
                                            if self.switch_button[6].rect.collidepoint(self.mouse_pos):  # popup name when mouse over
                                                pop_text = ("Frontline Attack Only", "Keep Formation", "All Out Attack")
                                                self.button_name_popup.pop(self.mouse_pos, pop_text[self.switch_button[6].event])
                                                self.battle_ui.add(self.button_name_popup)

                                        elif self.col_split_button in self.battle_ui and self.col_split_button.rect.collidepoint(self.mouse_pos):
                                            self.button_name_popup.pop(self.mouse_pos, "Split By Middle Column")
                                            self.battle_ui.add(self.button_name_popup)
                                            if mouse_left_up and self.last_selected.state != 10:
                                                self.splitunit(self.last_selected, 1)
                                                self.split_happen = True
                                                self.check_split(self.last_selected)
                                                self.battle_ui.remove(*self.leader_now)
                                                self.leader_now = self.last_selected.leader
                                                self.battle_ui.add(*self.leader_now)
                                                self.setup_unit_icon()

                                        elif self.row_split_button in self.battle_ui and self.row_split_button.rect.collidepoint(self.mouse_pos):
                                            self.button_name_popup.pop(self.mouse_pos, "Split by Middle Row")
                                            self.battle_ui.add(self.button_name_popup)
                                            if mouse_left_up and self.last_selected.state != 10:
                                                self.splitunit(self.last_selected, 0)
                                                self.split_happen = True
                                                self.check_split(self.last_selected)
                                                self.battle_ui.remove(*self.leader_now)
                                                self.leader_now = self.last_selected.leader
                                                self.battle_ui.add(*self.leader_now)
                                                self.setup_unit_icon()

                                        # elif self.button_ui[7].rect.collidepoint(self.mouse_pos):  # decimation effect
                                        #     self.button_name_popup.pop(self.mouse_pos, "Decimation")
                                        #     self.battle_ui.add(self.button_name_popup)
                                        #     if mouse_left_up and self.last_selected.state == 0:
                                        #         for subunit in self.last_selected.subunit_sprite:
                                        #             subunit.status_effect[98] = self.troop_data.status_list[98].copy()
                                        #             subunit.unit_health -= round(subunit.unit_health * 0.1)
                                    if self.leader_mouseover(mouse_right_up):
                                        self.battle_ui.remove(self.button_name_popup)
                                        pass
                                else:
                                    self.battle_ui.remove(self.leader_popup)  # remove leader name popup if no mouseover on any button
                                    self.battle_ui.remove(self.button_name_popup)  # remove popup if no mouseover on any button

                                if self.inspect:  # if inspect ui is open
                                    if mouse_left_up or mouse_right_up:
                                        if self.inspect_ui.rect.collidepoint(self.mouse_pos):  # if mouse pos inside unit ui when click
                                            self.click_any = True  # for avoiding right click or  subunit
                                            self.ui_click = True  # for avoiding clicking subunit under ui
                                            for subunit in self.inspect_subunit:
                                                if subunit.rect.collidepoint(
                                                        self.mouse_pos) and subunit in self.battle_ui:  # Change showing stat to the clicked subunit one
                                                    if mouse_left_up:
                                                        self.subunit_selected = subunit
                                                        self.subunit_selected_border.pop(self.subunit_selected.pos)
                                                        self.eventlog.add_log(
                                                            [0, str(self.subunit_selected.who.board_pos) + " " + str(
                                                                self.subunit_selected.who.name) + " in " +
                                                             self.subunit_selected.who.parentunit.leader[0].name + "'s parentunit is selected"], [3])
                                                        self.battle_ui.add(self.subunit_selected_border)
                                                        self.troop_card_ui.value_input(who=self.subunit_selected.who, weapon_list=self.all_weapon,
                                                                                       armour_list=self.all_armour, split=self.split_happen)

                                                        if self.troop_card_ui.option == 2:
                                                            self.trait_skill_blit()
                                                            self.effect_icon_blit()
                                                            self.countdown_skill_icon()
                                                        else:
                                                            self.kill_effect_icon()

                                                    elif mouse_right_up:
                                                        self.popout_lorebook(3, subunit.who.troop_id)
                                                    break

                                        elif self.troop_card_ui.rect.collidepoint(self.mouse_pos):  # mouse position in subunit card
                                            self.click_any = True
                                            self.ui_click = True  # for avoiding clicking subunit under ui
                                            self.unitcardbutton_click(self.subunit_selected.who)

                                    if self.troop_card_ui.option == 2:
                                        if self.effect_icon_mouse_over(self.skill_icon, mouse_right_up):
                                            pass
                                        elif self.effect_icon_mouse_over(self.effect_icon, mouse_right_up):
                                            pass
                                        else:
                                            self.battle_ui.remove(self.effect_popup)

                                else:
                                    self.kill_effect_icon()

                                if mouse_right_up and self.ui_click is False:  # Unit command
                                    self.last_selected.command(self.battle_mouse_pos[1], mouse_right_up, double_mouse_right,
                                                               self.last_mouseover, key_state)

                                self.before_selected = self.last_selected

                            # ^ End subunit selected code

                        elif self.game_state == 2:  # uniteditor state
                            self.battle_ui.remove(self.leader_popup)
                            if self.popup_listbox in self.battle_ui and self.popup_listbox.type == "leader" \
                                    and self.popup_listbox.rect.collidepoint(
                                self.mouse_pos):  # this need to be at the top here to prioritise popup click
                                self.ui_click = True
                                for index, name in enumerate(self.popup_namegroup):  # change leader with the new selected one
                                    if name.rect.collidepoint(self.mouse_pos):
                                        if mouse_left_up and (self.show_in_card is not None and self.show_in_card.name != "None"):
                                            if self.show_in_card.leader is not None and \
                                                    self.leader_now[
                                                        self.show_in_card.leader.army_position].name != "None":  # remove old leader
                                                self.leader_now[self.show_in_card.leader.army_position].change_leader(1,
                                                                                                                      self.leader_stat)
                                                self.leader_now[self.show_in_card.leader.army_position].change_subunit(
                                                    None)

                                            true_index = [index for index, value in
                                                         enumerate(list(self.leader_stat.leader_list.values())) if value[0] == name.name][0]
                                            true_index = list(self.leader_stat.leader_list.keys())[true_index]
                                            self.leader_now[self.selected_leader].change_leader(true_index, self.leader_stat)
                                            self.leader_now[self.selected_leader].change_subunit(self.show_in_card)
                                            self.show_in_card.leader = self.leader_now[self.selected_leader]
                                            self.preview_authority(self.leader_now,
                                                                   self.leader_now[self.selected_leader].subunit.army_id)
                                            self.troop_card_ui.value_input(who=self.show_in_card,
                                                                           weapon_list=self.all_weapon,
                                                                           armour_list=self.all_armour,
                                                                           change_option=1)
                                            unit_dict = self.convert_slot_dict("test")
                                            if unit_dict is not None:
                                                warn_list = []
                                                leader_list = [int(item) for item in unit_dict['test'][-3].split(",")]
                                                leader_list = [item for item in leader_list if 1 < item < 10000]
                                                leader_list_set = set(leader_list)
                                                if len(leader_list) != len(leader_list_set):  # unit has duplicate unique leader
                                                    warn_list.append(self.warning_msg.duplicateleader_warn)
                                                if unit_dict['test'][-1] == "0":  # unit has leader/unit of multi faction
                                                    warn_list.append(self.warning_msg.multifaction_warn)
                                                if len(warn_list) > 0:
                                                    self.warning_msg.warning(warn_list)
                                                    self.battle_ui.add(self.warning_msg)

                                        elif mouse_right_up:
                                            self.popout_lorebook(8, self.current_popu_prow + index + 1)

                            elif self.unit_listbox.rect.collidepoint(self.mouse_pos) and self.unit_listbox in self.battle_ui:
                                self.ui_click = True
                                for index, name in enumerate(self.unitpreset_namegroup):
                                    if name.rect.collidepoint(self.mouse_pos) and mouse_left_up:
                                        self.preset_select_border.change_pos(name.rect.topleft)  # change border to one selected
                                        if list(self.custom_unit_preset_list.keys())[index] != "New Preset":
                                            self.unit_preset_name = name.name
                                            unit_list = []
                                            arraylist = list(self.custom_unit_preset_list[list(self.custom_unit_preset_list.keys())[index]])
                                            for listnum in (0, 1, 2, 3, 4, 5, 6, 7):
                                                unit_list += [int(item) if item.isdigit() else item
                                                             for item in arraylist[listnum].split(",")]
                                            leader_who_list = [int(item) if item.isdigit() else item
                                                             for item in arraylist[8].split(",")]
                                            leader_pos_list = [int(item) if item.isdigit() else item
                                                             for item in arraylist[9].split(",")]

                                            for unit_index, item in enumerate(unit_list):  # change all slot to whatever save in the selected preset
                                                for slot in self.unit_build_slot:
                                                    if slot.game_id == unit_index:
                                                        slot.change_troop(item, self.base_terrain,
                                                                          self.base_terrain * len(
                                                                              self.battle_map_feature.feature_list)
                                                                          + self.feature_terrain, self.current_weather)
                                                        break

                                            for leader_index, item in enumerate(leader_who_list):
                                                self.preview_leader[leader_index].leader = None
                                                if self.preview_leader[leader_index].subunit is not None:
                                                    self.preview_leader[leader_index].subunit.leader = None

                                                self.preview_leader[leader_index].change_leader(item, self.leader_stat)

                                                pos_index = 0
                                                for slot in self.unit_build_slot:  # can't use game_id here as none subunit not count in position check
                                                    if pos_index == leader_pos_list[leader_index]:
                                                        self.preview_leader[leader_index].change_subunit(slot)
                                                        slot.leader = self.preview_leader[leader_index]
                                                        break
                                                    else:
                                                        if slot.name != "None":
                                                            pos_index += 1

                                            self.leader_now = [leader for leader in self.preview_leader]
                                            self.battle_ui.add(*self.leader_now)  # add leader portrait to draw
                                            self.show_in_card = slot
                                            self.command_ui.value_input(who=self.show_in_card)
                                            self.troop_card_ui.value_input(who=self.show_in_card, weapon_list=self.all_weapon,
                                                                           armour_list=self.all_armour)  # update subunit card on selected subunit
                                            if self.troop_card_ui.option == 2:
                                                self.trait_skill_blit()
                                                self.effect_icon_blit()
                                                self.countdown_skill_icon()
                                            # self.previewauthority(self.preview_leader, 0)  # calculate authority

                                        else:  # new preset
                                            self.unit_preset_name = ""
                                            for slot in self.unit_build_slot:  # reset all sub-subunit slot
                                                slot.change_troop(0, self.base_terrain,
                                                                  self.base_terrain * len(
                                                                      self.battle_map_feature.feature_list) + self.feature_terrain,
                                                                  self.current_weather)
                                                slot.leader = None  # remove leader link in

                                            for leader in self.preview_leader:
                                                leader.change_subunit(None)  # remove subunit link in leader
                                                leader.change_leader(1, self.leader_stat)

                                            self.leader_now = [leader for leader in self.preview_leader]
                                            self.battle_ui.add(*self.leader_now)  # add leader portrait to draw
                                            self.show_in_card = slot
                                            self.command_ui.value_input(who=self.show_in_card)

                                            # self.troop_card_ui.valueinput(attacker=self.show_in_card, weapon_list=self.allweapon, armour_list=self.allarmour,
                                            #                       change_option=1)

                            elif self.command_ui in self.battle_ui and self.command_ui.rect.collidepoint(self.mouse_pos):
                                self.ui_click = True
                                for leader_index, leader in enumerate(self.leader_now):  # loop mouse pos on leader portrait
                                    if leader.rect.collidepoint(self.mouse_pos):
                                        army_position = self.leader_level[leader.army_position + 4]

                                        self.leader_popup.pop(self.mouse_pos, army_position + ": " + leader.name)  # popup leader name when mouse over
                                        self.battle_ui.add(self.leader_popup)

                                        if mouse_left_up:  # open list of leader to change leader in that slot
                                            self.selected_leader = leader_index
                                            self.popup_list_newopen(leader.rect.midright, self.leader_list, "leader")

                                        elif mouse_right_up:
                                            self.popout_lorebook(8, leader.leader_id)
                                        break

                            elif self.troop_card_ui.rect.collidepoint(self.mouse_pos):
                                self.ui_click = True
                                if self.show_in_card is not None and mouse_left_up:
                                    self.unitcardbutton_click(self.show_in_card)

                                if self.troop_card_ui.option == 2:
                                    for icon_list in (self.effect_icon, self.skill_icon):
                                        if self.effect_icon_mouse_over(self.skill_icon, mouse_right_up):
                                            pass
                                        elif self.effect_icon_mouse_over(self.effect_icon, mouse_right_up):
                                            pass
                                        else:
                                            self.battle_ui.remove(self.effect_popup)

                            elif mouse_left_up or mouse_left_down or mouse_right_up:  # left click for select, hold left mouse for scrolling, right click for encyclopedia
                                if mouse_left_up or mouse_left_down:
                                    if self.popup_listbox in self.battle_ui:
                                        if self.popup_listbox.rect.collidepoint(self.mouse_pos):
                                            self.ui_click = True
                                            for index, name in enumerate(self.popup_namegroup):
                                                if name.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # click on name in list
                                                    if self.popup_listbox.type == "terrain":
                                                        self.terrain_change_button.changetext(self.battle_map_base.terrain_list[index])
                                                        self.base_terrain = index
                                                        self.editor_map_change(map.terrain_colour[self.base_terrain],
                                                                               map.feature_colour[self.feature_terrain])

                                                    elif self.popup_listbox.type == "feature":
                                                        self.feature_change_button.changetext(self.battle_map_feature.feature_list[index])
                                                        self.feature_terrain = index
                                                        self.editor_map_change(map.terrain_colour[self.base_terrain],
                                                                               map.feature_colour[self.feature_terrain])

                                                    elif self.popup_listbox.type == "weather":
                                                        self.weather_type = int(index / 3)
                                                        self.weather_strength = index - (self.weather_type * 3)
                                                        self.weather_change_button.changetext(self.weather_list[index])
                                                        del self.current_weather
                                                        self.current_weather = weather.Weather(self.time_ui, self.weather_type + 1,
                                                                                               self.weather_strength, self.all_weather)

                                                    for slot in self.unit_build_slot:  # reset all troop stat
                                                        slot.change_troop(slot.troop_id, self.base_terrain,
                                                                          self.base_terrain * len(
                                                                              self.battle_map_feature.feature_list) + self.feature_terrain,
                                                                          self.current_weather)
                                                    if self.show_in_card is not None:  # reset subunit card as well
                                                        self.command_ui.value_input(who=self.show_in_card)
                                                        self.troop_card_ui.value_input(who=self.show_in_card, weapon_list=self.all_weapon,
                                                                                       armour_list=self.all_armour,
                                                                                       change_option=1)
                                                        if self.troop_card_ui.option == 2:
                                                            self.trait_skill_blit()
                                                            self.effect_icon_blit()
                                                            self.countdown_skill_icon()

                                                    for this_name in self.popup_namegroup:  # remove troop name list
                                                        this_name.kill()
                                                        del this_name

                                                    self.battle_ui.remove(self.popup_listbox, self.popup_listscroll)
                                                    break

                                        elif self.popup_listscroll.rect.collidepoint(self.mouse_pos):  # scrolling on list
                                            self.ui_click = True
                                            self.current_popu_prow = self.popup_listscroll.user_input(
                                                self.mouse_pos)  # update the scroll and get new current subsection
                                            if self.popup_listbox.type == "terrain":
                                                setup_list(self.screen_scale, menu.NameList, self.current_popu_prow, self.battle_map_base.terrain_list,
                                                           self.popup_namegroup, self.popup_listbox, self.battle_ui, layer=17)
                                            elif self.popup_listbox.type == "feature":
                                                setup_list(self.screen_scale, menu.NameList, self.current_popu_prow, self.battle_map_feature.feature_list,
                                                           self.popup_namegroup, self.popup_listbox, self.battle_ui, layer=17)
                                            elif self.popup_listbox.type == "weather":
                                                setup_list(self.screen_scale, menu.NameList, self.current_popu_prow, self.weather_list,
                                                           self.popup_namegroup,
                                                           self.popup_listbox, self.battle_ui, layer=17)
                                            elif self.popup_listbox.type == "leader":
                                                setup_list(self.screen_scale, menu.NameList, self.current_popu_prow, self.leader_list,
                                                           self.popup_namegroup,
                                                           self.popup_listbox, self.battle_ui, layer=19)

                                        else:
                                            self.battle_ui.remove(self.popup_listbox, self.popup_listscroll, *self.popup_namegroup)

                                    elif self.troop_scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroll
                                        self.ui_click = True
                                        self.current_troop_row = self.troop_scroll.user_input(
                                            self.mouse_pos)  # update the scroll and get new current subsection
                                        if self.current_list_show == "troop":
                                            setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list, self.troop_namegroup,
                                                       self.troop_listbox, self.battle_ui)
                                        elif self.current_list_show == "faction":
                                            setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.faction_list, self.troop_namegroup,
                                                       self.troop_listbox, self.battle_ui)

                                    elif self.unit_preset_name_scroll.rect.collidepoint(self.mouse_pos):
                                        self.ui_click = True
                                        self.current_unit_row = self.unit_preset_name_scroll.user_input(
                                            self.mouse_pos)  # update the scroll and get new current subsection
                                        setup_list(self.screen_scale, menu.NameList, self.current_unit_row, list(self.custom_unit_preset_list.keys()),
                                                   self.unitpreset_namegroup, self.unit_listbox, self.battle_ui)  # setup preset army list

                                    elif self.unit_build_slot in self.battle_ui:
                                        clicked_slot = None
                                        for slot in self.unit_build_slot:  # left click on any sub-subunit slot
                                            if slot.rect.collidepoint(self.mouse_pos):
                                                self.ui_click = True
                                                clicked_slot = slot
                                                break

                                        if clicked_slot is not None:
                                            if key_state[pygame.K_LSHIFT] or key_state[pygame.K_RSHIFT]:  # add all sub-subunit from the first selected
                                                first_one = None
                                                for new_slot in self.unit_build_slot:
                                                    if new_slot.army_id == clicked_slot.armyid and new_slot.game_id <= clicked_slot.gameid:
                                                        if first_one is None and new_slot.selected:  # found the previous selected sub-subunit
                                                            first_one = new_slot.game_id
                                                            if clicked_slot.gameid <= first_one:  # cannot go backward, stop loop
                                                                break
                                                            elif clicked_slot.selected is False:  # forward select, acceptable
                                                                clicked_slot.selected = True
                                                                self.unit_edit_border.add(
                                                                    battleui.SelectedSquad(clicked_slot.inspect_pos, 5))
                                                                self.battle_ui.add(*self.unit_edit_border)
                                                        elif first_one is not None and new_slot.game_id > first_one and new_slot.selected is False:  # select from first select to clicked
                                                            new_slot.selected = True
                                                            self.unit_edit_border.add(
                                                                battleui.SelectedSquad(new_slot.inspect_pos, 5))
                                                            self.battle_ui.add(*self.unit_edit_border)

                                            elif key_state[pygame.K_LCTRL] or key_state[
                                                pygame.K_RCTRL]:  # add another selected sub-subunit with left ctrl + left mouse button
                                                if clicked_slot.selected is False:
                                                    clicked_slot.selected = True
                                                    self.unit_edit_border.add(battleui.SelectedSquad(clicked_slot.inspect_pos, 5))
                                                    self.battle_ui.add(*self.unit_edit_border)

                                            elif key_state[pygame.K_LALT] or key_state[pygame.K_RALT]:
                                                if clicked_slot.selected and len(self.unit_edit_border) > 1:
                                                    clicked_slot.selected = False
                                                    for border in self.unit_edit_border:
                                                        if border.pos == clicked_slot.inspect_pos:
                                                            border.kill()
                                                            del border
                                                            break

                                            else:  # select one sub-subunit by normal left click
                                                for border in self.unit_edit_border:  # remove all border first
                                                    border.kill()
                                                    del border
                                                for new_slot in self.unit_build_slot:
                                                    new_slot.selected = False
                                                clicked_slot.selected = True
                                                self.unit_edit_border.add(battleui.SelectedSquad(clicked_slot.inspect_pos, 5))
                                                self.battle_ui.add(*self.unit_edit_border)

                                                if clicked_slot.name != "None":
                                                    self.battle_ui.remove(*self.leader_now)
                                                    self.leader_now = [leader for leader in self.preview_leader]
                                                    self.battle_ui.add(*self.leader_now)  # add leader portrait to draw
                                                    self.show_in_card = slot
                                                    self.command_ui.value_input(who=self.show_in_card)
                                                    self.troop_card_ui.value_input(who=self.show_in_card, weapon_list=self.all_weapon,
                                                                                   armour_list=self.all_armour)  # update subunit card on selected subunit
                                                    if self.troop_card_ui.option == 2:
                                                        self.trait_skill_blit()
                                                        self.effect_icon_blit()
                                                        self.countdown_skill_icon()

                                if mouse_left_up or mouse_right_up:
                                    if self.unit_build_slot in self.battle_ui and self.troop_listbox.rect.collidepoint(self.mouse_pos):
                                        self.ui_click = True
                                        for index, name in enumerate(self.troop_namegroup):
                                            if name.rect.collidepoint(self.mouse_pos):
                                                if self.current_list_show == "faction":
                                                    self.current_troop_row = 0

                                                    if mouse_left_up:
                                                        self.faction_pick = index
                                                        self.filter_troop_list()
                                                        if index != 0:  # pick faction
                                                            self.leader_list = [item[1][0] for this_index, item in
                                                                                enumerate(self.leader_stat.leader_list.items())
                                                                                if this_index > 0 and (item[1][0] == "None" or
                                                                                                      (item[0] >= 10000 and item[1][8] in (
                                                                                                          0, index)) or
                                                                                                      item[0] in self.all_faction.faction_list[index][
                                                                                                          2])]

                                                        else:  # pick all faction
                                                            self.leader_list = self.leader_list = [item[0] for item in
                                                                                                   self.leader_stat.leader_list.values()][1:]

                                                        setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list,
                                                                   self.troop_namegroup,
                                                                   self.troop_listbox, self.battle_ui)  # setup troop name list
                                                        self.troop_scroll.change_image(new_row=self.current_troop_row,
                                                                                       log_size=len(self.troop_list))  # change troop scroll image

                                                        self.main.make_team_coa([index], ui_class=self.battle_ui, one_team=True,
                                                                                team1_set_pos=(
                                                                                  self.troop_listbox.rect.midleft[0] - int(
                                                                                      (200 * self.screen_scale[0]) / 2),
                                                                                  self.troop_listbox.rect.midleft[1]))  # change team coa_list

                                                        self.current_list_show = "troop"

                                                    elif mouse_right_up:
                                                        self.popout_lorebook(2, index)

                                                elif self.current_list_show == "troop":
                                                    if mouse_left_up:
                                                        for slot in self.unit_build_slot:
                                                            if slot.selected:
                                                                if key_state[pygame.K_LSHIFT]:  # change all sub-subunit in army
                                                                    for new_slot in self.unit_build_slot:
                                                                        if new_slot.army_id == slot.army_id:
                                                                            new_slot.change_troop(self.troop_index_list[index + self.current_troop_row],
                                                                                                 self.base_terrain, self.base_terrain * len(
                                                                                                     self.battle_map_feature.feature_list) +
                                                                                                  self.feature_terrain, self.current_weather)

                                                                else:
                                                                    slot.change_troop(self.troop_index_list[index + self.current_troop_row],
                                                                                      self.base_terrain, self.base_terrain *
                                                                                      len(self.battle_map_feature.feature_list) + self.feature_terrain,
                                                                                      self.current_weather)

                                                                if slot.name != "None":  # update information of subunit that just got changed
                                                                    self.battle_ui.remove(*self.leader_now)
                                                                    self.leader_now = [leader for leader in self.preview_leader]
                                                                    self.battle_ui.add(*self.leader_now)  # add leader portrait to draw
                                                                    self.show_in_card = slot
                                                                    self.preview_authority(self.leader_now, slot.army_id)
                                                                    self.troop_card_ui.value_input(who=self.show_in_card,
                                                                                                   weapon_list=self.all_weapon,
                                                                                                   armour_list=self.all_armour)  # update subunit card on selected subunit
                                                                    if self.troop_card_ui.option == 2:
                                                                        self.trait_skill_blit()
                                                                        self.effect_icon_blit()
                                                                        self.countdown_skill_icon()
                                                                elif slot.name == "None" and slot.leader is not None:  # remove leader from none subunit if any
                                                                    slot.leader.change_leader(1, self.leader_stat)
                                                                    slot.leader.change_subunit(None)  # remove subunit link in leader
                                                                    slot.leader = None  # remove leader link in subunit
                                                                    self.preview_authority(self.leader_now, slot.army_id)
                                                        unit_dict = self.convert_slot_dict("test")
                                                        if unit_dict is not None and unit_dict['test'][-1] == "0":
                                                            self.warning_msg.warning([self.warning_msg.multifaction_warn])
                                                            self.battle_ui.add(self.warning_msg)

                                                    elif mouse_right_up:  # open encyclopedia
                                                        self.popout_lorebook(3, self.troop_index_list[index + self.current_troop_row])
                                                break

                                    elif self.filter_box.rect.collidepoint(self.mouse_pos):
                                        self.ui_click = True
                                        if mouse_left_up:
                                            if self.team_change_button.rect.collidepoint(self.mouse_pos):
                                                if self.team_change_button.event == 0:
                                                    self.team_change_button.event = 1

                                                elif self.team_change_button.event == 1:
                                                    self.team_change_button.event = 0

                                                for slot in self.unit_build_slot:
                                                    slot.team = self.team_change_button.event + 1
                                                    slot.change_team(True)
                                                    self.command_ui.value_input(
                                                        who=slot)  # loop valueinput so it change team correctly

                                            elif self.slot_display_button.rect.collidepoint(self.mouse_pos):
                                                if self.slot_display_button.event == 0:  # hide
                                                    self.slot_display_button.event = 1
                                                    self.battle_ui.remove(self.unitsetup_stuff, self.leader_now)
                                                    self.kill_effect_icon()

                                                elif self.slot_display_button.event == 1:  # show
                                                    self.slot_display_button.event = 0
                                                    self.battle_ui.add(self.unitsetup_stuff, self.leader_now)

                                            elif self.deploy_button.rect.collidepoint(self.mouse_pos) and self.unit_build_slot in self.battle_ui:
                                                can_deploy = True
                                                subunit_count = 0
                                                warning_list = []
                                                for slot in self.unit_build_slot:
                                                    if slot.troop_id != 0:
                                                        subunit_count += 1
                                                if subunit_count < 8:
                                                    can_deploy = False
                                                    warning_list.append(self.warning_msg.eightsubunit_warn)
                                                if self.leader_now == [] or self.preview_leader[0].name == "None":
                                                    can_deploy = False
                                                    warning_list.append(self.warning_msg.mainleader_warn)

                                                if can_deploy:
                                                    unit_gameid = 0
                                                    if len(self.all_unit_index) > 0:
                                                        unit_gameid = self.all_unit_index[-1] + 1
                                                    current_preset = self.convert_slot_dict(self.unit_preset_name, [str(int(self.base_camera_pos[0])),
                                                                                                                   str(int(self.base_camera_pos[1]))],
                                                                                           unit_gameid)
                                                    subunit_gameid = 0
                                                    if len(self.subunit) > 0:
                                                        for subunit in self.subunit:
                                                            subunit_gameid = subunit.game_id
                                                        subunit_gameid = subunit_gameid + 1
                                                    for slot in self.unit_build_slot:  # just for grabing current selected team
                                                        current_preset[self.unit_preset_name] += (0, 100, 100, slot.team)
                                                        longscript.convertedit_unit(self,
                                                                                    (self.team0_unit, self.team1_unit, self.team2_unit)[slot.team],
                                                                                    current_preset[self.unit_preset_name],
                                                                                    self.team_colour[slot.team],
                                                                                    pygame.transform.scale(
                                                                                        self.coa_list[int(current_preset[self.unit_preset_name][-1])],
                                                                                        (60, 60)), subunit_gameid)
                                                        break
                                                    self.slot_display_button.event = 1
                                                    self.kill_effect_icon()
                                                    self.setup_unit_icon()
                                                    self.battle_ui.remove(self.unitsetup_stuff, self.leader_now)
                                                    for unit in self.all_unit_list:
                                                        unit.startset(self.subunit)
                                                    for subunit in self.subunit:
                                                        subunit.gamestart(self.camera_scale)
                                                    for leader in self.leader_updater:
                                                        leader.gamestart()

                                                    for unit in self.all_unit_list:
                                                        unit.command(self.battle_mouse_pos[0], False, False, self.last_mouseover, None,
                                                                     othercommand=1)
                                                else:
                                                    self.warning_msg.warning(warning_list)
                                                    self.battle_ui.add(self.warning_msg)
                                            else:
                                                for box in self.filter_tick_box:
                                                    if box in self.battle_ui and box.rect.collidepoint(self.mouse_pos):
                                                        if box.tick is False:
                                                            box.change_tick(True)
                                                        else:
                                                            box.change_tick(False)
                                                        if box.option == "meleeinf":
                                                            self.filter_troop[0] = box.tick
                                                        elif box.option == "rangeinf":
                                                            self.filter_troop[1] = box.tick
                                                        elif box.option == "meleecav":
                                                            self.filter_troop[2] = box.tick
                                                        elif box.option == "rangecav":
                                                            self.filter_troop[3] = box.tick
                                                        if self.current_list_show == "troop":
                                                            self.current_troop_row = 0
                                                            self.filter_troop_list()
                                                            setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list,
                                                                       self.troop_namegroup,
                                                                       self.troop_listbox, self.battle_ui)  # setup troop name list
                                    elif self.terrain_change_button.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # change map terrain button
                                        self.ui_click = True
                                        self.popup_list_newopen(self.terrain_change_button.rect.midtop, self.battle_map_base.terrain_list, "terrain")

                                    elif self.feature_change_button.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # change map feature button
                                        self.ui_click = True
                                        self.popup_list_newopen(self.feature_change_button.rect.midtop, self.battle_map_feature.feature_list, "feature")

                                    elif self.weather_change_button.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # change map weather button
                                        self.ui_click = True
                                        self.popup_list_newopen(self.weather_change_button.rect.midtop, self.weather_list, "weather")

                                    elif self.unit_delete_button.rect.collidepoint(self.mouse_pos) and mouse_left_up and \
                                            self.unit_delete_button in self.battle_ui:  # delete preset button
                                        self.ui_click = True
                                        if self.unit_preset_name == "":
                                            pass
                                        else:
                                            self.text_input_popup = ("confirm_input", "delete_preset")
                                            self.confirm_ui.change_instruction("Delete Selected Preset?")
                                            self.battle_ui.add(*self.confirm_ui_popup)

                                    elif self.unit_save_button.rect.collidepoint(self.mouse_pos) and mouse_left_up and \
                                            self.unit_save_button in self.battle_ui:  # save preset button
                                        self.ui_click = True
                                        self.text_input_popup = ("text_input", "save_unit")

                                        if self.unit_preset_name == "":
                                            self.input_box.text_start("")
                                        else:
                                            self.input_box.text_start(self.unit_preset_name)

                                        self.input_ui.change_instruction("Preset Name:")
                                        self.battle_ui.add(*self.input_ui_popup)

                                    elif self.warning_msg in self.battle_ui and self.warning_msg.rect.collidepoint(self.mouse_pos):
                                        self.battle_ui.remove(self.warning_msg)

                                    elif self.team_coa in self.battle_ui:
                                        for team in self.team_coa:
                                            if team.rect.collidepoint(self.mouse_pos) and mouse_left_up:
                                                self.ui_click = True
                                                if self.current_list_show == "troop":
                                                    self.current_troop_row = 0
                                                    setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.faction_list,
                                                               self.troop_namegroup,
                                                               self.troop_listbox, self.battle_ui)
                                                    self.troop_scroll.change_image(new_row=self.current_troop_row,
                                                                                   log_size=len(self.faction_list))  # change troop scroll image
                                                    self.current_list_show = "faction"

                    if self.last_selected is not None:
                        if self.game_state == 1 and self.last_selected.state != 100:
                            if self.before_selected is None:  # add back the pop up ui so it get shown when click subunit with none selected before
                                self.battle_ui.add(self.unitstat_ui, self.command_ui)  # add leader and top ui
                                self.battle_ui.add(self.inspect_button)  # add inspection ui open/close button

                                self.add_behaviour_ui(self.last_selected)

                            elif self.before_selected != self.last_selected or self.split_happen:  # change subunit information when select other unit
                                if self.inspect:  # change inspect ui
                                    self.new_unit_click = True
                                    self.battle_ui.remove(*self.inspect_subunit)

                                    self.subunit_selected = None
                                    for index, subunit in enumerate(self.last_selected.subunit_sprite_array.flat):
                                        if subunit is not None:
                                            self.inspect_subunit[index].add_subunit(subunit)
                                            self.battle_ui.add(self.inspect_subunit[index])
                                            if self.subunit_selected is None:
                                                self.subunit_selected = self.inspect_subunit[index]

                                    self.subunit_selected_border.pop(self.subunit_selected.pos)
                                    self.battle_ui.add(self.subunit_selected_border)
                                    self.troop_card_ui.value_input(who=self.subunit_selected.who, weapon_list=self.all_weapon, armour_list=self.all_armour,
                                                                   split=self.split_happen)
                                self.battle_ui.remove(*self.leader_now)

                                self.add_behaviour_ui(self.last_selected, else_check=True)

                                if self.split_happen:  # end split check
                                    self.split_happen = False

                            else:  # Update topbar and command ui value every 1.1 seconds
                                if self.ui_timer >= 1.1:
                                    self.unitstat_ui.value_input(who=self.last_selected, split=self.split_happen)
                                    self.command_ui.value_input(who=self.last_selected, split=self.split_happen)

                        elif self.game_state == 2 and self.unit_build_slot not in self.battle_ui:
                            if (mouse_right_up or mouse_right_down) and self.ui_click is False:  # Unit placement
                                self.last_selected.placement(self.battle_mouse_pos[1], mouse_right_up, mouse_right_down, double_mouse_right)

                            if key_state[pygame.K_DELETE]:
                                for unit in self.troop_number_sprite:
                                    if unit.who == self.last_selected:
                                        unit.delete()
                                        unit.kill()
                                        del unit
                                for subunit in self.last_selected.subunit_sprite:
                                    subunit.delete()
                                    self.all_subunit_list.remove(subunit)
                                    subunit.kill()
                                    del subunit
                                for leader in self.last_selected.leader:
                                    leader.delete()
                                    leader.kill()
                                    del leader
                                del [self.team0_pos_list, self.team1_pos_list, self.team2_pos_list][self.last_selected.team][
                                    self.last_selected.game_id]
                                self.last_selected.delete()
                                self.last_selected.kill()
                                self.all_unit_list.remove(self.last_selected)
                                self.all_unit_index.remove(self.last_selected.game_id)
                                self.setup_unit_icon()
                                self.last_selected = None

                    # v Update value of the clicked subunit every 1.1 second
                    if self.game_state == 1 and self.inspect and ((self.ui_timer >= 1.1 and self.troop_card_ui.option != 0) or
                                                                  self.before_selected != self.last_selected):
                        self.troop_card_ui.value_input(who=self.subunit_selected.who, weapon_list=self.all_weapon, armour_list=self.all_armour,
                                                       split=self.split_happen)
                        if self.troop_card_ui.option == 2:  # skill and status effect card
                            self.countdown_skill_icon()
                            self.effect_icon_blit()
                            if self.before_selected != self.last_selected:  # change subunit, reset trait icon as well
                                self.trait_skill_blit()
                                self.countdown_skill_icon()
                        else:
                            self.kill_effect_icon()
                    # ^ End update value

                    # v Drama text function
                    if self.drama_timer == 0 and len(self.drama_text.queue) != 0:  # Start timer and add to allui If there is event queue
                        self.battle_ui.add(self.drama_text)
                        self.drama_text.process_queue()
                        self.drama_timer = 0.1
                    elif self.drama_timer > 0:
                        self.drama_text.play_animation()
                        self.drama_timer += self.ui_dt
                        if self.drama_timer > 3:
                            self.drama_timer = 0
                            self.battle_ui.remove(self.drama_text)
                    # ^ End drama

                    if self.dt > 0:
                        self.team_troopnumber = [1, 1, 1]  # reset troop count

                        # v Event log timer
                        if self.event_schedule is not None and self.event_list != [] and self.time_number.time_number >= self.event_schedule:
                            self.eventlog.add_log(None, None, event_id=self.event_id)
                            for event in self.eventlog.map_event:
                                if self.eventlog.map_event[event][3] is not None and self.eventlog.map_event[event][3] > self.time_number.time_number:
                                    self.event_id = event
                                    self.event_schedule = self.eventlog.map_event[event][3]
                                    break
                            self.event_list = self.event_list[1:]
                        # ^ End event log timer

                        # v Weather system
                        if self.weather_current is not None and self.time_number.time_number >= self.weather_current:
                            del self.current_weather
                            this_weather = self.weather_event[0]

                            if this_weather[0] != 0:
                                self.current_weather = weather.Weather(self.time_ui, this_weather[0], this_weather[2], self.all_weather)
                            else:  # Random weather
                                self.current_weather = weather.Weather(self.time_ui, random.randint(0, 11), random.randint(0, 2),
                                                                       self.all_weather)
                            self.weather_event.pop(0)
                            self.show_map.add_effect(self.battle_map_height,
                                                     self.weather_effect_imgs[self.current_weather.weather_type][self.current_weather.level])

                            if len(self.weather_event) > 0:  # Get end time of next event which is now index 0
                                self.weather_current = self.weather_event[0][1]
                            else:
                                self.weather_current = None

                        if self.current_weather.spawn_rate > 0 and len(self.weather_matter) < self.current_weather.speed:
                            spawn_number = range(0,
                                             int(self.current_weather.spawn_rate * self.dt * random.randint(0,
                                                                                                            10)))  # number of sprite to spawn at this time
                            for spawn in spawn_number:  # spawn each weather sprite
                                true_pos = (random.randint(10, self.screen_rect.width), 0)  # starting pos
                                target = (true_pos[0], self.screen_rect.height)  # final base_target pos

                                if self.current_weather.spawn_angle == 225:  # top right to bottom left movement
                                    start_pos = random.randint(10, self.screen_rect.width * 2)  # starting x pos that can be higher than screen width
                                    true_pos = (start_pos, 0)
                                    if start_pos >= self.screen_rect.width:  # x higher than screen width will spawn on the right corner of screen but not at top
                                        start_pos = self.screen_rect.width  # revert x back to screen width
                                        true_pos = (start_pos, random.randint(0, self.screen_rect.height))

                                    if true_pos[1] > 0:  # start position simulate from beyond top right of screen
                                        target = (true_pos[1] * self.weatherscreenadjust, self.screen_rect.height)
                                    elif true_pos[0] < self.screen_rect.width:  # start position inside screen width
                                        target = (0, true_pos[0] / self.weatherscreenadjust)

                                elif self.current_weather.spawn_angle == 270:  # right to left movement
                                    true_pos = (self.screen_rect.width, random.randint(0, self.screen_rect.height))
                                    target = (0, true_pos[1])

                                random_pic = random.randint(0, len(self.weather_matter_imgs[self.current_weather.weather_type]) - 1)
                                self.weather_matter.add(weather.MatterSprite(true_pos, target,
                                                                             self.current_weather.speed,
                                                                             self.weather_matter_imgs[self.current_weather.weather_type][
                                                                                random_pic]))
                        # ^ End weather system

                        # v Music System
                        if len(self.music_schedule) > 0 and self.time_number.time_number >= self.music_schedule[0]:
                            pygame.mixer.music.unload()
                            self.music_current = self.music_event[0].copy()
                            self.pickmusic = random.randint(0, len(self.music_current) - 1)
                            pygame.mixer.music.load(self.musiclist[self.music_current[self.pickmusic]])
                            pygame.mixer.music.play(fade_ms=100)
                            self.music_schedule = self.music_schedule[1:]
                            self.music_event = self.music_event[1:]
                        # ^ End music system

                        for unit in self.all_unit_list:
                            unit.collide = False  # reset collide

                        if len(self.all_subunit_list) > 1:
                            tree = KDTree(
                                [sprite.base_pos for sprite in self.all_subunit_list])  # collision loop check, much faster than pygame collide check
                            collisions = tree.query_pairs(self.collide_distance)
                            for one, two in collisions:
                                sprite_one = self.all_subunit_list[one]
                                sprite_two = self.all_subunit_list[two]
                                if sprite_one.parentunit != sprite_two.parentunit:  # collide with subunit in other unit
                                    if sprite_one.base_pos.distance_to(sprite_one.base_pos) < self.full_distance:
                                        sprite_one.fullmerge.append(sprite_two)
                                        sprite_two.fullmerge.append(sprite_one)

                                    if sprite_one.front_pos.distance_to(sprite_two.base_pos) < self.front_distance:  # first subunit collision
                                        if sprite_one.team != sprite_two.team:  # enemy team
                                            sprite_one.enemy_front.append(sprite_two)
                                            sprite_one.parentunit.collide = True
                                        elif sprite_one.state in (2, 4, 6, 10, 11, 13) or \
                                                sprite_two.state in (2, 4, 6, 10, 11, 13):  # cannot run pass other unit if either run or in combat
                                            sprite_one.friend_front.append(sprite_two)
                                            sprite_one.parentunit.collide = True
                                        sprite_one.collide_penalty = True
                                    else:
                                        if sprite_one.team != sprite_two.team:  # enemy team
                                            sprite_one.enemy_side.append(sprite_two)
                                    if sprite_two.front_pos.distance_to(sprite_one.base_pos) < self.front_distance:  # second subunit
                                        if sprite_one.team != sprite_two.team:  # enemy team
                                            sprite_two.enemy_front.append(sprite_one)
                                            sprite_two.parentunit.collide = True
                                        elif sprite_one.state in (2, 4, 6, 10, 11, 13) or \
                                                sprite_two.state in (2, 4, 6, 10, 11, 13):
                                            sprite_two.friend_front.append(sprite_one)
                                            sprite_two.parentunit.collide = True
                                        sprite_two.collide_penalty = True
                                    else:
                                        if sprite_one.team != sprite_two.team:  # enemy team
                                            sprite_two.enemy_side.append(sprite_one)

                                else:  # collide with subunit in same unit
                                    if sprite_one.front_pos.distance_to(sprite_two.base_pos) < self.front_distance:  # first subunit collision
                                        if sprite_one.base_pos.distance_to(sprite_one.base_pos) < self.full_distance:
                                            sprite_one.fullmerge.append(sprite_two)
                                            sprite_two.fullmerge.append(sprite_one)

                                        if sprite_one.state in (2, 4, 6, 10, 11, 12, 13, 99) or \
                                                sprite_two.state in (2, 4, 6, 10, 11, 12, 13):
                                            sprite_one.same_front.append(sprite_two)
                                    if sprite_two.front_pos.distance_to(sprite_one.base_pos) < self.front_distance:  # second subunit
                                        # if sprite_one.frontline:
                                        if sprite_one.state in (2, 4, 6, 10, 11, 12, 13, 99) or \
                                                sprite_two.state in (2, 4, 6, 10, 11, 12, 13):
                                            sprite_two.same_front.append(sprite_one)

                        self.subunit_pos_array = self.map_move_array.copy()
                        for subunit in self.all_subunit_list:
                            for y in subunit.posrange[0]:
                                for x in subunit.posrange[1]:
                                    self.subunit_pos_array[x][y] = 0

                    # v Updater
                    self.unit_updater.update(self.current_weather, self.subunit, self.dt, self.camera_scale,
                                             self.battle_mouse_pos[0], mouse_left_up)
                    self.last_mouseover = None  # reset last parentunit mouse over

                    self.leader_updater.update()
                    self.subunit_updater.update(self.current_weather, self.dt, self.camera_scale, self.combat_timer,
                                                self.battle_mouse_pos[0], mouse_left_up)

                    # v Run pathfinding for melee combat no more than limit number of subunit per update to prevent stutter
                    if len(self.combat_path_queue) > 0:
                        run = 0
                        while len(self.combat_path_queue) > 0 and run < 5:
                            self.combat_path_queue[0].combat_pathfind()
                            self.combat_path_queue = self.combat_path_queue[1:]
                            run += 1
                    # ^ End melee pathfinding

                    # v Remove the subunit ui when click at empty space
                    if mouse_left_up and self.click_any is False:  # not click at any parentunit
                        if self.last_selected is not None:  # any parentunit is selected
                            self.last_selected = None  # reset last_selected
                            self.before_selected = None  # reset before selected parentunit after remove last selected
                            self.remove_unit_ui()
                            if self.game_state == 2 and self.slot_display_button.event == 0:  # add back ui again for when unit editor ui displayed
                                self.battle_ui.add(self.unitsetup_stuff, self.leader_now)
                    # ^ End remove

                    if self.ui_timer > 1:
                        self.scale_ui.change_fight_scale(self.team_troopnumber)  # change fight colour scale on time_ui bar
                        self.last_team_troopnumber = self.team_troopnumber

                    if self.combat_timer >= 0.5:  # reset combat timer every 0.5 seconds
                        self.combat_timer -= 0.5  # not reset to 0 because higher speed can cause inconsistency in update timing

                    self.effect_updater.update(self.subunit, self.dt, self.camera_scale)
                    self.weather_updater.update(self.dt, self.time_number.time_number)
                    self.mini_map.update(self.camera_scale, [self.camera_pos, self.cameraupcorner], self.team1_pos_list, self.team2_pos_list)

                    self.ui_updater.update()  # update ui
                    self.camera.update(self.camera_pos, self.battle_camera, self.camera_scale)
                    # ^ End battle updater

                    # v Update self time
                    self.dt = self.clock.get_time() / 1000  # dt before game_speed
                    if self.ui_timer >= 1.1:  # reset ui timer every 1.1 seconds
                        self.ui_timer -= 1.1
                    self.ui_timer += self.dt  # ui update by real time instead of self time to reduce workload
                    self.ui_dt = self.dt  # get ui timer before apply self

                    self.dt = self.dt * self.game_speed  # apply dt with game_speed for ingame calculation
                    if self.dt > 0.1:
                        self.dt = 0.1  # make it so stutter does not cause sprite to clip other sprite especially when zoom change

                    self.combat_timer += self.dt  # update combat timer
                    self.time_number.timerupdate(self.dt * 10)  # update ingame time with 5x speed

                    if self.mode == "battle" and (len(self.team1_unit) <= 0 or len(self.team2_unit) <= 0):
                        if self.battledone_box not in self.battle_ui:
                            if len(self.team1_unit) <= 0 and len(self.team2_unit) <= 0:
                                team_win = 0  # draw
                            elif len(self.team2_unit) <= 0:
                                team_win = 1
                            else:
                                team_win = 2
                            if team_win != 0:
                                for index, coa in enumerate(self.team_coa):
                                    if index == team_win - 1:
                                        self.battledone_box.pop(coa.name)
                                        break
                            else:
                                self.battledone_box.pop("Draw")
                            self.gamedone_button.rect = self.gamedone_button.image.get_rect(midtop=self.gamedone_button.pos)
                            self.battle_ui.add(self.battledone_box, self.gamedone_button)
                        else:
                            if mouse_left_up and self.gamedone_button.rect.collidepoint(self.mouse_pos):
                                self.game_state = 3  # end battle mode, result screen
                                self.game_speed = 0
                                coa_list = [None, None]
                                for index, coa in enumerate(self.team_coa):
                                    coa_list[index] = coa.image
                                self.battledone_box.show_result(coa_list[0], coa_list[1], [self.start_troopnumber, self.team_troopnumber,
                                                                                         self.wound_troopnumber, self.death_troopnumber,
                                                                                         self.flee_troopnumber, self.capture_troopnumber])
                                self.gamedone_button.rect = self.gamedone_button.image.get_rect(center=(self.battledone_box.rect.midbottom[0],
                                                                                                        self.battledone_box.rect.midbottom[1] / 1.3))

                        # print('end', self.team_troopnumber, self.last_team_troopnumber, self.start_troopnumber, self.wound_troopnumber,
                        #       self.death_troopnumber, self.flee_troopnumber, self.capture_troopnumber)
                    # ^ End update self time

                elif self.game_state == 0:  # Complete self pause when open either esc menu or enclycopedia
                    command = self.escmenu_process(mouse_left_up, mouse_left_down, esc_press, mouse_scroll_up, mouse_scroll_down, self.battle_ui)
                    if command == "end_battle":
                        return

            elif self.text_input_popup != (None, None):  # currently have input text pop up on screen, stop everything else until done
                for button in self.input_button:
                    button.update(self.mouse_pos, mouse_left_up, mouse_left_down, "any")

                if self.input_ok_button.event:
                    self.input_ok_button.event = False

                    if self.text_input_popup[1] == "save_unit":
                        current_preset = self.convert_slot_dict(self.input_box.text)
                        if current_preset is not None:
                            self.custom_unit_preset_list.update(current_preset)

                            self.unit_preset_name = self.input_box.text
                            setup_list(self.screen_scale, menu.NameList, self.current_unit_row, list(self.custom_unit_preset_list.keys()),
                                       self.unitpreset_namegroup, self.unit_listbox, self.battle_ui)  # setup preset unit list
                            for name in self.unitpreset_namegroup:  # loop to change selected border position to the last in preset list
                                if name.name == self.unit_preset_name:
                                    self.preset_select_border.change_pos(name.rect.topleft)
                                    break

                            self.save_preset()
                        else:
                            self.warning_msg.warning([self.warning_msg.eightsubunit_warn])
                            self.battle_ui.add(self.warning_msg)

                    elif self.text_input_popup[1] == "delete_preset":
                        del self.custom_unit_preset_list[self.unit_preset_name]
                        self.unit_preset_name = ""
                        setup_list(self.screen_scale, menu.NameList, self.current_unit_row, list(self.custom_unit_preset_list.keys()),
                                   self.unitpreset_namegroup, self.unit_listbox, self.battle_ui)  # setup preset unit list
                        for name in self.unitpreset_namegroup:  # loop to change selected border position to the first in preset list
                            self.preset_select_border.change_pos(name.rect.topleft)
                            break

                        self.save_preset()

                    elif self.text_input_popup[1] == "quit":
                        self.battle_ui.clear(self.screen, self.background)
                        self.battle_camera.clear(self.screen, self.background)
                        pygame.quit()
                        sys.exit()

                    self.input_box.text_start("")
                    self.text_input_popup = (None, None)
                    self.battle_ui.remove(*self.input_ui_popup, *self.confirm_ui_popup)

                elif self.input_cancel_button.event or esc_press:
                    self.input_cancel_button.event = False
                    self.input_box.text_start("")
                    self.text_input_popup = (None, None)
                    self.battle_ui.remove(*self.input_ui_popup, *self.confirm_ui_popup)

            self.screen.blit(self.camera.image, (0, 0))  # Draw the self camera and everything that appear in it
            self.battle_ui.draw(self.screen)  # Draw the UI
            pygame.display.update()  # update self display, draw everything
            self.clock.tick(60)  # clock update even if self pause
