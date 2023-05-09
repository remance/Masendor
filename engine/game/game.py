import ast
import configparser
import glob
import os.path
import sys

import pygame
from pygame.locals import *

from engine import utility

from engine.battlemap import battlemap
from engine.weather import weather
from engine.uibattle import uibattle
from engine.uimenu import uimenu
from engine.battle import battle
from engine.unit import unit
from engine.effect import effect
from engine.data import datasprite, datamap, datalocalisation
from engine.lorebook import lorebook
from engine.drama import drama
from engine.battle import setup_battle_unit

direction_list = datasprite.direction_list

load_image = utility.load_image
load_images = utility.load_images
csv_read = utility.csv_read
load_sound = utility.load_sound
edit_config = utility.edit_config
make_bar_list = utility.make_bar_list
load_base_button = utility.load_base_button
text_objects = utility.text_objects
setup_list = utility.setup_list
list_scroll = utility.list_scroll
number_to_minus_or_plus = utility.number_to_minus_or_plus
empty_function = utility.empty_function

# Module that get loads with import in game.setup after

from engine.game.setup import make_battle_ui

make_battle_ui = make_battle_ui.make_battle_ui

from engine.game.setup import make_editor_ui
make_editor_ui = make_editor_ui.make_editor_ui

from engine.game.setup import make_esc_menu
make_esc_menu = make_esc_menu.make_esc_menu

from engine.game.setup import make_faction_troop_leader_data
make_faction_troop_leader_data = make_faction_troop_leader_data.make_faction_troop_leader_data

from engine.game.setup import make_icon_data
make_icon_data = make_icon_data.make_icon_data

from engine.game.setup import make_input_box
make_input_box = make_input_box.make_input_box

from engine.game.setup import make_lorebook
make_lorebook = make_lorebook.make_lorebook

from engine.game.setup import make_option_menu
make_option_menu = make_option_menu.make_option_menu

version_name = "Future Visionary"  # Game version name that will appear as game name


