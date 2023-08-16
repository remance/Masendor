import ast
import configparser
import glob
import os.path
import sys
from pathlib import Path

import pygame
from pygame.locals import *

from engine.battle.battle import Battle
from engine.battle.setup_battle_unit import setup_battle_unit
from engine.battlemap.battlemap import BaseMap, FeatureMap, HeightMap, FinalMap
from engine.data.datalocalisation import Localisation
from engine.data.datamap import BattleMapData
from engine.data.datasprite import TroopAnimationData
from engine.effect.effect import Effect
from engine.game.activate_input_popup import activate_input_popup
from engine.game.assign_key import assign_key
from engine.game.back_mainmenu import back_mainmenu
from engine.game.change_battle_source import change_battle_source
from engine.game.change_pause_update import change_pause_update
from engine.game.change_sound_volume import change_sound_volume
from engine.game.create_config import create_config
from engine.game.create_preview_map import create_preview_map
from engine.game.create_sound_effect_pool import create_sound_effect_pool
from engine.game.create_team_coa import create_team_coa
from engine.game.create_troop_sprite import create_troop_sprite
from engine.game.create_troop_sprite_pool import create_troop_sprite_pool
from engine.game.loading_screen import loading_screen
from engine.game.menu_custom_leader_setup import menu_custom_leader_setup
from engine.game.menu_custom_map_select import custom_map_list_on_select, custom_faction_list_on_select, \
    custom_weather_list_on_select, menu_custom_map_select
from engine.game.menu_custom_unit_setup import menu_custom_unit_setup, custom_set_list_on_select
from engine.game.menu_game_editor import menu_game_editor
from engine.game.menu_keybind import menu_keybind
from engine.game.menu_main import menu_main
from engine.game.menu_option import menu_option
from engine.game.menu_preset_map_select import menu_preset_map_select
from engine.game.read_selected_map_lore import read_selected_map_lore
# Method in game.setup
from engine.game.setup.make_editor_ui import make_editor_ui
from engine.game.setup.make_faction_troop_leader_data import make_faction_troop_leader_data
from engine.game.setup.make_icon_data import make_icon_data
from engine.game.setup.make_input_box import make_input_box
from engine.game.setup.make_lorebook import make_lorebook
from engine.game.setup.make_option_menu import make_option_menu
from engine.game.start_battle import start_battle
from engine.lorebook.lorebook import Lorebook, SubsectionName, lorebook_process
from engine.menubackground.menubackground import MenuActor, MenuRotate, StaticImage
from engine.uibattle.uibattle import MiniMap, UnitIcon, SkillIcon, SpriteIndicator, AimTarget, BattleCursor, \
    WeaponUI, FollowerUI, StatusUI, UnitSelector, UIScroll, Profiler, TempUnitIcon, FPSCount, HealthStaminaBar
from engine.uimenu.uimenu import MapPreview, OptionMenuText, SliderMenu, TeamCoa, MenuCursor, BoxUI, BrownMenuButton, \
    ListUI, ListAdapter, URLIconLink, CampaignListAdapter, LeaderModel, MenuButton, BackgroundBox, OrgChart, \
    TickBox, TextPopup, MapTitle, NameTextBox
from engine.unit.unit import Unit, Troop, Leader, rotation_dict, rotation_list
from engine.updater.updater import ReversedLayeredUpdates
from engine.utility import load_image, load_images, csv_read, edit_config, load_base_button, text_objects, \
    number_to_minus_or_plus
from engine.weather.weather import MatterSprite, SpecialWeatherEffect

version_name = "Victores et Victos"  # Game name that will appear as game name


