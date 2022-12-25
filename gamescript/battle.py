import datetime
import glob
import os
import random
import sys

import pygame
import pygame.freetype
from gamescript import camera, weather, battleui, menu, subunit, unit, leader, uniteditor, datasprite
from gamescript.common import utility

direction_list = datasprite.direction_list

from pygame.locals import *
from scipy.spatial import KDTree

from pathlib import Path

load_image = utility.load_image
load_images = utility.load_images
csv_read = utility.csv_read
load_sound = utility.load_sound
edit_config = utility.edit_config
setup_list = utility.setup_list
clean_group_object = utility.clean_group_object

script_dir = os.path.split(os.path.abspath(__file__))[0] + "/"


class Battle:
    empty_method = utility.empty_method
    popup_list_open = utility.popup_list_open

    # Import from common.battle
    camera_fix = empty_method
    camera_process = empty_method
    camera_zoom_change = empty_method
    generate_unit = empty_method
    popout_lorebook = empty_method
    remove_unit_ui = empty_method
    setup_battle_unit = empty_method
    time_update = empty_method

    # Import common.ui
    change_inspect_subunit = empty_method
    countdown_skill_icon = empty_method
    effect_icon_blit = empty_method
    effect_icon_mouse_over = empty_method
    escmenu_process = empty_method
    kill_effect_icon = empty_method
    leader_command_ui_mouse_over = empty_method
    trait_skill_icon_blit = empty_method
    troop_card_button_click = empty_method
    ui_mouse_click = empty_method
    ui_icon_mouse_over = empty_method

    # import from common.battle.uniteditor
    convert_unit_slot_to_dict = empty_method
    editor_map_change = empty_method
    filter_troop_list = empty_method
    preview_authority = empty_method
    save_custom_unit_preset = empty_method
    unit_editor_deploy = empty_method

    # import from *genre*.battle
    add_behaviour_ui = empty_method
    battle_keyboard_process = empty_method
    battle_mouse_process = empty_method
    change_battle_state = empty_method
    editor_mouse_process = empty_method
    manual_aim = empty_method
    mouse_process = empty_method
    mouse_scrolling_process = empty_method
    remove_unit_ui_check = empty_method
    selected_unit_process = empty_method
    setup_battle_ui = empty_method

    for folder in ("battle", "battle/uniteditor", "ui"):
        for entry in os.scandir(Path(script_dir + "/common/" + folder + "/")):  # load and replace modules from common
            if entry.is_file():
                if ".pyc" in entry.name:
                    file_name = entry.name[:-4]
                elif ".py" in entry.name:
                    file_name = entry.name[:-3]
                exec(f"from gamescript.common." + folder.replace("/", ".") + " import " + file_name)
                exec(f"" + file_name + " = " + file_name + "." + file_name)

    # variable that get changed based on genre
    start_zoom = 1
    max_zoom = 10
    max_camera_zoom_image_scale = 11
    start_zoom_mode = "Free"
    time_speed_scale = 1
    troop_size_adjustable = False
    add_troop_number_sprite = False

    def __init__(self, main, window_style):
        self.mode = None  # battle map mode can be "unit_editor" for unit editor or "battle" for self battle
        self.player_char = None  # player subunit for genre that allow player to directly control only one subunit
        self.main = main
        self.genre = main.genre

        self.config = main.config
        self.master_volume = main.master_volume
        self.play_troop_animation = main.play_troop_animation
        self.screen_rect = main.screen_rect
        self.main_dir = main.main_dir
        self.screen_scale = main.screen_scale
        self.event_log = main.event_log
        self.battle_camera = main.battle_camera
        self.battle_ui_updater = main.battle_ui_updater

        self.unit_updater = main.unit_updater
        self.subunit_updater = main.subunit_updater
        self.leader_updater = main.leader_updater
        self.ui_updater = main.ui_updater
        self.weather_updater = main.weather_updater
        self.effect_updater = main.effect_updater

        self.cursor = main.cursor

        self.battle_map_base = main.battle_base_map
        self.battle_map_feature = main.battle_feature_map
        self.battle_map_height = main.battle_height_map
        self.battle_map = main.battle_map

        self.damage_sprites = main.damage_sprites
        self.direction_arrows = main.direction_arrows
        self.troop_number_sprite = main.troop_number_sprite

        self.mini_map = main.mini_map
        self.event_log = main.event_log
        self.button_ui = main.button_ui
        self.inspect_selected_border = main.inspect_selected_border

        self.fps_count = main.fps_count

        self.terrain_check = main.terrain_check
        self.single_text_popup = main.single_text_popup
        self.drama_text = main.drama_text

        self.skill_icon = main.skill_icon
        self.effect_icon = main.effect_icon

        self.battle_menu = main.battle_menu
        self.battle_menu_button = main.battle_menu_button
        self.esc_option_menu_button = main.esc_option_menu_button

        self.unit_delete_button = main.unit_delete_button
        self.unit_save_button = main.unit_save_button
        self.editor_troop_list_box = main.editor_troop_list_box
        self.troop_namegroup = main.troop_namegroup
        self.filter_box = main.filter_box
        self.filter_tick_box = main.filter_tick_box
        self.team_change_button = main.team_change_button
        self.slot_display_button = main.slot_display_button
        self.test_button = main.test_button
        self.deploy_button = main.deploy_button
        self.popup_list_box = main.popup_list_box
        self.popup_namegroup = main.popup_namegroup
        self.terrain_change_button = main.terrain_change_button
        self.feature_change_button = main.feature_change_button
        self.weather_change_button = main.weather_change_button
        self.unit_build_slot = main.unit_build_slot
        self.subunit_build = main.subunit_build
        self.unit_edit_border = main.unit_edit_border
        self.unitpreset_namegroup = main.unitpreset_namegroup
        self.preset_select_border = main.preset_select_border
        self.custom_unit_preset_list = main.custom_unit_preset_list
        self.unit_preset_list_box = main.unit_preset_list_box
        self.team_coa = main.team_coa
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

        self.time_ui = main.time_ui
        self.time_number = main.time_number

        self.battle_scale_ui = main.battle_scale_ui

        self.speed_number = main.speed_number

        self.weather_matter = main.weather_matter
        self.weather_effect = main.weather_effect

        self.encyclopedia = main.encyclopedia
        self.lore_name_list = main.lore_name_list
        self.filter_tag_list = main.filter_tag_list
        self.lore_button_ui = main.lore_button_ui
        self.subsection_name = main.subsection_name
        self.tag_filter_name = main.tag_filter_name
        self.page_button = main.page_button

        self.encyclopedia_stuff = main.encyclopedia_stuff

        self.status_images = main.status_images
        self.role_images = main.role_images
        self.trait_images = main.trait_images
        self.skill_images = main.skill_images

        self.map_corner = (999, 999)
        self.max_camera = (999 * self.screen_scale[0], 999 * self.screen_scale[1])
        self.subunit_hitbox_size = main.subunit_hitbox_size
        self.subunit_inspect_sprite_size = main.subunit_inspect_sprite_size
        self.collide_distance = self.subunit_hitbox_size / 10  # distance to check collision
        self.front_distance = self.subunit_hitbox_size / 20  # distance from front side
        self.full_distance = self.front_distance / 2  # distance for sprite merge check

        self.preview_leader = []
        self.inspect_subunit = []  # list of subunit shown in inspect ui

        self.combat_path_queue = []  # queue of sub-unit to run melee combat pathfiding
        self.map_move_array = []  # array for pathfinding
        self.subunit_pos_array = []  # pathfinding array after include subunit position as 0
        self.map_def_array = []  # array for defence calculation

        self.esc_slider_menu = main.esc_slider_menu
        self.esc_value_boxes = main.esc_value_boxes

        self.event_log_button = main.event_log_button
        self.time_button = main.time_button

        self.troop_card_ui = main.troop_card_ui
        self.troop_card_button = main.troop_card_button
        self.unitstat_ui = main.unitstat_ui
        self.wheel_ui = main.wheel_ui
        self.eight_wheel_ui = main.eight_wheel_ui
        self.four_wheel_ui = main.four_wheel_ui

        # Genre UI, get added later in change_genre method in Game

        self.command_ui = None
        self.inspect_ui = None
        self.inspect_button = None
        self.col_split_button = None
        self.row_split_button = None
        self.decimation_button = None
        self.behaviour_switch_button = None

        self.leader_level = main.leader_level

        self.battle_done_box = main.battle_done_box
        self.battle_done_button = main.battle_done_button

        self.weather_screen_adjust = self.screen_rect.width / self.screen_rect.height  # for weather sprite spawn position
        self.right_corner = self.screen_rect.width - (5 * self.screen_scale[0])
        self.bottom_corner = self.screen_rect.height - (5 * self.screen_scale[1])
        self.center_screen = [self.screen_rect.width / 2, self.screen_rect.height / 2]  # center position of the screen

        # data specific to ruleset
        self.faction_data = None
        self.coa_list = None

        self.troop_data = None
        self.leader_data = None

        self.battle_map_data = None
        self.weather_data = None
        self.weather_matter_images = None
        self.weather_effect_images = None
        self.day_effect_images = None
        self.weather_list = None
        self.feature_mod = None

        self.current_weather = weather.Weather(self.time_ui, 0, 0, self.weather_data)

        self.generic_animation_pool = None
        self.gen_body_sprite_pool = None
        self.gen_weapon_sprite_pool = None
        self.gen_armour_sprite_pool = None
        self.effect_sprite_pool = None
        self.weapon_joint_list = None

        self.colour_list = None
        self.colour_list = None

        self.generic_action_data = None
        self.subunit_animation_pool = None

        self.game_speed = 0
        self.game_speed_list = (0, 0.5, 1, 2, 4, 6)  # available game speed
        self.day_time = "Day"
        self.old_day_time = self.day_time
        self.leader_now = []
        self.team_troop_number = []  # list of troop number in each team, minimum at one because percentage can't divide by 0
        self.last_team_troop_number = []
        self.battle_scale = []
        self.start_troop_number = []
        self.wound_troop_number = []
        self.death_troop_number = []
        self.flee_troop_number = []
        self.capture_troop_number = []
        self.faction_pick = 0
        self.current_pop_up_row = 0
        self.filter_troop = [True, True, True,
                             True]  # filter in this order: melee infantry, range inf, melee cavalry, range cav
        self.current_selected = None
        self.before_selected = None
        self.player_input_state = None  # specific player command input and ui

        self.all_team_unit = {1: pygame.sprite.Group(),
                              2: pygame.sprite.Group(), "alive": pygame.sprite.Group()}  # more team can be added later
        self.team_pos_list = {key: {} for key in self.all_team_unit.keys()}  # all alive team unit position
        self.subunit_pos_list = []

        self.battle_subunit_list = []  # list of all subunit alive in battle, need to be in list for collision check
        self.visible_subunit_list = {}  # list of subunit visible to the team

        self.filter_stuff = (self.filter_box, self.slot_display_button, self.team_change_button, self.deploy_button,
                             self.terrain_change_button,
                             self.feature_change_button, self.weather_change_button, self.filter_tick_box)

        self.best_depth = pygame.display.mode_ok(self.screen_rect.size, window_style, 32)  # Set the display mode
        self.screen = pygame.display.set_mode(self.screen_rect.size, window_style | pygame.RESIZABLE,
                                              self.best_depth)  # set up self screen

        # Assign battle variable to some classes
        unit.Unit.battle = self
        unit.Unit.image_size = self.subunit_inspect_sprite_size
        subunit.Subunit.battle = self
        leader.Leader.battle = self

        # Create the game camera
        self.camera_zoom = 1  # camera zoom level, starting at the furthest zoom
        self.camera_mode = "Free"  # mode of game camera
        self.base_camera_pos = pygame.Vector2(500 * self.screen_scale[0],
                                              500 * self.screen_scale[
                                                  1])  # Camera pos at furthest zoom for recalculate sprite pos after zoom
        self.camera_pos = self.base_camera_pos * self.camera_zoom  # Camera pos at the current zoom, start at center of map
        self.shown_camera_pos = self.camera_pos  # pos of camera shown to player, in case of screen shaking or other effects

        self.screen_shake_value = 0  # count for how long to shake camera

        self.camera_topleft_corner = (self.camera_pos[0] - self.center_screen[0],
                                      self.camera_pos[1] - self.center_screen[
                                          1])  # calculate top left corner of camera position

        camera.Camera.screen_rect = self.screen_rect
        self.camera = camera.Camera(self.shown_camera_pos, self.camera_zoom)

        self.clock = pygame.time.Clock()  # Game clock to keep track of realtime pass

        self.background = pygame.Surface(self.screen_rect.size)  # Create background image
        self.background.fill((255, 255, 255))  # fill background image with black colour

    def prepare_new_game(self, ruleset, ruleset_folder, team_selected, enactment, map_selected,
                         map_source, unit_scale, mode, char_selected=None):
        """Setup stuff when start new battle"""
        self.ruleset = ruleset  # current ruleset used
        self.ruleset_folder = ruleset_folder  # the folder of rulseset used
        self.map_selected = map_selected  # map folder name
        self.map_source = str(map_source)
        self.unit_scale = unit_scale
        self.team_selected = team_selected  # player selected team
        self.char_selected = char_selected
        self.enactment = enactment  # enactment mod, control both team
        if self.enactment:
            self.team_selected = "alive"

        self.faction_data = self.main.faction_data
        self.coa_list = self.faction_data.coa_list

        self.troop_data = self.main.troop_data
        self.leader_data = self.main.leader_data

        self.troop_card_ui.troop_data = self.troop_data

        self.generic_animation_pool = self.main.generic_animation_pool
        self.gen_body_sprite_pool = self.main.gen_body_sprite_pool
        self.gen_weapon_sprite_pool = self.main.gen_weapon_sprite_pool
        self.gen_armour_sprite_pool = self.main.gen_armour_sprite_pool
        self.effect_sprite_data = self.main.effect_sprite_data
        self.weapon_joint_list = self.main.weapon_joint_list

        self.colour_list = self.main.colour_list

        self.unit_editor_stuff = (self.subunit_build, self.unit_edit_border, self.troop_card_ui,
                                  self.team_coa, self.troop_card_button, self.editor_troop_list_box,
                                  self.troop_namegroup, self.unit_preset_list_box, self.preset_select_border,
                                  self.unitpreset_namegroup, self.unit_save_button, self.unit_delete_button)

        # Load weather schedule
        try:
            self.weather_event = csv_read(self.main_dir, "weather.csv",
                                          ("data", "ruleset", self.ruleset_folder, "map", self.map_selected,
                                           self.map_source), output_type="list")
            self.weather_event = self.weather_event[1:]
            utility.convert_str_time(self.weather_event)
        except (FileNotFoundError, TypeError):  # If no weather found or no map use default light sunny weather start at 9:00
            new_time = datetime.datetime.strptime("09:00:00", "%H:%M:%S").time()
            new_time = datetime.timedelta(hours=new_time.hour, minutes=new_time.minute, seconds=new_time.second)
            self.weather_event = [[4, new_time, 0]]  # default weather light sunny all day
        self.weather_playing = self.weather_event[0][
            1]  # weather_current here is used as the reference for map starting time

        # Random music played from list
        if pygame.mixer:
            self.SONG_END = pygame.USEREVENT + 1
            self.musiclist = glob.glob(os.path.join(self.main_dir, "data", "sound", "music", "*.ogg"))
            try:
                self.music_event = csv_read(self.main_dir, "musicevent.csv",
                                            ("data", "ruleset", self.ruleset_folder, "map", self.map_selected),
                                            output_type="list")
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
                    self.music_schedule = [self.weather_playing]
                    self.music_event = [[5]]
            except:  # any reading error will play random custom music instead
                self.music_schedule = [self.weather_playing]
                self.music_event = [[5]]  # TODO change later when has custom playlist

        try:  # get new map event for event log
            map_event = csv_read(self.main_dir, "eventlog.csv",
                                 ("data", "ruleset", self.ruleset_folder, "map", self.map_selected, self.map_source))
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

        self.time_number.start_setup(self.weather_playing)

        if map_selected is not None:  # Create battle map
            images = load_images(self.main_dir, subfolder=("ruleset", self.ruleset_folder, "map", self.map_selected))
            self.battle_map_base.draw_image(images["base"])
            self.battle_map_feature.draw_image(images["feature"])
            self.battle_map_height.draw_image(images["height"])

            try:  # place_name map layer is optional, if not existed in folder then assign None
                place_name_map = images["placename"]
            except Exception:
                place_name_map = None
            self.battle_map.draw_image(self.battle_map_base, self.battle_map_feature, self.battle_map_height,
                                       place_name_map, self, False)
        else:
            self.editor_map_change(self.battle_map_base.terrain_colour[0],  # temperate
                                   self.battle_map_feature.feature_colour[0])  # plain

        self.map_corner = (len(self.battle_map_base.map_array[0]), len(self.battle_map_base.map_array))  # get map size that troop can move

        self.max_camera = ((self.battle_map_height.image.get_width() - 1) * self.screen_scale[0],
                           (self.battle_map_height.image.get_height() - 1) * self.screen_scale[1])  # reset max camera to new map size

        self.battle_subunit_list = []
        self.visible_subunit_list = {}

        # initialise starting subunit sprites
        self.mode = mode

        self.setup_battle_ui("add")
        leader.Leader.leader_pos = self.command_ui.leader_pos

        if self.mode == "battle":
            self.camera_zoom = self.start_zoom  # Camera zoom
            self.camera_mode = self.start_zoom_mode
            self.setup_battle_unit(self.all_team_unit, self.troop_data.troop_list, self.leader_data.leader_list)
            self.team_troop_number = [1 for _ in self.all_team_unit]  # reset list of troop number in each team
            self.battle_scale = [(value / sum(self.team_troop_number) * 100) for value in self.team_troop_number]
            self.start_troop_number = [0 for _ in self.all_team_unit]
            self.wound_troop_number = [0 for _ in self.all_team_unit]
            self.death_troop_number = [0 for _ in self.all_team_unit]
            self.flee_troop_number = [0 for _ in self.all_team_unit]
            self.capture_troop_number = [0 for _ in self.all_team_unit]
            self.team_pos_list = {key: {} for key in self.all_team_unit.keys()}
            self.subunit_pos_list = []
            self.visible_subunit_list = {key: {} for key in self.all_team_unit.keys() if key != "alive"}

            self.battle_scale_ui.change_fight_scale(self.battle_scale)

            subunit_to_make = tuple(set([this_subunit.troop_id for this_subunit in self.subunit_updater]))
            who_todo = {key: value for key, value in self.troop_data.troop_list.items() if key in subunit_to_make}
            if self.main.leader_sprite:
                for this_unit in self.unit_updater:
                    for this_leader in this_unit.leader:
                        who_todo |= {
                            "h" + str(this_leader.leader_id): self.leader_data.leader_list[this_leader.leader_id]}
            self.subunit_animation_pool = self.main.create_sprite_pool(direction_list, self.main.troop_sprite_size,
                                                                       self.screen_scale,
                                                                       who_todo)

        else:
            self.camera_zoom = 1  # always start at furthest zoom for editor
            self.camera_mode = "Free"  # start with free camera mode

            self.team_troop_number = [1, 1, 1]  # reset list of troop number in each team
            self.battle_scale = [(value / sum(self.team_troop_number) * 100) for value in self.team_troop_number]
            self.start_troop_number = [0, 0, 0]

            # who_todo = {key: value for key, value in
            #             self.troop_data.troop_list.items()}  # TODO change to depend on subunit add
            # self.subunit_animation_pool = self.main.create_sprite_pool(direction_list, self.main.troop_sprite_size,
            #                                                            self.screen_scale, who_todo)

            for this_leader in self.preview_leader:
                this_leader.change_preview_leader(this_leader.leader_id)

    def run_game(self):
        # Create Starting Values
        self.game_state = "battle"  # battle mode
        self.current_unit_row = 0  # custom unit preset current row in editor
        self.current_troop_row = 0  # troop selection current row in editor
        self.current_pop_up_row = 0
        self.input_popup = (None, None)  # no popup asking for user text input state
        self.leader_now = []  # list of showing leader in command ui
        self.current_selected = None  # Which unit is currently selected
        self.drama_text.queue = []  # reset drama text popup queue

        if self.mode == "unit_editor":
            self.game_state = "editor"  # editor mode

            self.troop_list = [item["Name"] for item in self.troop_data.troop_list.values()][
                              1:]  # generate troop name list
            self.troop_index_list = list(range(0, len(self.troop_list) + 1))

            self.leader_list = [item["Name"] for item in self.leader_data.leader_list.values()][
                               1:]  # generate leader name list

            setup_list(self.screen_scale, menu.NameList, self.current_unit_row,
                       tuple(self.custom_unit_preset_list.keys()),
                       self.unitpreset_namegroup, self.unit_preset_list_box,
                       self.battle_ui_updater)  # setup preset army list
            setup_list(self.screen_scale, menu.NameList, self.current_troop_row, self.troop_list,
                       self.troop_namegroup, self.editor_troop_list_box,
                       self.battle_ui_updater)  # setup troop name list

            self.current_list_show = "troop"
            self.unit_preset_name = ""
            self.prepare_state = True
            self.base_terrain = 0
            self.feature_terrain = 0
            self.weather_type = 4
            self.weather_strength = 0
            self.current_weather.__init__(self.time_ui, self.weather_type, self.weather_strength, self.weather_data)
            self.subunit_in_card = None  # current sub-subunit showing in subunit card

            self.main.create_team_coa([0], ui_class=self.battle_ui_updater, one_team=True,
                                      team1_set_pos=(self.editor_troop_list_box.rect.midleft[0] - int(
                                          (300 * self.screen_scale[0]) / 2),
                                                     self.editor_troop_list_box.rect.midleft[
                                                         1]))  # default faction select as all faction

            self.editor_troop_list_box.scroll.change_image(new_row=self.current_troop_row,
                                                           row_size=len(self.troop_list))  # change troop scroll image

            for index, slot in enumerate(
                    self.subunit_build):  # start with the first player subunit slot selected when enter
                if index == 0:
                    slot.selected = True
                    for border in self.unit_edit_border:
                        border.kill()
                        del border
                    self.unit_edit_border.add(battleui.SelectedSquad(slot.inspect_pos))
                    self.battle_ui_updater.add(*self.unit_edit_border)
                else:  # reset all other slots
                    slot.selected = False

            self.base_camera_pos = pygame.Vector2(500 * self.screen_scale[0],
                                                  500 * self.screen_scale[1])
            self.camera_pos = self.base_camera_pos * self.camera_zoom
            self.camera_fix()
            self.shown_camera_pos = self.camera_pos

            self.weather_playing = None  # remove weather schedule from editor test

            self.change_battle_state()

            for name in self.unitpreset_namegroup:  # loop to change selected border position to the first in preset list
                self.preset_select_border.change_pos(name.rect.topleft)
                break

        else:  # normal battle
            self.change_battle_state()

            if self.char_selected is not None:  # select player char by default if control only one
                for unit in self.all_team_unit["alive"]:  # get player char
                    if unit.game_id == self.char_selected:
                        self.player_char = unit.leader[0].subunit
                        unit.leader[0].subunit.player_manual_control = True
                        self.current_selected = unit
                        unit.just_selected = True
                        unit.selected = True
                        if self.camera_mode == "Follow":
                            self.base_camera_pos = pygame.Vector2(self.player_char.base_pos[0] * self.screen_scale[0],
                                                                  self.player_char.base_pos[1] * self.screen_scale[1])
                            self.camera_pos = self.base_camera_pos * self.camera_zoom
                            self.camera_fix()
                        break
            else:
                self.base_camera_pos = pygame.Vector2(500 * self.screen_scale[0],
                                                      500 * self.screen_scale[1])
                self.camera_pos = self.base_camera_pos * self.camera_zoom
                self.camera_fix()

            self.shown_camera_pos = self.camera_pos

        self.map_scale_delay = 0  # delay for map zoom input
        self.text_delay = 0
        self.mouse_timer = 0  # This is timer for checking double mouse click, use realtime
        self.screen_shake_value = 0
        self.ui_timer = 0  # This is timer for ui update function, use realtime
        self.drama_timer = 0  # This is timer for combat related function, use self time (realtime * game_speed)
        self.dt = 0  # Realtime used for time calculation
        self.ui_dt = 0  # Realtime used for ui timer
        self.weather_spawn_timer = 0
        self.last_mouseover = None  # Which subunit last mouse over
        self.speed_number.speed_update(self.game_speed)
        self.click_any = False  # For checking if mouse click on anything, if not close ui related to unit
        self.new_unit_click = False  # For checking if another subunit is clicked when inspect ui open
        self.inspect = False  # For checking if inspect ui is currently open or not

        self.map_mode = 0  # default, another one show height map
        self.subunit_selected = None  # which subunit in inspect ui is selected in last update loop
        self.before_selected = None  # Which unit is selected before
        self.split_happen = False  # Check if unit get split in that loop
        self.show_troop_number = True  # for toggle troop number on/off
        self.player_input_state = None

        self.base_mouse_pos = [0, 0]  # mouse position list in battle map not screen without zoom
        self.battle_mouse_pos = [0, 0]  # with camera zoom adjust
        self.command_mouse_pos = [0, 0]  # with zoom but no revert screen scale for unit command
        self.unit_selector.current_row = 0

        self.time_update()

        self.effect_updater.update(self.all_team_unit["alive"], self.dt, self.camera_zoom)

        # self.map_def_array = []
        # self.mapunitarray = [[x[random.randint(0, 1)] if i != j else 0 for i in range(1000)] for j in range(1000)]
        pygame.mixer.music.set_endevent(self.SONG_END)  # End current music before battle start

        while True:  # self running
            self.fps_count.fps_show(self.clock)
            event_key_press = None
            mouse_left_up = False  # left click
            mouse_left_down = False  # hold left click
            mouse_right_up = False  # right click
            mouse_right_down = False  # hold right click
            double_mouse_right = False  # double right click
            mouse_scroll_down = False
            mouse_scroll_up = False
            key_press = pygame.key.get_pressed()
            esc_press = False
            self.click_any = False

            self.true_dt = self.clock.get_time() / 1000  # dt before game_speed

            self.battle_ui_updater.remove(self.single_text_popup)  # remove button text popup every update

            self.mouse_pos = pygame.mouse.get_pos()  # current mouse pos based on screen

            self.cursor.update(self.mouse_pos)

            self.base_mouse_pos = pygame.Vector2((self.mouse_pos[0] - self.center_screen[0] + self.camera_pos[0]),
                                                 (self.mouse_pos[1] - self.center_screen[1] + self.camera_pos[
                                                     1]))  # mouse pos on the map based on camera position
            self.battle_mouse_pos = self.base_mouse_pos / self.camera_zoom  # mouse pos on the map at current camera zoom scale
            self.command_mouse_pos = pygame.Vector2(self.battle_mouse_pos[0] / self.screen_scale[0],
                                                    self.battle_mouse_pos[1] / self.screen_scale[
                                                        1])  # with screen scale

            self.battle_ui_updater.clear(self.screen, self.background)  # Clear sprite before update new one

            for event in pygame.event.get():  # get event that happen
                if event.type == QUIT:  # quit self
                    self.input_popup = ("confirm_input", "quit")
                    self.confirm_ui.change_instruction("Quit Game?")
                    self.battle_ui_updater.add(*self.confirm_ui_popup)

                elif event.type == self.SONG_END:  # change music track
                    pygame.mixer.music.unload()
                    self.picked_music = random.randint(0, len(self.music_current) - 1)
                    pygame.mixer.music.load(self.musiclist[self.music_current[self.picked_music]])
                    pygame.mixer.music.play(fade_ms=100)

                elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:  # open/close menu
                    esc_press = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # left click
                        mouse_left_up = True
                        self.new_unit_click = False
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
                    if self.input_popup[0] == "text_input":  # event update to input box
                        self.input_box.player_input(event, key_press)
                        self.text_delay = 0.1
                    else:
                        event_key_press = event.key

            if pygame.mouse.get_pressed()[0]:  # Hold left click
                mouse_left_down = True
            elif pygame.mouse.get_pressed()[2]:  # Hold left click
                mouse_right_down = True

            if self.map_scale_delay > 0:  # time delay before player can scroll map zoom
                self.map_scale_delay += self.ui_dt
                if self.map_scale_delay >= 0.1:  # delay for 1 second until user can change scale again
                    self.map_scale_delay = 0

            if self.input_popup == (None, None):
                if esc_press:  # open/close menu
                    if self.game_state in ("battle", "editor"):  # in battle or editor mode
                        self.game_state = "menu"  # open menu
                        self.battle_ui_updater.add(self.battle_menu,
                                                   *self.battle_menu_button)  # add menu and its buttons to drawer
                        esc_press = False  # reset esc press, so it not stops esc menu when open

                if self.game_state in ("battle", "editor"):  # game in battle state
                    if self.player_input_state is None:  # register user input during gameplay
                        if mouse_scroll_up or mouse_scroll_down:  # Mouse scroll
                            self.mouse_scrolling_process(mouse_scroll_up, mouse_scroll_down)

                        # keyboard input
                        if event_key_press is not None:
                            self.battle_keyboard_process(event_key_press)

                        self.camera_process(key_press)

                        if self.mouse_timer != 0:  # player click mouse once before
                            self.mouse_timer += self.ui_dt  # increase timer for mouse click using real time
                            if self.mouse_timer >= 0.3:  # time pass 0.3 second no longer count as double click
                                self.mouse_timer = 0

                        if mouse_left_up or mouse_right_up or mouse_left_down or mouse_right_down or key_press:
                            self.mouse_process(mouse_left_up, mouse_right_up, mouse_left_down,
                                               mouse_right_down, key_press)

                            if self.game_state == "battle":
                                self.battle_mouse_process(mouse_left_up, mouse_right_up, double_mouse_right,
                                                          mouse_left_down, mouse_right_down, key_press, event_key_press)

                            elif self.game_state == "editor":  # unit editor state
                                self.editor_mouse_process(mouse_left_up, mouse_right_up, mouse_left_down,
                                                          mouse_right_down, key_press, event_key_press)

                        self.selected_unit_process(mouse_left_up, mouse_right_up, double_mouse_right,
                                                   mouse_left_down, mouse_right_down, key_press, event_key_press)
                    else:  # register and process ui that require player input and block everything else
                        if type(self.player_input_state) != str:  # ui input state
                            choice = self.player_input_state.selection(self.mouse_pos)
                            if self.player_input_state in self.wheel_ui:  # wheel ui process
                                if mouse_left_up:
                                    self.wheel_ui_process(choice)
                                elif event_key_press == pygame.K_q:  # Close unit command wheel ui
                                    self.battle_ui_updater.remove(self.wheel_ui)
                                    self.player_input_state = None
                        elif "aim" in self.player_input_state:
                            self.manual_aim(event_key_press, mouse_left_up, mouse_right_up, mouse_scroll_up,
                                            mouse_scroll_down)

                    # Drama text function
                    if self.drama_timer == 0 and len(
                            self.drama_text.queue) != 0:  # Start timer and add to main_ui If there is event queue
                        self.battle_ui_updater.add(self.drama_text)
                        self.drama_text.process_queue()
                        self.drama_timer = 0.1
                    elif self.drama_timer > 0:
                        self.drama_text.play_animation()
                        self.drama_timer += self.ui_dt
                        if self.drama_timer > 3:
                            self.drama_timer = 0
                            self.battle_ui_updater.remove(self.drama_text)

                    if self.dt > 0:  # Part that run when game not pause only

                        # Event log
                        if self.event_schedule is not None and self.event_list != [] and self.time_number.time_number >= self.event_schedule:
                            self.event_log.add_log(None, None, event_id=self.event_id)
                            for event in self.event_log.map_event:
                                if self.event_log.map_event[event][3] is not None and self.event_log.map_event[event][
                                    3] > self.time_number.time_number:
                                    self.event_id = event
                                    self.event_schedule = self.event_log.map_event[event][3]
                                    break
                            self.event_list = self.event_list[1:]

                        # Weather system
                        if self.weather_playing is not None and self.time_number.time_number >= self.weather_playing:
                            this_weather = self.weather_event[0]

                            if this_weather[0] != 0 and this_weather[0] in self.weather_data:
                                self.current_weather.__init__(self.time_ui, this_weather[0], this_weather[2],
                                                              self.weather_data)
                            else:  # Clear weather when no weather found, also for when input weather not in ruleset
                                self.current_weather.__init__(self.time_ui, 0, 0, self.weather_data)
                            self.weather_event.pop(0)
                            try:
                                self.battle_map.add_effect(self.battle_map_height,
                                                           effect_image=
                                                           self.weather_effect_images[self.current_weather.name][
                                                               self.current_weather.level],
                                                           time_image=self.day_effect_images[self.day_time])
                                self.battle_map.change_scale(self.camera_zoom)
                            except IndexError:  # weather does not have effect
                                pass

                            if len(self.weather_event) > 0:  # Get end time of next event which is now index 0
                                self.weather_playing = self.weather_event[0][1]
                            else:
                                self.weather_playing = None

                        if self.current_weather.spawn_rate > 0:
                            self.weather_spawn_timer += self.dt
                            if self.weather_spawn_timer >= self.current_weather.spawn_rate:
                                self.weather_spawn_timer = 0
                                true_pos = (random.randint(10, self.screen_rect.width), 0)  # starting pos
                                target = (true_pos[0], self.screen_rect.height)  # final base_target pos

                                if self.current_weather.spawn_angle == 225:  # top right to bottom left movement
                                    start_pos = random.randint(10,
                                                               self.screen_rect.width * 2)  # starting x pos that can be higher than screen width
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
                                    target = (true_pos[1] - (self.screen_rect.width / 1.5), true_pos[1])

                                random_pic = random.randint(0, len(
                                    self.weather_matter_images[self.current_weather.name]) - 1)
                                self.weather_matter.add(weather.MatterSprite(true_pos, target,
                                                                             self.current_weather.speed,
                                                                             self.weather_matter_images[
                                                                                 self.current_weather.name][
                                                                                 random_pic]))

                        # Screen shaking
                        self.shown_camera_pos = self.camera_pos  # reset camera pos first
                        if self.screen_shake_value > 0:
                            self.screen_shake_value -= 1
                            self.shake_camera()
                            if self.screen_shake_value < 0:
                                self.screen_shake_value = 0

                        # Music System
                        if len(self.music_schedule) > 0 and self.time_number.time_number >= self.music_schedule[0]:
                            pygame.mixer.music.unload()
                            self.music_current = self.music_event[0].copy()
                            self.picked_music = random.randint(0, len(self.music_current) - 1)
                            pygame.mixer.music.load(self.musiclist[self.music_current[self.picked_music]])
                            pygame.mixer.music.play(fade_ms=100)
                            self.music_schedule = self.music_schedule[1:]
                            self.music_event = self.music_event[1:]

                        # Subunit collide check
                        for this_unit in self.all_team_unit["alive"]:  # reset collide
                            this_unit.collide = False

                        if len(self.battle_subunit_list) > 1:
                            tree = KDTree(self.subunit_pos_list)  # collision loop check, much faster than pygame collide check
                            collisions = tree.query_pairs(self.collide_distance)
                            for one, two in collisions:
                                sprite_one = self.battle_subunit_list[one]
                                sprite_two = self.battle_subunit_list[two]
                                if sprite_one.unit != sprite_two.unit:  # collide with subunit in other unit
                                    if sprite_one.base_pos.distance_to(sprite_one.base_pos) < self.full_distance:
                                        sprite_one.full_merge.append(sprite_two)
                                        sprite_two.full_merge.append(sprite_one)

                                    if sprite_one.front_pos.distance_to(
                                            sprite_two.base_pos) < self.front_distance:  # first subunit collision
                                        if sprite_one.team != sprite_two.team:  # enemy team
                                            sprite_one.enemy_front.append(sprite_two)
                                            sprite_one.unit.collide = True
                                        elif sprite_one.state in (2, 4, 6, 10, 11, 13) or \
                                                sprite_two.state in (
                                        2, 4, 6, 10, 11, 13):  # cannot run pass other unit if either run or in combat
                                            sprite_one.friend_front.append(sprite_two)
                                            sprite_one.unit.collide = True
                                        sprite_one.collide_penalty = True
                                    else:
                                        if sprite_one.team != sprite_two.team:  # enemy team
                                            sprite_one.enemy_side.append(sprite_two)
                                    if sprite_two.front_pos.distance_to(
                                            sprite_one.base_pos) < self.front_distance:  # second subunit
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
                                    if sprite_one.front_pos.distance_to(
                                            sprite_two.base_pos) < self.front_distance:  # first subunit collision
                                        if sprite_one.base_pos.distance_to(sprite_one.base_pos) < self.full_distance:
                                            sprite_one.full_merge.append(sprite_two)
                                            sprite_two.full_merge.append(sprite_one)

                                        if sprite_one.state in (2, 4, 6, 10, 11, 12, 13, 99) or \
                                                sprite_two.state in (2, 4, 6, 10, 11, 12, 13):
                                            sprite_one.same_front.append(sprite_two)
                                    if sprite_two.front_pos.distance_to(
                                            sprite_one.base_pos) < self.front_distance:  # second subunit
                                        if sprite_one.state in (2, 4, 6, 10, 11, 12, 13, 99) or \
                                                sprite_two.state in (2, 4, 6, 10, 11, 12, 13):
                                            sprite_two.same_front.append(sprite_one)

                        self.subunit_pos_array = self.map_move_array.copy()
                        for this_subunit in self.battle_subunit_list:
                            for y in this_subunit.pos_range[0]:
                                for x in this_subunit.pos_range[1]:
                                    self.subunit_pos_array[x][y] = 0

                    # Battle related updater
                    self.unit_updater.update(self.current_weather, self.subunit_updater, self.dt, self.camera_zoom,
                                             self.base_mouse_pos, mouse_left_up)
                    self.last_mouseover = None  # reset last unit mouse over
                    self.leader_updater.update()
                    self.subunit_updater.update(self.current_weather, self.dt, self.camera_zoom,
                                                self.base_mouse_pos, mouse_left_up)

                    # Run pathfinding for melee combat no more than limit number of subunit per update to prevent stutter
                    if len(self.combat_path_queue) > 0:
                        run = 0
                        while len(self.combat_path_queue) > 0 and run < 5:
                            self.combat_path_queue[0].combat_pathfind()
                            self.combat_path_queue = self.combat_path_queue[1:]
                            run += 1

                    self.remove_unit_ui_check(mouse_left_up)

                    if self.ui_timer > 1:
                        self.battle_scale = [(value / sum(self.team_troop_number) * 100) for value in
                                             self.team_troop_number]
                        self.battle_scale_ui.change_fight_scale(
                            self.battle_scale)  # change fight colour scale on time_ui bar

                    self.effect_updater.update(self.subunit_updater, self.dt, self.camera_zoom)
                    self.weather_updater.update(self.dt, self.time_number.time_number)
                    self.mini_map.update(self.camera_zoom, [self.camera_pos, self.camera_topleft_corner],
                                         self.team_pos_list)

                    self.ui_updater.update()  # update ui

                    self.camera.update(self.shown_camera_pos, self.battle_camera, self.camera_zoom)

                    # Update game time
                    self.dt = self.true_dt * self.game_speed  # apply dt with game_speed for calculation
                    if self.ui_timer >= 1.1:  # reset ui timer every 1.1 seconds
                        self.ui_timer -= 1.1
                    self.ui_timer += self.dt  # ui update by real time instead of self time to reduce workload
                    self.ui_dt = self.dt  # get ui timer before apply self

                    if self.dt > 0.1:
                        self.dt = 0.1  # make it so stutter and lag does not cause overtime issue

                    self.time_number.timer_update(
                        self.dt * self.time_speed_scale)  # update battle time with genre speed
                    self.time_update()

                    if self.mode == "battle" and len([key for key, value in self.all_team_unit.items() if
                                                      key != "alive" and len(value) > 0]) <= 1:
                        if self.battle_done_box not in self.battle_ui_updater:
                            if len(self.all_team_unit["alive"]) <= 0:
                                team_win = 0  # draw
                                self.battle_done_box.pop("Draw")
                            else:
                                for key, value in self.all_team_unit.items():
                                    if key != "alive":
                                        if len(value) > 0:
                                            team_win = key
                                            for index, coa in enumerate(self.team_coa):
                                                if index == team_win - 1:
                                                    self.battle_done_box.pop(coa.name)
                                                    break

                            self.battle_done_button.rect = self.battle_done_button.image.get_rect(
                                midtop=self.battle_done_button.pos)
                            self.battle_ui_updater.add(self.battle_done_box, self.battle_done_button)
                        else:
                            if mouse_left_up and self.battle_done_button.rect.collidepoint(self.mouse_pos):
                                self.game_state = "end"  # end battle mode, result screen
                                self.game_speed = 0
                                coa_list = [None, None]
                                for index, coa in enumerate(self.team_coa):
                                    coa_list[index] = coa.image
                                self.battle_done_box.show_result(coa_list[0], coa_list[1],
                                                                 (self.start_troop_number, self.team_troop_number,
                                                                  self.wound_troop_number, self.death_troop_number,
                                                                  self.flee_troop_number, self.capture_troop_number))
                                self.battle_done_button.rect = self.battle_done_button.image.get_rect(
                                    center=(self.battle_done_box.rect.midbottom[0],
                                            self.battle_done_box.rect.midbottom[
                                                1] / 1.3))
                    # ^ End update self time

                elif self.game_state == "menu":  # Complete self pause when open either esc menu or encyclopedia
                    command = self.escmenu_process(mouse_left_up, mouse_left_down, esc_press, mouse_scroll_up,
                                                   mouse_scroll_down, self.battle_ui_updater)
                    if command == "end_battle":
                        return

            elif self.input_popup != (
            None, None):  # currently, have input text pop up on screen, stop everything else until done
                for button in self.input_button:
                    button.update(self.mouse_pos, mouse_left_up, mouse_left_down)

                if self.input_ok_button.event:
                    self.input_ok_button.event = False

                    if self.input_popup[1] == "save_unit":
                        current_preset = self.convert_unit_slot_to_dict(self.input_box.text)
                        if current_preset is not None:
                            self.custom_unit_preset_list.update(current_preset)

                            self.unit_preset_name = self.input_box.text
                            setup_list(self.screen_scale, menu.NameList, self.current_unit_row,
                                       tuple(self.custom_unit_preset_list.keys()),
                                       self.unitpreset_namegroup, self.unit_preset_list_box,
                                       self.battle_ui_updater)  # setup preset unit list
                            for name in self.unitpreset_namegroup:  # loop to change selected border position to the last in preset list
                                if name.name == self.unit_preset_name:
                                    self.preset_select_border.change_pos(name.rect.topleft)
                                    break

                            self.save_custom_unit_preset()
                        else:
                            self.warning_msg.warning([self.warning_msg.min_subunit_warn])
                            self.battle_ui_updater.add(self.warning_msg)

                    elif self.input_popup[1] == "delete_preset":
                        del self.custom_unit_preset_list[self.unit_preset_name]
                        self.unit_preset_name = ""
                        setup_list(self.screen_scale, menu.NameList, self.current_unit_row,
                                   tuple(self.custom_unit_preset_list.keys()),
                                   self.unitpreset_namegroup, self.unit_preset_list_box,
                                   self.battle_ui_updater)  # setup preset unit list
                        for name in self.unitpreset_namegroup:  # loop to change selected border position to the first in preset list
                            self.preset_select_border.change_pos(name.rect.topleft)
                            break

                        self.save_custom_unit_preset()

                    elif self.input_popup[1] == "quit":
                        self.battle_ui_updater.clear(self.screen, self.background)
                        self.battle_camera.clear(self.screen, self.background)
                        pygame.quit()
                        sys.exit()

                    self.input_box.text_start("")
                    self.input_popup = (None, None)
                    self.battle_ui_updater.remove(*self.input_ui_popup, *self.confirm_ui_popup)

                elif self.input_cancel_button.event or esc_press:
                    self.input_cancel_button.event = False
                    self.input_box.text_start("")
                    self.input_popup = (None, None)
                    self.battle_ui_updater.remove(*self.input_ui_popup, *self.confirm_ui_popup)

                elif self.input_popup[0] == "text_input":
                    if self.text_delay == 0:
                        if event_key_press[self.input_box.hold_key]:
                            self.input_box.player_input(None, key_press)
                            self.text_delay = 0.1
                    else:
                        self.text_delay += self.true_dt
                        if self.text_delay >= 0.3:
                            self.text_delay = 0

            self.screen.blit(self.camera.image, (0, 0))  # Draw the self camera and everything that appear in it
            self.battle_ui_updater.draw(self.screen)  # Draw the UI
            pygame.display.update()  # update self display, draw everything
            self.clock.tick(60)  # clock update even if self pause

    def exit_battle(self):
        self.battle_ui_updater.clear(self.screen, self.background)  # remove all sprite
        self.battle_camera.clear(self.screen, self.background)  # remove all sprite

        self.setup_battle_ui("remove")  # remove ui from group

        self.battle_ui_updater.remove(self.battle_menu, *self.battle_menu_button, *self.esc_slider_menu,
                                      *self.esc_value_boxes, self.battle_done_box, self.battle_done_button)  # remove menu

        # remove all reference from battle object
        self.player_char = None
        for value in self.all_team_unit.values():  # remove unit from group first
            value.empty()
        self.all_team_unit = {1: pygame.sprite.Group(),
                              2: pygame.sprite.Group(), "alive": pygame.sprite.Group()}  # reset dict
        self.team_pos_list = {key: {} for key in self.team_pos_list.keys()}

        clean_group_object((self.subunit_updater, self.leader_updater, self.unit_updater, self.unit_icon,
                            self.troop_number_sprite, self.damage_sprites, self.weather_matter))

        self.subunit_animation_pool = None
        self.generic_action_data = None

        self.remove_unit_ui()

        self.combat_path_queue = []
        self.battle_subunit_list = []
        self.map_move_array = []
        self.subunit_pos_array = []
        self.map_def_array = []
        self.subunit_pos_list = []
        self.current_selected = None
        self.before_selected = None
        self.last_mouseover = None

        self.player_char = None

        self.drama_timer = 0  # reset drama text popup
        self.battle_ui_updater.remove(self.drama_text)

        self.battle_map_base.clear_image()
        self.battle_map_feature.clear_image()
        self.battle_map_height.clear_image()
        self.battle_map.clear_image()

        if self.mode == "unit_editor":
            self.subunit_in_card = None

            self.battle_ui_updater.remove(self.unit_editor_stuff, self.filter_stuff,
                                          self.popup_list_box, self.popup_list_box.scroll, *self.popup_namegroup)

            for group in self.troop_namegroup, self.unit_edit_border, self.unitpreset_namegroup:
                for item in group:  # remove name list
                    item.kill()
                    del item

            for slot in self.subunit_build:  # reset all sub-subunit slot
                slot.kill()
                slot.__init__(0, slot.game_id, self.unit_build_slot, slot.pos, 100, 100, (1, 1), self.genre, "edit")
                slot.kill()
                self.subunit_build.add(slot)
                slot.leader = None  # remove leader link in

            for this_leader in self.preview_leader:
                this_leader.change_editor_subunit(None)  # remove subunit link in leader
                this_leader.change_preview_leader(1)

            self.faction_pick = 0
            self.filter_troop = [True, True, True, True]
            self.troop_list = [item["Name"] for item in self.troop_data.troop_list.values()][
                              1:]  # reset troop filter back to all faction
            self.troop_index_list = list(range(0, len(self.troop_list) + 1))

            self.leader_list = [item["Name"] for item in self.leader_data.leader_list.values()][
                               1:]  # generate leader name list)

        self.leader_now = []
