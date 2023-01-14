import configparser
import csv
import glob
import importlib
import os.path
import sys
from pathlib import Path

import pygame
import pygame.freetype
import screeninfo
from gamescript import battlemap, weather, lorebook, drama, battleui, menu, damagesprite, uniteditor, \
    battle, leader, unit, subunit, datasprite, datamap
from gamescript.common import utility
from gamescript.common.battle import setup_battle_unit, generate_unit
from pygame.locals import *

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
empty_function = utility.empty_function

# Module that get loads with import in common.game.setup after
make_battle_list_data = empty_function
make_battle_ui = empty_function
make_editor_ui = empty_function
make_esc_menu = empty_function
make_event_log = empty_function
make_faction_troop_leader_data = empty_function
make_genre_specific_ui = empty_function
make_icon_data = empty_function
make_input_box = empty_function
make_lorebook = empty_function
make_option_menu = empty_function
make_popup_ui = empty_function

script_dir = os.path.split(os.path.abspath(__file__))[0] + "/"
for entry in os.scandir(Path(script_dir + "/common/game/setup/")):  # load and replace modules from common.game.setup
    if entry.is_file():
        if ".py" in entry.name:
            file_name = entry.name[:-3]
        elif ".pyc" in entry.name:
            file_name = entry.name[:-4]
        exec(f"from gamescript.common.game.setup import " + file_name)
        exec(f"" + file_name + " = " + file_name + "." + file_name)

version_name = "Dream Decision"  # Game version name that will appear as game name

unit_state_text = {0: "Idle", 1: "Walk", 2: "Run", 3: "Walk (M)", 4: "Run (M)", 5: "Walk (R)", 6: "Run (R)",
                   7: "Walk (F)", 8: "Run (F)", 10: "Melee", 11: "Shoot", 12: "Walk (S)", 13: "Run (S)",
                   65: "Sleep", 66: "Camp", 67: "Rest", 68: "Dance", 69: "Party", 95: "Disobey", 96: "Retreat",
                   97: "Collapse", 98: "Retreat", 99: "Broken", 100: "Destroyed"}

subunit_state_text = {0: "Idle", 1: "Walk", 2: "Run", 3: "Walk (M)", 4: "Run (M)", 5: "Walk (R)", 6: "Run (R)",
                      10: "Melee", 11: "Shoot",
                      12: "Walk (S)", 13: "Run (S)", 95: "Disobey", 96: "Flee", 97: "Rest", 98: "Flee", 99: "Flee",
                      100: "Dead"}
subunit_state = {key: value.split(" ")[0] for key, value in subunit_state_text.items()}

leader_state_text = {96: "Flee", 97: "POW", 98: "MIA", 99: "WIA", 100: "KIA"}

morale_state_text = {0: "Broken", 1: "Fleeing", 2: "Breaking", 3: "Poor", 4: "Wavering", 5: "Balanced",
                     6: "Steady", 7: "Fine", 8: "Confident", 9: "Eager", 10: "Ready", 11: "Merry", 12: "Elated",
                     13: "Ecstatic",
                     14: "Inspired", 15: "Fervent"}  # unit morale state name

stamina_state_text = {0: "Collapse", 1: "Exhausted", 2: "Severed", 3: "Very Tired", 4: "Tired", 5: "Winded",
                      6: "Moderate",
                      7: "Alert", 8: "Warmed Up", 9: "Active", 10: "Fresh"}  # unit stamina state name

quality_text = ("Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect")  # item quality name

leader_level = ("Commander", "Sub-General", "Sub-General", "Sub-Commander", "General", "Sub-General", "Sub-General",
                "Advisor")  # Name of leader position in unit, the first 4 is for commander unit

team_colour = unit.team_colour

script_folder = "gamescript"


