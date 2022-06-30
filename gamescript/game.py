import configparser
import csv
import glob
import os.path
import sys
import screeninfo
import importlib
from pathlib import Path

import pygame
import pygame.freetype
from pygame.locals import *

from gamescript import battlemap, weather, lorebook, drama, battleui, popup, menu, rangeattack, uniteditor, \
    battle, leader, unit, subunit, datasprite, datamap
from gamescript.common import utility
from gamescript.common.battle import setup_battle_unit, generate_unit

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

# Module that get loads with import in common.game.setup after


def make_battle_list_data(*args): pass
def make_battle_ui(*args): pass
def make_editor_ui(*args): pass
def make_esc_menu(*args): pass
def make_event_log(*args): pass
def make_faction_troop_leader_equipment_data(*args): pass
def make_genre_specific_ui(*args): pass
def make_icon_data(*args): pass
def make_input_box(*args): pass
def make_lorebook(*args): pass
def make_option_menu(*args): pass
def make_popup_ui(*args): pass


script_dir = os.path.split(os.path.abspath(__file__))[0] + "/"

for entry in os.scandir(script_dir + "/common/game/setup/"):  # load and replace modules from common.game.setup
    if entry.is_file() and ".py" in entry.name:
        file_name = entry.name[:-3]
        exec(f"from gamescript.common.game.setup import " + file_name)
        exec(f"" + file_name + " = " + file_name + "." + file_name)

version_name = "Dream Decision"  # Game version name that will appear as game name

unit_state_text = {0: "Idle", 1: "Walk", 2: "Run", 3: "Walk (M)", 4: "Run (M)", 5: "Walk (R)", 6: "Run (R)",
                   7: "Walk (F)", 8: "Run (F)", 10: "Melee", 11: "Shoot", 12: "Walk (S)", 13: "Run (S)",
                   65: "Sleep", 66: "Camp", 67: "Rest", 68: "Dance", 69: "Party", 95: "Disobey", 96: "Retreat",
                   97: "Collapse", 98: "Retreat", 99: "Broken", 100: "Destroyed"}

subunit_state_text = {0: "Idle", 1: "Walk", 2: "Run", 3: "Walk (M)", 4: "Run (M)", 5: "Walk (R)", 6: "Run (R)", 10: "Melee", 11: "Shoot",
                      12: "Walk (S)", 13: "Run (S)", 95: "Disobey", 96: "Flee", 97: "Rest", 98: "Flee", 99: "Broken", 100: "Dead"}
subunit_state = {key: value.split(" ")[0] for key, value in subunit_state_text.items()}

leader_state_text = {96: "Flee", 97: "POW", 98: "MIA", 99: "WIA", 100: "KIA"}

morale_state_text = {0: "Broken", 1: "Fleeing", 2: "Breaking", 3: "Poor", 4: "Wavering", 5: "Balanced",
                     6: "Steady", 7: "Fine", 8: "Confident", 9: "Eager", 10: "Ready", 11: "Merry", 12: "Elated", 13: "Ecstatic",
                     14: "Inspired", 15: "Fervent"}  # unit morale state name

stamina_state_text = {0: "Collapse", 1: "Exhausted", 2: "Severed", 3: "Very Tired", 4: "Tired", 5: "Winded", 6: "Moderate",
                      7: "Alert", 8: "Warmed Up", 9: "Active", 10: "Fresh"}  # unit stamina state name

quality_text = ("Broken", "Very Poor", "Poor", "Standard", "Good", "Superb", "Perfect")  # item quality name

leader_level = ("Commander", "Sub-General", "Sub-General", "Sub-Commander", "General", "Sub-General", "Sub-General",
                "Advisor")  # Name of leader position in unit, the first 4 is for commander unit

team_colour = unit.team_colour


