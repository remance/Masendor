import csv
import datetime
import glob
import os
import random
import sys

import pygame
import pygame.freetype
from gamescript import camera, map, weather, battleui, menu, subunit, unit, leader
from gamescript.common import utility, escmenu, editor

from pygame.locals import *
from scipy.spatial import KDTree

load_image = utility.load_image
load_images = utility.load_images
csv_read = utility.csv_read
load_sound = utility.load_sound
editconfig = utility.edit_config
setup_list = utility.setup_list


def change_battle_genre(genre):
    if genre == "tactical":
        from gamescript.tactical.battle import setup, user
        from gamescript.tactical.unit import combat
        from gamescript.tactical.subunit import fight
        from gamescript.tactical.editor import convert
        from gamescript.tactical.ui import selector
    elif genre == "arcade":
        from gamescript.arcade.subunit import fight, spawn, movement

    Battle.split_unit = combat.split_unit
    Battle.check_split = combat.check_split
    Battle.unit_setup = setup.unit_setup
    Battle.convert_edit_unit = convert.convert_edit_unit
    Battle.setup_unit_icon = selector.setup_unit_icon
    Battle.battle_mouse_scrolling = user.battle_mouse_scrolling
    Battle.battle_key_press = user.battle_key_press
    Battle.battle_mouse = user.battle_mouse
    Battle.battle_state_mouse = user.battle_state_mouse
    Battle.selected_unit_process = user.selected_unit_process