class Game:
    empty_method = utility.empty_method

    # import from common.game
    back_mainmenu = empty_method
    change_battle_source = empty_method
    change_to_source_selection_menu = empty_method
    change_sound_volume = empty_method
    convert_formation_preset = empty_method
    create_preview_map = empty_method
    create_sound_effect_pool = empty_method
    create_sprite_pool = empty_method
    create_team_coa = empty_method
    create_unit_slot = empty_method
    loading_screen = empty_method
    menu_game_editor = empty_method
    menu_char_select = empty_method
    menu_main = empty_method
    menu_map_select = empty_method
    menu_option = empty_method
    menu_team_select = empty_method
    read_battle_source = empty_method
    read_selected_map_data = empty_method
    start_battle = empty_method

    # import from *genre*.game
    leader_position_check = empty_method

    generate_unit = generate_unit.generate_unit
    setup_battle_unit = setup_battle_unit.setup_battle_unit

    popup_list_open = utility.popup_list_open

    lorebook_process = lorebook.lorebook_process

    script_dir = script_dir
    for entry in os.scandir(Path(script_dir + "/common/game/")):  # load and replace modules from common.game
        if entry.is_file():
            if ".pyc" in entry.name:
                file_name = entry.name[:-4]
            elif ".py" in entry.name:
                file_name = entry.name[:-3]
                exec(f"from gamescript.common.game import " + file_name)
                exec(f"" + file_name + " = " + file_name + "." + file_name)

    # Will be changed in change_game_genre function depending on selected genre
    char_select = False
    leader_sprite = False
    troop_sprite_size = (200, 200)
    start_zoom = 1
    start_zoom_mode = "Follow"
    time_speed_scale = 1
    troop_size_adjustable = False
    unit_size = (8, 8)
    add_troop_number_sprite = False
    command_ui_type = "command"

    def __init__(self, main_dir, error_log):
        pygame.init()  # Initialize pygame

        pygame.mouse.set_visible(False)  # set mouse as not visible, use in-game mouse sprite

        self.main_dir = main_dir
        self.error_log = error_log

        lorebook.Lorebook.main_dir = self.main_dir
        uniteditor.PreviewBox.main_dir = self.main_dir

        # Read config file
        config = configparser.ConfigParser()
        try:
            config.read_file(open(os.path.join(self.main_dir, "configuration.ini")))  # read config file
        except FileNotFoundError:  # Create config file if not found with the default
            try:  # for repo version
                genre_folder = Path(os.path.join(self.main_dir, script_folder))
                genre_folder = [x for x in genre_folder.iterdir() if x.is_dir()]
            except FileNotFoundError:  # for release version
                genre_folder = Path(os.path.join(self.main_dir, "lib", script_folder))
                genre_folder = [x for x in genre_folder.iterdir() if x.is_dir()]
            genre_folder = [os.sep.join(os.path.normpath(folder_name).split(os.sep)[-1:]).capitalize() for folder_name
                            in genre_folder]
            if "__pycache__" in genre_folder:
                genre_folder.remove("__pycache__")  # just grab the first genre folder as default
            if "Common" in genre_folder:
                genre_folder.remove("Common")
            config = configparser.ConfigParser()

            screen = screeninfo.get_monitors()[0]
            screen_width = int(screen.width)
            screen_height = int(screen.height)

            config["DEFAULT"] = {"screen_width": screen_width, "screen_height": screen_height, "full_screen": "0",
                                 "player_Name": "Noname", "master_volume": "100.0", "music_volume": "0.0",
                                 "voice_volume": "100.0", "effect_volume": "100.0", "max_fps": "60", "ruleset": "1",
                                 "genre": genre_folder[-1], "language": "en", "play_troop_animation": "1"}
            config["USER"] = {key: value for key, value in config["DEFAULT"].items()}
            with open(os.path.join(self.main_dir, "configuration.ini"), "w") as cf:
                config.write(cf)
            config.read_file(open(os.path.join(self.main_dir, "configuration.ini")))

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
        self.genre = str(self.config["USER"]["genre"])
        self.language = str(self.config["USER"]["language"])
        self.ruleset = 1  # for now default historical ruleset only
        self.play_troop_animation = int(self.config["USER"]["play_troop_animation"])

        # Set the display mode
        self.screen_rect = Rect(0, 0, self.screen_width, self.screen_height)
        self.screen_scale = (self.screen_rect.width / 1920, self.screen_rect.height / 1080)
        unit.Unit.screen_scale = self.screen_scale
        subunit.Subunit.screen_scale = self.screen_scale
        damagesprite.DamageSprite.screen_scale = self.screen_scale

        self.window_style = 0
        if self.full_screen == 1:
            self.window_style = pygame.FULLSCREEN
        self.best_depth = pygame.display.mode_ok(self.screen_rect.size, self.window_style, 32)
        self.screen = pygame.display.set_mode(self.screen_rect.size, self.window_style | pygame.RESIZABLE,
                                              self.best_depth)

        self.clock = pygame.time.Clock()

        self.loading = load_image(self.main_dir, self.screen_scale, "loading.png", ("ui", "mainmenu_ui"))
        self.loading = pygame.transform.scale(self.loading, self.screen_rect.size)

        self.ruleset_list = csv_read(self.main_dir, "ruleset_list.csv", ("data", "ruleset"))  # get ruleset list
        self.ruleset_folder = str(self.ruleset_list[self.ruleset][1]).strip("/")

        if not os.path.exists("profile"):  # make profile folder if not existed
            os.umask(0)
            os.makedirs("profile")
            os.makedirs("profile/unitpreset")
        if not os.path.exists("profile/unitpreset/" + str(self.ruleset)):  # create unitpreset folder for ruleset
            os.umask(0)
            os.makedirs("profile/unitpreset/" + str(self.ruleset))
        try:
            custom_unit_preset_list = csv_read(self.main_dir, "custom_unitpreset.csv",
                                               ("profile", "unitpreset", str(self.ruleset)))
            del custom_unit_preset_list["Name"]
            self.custom_unit_preset_list = {"New Preset": 0, **custom_unit_preset_list}
        except FileNotFoundError:
            with open("profile/unitpreset/" + str(self.ruleset) + "/custom_unitpreset.csv", "w") as edit_file:
                file_writer = csv.writer(edit_file, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
                file_writer.writerow(
                    ("Name", "Row 1", "Row 2", "Row 3", "Row 4", "Row 5", "Row 6",
                     "Row 7", "Row 8", "Leader", "Leader POS", "Faction"))  # create header
                edit_file.close()

            self.custom_unit_preset_list = {}

        # if not os.path.exists("\customunit"): # make custom subunit folder if not existed

        self.enactment = True
        self.unit_state_text = unit_state_text
        self.subunit_state = subunit_state
        self.leader_state_text = leader_state_text
        self.morale_state_text = morale_state_text
        self.stamina_state_text = stamina_state_text
        self.leader_level = leader_level

        self.map_source = 0  # current selected map source
        self.team_selected = 1
        self.char_selected = 0
        self.current_popup_row = 0
        self.team_pos = {}  # for saving preview map unit pos

        self.dt = 0
        self.text_delay = 0

        # Decorate the self window
        # icon = load_image(self.main_dir, "sword.jpg")
        # icon = pygame.transform.scale(icon, (32, 32))
        # pygame.display.set_icon(icon)

        # Initialise groups and objects

        # main drawer for ui
        self.main_ui_updater = pygame.sprite.LayeredUpdates()  # sprite drawer group

        # game start menu
        self.menu_button = pygame.sprite.Group()  # group of menu buttons that are currently get shown and update
        self.menu_icon = pygame.sprite.Group()  # mostly for option icon like volumne or screen resolution
        self.menu_slider = pygame.sprite.Group()

        # encyclopedia
        self.lore_button_ui = pygame.sprite.Group()  # buttons for encyclopedia group
        self.subsection_name = pygame.sprite.Group()  # subsection name objects group in encyclopedia blit on lore_name_list
        self.tag_filter_name = pygame.sprite.Group()  # tag filter objects group in encyclopedia blit on filter_name_list

        # battle select menu
        self.map_namegroup = pygame.sprite.Group()  # map name list group
        self.team_coa = pygame.sprite.Group()  # team coat of arm that also act as team selection icon
        self.army_stat = pygame.sprite.Group()  # ui box that show army stat in preset battle preparation screen
        self.char_stat = {}
        self.source_namegroup = pygame.sprite.Group()  # source name list group
        self.tick_box = pygame.sprite.Group()  # option tick box
        # battle related

        # unit editor
        self.troop_namegroup = pygame.sprite.Group()  # troop name list group
        self.popup_namegroup = pygame.sprite.Group()
        self.unit_edit_border = pygame.sprite.Group()  # border that appear when selected sub-subunit
        self.unitpreset_namegroup = pygame.sprite.Group()  # preset name list
        self.subunit_build = pygame.sprite.Group()

        # battle object group
        self.battle_camera = pygame.sprite.LayeredUpdates()  # layer drawer self camera, all image pos should be based on the map not screen
        self.battle_ui_updater = pygame.sprite.LayeredUpdates()  # this is layer drawer for ui, all image pos should be based on the screen

        self.unit_updater = pygame.sprite.Group()  # updater for unit objects, only for in battle not editor or preview
        self.subunit_updater = pygame.sprite.Group()  # updater for subunit objects
        self.leader_updater = pygame.sprite.Group()  # updater for leader objects
        self.ui_updater = pygame.sprite.Group()  # updater for ui objects
        self.weather_updater = pygame.sprite.Group()  # updater for weather objects
        self.effect_updater = pygame.sprite.Group()  # updater for effect objects (e.g. range melee_attack sprite)

        self.preview_char = pygame.sprite.Group()  # group for char list in char select screen

        self.damage_sprites = pygame.sprite.Group()  # all damage sprite group and maybe other range effect stuff later
        self.direction_arrows = pygame.sprite.Group()
        self.troop_number_sprite = pygame.sprite.Group()  # troop text number that appear next to unit sprite

        self.button_ui = pygame.sprite.Group()  # ui button group in battle
        self.inspect_selected_border = pygame.sprite.Group()  # subunit selected border in inspect ui unit box
        self.wheel_ui = pygame.sprite.Group()

        self.skill_icon = pygame.sprite.Group()  # skill and trait icon objects
        self.effect_icon = pygame.sprite.Group()  # status effect icon objects

        self.battle_menu_button = pygame.sprite.Group()  # buttons for esc menu object group
        self.esc_option_menu_button = pygame.sprite.Group()  # buttons for esc menu option object group
        self.slider_menu = pygame.sprite.Group()  # volume slider in esc option menu

        self.unit_icon = pygame.sprite.Group()  # unit icon object group in unit selector ui
        self.weather_matter = pygame.sprite.Group()  # sprite of weather effect group such as rain sprite
        self.weather_effect = pygame.sprite.Group()  # sprite of special weather effect group such as fog that cover whole screen

        # Assign containers
        menu.MenuButton.containers = self.menu_button
        menu.OptionMenuText.containers = self.menu_icon
        menu.SliderMenu.containers = self.menu_slider, self.slider_menu

        menu.NameList.containers = self.map_namegroup
        menu.TeamCoa.containers = self.team_coa

        menu.TickBox.containers = self.tick_box

        lorebook.SubsectionName.containers = self.main_ui_updater, self.battle_ui_updater

        uniteditor.PreviewBox.effect_image = load_image(self.main_dir, self.screen_scale, "effect.png",
                                                        "map")  # map special effect image

        # battle containers
        battleui.SwitchButton.containers = self.ui_updater
        battleui.SelectedSquad.containers = self.unit_edit_border, self.battle_ui_updater
        battleui.SkillCardIcon.containers = self.skill_icon, self.battle_ui_updater
        battleui.EffectCardIcon.containers = self.effect_icon, self.battle_ui_updater
        battleui.UnitIcon.containers = self.unit_icon, self.main_ui_updater, self.battle_ui_updater
        battleui.TroopNumber.containers = self.troop_number_sprite, self.effect_updater, self.battle_camera
        battleui.DirectionArrow.containers = self.direction_arrows, self.effect_updater, self.battle_camera
        battleui.WheelUI.containers = self.wheel_ui

        damagesprite.DamageSprite.containers = self.damage_sprites, self.effect_updater, self.battle_camera

        menu.EscButton.containers = self.battle_menu_button, self.esc_option_menu_button

        weather.MatterSprite.containers = self.weather_matter, self.battle_ui_updater, self.weather_updater
        weather.SpecialEffect.containers = self.weather_effect, self.battle_ui_updater, self.weather_updater

        unit.Unit.containers = self.unit_updater
        subunit.Subunit.containers = self.subunit_updater, self.battle_camera
        leader.Leader.containers = self.leader_updater

        # game cursor
        cursor_images = load_images(self.main_dir, subfolder=("ui", "cursor"))  # no need to scale cursor
        self.cursor = menu.Cursor(cursor_images)
        self.main_ui_updater.add(self.cursor)
        self.battle_ui_updater.add(self.cursor)

        self.game_intro(self.screen, self.clock, False)  # run intro

        # Main menu related stuff
        image_list = load_base_button(self.main_dir, self.screen_scale)
        self.preset_map_button = menu.MenuButton(self.screen_scale, image_list,
                                                 (self.screen_rect.width / 2,
                                                  self.screen_rect.height - (image_list[0].get_height() * 8.5)),
                                                 self.main_ui_updater, text="Preset Map")
        self.custom_map_button = menu.MenuButton(self.screen_scale, image_list,
                                                 (self.screen_rect.width / 2,
                                                  self.screen_rect.height - (image_list[0].get_height() * 7)),
                                                 self.main_ui_updater, text="Custom Map")
        self.game_edit_button = menu.MenuButton(self.screen_scale, image_list,
                                                (self.screen_rect.width / 2,
                                                 self.screen_rect.height - (image_list[0].get_height() * 5.5)),
                                                self.main_ui_updater, text="Unit Editor")
        self.lore_button = menu.MenuButton(self.screen_scale, image_list,
                                           (self.screen_rect.width / 2,
                                            self.screen_rect.height - (image_list[0].get_height() * 4)),
                                           self.main_ui_updater, text="Encyclopedia")
        self.option_button = menu.MenuButton(self.screen_scale, image_list,
                                             (self.screen_rect.width / 2,
                                              self.screen_rect.height - (image_list[0].get_height() * 2.5)),
                                             self.main_ui_updater, text="Option")
        self.quit_button = menu.MenuButton(self.screen_scale, image_list,
                                           (self.screen_rect.width / 2,
                                            self.screen_rect.height - (image_list[0].get_height())),
                                           self.main_ui_updater, text="Quit")
        self.mainmenu_button = (self.preset_map_button, self.custom_map_button, self.game_edit_button,
                                self.lore_button, self.option_button, self.quit_button)

        # Battle map
        self.battle_base_map = battlemap.BaseMap(self.main_dir)  # create base terrain map
        self.battle_feature_map = battlemap.FeatureMap(self.main_dir)  # create terrain feature map
        self.battle_height_map = battlemap.HeightMap()  # create height map
        self.battle_map = battlemap.BeautifulMap(self.main_dir, self.screen_scale)
        self.battle_camera.add(self.battle_map)

        damagesprite.DamageSprite.height_map = self.battle_height_map
        subunit.Subunit.base_map = self.battle_base_map  # add battle map to subunit class
        subunit.Subunit.feature_map = self.battle_feature_map
        subunit.Subunit.height_map = self.battle_height_map

        # Battle map select menu button
        battle_select_image = load_images(self.main_dir, screen_scale=self.screen_scale,
                                          subfolder=("ui", "mapselect_ui"))

        self.map_title = menu.MapTitle(self.screen_scale, (self.screen_rect.width / 2, 0))

        self.map_description = menu.DescriptionBox(battle_select_image["map_description"], self.screen_scale,
                                                   (self.screen_rect.width / 2, self.screen_rect.height / 1.3))
        self.map_show = menu.MapPreview(self.main_dir, self.screen_scale,
                                        (self.screen_rect.width / 2, self.screen_rect.height / 3),
                                        self.battle_base_map.terrain_colour, self.battle_feature_map.feature_colour,
                                        self.battle_map.battle_map_colour)
        self.source_description = menu.DescriptionBox(battle_select_image["source_description"], self.screen_scale,
                                                      (self.screen_rect.width / 2, self.screen_rect.height / 1.3),
                                                      text_size=24)

        self.char_selector = battleui.UnitSelector((self.screen_rect.width / 5, self.screen_rect.height / 1.5),
                                                   battle_select_image["char_select"], icon_scale=0.4)
        battleui.UIScroll(self.char_selector, self.char_selector.rect.topright)  # scroll bar for char pick

        bottom_height = self.screen_rect.height - image_list[0].get_height()
        self.select_button = menu.MenuButton(self.screen_scale, image_list,
                                             (self.screen_rect.width - image_list[0].get_width(), bottom_height),
                                             self.main_ui_updater, text="Select")
        self.start_button = menu.MenuButton(self.screen_scale, image_list,
                                            (self.screen_rect.width - image_list[0].get_width(), bottom_height),
                                            self.main_ui_updater, text="Start")
        self.map_back_button = menu.MenuButton(self.screen_scale, image_list,
                                               (self.screen_rect.width - (
                                                       self.screen_rect.width - image_list[0].get_width()),
                                                bottom_height),
                                               self.main_ui_updater, text="Back")
        self.char_back_button = menu.MenuButton(self.screen_scale, image_list,
                                                (self.screen_rect.width - (
                                                        self.screen_rect.width - image_list[0].get_width()),
                                                 bottom_height),
                                                self.main_ui_updater, text="Back")
        self.map_select_button = (self.select_button, self.map_back_button)
        self.team_select_button = (self.start_button, self.map_back_button)
        self.char_select_button = (self.start_button, self.char_back_button)

        self.map_list_box = menu.ListBox(self.screen_scale, (self.screen_rect.width / 25, self.screen_rect.height / 20),
                                         battle_select_image["name_list"])
        battleui.UIScroll(self.map_list_box, self.map_list_box.rect.topright)  # scroll bar for map list

        self.source_list_box = menu.ListBox(self.screen_scale, (0, 0),
                                            battle_select_image["top_box"])  # source list ui box
        battleui.UIScroll(self.source_list_box, self.source_list_box.rect.topright)  # scroll bar for source list
        self.map_option_box = menu.MapOptionBox(self.screen_scale, (self.screen_rect.width, 0),
                                                battle_select_image["top_box"],
                                                0)  # ui box for battle option during preparation screen

        self.enactment_tick_box = menu.TickBox(self.screen_scale, (self.map_option_box.rect.bottomright[0] / 1.2,
                                                                   self.map_option_box.rect.bottomright[1] / 4),
                                               battle_select_image["untick"], battle_select_image["tick"], "enactment")
        self.tick_box.add(self.enactment_tick_box)
        if self.enactment:
            self.enactment_tick_box.change_tick(True)

        self.current_map_row = 0
        self.current_map_select = 0
        self.current_source_row = 0
        self.char_select_row = 0

        self.source_name_list = [""]
        self.source_scale_text = [""]
        self.source_scale = [""]
        self.source_text = [""]

        self.unit_scale = 1

        # Unit and subunit editor button in game start menu

        self.unit_edit_button = menu.MenuButton(self.screen_scale, image_list,
                                                (self.screen_rect.width / 2,
                                                 self.screen_rect.height - (image_list[0].get_height() * 4)),
                                                self.main_ui_updater, text="Unit Editor")
        self.subunit_create_button = menu.MenuButton(self.screen_scale, image_list,
                                                     (self.screen_rect.width / 2,
                                                      self.screen_rect.height - (image_list[0].get_height() * 2.5)),
                                                     self.main_ui_updater, text="Troop Creator")
        self.editor_back_button = menu.MenuButton(self.screen_scale, image_list,
                                                  (self.screen_rect.width / 2,
                                                   self.screen_rect.height - image_list[0].get_height()),
                                                  self.main_ui_updater, text="Back")
        self.editor_button = (self.unit_edit_button, self.subunit_create_button, self.editor_back_button)

        # Option menu button
        option_menu_dict = make_option_menu(self.main_dir, self.screen_scale, self.screen_rect, self.screen_width,
                                            self.screen_height, image_list,
                                            {"master": self.master_volume, "music": self.music_volume,
                                             "voice": self.voice_volume, "effect": self.effect_volume},
                                            self.full_screen, self.play_troop_animation, self.main_ui_updater,
                                            battle_select_image)
        self.back_button = option_menu_dict["back_button"]
        self.default_button = option_menu_dict["default_button"]
        self.resolution_drop = option_menu_dict["resolution_drop"]
        self.resolution_bar = option_menu_dict["resolution_bar"]
        self.resolution_text = option_menu_dict["resolution_text"]
        self.option_menu_sliders = option_menu_dict["volume_sliders"]
        self.value_boxes = option_menu_dict["value_boxes"]
        self.volume_texts = option_menu_dict["volume_texts"]
        self.fullscreen_box = option_menu_dict["fullscreen_box"]
        self.fullscreen_text = option_menu_dict["fullscreen_text"]
        self.animation_box = option_menu_dict["animation_box"]
        self.animation_text = option_menu_dict["animation_text"]

        self.option_text_list = tuple([self.resolution_text, self.fullscreen_text, self.animation_text] + [value for value in self.volume_texts.values()])
        self.option_menu_button = (
        self.back_button, self.default_button, self.resolution_drop, self.fullscreen_box, self.animation_box)

        # Genre related stuff
        genre_folder = Path(os.path.join(main_dir, script_folder))  # Load genre list
        subdirectories = [x for x in genre_folder.iterdir() if x.is_dir()]
        subdirectories = [os.sep.join(os.path.normpath(folder_name).split(os.sep)[-1:]).capitalize() for folder_name in
                          subdirectories]
        if "__pycache__" in subdirectories:
            subdirectories.remove("__pycache__")
        subdirectories.remove("Common")
        self.genre_list = subdirectories  # map name list for map selection list

        box_image = load_image(self.main_dir, self.screen_scale, "genre_box.png", ("ui", "mainmenu_ui"))
        self.genre_change_box = menu.TextBox(self.screen_scale, box_image, (box_image.get_width(), 0),
                                             self.genre.capitalize())  # genre box ui

        # Profile box
        self.profile_name = self.profile_name
        profile_box_image = load_image(self.main_dir, self.screen_scale, "profile_box.png", ("ui", "mainmenu_ui"))
        self.profile_box = menu.TextBox(self.screen_scale, profile_box_image, (self.screen_width, 0),
                                        self.profile_name)  # profile name box at top right of screen at start_set menu screen

        # Load sound effect
        self.sound_effect_pool = self.create_sound_effect_pool()

        # Music player
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer = None
        if pygame.mixer:
            pygame.mixer.music.set_volume(self.master_volume)
            self.SONG_END = pygame.USEREVENT + 1
            self.music_list = glob.glob(self.main_dir + "/data/sound/music/*.ogg")
            pygame.mixer.music.load(self.music_list[0])
            pygame.mixer.music.play(-1)

        # Battle related stuffs
        subunit_ui_images = load_images(self.main_dir,
                                        subfolder=("ui", "subunit_ui"))  # no scaling when loaded for subunit sprite yet
        new_subunit_ui_images = {}
        for this_size in range(2, 11):  # create hp and stamina ring for 10 possible subunit sizes
            new_subunit_ui_images["health" + str(this_size)] = \
                {key: pygame.transform.smoothscale(value,
                                                   (value.get_width() * this_size, value.get_height() * this_size))
                 for key, value in subunit_ui_images.items() if "health" in key}
            new_subunit_ui_images["stamina" + str(this_size)] = \
                {key: pygame.transform.smoothscale(value,
                                                   (value.get_width() * this_size, value.get_height() * this_size))
                 for key, value in subunit_ui_images.items() if "stamina" in key}

        subunit_ui_images |= new_subunit_ui_images

        for stuff in subunit_ui_images:  # scale images with screen scale
            if type(subunit_ui_images[stuff]) != dict:
                subunit_ui_images[stuff] = pygame.transform.smoothscale(subunit_ui_images[stuff], (
                    subunit_ui_images[stuff].get_width() * self.screen_scale[0],
                    subunit_ui_images[stuff].get_height() * self.screen_scale[1]))
            else:
                for stuff2 in subunit_ui_images[stuff]:
                    subunit_ui_images[stuff][stuff2] = pygame.transform.smoothscale(subunit_ui_images[stuff][stuff2], (
                        subunit_ui_images[stuff][stuff2].get_width() * self.screen_scale[0],
                        subunit_ui_images[stuff][stuff2].get_height() * self.screen_scale[1]))

        subunit.Subunit.subunit_ui_images = subunit_ui_images

        self.fps_count = battleui.FPScount()  # FPS number counter
        self.battle_ui_updater.add(self.fps_count)

        battle_ui_image = load_images(self.main_dir, screen_scale=self.screen_scale, subfolder=("ui", "battle_ui"))
        battleui.SelectedSquad.image = battle_ui_image[
            "ui_subunit_clicked"]  # subunit border image always the last one

        self.inspect_selected_border = battleui.SelectedSquad((0, 0))  # yellow border on selected subunit in inspect ui

        # Battle ui
        self.status_images, self.role_images, self.trait_images, self.skill_images = make_icon_data(self.main_dir,
                                                                                                    self.screen_scale)

        self.mini_map = battleui.MiniMap((self.screen_rect.width, self.screen_rect.height), self.screen_scale)
        self.battle_ui_updater.add(self.mini_map)

        battle_icon_image = load_images(self.main_dir, screen_scale=self.screen_scale,
                                        subfolder=("ui", "battle_ui", "topbar_icon"))
        battle_ui_dict = make_battle_ui(battle_ui_image, battle_icon_image, team_colour, self.screen_rect.size)
        self.time_ui = battle_ui_dict["time_ui"]
        self.time_number = battle_ui_dict["time_number"]
        self.speed_number = battle_ui_dict["speed_number"]
        self.battle_scale_ui = battle_ui_dict["battle_scale_ui"]
        self.time_button = battle_ui_dict["time_button"]
        self.battle_ui_updater.add(self.time_ui, self.time_number, self.speed_number)
        self.unit_selector = battle_ui_dict["unit_selector"]
        self.unitstat_ui = battle_ui_dict["unitstat_ui"]
        self.unitstat_ui.unit_state_text = unit_state_text
        self.eight_wheel_ui = battle_ui_dict["eight_wheel_ui"]
        self.four_wheel_ui = battle_ui_dict["four_wheel_ui"]

        weather.Weather.wind_compass_images = {"wind_compass": battle_ui_image["wind_compass"],
                                               "wind_arrow": battle_ui_image["wind_arrow"]}

        # Unit editor
        editor_dict = make_editor_ui(self.main_dir, self.screen_scale, self.screen_rect,
                                     load_image(self.main_dir, self.screen_scale, "name_list.png",
                                                ("ui", "mapselect_ui")),
                                     load_base_button(self.main_dir, self.screen_scale), self.battle_scale_ui,
                                     team_colour,
                                     self.main_ui_updater)
        self.unit_preset_list_box = editor_dict["unit_listbox"]
        self.preset_select_border = editor_dict["preset_select_border"]
        self.editor_troop_list_box = editor_dict["troop_listbox"]
        self.unit_delete_button = editor_dict["unit_delete_button"]
        self.unit_save_button = editor_dict["unit_save_button"]
        self.popup_list_box = editor_dict["popup_listbox"]
        self.terrain_change_button = editor_dict["terrain_change_button"]
        self.feature_change_button = editor_dict["feature_change_button"]
        self.weather_change_button = editor_dict["weather_change_button"]
        self.filter_box = editor_dict["filter_box"]
        self.team_change_button = editor_dict["team_change_button"]
        self.slot_display_button = editor_dict["slot_display_button"]
        self.deploy_button = editor_dict["deploy_button"]
        self.test_button = editor_dict["test_button"]
        self.filter_tick_box = editor_dict["filter_tick_box"]
        self.warning_msg = editor_dict["warning_msg"]
        self.unit_build_slot = editor_dict["unit_build_slot"]
        self.unit_updater.remove(self.unit_build_slot)

        self.tick_box.add(*self.filter_tick_box)

        # user input popup ui
        input_ui_dict = make_input_box(self.main_dir, self.screen_scale, self.screen_rect,
                                       load_base_button(self.main_dir, self.screen_scale))
        self.input_ui = input_ui_dict["input_ui"]
        self.input_ok_button = input_ui_dict["input_ok_button"]
        self.input_cancel_button = input_ui_dict["input_cancel_button"]
        self.input_box = input_ui_dict["input_box"]
        self.confirm_ui = input_ui_dict["confirm_ui"]
        self.input_button = (self.input_ok_button, self.input_cancel_button)
        self.input_ui_popup = (self.input_ui, self.input_box, self.input_ok_button, self.input_cancel_button)
        self.confirm_ui_popup = (self.confirm_ui, self.input_ok_button, self.input_cancel_button)

        # Other ui in battle
        self.battle_done_box = battleui.BattleDone(self.screen_scale, (self.screen_width / 2, self.screen_height / 2),
                                                   battle_ui_image["end_box"], battle_ui_image["result_box"])
        self.battle_done_button = battleui.UIButton(battle_ui_image["end_button"], layer=19)
        self.battle_done_button.change_pos(
            (self.battle_done_box.pos[0], self.battle_done_box.box_image.get_height() * 0.8))

        drama.TextDrama.images = load_images(self.main_dir, screen_scale=self.screen_scale,
                                             subfolder=("ui", "popup_ui", "drama_text"))
        drama.TextDrama.screen_rect = self.screen_rect
        self.drama_text = drama.TextDrama(
            self.screen_scale)  # message at the top of screen that show up for important event

        event_log_dict = make_event_log(battle_ui_image, self.screen_rect)
        self.event_log = event_log_dict["event_log"]
        self.troop_log_button = event_log_dict["troop_log_button"]
        self.event_log_button = event_log_dict["event_log_button"]
        subunit.Subunit.event_log = self.event_log  # Assign event_log to subunit class to broadcast event to the log
        self.battle_ui_updater.add(self.event_log.scroll)

        esc_menu_dict = make_esc_menu(self.main_dir, self.screen_rect, self.screen_scale, self.master_volume)
        self.battle_menu = esc_menu_dict["battle_menu"]
        self.battle_menu_button = esc_menu_dict["battle_menu_button"]
        self.esc_option_menu_button = esc_menu_dict["esc_option_menu_button"]
        self.esc_slider_menu = esc_menu_dict["esc_slider_menu"]
        self.esc_value_boxes = esc_menu_dict["esc_value_boxes"]

        popup_ui_dict = make_popup_ui(self.main_dir, self.screen_rect, self.screen_scale, battle_ui_image)
        self.troop_card_ui = popup_ui_dict["troop_card_ui"]
        self.troop_card_button = popup_ui_dict["troop_card_button"]
        self.terrain_check = popup_ui_dict["terrain_check"]
        self.single_text_popup = popup_ui_dict["single_text_popup"]
        self.terrain_check = popup_ui_dict["terrain_check"]
        self.char_popup = popup_ui_dict["char_popup"]
        self.ui_updater.add(self.troop_card_ui)
        self.button_ui.add(self.troop_card_button)

        self.encyclopedia, self.lore_name_list, self.filter_tag_list, self.lore_button_ui, self.page_button = make_lorebook(
            self, self.main_dir, self.screen_scale, self.screen_rect)

        self.encyclopedia_stuff = (self.encyclopedia, self.lore_name_list, self.filter_tag_list,
                                   self.lore_name_list.scroll, self.filter_tag_list.scroll, *self.lore_button_ui)

        self.subunit_inspect_sprite_size = (62 * self.screen_scale[0], 62 * self.screen_scale[1])

        self.battle_game = battle.Battle(self, self.window_style)
        self.battle_game.generate_unit = self.generate_unit
        self.battle_game.leader_position_check = self.leader_position_check

        self.change_game_genre(self.genre)

        self.troop_card_ui.weapon_list = self.troop_data.weapon_list
        self.troop_card_ui.armour_list = self.troop_data.armour_list
        self.troop_card_ui.terrain_list = self.battle_base_map.terrain_list
        self.troop_card_ui.feature_list = self.battle_feature_map.feature_list  # add terrain feature list name to subunit card

        subunit.Subunit.battle = self.battle_game
        leader.Leader.battle = self.battle_game

        start_pos = [(self.screen_rect.width / 2) - (self.subunit_inspect_sprite_size[0] * 5),
                     (self.screen_rect.height / 2) - (self.subunit_inspect_sprite_size[1] * 4)]
        self.create_unit_slot(0, 0, range(0, 64), start_pos)  # make player custom unit slot

        # Starting script
        self.main_ui_updater.remove(*self.menu_button)  # remove all button from drawing
        self.menu_button.remove(
            *self.menu_button)  # remove all button at the start and add later depending on menu_state
        self.menu_button.add(*self.mainmenu_button)  # add only game start menu button back

        self.start_menu_ui_only = *self.menu_button, self.profile_box, self.genre_change_box  # ui that only appear at the start menu
        self.main_ui_updater.add(*self.start_menu_ui_only)
        self.menu_state = "main_menu"
        self.input_popup = (None, None)  # popup for text input state
        self.choosing_faction = True  # swap list between faction and subunit, always start with choose faction first as true

        self.loading_screen("end")

        self.run()

    def change_ruleset(self):
        self.troop_data, self.leader_data, self.faction_data = make_faction_troop_leader_data(self.main_dir,
                                                                                              self.screen_scale,
                                                                                              self.ruleset_folder,
                                                                                              self.language)

        self.battle_map_data = datamap.BattleMapData(self.main_dir, self.screen_scale, self.ruleset, self.language)

        self.battle_game.battle_map_data = self.battle_map_data
        self.battle_game.weather_data = self.battle_map_data.weather_data
        self.battle_game.weather_matter_images = self.battle_map_data.weather_matter_images
        self.battle_game.weather_effect_images = self.battle_map_data.weather_effect_images
        self.battle_game.day_effect_images = self.battle_map_data.day_effect_images
        self.battle_game.weather_list = self.battle_map_data.weather_list
        self.battle_game.feature_mod = self.battle_map_data.feature_mod

        subunit.Subunit.troop_data = self.troop_data
        subunit.Subunit.leader_data = self.leader_data
        subunit.Subunit.troop_sprite_list = self.troop_data.troop_sprite_list
        subunit.Subunit.leader_sprite_list = self.leader_data.leader_sprite_list
        subunit.Subunit.status_list = self.troop_data.status_list
        subunit.Subunit.subunit_state = self.subunit_state

        self.convert_formation_preset()
        unit.Unit.unit_formation_list = self.troop_data.unit_formation_list

        self.preset_map_list, self.preset_map_folder, self.custom_map_list, \
        self.custom_map_folder = make_battle_list_data(self.main_dir, self.ruleset_folder, self.language)

        self.troop_animation = datasprite.TroopAnimationData(self.main_dir,
                                                             [self.troop_data.race_list[key]["Name"] for key in
                                                              self.troop_data.race_list])
        self.generic_animation_pool = self.troop_animation.generic_animation_pool  # animation data pool
        self.gen_body_sprite_pool = self.troop_animation.gen_body_sprite_pool  # body sprite pool
        self.gen_weapon_sprite_pool = self.troop_animation.gen_weapon_sprite_pool  # weapon sprite pool
        self.gen_armour_sprite_pool = self.troop_animation.gen_armour_sprite_pool  # armour sprite pool
        self.weapon_joint_list = self.troop_animation.weapon_joint_list  # weapon joint data
        self.colour_list = self.troop_animation.colour_list  # skin colour list

        self.effect_sprite_pool = self.troop_animation.effect_sprite_pool
        self.effect_animation_pool = self.troop_animation.effect_animation_pool

        self.command_ui.weapon_sprite_pool = self.gen_weapon_sprite_pool

        # flip (covert for ingame angle)
        bullet_sprite_pool = {}
        for key, value in self.effect_sprite_pool.items():
            bullet_sprite_pool[key] = {}
            for key2, value2 in value.items():
                bullet_sprite_pool[key][key2] = {}
                for key3, value3 in value2.items():
                    image = pygame.transform.flip(value3, False, True)
                    bullet_sprite_pool[key][key2][key3] = image
        bullet_weapon_sprite_pool = {}
        for key, value in self.gen_weapon_sprite_pool.items():
            bullet_weapon_sprite_pool[key] = {}
            for key2, value2 in value.items():
                bullet_weapon_sprite_pool[key][key2] = {}
                for key3, value3 in value2.items():
                    bullet_weapon_sprite_pool[key][key2][key3] = {}
                    for key4, value4 in value3.items():
                        image = pygame.transform.flip(value4, False, True)
                        image = pygame.transform.scale(image, (int(image.get_width() / 2), int(image.get_height() / 2)))
                        bullet_weapon_sprite_pool[key][key2][key3][key4] = image

        damagesprite.DamageSprite.bullet_sprite_pool = bullet_sprite_pool
        damagesprite.DamageSprite.bullet_weapon_sprite_pool = bullet_weapon_sprite_pool
        damagesprite.DamageSprite.effect_sprite_pool = self.effect_sprite_pool
        damagesprite.DamageSprite.effect_animation_pool = self.effect_animation_pool

        # Encyclopedia
        lorebook.Lorebook.concept_stat = csv_read(self.main_dir, "concept_stat.csv",
                                                  ("data", "ruleset", self.ruleset_folder, "lore"), header_key=True)
        lorebook.Lorebook.concept_lore = csv_read(self.main_dir, "concept_lore" + "_" + self.language + ".csv",
                                                  ("data", "ruleset", self.ruleset_folder, "lore"))
        lorebook.Lorebook.history_stat = csv_read(self.main_dir, "history_stat.csv",
                                                  ("data", "ruleset", self.ruleset_folder, "lore"), header_key=True)
        lorebook.Lorebook.history_lore = csv_read(self.main_dir, "history_lore" + "_" + self.language + ".csv",
                                                  ("data", "ruleset", self.ruleset_folder, "lore"))

        lorebook.Lorebook.faction_data = self.faction_data
        lorebook.Lorebook.troop_data = self.troop_data
        lorebook.Lorebook.leader_data = self.leader_data
        lorebook.Lorebook.battle_map_data = self.battle_map_data
        lorebook.Lorebook.screen_rect = self.screen_rect
        lorebook.Lorebook.unit_state_text = self.unit_state_text

        self.encyclopedia.change_ruleset()

        # Error log for selected genre, ruleset
        self.error_log.write("Ruleset: " + self.ruleset_list[self.ruleset][0] + ", Mode: " + self.genre)

        self.preview_leader = (leader.Leader(1, 0, 0, None, self.leader_data, layer=11),
                               leader.Leader(1, 0, 1, None, self.leader_data, layer=11),
                               leader.Leader(1, 0, 2, None, self.leader_data, layer=11),
                               leader.Leader(1, 0, 3, None, self.leader_data,
                                             layer=11))  # list of preview leader for unit editor
        for this_leader in self.preview_leader:
            self.leader_updater.remove(this_leader)
        self.battle_game.preview_leader = self.preview_leader
        self.leader_updater.remove(*self.preview_leader)  # remove preview leader from updater since not use in battle

    def change_game_genre(self, genre):
        """Add new genre module here"""

        def import_genre_module(directory, old_genre, new_genre, change_object, folder_list):
            """
            Import module from specific genre folder
            :param directory: Directory path to game file
            :param old_genre: Old genre folder name
            :param new_genre: Genre folder name
            :param change_object: Object that require the module as class function
            :param folder_list: List of folder name to import module
            """

            def empty(*args):  # empty method for genre that does not use already existing method in new selected genre
                pass

            for folder in folder_list:
                try:
                    for this_file in os.scandir(Path(directory + new_genre + "/" + folder)):
                        if this_file.is_file():
                            if ".py" in this_file.name:
                                file_name = this_file.name[:-3]
                            elif ".pyc" in this_file.name:
                                file_name = this_file.name[:-4]

                            exec(f"from " + script_folder + "." + new_genre + "." +
                                 folder.replace("/", ".") + " import " + file_name)
                            try:
                                exec(
                                    f"" + change_object.lower() + "." + change_object + "." +
                                    file_name + " = " + file_name + "." + file_name)
                            except NameError:
                                exec(
                                    f"" + change_object + "." + file_name + " = " + file_name + "." + file_name)

                except FileNotFoundError:
                    pass

                # Check whether the old genre method not existed in the new one, replace with empty method
                if old_genre != new_genre:
                    try:
                        new_folder = [this_file.name for this_file in
                                      os.scandir(Path(directory + new_genre + "/" + folder))]
                    except FileNotFoundError:
                        new_folder = ()
                    try:
                        for this_file in os.scandir(Path(directory + old_genre + "/" + folder)):
                            if this_file.is_file():
                                if this_file.name not in new_folder:
                                    if ".pyc" in this_file.name:
                                        file_name = this_file.name[:-4]
                                    elif ".py" in this_file.name:
                                        file_name = this_file.name[:-3]
                                    try:
                                        exec(
                                            f"" + change_object.lower() + "." + change_object + "." +
                                            file_name + " = list({empty})[0]")
                                    except NameError:
                                        exec(
                                            f"" + change_object + "." + file_name + " = list({empty})[0]")

                    except FileNotFoundError:
                        pass

        if type(genre) == int:
            new_genre = self.genre_list[genre].lower()
        else:
            new_genre = genre.lower()

        import_genre_module(self.script_dir, self.genre, new_genre, "Game", ("game",))

        genre_setting = importlib.import_module("gamescript." + new_genre + ".genre_setting")

        # Change genre for other objects
        import_genre_module(self.script_dir, self.genre, new_genre, "Subunit", ("subunit",))
        import_genre_module(self.script_dir, self.genre, new_genre, "Unit", ("unit",))
        import_genre_module(self.script_dir, self.genre, new_genre, "Battle", ("battle", "ui"))
        import_genre_module(self.script_dir, self.genre, new_genre, "Leader", ("leader",))

        for object_key in genre_setting.object_variable:  # add genre-specific variables to appropriate object
            for key, value in genre_setting.object_variable[object_key].items():
                if "object" in object_key[1]:
                    how = object_key[0]
                    if "self" in object_key[1]:
                        how = "self." + object_key[0]
                elif object_key[1] == "class":
                    how = object_key[0] + "." + object_key[0].capitalize()
                if type(value) == str:  # string type value
                    exec(f"" + how + "." + key + " = list({value})[0]")
                else:  # any other type value
                    exec(f"" + how + "." + key + " = " + str(value))

        self.genre = new_genre
        self.battle_game.genre = self.genre

        if self.char_select:  # genre with character select screen
            self.team_select_button = (self.map_select_button, self.map_back_button)
        else:
            self.team_select_button = (self.start_button, self.map_back_button)

        self.genre_change_box.change_text(self.genre.capitalize())
        edit_config("USER", "genre", self.genre, "configuration.ini", self.config)

        genre_battle_ui_image = load_images(self.main_dir, screen_scale=self.screen_scale,
                                            subfolder=(self.genre, "ui", "battle_ui"))

        genre_icon_image = load_images(self.main_dir, screen_scale=self.screen_scale,
                                       subfolder=(self.genre, "ui", "battle_ui", "commandbar_icon"))

        self.genre_ui_dict = make_genre_specific_ui(self.main_dir, self.screen_scale, self.genre, self.command_ui_type)
        self.command_ui = self.genre_ui_dict["command_ui"]
        self.ui_updater.add(self.command_ui)
        leader.Leader.leader_pos = self.command_ui.leader_pos

        self.col_split_button = self.genre_ui_dict["col_split_button"]
        self.row_split_button = self.genre_ui_dict["row_split_button"]
        self.decimation_button = self.genre_ui_dict["decimation_button"]
        self.inspect_button = self.genre_ui_dict["inspect_button"]

        self.inspect_ui = self.genre_ui_dict["inspect_ui"]
        self.ui_updater.add(self.inspect_ui)

        # Behaviour button that once click switch to other mode for subunit behaviour
        self.behaviour_switch_button = self.genre_ui_dict["behaviour_switch_button"]

        self.battle_game.command_ui = self.command_ui
        self.battle_game.col_split_button = self.col_split_button
        self.battle_game.row_split_button = self.row_split_button
        self.battle_game.inspect_button = self.inspect_button
        self.battle_game.inspect_ui = self.inspect_ui
        self.battle_game.behaviour_switch_button = self.behaviour_switch_button
        self.battle_game.max_camera_zoom_image_scale = self.battle_game.max_camera_zoom + 1

        if self.command_ui.ui_type == "command":
            self.command_ui.load_sprite(genre_battle_ui_image["command_box"], genre_icon_image)
        else:
            self.command_ui.load_sprite(None, None)

        self.genre_ui_dict["col_split_button"].image = genre_battle_ui_image["colsplit_button"]
        self.genre_ui_dict["row_split_button"].image = genre_battle_ui_image["rowsplit_button"]

        self.genre_ui_dict["decimation_button"].image = genre_battle_ui_image["decimation"]

        # Unit inspect information ui
        self.genre_ui_dict["inspect_button"].image = genre_battle_ui_image["army_inspect_button"]

        self.genre_ui_dict["inspect_ui"].image = genre_battle_ui_image["army_inspect"]

        skill_condition_button = [genre_battle_ui_image["skillcond_0"], genre_battle_ui_image["skillcond_1"],
                                  genre_battle_ui_image["skillcond_2"], genre_battle_ui_image["skillcond_3"]]
        shoot_condition_button = [genre_battle_ui_image["fire_0"], genre_battle_ui_image["fire_1"]]
        behaviour_button = [genre_battle_ui_image["hold_0"], genre_battle_ui_image["hold_1"],
                            genre_battle_ui_image["hold_2"]]
        range_condition_button = [genre_battle_ui_image["minrange_0"], genre_battle_ui_image["minrange_1"]]
        arc_condition_button = [genre_battle_ui_image["arc_0"], genre_battle_ui_image["arc_1"],
                                genre_battle_ui_image["arc_2"]]
        run_condition_button = [genre_battle_ui_image["runtoggle_0"], genre_battle_ui_image["runtoggle_1"]]
        melee_condition_button = [genre_battle_ui_image["meleeform_0"], genre_battle_ui_image["meleeform_1"],
                                  genre_battle_ui_image["meleeform_2"]]
        button_list = (skill_condition_button, shoot_condition_button, behaviour_button, range_condition_button,
                       arc_condition_button, run_condition_button, melee_condition_button)
        for index, button_image in enumerate(button_list):
            self.genre_ui_dict["behaviour_switch_button"][index].change_genre(button_image)

        self.change_ruleset()

        # Background image
        try:
            bgd_tile = load_image(self.main_dir, self.screen_scale, self.genre + ".png", ("ui", "mainmenu_ui"))
        except FileNotFoundError:
            bgd_tile = load_image(self.main_dir, self.screen_scale, "default.png", ("ui", "mainmenu_ui"))
        bgd_tile = pygame.transform.scale(bgd_tile, self.screen_rect.size)
        self.background = pygame.Surface(self.screen_rect.size)
        self.background.blit(bgd_tile, (0, 0))

    def game_intro(self, screen, clock, intro):
        timer = 0
        # The record is truthful, unbiased, correct and approved by appointed certified historians.
        # quote = ["Those attacker fail to learn from the mistakes of their predecessors are destined to repeat them. George Santayana",
        # "It is more important to out-think your enemy, than to out-fight him, Sun Tzu"]
        while intro:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
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

        pygame.display.set_caption(
            version_name + " " + self.genre.capitalize())  # set the self name on program border/tab

    def run(self):
        while True:
            # Get user input
            self.dt = self.clock.get_time() / 1000  # dt before game_speed
            mouse_left_up = False
            mouse_left_down = False
            mouse_right_up = False
            mouse_scroll_down = False
            mouse_scroll_up = False
            esc_press = False
            input_esc = False
            key_press = pygame.key.get_pressed()
            if pygame.mouse.get_pressed()[0]:  # Hold left click
                mouse_left_down = True
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # left click
                        mouse_left_up = True
                    elif event.button == 3:
                        mouse_right_up = True
                    elif event.button == 4:  # Mouse scroll down
                        mouse_scroll_up = True

                    elif event.button == 5:  # Mouse scroll up
                        mouse_scroll_down = True

                elif event.type == KEYDOWN:
                    if self.input_popup[0] is not None:  # event update to input box
                        if event.key == K_ESCAPE:
                            input_esc = True
                        elif self.input_popup[0] == "text_input":
                            self.input_box.player_input(event, key_press)
                            self.text_delay = 0.1
                    else:
                        if event.key == K_ESCAPE:
                            esc_press = True

                if event.type == QUIT or self.quit_button.event or (esc_press and self.menu_state == "main_menu"):
                    self.quit_button.event = False
                    self.input_popup = ("confirm_input", "quit")
                    self.confirm_ui.change_instruction("Quit Game?")
                    self.main_ui_updater.add(*self.confirm_ui_popup)

            self.mouse_pos = pygame.mouse.get_pos()
            self.cursor.update(self.mouse_pos)
            # ^ End user input

            self.screen.blit(self.background, (0, 0))  # blit background over instead of clear() to reset screen

            if self.input_popup[
                0] is not None:  # currently, have input text pop up on screen, stop everything else until done
                for button in self.input_button:
                    button.update(self.mouse_pos, mouse_left_up, mouse_left_down)

                if self.input_ok_button.event or key_press[pygame.K_RETURN] or key_press[pygame.K_KP_ENTER]:
                    self.input_ok_button.event = False

                    if self.input_popup[1] == "profile_name":
                        self.profile_name = self.input_box.text
                        self.profile_box.change_text(self.profile_name)

                        edit_config("USER", "player_name", self.profile_name, "configuration.ini", self.config)

                    elif self.input_popup[1] == "quit":
                        pygame.time.wait(1000)
                        if pygame.mixer:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.unload()
                        pygame.quit()
                        sys.exit()

                    self.input_box.text_start("")
                    self.input_popup = (None, None)
                    self.main_ui_updater.remove(*self.input_ui_popup)

                elif self.input_cancel_button.event or input_esc:
                    self.input_cancel_button.event = False
                    self.input_box.text_start("")
                    self.input_popup = (None, None)
                    self.main_ui_updater.remove(*self.input_ui_popup, *self.confirm_ui_popup)

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

                elif self.menu_state == "preset_map" or self.menu_state == "custom_map":
                    self.menu_map_select(mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press)

                elif self.menu_state == "team_select":
                    self.menu_team_select(mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press)

                elif self.menu_state == "char_select":
                    self.menu_char_select(mouse_left_up, mouse_left_down, mouse_scroll_up,
                                          mouse_scroll_down, esc_press)

                elif self.menu_state == "game_creator":
                    self.menu_game_editor(mouse_left_up, mouse_left_down, mouse_scroll_up,
                                          mouse_scroll_down, esc_press)

                elif self.menu_state == "option":
                    self.menu_option(mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press)

                elif self.menu_state == "encyclopedia":
                    command = self.lorebook_process(self.main_ui_updater, mouse_left_up, mouse_left_down,
                                                    mouse_scroll_up, mouse_scroll_down, esc_press)
                    if esc_press or command == "exit":
                        self.menu_state = "main_menu"  # change menu back to default 0

            self.main_ui_updater.draw(self.screen)
            pygame.display.update()
            self.clock.tick(60)