class Game:
    empty_method = utility.empty_method

    # import from common.game
    back_mainmenu = empty_method
    change_battle_source = empty_method
    change_to_source_selection_menu = empty_method
    char_select_menu_process = empty_method
    convert_formation_preset = empty_method
    create_preview_map = empty_method
    create_sprite_pool = empty_method
    create_team_coa = empty_method
    create_unit_slot = empty_method
    game_editor_menu_process = empty_method
    main_menu_process = empty_method
    map_select_menu_process = empty_method
    option_menu_process = empty_method
    read_battle_source = empty_method
    read_selected_map_data = empty_method
    start_battle = empty_method
    team_select_menu_process = empty_method

    # import from *genre*.game
    leader_position_check = empty_method

    generate_unit = generate_unit.generate_unit
    setup_battle_unit = setup_battle_unit.setup_battle_unit

    popup_list_open = utility.popup_list_open

    lorebook_process = lorebook.lorebook_process

    script_dir = script_dir
    for entry in os.scandir(script_dir + "/common/game/"):  # load and replace modules from common.game
        if entry.is_file() and ".py" in entry.name:
            file_name = entry.name[:-3]
            exec(f"from gamescript.common.game import " + file_name)
            exec(f"" + file_name + " = " + file_name + "." + file_name)

    # Will be changed in genre_change function depending on selected genre
    char_select = False
    leader_sprite = False
    troop_sprite_size = (200, 200)
    unit_size = (8, 8)
    start_zoom = 1
    start_zoom_mode = "Follow"
    time_speed_scale = 1
    troop_size_adjustable = False
    add_troop_number_sprite = False

    def __init__(self, main_dir, error_log):
        pygame.init()  # Initialize pygame

        self.main_dir = main_dir
        self.error_log = error_log

        lorebook.Lorebook.main_dir = self.main_dir
        battlemap.FeatureMap.main_dir = self.main_dir
        battlemap.BeautifulMap.main_dir = self.main_dir
        uniteditor.PreviewBox.main_dir = self.main_dir

        # Read config file
        config = configparser.ConfigParser()
        try:
            config.read_file(open("configuration.ini"))  # read config file
        except FileNotFoundError:  # Create config file if not found with the default
            genre_folder = Path(os.path.join(self.main_dir, "gamescript"))
            genre_folder = [x for x in genre_folder.iterdir() if x.is_dir()]
            genre_folder = [str(folder_name).split("\\")[-1].capitalize() for folder_name in genre_folder]
            genre_folder.remove("__pycache__")  # just grab the first genre folder as default

            config = configparser.ConfigParser()

            screen = screeninfo.get_monitors()[0]
            screen_width = int(screen.width)
            screen_height = int(screen.height)

            config["DEFAULT"] = {"screen_width": screen_width, "screen_height": screen_height, "fullscreen": "0",
                                 "player_Name": "Noname", "master_volume": "100.0", "music_volume": "0.0",
                                 "voice_volume": "0.0", "max_fps": "60", "ruleset": "1", "genre": genre_folder[-1]}
            with open("configuration.ini", "w") as cf:
                config.write(cf)
            config.read_file(open("configuration.ini"))

        self.config = config
        self.screen_width = int(self.config["DEFAULT"]["screen_width"])
        self.screen_height = int(self.config["DEFAULT"]["screen_height"])
        self.full_screen = int(self.config["DEFAULT"]["fullscreen"])
        self.master_volume = float(self.config["DEFAULT"]["master_volume"])
        self.profile_name = str(self.config["DEFAULT"]["player_Name"])
        self.genre = str(self.config["DEFAULT"]["genre"])
        self.ruleset = 1  # for now default historical ruleset only

        # Set the display mode
        self.screen_rect = Rect(0, 0, self.screen_width, self.screen_height)
        self.screen_scale = (self.screen_rect.width / 1920, self.screen_rect.height / 1080)
        self.window_style = 0
        if self.full_screen == 1:  # fullscreen = 1
            self.window_style = pygame.FULLSCREEN
        self.best_depth = pygame.display.mode_ok(self.screen_rect.size, self.window_style, 32)
        self.screen = pygame.display.set_mode(self.screen_rect.size, self.window_style | pygame.RESIZABLE, self.best_depth)

        self.clock = pygame.time.Clock()

        self.loading = load_image(self.main_dir, self.screen_scale, "loading.png", "ui\\mainmenu_ui")
        self.loading = pygame.transform.scale(self.loading, self.screen_rect.size)
        self.game_intro(self.screen, self.clock, False)  # run intro

        self.ruleset_list = csv_read(self.main_dir, "ruleset_list.csv", ["data", "ruleset"])  # get ruleset list
        self.ruleset_folder = str(self.ruleset_list[self.ruleset][1]).strip("/").strip("\\")

        if not os.path.exists("../profile"):  # make profile folder if not existed
            os.makedirs("../profile")
            os.makedirs("../profile/unitpreset")
        if not os.path.exists("profile/unitpreset/" + str(self.ruleset)):  # create unitpreset folder for ruleset
            os.makedirs("profile/unitpreset/" + str(self.ruleset))
        try:
            custom_unit_preset_list = csv_read(self.main_dir, "custom_unitpreset.csv",
                                               ["profile", "unitpreset", str(self.ruleset)])
            del custom_unit_preset_list["presetname"]
            self.custom_unit_preset_list = {"New Preset": 0, **custom_unit_preset_list}
        except Exception:
            with open("profile/unitpreset/" + str(self.ruleset) + "/custom_unitpreset.csv", "w") as edit_file:
                file_writer = csv.writer(edit_file, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
                file_writer.writerow(["presetname", "unitline2", "unitline2", "unitline3", "unitline4", "unitline15", "unitline6",
                                     "unitline7", "unitline8", "leader", "leaderposition", "faction"])  # create header
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
        self.lore_name_list = pygame.sprite.Group()  # box sprite for showing subsection name list in encyclopedia
        self.subsection_name = pygame.sprite.Group()  # subsection name objects group in encyclopedia blit on lore_name_list

        # battle select menu
        self.map_namegroup = pygame.sprite.Group()  # map name list group
        self.team_coa = pygame.sprite.Group()  # team coat of arm that also act as team selection icon
        self.army_stat = pygame.sprite.Group()  # ui box that show army stat in preset battle preparation screen
        self.char_stat = {}
        self.source_namegroup = pygame.sprite.Group()  # source name list group
        self.tick_box = pygame.sprite.Group()  # option tick box
        # battle related

        # esc option menu
        self.value_box = pygame.sprite.Group()  # value number and box in esc menu option

        # unit editor
        self.troop_namegroup = pygame.sprite.Group()  # troop name list group
        self.popup_namegroup = pygame.sprite.Group()
        self.unit_edit_border = pygame.sprite.Group()  # border that appear when selected sub-subunit
        self.unitpreset_namegroup = pygame.sprite.Group()  # preset name list
        self.subunit_build = pygame.sprite.Group()

        # battle object group
        self.battle_camera = pygame.sprite.LayeredUpdates()  # layer drawer self camera, all image pos should be based on the map not screen
        unit.Unit.battle_camera = self.battle_camera
        # the camera layer is as followed 0 = terrain map, 1 = dead unit, 2 = map special feature, 3 = , 4 = subunit, 5 = sub-subunit,
        # 6 = flying subunit, 7 = arrow/range, 8 = weather, 9 = weather matter, 10 = ui/button, 11 = subunit inspect, 12 pop up
        self.battle_ui_updater = pygame.sprite.LayeredUpdates()  # this is layer drawer for ui, all image pos should be based on the screen

        self.unit_updater = pygame.sprite.Group()  # updater for unit objects, only for in battle not editor or preview
        self.subunit_updater = pygame.sprite.Group()  # updater for subunit objects
        self.leader_updater = pygame.sprite.Group()  # updater for leader objects
        self.ui_updater = pygame.sprite.Group()  # updater for ui objects
        self.weather_updater = pygame.sprite.Group()  # updater for weather objects
        self.effect_updater = pygame.sprite.Group()  # updater for effect objects (e.g. range melee_attack sprite)

        self.preview_char = pygame.sprite.Group()  # group for char list in char select screen

        self.subunit_group = pygame.sprite.Group()  # all subunits group

        self.leader_group = pygame.sprite.Group()  # all leaders group

        self.range_attacks = pygame.sprite.Group()  # all range_attacks group and maybe other range effect stuff later
        self.direction_arrows = pygame.sprite.Group()
        self.troop_number_sprite = pygame.sprite.Group()  # troop text number that appear next to unit sprite

        self.button_ui = pygame.sprite.Group()  # ui button group in battle
        self.inspect_selected_border = pygame.sprite.Group()  # subunit selected border in inspect ui unit box
        self.wheel_ui = pygame.sprite.Group()

        self.buttonname_popup = pygame.sprite.Group()  # button name pop up ui when mouse over button
        self.leader_popup = pygame.sprite.Group()  # leader name pop up ui when mouse over leader image in command ui
        self.effect_popup = pygame.sprite.Group()  # effect name pop up ui when mouse over status effect icon

        self.skill_icon = pygame.sprite.Group()  # skill and trait icon objects
        self.effect_icon = pygame.sprite.Group()  # status effect icon objects

        self.battle_menu_button = pygame.sprite.Group()  # buttons for esc menu object group
        self.escoption_menu_button = pygame.sprite.Group()  # buttons for esc menu option object group
        self.slider_menu = pygame.sprite.Group()  # volume slider in esc option menu

        self.unit_icon = pygame.sprite.Group()  # unit icon object group in unit selector ui
        self.weather_matter = pygame.sprite.Group()  # sprite of weather effect group such as rain sprite
        self.weather_effect = pygame.sprite.Group()  # sprite of special weather effect group such as fog that cover whole screen

        # Assign containers
        menu.MenuButton.containers = self.menu_button
        menu.MenuIcon.containers = self.menu_icon
        menu.SliderMenu.containers = self.menu_slider, self.slider_menu
        menu.ValueBox.containers = self.value_box

        menu.NameList.containers = self.map_namegroup
        menu.TeamCoa.containers = self.team_coa

        menu.TickBox.containers = self.tick_box

        lorebook.SubsectionList.containers = self.lore_name_list
        lorebook.SubsectionName.containers = self.subsection_name, self.main_ui_updater, self.battle_ui_updater

        uniteditor.PreviewBox.effect_image = load_image(self.main_dir, self.screen_scale, "effect.png", "map")  # map special effect image

        # battle containers
        battleui.SwitchButton.containers = self.ui_updater
        battleui.SelectedSquad.containers = self.inspect_selected_border, self.unit_edit_border, self.main_ui_updater, self.battle_ui_updater
        battleui.SkillCardIcon.containers = self.skill_icon, self.battle_ui_updater
        battleui.EffectCardIcon.containers = self.effect_icon, self.battle_ui_updater
        battleui.UnitIcon.containers = self.unit_icon, self.main_ui_updater, self.battle_ui_updater
        battleui.TroopNumber.containers = self.troop_number_sprite, self.effect_updater, self.battle_camera
        battleui.DirectionArrow.containers = self.direction_arrows, self.effect_updater, self.battle_camera
        battleui.WheelUI.containers = self.wheel_ui

        popup.TextPopup.containers = self.buttonname_popup, self.leader_popup
        popup.EffectIconPopup.containers = self.effect_popup

        rangeattack.RangeAttack.containers = self.range_attacks, self.effect_updater, self.battle_camera

        menu.EscButton.containers = self.battle_menu_button, self.escoption_menu_button

        weather.MatterSprite.containers = self.weather_matter, self.battle_ui_updater, self.weather_updater
        weather.SpecialEffect.containers = self.weather_effect, self.battle_ui_updater, self.weather_updater

        unit.Unit.containers = self.unit_updater
        subunit.Subunit.containers = self.subunit_updater, self.battle_camera
        leader.Leader.containers = self.leader_updater

        # Main menu related stuff
        image_list = load_base_button(self.main_dir, self.screen_scale)
        self.preset_map_button = menu.MenuButton(self.screen_scale, image_list,
                                                 (self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 8.5)),
                                                 self.main_ui_updater, text="Preset Map")
        self.custom_map_button = menu.MenuButton(self.screen_scale, image_list,
                                                 (self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 7)),
                                                 self.main_ui_updater, text="Custom Map")
        self.game_edit_button = menu.MenuButton(self.screen_scale, image_list,
                                                (self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 5.5)),
                                                self.main_ui_updater, text="Unit Editor")
        self.lore_button = menu.MenuButton(self.screen_scale, image_list,
                                           (self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 4)),
                                           self.main_ui_updater, text="Encyclopedia")
        self.option_button = menu.MenuButton(self.screen_scale, image_list,
                                             (self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 2.5)),
                                             self.main_ui_updater, text="Option")
        self.quit_button = menu.MenuButton(self.screen_scale, image_list,
                                           (self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height())),
                                           self.main_ui_updater, text="Quit")
        self.mainmenu_button = (self.preset_map_button, self.custom_map_button, self.game_edit_button,
                                self.lore_button, self.option_button, self.quit_button)

        # Battle map select menu button
        battle_select_image = load_images(self.main_dir, self.screen_scale, ["ui", "mapselect_ui"], load_order=False)

        self.map_title = menu.MapTitle(self.screen_scale, (self.screen_rect.width / 2, 0))

        self.map_description = menu.DescriptionBox(battle_select_image["map_description.png"], self.screen_scale,
                                                   (self.screen_rect.width / 2, self.screen_rect.height / 1.3))
        self.map_show = menu.MapPreview(self.main_dir, self.screen_scale, (self.screen_rect.width / 2, self.screen_rect.height / 3))
        self.source_description = menu.DescriptionBox(battle_select_image["source_description.png"], self.screen_scale,
                                                      (self.screen_rect.width / 2, self.screen_rect.height / 1.3), text_size=24)

        self.char_selector = battleui.UnitSelector((self.screen_rect.width / 5, self.screen_rect.height / 1.5),
                                                   battle_select_image["char_select.png"])
        battleui.UIScroll(self.char_selector, self.char_selector.rect.topright)  # scroll bar for char pick

        bottom_height = self.screen_rect.height - image_list[0].get_height()
        self.select_button = menu.MenuButton(self.screen_scale, image_list, (self.screen_rect.width - image_list[0].get_width(), bottom_height),
                                             self.main_ui_updater, text="Select")
        self.start_button = menu.MenuButton(self.screen_scale, image_list, (self.screen_rect.width - image_list[0].get_width(), bottom_height),
                                            self.main_ui_updater, text="Start")
        self.map_back_button = menu.MenuButton(self.screen_scale, image_list,
                                               (self.screen_rect.width - (self.screen_rect.width - image_list[0].get_width()), bottom_height),
                                               self.main_ui_updater, text="Back")
        self.char_back_button = menu.MenuButton(self.screen_scale, image_list,
                                               (self.screen_rect.width - (self.screen_rect.width - image_list[0].get_width()), bottom_height),
                                               self.main_ui_updater, text="Back")
        self.map_select_button = (self.select_button, self.map_back_button)
        self.team_select_button = (self.start_button, self.map_back_button)
        self.char_select_button = (self.start_button, self.char_back_button)

        self.map_list_box = menu.ListBox(self.screen_scale, (self.screen_rect.width / 25, self.screen_rect.height / 20),
                                         battle_select_image["name_list.png"])
        battleui.UIScroll(self.map_list_box, self.map_list_box.rect.topright)  # scroll bar for map list

        self.source_list_box = menu.ListBox(self.screen_scale, (0, 0), battle_select_image["top_box.png"])  # source list ui box
        battleui.UIScroll(self.source_list_box, self.source_list_box.rect.topright)  # scroll bar for source list
        self.map_option_box = menu.MapOptionBox(self.screen_scale, (self.screen_rect.width, 0), battle_select_image["top_box.png"],
                                                0)  # ui box for battle option during preparation screen

        self.enactment_tick_box = menu.TickBox(self.screen_scale, (self.map_option_box.rect.bottomright[0] / 1.2,
                                                                   self.map_option_box.rect.bottomright[1] / 4),
                                               battle_select_image["untick.png"], battle_select_image["tick.png"], "enactment")
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
                                                (self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 4)),
                                                self.main_ui_updater, text="Army Editor")
        self.subunit_create_button = menu.MenuButton(self.screen_scale, image_list,
                                                     (self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 2.5)),
                                                     self.main_ui_updater, text="Troop Creator")
        self.editor_back_button = menu.MenuButton(self.screen_scale, image_list,
                                                  (self.screen_rect.width / 2, self.screen_rect.height - image_list[0].get_height()),
                                                  self.main_ui_updater, text="Back")
        self.editor_button = (self.unit_edit_button, self.subunit_create_button, self.editor_back_button)

        # Option menu button
        option_menu_dict = make_option_menu(self.main_dir, self.screen_scale, self.screen_rect, self.screen_width, self.screen_height,
                                            image_list, self.master_volume, self.main_ui_updater)
        self.back_button = option_menu_dict["back_button"]
        self.resolution_drop = option_menu_dict["resolution_drop"]
        self.resolution_bar = option_menu_dict["resolution_bar"]
        self.resolution_icon = option_menu_dict["resolution_icon"]
        self.volume_slider = option_menu_dict["volume_slider"]
        self.value_box = option_menu_dict["value_box"]
        self.volume_icon = option_menu_dict["volume_icon"]

        self.option_icon_list = (self.resolution_icon, self.volume_icon)
        self.option_menu_button = (self.back_button, self.resolution_drop)
        self.option_menu_slider = self.volume_slider

        # Genre related stuff
        genre_folder = Path(os.path.join(main_dir, "gamescript"))  # Load genre list
        subdirectories = [x for x in genre_folder.iterdir() if x.is_dir()]
        subdirectories = [str(folder_name).split("\\")[-1].capitalize() for folder_name in subdirectories]
        subdirectories.remove("__pycache__")
        subdirectories.remove("Common")
        self.genre_list = subdirectories  # map name list for map selection list

        box_image = load_image(self.main_dir, self.screen_scale, "genre_box.png", "ui\\mainmenu_ui")
        self.genre_change_box = menu.TextBox(self.screen_scale, box_image, (box_image.get_width(), 0),
                                             self.genre.capitalize())  # genre box ui

        # Profile box
        self.profile_name = self.profile_name
        profile_box_image = load_image(self.main_dir, self.screen_scale, "profile_box.png", "ui\\mainmenu_ui")
        self.profile_box = menu.TextBox(self.screen_scale, profile_box_image, (self.screen_width, 0),
                                        self.profile_name)  # profile name box at top right of screen at start_set menu screen

        # Music player
        if pygame.mixer and not pygame.mixer.get_init():
            pygame.mixer = None
        if pygame.mixer:
            self.master_volume = float(self.master_volume / 100)
            pygame.mixer.music.set_volume(self.master_volume)
            self.SONG_END = pygame.USEREVENT + 1
            self.music_list = glob.glob(self.main_dir + "/data/sound/music/*.ogg")
            pygame.mixer.music.load(self.music_list[0])
            pygame.mixer.music.play(-1)
        # ^ End Main menu

        # v Battle related stuffs
        unit_ui_images = load_images(self.main_dir, self.screen_scale, ["ui", "unit_ui"])
        subunit.Subunit.unit_ui_images = unit_ui_images

        subunit_icon_image = unit_ui_images["ui_squad_player.png"]
        self.icon_sprite_width = subunit_icon_image.get_width()
        self.icon_sprite_height = subunit_icon_image.get_height()

        self.fps_count = battleui.FPScount()  # FPS number counter
        self.battle_ui_updater.add(self.fps_count)

        battle_ui_image = load_images(self.main_dir, self.screen_scale, ["ui", "battle_ui"], load_order=False)
        battleui.SelectedSquad.image = battle_ui_image[
            "ui_subunit_clicked.png"]  # subunit border image always the last one

        # Battle map
        self.battle_base_map = battlemap.BaseMap()  # create base terrain map
        self.battle_feature_map = battlemap.FeatureMap()  # create terrain feature map
        self.battle_height_map = battlemap.HeightMap()  # create height map
        self.show_map = battlemap.BeautifulMap(self.screen_scale)
        self.battle_camera.add(self.show_map)

        rangeattack.RangeAttack.height_map = self.battle_height_map
        subunit.Subunit.base_map = self.battle_base_map  # add battle map to subunit class
        subunit.Subunit.feature_map = self.battle_feature_map
        subunit.Subunit.height_map = self.battle_height_map

        self.status_images, self.role_images, self.trait_images, self.skill_images = make_icon_data(self.main_dir, self.screen_scale)

        self.mini_map = battleui.MiniMap((self.screen_rect.width, self.screen_rect.height), self.screen_scale)
        self.battle_ui_updater.add(self.mini_map)

        # Game sprite Effect
        effect_images = load_images(self.main_dir, self.screen_scale, ["sprite", "effect"], load_order=False)
        rangeattack.RangeAttack.images = [effect_images["arrow.png"]]
        rangeattack.RangeAttack.screen_scale = self.screen_scale

        # Battle ui
        battle_icon_image = load_images(self.main_dir, self.screen_scale, ["ui", "battle_ui", "topbar_icon"],
                                        load_order=False)
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

        # Unit editor
        editor_dict = make_editor_ui(self.main_dir, self.screen_scale, self.screen_rect,
                                     load_image(self.main_dir, self.screen_scale, "name_list.png", "ui\\mapselect_ui"),
                                     load_base_button(self.main_dir, self.screen_scale), self.battle_scale_ui, team_colour,
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

        self.preview_leader = [uniteditor.PreviewLeader(1, 0, 0),
                               uniteditor.PreviewLeader(1, 0, 1),
                               uniteditor.PreviewLeader(1, 0, 2),
                               uniteditor.PreviewLeader(1, 0, 3)]  # list of preview leader for unit editor
        self.leader_updater.remove(*self.preview_leader)  # remove preview leader from updater since not use in battle

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

        self.genre_ui_dict = make_genre_specific_ui(self.main_dir, self.screen_scale, self.genre)
        self.command_ui = self.genre_ui_dict["command_ui"]
        self.ui_updater.add(self.command_ui)
        uniteditor.PreviewLeader.leader_pos = self.command_ui.leader_pos
        leader.Leader.leader_pos = self.command_ui.leader_pos

        self.col_split_button = self.genre_ui_dict["col_split_button"]
        self.row_split_button = self.genre_ui_dict["row_split_button"]
        self.decimation_button = self.genre_ui_dict["decimation_button"]
        self.inspect_button = self.genre_ui_dict["inspect_button"]
        self.main_ui_updater.remove(
            self.inspect_selected_border)  # remove subunit border sprite from start_set menu drawer

        self.inspect_ui = self.genre_ui_dict["inspect_ui"]
        self.ui_updater.add(self.inspect_ui)
        self.inspect_selected_border = battleui.SelectedSquad((0, 0))  # yellow border on selected subunit in inspect ui
        self.main_ui_updater.remove(
            self.inspect_selected_border)  # remove subunit border sprite from start_set menu drawer

        # Behaviour button that once click switch to other mode for subunit behaviour
        self.behaviour_switch_button = self.genre_ui_dict["behaviour_switch_button"]

        # Other ui in battle
        self.battle_done_box = battleui.BattleDone(self.screen_scale, (self.screen_width / 2, self.screen_height / 2),
                                                   battle_ui_image["end_box.png"], battle_ui_image["result_box.png"])
        self.battle_done_button = battleui.UIButton(battle_ui_image["end_button.png"], layer=19)
        self.battle_done_button.change_pos((self.battle_done_box.pos[0], self.battle_done_box.box_image.get_height() * 0.8))

        drama.TextDrama.images = load_images(self.main_dir, self.screen_scale, ["ui", "popup_ui", "drama_text"], load_order=False)
        drama.TextDrama.screen_rect = self.screen_rect
        self.drama_text = drama.TextDrama(self.screen_scale)  # message at the top of screen that show up for important event

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
        self.esc_value_box = esc_menu_dict["esc_value_box"]

        popup_ui_dict = make_popup_ui(self.main_dir, self.screen_rect, self.screen_scale, battle_ui_image)
        self.troop_card_ui = popup_ui_dict["troop_card_ui"]
        self.troop_card_button = popup_ui_dict["troop_card_button"]
        self.terrain_check = popup_ui_dict["terrain_check"]
        self.button_name_popup = popup_ui_dict["button_name_popup"]
        self.terrain_check = popup_ui_dict["terrain_check"]
        self.button_name_popup = popup_ui_dict["button_name_popup"]
        self.leader_popup = popup_ui_dict["leader_popup"]
        self.effect_popup = popup_ui_dict["effect_popup"]
        self.char_popup = popup_ui_dict["char_popup"]
        self.ui_updater.add(self.troop_card_ui)
        self.button_ui.add(self.troop_card_button)

        self.encyclopedia, self.lore_name_list, self.lore_button_ui, self.page_button = make_lorebook(self.main_dir, self.ruleset_folder, self.screen_scale, self.screen_rect)

        self.battle_map_data = datamap.BattleMapData(self.main_dir, self.screen_scale)

        self.battle_game = battle.Battle(self, self.window_style)
        self.change_game_genre(self.genre)

        self.troop_card_ui.feature_list = self.battle_map_data.feature_list  # add terrain feature list name to subunit card

        subunit.Subunit.battle = self.battle_game
        leader.Leader.battle = self.battle_game
        start_pos = [(self.screen_rect.width / 2) - (self.icon_sprite_width * 5),
                     (self.screen_rect.height / 2) - (self.icon_sprite_height * 4)]
        self.create_unit_slot(0, 0, range(0, 64), start_pos)  # make player custom unit slot
        # ^ End battle related stuffs

        # starting script
        self.main_ui_updater.remove(*self.menu_button)  # remove all button from drawing
        self.menu_button.remove(
            *self.menu_button)  # remove all button at the start and add later depending on menu_state
        self.menu_button.add(*self.mainmenu_button)  # add only game start menu button back

        self.start_menu_ui_only = *self.menu_button, self.profile_box, self.genre_change_box  # ui that only appear at the start menu
        self.main_ui_updater.add(*self.start_menu_ui_only)
        self.menu_state = "main_menu"
        self.input_popup = (None, None)  # popup for text input state
        self.choosing_faction = True  # swap list between faction and subunit, always start with choose faction first as true

        pygame.mouse.set_visible(True)  # set mouse as visible

        self.run()

    def change_ruleset(self):
        self.weapon_data, self.armour_data, self.troop_data, self.leader_data, self.faction_data = make_faction_troop_leader_equipment_data(self.main_dir, self.screen_scale, self.ruleset, self.ruleset_folder)
        subunit.Subunit.screen_scale = self.screen_scale
        subunit.Subunit.weapon_data = self.weapon_data
        subunit.Subunit.armour_data = self.armour_data
        subunit.Subunit.troop_data = self.troop_data
        subunit.Subunit.leader_data = self.leader_data
        subunit.Subunit.status_list = self.troop_data.status_list
        subunit.Subunit.subunit_state = self.subunit_state

        self.convert_formation_preset()
        unit.Unit.unit_formation_list = self.troop_data.unit_formation_list

        self.preset_map_list, self.preset_map_folder, self.custom_map_list, \
        self.custom_map_folder = make_battle_list_data(self.main_dir, self.ruleset_folder)

        self.troop_animation = datasprite.TroopAnimationData(self.main_dir, [self.troop_data.race_list[key]["Name"] for key in self.troop_data.race_list])
        self.generic_action_data = self.troop_animation.generic_action_data  # action data pool
        self.generic_animation_pool = self.troop_animation.generic_animation_pool  # animation data pool
        self.gen_body_sprite_pool = self.troop_animation.gen_body_sprite_pool  # body sprite pool
        self.gen_weapon_sprite_pool = self.troop_animation.gen_weapon_sprite_pool  # weapon sprite pool
        self.gen_armour_sprite_pool = self.troop_animation.gen_armour_sprite_pool  # armour sprite pool
        self.weapon_joint_list = self.troop_animation.weapon_joint_list  # weapon joint data
        self.hair_colour_list = self.troop_animation.hair_colour_list  # hair colour list
        self.skin_colour_list = self.troop_animation.skin_colour_list  # skin colour list

        subunit.Subunit.generic_action_data = self.generic_action_data

        self.effect_sprite_pool = datasprite.EffectSpriteData(self.main_dir)

        who_todo = {key: value for key, value in self.troop_data.troop_list.items()}
        self.preview_sprite_pool = self.create_sprite_pool(direction_list, self.troop_sprite_size, self.screen_scale,
                                                           who_todo, preview=True)

        # Encyclopedia
        lorebook.Lorebook.faction_lore = self.faction_data.faction_list
        lorebook.Lorebook.troop_list = self.troop_data.troop_list
        lorebook.Lorebook.troop_lore = self.troop_data.troop_lore
        lorebook.Lorebook.armour_list = self.armour_data.armour_list
        lorebook.Lorebook.weapon_list = self.weapon_data.weapon_list
        lorebook.Lorebook.mount_list = self.troop_data.mount_list
        lorebook.Lorebook.mount_armour_list = self.troop_data.mount_armour_list
        lorebook.Lorebook.status_list = self.troop_data.status_list
        lorebook.Lorebook.skill_list = self.troop_data.skill_list
        lorebook.Lorebook.trait_list = self.troop_data.trait_list
        lorebook.Lorebook.leader_data = self.leader_data
        lorebook.Lorebook.leader_lore = self.leader_data.leader_lore
        lorebook.Lorebook.feature_mod = self.battle_map_data.feature_mod
        lorebook.Lorebook.weather_data = self.battle_map_data.weather_data
        lorebook.Lorebook.landmark_data = None
        lorebook.Lorebook.troop_grade_list = self.troop_data.grade_list
        lorebook.Lorebook.troop_class_list = self.troop_data.role
        lorebook.Lorebook.leader_class_list = self.leader_data.leader_class
        lorebook.Lorebook.mount_grade_list = self.troop_data.mount_grade_list
        lorebook.Lorebook.race_list = self.troop_data.race_list
        lorebook.Lorebook.screen_rect = self.screen_rect
        lorebook.Lorebook.unit_state_text = self.unit_state_text
        lorebook.Lorebook.preview_sprite_pool = self.preview_sprite_pool

        self.encyclopedia.change_ruleset()

    def change_game_genre(self, genre):
        """Add new genre module here"""

        def import_genre_module(directory, old_genre, new_genre, change_object, folder_list, script_folder="gamescript"):
            """
            Import module from specific genre folder
            :param directory: Directory path to game file
            :param new_genre: Old genre folder name
            :param genre: Genre folder name
            :param change_object: Object that require the module as class function
            :param folder_list: List of folder name to import module
            :param script_folder: Name of game script folder
            """
            def empty(*args):  # empty method for genre that does not use already existing method in new selected genre
                pass

            for folder in folder_list:
                try:
                    for this_file in os.scandir(directory + new_genre + "/" + folder):
                        if this_file.is_file() and ".py" in this_file.name:
                            file_name = this_file.name[:-3]
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
                        new_folder = [this_file.name for this_file in os.scandir(directory + new_genre + "/" + folder)]
                    except FileNotFoundError:
                        new_folder = ()
                    try:
                        for this_file in os.scandir(directory + old_genre + "/" + folder):
                            if this_file.is_file() and ".py" in this_file.name:
                                if this_file.name not in new_folder:
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
        import_genre_module(self.script_dir, self.genre, new_genre, "Battle", ("battle", "battle/uniteditor", "ui"))
        import_genre_module(self.script_dir, self.genre, new_genre, "Leader", ("leader",))

        self.battle_game.generate_unit = self.generate_unit

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

        # calculate order placement from unit size setting
        self.genre = new_genre
        self.battle_game.genre = self.genre

        if self.char_select:  # genre with character select screen
            self.team_select_button = (self.map_select_button, self.map_back_button)
        else:
            self.team_select_button = (self.start_button, self.map_back_button)

        self.genre_change_box.change_text(self.genre.capitalize())
        edit_config("DEFAULT", "genre", self.genre, "configuration.ini", self.config)

        genre_battle_ui_image = load_images(self.main_dir, self.screen_scale, [self.genre, "ui", "battle_ui"],
                                            load_order=False)

        genre_icon_image = load_images(self.main_dir, self.screen_scale, [self.genre, "ui", "battle_ui",
                                                                          "commandbar_icon"], load_order=False)
        self.genre_ui_dict["command_ui"].load_sprite(genre_battle_ui_image["command_box.png"], genre_icon_image)

        self.genre_ui_dict["col_split_button"].image = genre_battle_ui_image["colsplit_button.png"]
        self.genre_ui_dict["row_split_button"].image = genre_battle_ui_image["rowsplit_button.png"]

        self.genre_ui_dict["decimation_button"].image = genre_battle_ui_image["decimation.png"]

        # Unit inspect information ui
        self.genre_ui_dict["inspect_button"].image = genre_battle_ui_image["army_inspect_button.png"]

        self.genre_ui_dict["inspect_ui"].image = genre_battle_ui_image["army_inspect.png"]

        skill_condition_button = [genre_battle_ui_image["skillcond_0.png"], genre_battle_ui_image["skillcond_1.png"],
                                  genre_battle_ui_image["skillcond_2.png"], genre_battle_ui_image["skillcond_3.png"]]
        shoot_condition_button = [genre_battle_ui_image["fire_0.png"], genre_battle_ui_image["fire_1.png"]]
        behaviour_button = [genre_battle_ui_image["hold_0.png"], genre_battle_ui_image["hold_1.png"],
                            genre_battle_ui_image["hold_2.png"]]
        range_condition_button = [genre_battle_ui_image["minrange_0.png"], genre_battle_ui_image["minrange_1.png"]]
        arc_condition_button = [genre_battle_ui_image["arc_0.png"], genre_battle_ui_image["arc_1.png"],
                                genre_battle_ui_image["arc_2.png"]]
        run_condition_button = [genre_battle_ui_image["runtoggle_0.png"], genre_battle_ui_image["runtoggle_1.png"]]
        melee_condition_button = [genre_battle_ui_image["meleeform_0.png"], genre_battle_ui_image["meleeform_1.png"],
                                  genre_battle_ui_image["meleeform_2.png"]]
        button_list = (skill_condition_button, shoot_condition_button, behaviour_button, range_condition_button,
                       arc_condition_button, run_condition_button, melee_condition_button)
        for index, button_image in enumerate(button_list):
            self.genre_ui_dict["behaviour_switch_button"][index].change_genre(button_image)

        self.change_ruleset()

        # Background image
        try:
            bgd_tile = load_image(self.main_dir, self.screen_scale, self.genre + ".png", "ui\\mainmenu_ui")
        except FileNotFoundError:
            bgd_tile = load_image(self.main_dir, self.screen_scale, "default.png", "ui\\mainmenu_ui")
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

        self.screen.blit(self.loading, (0, 0))  # blit loading screen after intro
        pygame.display.update()

        pygame.display.set_caption(version_name + " " + self.genre.capitalize())  # set the self name on program border/tab

    def run(self):
        while True:
            # v Get user input
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
                    else:
                        if event.key == K_ESCAPE:
                            esc_press = True

                if event.type == QUIT or self.quit_button.event or (esc_press and self.menu_state == "main_menu"):
                    self.quit_button.event = False
                    self.input_popup = ("confirm_input", "quit")
                    self.confirm_ui.change_instruction("Quit Game?")
                    self.main_ui_updater.add(*self.confirm_ui_popup)

            self.mouse_pos = pygame.mouse.get_pos()
            # ^ End user input

            self.screen.blit(self.background, (0, 0))  # blit background over instead of clear() to reset screen

            if self.input_popup[0] is not None:  # currently, have input text pop up on screen, stop everything else until done
                for button in self.input_button:
                    button.update(self.mouse_pos, mouse_left_up, mouse_left_down)

                if self.input_ok_button.event or key_press[pygame.K_RETURN] or key_press[pygame.K_KP_ENTER]:
                    self.input_ok_button.event = False

                    if self.input_popup[1] == "profile_name":
                        self.profile_name = self.input_box.text
                        self.profile_box.change_text(self.profile_name)

                        edit_config("DEFAULT", "playername", self.profile_name, "configuration.ini", self.config)

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

            elif self.input_popup == (None, None):
                self.menu_button.update(self.mouse_pos, mouse_left_up, mouse_left_down)
                if self.menu_state == "main_menu":
                    self.main_menu_process(mouse_left_up)

                elif self.menu_state == "preset_map" or self.menu_state == "custom_map":
                    self.map_select_menu_process(mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press)

                elif self.menu_state == "team_select":
                    self.team_select_menu_process(mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press)

                elif self.menu_state == "char_select":
                    self.char_select_menu_process(mouse_left_up, mouse_left_down, mouse_scroll_up,
                                                  mouse_scroll_down, esc_press)

                elif self.menu_state == "game_creator":
                    self.game_editor_menu_process(mouse_left_up, mouse_left_down, mouse_scroll_up,
                                                  mouse_scroll_down, esc_press)

                elif self.menu_state == "option":
                    self.option_menu_process(mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press)

                elif self.menu_state == "encyclopedia":
                    command = self.lorebook_process(self.main_ui_updater, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press)
                    if esc_press or command == "exit":
                        self.menu_state = "main_menu"  # change menu back to default 0

            self.main_ui_updater.draw(self.screen)
            pygame.display.update()
            self.clock.tick(60)