class Game:
    game = None
    battle = None
    main_dir = None
    data_dir = None
    font_dir = None
    module_dir = None
    art_style_dir = None
    ui_font = None
    language = None
    localisation = None
    cursor = None
    ui_updater = None
    ui_drawer = None
    module = None
    art_style = None
    art_style_list = None

    screen_rect = None
    screen_scale = (1, 1)
    screen_size = ()

    game_version = "0.7.2"
    mouse_bind = {"left click": 1, "middle click": 2, "right click": 3, "scroll up": 4, "scroll down": 5}
    mouse_bind_name = {value: key for key, value in mouse_bind.items()}
    joystick_bind_name = {"XBox": {0: "A", 1: "B", 2: "X", 3: "Y", 4: "-", 5: "Home", 6: "+", 7: "Start", 8: None,
                                   9: None, 10: None, 11: "D-Up", 12: "D-Down", 13: "D-Left", 14: "D-Right",
                                   15: "Capture", "axis-0": "L. Stick Left", "axis+0": "L. Stick R.",
                                   "axis-1": "L. Stick U.", "axis+1": "L. Stick D.",
                                   "axis-2": "R. Stick Left", "axis+2": "R. Stick R.",
                                   "axis-3": "R. Stick U.", "axis+3": "R. Stick D.",
                                   "hat-0": "L. Arrow", "hat+0": "R. Arrow",
                                   "hat-1": "U. Arrow", "hat+1": "D. Arrow", },
                          "Other": {0: "1", 1: "2", 2: "3", 3: "4", 4: "L1", 5: "R1", 6: "L2", 7: "R2", 8: "Select",
                                    9: "Start", 10: "L. Stick", 11: "R. Stick", 12: None, 13: None, 14: None, 15: None,
                                    "axis-0": "L. Stick L.", "axis+0": "L. Stick R.",
                                    "axis-1": "L. Stick U.", "axis+1": "L. Stick D.",
                                    "axis-2": "R. Stick Left", "axis+2": "R. Stick R.",
                                    "axis-3": "R. Stick U.", "axis+3": "R. Stick D.",
                                    "hat-0": "L. Arrow", "hat+0": "R. Arrow",
                                    "hat-1": "U. Arrow", "hat+1": "D. Arrow",
                                    },
                          "PS": {0: "X", 1: "O", 2: "□", 3: "△", 4: "Share", 5: "PS", 6: "Options", 7: None, 8: None,
                                 9: None, 10: None, 11: "D-Up", 12: "D-Down", 13: "D-Left", 14: "D-R.",
                                 15: "T-Pad", "axis-0": "L. Stick L.", "axis+0": "L. Stick R.",
                                 "axis-1": "L. Stick U.", "axis+1": "L. Stick D.",
                                 "axis-2": "R. Stick Left", "axis+2": "R. Stick R.",
                                 "axis-3": "R. Stick U.", "axis+3": "R. Stick D.",
                                 "hat-0": "L. Arrow", "hat+0": "R. Arrow",
                                 "hat-1": "U. Arrow", "hat+1": "D. Arrow"}}

    # import from game
    activate_input_popup = activate_input_popup
    assign_key = assign_key
    back_mainmenu = back_mainmenu
    change_battle_source = change_battle_source
    change_pause_update = change_pause_update
    change_sound_volume = change_sound_volume
    create_config = create_config
    create_preview_map = create_preview_map
    create_sound_effect_pool = create_sound_effect_pool
    create_team_coa = create_team_coa
    create_troop_sprite = create_troop_sprite
    create_troop_sprite_pool = create_troop_sprite_pool
    loading_screen = loading_screen
    menu_game_editor = menu_game_editor
    menu_keybind = menu_keybind
    menu_main = menu_main
    menu_custom_map_select = menu_custom_map_select
    menu_option = menu_option
    menu_preset_map_select = menu_preset_map_select
    menu_custom_leader_setup = menu_custom_leader_setup
    menu_custom_unit_setup = menu_custom_unit_setup
    read_selected_map_lore = read_selected_map_lore
    start_battle = start_battle
    lorebook_process = lorebook_process
    setup_battle_unit = setup_battle_unit

    troop_sprite_size = (200, 200)

    team_colour = {0: (50, 50, 50), 1: (50, 50, 150), 2: (200, 50, 50), 3: (200, 200, 0), 4: (0, 200, 0),
                   5: (200, 0, 200), 6: (140, 90, 40), 7: (100, 170, 170), 8: (230, 120, 0), 9: (230, 60, 110),
                   10: (130, 120, 200), 11: (100, 150, 120), 12: (175, 165, 115)}
    selected_team_colour = {0: (200, 200, 200), 1: (180, 180, 255), 2: (255, 150, 150), 3: (255, 255, 150),
                            4: (150, 255, 150), 5: (255, 150, 255), 6: (200, 140, 70), 7: (160, 200, 200),
                            8: (255, 150, 45), 9: (230, 140, 160), 10: (200, 190, 230), 11: (170, 200, 180),
                            12: (210, 200, 170)}

    skill_level_text = ("E", "E+", "D", "D+", "C", "C+", "B", "B+", "A", "A+", "S")

    resolution_list = ("3200 x 1800", "2560 x 1440", "1920 x 1080", "1600 x 900", "1360 x 768",
                       "1280 x 720", "1024 x 576", "960 x 540", "854 x 480")

    def __init__(self, main_dir, error_log):

        Game.game = self
        Game.main_dir = main_dir
        Game.data_dir = os.path.join(self.main_dir, "data")
        Game.font_dir = os.path.join(self.data_dir, "font")

        pygame.init()  # Initialize pygame

        pygame.mouse.set_visible(False)  # set mouse as not visible, use in-game mouse sprite

        self.error_log = error_log
        self.error_log.write("Game Version: " + self.game_version)

        part_folder = Path(os.path.join(self.data_dir, "module"))
        self.module_list = {os.path.split(
            os.sep.join(os.path.normpath(x).split(os.sep)))[-1]: x for x
                            in part_folder.iterdir() if x.is_dir()}  # get module list
        if "tutorial" in self.module_list:
            self.module_list.pop("tutorial")  # get tutorial module from list

        # Read config file
        config = configparser.ConfigParser()  # initiate config reader
        try:
            config.read_file(open(os.path.join(self.main_dir, "configuration.ini")))  # read config file
        except FileNotFoundError:  # Create config file if not found with the default
            config = self.create_config()

        try:
            self.config = config
            self.show_fps = int(self.config["USER"]["fps"])
            self.screen_width = int(self.config["USER"]["screen_width"])
            self.screen_height = int(self.config["USER"]["screen_height"])
            self.full_screen = int(self.config["USER"]["full_screen"])
            self.master_volume = float(self.config["USER"]["master_volume"])
            self.music_volume = float(self.config["USER"]["music_volume"])
            self.play_music_volume = self.master_volume * self.music_volume / 10000  # convert volume into percentage
            self.effect_volume = float(self.config["USER"]["effect_volume"])
            self.play_effect_volume = self.master_volume * self.effect_volume / 10000
            self.voice_volume = float(self.config["USER"]["voice_volume"])
            self.play_voice_volume = self.master_volume * self.voice_volume / 10000
            self.profile_name = str(self.config["USER"]["player_Name"])
            self.language = str(self.config["USER"]["language"])
            self.player1_key_bind = ast.literal_eval(self.config["USER"]["keybind player 1"])
            self.player1_key_control = self.config["USER"]["control player 1"]
            Game.module = self.config["USER"]["module"]
            Game.art_style = self.config["USER"]["art_style"]
            if self.game_version != self.config["VERSION"]["ver"]:  # remake config as game version change
                raise KeyError  # cause KeyError to reset config file
        except (KeyError, TypeError, NameError):  # config error will make the game recreate config with default
            config = self.create_config()
            self.config = config
            self.show_fps = int(self.config["USER"]["fps"])
            self.screen_width = int(self.config["USER"]["screen_width"])
            self.screen_height = int(self.config["USER"]["screen_height"])
            self.full_screen = int(self.config["USER"]["full_screen"])
            self.master_volume = float(self.config["USER"]["master_volume"])
            self.music_volume = float(self.config["USER"]["music_volume"])
            self.play_music_volume = self.master_volume * self.music_volume / 10000
            self.effect_volume = float(self.config["USER"]["effect_volume"])
            self.play_effect_volume = self.master_volume * self.effect_volume / 10000
            self.voice_volume = float(self.config["USER"]["voice_volume"])
            self.play_voice_volume = self.master_volume * self.voice_volume / 10000
            self.profile_name = str(self.config["USER"]["player_Name"])
            self.language = str(self.config["USER"]["language"])
            self.player1_key_bind = ast.literal_eval(self.config["USER"]["keybind player 1"])
            self.player1_key_control = self.config["USER"]["control player 1"]
            Game.module = self.config["USER"]["module"]
            Game.art_style = self.config["USER"]["art_style"]

        Game.language = self.language

        self.module_folder = self.module_list[self.module]
        self.error_log.write("Use module: " + self.module)  # error log selected module

        Game.module_dir = os.path.join(self.data_dir, "module", self.module_folder)
        Game.art_style_dir = os.path.join(self.module_dir, "animation", self.art_style)
        Game.ui_font = csv_read(self.module_dir, "ui_font.csv", ("ui",), header_key=True)
        for item in Game.ui_font:  # add ttf file extension for font data reading.
            Game.ui_font[item] = os.path.join(self.font_dir, Game.ui_font[item]["Font"] + ".ttf")

        part_folder = Path(os.path.join(self.module_dir, "animation"))
        Game.art_style_list = {os.path.split(
            os.sep.join(os.path.normpath(x).split(os.sep)))[-1]: x for x
                               in part_folder.iterdir() if x.is_dir()}  # get art style list
        config.read_file(open(os.path.join(self.art_style_dir, "stat.ini")))  # read config file

        self.design_sprite_size = (int(config["DEFAULT"]["design_sprite_width"]),
                                   int(config["DEFAULT"]["design_sprite_height"]))

        # Set the display mode
        # game default screen size is 1920 x 1080, other resolution get scaled from there
        Game.screen_scale = (self.screen_width / 1920, self.screen_height / 1080)
        Game.screen_size = (self.screen_width, self.screen_height)

        self.window_style = 0
        if self.full_screen == 1:
            self.window_style = pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(self.screen_size, self.window_style)
        Game.screen_rect = self.screen.get_rect()

        Unit.screen_scale = self.screen_scale
        Unit.team_colour = self.team_colour
        MapPreview.colour = self.team_colour
        MapPreview.selected_colour = self.selected_team_colour
        MiniMap.colour = self.team_colour
        MiniMap.selected_colour = self.selected_team_colour
        UnitIcon.colour = self.team_colour
        Effect.screen_scale = self.screen_scale
        FinalMap.team_colour = self.team_colour
        FinalMap.selected_team_colour = self.selected_team_colour

        self.clock = pygame.time.Clock()  # set get clock

        self.loading = load_image(self.module_dir, self.screen_scale, "loading.png", ("ui", "mainmenu_ui"))
        self.loading = pygame.transform.scale(self.loading, self.screen_rect.size)

        self.joysticks = {}
        self.joystick_name = {}

        self.map_type = ""
        self.team_selected = 1
        self.unit_selected = None
        self.map_source_selected = 0  # current selected map source
        self.team_pos = {}  # for saving preview map unit pos
        self.play_map_data = {"info": {"weather": [[0, "09:00:00", 0, 0]]}, "unit": {"pos": {}}, "camp_pos": {}}
        self.play_source_data = {"unit": [], "event_log": {}, "weather": [[0, "09:00:00", 0, 0]]}
        self.remember_custom_list = {}  # dict to save actual list and its localisation name item

        self.dt = 0
        self.text_delay = 0
        self.url_delay = 0

        # Decorate game icon window
        # icon = load_image(self.data_dir, "sword.jpg")
        # icon = pygame.transform.scale(icon, (32, 32))
        # pygame.display.set_icon(icon)

        # Initialise groups

        Game.ui_updater = ReversedLayeredUpdates()  # main drawer for ui in main menu
        Game.ui_drawer = pygame.sprite.LayeredUpdates()

        # game start menu group
        self.menu_icon = pygame.sprite.Group()  # mostly for option icon like volume or screen resolution
        self.menu_slider = pygame.sprite.Group()

        # encyclopedia group
        self.subsection_name = pygame.sprite.Group()  # subsection name objects group in encyclopedia blit on lore_name_list
        self.tag_filter_name = pygame.sprite.Group()  # tag filter objects group in encyclopedia blit on filter_name_list

        # battle select menu group
        self.team_coa = pygame.sprite.Group()  # team coat of arm that also act as team selection icon

        # battle object group
        self.battle_camera = pygame.sprite.LayeredUpdates()  # layer drawer battle camera, all image pos should be based on the map not screen
        self.battle_ui_updater = ReversedLayeredUpdates()  # this is updater and drawer for ui, all image pos should be based on the screen
        self.battle_ui_drawer = pygame.sprite.LayeredUpdates()
        self.battle_cursor_drawer = pygame.sprite.LayeredUpdates()

        self.unit_updater = pygame.sprite.Group()  # updater for unit objects
        self.realtime_ui_updater = pygame.sprite.Group()  # for UI stuff that need to be updated in real time like drama and weather objects, also used as drawer
        self.effect_updater = pygame.sprite.Group()  # updater for effect objects (e.g. range melee_attack sprite)

        self.all_units = pygame.sprite.Group()  # group to keep all unit object for cleaning

        self.preview_units = pygame.sprite.Group()  # group for unit list in unit select screen

        self.shoot_lines = pygame.sprite.Group()
        self.button_ui = pygame.sprite.Group()  # ui button group in battle

        self.ui_boxes = pygame.sprite.Group()

        self.skill_icons = pygame.sprite.Group()  # skill and trait icon objects

        self.slider_menu = pygame.sprite.Group()  # volume slider in esc option menu

        self.unit_icon = pygame.sprite.Group()  # Unit icon object group in selector ui
        self.weather_matters = pygame.sprite.Group()  # sprite of weather effect group such as rain sprite
        self.weather_effect = pygame.sprite.Group()  # sprite of special weather effect group such as fog that cover whole screen

        # Assign containers
        OptionMenuText.containers = self.menu_icon
        SliderMenu.containers = self.menu_slider, self.slider_menu
        TeamCoa.containers = self.team_coa, self.ui_updater, self.ui_drawer

        MenuRotate.containers = self.ui_updater, self.ui_drawer
        MenuActor.containers = self.ui_updater, self.ui_drawer

        SubsectionName.containers = self.ui_updater, self.ui_drawer, self.battle_ui_updater, self.battle_ui_drawer

        # battle containers
        SkillIcon.containers = self.skill_icons, self.battle_ui_updater, self.battle_ui_drawer
        HealthStaminaBar.containers = self.battle_ui_updater, self.battle_ui_drawer
        WeaponUI.containers = self.battle_ui_updater, self.battle_ui_drawer
        FollowerUI.containers = self.battle_ui_updater, self.battle_ui_drawer
        StatusUI.containers = self.battle_ui_updater, self.battle_ui_drawer
        UnitIcon.containers = self.unit_icon, self.ui_updater, self.ui_drawer
        SpriteIndicator.containers = self.effect_updater, self.battle_camera
        AimTarget.containers = self.shoot_lines, self.battle_camera
        BattleCursor.containers = self.battle_ui_updater, self.battle_cursor_drawer

        Effect.containers = self.effect_updater, self.battle_camera

        MenuCursor.containers = self.ui_updater, self.ui_drawer

        MatterSprite.containers = self.weather_matters, self.realtime_ui_updater
        SpecialWeatherEffect.containers = self.weather_effect, self.battle_ui_updater, self.battle_ui_drawer

        Troop.containers = self.unit_updater, self.all_units, self.battle_camera
        Leader.containers = self.unit_updater, self.all_units, self.battle_camera

        # Create game cursor, make sure it is the first object in ui to be created, so it is always update first
        cursor_images = load_images(self.module_dir, subfolder=("ui", "cursor_menu"))  # no need to scale cursor
        self.cursor = MenuCursor(cursor_images)
        Game.cursor = self.cursor

        self.game_intro(self.screen, self.clock, False)  # run intro

        # Load game localisation data

        self.localisation = Localisation()
        Game.localisation = self.localisation

        # Battle related data
        self.troop_data, self.leader_data, self.faction_data = make_faction_troop_leader_data(self.module_dir,
                                                                                              self.screen_scale)

        self.battle_map_data = BattleMapData()

        MapPreview.terrain_colour = self.battle_map_data.terrain_colour
        MapPreview.feature_colour = self.battle_map_data.feature_colour
        MapPreview.battle_map_colour = self.battle_map_data.battle_map_colour

        self.preset_map_folder = self.battle_map_data.preset_map_folder
        self.battle_map_list = self.battle_map_data.battle_map_list
        self.battle_map_folder = self.battle_map_data.battle_map_folder
        self.battle_campaign = self.battle_map_data.battle_campaign  # for reference to preset campaign
        self.preset_map_data = self.battle_map_data.preset_map_data

        Unit.troop_data = self.troop_data
        Unit.leader_data = self.leader_data
        Unit.troop_sprite_list = self.troop_data.troop_sprite_list
        Unit.leader_sprite_list = self.leader_data.leader_sprite_list
        Unit.status_list = self.troop_data.status_list
        Unit.all_formation_list = self.troop_data.default_formation_list
        Unit.effect_list = self.troop_data.effect_list

        Effect.effect_list = self.troop_data.effect_list

        self.troop_animation = TroopAnimationData([str(self.troop_data.race_list[key]["Name"]) for key in
                                                   self.troop_data.race_list], self.team_colour)
        self.unit_animation_data = self.troop_animation.unit_animation_data  # animation data pool
        self.body_sprite_pool = self.troop_animation.body_sprite_pool  # body sprite pool
        self.weapon_sprite_pool = self.troop_animation.weapon_sprite_pool  # weapon sprite pool
        self.armour_sprite_pool = self.troop_animation.armour_sprite_pool  # armour sprite pool
        self.weapon_joint_list = self.troop_animation.weapon_joint_list  # weapon joint data, for placing handle to hand
        self.colour_list = self.troop_animation.colour_list  # sprite colourising list

        self.effect_sprite_pool = self.troop_animation.effect_sprite_pool  # effect sprite pool
        self.effect_animation_pool = self.troop_animation.effect_animation_pool  # effect sprite animation pool

        WeaponUI.weapon_sprite_pool = self.weapon_sprite_pool

        # flip (covert for ingame angle)
        bullet_sprite_pool = {}
        for key, value in self.effect_sprite_pool.items():
            bullet_sprite_pool[key] = {}
            for key2, value2 in value.items():
                image = pygame.transform.flip(value2, False, True)
                bullet_sprite_pool[key][key2] = image
        bullet_weapon_sprite_pool = {}
        for key, value in self.weapon_sprite_pool.items():
            bullet_weapon_sprite_pool[key] = {}
            for key2, value2 in value.items():
                bullet_weapon_sprite_pool[key][key2] = {}
                for key3, value3 in value2.items():
                    if key3 == "Bullet":
                        bullet_weapon_sprite_pool[key][key2][key3] = {}
                        image = pygame.transform.flip(value3, False, True)
                        bullet_weapon_sprite_pool[key][key2][key3] = image

        Effect.bullet_sprite_pool = bullet_sprite_pool
        Effect.bullet_weapon_sprite_pool = bullet_weapon_sprite_pool
        Effect.effect_sprite_pool = self.effect_sprite_pool
        Effect.effect_animation_pool = self.effect_animation_pool

        # Load sound effect
        self.sound_effect_pool = self.create_sound_effect_pool()

        # Battle map object
        self.battle_base_map = BaseMap()  # create base terrain map
        self.battle_feature_map = FeatureMap(self.battle_base_map)  # create terrain feature map
        self.battle_height_map = HeightMap()  # create height map
        self.battle_map = FinalMap(self.battle_height_map)
        self.battle_camera.add(self.battle_map)

        Effect.height_map = self.battle_height_map
        Unit.base_map = self.battle_base_map  # add battle map to unit class
        Unit.feature_map = self.battle_feature_map
        Unit.height_map = self.battle_height_map

        # Music player
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer = None
        if pygame.mixer:
            pygame.mixer.set_num_channels(1000)
            pygame.mixer.music.set_volume(self.play_music_volume)
            self.SONG_END = pygame.USEREVENT + 1
            self.music_list = glob.glob(self.module_dir + "/sound/music/menu.ogg")
            pygame.mixer.music.load(self.music_list[0])
            pygame.mixer.music.play(-1)

        # Main menu interface

        self.fps_count = FPSCount(self)  # FPS number counter
        if self.show_fps:
            self.add_ui_updater(self.fps_count)

        base_button_image_list = load_base_button(self.module_dir, self.screen_scale)

        main_menu_buttons_box = BoxUI((400, 500), parent=self.screen)

        f = 0.68
        self.preset_map_button = BrownMenuButton((0, -1 * f), key_name="main_menu_preset_map",
                                                 parent=main_menu_buttons_box)
        self.custom_map_button = BrownMenuButton((0, -0.6 * f), key_name="main_menu_custom_map",
                                                 parent=main_menu_buttons_box)
        # self.game_edit_button = BrownMenuButton((0, -0.2 * f), key_name="main_menu_editor",
        #                                         parent=main_menu_buttons_box)
        self.lore_button = BrownMenuButton((0, -0.2 * f), key_name="main_menu_lorebook", parent=main_menu_buttons_box)
        self.option_button = BrownMenuButton((0, 0.2 * f), key_name="game_option", parent=main_menu_buttons_box)
        self.quit_button = BrownMenuButton((0, 0.6 * f), key_name="game_quit", parent=main_menu_buttons_box)

        main_menu_button_images = load_images(self.module_dir, screen_scale=self.screen_scale,
                                              subfolder=("ui", "mainmenu_ui"))

        self.discord_button = URLIconLink(main_menu_button_images["discord"], (self.screen_width, 0),
                                          "https://discord.gg/q7yxz4netf")
        self.youtube_button = URLIconLink(main_menu_button_images["youtube"], self.discord_button.rect.topleft,
                                          "https://www.youtube.com/channel/UCgapwWog3mYhkEKIGW8VZtw")
        self.github_button = URLIconLink(main_menu_button_images["github"], self.youtube_button.rect.topleft,
                                         "https://github.com/remance/Masendor")

        self.mainmenu_button = (self.preset_map_button, self.custom_map_button,
                                self.lore_button, self.option_button, self.quit_button, main_menu_buttons_box,
                                self.discord_button, self.youtube_button, self.github_button)  # self.game_edit_button,

        # Battle map select menu button

        self.preset_map_list_box = ListUI(pivot=(-0.9, -0.9), origin=(-1, -1), size=(.2, .8),
                                          items=CampaignListAdapter(),
                                          parent=self.screen, item_size=20)

        self.custom_battle_map_list_box = ListUI(pivot=(-0.9, -0.9), origin=(-1, -1), size=(.2, .8),
                                                 items=ListAdapter(self.battle_map_list,
                                                                   replace_on_select=custom_map_list_on_select),
                                                 parent=self.screen, item_size=20)

        self.custom_unit_list_box = ListUI(pivot=(-0.9, -0.8), origin=(-1, -1), size=(.2, .75),
                                           items=ListAdapter(["None"]),
                                           parent=self.screen, item_size=18)

        self.custom_unit_list_select = NameTextBox((self.custom_unit_list_box.image.get_width(),
                                                    60 * self.screen_scale[1]),
                                                   (self.custom_unit_list_box.rect.midtop[0],
                                                    self.custom_unit_list_box.rect.midtop[1] -
                                                    25 * self.screen_scale[1]), "Selected: Leader List",
                                                   text_size=30 * self.screen_scale[1],
                                                   box_colour=(240, 230, 175))

        self.custom_unit_list_select_box = ListUI(pivot=(-0.9, -0.8), origin=(-1, -1), size=(.2, .2),
                                                  items=ListAdapter(["Leader List", "Preset Unit List",
                                                                     "Preset Army List"],
                                                                    replace_on_select=custom_set_list_on_select),
                                                  parent=self.screen, item_size=3)

        self.custom_battle_faction_list_box = ListUI(pivot=(-0.03, -0.1), origin=(-1, -1), size=(.3, .4),
                                                     items=ListAdapter(["None"] + self.faction_data.faction_name_list,
                                                                       replace_on_select=custom_faction_list_on_select),
                                                     parent=self.screen, item_size=10)

        self.troop_list_box = ListUI(pivot=(-0.03, -0.1), origin=(-1, -1), size=(.3, .4),
                                     items=ListAdapter(["None"]), parent=self.screen, item_size=10)

        self.weather_list_box = ListUI(pivot=(0, -0.1), origin=(-1, -1), size=(.3, .4),
                                       items=ListAdapter(self.battle_map_data.weather_list,
                                                         replace_on_select=custom_weather_list_on_select),
                                       parent=self.screen, item_size=10, layer=20)

        battle_select_image = load_images(self.module_dir, screen_scale=self.screen_scale,
                                          subfolder=("ui", "mapselect_ui"))

        self.map_title = MapTitle((self.screen_rect.width / 2, 0))

        self.map_preview = MapPreview(self.preset_map_list_box.rect.topright)

        self.unit_selector = UnitSelector(self.map_preview.rect.topright,
                                          battle_select_image["unit_select"], icon_scale=0.4)

        self.team_coa_box = BackgroundBox(self.map_preview.rect.bottomright,
                                          battle_select_image["team_coa_box"])

        UIScroll(self.unit_selector, self.unit_selector.rect.topright)  # scroll bar for unit pick

        self.unit_model_room = LeaderModel(self.unit_selector.rect.bottomright,
                                           battle_select_image["small_box"])  # troop stat

        bottom_height = self.screen_rect.height - base_button_image_list[0].get_height()
        self.select_button = MenuButton(base_button_image_list,
                                        (self.screen_rect.width - base_button_image_list[0].get_width(), bottom_height),
                                        key_name="select_button")
        self.start_button = MenuButton(base_button_image_list,
                                       (self.screen_rect.width - base_button_image_list[0].get_width(), bottom_height),
                                       key_name="start_button")
        self.map_back_button = MenuButton(base_button_image_list,
                                          (
                                              self.screen_rect.width - (self.screen_rect.width - base_button_image_list[
                                                  0].get_width()),
                                              bottom_height), key_name="back_button")

        self.map_select_button = (self.select_button, self.map_back_button)
        self.team_select_button = (self.select_button, self.map_back_button)
        self.unit_select_button = (self.start_button, self.map_back_button)

        self.team_stat_box = BackgroundBox(self.unit_model_room.rect.bottomright,
                                           battle_select_image["small_box"])  # ui box to display team troop number

        self.custom_map_option_box = BackgroundBox(self.unit_model_room.rect.bottomright,
                                                   battle_select_image["small_box"])  # ui box for battle option

        self.org_chart = OrgChart(load_image(self.module_dir, self.screen_scale, "org.png", ("ui", "mapselect_ui")),
                                  self.unit_selector.rect.bottomleft)

        self.camp_icon = []

        self.night_battle_tick_box = TickBox((self.custom_map_option_box.rect.topleft[0] * 1.05,
                                              self.custom_map_option_box.rect.topleft[1] * 1.05),
                                             battle_select_image["untick"], battle_select_image["tick"],
                                             "night")
        self.weather_custom_select = NameTextBox((self.custom_map_option_box.image.get_width() -
                                                  (10 * self.screen_scale[0]), 30 * self.screen_scale[1]),
                                                 (self.custom_map_option_box.rect.center[0],
                                                  self.custom_map_option_box.rect.center[1] +
                                                  self.custom_map_option_box.image.get_height() / 3.5),
                                                 "Weather: Light Random")
        self.wind_custom_select = NameTextBox((self.custom_map_option_box.image.get_width() -
                                               (10 * self.screen_scale[0]), 30 * self.screen_scale[1]),
                                              (self.custom_map_option_box.rect.center[0],
                                               self.custom_map_option_box.rect.center[1] +
                                               self.custom_map_option_box.image.get_height() / 10),
                                              "Wind Direction: 0")

        self.current_map_row = 0
        self.current_map_select = 0
        self.current_source_row = 0
        self.unit_select_row = 0

        self.source_name_list = [""]
        self.source_scale_text = [""]
        self.source_scale = [""]
        self.source_text = [""]

        # Unit and troop editor button in game start menu
        self.unit_edit_button = MenuButton(base_button_image_list, (self.screen_rect.width / 2,
                                                                    self.screen_rect.height - (base_button_image_list[
                                                                                                   0].get_height() * 4)),
                                           key_name="main_menu_unit_editor")
        self.troop_create_button = MenuButton(base_button_image_list, (self.screen_rect.width / 2,
                                                                       self.screen_rect.height - (
                                                                               base_button_image_list[
                                                                                   0].get_height() * 2.5)),
                                              key_name="main_menu_troop_editor")
        self.editor_back_button = MenuButton(base_button_image_list, (self.screen_rect.width / 2,
                                                                      self.screen_rect.height - base_button_image_list[
                                                                          0].get_height()),
                                             key_name="back_button")
        self.editor_button = (self.unit_edit_button, self.troop_create_button, self.editor_back_button)

        # Option menu button
        option_menu_dict = make_option_menu(self.profile_name, base_button_image_list, self.config["USER"],
                                            self.player1_key_bind, battle_select_image)
        self.profile_box = option_menu_dict["profile_box"]
        self.back_button = option_menu_dict["back_button"]
        self.keybind_button = option_menu_dict["keybind_button"]
        self.default_button = option_menu_dict["default_button"]
        self.resolution_drop = option_menu_dict["resolution_drop"]
        self.resolution_bar = option_menu_dict["resolution_bar"]
        self.resolution_text = option_menu_dict["resolution_text"]
        self.art_style_drop = option_menu_dict["art_style_drop"]
        self.art_style_bar = option_menu_dict["art_style_bar"]
        self.art_style_text = option_menu_dict["art_style_text"]
        self.option_menu_sliders = option_menu_dict["volume_sliders"]
        self.value_boxes = option_menu_dict["value_boxes"]
        self.volume_texts = option_menu_dict["volume_texts"]
        self.fullscreen_box = option_menu_dict["fullscreen_box"]
        self.fullscreen_text = option_menu_dict["fullscreen_text"]
        self.fps_box = option_menu_dict["fps_box"]
        self.fps_text = option_menu_dict["fps_text"]
        self.keybind_text = option_menu_dict["keybind_text"]
        self.keybind_icon = option_menu_dict["keybind_icon"]
        self.control_switch = option_menu_dict["control_switch"]

        self.option_text_list = tuple(
            [self.resolution_text, self.art_style_text, self.fullscreen_text, self.fps_text] +
            [value for value in self.volume_texts.values()])
        self.option_menu_button = (
            self.back_button, self.default_button, self.keybind_button, self.resolution_drop, self.art_style_drop,
            self.fullscreen_box, self.fps_box)

        # User input popup ui
        input_ui_dict = make_input_box(self.module_dir, self.screen_scale, self.screen_rect,
                                       load_base_button(self.module_dir, self.screen_scale))
        self.input_ui = input_ui_dict["input_ui"]
        self.input_ok_button = input_ui_dict["input_ok_button"]
        self.input_close_button = input_ui_dict["input_close_button"]
        self.input_cancel_button = input_ui_dict["input_cancel_button"]
        self.input_box = input_ui_dict["input_box"]
        self.input_ui_popup = (self.input_ok_button, self.input_cancel_button, self.input_ui, self.input_box)
        self.confirm_ui_popup = (self.input_ok_button, self.input_cancel_button, self.input_ui)
        self.inform_ui_popup = (self.input_close_button, self.input_ui, self.input_box)
        self.all_input_ui_popup = (self.input_ok_button, self.input_cancel_button, self.input_close_button,
                                   self.input_ui, self.input_box)

        editor_dict = make_editor_ui(self.module_dir, self.screen_scale, self.screen_rect,
                                     load_image(self.module_dir, self.screen_scale, "name_list.png",
                                                ("ui", "mapselect_ui")),
                                     load_base_button(self.module_dir, self.screen_scale), self.ui_updater)
        self.unit_preset_list_box = editor_dict["unit_listbox"]
        self.editor_troop_list_box = editor_dict["troop_listbox"]
        self.unit_delete_button = editor_dict["unit_delete_button"]
        self.unit_save_button = editor_dict["unit_save_button"]

        self.unit_editor_ui = (self.unit_preset_list_box, self.editor_troop_list_box,
                               self.unit_delete_button, self.unit_save_button)

        self.skill_images = make_icon_data(self.module_dir, self.screen_scale)

        # Text popup
        self.text_popup = TextPopup()  # popup box that show text when mouse over something

        # Encyclopedia interface
        Lorebook.concept_stat = csv_read(self.module_dir, "concept_stat.csv", ("lore",), header_key=True)
        Lorebook.concept_lore = self.localisation.create_lore_data("concept")
        Lorebook.history_stat = csv_read(self.module_dir, "history_stat.csv", ("lore",), header_key=True)
        Lorebook.history_lore = self.localisation.create_lore_data("history")

        Lorebook.faction_data = self.faction_data
        Lorebook.troop_data = self.troop_data
        Lorebook.leader_data = self.leader_data
        Lorebook.battle_map_data = self.battle_map_data

        self.encyclopedia, self.lore_name_list, self.filter_tag_list, self.lore_buttons = make_lorebook(self)

        self.encyclopedia_stuff = (self.encyclopedia, self.lore_name_list, self.filter_tag_list,
                                   self.lore_name_list.scroll, self.filter_tag_list.scroll, self.lore_buttons.values())

        self.battle = Battle(self)
        self.player1_battle_cursor = self.battle.player1_battle_cursor

        Game.battle = self.battle
        Unit.battle = self.battle
        Effect.battle = self.battle

        unit_to_make = tuple(set([this_unit for this_unit in self.troop_data.troop_list] +
                                 [this_unit for this_unit in self.leader_data.leader_list]))
        who_todo = {key: value for key, value in self.troop_data.troop_list.items() if key in unit_to_make}
        who_todo |= {key: value for key, value in self.leader_data.leader_list.items() if key in unit_to_make}

        # self.create_troop_sprite_pool(who_todo)

        # Background image
        self.background_image = load_images(self.module_dir, screen_scale=self.screen_scale,
                                            subfolder=("ui", "mainmenu_ui", "background"))
        self.atlas = MenuRotate((self.screen_width / 2, self.screen_height / 2), self.background_image["atlas"], 5)
        self.hide_background = StaticImage((self.screen_width / 2, self.screen_height / 2),
                                           self.background_image["hide"])
        self.menu_actor_data = csv_read(self.module_dir, "menu_actor.csv", ("ui",), header_key=True)
        self.menu_actors = []
        for stuff in self.menu_actor_data.values():
            if stuff["Type"] == "unit":
                if "-" in stuff["ID"]:
                    who_todo = {key: value for key, value in self.leader_data.leader_list.items() if key == stuff["ID"]}
                else:
                    who_todo = {key: value for key, value in self.troop_data.troop_list.items() if key == stuff["ID"]}
                sprite_direction = rotation_dict[min(rotation_list, key=lambda x: abs(
                    x - stuff["Angle"]))]  # find closest in list of rotation for sprite direction
                preview_sprite_pool, _ = self.create_troop_sprite_pool(who_todo, preview=True,
                                                                       specific_preview=(stuff["Animation"],
                                                                                         None,
                                                                                         sprite_direction),
                                                                       max_preview_size=stuff["Size"])

                self.menu_actors.append(MenuActor((float(stuff["POS"].split(",")[0]) * self.screen_width,
                                                   float(stuff["POS"].split(",")[1]) * self.screen_height),
                                                  preview_sprite_pool[stuff["ID"]]))

        # self.background = self.background_image["main"]

        # Starting script
        self.add_ui_updater(self.mainmenu_button)

        self.menu_state = "main_menu"
        self.input_popup = None  # popup for text input state
        self.choosing_faction = True  # swap list between faction and unit, always start with choose faction first as true

        self.loading_screen("end")

        self.run()

    def game_intro(self, screen, clock, intro):
        timer = 0
        # The record is truthful, unbiased, correct and approved by appointed certified historians.
        # quote = ["Those attacker fail to learn from the mistakes of their predecessors are destined to repeat them. George Santayana",
        # "It is more important to out-think your enemy, than to out-fight him, Sun Tzu"]
        while intro:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    intro = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            large_text = pygame.font.Font("freesansbold.ttf", 115)
            text_surf, text_rect = text_objects("Test Intro", large_text)
            text_rect.center = (700, 600)
            screen.blit(text_surf, text_rect)
            pygame.display.update()
            clock.tick(60)
            timer += 1
            if timer == 1000:
                intro = False

        self.loading_screen("start")

        pygame.display.set_caption(version_name)  # set the self name on program border/tab

    def add_ui_updater(self, *args):
        self.ui_updater.add(*args)
        self.ui_drawer.add(*args)

    def remove_ui_updater(self, *args):
        self.ui_updater.remove(*args)
        self.ui_drawer.remove(*args)

    def setup_profiler(self):
        self.profiler = Profiler()
        self.profiler.enable()
        self.battle.add_ui_updater(self.profiler)

    def run(self):
        while True:
            # Get user input
            self.dt = self.clock.get_time() / 1000  # dt before game_speed
            self.cursor.scroll_down = False
            self.cursor.scroll_up = False
            esc_press = False
            key_press = pygame.key.get_pressed()

            if self.url_delay:
                self.url_delay -= self.dt
                if self.url_delay < 0:
                    self.url_delay = 0

            if self.config["USER"]["control player 1"] == "joystick" and self.input_popup[0] == "keybind_input":
                for joystick in self.joysticks.values():  # TODO change this when has multiplayer
                    for i in range(joystick.get_numaxes()):
                        if joystick.get_axis(i):
                            if i not in (2, 3):  # prevent right axis from being assigned
                                axis_name = "axis" + number_to_minus_or_plus(joystick.get_axis(i)) + str(i)
                                self.assign_key(axis_name)

                    for i in range(joystick.get_numhats()):
                        if joystick.get_hat(i)[0]:
                            hat_name = "hat" + number_to_minus_or_plus(joystick.get_axis(i)) + str(0)
                            self.assign_key(hat_name)
                        elif joystick.get_hat(i)[1]:
                            hat_name = "hat" + number_to_minus_or_plus(joystick.get_axis(i)) + str(1)
                            self.assign_key(hat_name)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 4:  # Mouse scroll down
                        self.cursor.scroll_up = True
                    elif event.button == 5:  # Mouse scroll up
                        self.cursor.scroll_down = True

                    if self.input_popup and self.input_popup[0] == "keybind_input":
                        if self.config["USER"]["control player 1"] == "keyboard" and not \
                                self.input_close_button.event_press:  # check for keyboard mouse key
                            self.assign_key(tuple(self.mouse_bind.keys())[tuple(
                                self.mouse_bind.values()).index(event.button)])

                elif event.type == pygame.JOYBUTTONUP:
                    joystick = event.instance_id
                    if self.config["USER"]["control player 1"] == "joystick" and self.input_popup[0] == "keybind_input":
                        # check for button press
                        self.assign_key(event.button)

                elif event.type == pygame.KEYDOWN:
                    if self.input_popup:  # event update to input box
                        if event.key == pygame.K_ESCAPE:
                            esc_press = True

                        elif self.input_popup[0] == "keybind_input" and \
                                self.config["USER"]["control player 1"] == "keyboard":
                            self.assign_key(event.key)

                        elif self.input_popup[0] == "text_input":
                            self.input_box.player_input(event, key_press)
                            self.text_delay = 0.1
                    else:
                        if event.key == pygame.K_ESCAPE:
                            esc_press = True

                elif event.type == pygame.JOYDEVICEADDED:
                    # Player add new joystick by plug in
                    joy = pygame.joystick.Joystick(event.device_index)
                    self.joysticks[joy.get_instance_id()] = joy
                    joy_name = joy.get_name()
                    for name in self.joystick_bind_name:
                        if name in joy_name:  # find common name
                            self.joystick_name[joy.get_instance_id()] = name
                    if joy.get_instance_id() not in self.joystick_name:
                        self.joystick_name[joy.get_instance_id()] = "Other"

                elif event.type == pygame.JOYDEVICEREMOVED:
                    # Player unplug joystick
                    del self.joysticks[event.instance_id]
                    del self.joystick_name[event.instance_id]

                elif event.type == QUIT:
                    esc_press = True

            self.remove_ui_updater(self.text_popup)
            self.ui_updater.update()

            # Reset screen
            self.screen.fill((220, 220, 180))
            # self.screen.blit(self.background, (0, 0))  # blit background over instead of clear() to reset screen

            if self.input_popup:  # currently, have input text pop up on screen, stop everything else until done
                if self.input_ok_button.event_press or key_press[pygame.K_RETURN] or key_press[pygame.K_KP_ENTER]:
                    done = True
                    if self.input_popup[1] == "profile_name":
                        self.profile_name = self.input_box.text
                        self.profile_box.change_text(self.profile_name)

                        edit_config("USER", "player_name", self.profile_name, "configuration.ini", self.config)

                    elif "custom_camp_size" in self.input_popup[1] and self.input_box.text.isdigit():
                        pos = self.input_popup[1].split("/")[1]
                        pos = pos.replace("(", "").replace(")", "").split(", ")
                        pos = [float(item) for item in pos]
                        self.play_map_data["camp_pos"][int(self.input_popup[1][-1])].insert(0, [pos,
                                                                                                int(self.input_box.text)])
                        self.camp_icon.insert(0, TempUnitIcon(int(self.input_popup[1][-1]),
                                                              self.input_box.text, self.input_box.text, 0))
                        self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)
                        self.map_preview.change_mode(1, camp_pos_list=self.play_map_data["camp_pos"])

                    elif "custom_active_troop_number" in self.input_popup[1] and self.input_box.text.isdigit():
                        for this_unit in self.unit_icon:
                            if this_unit.selected and this_unit.who.index is not None:
                                input_text = int(self.input_box.text)
                                if input_text:
                                    self.play_source_data["unit"][this_unit.who.index]["Troop"][self.input_popup[2]] = \
                                        [input_text, 0]
                                    self.activate_input_popup(("text_input", "custom_reserve_troop_number",
                                                               self.input_popup[2]), "Reserve troop number:",
                                                              self.input_ui_popup)
                                    done = False
                                else:
                                    if self.input_popup[2] in self.play_source_data["unit"][this_unit.who.index]["Troop"]:
                                        self.play_source_data["unit"][this_unit.who.index]["Troop"].pop(self.input_popup[2])
                                break

                    elif "custom_reserve_troop_number" in self.input_popup[1] and self.input_box.text.isdigit():
                        for this_unit in self.unit_icon:
                            if this_unit.selected:
                                self.play_source_data["unit"][this_unit.who.index]["Troop"][self.input_popup[2]][1] = \
                                    self.input_box.text
                                break

                    elif "replace key" in self.input_popup[1]:
                        old_key = self.player1_key_bind[self.config["USER"]["control player 1"]][self.input_popup[1][1]]
                        self.player1_key_bind[self.config["USER"]["control player 1"]][
                            self.input_popup[1][1]] = self.player1_key_bind[self.config["USER"]["control player 1"]][
                            self.input_popup[1][2]]
                        self.player1_key_bind[self.config["USER"]["control player 1"]][self.input_popup[1][2]] = old_key
                        edit_config("USER", "keybind player 1", self.player1_key_bind,
                                    "configuration.ini", self.config)
                        for key, value in self.keybind_icon.items():
                            if key == self.input_popup[1][1]:
                                if self.joysticks:
                                    value.change_key(self.config["USER"]["control player 1"],
                                                     self.player1_key_bind[self.config["USER"]["control player 1"]][
                                                         self.input_popup[1][1]],
                                                     self.joystick_bind_name[
                                                         self.joystick_name[tuple(self.joystick_name.keys())[0]]])
                                else:
                                    value.change_key(self.config["USER"]["control player 1"],
                                                     self.player1_key_bind[self.config["USER"]["control player 1"]][
                                                         self.input_popup[1][1]], None)

                            elif key == self.input_popup[1][2]:
                                if self.joysticks:
                                    value.change_key(self.config["USER"]["control player 1"],
                                                     self.player1_key_bind[self.config["USER"]["control player 1"]][
                                                         self.input_popup[1][2]],
                                                     self.joystick_bind_name[
                                                         self.joystick_name[tuple(self.joystick_name.keys())[0]]])
                                else:
                                    value.change_key(self.config["USER"]["control player 1"],
                                                     self.player1_key_bind[self.config["USER"]["control player 1"]][
                                                         self.input_popup[1][2]], None)

                    elif "wind" in self.input_popup[1] and self.input_box.text.isdigit():
                        self.play_source_data["weather"][0][2] = int(self.input_box.text)
                        self.wind_custom_select.rename("Wind Direction: " + self.input_box.text)

                    elif self.input_popup[1] == "quit":
                        pygame.time.wait(1000)
                        if pygame.mixer:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.unload()
                        pygame.quit()
                        sys.exit()

                    if done:
                        self.change_pause_update(False)
                        self.input_box.text_start("")
                        self.input_popup = None
                        self.remove_ui_updater(self.all_input_ui_popup)

                elif self.input_cancel_button.event_press or self.input_close_button.event_press or esc_press:
                    self.change_pause_update(False)
                    self.input_box.text_start("")
                    self.input_popup = None
                    self.remove_ui_updater(self.all_input_ui_popup)

                elif self.input_popup[0] == "text_input":
                    if self.text_delay == 0:
                        if key_press[self.input_box.hold_key]:
                            self.input_box.player_input(None, key_press)
                            self.text_delay = 0.1
                    else:
                        self.text_delay += self.dt
                        if self.text_delay >= 0.3:
                            self.text_delay = 0

            elif not self.input_popup:
                if self.menu_state == "main_menu":
                    self.menu_main(esc_press)

                elif self.menu_state == "preset_map":
                    self.menu_preset_map_select(esc_press)

                elif self.menu_state == "custom_map":
                    self.menu_custom_map_select(esc_press)

                elif self.menu_state == "custom_unit_setup":
                    self.menu_custom_unit_setup(esc_press)

                elif self.menu_state == "custom_leader_setup":
                    self.menu_custom_leader_setup(esc_press)

                elif self.menu_state == "game_creator":
                    self.menu_game_editor(esc_press)

                elif self.menu_state == "option":
                    self.menu_option(esc_press)

                elif self.menu_state == "keybind":
                    self.menu_keybind(esc_press)

                elif self.menu_state == "encyclopedia":
                    command = self.lorebook_process(esc_press)
                    if esc_press or command == "exit":
                        self.menu_state = "main_menu"  # change menu back to default 0

            self.ui_drawer.draw(self.screen)
            pygame.display.update()
            self.clock.tick(60)
