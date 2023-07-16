import os
import sys
import time

import pygame
from pygame import Vector2, display
from pygame.locals import *

from engine.ai import ai
from engine.battle.add_skill_icon import add_skill_icon
from engine.battle.add_sound_effect_queue import add_sound_effect_queue
from engine.battle.cal_shake_value import cal_shake_value
from engine.battle.camera_fix import camera_fix
from engine.battle.camera_process import camera_process
from engine.battle.change_battle_state import change_battle_state
from engine.battle.countdown_skill_icon import countdown_skill_icon
from engine.battle.escmenu_process import escmenu_process
from engine.battle.kill_effect_icon import kill_effect_icon
from engine.battle.play_sound_effect import play_sound_effect
from engine.battle.player_aim import player_aim
from engine.battle.player_cancel_input import player_cancel_input
from engine.battle.player_input_process import player_input_process
from engine.battle.player_skill_perform import player_skill_perform
from engine.battle.setup.make_battle_ui import make_battle_ui
from engine.battle.setup.make_esc_menu import make_esc_menu
from engine.battle.setup_battle_unit import setup_battle_unit
from engine.battle.shake_camera import shake_camera
from engine.battle.spawn_weather_matter import spawn_weather_matter
from engine.battle.time_update import time_update
from engine.battle.wheel_ui_process import wheel_ui_process
from engine.camera.camera import Camera
from engine.drama.drama import TextDrama
from engine.effect.effect import Effect
from engine.game.activate_input_popup import activate_input_popup
from engine.game.change_pause_update import change_pause_update
from engine.lorebook.lorebook import lorebook_process
from engine.uibattle.uibattle import BattleCursor, FPSCount, SkillIcon, AimTarget, BattleDone, ButtonUI, EventLog, \
    UIScroll, MiniMap
from engine.unit.unit import Unit
from engine.utility import load_image, load_images, number_to_minus_or_plus, clean_group_object, convert_str_time
from engine.weather.weather import Weather

script_dir = os.path.split(os.path.abspath(__file__))[0] + "/"

# ----
# perhaps this can be in its own file?

load_timer = None


def set_start_load(self, what):  # For output asset loading time in terminal
    globals()['load_timer'] = time.time()
    self.game.loading_screen("Loading " + what)  # change loading screen to display progress
    return "Loading {0}... ".format(what)


def set_done_load():
    duration = time.time() - globals()['load_timer']
    return " DONE ({0}s)\n".format(duration)


