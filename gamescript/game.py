import configparser
import glob
import os.path
import sys
from pathlib import Path

import pygame
import pygame.freetype
import screeninfo
from gamescript import battlemap, weather, battleui, menu, damagesprite, effectsprite, battle, subunit, datasprite, \
    datamap, lorebook, drama, popup

from gamescript.common import utility
from gamescript.common.battle import setup_battle_troop
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

morale_state_text = {0: "Broken", 1: "Fleeing", 2: "Breaking", 3: "Poor", 4: "Wavering", 5: "Balanced",
                     6: "Steady", 7: "Fine", 8: "Confident", 9: "Eager", 10: "Ready", 11: "Merry", 12: "Elated",
                     13: "Ecstatic",
                     14: "Inspired", 15: "Fervent"}  # unit morale state name

stamina_state_text = {0: "Collapse", 1: "Exhausted", 2: "Severed", 3: "Very Tired", 4: "Tired", 5: "Winded",
                      6: "Moderate",
                      7: "Alert", 8: "Warmed Up", 9: "Active", 10: "Fresh"}  # unit stamina state name

script_folder = "gamescript"


class Game:
    empty_method = utility.empty_method

    # import from common.game
    back_mainmenu = empty_method
    change_battle_source = empty_method
    change_to_source_selection_menu = empty_method
    change_sound_volume = empty_method
    create_preview_map = empty_method
    create_sound_effect_pool = empty_method
    create_team_coa = empty_method
    create_troop_sprite = empty_method
    create_troop_sprite_pool = empty_method
    loading_screen = empty_method
    menu_char_select = empty_method
    menu_main = empty_method
    menu_map_select = empty_method
    menu_option = empty_method
    menu_team_select = empty_method
    read_battle_source = empty_method
    read_selected_map_data = empty_method
    start_battle = empty_method

    popup_list_open = utility.popup_list_open
    lorebook_process = lorebook.lorebook_process
    setup_battle_troop = setup_battle_troop.setup_battle_troop

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
    troop_sprite_size = (200, 200)
    start_zoom_mode = "Follow"

    team_colour = {0: (50, 50, 50), 1: (0, 0, 200), 2: (200, 0, 0), 3: (200, 200, 0), 4: (0, 200, 0), 5: (200, 0, 200),
                   6: (140, 90, 40), 7: (100, 170, 170), 8: (230, 120, 0), 9: (230, 60, 110), 10: (130, 120, 200)}
    selected_team_colour = {0: (200, 200, 200), 1: (150, 150, 255), 2: (255, 40, 40), 3: (255, 255, 150),
                            4: (150, 255, 150), 5: (255, 150, 255), 6: (200, 140, 70), 7: (160, 200, 200),
                            8: (255, 150, 45), 9: (230, 140, 160), 10: (200, 190, 230)}

    def __init__(self, main_dir, error_log):
        pygame.init()  # Initialize pygame

        pygame.mouse.set_visible(False)  # set mouse as not visible, use in-game mouse sprite

        self.main_dir = main_dir
        self.error_log = error_log

        lorebook.Lorebook.main_dir = self.main_dir

        # Read config file
        config = configparser.ConfigParser()
        try:
            config.read_file(open(os.path.join(self.main_dir, "configuration.ini")))  # read config file
        except FileNotFoundError:  # Create config file if not found with the default
            config = configparser.ConfigParser()

            screen = screeninfo.get_monitors()[0]
            screen_width = int(screen.width)
            screen_height = int(screen.height)

            config["DEFAULT"] = {"screen_width": screen_width, "screen_height": screen_height, "full_screen": "0",
                                 "player_Name": "Noname", "master_volume": "100.0", "music_volume": "0.0",
                                 "voice_volume": "100.0", "effect_volume": "100.0", "max_fps": "60", "ruleset": "1",
                                 "language": "en"}
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
        self.language = str(self.config["USER"]["language"])
        self.ruleset = 1  # for now default historical ruleset only

        # Set the display mode
        self.screen_rect = Rect(0, 0, self.screen_width, self.screen_height)
        self.screen_scale = (self.screen_rect.width / 1920, self.screen_rect.height / 1080)

        self.window_style = 0
        if self.full_screen == 1:
            self.window_style = pygame.FULLSCREEN
        self.best_depth = pygame.display.mode_ok(self.screen_rect.size, self.window_style, 32)
        self.screen = pygame.display.set_mode(self.screen_rect.size, self.window_style | pygame.RESIZABLE,
                                              self.best_depth)

        subunit.Subunit.screen_scale = self.screen_scale
        subunit.Subunit.team_colour = self.team_colour
        menu.MapPreview.colour = self.team_colour
        menu.MapPreview.selected_colour = self.selected_team_colour
        damagesprite.DamageSprite.screen_scale = self.screen_scale
        battlemap.BeautifulMap.team_colour = self.team_colour
        battlemap.BeautifulMap.selected_team_colour = self.selected_team_colour

        self.clock = pygame.time.Clock()

        self.loading = load_image(self.main_dir, self.screen_scale, "loading.png", ("ui", "mainmenu_ui"))
        self.loading = pygame.transform.scale(self.loading, self.screen_rect.size)

        self.ruleset_list = csv_read(self.main_dir, "ruleset_list.csv", ("data", "ruleset"))  # get ruleset list
        self.ruleset_folder = str(self.ruleset_list[self.ruleset][1]).strip("/")

        self.map_type = ""
        self.map_source = 0  # current selected map source
        self.team_selected = 1
        self.char_selected = 0
        self.current_popup_row = 0
        self.team_pos = {}  # for saving preview map subunit pos
        self.camp_pos = {}  # for saving preview map camp pos

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

        # battle object group
        self.battle_camera = pygame.sprite.LayeredUpdates()  # layer drawer self camera, all image pos should be based on the map not screen
        self.battle_ui_updater = pygame.sprite.LayeredUpdates()  # this is layer drawer for ui, all image pos should be based on the screen

        self.subunit_updater = pygame.sprite.Group()  # updater for subunit objects
        self.ui_updater = pygame.sprite.Group()  # updater for ui objects
        self.weather_updater = pygame.sprite.Group()  # updater for weather objects
        self.effect_updater = pygame.sprite.Group()  # updater for effect objects (e.g. range melee_attack sprite)

        self.all_subunits = pygame.sprite.Group()

        self.preview_char = pygame.sprite.Group()  # group for char list in char select screen

        self.sprite_indicator = pygame.sprite.Group()

        self.shoot_lines = pygame.sprite.Group()
        self.button_ui = pygame.sprite.Group()  # ui button group in battle

        self.skill_icon = pygame.sprite.Group()  # skill and trait icon objects
        self.effect_icon = pygame.sprite.Group()  # status effect icon objects

        self.battle_menu_button = pygame.sprite.Group()  # buttons for esc menu object group
        self.esc_option_menu_button = pygame.sprite.Group()  # buttons for esc menu option object group
        self.slider_menu = pygame.sprite.Group()  # volume slider in esc option menu

        self.char_icon = pygame.sprite.Group()  # Character icon object group in selector ui
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

        # battle containers
        battleui.SkillCardIcon.containers = self.skill_icon, self.battle_ui_updater
        battleui.EffectCardIcon.containers = self.effect_icon, self.battle_ui_updater
        battleui.CharIcon.containers = self.char_icon, self.main_ui_updater, self.battle_ui_updater
        battleui.SpriteIndicator.containers = self.effect_updater, self.battle_camera
        battleui.AimTarget.containers = self.shoot_lines, self.battle_camera

        damagesprite.DamageSprite.containers = self.effect_updater, self.battle_camera
        effectsprite.EffectSprite.containers = self.effect_updater, self.battle_camera

        menu.EscButton.containers = self.battle_menu_button, self.esc_option_menu_button

        weather.MatterSprite.containers = self.weather_matter, self.battle_ui_updater, self.weather_updater
        weather.SpecialEffect.containers = self.weather_effect, self.battle_ui_updater, self.weather_updater

        subunit.Subunit.containers = self.subunit_updater, self.all_subunits, self.battle_camera

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
        self.lore_button = menu.MenuButton(self.screen_scale, image_list,
                                           (self.screen_rect.width / 2,
                                            self.screen_rect.height - (image_list[0].get_height() * 5.5)),
                                           self.main_ui_updater, text="Encyclopedia")
        self.option_button = menu.MenuButton(self.screen_scale, image_list,
                                             (self.screen_rect.width / 2,
                                              self.screen_rect.height - (image_list[0].get_height() * 4)),
                                             self.main_ui_updater, text="Option")
        self.quit_button = menu.MenuButton(self.screen_scale, image_list,
                                           (self.screen_rect.width / 2,
                                            self.screen_rect.height - (image_list[0].get_height() * 2.5)),
                                           self.main_ui_updater, text="Quit")
        self.mainmenu_button = (self.preset_map_button, self.custom_map_button, self.lore_button,
                                self.option_button, self.quit_button)

        # Battle map
        self.battle_base_map = battlemap.BaseMap(self.main_dir)  # create base terrain map
        self.battle_feature_map = battlemap.FeatureMap(self.main_dir)  # create terrain feature map
        self.battle_height_map = battlemap.HeightMap()  # create height map
        self.battle_map = battlemap.BeautifulMap(self.main_dir, self.screen_scale, self.battle_height_map)
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
                                        (self.screen_rect.width / 2, self.screen_rect.height / 3))

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
        self.team_select_button = (self.select_button, self.map_back_button)
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
        self.observe_mode_tick_box = menu.TickBox(self.screen_scale,
                                                  (self.map_option_box.rect.bottomright[0] / 1.2,
                                                   self.map_option_box.rect.bottomright[1] / 4),
                                                  battle_select_image["untick"], battle_select_image["tick"], "observe")

        self.current_map_row = 0
        self.current_map_select = 0
        self.current_source_row = 0
        self.char_select_row = 0

        self.enactment = False

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
                                            self.full_screen, self.main_ui_updater,
                                            battle_select_image=battle_select_image)
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

        self.option_text_list = tuple(
            [self.resolution_text, self.fullscreen_text] + [value for value in
                                                                                 self.volume_texts.values()])
        self.option_menu_button = (
            self.back_button, self.default_button, self.resolution_drop, self.fullscreen_box)

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
            pygame.mixer.set_num_channels(1000)
            pygame.mixer.music.set_volume(self.master_volume)
            self.SONG_END = pygame.USEREVENT + 1
            self.music_list = glob.glob(self.main_dir + "/data/sound/music/*.ogg")
            pygame.mixer.music.load(self.music_list[0])
            pygame.mixer.music.play(-1)

        # Battle related stuffs
        subunit_ui_images = load_images(self.main_dir,
                                        subfolder=("ui", "subunit_ui"))  # no scaling when loaded for subunit sprite yet

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

        # Battle ui
        self.status_images, self.role_images, self.trait_images, self.skill_images = make_icon_data(self.main_dir,
                                                                                                    self.screen_scale)

        self.mini_map = battleui.MiniMap((self.screen_rect.width, self.screen_rect.height), self.screen_scale)
        self.battle_ui_updater.add(self.mini_map)

        battle_icon_image = load_images(self.main_dir, screen_scale=self.screen_scale,
                                        subfolder=("ui", "battle_ui", "topbar_icon"))
        battle_ui_dict = make_battle_ui(battle_ui_image, battle_icon_image, self.team_colour,
                                        self.screen_rect.size, self.screen_scale)
        self.time_ui = battle_ui_dict["time_ui"]
        self.time_number = battle_ui_dict["time_number"]
        self.battle_scale_ui = battle_ui_dict["battle_scale_ui"]
        self.battle_ui_updater.add(self.time_ui, self.time_number)
        self.wheel_ui = battle_ui_dict["wheel_ui"]
        self.command_ui = battle_ui_dict["command_ui"]

        # 4 Skill icons near hero ui, TODO change key later when can set keybind
        battleui.SkillCardIcon(self.screen_scale, self.skill_images["0"], (self.command_ui.image.get_width() +
                                                        self.skill_images["0"].get_width() / 2, 0), "Q")
        battleui.SkillCardIcon(self.screen_scale, self.skill_images["0"], (self.command_ui.image.get_width() +
                                                        self.skill_images["0"].get_width() * 2, 0), "E")
        battleui.SkillCardIcon(self.screen_scale, self.skill_images["0"], (self.command_ui.image.get_width() +
                                                        self.skill_images["0"].get_width() * 3.5, 0), "R")
        battleui.SkillCardIcon(self.screen_scale, self.skill_images["0"], (self.command_ui.image.get_width() +
                                                        self.skill_images["0"].get_width() * 5, 0), "T")

        weather.Weather.wind_compass_images = {"wind_compass": battle_ui_image["wind_compass"],
                                               "wind_arrow": battle_ui_image["wind_arrow"]}

        empty_aim = pygame.Surface((0, 0))
        battleui.AimTarget.aim_images = {0: battle_ui_image["aim_0"], 1: battle_ui_image["aim_1"],
                                         2: battle_ui_image["aim_2"], 3: empty_aim}

        box_image = load_image(main_dir, self.screen_scale, "unit_presetbox.png", ("ui", "mainmenu_ui"))
        self.popup_list_box = menu.ListBox(self.screen_scale, (0, 0), box_image,
                                           15)  # popup box need to be in higher layer
        battleui.UIScroll(self.popup_list_box, self.popup_list_box.rect.topright)

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
            (self.battle_done_box.pos[0], self.battle_done_box.box_image.get_height() * 2))

        drama.TextDrama.images = load_images(self.main_dir, screen_scale=self.screen_scale,
                                             subfolder=("ui", "popup_ui", "drama_text"))
        drama.TextDrama.screen_rect = self.screen_rect
        self.drama_text = drama.TextDrama(
            self.screen_scale)  # message at the top of screen that show up for important event

        self.event_log = battleui.EventLog(battle_ui_image["event_log"], (0, self.screen_rect.height))
        battleui.UIScroll(self.event_log, self.event_log.rect.topright)  # event log scroll
        subunit.Subunit.event_log = self.event_log  # Assign event_log to subunit class to broadcast event to the log
        self.battle_ui_updater.add(self.event_log.scroll)

        esc_menu_dict = make_esc_menu(self.main_dir, self.screen_rect, self.screen_scale, self.master_volume)
        self.battle_menu = esc_menu_dict["battle_menu"]
        self.battle_menu_button = esc_menu_dict["battle_menu_button"]
        self.esc_option_menu_button = esc_menu_dict["esc_option_menu_button"]
        self.esc_slider_menu = esc_menu_dict["esc_slider_menu"]
        self.esc_value_boxes = esc_menu_dict["esc_value_boxes"]

        self.single_text_popup = popup.TextPopup(self.screen_scale,
                                                 self.screen_rect.size)  # popup box that show name when mouse over

        self.encyclopedia, self.lore_name_list, self.filter_tag_list, self.lore_button_ui, self.page_button = make_lorebook(
            self, self.main_dir, self.screen_scale, self.screen_rect)

        self.encyclopedia_stuff = (self.encyclopedia, self.lore_name_list, self.filter_tag_list,
                                   self.lore_name_list.scroll, self.filter_tag_list.scroll, *self.lore_button_ui)

        self.battle = battle.Battle(self)

        self.ui_updater.add(self.command_ui)

        self.change_ruleset()

        # Background image
        self.background = pygame.transform.scale(load_image(self.main_dir, self.screen_scale,
                                                            "default.png", ("ui", "mainmenu_ui")),
                                                 self.screen_rect.size)

        subunit.Subunit.battle = self.battle
        damagesprite.DamageSprite.battle = self.battle
        effectsprite.EffectSprite.battle = self.battle

        # Starting script
        self.main_ui_updater.remove(*self.menu_button)  # remove all button from drawing
        self.menu_button.remove(
            *self.menu_button)  # remove all button at the start and add later depending on menu_state
        self.menu_button.add(*self.mainmenu_button)  # add only game start menu button back

        self.start_menu_ui_only = *self.menu_button, self.profile_box  # ui that only appear at the start menu
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

        self.battle_map_data = datamap.BattleMapData(self.main_dir, self.screen_scale, self.ruleset_folder,
                                                     self.language)

        self.battle.battle_map_base.terrain_list = self.battle_map_data.terrain_list
        self.battle.battle_map_base.terrain_colour = self.battle_map_data.terrain_colour
        self.battle.battle_map_feature.feature_list = self.battle_map_data.feature_list
        self.battle.battle_map_feature.feature_colour = self.battle_map_data.feature_colour
        self.battle.battle_map_feature.feature_mod = self.battle_map_data.feature_mod

        self.battle.battle_map.battle_map_colour = self.battle_map_data.battle_map_colour
        self.battle.battle_map.texture_images = self.battle_map_data.map_texture
        self.battle.battle_map.load_texture_list = self.battle_map_data.texture_folder
        self.battle.battle_map.empty_texture = self.battle_map_data.empty_image
        self.battle.battle_map.camp_texture = self.battle_map_data.camp_image

        self.map_show.terrain_colour = self.battle_map_data.terrain_colour
        self.map_show.feature_colour = self.battle_map_data.feature_colour
        self.map_show.battle_map_colour = self.battle_map_data.battle_map_colour

        self.battle.battle_map_data = self.battle_map_data
        self.battle.weather_data = self.battle_map_data.weather_data
        self.battle.weather_matter_images = self.battle_map_data.weather_matter_images
        self.battle.weather_effect_images = self.battle_map_data.weather_effect_images
        self.battle.day_effect_images = self.battle_map_data.day_effect_images
        self.battle.weather_list = self.battle_map_data.weather_list
        self.battle.feature_mod = self.battle_map_data.feature_mod

        subunit.Subunit.troop_data = self.troop_data
        subunit.Subunit.leader_data = self.leader_data
        subunit.Subunit.troop_sprite_list = self.troop_data.troop_sprite_list
        subunit.Subunit.leader_sprite_list = self.leader_data.leader_sprite_list
        subunit.Subunit.status_list = self.troop_data.status_list
        subunit.Subunit.all_formation_list = self.troop_data.default_formation_list
        subunit.Subunit.effect_list = self.troop_data.effect_list

        damagesprite.DamageSprite.effect_list = self.troop_data.effect_list
        effectsprite.EffectSprite.effect_list = self.troop_data.effect_list

        self.preset_map_list, self.preset_map_folder, self.custom_map_list, \
        self.custom_map_folder = make_battle_list_data(self.main_dir, self.ruleset_folder, self.language)

        self.troop_animation = datasprite.TroopAnimationData(self.main_dir,
                                                             [str(self.troop_data.race_list[key]["Name"]) for key in
                                                              self.troop_data.race_list], self.team_colour)
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
                image = pygame.transform.flip(value2, False, True)
                bullet_sprite_pool[key][key2] = image
        bullet_weapon_sprite_pool = {}
        for key, value in self.gen_weapon_sprite_pool.items():
            bullet_weapon_sprite_pool[key] = {}
            for key2, value2 in value.items():
                bullet_weapon_sprite_pool[key][key2] = {}
                for key3, value3 in value2.items():
                    if key3 == "base_main":
                        bullet_weapon_sprite_pool[key][key2][key3] = {}
                        image = pygame.transform.flip(value3, False, True)
                        bullet_weapon_sprite_pool[key][key2][key3] = image

        damagesprite.DamageSprite.bullet_sprite_pool = bullet_sprite_pool
        damagesprite.DamageSprite.bullet_weapon_sprite_pool = bullet_weapon_sprite_pool
        damagesprite.DamageSprite.effect_sprite_pool = self.effect_sprite_pool
        damagesprite.DamageSprite.effect_animation_pool = self.effect_animation_pool

        effectsprite.EffectSprite.effect_sprite_pool = self.effect_sprite_pool
        effectsprite.EffectSprite.effect_animation_pool = self.effect_animation_pool

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

        self.encyclopedia.change_ruleset()

        # Error log for selected ruleset
        self.error_log.write("Ruleset: " + self.ruleset_list[self.ruleset][0])

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

        pygame.display.set_caption(version_name)  # set the self name on program border/tab

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
                    if self.input_popup[0]:  # event update to input box
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
                0]:  # currently, have input text pop up on screen, stop everything else until done
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
                    self.map_type = self.menu_state[:-4]
                    self.menu_map_select(mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press)

                elif self.menu_state == "team_select":
                    self.menu_team_select(mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press)

                elif self.menu_state == "char_select":
                    self.menu_char_select(mouse_left_up, mouse_left_down, mouse_scroll_up,
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