class Game:
    game = None
    main_dir = None
    data_dir = None
    font_dir = None
    module_dir = None
    ui_font = None
    language = None
    localisation = None

    screen_scale = (1, 1)
    screen_size = ()

    game_version = "0.7.1.6"
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

    from engine.game import assign_key
    assign_key = assign_key.assign_key

    from engine.game import back_mainmenu
    back_mainmenu = back_mainmenu.back_mainmenu

    from engine.game import change_battle_source
    change_battle_source = change_battle_source.change_battle_source

    from engine.game import change_sound_volume
    change_sound_volume = change_sound_volume.change_sound_volume

    from engine.game import create_config
    create_config = create_config.create_config

    from engine.game import create_preview_map
    create_preview_map = create_preview_map.create_preview_map

    from engine.game import create_sound_effect_pool
    create_sound_effect_pool = create_sound_effect_pool.create_sound_effect_pool

    from engine.game import create_team_coa
    create_team_coa = create_team_coa.create_team_coa

    from engine.game import create_troop_sprite
    create_troop_sprite = create_troop_sprite.create_troop_sprite

    from engine.game import create_troop_sprite_pool
    create_troop_sprite_pool = create_troop_sprite_pool.create_troop_sprite_pool

    from engine.game import loading_screen
    loading_screen = loading_screen.loading_screen

    from engine.game import menu_custom_unit_select
    menu_custom_unit_select = menu_custom_unit_select.menu_custom_unit_select

    from engine.game import menu_custom_team_select
    menu_custom_team_select = menu_custom_team_select.menu_custom_team_select

    from engine.game import menu_game_editor
    menu_game_editor = menu_game_editor.menu_game_editor

    from engine.game import menu_keybind
    menu_keybind = menu_keybind.menu_keybind

    from engine.game import menu_main
    menu_main = menu_main.menu_main

    from engine.game import menu_custom_map_select
    menu_custom_map_select = menu_custom_map_select.menu_custom_map_select

    from engine.game import menu_option
    menu_option = menu_option.menu_option

    from engine.game import menu_preset_map_select
    menu_preset_map_select = menu_preset_map_select.menu_preset_map_select

    from engine.game import menu_custom_leader_setup
    menu_custom_leader_setup = menu_custom_leader_setup.menu_custom_leader_setup

    from engine.game import menu_custom_unit_setup
    menu_custom_unit_setup = menu_custom_unit_setup.menu_custom_unit_setup

    from engine.game import read_selected_map_data
    read_selected_map_data = read_selected_map_data.read_selected_map_data

    from engine.game import start_battle
    start_battle = start_battle.start_battle

    popup_list_open = utility.popup_list_open
    lorebook_process = lorebook.lorebook_process
    setup_battle_unit = setup_battle_unit.setup_battle_unit

    troop_sprite_size = (200, 200)

    team_colour = {0: (50, 50, 50), 1: (50, 50, 150), 2: (200, 50, 50), 3: (200, 200, 0), 4: (0, 200, 0),
                   5: (200, 0, 200), 6: (140, 90, 40), 7: (100, 170, 170), 8: (230, 120, 0), 9: (230, 60, 110),
                   10: (130, 120, 200)}
    selected_team_colour = {0: (200, 200, 200), 1: (180, 180, 255), 2: (255, 150, 150), 3: (255, 255, 150),
                            4: (150, 255, 150), 5: (255, 150, 255), 6: (200, 140, 70), 7: (160, 200, 200),
                            8: (255, 150, 45), 9: (230, 140, 160), 10: (200, 190, 230)}

    leader_skill_level_text = ("E", "E+", "D", "D+", "C", "C+", "B", "B+", "A", "A+", "S")

    def __init__(self, main_dir, error_log):

        Game.game = self
        Game.main_dir = main_dir
        Game.data_dir = os.path.join(self.main_dir, "data")
        Game.font_dir = os.path.join(self.data_dir, "font")

        pygame.init()  # Initialize pygame

        pygame.mouse.set_visible(False)  # set mouse as not visible, use in-game mouse sprite

        self.error_log = error_log
        self.error_log.write("Game Version: " + self.game_version)

        # Read config file
        config = configparser.ConfigParser()  # initiate config reader
        try:
            config.read_file(open(os.path.join(self.main_dir, "configuration.ini")))  # read config file
        except FileNotFoundError:  # Create config file if not found with the default
            config = self.create_config()

        try:
            self.config = config
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
            self.module = int(self.config["USER"]["module"])
            if self.game_version != self.config["VERSION"]["ver"]:  # remake config as game version change
                reset_config  # cause NameError to reset config file
        except (KeyError, TypeError, NameError):  # config error will make the game recreate config with default
            config = self.create_config()
            self.config = config
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
            self.module = int(self.config["USER"]["module"])

        Game.language = self.language

        self.module_list = csv_read(self.data_dir, "module_list.csv", ("module",))  # get module list
        self.module_folder = str(self.module_list[self.module][0]).strip("/").lower()
        self.error_log.write("Use module: " + self.module_folder)  # error log selected module

        Game.module_dir = os.path.join(self.data_dir, "module", self.module_folder)
        Game.ui_font = csv_read(self.module_dir, "ui_font.csv", ("ui",), header_key=True)
        for item in Game.ui_font:  # add ttf file extension for font data reading.
            Game.ui_font[item] = os.path.join(self.font_dir, Game.ui_font[item]["Font"] + ".ttf")
        # Set the display mode
        self.screen_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
        self.screen_scale = (self.screen_rect.width / 1920, self.screen_rect.height / 1080)
        Game.screen_size = self.screen_rect.size
        Game.screen_scale = self.screen_scale

        self.window_style = 0
        if self.full_screen == 1:
            self.window_style = pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(self.screen_rect.size, self.window_style)

        unit.Unit.screen_scale = self.screen_scale
        unit.Unit.team_colour = self.team_colour
        uimenu.MapPreview.colour = self.team_colour
        uimenu.MapPreview.selected_colour = self.selected_team_colour
        uibattle.MiniMap.colour = self.team_colour
        uibattle.MiniMap.selected_colour = self.selected_team_colour
        uibattle.UnitIcon.colour = self.team_colour
        effect.Effect.screen_scale = self.screen_scale
        battlemap.BeautifulMap.team_colour = self.team_colour
        battlemap.BeautifulMap.selected_team_colour = self.selected_team_colour

        self.clock = pygame.time.Clock()  # set get clock

        self.loading = load_image(self.module_dir, self.screen_scale, "loading.png", ("ui", "mainmenu_ui"))
        self.loading = pygame.transform.scale(self.loading, self.screen_rect.size)

        self.joysticks = {}
        self.joystick_name = {}

        self.map_type = ""
        self.map_source = 0  # current selected map source
        self.team_selected = 1
        self.unit_selected = 0
        self.current_popup_row = 0
        self.team_pos = {}  # for saving preview map unit pos
        self.camp_pos = {}  # for saving preview map camp pos
        self.map_data = None
        self.map_info = None
        self.map_unit_data = None

        self.dt = 0
        self.text_delay = 0

        # Decorate game icon window
        # icon = load_image(self.data_dir, "sword.jpg")
        # icon = pygame.transform.scale(icon, (32, 32))
        # pygame.display.set_icon(icon)

        # Initialise groups

        self.main_ui_updater = pygame.sprite.LayeredUpdates()  # main drawer for ui in main menu

        # game start menu group
        self.menu_button = pygame.sprite.Group()  # group of menu buttons that are currently get shown and update
        self.menu_icon = pygame.sprite.Group()  # mostly for option icon like volume or screen resolution
        self.menu_slider = pygame.sprite.Group()

        # encyclopedia group
        self.lore_button_ui = pygame.sprite.Group()  # buttons for encyclopedia group
        self.subsection_name = pygame.sprite.Group()  # subsection name objects group in encyclopedia blit on lore_name_list
        self.tag_filter_name = pygame.sprite.Group()  # tag filter objects group in encyclopedia blit on filter_name_list

        # battle select menu group
        self.map_namegroup = pygame.sprite.Group()  # map name list group
        self.popup_namegroup = pygame.sprite.Group()
        self.team_coa = pygame.sprite.Group()  # team coat of arm that also act as team selection icon
        self.source_namegroup = pygame.sprite.Group()  # source name list group

        # battle object group
        self.battle_camera = pygame.sprite.LayeredUpdates()  # layer drawer self camera, all image pos should be based on the map not screen
        self.battle_ui_updater = pygame.sprite.LayeredUpdates()  # this is layer drawer for ui, all image pos should be based on the screen
        self.hitbox_layer = pygame.sprite.LayeredUpdates()

        self.unit_updater = pygame.sprite.Group()  # updater for unit objects
        self.ui_updater = pygame.sprite.Group()  # updater for ui objects
        self.weather_updater = pygame.sprite.Group()  # updater for weather objects
        self.effect_updater = pygame.sprite.Group()  # updater for effect objects (e.g. range melee_attack sprite)

        self.all_units = pygame.sprite.Group()  # group to keep all unit object for cleaning

        self.preview_unit = pygame.sprite.Group()  # group for unit list in unit select screen

        self.sprite_indicator = pygame.sprite.Group()

        self.shoot_lines = pygame.sprite.Group()
        self.button_ui = pygame.sprite.Group()  # ui button group in battle

        self.skill_icon = pygame.sprite.Group()  # skill and trait icon objects
        self.effect_icon = pygame.sprite.Group()  # status effect icon objects

        self.battle_menu_button = pygame.sprite.Group()  # buttons for esc menu object group
        self.esc_option_menu_button = pygame.sprite.Group()  # buttons for esc menu option object group
        self.slider_menu = pygame.sprite.Group()  # volume slider in esc option menu

        self.unit_icon = pygame.sprite.Group()  # Unit icon object group in selector ui
        self.weather_matter = pygame.sprite.Group()  # sprite of weather effect group such as rain sprite
        self.weather_effect = pygame.sprite.Group()  # sprite of special weather effect group such as fog that cover whole screen

        # Assign containers
        uimenu.MenuButton.containers = self.menu_button
        uimenu.OptionMenuText.containers = self.menu_icon
        uimenu.SliderMenu.containers = self.menu_slider, self.slider_menu

        uimenu.TeamCoa.containers = self.team_coa

        lorebook.SubsectionName.containers = self.main_ui_updater, self.battle_ui_updater

        # battle containers
        uibattle.SkillCardIcon.containers = self.skill_icon, self.battle_ui_updater
        uibattle.UnitIcon.containers = self.unit_icon, self.main_ui_updater
        uibattle.SpriteIndicator.containers = self.effect_updater, self.battle_camera
        uibattle.AimTarget.containers = self.shoot_lines, self.battle_camera

        effect.Effect.containers = self.effect_updater, self.battle_camera

        uimenu.EscButton.containers = self.battle_menu_button, self.esc_option_menu_button

        weather.MatterSprite.containers = self.weather_matter, self.battle_ui_updater, self.weather_updater
        weather.SpecialEffect.containers = self.weather_effect, self.battle_ui_updater, self.weather_updater

        unit.Troop.containers = self.unit_updater, self.all_units, self.battle_camera
        unit.Leader.containers = self.unit_updater, self.all_units, self.battle_camera

        # Create game cursor
        cursor_images = load_images(self.module_dir, subfolder=("ui", "cursor"))  # no need to scale cursor
        self.cursor = uimenu.Cursor(cursor_images)
        self.main_ui_updater.add(self.cursor)
        self.battle_ui_updater.add(self.cursor)

        self.game_intro(self.screen, self.clock, False)  # run intro

        # Load game localisation data

        self.localisation = datalocalisation.Localisation()
        Game.localisation = self.localisation

        # Battle related data
        self.troop_data, self.leader_data, self.faction_data = make_faction_troop_leader_data(self.data_dir,
                                                                                              self.module_dir,
                                                                                              self.screen_scale,
                                                                                              self.language)

        self.battle_map_data = datamap.BattleMapData(self.module_dir, self.screen_scale, self.language)

        battlemap.BaseMap.terrain_list = self.battle_map_data.terrain_list
        battlemap.BaseMap.terrain_colour = self.battle_map_data.terrain_colour
        battlemap.FeatureMap.feature_list = self.battle_map_data.feature_list
        battlemap.FeatureMap.feature_colour = self.battle_map_data.feature_colour
        battlemap.FeatureMap.feature_mod = self.battle_map_data.feature_mod

        battlemap.BeautifulMap.battle_map_colour = self.battle_map_data.battle_map_colour
        battlemap.BeautifulMap.texture_images = self.battle_map_data.map_texture
        battlemap.BeautifulMap.load_texture_list = self.battle_map_data.texture_folder
        battlemap.BeautifulMap.empty_texture = self.battle_map_data.empty_image
        battlemap.BeautifulMap.camp_texture = self.battle_map_data.camp_image

        uimenu.MapPreview.terrain_colour = self.battle_map_data.terrain_colour
        uimenu.MapPreview.feature_colour = self.battle_map_data.feature_colour
        uimenu.MapPreview.battle_map_colour = self.battle_map_data.battle_map_colour

        battle.Battle.battle_map_data = self.battle_map_data
        battle.Battle.weather_data = self.battle_map_data.weather_data
        battle.Battle.weather_matter_images = self.battle_map_data.weather_matter_images
        battle.Battle.weather_effect_images = self.battle_map_data.weather_effect_images
        battle.Battle.day_effect_images = self.battle_map_data.day_effect_images
        battle.Battle.weather_list = self.battle_map_data.weather_list
        battle.Battle.feature_mod = self.battle_map_data.feature_mod
        self.preset_map_list = self.battle_map_data.preset_map_list
        self.preset_map_folder = self.battle_map_data.preset_map_folder
        self.battle_map_list = self.battle_map_data.battle_map_list
        self.battle_map_folder = self.battle_map_data.battle_map_folder

        unit.Unit.troop_data = self.troop_data
        unit.Unit.leader_data = self.leader_data
        unit.Unit.troop_sprite_list = self.troop_data.troop_sprite_list
        unit.Unit.leader_sprite_list = self.leader_data.leader_sprite_list
        unit.Unit.status_list = self.troop_data.status_list
        unit.Unit.all_formation_list = self.troop_data.default_formation_list
        unit.Unit.effect_list = self.troop_data.effect_list

        effect.Effect.effect_list = self.troop_data.effect_list

        self.troop_animation = datasprite.TroopAnimationData(self.data_dir, self.module_dir,
                                                             [str(self.troop_data.race_list[key]["Name"]) for key in
                                                              self.troop_data.race_list], self.team_colour)
        self.unit_animation_data = self.troop_animation.unit_animation_data  # animation data pool
        self.body_sprite_pool = self.troop_animation.body_sprite_pool  # body sprite pool
        self.weapon_sprite_pool = self.troop_animation.weapon_sprite_pool  # weapon sprite pool
        self.armour_sprite_pool = self.troop_animation.armour_sprite_pool  # armour sprite pool
        self.weapon_joint_list = self.troop_animation.weapon_joint_list  # weapon joint data, for placing handle to hand
        self.colour_list = self.troop_animation.colour_list  # sprite colourising list

        self.effect_sprite_pool = self.troop_animation.effect_sprite_pool  # effect sprite pool
        self.effect_animation_pool = self.troop_animation.effect_animation_pool  # effect sprite animation pool

        uibattle.HeroUI.weapon_sprite_pool = self.weapon_sprite_pool

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
                    if key3 == "Base Main":
                        bullet_weapon_sprite_pool[key][key2][key3] = {}
                        image = pygame.transform.flip(value3, False, True)
                        bullet_weapon_sprite_pool[key][key2][key3] = image

        effect.Effect.bullet_sprite_pool = bullet_sprite_pool
        effect.Effect.bullet_weapon_sprite_pool = bullet_weapon_sprite_pool
        effect.Effect.effect_sprite_pool = self.effect_sprite_pool
        effect.Effect.effect_animation_pool = self.effect_animation_pool

        # Battle map object
        self.battle_base_map = battlemap.BaseMap(self.main_dir)  # create base terrain map
        self.battle_feature_map = battlemap.FeatureMap(self.main_dir)  # create terrain feature map
        self.battle_height_map = battlemap.HeightMap()  # create height map
        self.battle_map = battlemap.BeautifulMap(self.main_dir, self.screen_scale, self.battle_height_map)
        self.battle_camera.add(self.battle_map)

        effect.Effect.height_map = self.battle_height_map
        unit.Unit.base_map = self.battle_base_map  # add battle map to unit class
        unit.Unit.feature_map = self.battle_feature_map
        unit.Unit.height_map = self.battle_height_map

        # Main menu interface

        image_list = load_base_button(self.module_dir, self.screen_scale)

        main_menu_buttons_box = uimenu.BoxUI((400, 500), parent=self.screen)

        f = 0.68
        self.preset_map_button = uimenu.BrownMenuButton((0, -1 * f), key_name="main_menu_preset_map", parent=main_menu_buttons_box)
        self.custom_map_button = uimenu.BrownMenuButton((0, -0.6 * f), key_name="main_menu_custom_map", parent=main_menu_buttons_box)
        self.game_edit_button = uimenu.BrownMenuButton((0, -0.2 * f), key_name="main_menu_editor", parent=main_menu_buttons_box)
        self.lore_button = uimenu.BrownMenuButton((0, 0.2 * f), key_name="main_menu_lorebook", parent=main_menu_buttons_box)
        self.option_button = uimenu.BrownMenuButton((0, 0.6 * f), key_name="game_option", parent=main_menu_buttons_box)
        self.quit_button = uimenu.BrownMenuButton((0, 1 * f), key_name="game_quit", parent=main_menu_buttons_box)

        # just to test
        test_list = uimenu.ListUI(pivot=(-1,-1), origin=(-1,-1), parent=self.screen, size=(200,600), items=["abc","def"])

        self.mainmenu_button = (self.preset_map_button, self.custom_map_button, self.game_edit_button,
                                self.lore_button, self.option_button, self.quit_button, main_menu_buttons_box)


        # Battle map select menu button
        battle_select_image = load_images(self.module_dir, screen_scale=self.screen_scale,
                                          subfolder=("ui", "mapselect_ui"))

        self.map_title = uimenu.MapTitle((self.screen_rect.width / 2, 0))

        self.map_preview = uimenu.MapPreview((self.screen_rect.width / 2, self.map_title.image.get_height()))

        self.unit_selector = uibattle.UnitSelector((self.screen_rect.width / 2, self.screen_rect.height),
                                                   battle_select_image["unit_select"], icon_scale=0.4)
        uibattle.UIScroll(self.unit_selector, self.unit_selector.rect.topright)  # scroll bar for unit pick

        bottom_height = self.screen_rect.height - image_list[0].get_height()
        self.select_button = uimenu.MenuButton(image_list,
                                               (self.screen_rect.width - image_list[0].get_width(), bottom_height),
                                               self.main_ui_updater, key_name="select_button")
        self.start_button = uimenu.MenuButton(image_list,
                                              (self.screen_rect.width - image_list[0].get_width(), bottom_height),
                                              self.main_ui_updater, key_name="start_button")
        self.map_back_button = uimenu.MenuButton(image_list,
                                                 (self.screen_rect.width - (
                                                         self.screen_rect.width - image_list[0].get_width()),
                                                  bottom_height),
                                                 self.main_ui_updater, key_name="back_button")

        self.map_select_button = (self.select_button, self.map_back_button)
        self.team_select_button = (self.select_button, self.map_back_button)
        self.unit_select_button = (self.start_button, self.map_back_button)

        self.map_list_box = uimenu.ListBox((self.screen_width - (battle_select_image["name_list"].get_width() * 2), 0),
                                           battle_select_image["name_list"])
        uibattle.UIScroll(self.map_list_box, self.map_list_box.rect.topright)  # scroll bar for map list

        self.unit_list_box = uimenu.ListBox((self.screen_width - battle_select_image["unit_list"].get_width(), 0),
                                            battle_select_image["unit_list"])
        uibattle.UIScroll(self.unit_list_box, self.unit_list_box.rect.topright)  # scroll bar for map list

        self.source_list_box = uimenu.ListBox((self.screen_width - (battle_select_image["name_list"].get_width()), 0),
                                              battle_select_image["top_box"])  # source list ui box
        uibattle.UIScroll(self.source_list_box, self.source_list_box.rect.topright)  # scroll bar for source list
        self.map_option_box = uimenu.MapOptionBox((self.screen_width, battle_select_image["top_box"].get_height()),
                                                  battle_select_image["top_box"],
                                                  0)  # ui box for battle option during preset map preparation screen
        self.custom_map_option_box = uimenu.MapOptionBox((self.screen_width, 0), battle_select_image["top_box"],
                                                         1)  # ui box for battle option during preparation screen

        self.custom_map_list_box = uimenu.ListUI(pivot=(-1, -1), origin=(-1, -1), size=(200, 600),
                                                 items=self.battle_map_list, parent=self.screen)

        self.org_chart = uimenu.OrgChart(load_image(self.module_dir, self.screen_scale,
                                                    "org.png", ("ui", "mapselect_ui")),
                                         (self.screen_rect.center[0] * 1.3, self.screen_rect.height / 12))

        self.army_stat = uimenu.ArmyStat(self.map_option_box.rect.bottomleft,
                                         load_image(self.module_dir, self.screen_scale, "stat.png",
                                                    ("ui", "mapselect_ui")))  # army stat
        self.unit_stat = {}
        self.camp_icon = [{}]

        model_room_image = load_image(self.module_dir, self.screen_scale, "model_room.png", ("ui", "mapselect_ui"))
        self.unit_model_room = uimenu.ArmyStat((self.screen_rect.center[0] - (model_room_image.get_width() / 2),
                                                self.unit_selector.rect.midtop[1] - model_room_image.get_height()),
                                               model_room_image)  # troop stat

        self.observe_mode_tick_box = uimenu.TickBox((self.map_option_box.rect.topleft[0] * 1.05,
                                                     self.map_option_box.rect.topleft[1] * 1.15),
                                                    battle_select_image["untick"], battle_select_image["tick"],
                                                    "observe")
        self.night_battle_tick_box = uimenu.TickBox((self.map_option_box.rect.topleft[0] * 1.05,
                                                     self.map_option_box.rect.topleft[1] * 1.3),
                                                    battle_select_image["untick"], battle_select_image["tick"], "night")
        self.weather_custom_select = uimenu.NameList(self.map_option_box,
                                                     (self.map_option_box.rect.midleft[0],
                                                      self.map_option_box.rect.midleft[
                                                          1] + self.map_option_box.image.get_height() / 4),
                                                     "Weather: Light Random")
        self.wind_custom_select = uimenu.NameList(self.map_option_box,
                                                  (self.map_option_box.rect.midleft[0],
                                                   self.map_option_box.rect.midleft[
                                                       1] + self.map_option_box.image.get_height() / 10),
                                                  "Wind Direction: 0")

        self.current_map_row = 0
        self.current_map_select = 0
        self.current_source_row = 0
        self.unit_select_row = 0

        self.enactment = False

        self.source_name_list = [""]
        self.source_scale_text = [""]
        self.source_scale = [""]
        self.source_text = [""]

        # Unit and troop editor button in game start menu

        self.unit_edit_button = uimenu.MenuButton(image_list,
                                                  (self.screen_rect.width / 2,
                                                   self.screen_rect.height - (image_list[0].get_height() * 4)),
                                                  self.main_ui_updater, key_name="main_menu_unit_editor")
        self.troop_create_button = uimenu.MenuButton(image_list,
                                                     (self.screen_rect.width / 2,
                                                      self.screen_rect.height - (image_list[0].get_height() * 2.5)),
                                                     self.main_ui_updater, key_name="main_menu_troop_editor")
        self.editor_back_button = uimenu.MenuButton(image_list,
                                                    (self.screen_rect.width / 2,
                                                     self.screen_rect.height - image_list[0].get_height()),
                                                    self.main_ui_updater, key_name="back_button")
        self.editor_button = (self.unit_edit_button, self.troop_create_button, self.editor_back_button)

        # Option menu button
        option_menu_dict = make_option_menu(self.module_dir, self.screen_scale, self.screen_rect, self.screen_width,
                                            self.screen_height, image_list,
                                            self.main_ui_updater, self.config["USER"], self.player1_key_bind,
                                            battle_select_image)
        self.back_button = option_menu_dict["back_button"]
        self.keybind_button = option_menu_dict["keybind_button"]
        self.default_button = option_menu_dict["default_button"]
        self.resolution_drop = option_menu_dict["resolution_drop"]
        self.resolution_bar = option_menu_dict["resolution_bar"]
        self.resolution_text = option_menu_dict["resolution_text"]
        self.option_menu_sliders = option_menu_dict["volume_sliders"]
        self.value_boxes = option_menu_dict["value_boxes"]
        self.volume_texts = option_menu_dict["volume_texts"]
        self.fullscreen_box = option_menu_dict["fullscreen_box"]
        self.fullscreen_text = option_menu_dict["fullscreen_text"]
        self.keybind_text = option_menu_dict["keybind_text"]
        self.keybind_icon = option_menu_dict["keybind_icon"]
        self.control_switch = option_menu_dict["control_switch"]

        self.option_text_list = tuple(
            [self.resolution_text, self.fullscreen_text] + [value for value in
                                                            self.volume_texts.values()])
        self.option_menu_button = (
            self.back_button, self.default_button, self.keybind_button, self.resolution_drop, self.fullscreen_box)

        # Profile box
        self.profile_name = self.profile_name
        profile_box_image = load_image(self.module_dir, self.screen_scale, "profile_box.png", ("ui", "mainmenu_ui"))
        self.profile_box = uimenu.TextBox(profile_box_image, (self.screen_width, 0),
                                          self.profile_name)  # profile name box at top right of screen at start_set menu screen

        # Load sound effect
        self.sound_effect_pool = self.create_sound_effect_pool()

        # Music player
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer = None
        if pygame.mixer:
            pygame.mixer.set_num_channels(1000)
            pygame.mixer.music.set_volume(self.master_volume)
            self.SONG_END = pygame.USEREVENT + 1
            self.music_list = glob.glob(self.module_dir + "/sound/music/*.ogg")
            pygame.mixer.music.load(self.music_list[0])
            pygame.mixer.music.play(-1)

        # Battle related UI
        self.fps_count = uibattle.FPScount()  # FPS number counter
        self.battle_ui_updater.add(self.fps_count)

        battle_ui_image = load_images(self.module_dir, screen_scale=self.screen_scale, subfolder=("ui", "battle_ui"))

        self.status_images, self.role_images, self.trait_images, self.skill_images = make_icon_data(self.module_dir,
                                                                                                    self.screen_scale)

        self.mini_map = uibattle.MiniMap((self.screen_rect.width, self.screen_rect.height))
        self.battle_ui_updater.add(self.mini_map)

        battle_ui_dict = make_battle_ui(battle_ui_image, self.team_colour,
                                        self.screen_rect.size)
        self.time_ui = battle_ui_dict["time_ui"]
        self.time_number = battle_ui_dict["time_number"]
        self.battle_scale_ui = battle_ui_dict["battle_scale_ui"]
        self.battle_ui_updater.add(self.time_ui, self.time_number)
        self.wheel_ui = battle_ui_dict["wheel_ui"]
        self.command_ui = battle_ui_dict["command_ui"]
        self.ui_updater.add(self.command_ui)

        weather.Weather.wind_compass_images = {"wind_compass": battle_ui_image["wind_compass"],
                                               "wind_arrow": battle_ui_image["wind_arrow"]}

        # 4 Skill icons UI
        uibattle.SkillCardIcon(self.skill_images["0"], (self.command_ui.image.get_width() +
                                                        self.skill_images["0"].get_width() / 2, 0), "0")
        uibattle.SkillCardIcon(self.skill_images["0"], (self.command_ui.image.get_width() +
                                                        self.skill_images["0"].get_width() * 2, 0), "1")
        uibattle.SkillCardIcon(self.skill_images["0"], (self.command_ui.image.get_width() +
                                                        self.skill_images["0"].get_width() * 3.5, 0), "2")
        uibattle.SkillCardIcon(self.skill_images["0"], (self.command_ui.image.get_width() +
                                                        self.skill_images["0"].get_width() * 5, 0), "3")

        uibattle.AimTarget.aim_images = {0: battle_ui_image["aim_0"], 1: battle_ui_image["aim_1"],
                                         2: battle_ui_image["aim_2"], 3: pygame.Surface((0, 0))}

        box_image = load_image(self.module_dir, self.screen_scale, "unit_presetbox.png", ("ui", "mainmenu_ui"))
        self.popup_list_box = uimenu.ListBox((0, 0), box_image,
                                             15)  # popup box need to be in higher layer
        uibattle.UIScroll(self.popup_list_box, self.popup_list_box.rect.topright)

        editor_dict = make_editor_ui(self.module_dir, self.screen_scale, self.screen_rect,
                                     load_image(self.module_dir, self.screen_scale, "name_list.png",
                                                ("ui", "mapselect_ui")),
                                     load_base_button(self.module_dir, self.screen_scale), self.main_ui_updater)
        self.unit_preset_list_box = editor_dict["unit_listbox"]
        self.preset_select_border = editor_dict["preset_select_border"]
        self.editor_troop_list_box = editor_dict["troop_listbox"]
        self.unit_delete_button = editor_dict["unit_delete_button"]
        self.unit_save_button = editor_dict["unit_save_button"]
        self.popup_list_box = editor_dict["popup_listbox"]
        self.filter_box = editor_dict["filter_box"]
        self.filter_tick_box = editor_dict["filter_tick_box"]

        self.unit_editor_ui = (self.unit_preset_list_box, self.preset_select_border, self.editor_troop_list_box,
                               self.unit_delete_button, self.unit_save_button, self.popup_list_box, self.filter_box,
                               self.filter_tick_box)

        # User input popup ui
        input_ui_dict = make_input_box(self.module_dir, self.screen_scale, self.screen_rect,
                                       load_base_button(self.module_dir, self.screen_scale))
        self.input_ui = input_ui_dict["input_ui"]
        self.input_ok_button = input_ui_dict["input_ok_button"]
        self.input_close_button = input_ui_dict["input_close_button"]
        self.input_cancel_button = input_ui_dict["input_cancel_button"]
        self.input_box = input_ui_dict["input_box"]
        self.confirm_ui = input_ui_dict["confirm_ui"]
        self.input_button = (self.input_ok_button, self.input_cancel_button, self.input_close_button)
        self.input_ui_popup = (self.input_ui, self.input_box, self.input_ok_button, self.input_cancel_button)
        self.confirm_ui_popup = (self.confirm_ui, self.input_ok_button, self.input_cancel_button)
        self.inform_ui_popup = (self.input_ui, self.input_box, self.input_close_button)

        # Other ui in battle
        self.battle_done_box = uibattle.BattleDone((self.screen_width / 2, self.screen_height / 2),
                                                   battle_ui_image["end_box"], battle_ui_image["result_box"])
        self.battle_done_button = uibattle.UIButton(battle_ui_image["end_button"], layer=19)
        self.battle_done_button.change_pos(
            (self.battle_done_box.pos[0], self.battle_done_box.box_image.get_height() * 2))

        drama.TextDrama.images = load_images(self.module_dir, screen_scale=self.screen_scale,
                                             subfolder=("ui", "popup_ui", "drama_text"))
        drama.TextDrama.screen_rect = self.screen_rect
        self.drama_text = drama.TextDrama()  # message at the top of screen that show up for important event

        # Battle event log
        self.event_log = uibattle.EventLog(battle_ui_image["event_log"], (0, self.screen_rect.height))
        uibattle.UIScroll(self.event_log, self.event_log.rect.topright)  # event log scroll
        unit.Unit.event_log = self.event_log  # Assign event_log to unit class to broadcast event to the log
        self.battle_ui_updater.add(self.event_log.scroll)

        # Battle ESC menu
        esc_menu_dict = make_esc_menu(self.module_dir, self.screen_rect, self.screen_scale, self.master_volume)
        self.battle_menu = esc_menu_dict["battle_menu"]
        self.battle_menu_button = esc_menu_dict["battle_menu_button"]
        self.esc_option_menu_button = esc_menu_dict["esc_option_menu_button"]
        self.esc_slider_menu = esc_menu_dict["esc_slider_menu"]
        self.esc_value_boxes = esc_menu_dict["esc_value_boxes"]

        # Text
        self.single_text_popup = uimenu.TextPopup()  # popup box that show name when mouse over

        # Encyclopedia interface
        self.encyclopedia, self.lore_name_list, self.filter_tag_list, self.lore_button_ui, self.page_button = make_lorebook(
            self, self.module_dir, self.screen_scale, self.screen_rect)

        self.encyclopedia_stuff = (self.encyclopedia, self.lore_name_list, self.filter_tag_list,
                                   self.lore_name_list.scroll, self.filter_tag_list.scroll, *self.lore_button_ui)

        lorebook.Lorebook.concept_stat = csv_read(self.module_dir, "concept_stat.csv",
                                                  ("lore",), header_key=True)
        lorebook.Lorebook.concept_lore = csv_read(self.module_dir, "concept_lore" + "_" + self.language + ".csv",
                                                  ("lore",))
        lorebook.Lorebook.history_stat = csv_read(self.module_dir, "history_stat.csv",
                                                  ("lore",), header_key=True)
        lorebook.Lorebook.history_lore = csv_read(self.module_dir, "history_lore" + "_" + self.language + ".csv",
                                                  ("lore",))

        lorebook.Lorebook.faction_data = self.faction_data
        lorebook.Lorebook.troop_data = self.troop_data
        lorebook.Lorebook.leader_data = self.leader_data
        lorebook.Lorebook.battle_map_data = self.battle_map_data
        lorebook.Lorebook.screen_rect = self.screen_rect

        self.encyclopedia.change_module()

        self.battle = battle.Battle(self)

        unit.Unit.battle = self.battle
        effect.Effect.battle = self.battle

        unit_to_make = tuple(set([this_unit for this_unit in self.troop_data.troop_list] +
                                 [this_unit for this_unit in self.leader_data.leader_list]))
        who_todo = {key: value for key, value in self.troop_data.troop_list.items() if key in unit_to_make}
        who_todo |= {key: value for key, value in self.leader_data.leader_list.items() if key in unit_to_make}

        # self.create_troop_sprite_pool(who_todo)

        # Background image
        self.background_image = load_images(self.module_dir, screen_scale=self.screen_scale,
                                            subfolder=("ui", "mainmenu_ui", "background"))
        self.background = self.background_image["main"]

        # Starting script
        self.main_ui_updater.remove(*self.menu_button)  # remove all button from drawing
        self.menu_button.remove(
            *self.menu_button)  # remove all button at the start and add later depending on menu_state
        self.menu_button.add(*self.mainmenu_button)  # add only game start menu button back

        self.start_menu_ui_only = *self.menu_button, self.profile_box  # ui that only appear at the start menu
        self.main_ui_updater.add(*self.start_menu_ui_only)
        self.menu_state = "main_menu"
        self.input_popup = (None, None)  # popup for text input state
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

    def setup_profiler(self):
        from engine.uibattle.uibattle import Profiler
        self.profiler = Profiler()
        self.profiler.enable()
        self.battle_ui_updater.add(self.profiler)

    def run(self):
        while True:
            # Get user input
            self.dt = self.clock.get_time() / 1000  # dt before game_speed
            mouse_left_up = False
            mouse_left_down = False
            mouse_center_up = False
            mouse_right_up = False
            mouse_right_down = False
            mouse_scroll_down = False
            mouse_scroll_up = False
            esc_press = False
            input_esc = False
            key_press = pygame.key.get_pressed()
            if pygame.mouse.get_pressed()[0]:  # Hold left click
                mouse_left_down = True
            elif pygame.mouse.get_pressed()[2]:  # Hold left click
                mouse_right_down = True

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
                    if event.button == 1:  # left click
                        mouse_left_up = True
                    elif event.button == 2:
                        mouse_center_up = True
                    elif event.button == 3:
                        mouse_right_up = True
                    elif event.button == 4:  # Mouse scroll down
                        mouse_scroll_up = True
                    elif event.button == 5:  # Mouse scroll up
                        mouse_scroll_down = True

                    if self.input_popup[0] == "keybind_input":
                        if self.config["USER"]["control player 1"] == "keyboard" and not \
                                self.input_close_button.rect.collidepoint(
                                    self.mouse_pos):  # check for keyboard mouse key
                            self.assign_key(tuple(self.mouse_bind.keys())[tuple(
                                self.mouse_bind.values()).index(event.button)])

                elif event.type == pygame.JOYBUTTONUP:
                    joystick = event.instance_id
                    if self.config["USER"]["control player 1"] == "joystick" and self.input_popup[0] == "keybind_input":
                        # check for button press
                        self.assign_key(event.button)

                elif event.type == pygame.KEYDOWN:
                    if self.input_popup[0]:  # event update to input box
                        if event.key == pygame.K_ESCAPE:
                            input_esc = True

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

                elif event.type == QUIT or self.quit_button.event or (esc_press and self.menu_state == "main_menu"):
                    self.quit_button.event = False
                    self.input_popup = ("confirm_input", "quit")
                    self.confirm_ui.change_instruction("Quit Game?")
                    self.main_ui_updater.add(*self.confirm_ui_popup)

            self.mouse_pos = pygame.mouse.get_pos()
            self.cursor.update(self.mouse_pos)
            # ^ End user input
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.background, (0, 0))  # blit background over instead of clear() to reset screen

            if self.input_popup[
                0]:  # currently, have input text pop up on screen, stop everything else until done
                for button in self.input_button:
                    button.update(self.mouse_pos, mouse_left_up, mouse_left_down)

                if self.input_ok_button.event or key_press[pygame.K_RETURN] or key_press[pygame.K_KP_ENTER]:
                    self.input_ok_button.event = False

                    if self.input_popup[1] == "profile_name":
                        self.profile_name = self.input_box.text
                        self.profile_box.change_text(self.profile_name)

                        edit_config("USER", "player_name", self.profile_name, "configuration.ini", self.config)

                    elif "custom_camp_size" in self.input_popup[1] and self.input_box.text.isdigit():
                        pos = self.input_popup[1].split("/")[1]
                        pos = pos.replace("(", "").replace(")", "").split(", ")
                        pos = [float(item) for item in pos]
                        self.camp_pos[0][int(self.input_popup[1][-1])].insert(0, [pos, int(self.input_box.text)])
                        self.camp_icon.insert(0, uibattle.TempUnitIcon(int(self.input_popup[1][-1]),
                                                                       self.input_box.text, 0))
                        self.unit_selector.setup_unit_icon(self.unit_icon, self.camp_icon)
                        self.map_preview.change_mode(1, camp_pos_list=self.camp_pos)

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
                        self.map_data["info"]["weather"][0][2] = int(self.input_box.text)
                        self.wind_custom_select.rename("Wind Direction: " + self.input_box.text)

                    elif self.input_popup[1] == "quit":
                        pygame.time.wait(1000)
                        if pygame.mixer:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.unload()
                        pygame.quit()
                        sys.exit()

                    self.input_box.text_start("")
                    self.input_popup = (None, None)
                    self.main_ui_updater.remove(*self.input_ui_popup, *self.confirm_ui_popup, *self.inform_ui_popup)

                elif self.input_cancel_button.event or self.input_close_button.event or input_esc:
                    self.input_cancel_button.event = False
                    self.input_close_button.event = False
                    self.input_box.text_start("")
                    self.input_popup = (None, None)
                    self.main_ui_updater.remove(*self.input_ui_popup, *self.confirm_ui_popup, *self.inform_ui_popup)

                elif self.input_popup[0] == "text_input":
                    if self.text_delay == 0:
                        if key_press[self.input_box.hold_key]:
                            self.input_box.player_input(None, key_press)
                            self.text_delay = 0.1
                    else:
                        self.text_delay += self.dt
                        if self.text_delay >= 0.3:
                            self.text_delay = 0

            elif self.input_popup == (None, None):
                self.menu_button.update(self.mouse_pos, mouse_left_up, mouse_left_down)
                if self.menu_state == "main_menu":
                    self.menu_main(mouse_left_up)

                elif self.menu_state == "preset_map":
                    self.menu_preset_map_select(mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down,
                                                esc_press)

                elif self.menu_state == "custom_map":
                    self.menu_custom_map_select(mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down,
                                                esc_press)

                elif self.menu_state == "custom_team_select":
                    self.menu_custom_team_select(mouse_left_up, mouse_left_down, mouse_right_up,
                                                 mouse_scroll_up, mouse_scroll_down, esc_press)

                elif self.menu_state == "custom_unit_select":
                    self.menu_custom_unit_select(mouse_left_up, mouse_left_down, mouse_scroll_up,
                                                 mouse_scroll_down, esc_press)

                elif self.menu_state == "custom_unit_setup":
                    self.menu_custom_unit_setup(mouse_left_up, mouse_left_down, mouse_right_up, mouse_scroll_up,
                                                mouse_scroll_down, esc_press)

                elif self.menu_state == "custom_leader_setup":
                    self.menu_custom_leader_setup(mouse_left_up, mouse_left_down, mouse_right_up, mouse_right_down,
                                                  mouse_scroll_up, mouse_scroll_down, esc_press)

                elif self.menu_state == "game_creator":
                    self.menu_game_editor(mouse_left_up, mouse_left_down, mouse_scroll_up,
                                          mouse_scroll_down, esc_press)

                elif self.menu_state == "option":
                    self.menu_option(mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press)

                elif self.menu_state == "keybind":
                    self.menu_keybind(mouse_left_up, esc_press)

                elif self.menu_state == "encyclopedia":
                    command = self.lorebook_process(self.main_ui_updater, mouse_left_up, mouse_left_down,
                                                    mouse_scroll_up, mouse_scroll_down, esc_press)
                    if esc_press or command == "exit":
                        self.menu_state = "main_menu"  # change menu back to default 0

            self.main_ui_updater.draw(self.screen)
            pygame.display.update()
            self.clock.tick(60)