class Battle:
    activate_input_popup = activate_input_popup
    add_skill_icon = add_skill_icon
    add_sound_effect_queue = add_sound_effect_queue
    cal_shake_value = cal_shake_value
    camera_fix = camera_fix
    camera_process = camera_process
    change_battle_state = change_battle_state
    change_pause_update = change_pause_update
    countdown_skill_icon = countdown_skill_icon
    play_sound_effect = play_sound_effect
    player_aim = player_aim
    player_cancel_input = player_cancel_input
    player_input_process = player_input_process
    player_skill_perform = player_skill_perform
    setup_battle_unit = setup_battle_unit
    shake_camera = shake_camera
    spawn_weather_matter = spawn_weather_matter
    time_update = time_update
    escmenu_process = escmenu_process
    kill_effect_icon = kill_effect_icon
    wheel_ui_process = wheel_ui_process
    lorebook_process = lorebook_process

    battle = None
    ui_updater = None
    ui_drawer = None
    screen = None
    battle_camera_size = None
    battle_camera_min = None
    battle_camera_max = None
    start_camera_mode = "Follow"

    def __init__(self, game):
        self.game = game
        Battle.battle = self

        self.clock = pygame.time.Clock()  # Game clock to keep track of realtime pass

        self.config = game.config
        self.master_volume = game.master_volume
        self.music_volume = game.music_volume
        self.effect_volume = game.effect_volume
        self.voice_volume = game.voice_volume
        self.play_music_volume = game.play_music_volume
        self.play_effect_volume = game.play_effect_volume
        self.play_voice_volume = game.play_voice_volume
        self.mouse_bind = game.mouse_bind
        self.mouse_bind_name = game.mouse_bind_name
        self.joystick_bind_name = game.joystick_bind_name
        self.player1_key_control = self.config["USER"]["control player 1"]
        self.player1_key_bind = game.player1_key_bind["keyboard"]
        self.player1_key_bind_name = {value: key for key, value in self.player1_key_bind.items()}
        self.player1_key_press = {key: False for key in self.player1_key_bind}
        self.player1_key_hold = {key: False for key in self.player1_key_bind if "Attack" in key or
                                 "Move" in key or "Input" in key}  # key that consider holding
        self.screen_rect = game.screen_rect

        Battle.battle_camera_size = (self.screen_rect.width * 0.8, self.screen_rect.height * 0.8)
        Battle.battle_camera_min = (self.screen_rect.width * 0.1, self.screen_rect.height * 0.1)
        Battle.battle_camera_max = ((self.screen_rect.width * 0.8) - 1, (self.screen_rect.height * 0.8) - 1)
        self.battle_camera_center = (self.battle_camera_size[0] / 2, self.battle_camera_size[1] / 2)

        self.main_dir = game.main_dir
        self.data_dri = game.data_dir
        self.module_dir = game.module_dir
        self.screen_scale = game.screen_scale
        self.battle_camera = game.battle_camera
        Battle.ui_updater = game.battle_ui_updater
        Battle.ui_drawer = game.battle_ui_drawer
        Battle.cursor_drawer = game.battle_cursor_drawer

        self.unit_updater = game.unit_updater
        self.all_units = game.all_units
        self.effect_updater = game.effect_updater
        self.realtime_ui_updater = game.realtime_ui_updater

        self.cursor = game.cursor
        self.joysticks = game.joysticks
        self.joystick_name = game.joystick_name

        self.battle_base_map = game.battle_base_map
        self.battle_feature_map = game.battle_feature_map
        self.battle_height_map = game.battle_height_map
        self.battle_map = game.battle_map

        self.shoot_lines = game.shoot_lines

        self.button_ui = game.button_ui

        self.text_popup = game.text_popup

        self.skill_icons = game.skill_icons

        self.input_box = game.input_box
        self.input_ui = game.input_ui
        self.input_ok_button = game.input_ok_button
        self.input_cancel_button = game.input_cancel_button
        self.input_ui_popup = game.input_ui_popup
        self.confirm_ui_popup = game.confirm_ui_popup
        self.all_input_ui_popup = game.all_input_ui_popup

        self.weather_matters = game.weather_matters
        self.weather_effect = game.weather_effect

        self.skill_images = game.skill_images

        self.encyclopedia = game.encyclopedia
        self.lore_name_list = game.lore_name_list
        self.filter_tag_list = game.filter_tag_list
        self.lore_buttons = game.lore_buttons
        self.subsection_name = game.subsection_name
        self.tag_filter_name = game.tag_filter_name

        self.encyclopedia_stuff = game.encyclopedia_stuff

        self.sound_effect_pool = game.sound_effect_pool
        self.sound_effect_queue = {}

        self.map_corner = (1000, 1000)
        self.max_camera = (1000, 1000)

        self.troop_ai_logic_queue = []
        self.pathfinding_thread = ai.PathfindingAI(self)

        self.unit_behaviour_wheel = \
            {"Main": {"Army": "Army", "Group": "Group", "Range Attack": "Range Attack", "Setting": "Setting"},
             "Group": {"Group Style": "Group Style",
                       "Group Phase": "Group Phase",
                       "Group Formation": "Group Formation",
                       "Group Position": "Group Position",
                       "Group Density": "Group Density",
                       "Group Order": "Group Order"},
             "Army": {"Army Style": "Army Style",
                      "Army Phase": "Army Phase",
                      "Army Formation": "Army Formation",
                      "Army Position": "Army Position",
                      "Army Density": "Army Density",
                      "Army Order": "Army Order"},
             "Range Attack": {"Focus Aim": "Focus Aim",
                              "Line Aim": "Line Aim",
                              "Leader Aim": "Leader Aim"},
             "Army Phase": {"Army Skirmish Phase": "Skirmish Phase", "Army Melee Phase": "Melee Phase",
                            "Army Bombard Phase": "Bombard Phase"},
             "Army Style": {"Army Infantry Flank": "Infantry Flank", "Army Cavalry Flank": "Cavalry Flank"},
             "Army Order": {"Army Stay Formation": "Stay Formation", "Army Follow": "Follow", "Army Free": "Free",
                            "Army Stay Here": "Stay Here"},
             "Army Position": {"Army Behind": "Behind", "Army Ahead": "Ahead", "Army Around": "Around"},
             "Army Density": {"Army Very Tight": "Very Tight", "Army Tight": "Tight",
                              "Army Very Loose": "Very Loose", "Army Loose": "Loose"},

             "Group Phase": {"Skirmish Phase": "Skirmish Phase", "Melee Phase": "Melee Phase",
                             "Bombard Phase": "Bombard Phase"},
             "Group Style": {"Infantry Flank": "Infantry Flank", "Cavalry Flank": "Cavalry Flank"},
             "Group Density": {"Very Tight": "Very Tight", "Tight": "Tight",
                               "Very Loose": "Very Loose", "Loose": "Loose"},
             "Group Position": {"Behind": "Behind", "Ahead": "Ahead", "Left": "Left", "Right": "Right",
                                "Around": "Around"},
             "Group Order": {"Stay Formation": "Stay Formation", "Follow": "Follow", "Free": "Free",
                             "Stay Here": "Stay Here"},
             "Setting": {"Height Map": "Height Map", "UI Hide": "UI Hide", "UI Show": "UI Show"}}

        self.weather_screen_adjust = self.screen_rect.width / self.screen_rect.height  # for weather sprite spawn position
        self.right_corner = self.screen_rect.width - (5 * self.screen_scale[0])
        self.bottom_corner = self.screen_rect.height - (5 * self.screen_scale[1])

        # data specific to module
        self.faction_data = self.game.faction_data
        self.coa_list = self.faction_data.coa_list

        self.troop_data = self.game.troop_data
        self.leader_data = self.game.leader_data

        self.battle_map_data = self.game.battle_map_data
        self.weather_data = self.battle_map_data.weather_data
        self.weather_matter_images = self.battle_map_data.weather_matter_images
        self.weather_effect_images = self.battle_map_data.weather_effect_images
        self.day_effect_images = self.battle_map.day_effect_images
        self.weather_list = self.battle_map_data.weather_list
        self.feature_mod = self.battle_map_data.feature_mod

        self.unit_animation_data = self.game.unit_animation_data
        self.body_sprite_pool = self.game.body_sprite_pool
        self.weapon_sprite_pool = self.game.weapon_sprite_pool
        self.armour_sprite_pool = self.game.armour_sprite_pool
        self.effect_sprite_pool = self.game.effect_sprite_pool
        self.effect_animation_pool = self.game.effect_animation_pool
        self.weapon_joint_list = self.game.weapon_joint_list
        self.team_colour = self.game.team_colour
        self.language = self.game.language
        self.localisation = self.game.localisation

        self.unit_animation_pool = None
        self.status_animation_pool = None

        self.game_speed = 0
        self.game_speed_list = (0, 0.5, 1, 2, 4, 6)  # available game speed
        self.day_time = "Day"
        self.old_day_time = self.day_time
        self.all_team_unit = {team: pygame.sprite.Group() for team in range(len(self.team_colour))}
        self.all_team_enemy = {team: pygame.sprite.Group() for team in range(len(self.team_colour))}
        self.team_troop_number = []  # list of troop number in each team, minimum at one because percentage can't divide by 0
        self.last_team_troop_number = []
        self.battle_scale = []
        self.start_troop_number = []
        self.death_troop_number = []
        self.flee_troop_number = []

        self.player_unit = None  # player unit
        self.portrait_rect = None
        self.player_input_state = None  # specific player command input and ui
        self.previous_player_input_state = None

        self.empty_portrait = pygame.Surface((150 * self.screen_scale[0], 150 * self.screen_scale[1]), pygame.SRCALPHA)
        pygame.draw.circle(self.empty_portrait, (20, 20, 20),
                           (self.empty_portrait.get_width() / 2, self.empty_portrait.get_height() / 2),
                           self.empty_portrait.get_width() / 2)

        self.active_unit_list = []  # list of all unit alive in battle, need to be in list for collision check
        self.visible_unit_list = {}  # list of unit visible to the team

        self.best_depth = pygame.display.mode_ok(self.screen_rect.size, self.game.window_style,
                                                 32)  # Set the display mode
        Battle.screen = pygame.display.set_mode(self.screen_rect.size, self.game.window_style,
                                                self.best_depth)  # set up self screen

        # Assign battle variable to some classes
        Unit.sound_effect_pool = self.sound_effect_pool
        Effect.sound_effect_pool = self.sound_effect_pool

        # Create battle ui
        cursor_images = load_images(self.module_dir, subfolder=("ui", "cursor_battle"))  # no need to scale cursor
        self.player1_battle_cursor = BattleCursor(cursor_images, self.player1_key_control)

        self.fps_count = FPSCount(self)  # FPS number counter
        if self.game.show_fps:
            self.add_ui_updater(self.fps_count)

        battle_ui_image = load_images(self.module_dir, screen_scale=self.screen_scale, subfolder=("ui", "battle_ui"))

        self.background = load_image(self.module_dir, self.screen_scale, "background.png",
                                     subfolder=("ui", "battle_ui", "background"),
                                     no_alpha=True)  # Create background image

        battle_ui_dict = make_battle_ui(battle_ui_image)

        self.time_ui = battle_ui_dict["time_ui"]
        self.time_number = battle_ui_dict["time_number"]
        self.battle_scale_ui = battle_ui_dict["battle_scale_ui"]
        self.add_ui_updater(self.time_ui, self.time_number, self.battle_scale_ui)
        self.wheel_ui = battle_ui_dict["wheel_ui"]
        self.health_bar = battle_ui_dict["health_bar"]
        self.stamina_bar = battle_ui_dict["stamina_bar"]
        self.weapon_ui = battle_ui_dict["weapon_ui"]
        self.status_ui = battle_ui_dict["status_ui"]
        self.follower_ui = battle_ui_dict["follower_ui"]

        self.current_weather = Weather(self.time_ui, 4, 0, 0, None)
        Weather.wind_compass_images = {"wind_compass": battle_ui_image["wind_compass"],
                                       "wind_arrow": battle_ui_image["wind_arrow"]}

        # 4 Skill icons UI
        SkillIcon(self.skill_images["0"], (0, 600 * self.screen_scale[1]), "0")
        SkillIcon(self.skill_images["0"], (self.skill_images["0"].get_width(), 600 * self.screen_scale[1]), "1")
        SkillIcon(self.skill_images["0"], (self.skill_images["0"].get_width() * 2, 600 * self.screen_scale[1]), "2")
        SkillIcon(self.skill_images["0"], (self.skill_images["0"].get_width() * 3, 600 * self.screen_scale[1]), "3")

        AimTarget.aim_images = {0: battle_ui_image["aim_0"], 1: battle_ui_image["aim_1"],
                                2: battle_ui_image["aim_2"], 3: pygame.Surface((0, 0))}

        self.battle_done_box = BattleDone((self.screen_rect.width / 2, self.screen_rect.height / 2),
                                          load_image(self.module_dir, self.screen_scale, "menu.png",
                                                     subfolder=("ui", "battlemenu_ui")))
        self.battle_done_button = ButtonUI(battle_ui_image["end_button"], layer=19)
        self.battle_done_button.change_pos(
            (self.battle_done_box.pos[0], self.battle_done_box.image.get_height() * 0.8))

        TextDrama.images = load_images(self.module_dir, screen_scale=self.screen_scale,
                                       subfolder=("ui", "popup_ui", "drama_text"))
        self.drama_text = TextDrama(
            self.battle_camera_size)  # message at the top of screen that show up for important event

        # Battle event log
        self.event_log = EventLog(battle_ui_image["event_log"], (self.screen_rect.width / 2, self.screen_rect.height))
        UIScroll(self.event_log, self.event_log.rect.topright)  # event log scroll
        Unit.event_log = self.event_log  # Assign event_log to unit class to broadcast event to the log

        # Battle ESC menu
        esc_menu_dict = make_esc_menu(self.master_volume, self.music_volume, self.voice_volume, self.effect_volume)
        self.battle_menu = esc_menu_dict["battle_menu"]
        self.battle_menu_button = esc_menu_dict["battle_menu_button"]
        self.esc_option_menu_button = esc_menu_dict["esc_option_menu_button"]
        self.esc_slider_menu = esc_menu_dict["esc_slider_menu"]
        self.esc_value_boxes = esc_menu_dict["esc_value_boxes"]
        self.esc_option_text = esc_menu_dict["volume_texts"]

        self.player1_mini_map = MiniMap((190 / 2 * self.screen_scale[0], self.screen_rect.height))
        self.add_ui_updater(self.player1_mini_map)

        # Create the game camera
        self.camera_mode = "Follow"  # mode of game camera
        self.true_camera_pos = Vector2(500, 500)  # camera pos on battle map
        self.camera_pos = Vector2(self.true_camera_pos[0] * self.screen_scale[0],
                                  self.true_camera_pos[1] * self.screen_scale[
                                      1]) * 5  # Camera pos with screen scale

        self.shown_camera_pos = self.camera_pos  # pos of camera shown to player, in case of screen shaking or other effects

        self.screen_shake_value = 0  # count for how long to shake camera

        self.camera_topleft_corner = (self.camera_pos[0] - self.battle_camera_center[0],
                                      self.camera_pos[1] - self.battle_camera_center[
                                          1])  # calculate top left corner of camera position

        self.camera = Camera(self.screen, self.battle_camera_size)

        self.base_cursor_pos = [0, 0]  # mouse pos on the map based on camera position
        self.battle_cursor_pos = [0, 0]  # mouse position list in battle map not screen with zoom
        self.command_cursor_pos = [0, 0]  # with zoom and screen scale for unit command

    def prepare_new_game(self, player_unit):

        for message in self.inner_prepare_new_game(player_unit):
            print(message, end="")

    def inner_prepare_new_game(self, player_unit):
        """Setup stuff when start new battle"""
        self.campaign_selected = self.game.campaign_selected  # campaign name
        self.map_selected = self.game.map_selected  # map folder name
        self.map_source_selected = str(self.game.map_source_selected)
        self.team_selected = self.game.team_selected  # player selected team

        self.player_unit = player_unit
        self.play_map_type = self.game.play_map_type
        self.play_map_data = self.game.play_map_data
        self.play_source_data = self.game.play_source_data
        self.camp_pos = self.play_map_data["camp_pos"]
        self.camp_enemy_check = {team: {index: False for index, _ in enumerate(value)} for team, value in
                                 self.camp_pos.items()}

        # Load weather schedule
        self.weather_event = [item.copy() for item in self.play_source_data["weather"]].copy()
        convert_str_time(self.weather_event)
        self.weather_playing = self.weather_event[0][1]  # used as the reference for map starting time

        # Random music played from list
        # yield set_start_load(self, "music")
        # if pygame.mixer:
        #     self.SONG_END = pygame.USEREVENT + 1
        #     self.music_list = glob.glob(os.path.join(self.main_dir, "data", "sound", "music", "*.ogg"))
        #     try:
        #         self.music_event = csv_read(self.main_dir, "music_event.csv",
        #                                     ("data", "module", self.module_folder, "map", play_map_type,
        #                                      self.map_selected), output_type="list")
        #         self.music_event = self.music_event[1:]
        #         if self.music_event:
        #             utility.convert_str_time(self.music_event)
        #             self.music_schedule = list(dict.fromkeys([item[1] for item in self.music_event]))
        #             new_list = []
        #             for time in self.music_schedule:
        #                 new_event_list = []
        #                 for event in self.music_event:
        #                     if time == event[1]:
        #                         new_event_list.append(event[0])
        #                 new_list.append(new_event_list)
        #             self.music_event = new_list
        #         else:
        #             self.music_schedule = [self.weather_playing]
        #             self.music_event = []
        #     except:  # any reading error will play random custom music instead
        #         self.music_schedule = [self.weather_playing]
        #         self.music_event = []  # TODO change later when has custom playlist
        # yield set_done_load()

        yield set_start_load(self, "map events")
        map_event = {}
        if self.play_map_type == "preset":  # create map event for preset map
            map_event_text = self.localisation.grab_text(("preset_map", self.game.battle_campaign[self.map_selected],
                                                          self.map_selected, "eventlog", int(self.map_source_selected)))
            map_event = \
            self.game.preset_map_data[self.campaign_selected][self.map_selected][int(self.map_source_selected)][
                "eventlog"].copy()
            for key in map_event:  # insert localisation text into event data
                map_event[key] = map_event[key].copy()  # make a copy to prevent replacement
                if key in map_event_text:
                    map_event[key]["Text"] = map_event_text[key]["Text"]
        EventLog.map_event = map_event

        self.event_log.make_new_log()  # reset old event log

        self.event_log.add_event_log(map_event)

        self.event_schedule = None
        self.event_list = []
        self.event_id = 0
        for index, event in enumerate(self.event_log.map_event):
            if self.event_log.map_event[event]["Time"]:
                if index == 0:
                    self.event_id = event
                    self.event_schedule = self.event_log.map_event[event]["Time"]
                self.event_list.append(event)

        self.time_number.start_setup(self.weather_playing)
        yield set_done_load()

        yield set_start_load(self, "based map images")
        images = load_images(self.module_dir,
                             subfolder=("map", "preset", self.game.battle_campaign[self.map_selected],
                                        self.map_selected))  # look for preset map first
        if not images:  # check custom map battle map
            images = load_images(self.module_dir, subfolder=("map", "custom", self.map_selected))
        self.battle_base_map.draw_image(images["base"])
        self.battle_feature_map.draw_image(images["feature"])
        self.battle_height_map.draw_image(images["height"])

        if "place_name" in images:  # place_name map layer is optional, if not existed in folder then assign None
            place_name_map = images["place_name"]
        else:
            place_name_map = None
        yield set_done_load()

        yield set_start_load(self, "draw battle map")
        self.battle_map.draw_image(self.battle_base_map, self.battle_feature_map, place_name_map, self.camp_pos)
        yield set_done_load()

        yield set_start_load(self, "common setup")
        self.map_corner = (
            len(self.battle_base_map.map_array[0]),
            len(self.battle_base_map.map_array))  # get map size that troop can move

        self.max_camera = ((self.battle_height_map.image.get_width() - 1),
                           (self.battle_height_map.image.get_height() - 1))  # reset max camera to new map size

        self.active_unit_list = []
        self.visible_unit_list = {}

        self.camera_mode = self.start_camera_mode
        if not self.player_unit:
            self.camera_mode = "Free"

        self.setup_battle_unit(self.unit_updater)

        for this_group in self.all_team_unit.values():
            this_group.empty()
        for this_group in self.all_team_enemy.values():
            this_group.empty()

        self.team_troop_number = [0 for _ in
                                  range(len(self.all_team_unit))]  # reset list of troop number in each team
        self.battle_scale = [1 for _ in self.team_troop_number]
        self.start_troop_number = [0 for _ in self.team_troop_number]
        self.death_troop_number = [0 for _ in self.team_troop_number]
        self.flee_troop_number = [0 for _ in self.team_troop_number]
        self.visible_unit_list = {key: {} for key in self.all_team_unit.keys()}

        self.battle_scale_ui.change_fight_scale(self.battle_scale)
        yield set_done_load()

        yield set_start_load(self, "unit animation")
        unit_to_make = tuple(set([this_unit.troop_id for this_unit in self.unit_updater]))
        who_todo = {key: value for key, value in self.troop_data.troop_list.items() if key in unit_to_make}
        who_todo |= {key: value for key, value in self.leader_data.leader_list.items() if key in unit_to_make}
        self.unit_animation_pool, self.status_animation_pool = self.game.create_troop_sprite_pool(who_todo)
        yield set_done_load()

    def run_game(self, map_data):
        # Create Starting Values
        self.game_state = "battle"  # battle mode
        self.current_weather.__init__(self.time_ui, 0, 0, 0, self.weather_data)  # start weather with random first
        self.input_popup = None  # no popup asking for user text input state
        self.drama_text.queue = []  # reset drama text popup queue

        self.change_battle_state()

        self.time_ui.change_pos((self.screen_rect.width / 2, 0), self.time_number)

        self.battle_scale_ui.change_pos(self.time_ui.rect.bottomleft)

        if self.player_unit:
            self.add_skill_icon()
        else:
            self.remove_ui_updater(self.skill_icons)

        self.shown_camera_pos = self.camera_pos

        self.player_unit_input_delay = 0
        self.text_delay = 0
        self.screen_shake_value = 0
        self.ui_timer = 0  # This is timer for ui update function, use realtime
        self.drama_timer = 0  # This is timer for combat related function, use self time (realtime * game_speed)
        self.dt = 0  # Realtime used for time calculation
        self.ui_dt = 0  # Realtime used for ui timer
        self.weather_spawn_timer = 0
        self.ten_second_reset_timer = 0

        self.player_input_state = None
        self.previous_player_input_state = None

        self.base_cursor_pos = [0, 0]  # mouse pos on the map based on camera position
        self.battle_cursor_pos = [0, 0]  # mouse position list in battle map not screen with zoom
        self.command_cursor_pos = [0, 0]  # with zoom and screen scale for unit command

        self.player1_key_control = self.config["USER"]["control player 1"]
        self.player1_key_bind = self.game.player1_key_bind[self.player1_key_control]
        self.player1_key_bind_name = {value: key for key, value in self.player1_key_bind.items()}
        self.player1_key_press = {key: False for key in self.player1_key_bind}
        self.player1_key_hold = {key: False for key in self.player1_key_hold}  # key that consider holding

        skill_key_list = []
        if self.player1_key_control == "keyboard":
            for key, value in self.player1_key_bind.items():
                if "Skill" in key:
                    if type(value) is int:
                        skill_key_list.append(pygame.key.name(value))
                    else:
                        skill_key_list.append(value)
        else:
            if self.joystick_name:
                joyname = self.joystick_name[tuple(self.joystick_name.keys())[0]]
            else:
                joyname = "Other"
            for key, value in self.player1_key_bind.items():
                if "Skill" in key:
                    skill_key_list.append(self.joystick_bind_name[joyname][value])

        for index, skill_icon in enumerate(self.skill_icons):
            skill_icon.change_key(skill_key_list[index])

        self.time_update()
        self.effect_updater.update(self.active_unit_list, self.dt)
        self.screen.blit(self.background, (0, 0))
        self.realtime_ui_updater.add(self.player1_battle_cursor)  # reset cursor when start battle
        self.remove_ui_updater(self.cursor)
        # self.map_def_array = []
        # self.mapunitarray = [[x[random.randint(0, 1)] if i != j else 0 for i in range(1000)] for j in range(1000)]
        # pygame.mixer.music.set_endevent(self.SONG_END)  # End current music before battle start

        frame = 0
        while True:  # self running
            frame += 1

            if frame % 30 == 0 and hasattr(self.game, "profiler"):
                self.game.profiler.refresh()

            self.cursor.scroll_down = False
            self.cursor.scroll_up = False
            key_state = pygame.key.get_pressed()
            esc_press = False

            self.player1_key_press = dict.fromkeys(self.player1_key_press, False)
            self.player1_key_hold = dict.fromkeys(self.player1_key_hold, False)

            self.true_dt = self.clock.get_time() / 1000  # dt before game_speed

            self.realtime_ui_updater.remove(self.text_popup)  # remove button text popup every update

            if self.player1_key_control == "keyboard" or self.game_state in ("menu", "end") or self.input_popup:
                if self.player1_key_control == "keyboard":
                    for key in self.player1_key_press:  # check for key holding
                        if type(self.player1_key_bind[key]) == int and key_state[self.player1_key_bind[key]]:
                            self.player1_key_hold[key] = True
            else:
                for joystick in self.joysticks.values():
                    for i in range(joystick.get_numaxes()):
                        if joystick.get_axis(i) > 0.1 or joystick.get_axis(i) < -0.1:
                            axis_name = "axis" + number_to_minus_or_plus(joystick.get_axis(i)) + str(i)
                            if axis_name in self.player1_key_bind_name:
                                self.player1_key_hold[self.player1_key_bind_name[axis_name]] = True

                    for i in range(joystick.get_numbuttons()):
                        if joystick.get_button(i) and i in self.player1_key_bind_name:
                            self.player1_key_hold[self.player1_key_bind_name[i]] = True

                    for i in range(joystick.get_numhats()):
                        if joystick.get_hat(i)[0] > 0.1 or joystick.get_hat(i)[0] < 0.1:
                            hat_name = "hat" + number_to_minus_or_plus(joystick.get_hat(i)[0]) + str(0)
                            if hat_name in self.player1_key_bind_name:
                                self.player1_key_press[self.player1_key_bind_name[hat_name]] = True
                        if joystick.get_hat(i)[1] > 0.1 or joystick.get_hat(i)[1] < 0.1:
                            hat_name = "hat" + number_to_minus_or_plus(joystick.get_hat(i)[1]) + str(1)
                            if hat_name in self.player1_key_bind_name:
                                self.player1_key_press[self.player1_key_bind_name[hat_name]] = True

            self.base_cursor_pos = Vector2(
                (self.player1_battle_cursor.pos[0] - self.battle_camera_center[0] + self.camera_pos[0]),
                (self.player1_battle_cursor.pos[1] - self.battle_camera_center[1] + self.camera_pos[
                    1]))  # mouse pos on the map based on camera position
            self.battle_cursor_pos = self.base_cursor_pos / 5  # mouse pos on the map at current camera zoom scale
            self.command_cursor_pos = Vector2(self.battle_cursor_pos[0] / self.screen_scale[0],
                                              self.battle_cursor_pos[1] / self.screen_scale[1])  # with screen scale

            for event in pygame.event.get():  # get event that happen
                if event.type == QUIT:  # quit game
                    self.input_popup = ("confirm_input", "quit")
                    self.input_ui.change_instruction("Quit Game?")
                    self.add_ui_updater(self.confirm_ui_popup, self.cursor)

                # elif event.type == self.SONG_END:  # change music track
                #     pygame.mixer.music.unload()
                #     self.picked_music = randint(0, len(self.playing_music) - 1)
                #     pygame.mixer.music.load(self.music_list[self.playing_music[self.picked_music]])
                #     pygame.mixer.music.play(fade_ms=100)

                elif event.type == pygame.JOYBUTTONUP:
                    joystick = event.instance_id
                    if self.player1_key_control == "joystick" and \
                            event.button in self.player1_key_bind_name:  # check for key press
                        self.player1_key_press[self.player1_key_bind_name[event.button]] = True

                elif event.type == pygame.KEYDOWN:
                    event_key_press = event.key
                    if event_key_press == K_ESCAPE:  # accept esc button always
                        esc_press = True
                    if self.player1_key_control == "keyboard" and \
                            event_key_press in self.player1_key_bind_name:  # check for key press
                        self.player1_key_press[self.player1_key_bind_name[event_key_press]] = True

                    # FOR DEVELOPMENT

                    # elif key_press == pygame.K_l and self.current_selected is not None:
                    #     for unit in self.player_unit.alive_troop_follower:
                    #         unit.base_morale = 0
                    elif event_key_press == pygame.K_k:
                        if self.player_unit:
                            for unit in self.player_unit.alive_leader_follower:
                                unit.health -= unit.health
                        # self.player_unit.health = 0
                    # elif key_press == pygame.K_m and self.player_unit is not None:
                    #     for follower in self.player_unit.alive_troop_follower:
                    #         follower.health = 0
                    # elif key_press == pygame.K_n and self.player_unit is not None:
                    #     for follower in self.player_unit.alive_leader_follower:
                    #         follower.health = 0
                    # elif key_press == pygame.K_b and self.player_unit is not None:
                    #     for follower in self.player_unit.alive_leader_follower:
                    #         for follower2 in follower.alive_troop_follower:
                    #             follower2.health = 0

                    if event.key == K_F1:
                        self.drama_text.queue.append("Hello and welcome to showcase video")
                    # elif event.key == K_F2:
                    #     self.drama_text.queue.append("Keybinding and Joystick controller")
                    # elif event.key == K_F3:
                    #     self.drama_text.queue.append("See video description for more detail")
                    # elif event.key == K_F4:
                    #     self.drama_text.queue.append("He juggled his sword and sing the Song of Roland")
                    # elif event.key == K_F5:
                    #     self.drama_text.queue.append("Rushed to the English line, he fought valiantly alone")
                    # elif event.key == K_F6:
                    #     self.drama_text.queue.append("The Saxon swarmed him and left him death, that they shall atone")
                    elif event.key == K_F7:  # clear profiler
                        if hasattr(self.game, "profiler"):
                            self.game.profiler.clear()
                    elif event.key == K_F8:  # show/hide profiler
                        if not hasattr(self.game, "profiler"):
                            self.game.setup_profiler()
                        self.game.profiler.switch_show_hide()
                    # elif event.key == K_F9:
                    #     for this_unit in self.unit_updater:
                    #         if this_unit.team == 1:
                    #             this_unit.health = 0

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 4:  # Mouse scroll up
                        self.cursor.scroll_up = True
                    elif event.button == 5:  # Mouse scroll down
                        self.cursor.scroll_down = True

                    press_button = self.mouse_bind_name[event.button]
                    if self.player1_key_control == "keyboard" and press_button in self.player1_key_bind_name:
                        # check for mouse press
                        self.player1_key_press[self.player1_key_bind_name[press_button]] = True

                elif event.type == pygame.JOYDEVICEADDED:
                    # Player add new joystick by plug in
                    joy = pygame.joystick.Joystick(event.device_index)
                    self.joysticks[joy.get_instance_id()] = joy

                elif event.type == pygame.JOYDEVICEREMOVED:
                    # Player unplug joystick
                    del self.joysticks[event.instance_id]

            for index, press in enumerate(pygame.mouse.get_pressed()):
                if press:  # check for mouse hold
                    if self.player1_key_control == "keyboard":
                        button_press = self.mouse_bind_name[index + 1]
                        if button_press in self.player1_key_bind_name:
                            self.player1_key_hold[self.player1_key_bind_name[button_press]] = True
                    if index == 0:  # Hold left click
                        mouse_left_down = True

            if self.player1_key_press["Menu/Cancel"]:  # or self.player2_key_press["Menu/Cancel"]
                # open/close menu
                esc_press = True

            if self.player_unit_input_delay:  # delay for command input
                self.player_unit_input_delay -= self.dt
                if self.player_unit_input_delay < 0:
                    self.player_unit_input_delay = 0

            self.ui_updater.update()  # update ui before more specific update

            if esc_press:  # open/close menu
                if self.game_state == "battle":  # in battle
                    self.game_speed = 0
                    self.game_state = "menu"  # open menu
                    self.add_ui_updater(self.battle_menu,
                                        self.battle_menu_button)  # add menu and its buttons to drawer
                    esc_press = False  # reset esc press, so it not stops esc menu when open
                    self.realtime_ui_updater.remove(self.player1_battle_cursor)
                    self.add_ui_updater(self.cursor)

            if self.game_state == "battle":  # game in battle state
                if not self.player_input_state:  # register user input during gameplay
                    # keyboard input
                    self.camera_process()
                    if self.player_unit:
                        self.player_input_process()

                else:  # register and process ui that require player input and block everything else
                    if type(self.player_input_state) is not str:  # ui input state
                        choice = self.player_input_state.selection(self.player1_battle_cursor.pos)
                        if self.player_input_state == self.wheel_ui:  # wheel ui process
                            if self.player1_key_press["Main Weapon Attack"]:
                                self.wheel_ui_process(choice)
                            elif self.player1_key_press["Order Menu"]:  # Close unit command wheel ui
                                self.realtime_ui_updater.remove(self.wheel_ui)
                                old_player_input_state = self.player_input_state
                                self.player_input_state = self.previous_player_input_state
                                self.previous_player_input_state = old_player_input_state
                    elif "aim" in self.player_input_state:
                        if "skill" not in self.player_input_state:
                            self.player_aim()
                        else:  # skill that require player to input target
                            self.player_skill_perform()

                # Drama text function
                if not self.drama_timer and self.drama_text.queue:  # Start timer and draw if there is event queue
                    self.realtime_ui_updater.add(self.drama_text)
                    self.drama_text.process_queue()
                    self.drama_timer = 0.1
                elif self.drama_timer:
                    self.drama_text.play_animation()
                    self.drama_timer += self.ui_dt
                    if self.drama_timer > 5:  # drama popup last for 5 seconds
                        self.drama_timer = 0
                        self.realtime_ui_updater.remove(self.drama_text)

                    # Music System
                    # if self.music_schedule and self.time_number.time_number >= self.music_schedule[0] and \
                    #         self.music_event:
                    #     pygame.mixer.music.unload()
                    #     self.playing_music = self.music_event[0].copy()
                    #     self.picked_music = randint(0, len(self.playing_music) - 1)
                    #     pygame.mixer.music.load(self.music_list[self.playing_music[self.picked_music]])
                    #     pygame.mixer.music.play(fade_ms=100)
                    #     self.music_schedule = self.music_schedule[1:]
                    #     self.music_event = self.music_event[1:]

                # Run troop ai logic no more than limit number of unit per update to prevent stutter
                if self.troop_ai_logic_queue:
                    limit = int(len(self.troop_ai_logic_queue) / 20)
                    if limit < 10:
                        limit = 10
                        if limit > len(self.troop_ai_logic_queue):
                            limit = len(self.troop_ai_logic_queue)
                    for index in range(limit):
                        this_unit = self.troop_ai_logic_queue[index]
                        if this_unit.alive:  # in case unit die or flee during queue
                            this_unit.ai_unit()

                    self.troop_ai_logic_queue = self.troop_ai_logic_queue[limit:]

                # Update game time
                self.dt = self.true_dt * self.game_speed  # apply dt with game_speed for calculation
                if self.dt > 0.1:  # one frame update should not be longer than 0.1 second for calculation
                    self.dt = 0.1  # make it so stutter and lag does not cause overtime issue

                self.ui_timer += self.dt  # ui update by real time instead of self time to reduce workload
                self.ui_dt = self.dt  # get ui timer before apply self

                if self.dt:  # Part that run when game not pause only
                    # Event log
                    if self.event_id and self.time_number.time_number >= self.event_schedule:
                        self.event_log.add_log(None, event_id=self.event_id)
                        self.event_list.pop(0)
                        if self.event_list:
                            self.event_id = self.event_list[0]
                            self.event_schedule = self.event_log.map_event[self.event_id]["Time"]
                        else:
                            self.event_id = None

                    # Weather system
                    if self.weather_playing and self.time_number.time_number >= self.weather_playing:
                        this_weather = self.weather_event[0]

                        if this_weather[0] in self.weather_data:
                            self.current_weather.__init__(self.time_ui, this_weather[0], this_weather[2],
                                                          this_weather[3], self.weather_data)
                        else:  # Clear weather when no weather found, also for when input weather not in module
                            self.current_weather.__init__(self.time_ui, 4, 0, 0, self.weather_data)
                        self.weather_event.pop(0)
                        if self.current_weather.name in self.weather_effect_images:
                            self.battle_map.change_map_stuff("effect", self.weather_effect_images[
                                self.current_weather.name][self.current_weather.level],
                                                             self.day_effect_images[self.day_time])

                        if self.weather_event:  # Get end time of next event which is now index 0
                            self.weather_playing = self.weather_event[0][1]
                        else:
                            self.weather_playing = None

                    if self.current_weather.spawn_rate:
                        self.weather_spawn_timer += self.dt
                        if self.weather_spawn_timer >= self.current_weather.spawn_rate:
                            self.weather_spawn_timer = 0
                            self.spawn_weather_matter()

                    # Screen shaking
                    self.shown_camera_pos = self.camera_pos  # reset camera pos first
                    if self.screen_shake_value:
                        self.screen_shake_value -= 1
                        self.shake_camera()
                        if self.screen_shake_value < 0:
                            self.screen_shake_value = 0

                    self.ten_second_reset_timer += self.dt
                    if self.ten_second_reset_timer > 10:
                        self.camp_enemy_check = {team: {index: False for index, _ in enumerate(value)} for
                                                 team, value in self.camp_enemy_check.items()}
                        self.ten_second_reset_timer -= 10

                    # Battle related updater
                    self.unit_updater.update(self.dt)
                    self.effect_updater.update(self.active_unit_list, self.dt)
                    self.realtime_ui_updater.update()

                    self.time_number.timer_update(self.dt * 100)  # update battle time
                    self.time_update()

                    self.camera.update(self.shown_camera_pos, self.battle_camera,
                                       out_surfaces=self.realtime_ui_updater)

                for key, value in self.sound_effect_queue.items():  # play each sound effect initiate in this loop
                    self.play_sound_effect(key, value[0], shake=value[1])
                self.sound_effect_queue = {}

                if self.ui_timer >= 0.1:
                    if self.player_unit:
                        self.follower_ui.value_input(self.player_unit)
                        self.health_bar.value_input(self.player_unit)
                        self.stamina_bar.value_input(self.player_unit)
                        self.weapon_ui.value_input(self.player_unit)
                        self.countdown_skill_icon()
                    self.battle_scale = [value / sum(self.team_troop_number) for value in
                                         self.team_troop_number]
                    self.battle_scale_ui.change_fight_scale(
                        self.battle_scale)  # change fight colour scale on time_ui bar
                    self.ui_drawer.draw(self.screen)  # draw the UI
                    self.ui_timer -= 0.1

            elif self.game_state == "end":
                self.screen.blit(self.background, (0, 0))  # keep reset screen
                self.ui_drawer.draw(self.screen)  # draw the UI
                if self.battle_done_box not in self.ui_updater:  # pop out who win screen first
                    if not self.active_unit_list:  # draw
                        self.battle_done_box.pop("Draw")
                    else:
                        for key, value in self.all_team_unit.items():
                            if value:
                                if "wt" + str(key) in self.event_log.map_event:
                                    self.event_log.add_log(
                                        (0, self.event_log.map_event["wt" + str(key)]["Text"]))
                                self.battle_done_box.pop(self.faction_data.faction_list[map_data[
                                    "Team Faction " + str(key)][0]]["Name"], self.coa_list[
                                                             int(map_data["Team Faction " + str(key)][0])])
                                break
                    self.battle_done_button.rect = self.battle_done_button.image.get_rect(
                        midtop=self.battle_done_button.pos)
                    self.add_ui_updater(self.battle_done_box, self.battle_done_button, self.cursor)
                    self.realtime_ui_updater.remove(self.player1_battle_cursor)
                else:
                    if esc_press or self.battle_done_button.event_press:
                        coa_list = [self.coa_list[map_data[key][0]] for key in map_data if
                                    "Team Faction" in key if map_data[key]]
                        if not self.battle_done_box.result_showing:  # show battle result stat
                            faction_name = {key: self.faction_data.faction_list[map_data[
                                key][0]]["Name"] for key in map_data if
                                            "Team Faction" in key if map_data[key]}

                            self.battle_done_box.show_result(coa_list,
                                                             {"Faction": faction_name,
                                                              "Total": self.start_troop_number,
                                                              "Alive": self.team_troop_number,
                                                              "Death": self.death_troop_number,
                                                              "Flee": self.flee_troop_number})
                            self.battle_done_button.rect = self.battle_done_button.image.get_rect(
                                center=(self.battle_done_box.rect.midbottom[0],
                                        self.battle_done_box.rect.midbottom[
                                            1] / 1.1))
                        else:  # already shown result, end battle
                            self.exit_battle()
                            return

            elif self.game_state == "menu":  # Complete battle pause when open either esc menu or encyclopedia
                self.screen.blit(self.background, (0, 0))  # keep reset screen
                self.ui_drawer.draw(self.screen)  # draw the UI

                if self.input_popup:  # currently, have input text pop up on screen, stop everything else until done
                    self.screen.blit(self.background, (0, 0))  # keep reset screen
                    self.ui_drawer.draw(self.screen)  # draw the UI
                    if self.input_ok_button.event_press:
                        if self.input_popup[1] == "quit":  # quit game
                            pygame.quit()
                            sys.exit()

                        self.input_box.text_start("")
                        self.input_popup = None
                        self.remove_ui_updater(self.input_ui_popup, self.confirm_ui_popup)
                        if self.game_state == "battle":
                            self.realtime_ui_updater.add(self.player1_battle_cursor)
                            self.remove_ui_updater(self.cursor)

                    elif self.input_cancel_button.event_press or esc_press:
                        self.change_pause_update(False)
                        self.input_box.text_start("")
                        self.input_popup = None
                        self.remove_ui_updater(self.input_ui_popup, self.confirm_ui_popup)

                else:
                    command = self.escmenu_process(esc_press)
                    if command == "end_battle":
                        return

            display.update()  # update game display, draw everything

            self.clock.tick(60)  # clock update even if self pause

    def add_ui_updater(self, *args):
        self.ui_updater.add(*args)
        self.ui_drawer.add(*args)

    def remove_ui_updater(self, *args):
        self.ui_updater.remove(*args)
        self.ui_drawer.remove(*args)

    def exit_battle(self):
        self.ui_updater.clear(self.screen, self.background)  # clear all sprite
        self.battle_camera.clear(self.screen, self.background)  # clear all sprite

        self.remove_ui_updater(self.battle_menu, self.battle_menu_button, self.esc_slider_menu.values(),
                               self.esc_value_boxes.values(), self.esc_option_text.values(), self.battle_done_box,
                               self.battle_done_button)  # remove menu

        # remove all reference from battle object
        self.player_unit = None

        self.active_unit_list = []

        self.troop_ai_logic_queue = []

        clean_group_object((self.shoot_lines, self.all_units, self.effect_updater, self.weather_matters))

        self.unit_animation_pool = None
        self.status_animation_pool = None
        self.generic_action_data = None

        self.sound_effect_queue = {}

        self.battle_base_map.clear_image()
        self.battle_feature_map.clear_image()
        self.battle_height_map.clear_image()
        self.battle_map.clear_image()

        self.drama_timer = 0  # reset drama text popup
        self.realtime_ui_updater.remove(self.drama_text)