class Battle:
    trait_skill_blit = utility.trait_skill_blit
    effect_icon_blit = utility.effect_icon_blit
    countdown_skill_icon = utility.countdown_skill_icon
    kill_effect_icon = utility.kill_effect_icon
    popout_lorebook = utility.popout_lorebook
    popup_list_new_open = utility.popup_list_open
    escmenu_process = escmenu.escmenu_process
    editor_map_change = editor.editor_map_change
    save_preset = editor.save_preset
    convert_slot_dict = editor.convert_slot_dict
    preview_authority = editor.preview_authority
    filter_troop_list = editor.filter_troop_list

    # method that change based on genre
    split_unit = None
    check_split = None
    unit_setup = None
    convert_edit_unit = None
    setup_unit_icon = None
    battle_mouse_scrolling = None
    battle_key_press = None
    battle_mouse = None
    battle_state_mouse = None
    selected_unit_process = None

    def __init__(self, main, window_style):
        # v Get self object/variable from gamestart
        self.mode = None  # battle map mode can be "uniteditor" for unit editor or "battle" for self battle
        self.main = main
        self.genre = main.genre

        self.config = main.config
        self.master_volume = main.master_volume
        self.screen_rect = main.screen_rect
        self.team_colour = main.team_colour
        self.main_dir = main.main_dir
        self.screen_scale = main.screen_scale
        self.event_log = main.event_log
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

        self.inspect_ui_pos = main.inspect_ui_pos
        self.inspect_subunit = main.inspect_subunit

        self.battle_map_base = main.battle_base_map
        self.battle_map_feature = main.battle_feature_map
        self.battle_map_height = main.battle_height_map
        self.show_map = main.show_map

        self.mini_map = main.mini_map
        self.event_log = main.event_log
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
        self.subunit_build = main.subunit_build
        self.unit_edit_border = main.unit_edit_border
        self.preview_leader = main.preview_leader
        self.unitpreset_namegroup = main.unitpreset_namegroup
        self.preset_select_border = main.preset_select_border
        self.custom_unit_preset_list = main.custom_unit_preset_list
        self.unit_listbox = main.unit_listbox
        self.troop_scroll = main.troop_scroll
        self.faction_list = main.faction_list
        self.popup_list_scroll = main.popup_list_scroll
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
        self.weather_matter_images = main.weather_matter_images
        self.weather_effect_images = main.weather_effect_images
        self.weather_list = main.weather_list

        self.feature_mod = main.feature_mod

        self.all_faction = main.all_faction
        self.coa_list = main.coa_list

        self.all_weapon = main.all_weapon
        self.all_armour = main.all_armour

        self.status_images = main.status_images
        self.role_images = main.role_images
        self.trait_images = main.trait_images
        self.skill_images = main.skill_images

        self.troop_data = main.troop_data
        self.leader_stat = main.leader_stat

        self.state_text = main.state_text

        self.max_camera = (999 * self.screen_scale[0], 999 * self.screen_scale[1])
        self.sprite_width = main.icon_sprite_width
        self.sprite_height = main.icon_sprite_height
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

        self.battle_done_box = main.battle_done_box
        self.battle_done_button = main.battle_done_button
        # ^ End load from gamestart

        self.weather_screen_adjust = self.screen_rect.width / self.screen_rect.height  # for weather sprite spawn position
        self.right_corner = self.screen_rect.width - (5 * self.screen_scale[0])
        self.bottom_corner = self.screen_rect.height - (5 * self.screen_scale[1])
        self.center_screen = [self.screen_rect.width / 2, self.screen_rect.height / 2]  # center position of the screen

        self.game_speed = 0
        self.game_speed_list = (0, 0.5, 1, 2, 4, 6)  # available game speed
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

        self.unitsetup_stuff = (self.subunit_build, self.unit_edit_border, self.command_ui, self.troop_card_ui,
                                self.team_coa, self.troop_card_button, self.troop_listbox, self.troop_scroll,
                                self.troop_namegroup, self.unit_listbox, self.preset_select_border,
                                self.unitpreset_namegroup, self.unit_save_button, self.unit_delete_button,
                                self.unit_preset_name_scroll)
        self.filter_stuff = (self.filter_box, self.slot_display_button, self.team_change_button, self.deploy_button, self.terrain_change_button,
                             self.feature_change_button, self.weather_change_button, self.filter_tick_box)

        self.best_depth = pygame.display.mode_ok(self.screen_rect.size, window_style, 32)  # Set the display mode
        self.screen = pygame.display.set_mode(self.screen_rect.size, window_style | pygame.RESIZABLE, self.best_depth)  # set up self screen

        # v Assign default variable to some class
        unit.Unit.battle = self
        unit.Unit.image_size = (self.sprite_width, self.sprite_height)
        subunit.Subunit.battle = self
        leader.Leader.battle = self
        # ^ End assign default

        self.background = pygame.Surface(self.screen_rect.size)  # Create background image
        self.background.fill((255, 255, 255))  # fill background image with black colour

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
            utility.convert_str_time(self.weather_event)
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
                    utility.convert_str_time(self.music_event)
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
            map_event = csv_read("event_log.csv",
                                 [self.main_dir, "data", "ruleset", self.ruleset_folder, "map", self.mapselected, self.source], 0)
            battleui.EventLog.map_event = map_event
        except Exception:  # can't find any event file
            map_event = {}  # create empty list

        self.event_log.make_new_log()  # reset old event log

        self.event_log.add_event_log(map_event)

        self.event_schedule = None
        self.event_list = []
        for index, event in enumerate(self.event_log.map_event):
            if self.event_log.map_event[event][3] is not None:
                if index == 0:
                    self.event_id = event
                    self.event_schedule = self.event_log.map_event[event][3]
                self.event_list.append(event)

        self.time_number.start_setup(self.weather_current)

        # v Create the battle map
        self.camera_pos = pygame.Vector2(500 * self.screen_scale[0],
                                         500 * self.screen_scale[1])  # Camera pos at the current zoom, start at center of map
        self.base_camera_pos = pygame.Vector2(500 * self.screen_scale[0],
                                              500 * self.screen_scale[1])  # Camera pos at furthest zoom for recalculate sprite pos after zoom
        self.camera_scale = 1  # Camera zoom
        camera.Camera.screen_rect = self.screen_rect
        self.camera = camera.Camera(self.camera_pos, self.camera_scale)

        if map_selected is not None:
            images = load_images(self.main_dir, (1, 1), ["ruleset", self.ruleset_folder, "map", self.mapselected], load_order=False)
            self.battle_map_base.draw_image(images["base.png"])
            self.battle_map_feature.draw_image(images["feature.png"])
            self.battle_map_height.draw_image(images["height.png"])

            try:  # place_name map layer is optional, if not existed in folder then assign None
                place_name_map = images[3]
            except Exception:
                place_name_map = None
            self.show_map.draw_image(self.battle_map_base, self.battle_map_feature, self.battle_map_height, place_name_map, self, False)
        else:  # for unit editor mode, create empty temperate glass map
            self.editor_map_change((166, 255, 107), (181, 230, 29))
        # ^ End create battle map

        self.clock = pygame.time.Clock()  # Game clock to keep track of realtime pass

        self.enactment = enactment  # enactment mod, control both team

        self.team0_pos_list = {}  # team 0 unit position
        self.team1_pos_list = {}  # team 1 unit position
        self.team2_pos_list = {}  # same for team 2

        self.all_unit_list = []  # list of every unit in self alive
        self.all_unit_index = []  # list of every unit index alive

        self.all_subunit_list = []  # list of all subunit alive in self

        # v initialise starting subunit sprites
        self.mode = mode
        if self.mode == "battle":
            self.start_troopnumber = [0, 0, 0]
            self.wound_troopnumber = [0, 0, 0]
            self.death_troopnumber = [0, 0, 0]
            self.flee_troopnumber = [0, 0, 0]
            self.capture_troopnumber = [0, 0, 0]
            self.unit_setup()
        # ^ End start subunit sprite

    def ui_mouse_over(self):
        """mouse over ui that is not subunit card and unitbox (topbar and commandbar)"""
        for this_ui in self.ui_updater:
            if this_ui in self.battle_ui and this_ui.rect.collidepoint(self.mouse_pos):
                self.click_any = True
                self.ui_click = True
                break
        return self.click_any

    def unit_icon_mouse_over(self, mouse_up, mouse_right):
        """process user mouse input on unit icon, left click = select, right click = go to unit position on map"""
        self.click_any = True
        self.ui_click = True
        if self.game_state == "battle" or (self.game_state == "editor" and self.subunit_build not in self.battle_ui):
            for icon in self.unit_icon:
                if icon.rect.collidepoint(self.mouse_pos):
                    if mouse_up:
                        self.last_selected = icon.army
                        self.last_selected.just_selected = True
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

    def button_mouse_over(self, mouse_right):
        """process user mouse input on various ui buttons"""
        for button in self.button_ui:
            if button in self.battle_ui and button.rect.collidepoint(self.mouse_pos):
                self.click_any = True
                self.ui_click = True  # for avoiding selecting subunit under ui
                break
        return self.click_any

    def leader_mouse_over(self, mouse_right):  # TODO make it so button and leader popup not show at same time
        """process user mouse input on leader portrait in command ui"""
        leader_mouse_over = False
        for this_leader in self.leader_now:
            if this_leader.rect.collidepoint(self.mouse_pos):
                if this_leader.unit.commander:
                    army_position = self.leader_level[this_leader.army_position]
                else:
                    army_position = self.leader_level[this_leader.army_position + 4]

                self.leader_popup.pop(self.mouse_pos, army_position + ": " + this_leader.name)  # popup leader name when mouse over
                self.battle_ui.add(self.leader_popup)
                leader_mouse_over = True

                if mouse_right:
                    self.popout_lorebook(8, this_leader.leader_id)
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
        self.battle_ui.remove(*self.ui_updater, self.troop_card_button, self.inspect_button, self.col_split_button, self.row_split_button)
        self.kill_effect_icon()
        self.battle_ui.remove(*self.switch_button, *self.inspect_subunit)  # remove change behaviour button and inspect ui subunit
        self.inspect = False  # inspect ui close
        self.battle_ui.remove(*self.leader_now)  # remove leader image from command ui
        self.subunit_selected = None  # reset subunit selected
        self.battle_ui.remove(self.subunit_selected_border)  # remove subunit selected border sprite
        self.leader_now = []  # clear leader list in command ui

    def camera_fix(self):
        if self.base_camera_pos[0] > self.max_camera[0]:  # camera cannot go further than 999 x
            self.base_camera_pos[0] = self.max_camera[0]
        elif self.base_camera_pos[0] < 0:  # camera cannot go less than 0 x
            self.base_camera_pos[0] = 0

        if self.base_camera_pos[1] > self.max_camera[1]:  # same for y
            self.base_camera_pos[1] = self.max_camera[1]
        elif self.base_camera_pos[1] < 0:
            self.base_camera_pos[1] = 0

    def add_behaviour_ui(self, who_input, else_check=False):
        if who_input.control:
            # self.battle_ui.add(self.button_ui[7])  # add decimation button
            self.battle_ui.add(*self.switch_button[0:7])  # add unit behaviour change button
            self.switch_button[0].event = who_input.skill_cond
            self.switch_button[1].event = who_input.fire_at_will
            self.switch_button[2].event = who_input.hold
            self.switch_button[3].event = who_input.use_min_range
            self.switch_button[4].event = who_input.shoot_mode
            self.switch_button[5].event = who_input.run_toggle
            self.switch_button[6].event = who_input.attack_mode
            self.check_split(who_input)  # check if selected unit can split, if yes draw button
        elif else_check:
            if self.row_split_button in self.battle_ui:
                self.row_split_button.kill()
            if self.col_split_button in self.battle_ui:
                self.col_split_button.kill()
            # self.battle_ui.remove(self.button_ui[7])  # remove decimation button
            self.battle_ui.remove(*self.switch_button[0:7])  # remove unit behaviour change button

        self.leader_now = who_input.leader
        self.battle_ui.add(*self.leader_now)  # add leader portrait to draw
        self.unitstat_ui.value_input(who=who_input, split=self.split_happen)
        self.command_ui.value_input(who=who_input, split=self.split_happen)

    def troop_card_button_click(self, who):
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

    def change_state(self):
        self.previous_game_state = self.game_state
        if self.game_state == "battle":  # change to battle state
            self.mini_map.draw_image(self.show_map.true_image, self.camera)

            if self.last_selected is not None:  # any unit is selected
                self.last_selected = None  # reset last_selected
                self.before_selected = None  # reset before selected unit after remove last selected

            self.command_ui.rect = self.command_ui.image.get_rect(
                center=self.command_ui.pos)  # change leader ui position back
            self.troop_card_ui.rect = self.troop_card_ui.image.get_rect(
                center=self.troop_card_ui.pos)  # change subunit card position back
            self.troop_card_button[0].rect = self.troop_card_button[0].image.get_rect(
                center=(self.troop_card_ui.pos[0] - 152, self.troop_card_ui.pos[1] + 10))
            self.troop_card_button[1].rect = self.troop_card_button[1].image.get_rect(
                center=(self.troop_card_ui.pos[0] - 152, self.troop_card_ui.pos[1] - 70))
            self.troop_card_button[2].rect = self.troop_card_button[2].image.get_rect(
                center=(self.troop_card_ui.pos[0] - 152, self.troop_card_ui.pos[1] - 30))
            self.troop_card_button[3].rect = self.troop_card_button[3].image.get_rect(
                center=(self.troop_card_ui.pos[0] - 152, self.troop_card_ui.pos[1] + 50))

            self.battle_ui.remove(self.filter_stuff, self.unitsetup_stuff, self.leader_now, self.button_ui, self.warning_msg)
            self.battle_ui.add(self.event_log, self.log_scroll, self.eventlog_button, self.time_button)

            self.game_speed = 1

            # v Run starting function
            for this_unit in self.all_unit_list:
                this_unit.start_set(self.subunit)
            for this_subunit in self.subunit:
                this_subunit.gamestart(self.camera_scale)
            for this_leader in self.leader_updater:
                this_leader.gamestart()
            # ^ End starting

        elif self.game_state == "editor":  # change to editor state
            self.inspect = False  # reset inspect ui
            self.mini_map.draw_image(self.show_map.true_image, self.camera)  # reset mini_map
            for arrow in self.range_attacks:  # remove all range attack
                arrow.kill()
                del arrow

            for this_unit in self.all_unit_list:  # reset all unit state
                this_unit.user_input(self.battle_mouse_pos[0], False, False, self.last_mouseover, None, other_command=2)

            self.troop_card_ui.rect = self.troop_card_ui.image.get_rect(bottomright=(self.screen_rect.width,
                                                                                     self.screen_rect.height))  # troop info card ui
            self.troop_card_button[0].rect = self.troop_card_button[0].image.get_rect(
                topleft=(self.troop_card_ui.rect.topleft[0],  # description button
                         self.troop_card_ui.rect.topleft[1] + 120))
            self.troop_card_button[1].rect = self.troop_card_button[1].image.get_rect(topleft=(self.troop_card_ui.rect.topleft[0],  # stat button
                                                                                               self.troop_card_ui.rect.topleft[1]))
            self.troop_card_button[2].rect = self.troop_card_button[2].image.get_rect(topleft=(self.troop_card_ui.rect.topleft[0],  # skill button
                                                                                               self.troop_card_ui.rect.topleft[1] + 40))
            self.troop_card_button[3].rect = self.troop_card_button[3].image.get_rect(topleft=(self.troop_card_ui.rect.topleft[0],  # equipment button
                                                                                               self.troop_card_ui.rect.topleft[1] + 80))

            self.battle_ui.remove(self.event_log, self.log_scroll, self.troop_card_button, self.col_split_button, self.row_split_button,
                                  self.eventlog_button, self.time_button, self.unitstat_ui, self.inspect_ui, self.leader_now, self.inspect_subunit,
                                  self.subunit_selected_border, self.inspect_button, self.switch_button)

            self.leader_now = [this_leader for this_leader in self.preview_leader]  # reset leader in command ui

            self.battle_ui.add(self.filter_stuff, self.unitsetup_stuff, self.test_button, self.command_ui, self.troop_card_ui, self.leader_now,
                               self.time_button)
            self.slot_display_button.event = 0  # reset display editor ui button to show
            self.game_speed = 0  # pause battle

            for slot in self.subunit_build:
                if slot.troop_id != 0:
                    self.command_ui.value_input(who=slot)
                    break

        self.speed_number.speed_update(self.game_speed)

    def exit_battle(self):
        self.battle_ui.clear(self.screen, self.background)  # remove all sprite
        self.battle_camera.clear(self.screen, self.background)  # remove all sprite

        self.battle_ui.remove(self.battle_menu, *self.battle_menu_button, *self.esc_slider_menu,
                              *self.esc_value_box, self.battle_done_box, self.battle_done_button)  # remove menu

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
                                  self.subunit_build, self.leader_now, self.preset_select_border,
                                  self.popup_listbox, self.popup_list_scroll, *self.popup_namegroup)

            for group in self.troop_namegroup, self.unit_edit_border, self.unitpreset_namegroup:
                for item in group:  # remove name list
                    item.kill()
                    del item

            for slot in self.subunit_build:  # reset all sub-subunit slot
                slot.__init__(0, slot.game_id, self.unit_build_slot, slot.pos, 100, 100, [1, 1], self.genre, "edit")
                slot.leader = None  # remove leader link in

            for this_leader in self.preview_leader:
                this_leader.change_subunit(None)  # remove subunit link in leader
                this_leader.change_preview_leader(1, self.leader_stat)

            del self.current_weather

            self.faction_pick = 0
            self.filter_troop = [True, True, True, True]
            self.troop_list = [item[0] for item in self.troop_data.troop_list.values()][
                              1:]  # reset troop filter back to all faction
            self.troop_index_list = list(range(0, len(self.troop_list) + 1))

            self.leader_list = [item[0] for item in self.leader_stat.leader_list.values()][
                               1:]  # generate leader name list)

            self.leader_now = []

    def run_game(self):
        # v Create Starting Values
        self.game_state = "battle"  # battle mode
        self.current_unit_row = 0
        self.current_troop_row = 0
        self.text_input_popup = (None, None)  # no popup asking for user text input state
        self.leader_now = []  # list of showing leader in command ui
        self.current_weather = None
        self.team_troopnumber = [1, 1, 1]  # reset list of troop number in each team
        self.last_team_troopnumber = [1, 1, 1]
        self.drama_text.queue = []  # reset drama text popup queue
        if self.mode == "uniteditor":
            self.game_state = "editor"  # editor mode

            self.troop_list = [item["Name"] for item in self.troop_data.troop_list.values()][1:]  # generate troop name list
            self.troop_index_list = list(range(0, len(self.troop_list) + 1))

            self.leader_list = [item["Name"] for item in self.leader_stat.leader_list.values()][1:]  # generate leader name list

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

            for index, slot in enumerate(self.subunit_build):  # start with the first player subunit slot selected when enter
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
        self.click_any = False  # For checking if mouse click on anything, if not close ui related to unit
        self.new_unit_click = False  # For checking if another subunit is clicked when inspect ui open
        self.inspect = False  # For checking if inspect ui is currently open or not
        self.last_selected = None  # Which unit is last selected
        self.map_mode = 0  # default, another one show height map
        self.subunit_selected = None  # which subunit in inspect ui is selected in last update loop
        self.before_selected = None  # Which unit is selected before
        self.split_happen = False  # Check if unit get split in that loop
        self.show_troop_number = True  # for toggle troop number on/off
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
            key_press = None
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
                    elif event.button == 5:  # Mouse scroll down
                        mouse_scroll_down = True

                elif event.type == pygame.KEYDOWN:
                    if self.text_input_popup[0] == "text_input":  # event update to input box
                        self.input_box.user_input(event)
                    else:
                        key_press = event.key

                if pygame.mouse.get_pressed()[0]:  # Hold left click
                    mouse_left_down = True
                elif pygame.mouse.get_pressed()[2]:  # Hold left click
                    mouse_right_down = True

            if self.text_input_popup == (None, None):
                if esc_press:  # open/close menu
                    if self.game_state in ("battle", "editor"):  # in battle or editor mode
                        self.game_state = "menu"  # open menu
                        self.battle_ui.add(self.battle_menu, *self.battle_menu_button)  # add menu and its buttons to drawer
                        esc_press = False  # reset esc press, so it not stops esc menu when open

                if self.game_state in ("battle", "editor"):  # self in battle state
                    # v register user input during gameplay
                    if mouse_scroll_up or mouse_scroll_down:  # Mouse scroll
                        self.battle_mouse_scrolling(mouse_scroll_up, mouse_scroll_down)

                    # keyboard input
                    if key_press is not None:
                        self.battle_key_press(key_press)

                    # v Camera movement
                    if key_state[K_s] or self.mouse_pos[1] >= self.bottom_corner:  # Camera move down
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

                    elif key_state[K_d] or self.mouse_pos[0] >= self.right_corner:  # Camera move right
                        self.base_camera_pos[0] += 4 * (11 - self.camera_scale)
                        self.camera_pos[0] = self.base_camera_pos[0] * self.camera_scale
                        self.camera_fix()

                    self.cameraupcorner = (self.camera_pos[0] - self.center_screen[0],
                                           self.camera_pos[1] - self.center_screen[1])  # calculate top left corner of camera position
                    # ^ End camera movement

                    if self.mouse_timer != 0:  # player click mouse once before
                        self.mouse_timer += self.ui_dt  # increase timer for mouse click using real time
                        if self.mouse_timer >= 0.3:  # time pass 0.3 second no longer count as double click
                            self.mouse_timer = 0

                    self.battle_mouse_pos[0] = pygame.Vector2((self.mouse_pos[0] - self.center_screen[0]) + self.camera_pos[0],
                                                              self.mouse_pos[1] - self.center_screen[1] + self.camera_pos[
                                                                  1])  # mouse pos on the map based on camera position
                    self.battle_mouse_pos[1] = self.battle_mouse_pos[0] / self.camera_scale  # mouse pos on the map at current camera zoom scale

                    if mouse_left_up or mouse_right_up or mouse_left_down or mouse_right_down:
                        self.battle_mouse(mouse_left_up, mouse_right_up, mouse_left_down, mouse_right_down, key_state)

                        if self.mini_map.rect.collidepoint(self.mouse_pos):  # mouse position on mini map
                            self.ui_click = True
                            if mouse_left_up:  # move self camera to position clicked on mini map
                                self.click_any = True
                                pos_mask = pygame.Vector2(int(self.mouse_pos[0] - self.mini_map.rect.x),
                                                          int(self.mouse_pos[1] - self.mini_map.rect.y))
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
                            self.unit_icon_mouse_over(mouse_left_up, mouse_right_up)

                        elif self.test_button.rect.collidepoint(self.mouse_pos) and self.test_button in self.battle_ui:
                            self.ui_click = True
                            if mouse_left_up:
                                self.click_any = True
                                if self.test_button.event == 0:
                                    self.test_button.event = 1
                                    new_mode = "battle"

                                elif self.test_button.event == 1:
                                    self.test_button.event = 0
                                    new_mode = "editor"
                                self.game_state = new_mode
                                self.change_state()

                        if self.game_state == "battle":
                            self.battle_state_mouse(mouse_left_up, mouse_right_up, double_mouse_right,
                                                    mouse_left_down, mouse_right_down, key_state, key_press)

                        elif self.game_state == "editor":  # unit editor state
                            self.editor_state_mouse(mouse_left_up, mouse_right_up, mouse_left_down, mouse_right_down, key_state, key_press)

                    self.selected_unit_process(mouse_left_up, mouse_right_up, double_mouse_right,
                                               mouse_left_down, mouse_right_down, key_state, key_press)

                    # v Drama text function
                    if self.drama_timer == 0 and len(self.drama_text.queue) != 0:  # Start timer and add to main_ui If there is event queue
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
                            self.event_log.add_log(None, None, event_id=self.event_id)
                            for event in self.event_log.map_event:
                                if self.event_log.map_event[event][3] is not None and self.event_log.map_event[event][3] > self.time_number.time_number:
                                    self.event_id = event
                                    self.event_schedule = self.event_log.map_event[event][3]
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
                                                     self.weather_effect_images[self.current_weather.weather_type][self.current_weather.level])

                            if len(self.weather_event) > 0:  # Get end time of next event which is now index 0
                                self.weather_current = self.weather_event[0][1]
                            else:
                                self.weather_current = None

                        if self.current_weather.spawn_rate > 0 and len(self.weather_matter) < self.current_weather.speed:
                            spawn_number = range(0, int(self.current_weather.spawn_rate *
                                                        self.dt * random.randint(0, 10)))  # number of sprite to spawn at this time
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
                                        target = (true_pos[1] * self.weather_screen_adjust, self.screen_rect.height)
                                    elif true_pos[0] < self.screen_rect.width:  # start position inside screen width
                                        target = (0, true_pos[0] / self.weather_screen_adjust)

                                elif self.current_weather.spawn_angle == 270:  # right to left movement
                                    true_pos = (self.screen_rect.width, random.randint(0, self.screen_rect.height))
                                    target = (0, true_pos[1])

                                random_pic = random.randint(0, len(self.weather_matter_images[self.current_weather.weather_type]) - 1)
                                self.weather_matter.add(weather.MatterSprite(true_pos, target,
                                                                             self.current_weather.speed,
                                                                             self.weather_matter_images[self.current_weather.weather_type][
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

                        for this_unit in self.all_unit_list:
                            this_unit.collide = False  # reset collide

                        if len(self.all_subunit_list) > 1:
                            tree = KDTree(
                                [sprite.base_pos for sprite in self.all_subunit_list])  # collision loop check, much faster than pygame collide check
                            collisions = tree.query_pairs(self.collide_distance)
                            for one, two in collisions:
                                sprite_one = self.all_subunit_list[one]
                                sprite_two = self.all_subunit_list[two]
                                if sprite_one.unit != sprite_two.unit:  # collide with subunit in other unit
                                    if sprite_one.base_pos.distance_to(sprite_one.base_pos) < self.full_distance:
                                        sprite_one.full_merge.append(sprite_two)
                                        sprite_two.full_merge.append(sprite_one)

                                    if sprite_one.front_pos.distance_to(sprite_two.base_pos) < self.front_distance:  # first subunit collision
                                        if sprite_one.team != sprite_two.team:  # enemy team
                                            sprite_one.enemy_front.append(sprite_two)
                                            sprite_one.unit.collide = True
                                        elif sprite_one.state in (2, 4, 6, 10, 11, 13) or \
                                                sprite_two.state in (2, 4, 6, 10, 11, 13):  # cannot run pass other unit if either run or in combat
                                            sprite_one.friend_front.append(sprite_two)
                                            sprite_one.unit.collide = True
                                        sprite_one.collide_penalty = True
                                    else:
                                        if sprite_one.team != sprite_two.team:  # enemy team
                                            sprite_one.enemy_side.append(sprite_two)
                                    if sprite_two.front_pos.distance_to(sprite_one.base_pos) < self.front_distance:  # second subunit
                                        if sprite_one.team != sprite_two.team:  # enemy team
                                            sprite_two.enemy_front.append(sprite_one)
                                            sprite_two.unit.collide = True
                                        elif sprite_one.state in (2, 4, 6, 10, 11, 13) or \
                                                sprite_two.state in (2, 4, 6, 10, 11, 13):
                                            sprite_two.friend_front.append(sprite_one)
                                            sprite_two.unit.collide = True
                                        sprite_two.collide_penalty = True
                                    else:
                                        if sprite_one.team != sprite_two.team:  # enemy team
                                            sprite_two.enemy_side.append(sprite_one)

                                else:  # collide with subunit in same unit
                                    if sprite_one.front_pos.distance_to(sprite_two.base_pos) < self.front_distance:  # first subunit collision
                                        if sprite_one.base_pos.distance_to(sprite_one.base_pos) < self.full_distance:
                                            sprite_one.full_merge.append(sprite_two)
                                            sprite_two.full_merge.append(sprite_one)

                                        if sprite_one.state in (2, 4, 6, 10, 11, 12, 13, 99) or \
                                                sprite_two.state in (2, 4, 6, 10, 11, 12, 13):
                                            sprite_one.same_front.append(sprite_two)
                                    if sprite_two.front_pos.distance_to(sprite_one.base_pos) < self.front_distance:  # second subunit
                                        # if sprite_one.frontline:
                                        if sprite_one.state in (2, 4, 6, 10, 11, 12, 13, 99) or \
                                                sprite_two.state in (2, 4, 6, 10, 11, 12, 13):
                                            sprite_two.same_front.append(sprite_one)

                        self.subunit_pos_array = self.map_move_array.copy()
                        for this_subunit in self.all_subunit_list:
                            for y in this_subunit.pos_range[0]:
                                for x in this_subunit.pos_range[1]:
                                    self.subunit_pos_array[x][y] = 0

                    # v Updater
                    self.unit_updater.update(self.current_weather, self.subunit, self.dt, self.camera_scale,
                                             self.battle_mouse_pos[0], mouse_left_up)
                    self.last_mouseover = None  # reset last unit mouse over

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
                    if mouse_left_up and self.click_any is False:  # not click at any unit
                        if self.last_selected is not None:  # any unit is selected
                            self.last_selected = None  # reset last_selected
                            self.before_selected = None  # reset before selected unit after remove last selected
                            self.remove_unit_ui()
                            if self.game_state == "editor" and self.slot_display_button.event == 0:  # add back ui again for when unit editor ui displayed
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
                        if self.battle_done_box not in self.battle_ui:
                            if len(self.team1_unit) <= 0 and len(self.team2_unit) <= 0:
                                team_win = 0  # draw
                            elif len(self.team2_unit) <= 0:
                                team_win = 1
                            else:
                                team_win = 2
                            if team_win != 0:
                                for index, coa in enumerate(self.team_coa):
                                    if index == team_win - 1:
                                        self.battle_done_box.pop(coa.name)
                                        break
                            else:
                                self.battle_done_box.pop("Draw")
                            self.battle_done_button.rect = self.battle_done_button.image.get_rect(midtop=self.battle_done_button.pos)
                            self.battle_ui.add(self.battle_done_box, self.battle_done_button)
                        else:
                            if mouse_left_up and self.battle_done_button.rect.collidepoint(self.mouse_pos):
                                self.game_state = "end"  # end battle mode, result screen
                                self.game_speed = 0
                                coa_list = [None, None]
                                for index, coa in enumerate(self.team_coa):
                                    coa_list[index] = coa.image
                                self.battle_done_box.show_result(coa_list[0], coa_list[1], [self.start_troopnumber, self.team_troopnumber,
                                                                                            self.wound_troopnumber, self.death_troopnumber,
                                                                                            self.flee_troopnumber, self.capture_troopnumber])
                                self.battle_done_button.rect = self.battle_done_button.image.get_rect(center=(self.battle_done_box.rect.midbottom[0],
                                                                                                              self.battle_done_box.rect.midbottom[
                                                                                                                  1] / 1.3))

                        # print('end', self.team_troopnumber, self.last_team_troopnumber, self.start_troopnumber, self.wound_troopnumber,
                        #       self.death_troopnumber, self.flee_troopnumber, self.capture_troopnumber)
                    # ^ End update self time

                elif self.game_state == "menu":  # Complete self pause when open either esc menu or encyclopedia
                    command = self.escmenu_process(mouse_left_up, mouse_left_down, esc_press, mouse_scroll_up, mouse_scroll_down, self.battle_ui)
                    if command == "end_battle":
                        return

            elif self.text_input_popup != (None, None):  # currently, have input text pop up on screen, stop everything else until done
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
