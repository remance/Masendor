import configparser
import csv
import gc
import glob
import os.path
import sys
from pathlib import Path

# import basic pygame modules
import pygame
import pygame.freetype
import screeninfo
from gamescript import map, weather, lorebook, drama, battleui, popup, menu, rangeattack, uniteditor, battle, leader, unit, subunit
from gamescript.common import utility
from gamescript.common.start import creation
from pygame.locals import *

direction_list = creation.direction_list

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
load_action = creation.load_action
load_animation_pool = creation.load_animation_pool
read_terrain_data = creation.read_terrain_data
read_weather_data = creation.read_weather_data
read_map_data = creation.read_map_data
read_faction_data = creation.read_faction_data
make_encyclopedia_ui = creation.make_encyclopedia_ui
make_input_box = creation.make_input_box
make_editor_ui = creation.make_editor_ui
load_icon_data = creation.load_icon_data
load_battle_data = creation.load_battle_data
load_option_menu = creation.load_option_menu
make_event_log = creation.make_event_log
make_esc_menu = creation.make_esc_menu
make_popup_ui = creation.make_popup_ui
make_time_ui = creation.make_time_ui
load_part_sprite_pool = creation.load_part_sprite_pool
load_effect_sprite_pool = creation.load_effect_sprite_pool
read_colour = creation.read_colour

version_name = "Dream Decision"

# Will keep leader, subunit, unit and other state as magic number since changing them take too much space, see below for referencing

unit_state_text = {0: "Idle", 1: "Walking", 2: "Running", 3: "Walk (M)", 4: "Run (M)", 5: "Walk (R)", 6: "Run (R)",
                   7: "Walk (F)", 8: "Run (F)", 10: "Fighting", 11: "shooting", 65: "Sleeping", 66: "Camping", 67: "Resting", 68: "Dancing",
                   69: "Partying", 95: "Disobey", 96: "Retreating", 97: "Collapse", 98: "Retreating", 99: "Broken", 100: "Destroyed"}

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

team_colour = unit.team_colour


def change_genre(self, genre):
    """Add new genre module here"""
    if type(genre) == int:
        self.genre = self.genre_list[genre].lower()
    else:
        self.genre = genre.lower()

    if self.genre == "tactical":
        from gamescript.tactical.start import begin
        MainMenu.change_source = begin.change_source
    elif self.genre == "arcade":
        from gamescript.arcade.start import begin
        MainMenu.change_source = begin.change_source

    subunit.change_subunit_genre(self.genre)
    unit.change_unit_genre(self.genre)
    battle.change_battle_genre(self.genre)

    self.genre_change_box.change_text(self.genre.capitalize())
    edit_config("DEFAULT", "genre", self.genre, "configuration.ini", self.config)


class MainMenu:
    leader_level = ("Commander", "Sub-General", "Sub-General", "Sub-Commander", "General", "Sub-General", "Sub-General",
                    "Advisor")  # Name of leader position in unit, the first 4 is for commander unit
    popup_list_open = utility.popup_list_open
    lorebook_process = lorebook.lorebook_process
    change_genre = change_genre
    create_sprite_pool = creation.create_sprite_pool

    def __init__(self, main_dir):
        pygame.init()  # Initialize pygame

        self.main_dir = main_dir

        # v Read config file
        config = configparser.ConfigParser()
        try:
            config.read_file(open("configuration.ini"))  # read config file
        except Exception:  # Create config file if not found with the default
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
        self.FULLSCREEN = int(self.config["DEFAULT"]["fullscreen"])
        self.master_volume = float(self.config["DEFAULT"]["master_volume"])
        self.profile_name = str(self.config["DEFAULT"]["player_Name"])
        self.genre = str(self.config["DEFAULT"]["genre"])
        self.ruleset = 1  # for now default historical ruleset only
        # ^ End read config

        # v Set the display mode
        self.screen_rect = Rect(0, 0, self.screen_width, self.screen_height)
        self.screen_scale = (self.screen_rect.width / 1920, self.screen_rect.height / 1080)
        self.window_style = 0
        if FULLSCREEN == 1:  # fullscreen = 1
            self.window_style = pygame.FULLSCREEN
        self.best_depth = pygame.display.mode_ok(self.screen_rect.size, self.window_style, 32)
        self.screen = pygame.display.set_mode(self.screen_rect.size, self.window_style | pygame.RESIZABLE, self.best_depth)
        # ^ End set display

        self.clock = pygame.time.Clock()

        self.loading = load_image(self.main_dir, self.screen_scale, "loading.png", "ui\\mainmenu_ui")
        self.loading = pygame.transform.scale(self.loading, self.screen_rect.size)
        self.game_intro(self.screen, self.clock, False)  # run intro

        # v Background image
        try:
            bgd_tile = load_image(self.main_dir, self.screen_scale, self.genre + ".png", "ui\\mainmenu_ui")
        except FileNotFoundError:
            bgd_tile = load_image(self.main_dir, self.screen_scale, "default.png", "ui\\mainmenu_ui")
        bgd_tile = pygame.transform.scale(bgd_tile, self.screen_rect.size)
        self.background = pygame.Surface(self.screen_rect.size)
        self.background.blit(bgd_tile, (0, 0))
        # ^ End background

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

        self.map_source = 0  # current selected map source
        self.team_selected = 1
        self.current_popup_row = 0

        # v Decorate the self window
        # icon = load_image(self.main_dir, "sword.jpg")
        # icon = pygame.transform.scale(icon, (32, 32))
        # pygame.display.set_icon(icon)
        # ^ End decorate

        # v Initialise groups and objects
        # main drawer for ui
        self.main_ui = pygame.sprite.LayeredUpdates()  # sprite drawer group

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
        self.battle_ui = pygame.sprite.LayeredUpdates()  # this is layer drawer for ui, all image pos should be based on the screen

        self.unit_updater = pygame.sprite.Group()  # updater for unit objects
        self.subunit_updater = pygame.sprite.Group()  # updater for subunit objects
        self.leader_updater = pygame.sprite.Group()  # updater for leader objects
        self.ui_updater = pygame.sprite.Group()  # updater for ui objects
        self.weather_updater = pygame.sprite.Group()  # updater for weather objects
        self.effect_updater = pygame.sprite.Group()  # updater for in-self effect objects (e.g. range melee_attack sprite)

        self.team0_unit = pygame.sprite.Group()  # team 0 units group
        self.team1_unit = pygame.sprite.Group()  # team 1 units group
        self.team2_unit = pygame.sprite.Group()  # team 2 units group

        self.team0_subunit = pygame.sprite.Group()  # team 0 units group
        self.team1_subunit = pygame.sprite.Group()  # team 1 units group
        self.team2_subunit = pygame.sprite.Group()  # team 2 units group

        self.subunit = pygame.sprite.Group()  # all subunits group

        self.army_leader = pygame.sprite.Group()  # all leaders group

        self.range_attacks = pygame.sprite.Group()  # all range_attacks group and maybe other range effect stuff later
        self.direction_arrows = pygame.sprite.Group()
        self.troop_number_sprite = pygame.sprite.Group()  # troop text number that appear next to unit sprite

        self.dead_unit = pygame.sprite.Group()  # dead subunit group

        self.button_ui = pygame.sprite.Group()  # buttons in battle group
        self.inspect_selected_border = pygame.sprite.Group()  # subunit selected border in inspect ui unit box

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
        # ^ End initialise

        # v Assign containers
        menu.MenuButton.containers = self.menu_button
        menu.MenuIcon.containers = self.menu_icon
        menu.SliderMenu.containers = self.menu_slider, self.slider_menu
        menu.ValueBox.containers = self.value_box

        menu.NameList.containers = self.map_namegroup
        menu.TeamCoa.containers = self.team_coa
        menu.ArmyStat.containers = self.army_stat

        menu.TickBox.containers = self.tick_box

        lorebook.SubsectionList.containers = self.lore_name_list
        lorebook.SubsectionName.containers = self.subsection_name, self.main_ui, self.battle_ui

        uniteditor.PreviewBox.main_dir = self.main_dir
        uniteditor.PreviewBox.effect_image = load_image(self.main_dir, self.screen_scale, "effect.png", "map")  # map special effect image

        # battle containers
        battleui.SwitchButton.containers = self.ui_updater
        battleui.SelectedSquad.containers = self.inspect_selected_border, self.unit_edit_border, self.main_ui, self.battle_ui
        battleui.SkillCardIcon.containers = self.skill_icon, self.battle_ui
        battleui.EffectCardIcon.containers = self.effect_icon, self.battle_ui
        battleui.ArmyIcon.containers = self.unit_icon, self.battle_ui
        battleui.TroopNumber.containers = self.troop_number_sprite, self.effect_updater, self.battle_camera
        battleui.DirectionArrow.containers = self.direction_arrows, self.effect_updater, self.battle_camera

        popup.OneLinePopup.containers = self.buttonname_popup, self.leader_popup
        popup.EffectIconPopup.containers = self.effect_popup

        rangeattack.RangeArrow.containers = self.range_attacks, self.effect_updater, self.battle_camera

        menu.EscButton.containers = self.battle_menu_button, self.escoption_menu_button

        weather.MatterSprite.containers = self.weather_matter, self.battle_ui, self.weather_updater
        weather.SpecialEffect.containers = self.weather_effect, self.battle_ui, self.weather_updater

        unit.Unit.containers = self.unit_updater
        subunit.Subunit.containers = self.subunit_updater, self.subunit, self.battle_camera
        leader.Leader.containers = self.army_leader, self.leader_updater
        # ^ End assign

        # v Main menu related stuff
        image_list = load_base_button(self.main_dir, self.screen_scale)
        self.preset_map_button = menu.MenuButton(self.screen_scale, image_list,
                                                 pos=(self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 8.5)),
                                                 menu_state="mainmenu", text="Preset Map")
        self.custom_map_button = menu.MenuButton(self.screen_scale, image_list,
                                                 pos=(self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 7)),
                                                 menu_state="mainmenu", text="Custom Map")
        self.game_edit_button = menu.MenuButton(self.screen_scale, image_list,
                                                pos=(self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 5.5)),
                                                menu_state="mainmenu", text="Unit Editor")
        self.lore_button = menu.MenuButton(self.screen_scale, image_list,
                                           pos=(self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 4)),
                                           menu_state="mainmenu", text="Encyclopedia")
        self.option_button = menu.MenuButton(self.screen_scale, image_list,
                                             pos=(self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 2.5)),
                                             menu_state="mainmenu", text="Option")
        self.quit_button = menu.MenuButton(self.screen_scale, image_list,
                                           pos=(self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height())),
                                           menu_state="mainmenu", text="Quit")
        self.mainmenu_button = (self.preset_map_button, self.custom_map_button, self.game_edit_button,
                                self.lore_button, self.option_button, self.quit_button)

        # Battle map select menu button
        battle_select_image = load_images(self.main_dir, self.screen_scale, ["ui", "mapselect_ui"], load_order=False)

        self.map_title = menu.MapTitle(self.screen_scale, (self.screen_rect.width / 2, 0))

        menu.ArmyStat.image = battle_select_image["stat.png"]

        self.map_description = menu.DescriptionBox(battle_select_image["map_description.png"], self.screen_scale,
                                                   (self.screen_rect.width / 2, self.screen_rect.height / 1.3))
        self.map_show = menu.MapShow(self.main_dir, self.screen_scale, (self.screen_rect.width / 2, self.screen_rect.height / 3))
        self.source_description = menu.DescriptionBox(battle_select_image["source_description.png"], self.screen_scale,
                                                      (self.screen_rect.width / 2, self.screen_rect.height / 1.3), text_size=24)

        bottom_height = self.screen_rect.height - image_list[0].get_height()
        self.select_button = menu.MenuButton(self.screen_scale, image_list, pos=(self.screen_rect.width - image_list[0].get_width(), bottom_height),
                                             text="Select")
        self.start_button = menu.MenuButton(self.screen_scale, image_list, pos=(self.screen_rect.width - image_list[0].get_width(), bottom_height),
                                            text="Start")
        self.map_back_button = menu.MenuButton(self.screen_scale, image_list,
                                               pos=(self.screen_rect.width - (self.screen_rect.width - image_list[0].get_width()), bottom_height),
                                               text="Back")
        self.map_select_button = (self.select_button, self.map_back_button)
        self.battle_setup_button = (self.start_button, self.map_back_button)

        self.map_listbox = menu.ListBox(self.screen_scale, (self.screen_rect.width / 25, self.screen_rect.height / 20),
                                        battle_select_image["name_list.png"])
        self.map_scroll = battleui.UIScroller(self.map_listbox.rect.topright, self.map_listbox.image.get_height(),
                                              self.map_listbox.max_show, layer=14)  # scroll bar for map list

        self.source_list_box = menu.ListBox(self.screen_scale, (0, 0), battle_select_image["top_box.png"])  # source list ui box
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

        self.source_name_list = [""]
        self.source_scale_text = [""]
        self.source_scale = [""]
        self.source_text = [""]

        # Unit and subunit editor button in game start menu

        self.unit_edit_button = menu.MenuButton(self.screen_scale, image_list,
                                                (self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 4)),
                                                text="Army Editor")
        self.subunit_create_button = menu.MenuButton(self.screen_scale, image_list,
                                                     (self.screen_rect.width / 2, self.screen_rect.height - (image_list[0].get_height() * 2.5)),
                                                     text="Troop Creator")
        self.editor_back_button = menu.MenuButton(self.screen_scale, image_list,
                                                  (self.screen_rect.width / 2, self.screen_rect.height - image_list[0].get_height()),
                                                  text="Back")
        self.editor_button = (self.unit_edit_button, self.subunit_create_button, self.editor_back_button)

        # Option menu button
        option_menu_dict = load_option_menu(self.main_dir, self.screen_scale, self.screen_rect, self.screen_width, self.screen_height,
                                            image_list, self.master_volume)
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
        if pygame.mixer:
            self.master_volume = float(self.master_volume / 100)
            pygame.mixer.music.set_volume(self.master_volume)
            self.SONG_END = pygame.USEREVENT + 1
            self.music_list = glob.glob(self.main_dir + "/data/sound/music/*.ogg")
            pygame.mixer.music.load(self.music_list[0])
            pygame.mixer.music.play(-1)
        # ^ End Main menu

        self.change_ruleset()

        # v Battle related stuffs
        unit_ui_images = load_images(self.main_dir, self.screen_scale, ["ui", "unit_ui"])
        subunit.Subunit.unit_ui_images = unit_ui_images

        subunit_icon_image = unit_ui_images["ui_squad_player.png"]
        self.icon_sprite_width = subunit_icon_image.get_width()
        self.icon_sprite_height = subunit_icon_image.get_height()

        self.fps_count = battleui.FPScount()  # FPS number counter
        self.battle_ui.add(self.fps_count)

        battle_ui_image = load_images(self.main_dir, self.screen_scale, ["ui", "battle_ui"], load_order=False)

        # Battle map
        self.battle_base_map = map.BaseMap()  # create base terrain map
        self.battle_feature_map = map.FeatureMap()  # create terrain feature map
        self.battle_height_map = map.HeightMap()  # create height map
        self.show_map = map.BeautifulMap(self.screen_scale)
        self.battle_camera.add(self.show_map)

        rangeattack.RangeArrow.height_map = self.battle_height_map
        subunit.Subunit.base_map = self.battle_base_map  # add battle map to subunit class
        subunit.Subunit.feature_map = self.battle_feature_map
        subunit.Subunit.height_map = self.battle_height_map

        self.status_images, self.role_images, self.trait_images, self.skill_images = load_icon_data(self.main_dir, self.screen_scale)

        self.mini_map = battleui.MiniMap((self.screen_rect.width, self.screen_rect.height), self.screen_scale)
        self.battle_ui.add(self.mini_map)

        # Game sprite Effect
        effect_images = load_images(self.main_dir, self.screen_scale, ["sprite", "effect"], load_order=False)
        # images = []
        # for images in imgsold:
        # x, y = images.get_width(), images.get_height()
        # images = pygame.transform.scale(images, (int(x ), int(y / 2)))
        # images.append(images)
        rangeattack.RangeArrow.images = [effect_images["arrow.png"]]
        rangeattack.RangeArrow.screen_scale = self.screen_scale

        # Time bar ui
        time_dict = make_time_ui(battle_ui_image)
        self.time_ui = time_dict["time_ui"]
        self.time_number = time_dict["time_number"]
        self.speed_number = time_dict["speed_number"]
        self.scale_ui = time_dict["scale_ui"]
        self.time_button = time_dict["time_button"]
        self.battle_ui.add(self.time_ui, self.time_number, self.speed_number)

        genre_battle_ui_image = load_images(self.main_dir, self.screen_scale, [self.genre, "ui", "battle_ui"], load_order=False)
        genre_icon_image = load_images(self.main_dir, self.screen_scale, [self.genre, "ui", "battle_ui", "commandbar_icon"], load_order=False)

        # Unit editor
        editor_dict = make_editor_ui(self.main_dir, self.screen_scale, self.screen_rect,
                                     load_image(self.main_dir, self.screen_scale, "name_list.png", "ui\\mapselect_ui"),
                                     load_base_button(self.main_dir, self.screen_scale), self.scale_ui, team_colour)
        self.unit_listbox = editor_dict["unit_listbox"]
        self.unit_preset_name_scroll = editor_dict["unit_preset_name_scroll"]
        self.preset_select_border = editor_dict["preset_select_border"]
        self.troop_listbox = editor_dict["troop_listbox"]
        self.troop_scroll = editor_dict["troop_scroll"]
        self.unit_delete_button = editor_dict["unit_delete_button"]
        self.unit_save_button = editor_dict["unit_save_button"]
        self.popup_listbox = editor_dict["popup_listbox"]
        self.popup_list_scroll = editor_dict["popup_list_scroll"]
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
        input_ui_dict = make_input_box(self.main_dir, self.screen_scale, self.screen_rect, load_base_button(self.main_dir, self.screen_scale))
        self.input_ui = input_ui_dict["input_ui"]
        self.input_ok_button = input_ui_dict["input_ok_button"]
        self.input_cancel_button = input_ui_dict["input_cancel_button"]
        self.input_box = input_ui_dict["input_box"]
        self.confirm_ui = input_ui_dict["confirm_ui"]
        self.input_button = (self.input_ok_button, self.input_cancel_button)
        self.input_ui_popup = (self.input_ui, self.input_box, self.input_ok_button, self.input_cancel_button)
        self.confirm_ui_popup = (self.confirm_ui, self.input_ok_button, self.input_cancel_button)

        # Army select list ui
        self.unit_selector = battleui.ArmySelect((0, 0), genre_battle_ui_image["unit_select_box.png"])
        self.select_scroll = battleui.UIScroller(self.unit_selector.rect.topright, genre_battle_ui_image["unit_select_box.png"].get_height(),
                                                 self.unit_selector.max_row_show)  # scroller for unit select ui

        self.command_ui = battleui.CommandBar(image=genre_battle_ui_image["command_box.png"],
                                              icon=genre_icon_image)  # Left top command ui with leader and unit behavious button

        self.ui_updater.add(self.command_ui)

        # Load all image of ui and icon from folder
        genre_icon_image = load_images(self.main_dir, self.screen_scale, ["ui", "battle_ui", "topbar_icon"], load_order=False)

        self.col_split_button = battleui.UIButton(genre_battle_ui_image["colsplit_button.png"], 0)  # unit split by column button
        self.row_split_button = battleui.UIButton(genre_battle_ui_image["rowsplit_button.png"], 1)  # unit split by row button

        self.decimation_button = battleui.UIButton(genre_battle_ui_image["decimation.png"], 1)

        # Right top bar ui that show rough information of selected battalions
        self.unitstat_ui = battleui.TopBar(image=battle_ui_image["topbar.png"], icon=genre_icon_image)
        self.unitstat_ui.unit_state_text = self.unit_state_text

        # Unit inspect information ui
        battleui.SelectedSquad.image = battle_ui_image["ui_subunit_clicked.png"]  # subunit border image always the last one
        self.inspect_button = battleui.UIButton(genre_battle_ui_image["army_inspect_button.png"], 1)  # unit inspect open/close button
        self.inspect_selected_border = battleui.SelectedSquad((0, 0))  # yellow border on selected subunit in inspect ui
        self.main_ui.remove(self.inspect_selected_border)  # remove subunit border sprite from start_set menu drawer

        self.inspect_ui = battleui.InspectUI(image=genre_battle_ui_image["army_inspect.png"])  # inspect ui that show subunit in selected unit
        self.ui_updater.add(self.inspect_ui)
        # v Subunit shown in inspect ui

        self.inspect_subunit = []

        # Behaviour button that once click switch to other mode for subunit behaviour
        skill_condition_button = [genre_battle_ui_image["skillcond_0.png"], genre_battle_ui_image["skillcond_1.png"], genre_battle_ui_image["skillcond_2.png"], genre_battle_ui_image["skillcond_3.png"]]
        shoot_condition_button = [genre_battle_ui_image["fire_0.png"], genre_battle_ui_image["fire_1.png"]]
        behaviour_button = [genre_battle_ui_image["hold_0.png"], genre_battle_ui_image["hold_1.png"], genre_battle_ui_image["hold_2.png"]]
        range_condition_button = [genre_battle_ui_image["minrange_0.png"], genre_battle_ui_image["minrange_1.png"]]
        arc_condition_button = [genre_battle_ui_image["arc_0.png"], genre_battle_ui_image["arc_1.png"], genre_battle_ui_image["arc_2.png"]]
        run_condition_button = [genre_battle_ui_image["runtoggle_0.png"], genre_battle_ui_image["runtoggle_1.png"]]
        melee_condition_button = [genre_battle_ui_image["meleeform_0.png"], genre_battle_ui_image["meleeform_1.png"], genre_battle_ui_image["meleeform_2.png"]]
        self.switch_button = [battleui.SwitchButton(skill_condition_button),  # skill condition button
                              battleui.SwitchButton(shoot_condition_button),  # fire at will button
                              battleui.SwitchButton(behaviour_button),  # behaviour button
                              battleui.SwitchButton(range_condition_button),  # shoot range button
                              battleui.SwitchButton(arc_condition_button),  # arc_shot button
                              battleui.SwitchButton(run_condition_button),  # toggle run button
                              battleui.SwitchButton(melee_condition_button)]  # toggle melee mode

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
        self.log_scroll = event_log_dict["log_scroll"]
        subunit.Subunit.event_log = self.event_log  # Assign event_log to subunit class to broadcast event to the log
        self.battle_ui.add(self.log_scroll)

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
        self.troop_card_ui.feature_list = self.feature_list  # add terrain feature list name to subunit card
        self.ui_updater.add(self.troop_card_ui)
        self.button_ui.add(self.troop_card_button)

        self.change_genre(self.genre)
        self.battle_game = battle.Battle(self, self.window_style)
        subunit.Subunit.battle = self.battle_game
        leader.Leader.battle = self.battle_game
        start_pos = [(self.screen_rect.width / 2) - (self.icon_sprite_width * 5),
                     (self.screen_rect.height / 2) - (self.icon_sprite_height * 4)]
        self.make_unit_slot(0, 0, range(0, 64), start_pos)  # make player custom unit slot
        # ^ End battle related stuffs

        # starting script
        self.main_ui.remove(*self.menu_button)  # remove all button from drawing
        self.menu_button.remove(
            *self.menu_button)  # remove all button at the start and add later depending on menu_state
        self.menu_button.add(*self.mainmenu_button)  # add only game start menu button back

        self.start_menu_ui_only = *self.menu_button, self.profile_box, self.genre_change_box  # ui that only appear at the start menu
        self.main_ui.add(*self.start_menu_ui_only)
        self.menu_state = "mainmenu"
        self.text_input_popup = (None, None)  # popup for text input state
        self.choosing_faction = True  # swap list between faction and subunit, always start with choose faction first as true

        pygame.mouse.set_visible(True)  # set mouse as visible

        self.run()

    def change_ruleset(self):

        self.faction_data, self.coa_list = read_faction_data(self.main_dir, self.screen_scale, self.ruleset_folder)
        self.weapon_data, self.armour_data, self.troop_data, self.leader_data = load_battle_data(self.main_dir, self.screen_scale, self.ruleset, self.ruleset_folder)
        subunit.Subunit.screen_scale = self.screen_scale
        subunit.Subunit.weapon_data = self.weapon_data
        subunit.Subunit.armour_data = self.armour_data
        subunit.Subunit.troop_data = self.troop_data
        subunit.Subunit.status_list = self.troop_data.status_list
        subunit.Subunit.subunit_state = self.subunit_state

        self.feature_mod, self.feature_list = read_terrain_data(self.main_dir)
        self.weather_data, self.weather_list, self.weather_matter_images, self.weather_effect_images = read_weather_data(
            self.main_dir, self.screen_scale)

        self.preset_map_list, self.preset_map_folder, self.custom_map_list, self.custom_map_folder = read_map_data(
            self.main_dir, self.ruleset_folder)

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
        lorebook.Lorebook.feature_mod = self.feature_mod
        lorebook.Lorebook.weather_data = self.weather_data
        lorebook.Lorebook.landmark_data = None
        lorebook.Lorebook.troop_grade_list = self.troop_data.grade_list
        lorebook.Lorebook.troop_class_list = self.troop_data.role
        lorebook.Lorebook.leader_class_list = self.leader_data.leader_class
        lorebook.Lorebook.mount_grade_list = self.troop_data.mount_grade_list
        lorebook.Lorebook.race_list = self.troop_data.race_list
        lorebook.Lorebook.screen_rect = self.screen_rect
        lorebook.Lorebook.main_dir = self.main_dir
        lorebook.Lorebook.unit_state_text = self.unit_state_text

        self.encyclopedia, self.lore_name_list, self.lore_button_ui, self.page_button, \
        self.lore_scroll = make_encyclopedia_ui(self.main_dir, self.ruleset_folder, self.screen_scale, self.screen_rect)

        self.generic_action_data = load_action(self.main_dir)
        subunit.Subunit.generic_action_data = self.generic_action_data
        animation_dict = load_animation_pool(self.main_dir)
        self.generic_animation_pool = animation_dict["generic_animation_pool"]

        self.skel_joint_list = animation_dict["skel_joint_list"]
        self.weapon_joint_list = animation_dict["weapon_joint_list"]

        pool_dict = load_part_sprite_pool(self.main_dir, [self.troop_data.race_list[key]["Name"] for key in self.troop_data.race_list])

        self.gen_body_sprite_pool = pool_dict["gen_body_sprite_pool"]
        self.gen_armour_sprite_pool = pool_dict["gen_armour_sprite_pool"]
        self.gen_weapon_sprite_pool = pool_dict["gen_weapon_sprite_pool"]

        self.effect_sprite_pool = load_effect_sprite_pool(self.main_dir)

        self.skin_colour_list, self.hair_colour_list = read_colour(self.main_dir)

        self.animation_sprite_pool = self.create_sprite_pool(direction_list, (150, 150), self.screen_scale)

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

    def back_mainmenu(self):
        self.menu_state = "mainmenu"

        self.main_ui.remove(*self.menu_button)

        self.menu_button.remove(*self.menu_button)
        self.menu_button.add(*self.mainmenu_button)

        self.main_ui.add(*self.start_menu_ui_only)

    def read_selected_map_data(self, map_list, file, source=False):
        if self.menu_state == "preset" or self.last_select == "preset":
            if source:
                data = csv_read(self.main_dir, file,
                                ["data", "ruleset", self.ruleset_folder, "map", map_list[self.current_map_select],
                                 str(self.map_source), self.genre])
            else:
                data = csv_read(self.main_dir, file,
                                ["data", "ruleset", self.ruleset_folder, "map", map_list[self.current_map_select]])
        else:
            data = csv_read(file, [self.main_dir, "data", "ruleset", self.ruleset_folder, "map/custom", map_list[self.current_map_select]])
        return data

    def make_team_coa(self, data, ui_class, one_team=False, team1_set_pos=None):
        for team in self.team_coa:
            team.kill()
            del team
        if team1_set_pos is None:
            team1_set_pos = (self.screen_rect.width / 2 - (400 * self.screen_scale[0]), self.screen_rect.height / 3)
        # position = self.map_show[0].get_rect()
        self.team_coa.add(menu.TeamCoa(self.screen_scale, team1_set_pos, self.coa_list[data[0]],
                                       1, self.faction_data.faction_list[data[0]]["Name"]))  # team 1

        if one_team is False:
            self.team_coa.add(menu.TeamCoa(self.screen_scale, (self.screen_rect.width / 2 + (400 * self.screen_scale[0]), self.screen_rect.height / 3),
                                           self.coa_list[data[1]], 2, self.faction_data.faction_list[data[1]]["Name"]))  # team 2
        ui_class.add(self.team_coa)

    def make_map(self, map_folder_list, map_list):
        # v Create map preview image
        if self.menu_state == "preset":
            map_images = load_images(self.main_dir, self.screen_scale, ["ruleset", self.ruleset_folder, "map",
                                                     map_folder_list[self.current_map_select]], load_order=False)
        else:
            map_images = load_images(self.main_dir, self.screen_scale, ["ruleset", self.ruleset_folder, "map/custom",
                                                     map_folder_list[self.current_map_select]], load_order=False)
        self.map_show.change_map(map_images["base.png"], map_images["feature.png"])
        self.main_ui.add(self.map_show)
        # ^ End map preview

        # v Create map title at the top
        self.map_title.change_name(map_list[self.current_map_select])
        self.main_ui.add(self.map_title)
        # ^ End map title

        # v Create map description
        data = self.read_selected_map_data(map_folder_list, "info.csv")
        description = [list(data.values())[1][0], list(data.values())[1][1]]
        self.map_description.change_text(description)
        self.main_ui.add(self.map_description)
        # ^ End map description

        self.make_team_coa([list(data.values())[1][2], list(data.values())[1][3]], self.main_ui)

    def make_unit_slot(self, game_id, troop_id, range_to_run, start_pos):
        width, height = 0, 0
        slot_number = 0  # Number of subunit based on the position in row and column
        for number in range_to_run:  # generate player unit slot for filling troop into preview unit
            width += self.icon_sprite_width
            dummy_subunit = subunit.Subunit(troop_id, game_id, self.unit_build_slot, (start_pos[0] + width, start_pos[1] + height),
                                            100, 100, [1, 1], self.genre, "edit")
            dummy_subunit.kill()  # not part of subunit in battle, remove from all groups
            self.subunit_build.add(dummy_subunit)
            slot_number += 1
            if slot_number % 8 == 0:  # Pass the last subunit in the row, go to the next one
                width = 0
                height += self.icon_sprite_height

            game_id += 1
        return game_id

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
                    if self.text_input_popup[0] is not None:  # event update to input box
                        if event.key == K_ESCAPE:
                            input_esc = True
                        elif self.text_input_popup[0] == "text_input":
                            self.input_box.user_input(event, key_press)
                    else:
                        if event.key == K_ESCAPE:
                            esc_press = True

                if event.type == QUIT or self.quit_button.event or (esc_press and self.menu_state == "mainmenu"):
                    self.quit_button.event = False
                    self.text_input_popup = ("confirm_input", "quit")
                    self.confirm_ui.change_instruction("Quit Game?")
                    self.main_ui.add(*self.confirm_ui_popup)

            self.mouse_pos = pygame.mouse.get_pos()
            # ^ End user input

            self.screen.blit(self.background, (0, 0))  # blit background over instead of clear() to reset screen

            if self.text_input_popup[0] is not None:  # currently, have input text pop up on screen, stop everything else until done
                for button in self.input_button:
                    button.update(self.mouse_pos, mouse_left_up, mouse_left_down, "any")

                if self.input_ok_button.event or key_press[pygame.K_RETURN] or key_press[pygame.K_KP_ENTER]:
                    self.input_ok_button.event = False

                    if self.text_input_popup[1] == "profile_name":
                        self.profile_name = self.input_box.text
                        self.profile_box.change_text(self.profile_name)

                        edit_config("DEFAULT", "playername", self.profile_name, "configuration.ini", self.config)

                    elif self.text_input_popup[1] == "quit":
                        pygame.time.wait(1000)
                        if pygame.mixer:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.unload()
                        pygame.quit()
                        sys.exit()

                    self.input_box.text_start("")
                    self.text_input_popup = (None, None)
                    self.main_ui.remove(*self.input_ui_popup)

                elif self.input_cancel_button.event or input_esc:
                    self.input_cancel_button.event = False
                    self.input_box.text_start("")
                    self.text_input_popup = (None, None)
                    self.main_ui.remove(*self.input_ui_popup, *self.confirm_ui_popup)

            elif self.text_input_popup == (None, None):
                self.menu_button.update(self.mouse_pos, mouse_left_up, mouse_left_down, self.menu_state)
                if self.menu_state == "mainmenu":

                    if self.preset_map_button.event:  # preset map list menu
                        self.menu_state = "preset"
                        self.last_select = self.menu_state
                        self.preset_map_button.event = False
                        self.main_ui.remove(*self.start_menu_ui_only, self.popup_listbox, self.popup_list_scroll,
                                            *self.popup_namegroup)
                        self.menu_button.remove(*self.menu_button)

                        setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.preset_map_list, self.map_namegroup, self.map_listbox,
                                   self.main_ui)
                        self.make_map(self.preset_map_folder, self.preset_map_list)

                        self.menu_button.add(*self.map_select_button)
                        self.main_ui.add(*self.map_select_button, self.map_listbox, self.map_title, self.map_scroll)

                    elif self.custom_map_button.event:  # custom map list menu
                        self.menu_state = "custom"
                        self.last_select = self.menu_state
                        self.custom_map_button.event = False
                        self.main_ui.remove(*self.start_menu_ui_only, self.popup_listbox, self.popup_list_scroll,
                                            *self.popup_namegroup)
                        self.menu_button.remove(*self.menu_button)

                        setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.custom_map_list, self.map_namegroup, self.map_listbox,
                                   self.main_ui)
                        self.make_map(self.custom_map_folder, self.custom_map_list)

                        self.menu_button.add(*self.map_select_button)
                        self.main_ui.add(*self.map_select_button, self.map_listbox, self.map_title, self.map_scroll)

                    elif self.game_edit_button.event:  # custom subunit/sub-subunit editor menu
                        self.menu_state = "gamecreator"
                        self.game_edit_button.event = False
                        self.main_ui.remove(*self.start_menu_ui_only, self.popup_listbox, self.popup_list_scroll,
                                            *self.popup_namegroup)
                        self.menu_button.remove(*self.menu_button)

                        self.menu_button.add(*self.editor_button)
                        self.main_ui.add(*self.editor_button)

                    elif self.option_button.event:  # change start_set menu to option menu
                        self.menu_state = "option"
                        self.option_button.event = False
                        self.main_ui.remove(*self.start_menu_ui_only, self.popup_listbox, self.popup_list_scroll,
                                            *self.popup_namegroup)
                        self.menu_button.remove(*self.menu_button)

                        self.menu_button.add(*self.option_menu_button)
                        self.main_ui.add(*self.menu_button, self.option_menu_slider, self.value_box)
                        self.main_ui.add(*self.option_icon_list)

                    elif self.lore_button.event:  # open encyclopedia
                        self.before_lore_state = self.menu_state
                        self.menu_state = "encyclopedia"
                        self.main_ui.add(self.encyclopedia, self.lore_name_list, *self.lore_button_ui,
                                         self.lore_scroll)  # add sprite related to encyclopedia
                        self.encyclopedia.change_section(0, self.lore_name_list, self.subsection_name, self.lore_scroll, self.page_button, self.main_ui)
                        self.lore_button.event = False

                    elif mouse_left_up and self.profile_box.rect.collidepoint(self.mouse_pos):
                        self.text_input_popup = ("text_input", "profile_name")
                        self.input_box.text_start(self.profile_name)
                        self.input_ui.change_instruction("Profile Name:")
                        self.main_ui.add(self.input_ui_popup)

                    elif mouse_left_up and self.genre_change_box.rect.collidepoint(self.mouse_pos):
                        self.popup_list_open(self.genre_change_box.rect.bottomleft, self.genre_list, "genre")

                    elif self.popup_listbox in self.main_ui:
                        if self.popup_listbox.rect.collidepoint(self.mouse_pos):
                            self.ui_click = True
                            for index, name in enumerate(self.popup_namegroup):
                                if name.rect.collidepoint(self.mouse_pos) and mouse_left_up:  # click on name in list
                                    self.change_genre(index)

                                    for thisname in self.popup_namegroup:  # remove troop name list
                                        thisname.kill()
                                        del thisname

                                    self.main_ui.remove(self.popup_listbox, self.popup_list_scroll)
                                    break

                        elif self.popup_list_scroll.rect.collidepoint(self.mouse_pos):  # scrolling on list
                            self.ui_click = True
                            self.current_popup_row = self.popup_list_scroll.user_input(
                                self.mouse_pos)  # update the scroller and get new current subsection
                            setup_list(self.screen_scale, menu.NameList, self.current_popup_row, self.genre_list,
                                       self.popup_namegroup, self.popup_listbox, self.main_ui)

                        # else:
                        #     self.main_ui.remove(self.popup_listbox, self.popup_list_scroll, *self.popup_namegroup)

                elif self.menu_state == "preset" or self.menu_state == "custom":
                    if mouse_left_up or mouse_left_down:
                        if mouse_left_up:
                            for index, name in enumerate(self.map_namegroup):  # user click on map name, change map
                                if name.rect.collidepoint(self.mouse_pos):
                                    self.current_map_select = index
                                    if self.menu_state == "preset":  # make new map image
                                        self.make_map(self.preset_map_folder, self.preset_map_list)
                                    else:
                                        self.make_map(self.custom_map_folder, self.custom_map_list)
                                    break

                        if self.map_scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroll
                            self.current_map_row = self.map_scroll.user_input(
                                self.mouse_pos)  # update the scroll and get new current subsection
                            setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.preset_map_list,
                                       self.map_namegroup, self.map_listbox,
                                       self.main_ui)

                    if self.map_listbox.rect.collidepoint(self.mouse_pos):
                        self.current_map_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down, self.map_scroll, self.map_listbox,
                                                           self.current_map_row, self.preset_map_list, self.map_namegroup, self.main_ui)

                    if self.map_back_button.event or esc_press:
                        self.map_back_button.event = False
                        self.current_map_row = 0
                        self.current_map_select = 0

                        self.main_ui.remove(self.map_listbox, self.map_show, self.map_scroll, self.map_description,
                                            self.team_coa, self.map_title)

                        for group in (self.map_namegroup, self.team_coa):  # remove no longer related sprites in group
                            for stuff in group:
                                stuff.kill()
                                del stuff

                        self.back_mainmenu()

                    elif self.select_button.event:  # select this map, go to prepare setup
                        self.current_source_row = 0
                        self.menu_state = "battlemapset"
                        self.select_button.event = False

                        self.main_ui.remove(*self.map_select_button, self.map_listbox, self.map_scroll, self.map_description)
                        self.menu_button.remove(*self.map_select_button)

                        for stuff in self.map_namegroup:  # remove map name item
                            stuff.kill()
                            del stuff

                        for team in self.team_coa:
                            if self.team_selected == team.team:
                                team.change_select(True)

                        openfolder = self.preset_map_folder
                        if self.last_select == "custom":
                            openfolder = self.custom_map_folder
                        try:
                            self.source_list = self.read_selected_map_data(openfolder, "source.csv")
                            self.source_name_list = [value[0] for value in list(self.source_list.values())[1:]]
                            self.source_scale_text = [value[1] for value in list(self.source_list.values())[1:]]
                            self.source_scale = [(float(value[2]), float(value[3]), float(value[4]), float(value[5]))
                                                 for value in
                                                 list(self.source_list.values())[1:]]
                            self.source_text = [value[-1] for value in list(self.source_list.values())[1:]]
                        except Exception:  # no source.csv make empty list
                            self.source_name_list = [""]
                            self.source_scale_text = [""]
                            self.source_scale = [""]
                            self.source_text = [""]

                        setup_list(self.screen_scale, menu.NameList, self.current_source_row, self.source_name_list,
                                   self.source_namegroup, self.source_list_box, self.main_ui)

                        self.source_scroll = battleui.UIScroller(self.source_list_box.rect.topright,
                                                                 self.source_list_box.image.get_height(),
                                                                 self.source_list_box.max_show,
                                                                 layer=16)  # scroll bar for source list

                        for index, team in enumerate(self.team_coa):
                            if index == 0:
                                self.army_stat.add(
                                    menu.ArmyStat(self.screen_scale, (team.rect.bottomleft[0], self.screen_rect.height / 1.5)))  # left army stat
                            else:
                                self.army_stat.add(
                                    menu.ArmyStat(self.screen_scale, (team.rect.bottomright[0], self.screen_rect.height / 1.5)))  # right army stat

                        self.change_source([self.source_scale_text[self.map_source], self.source_text[self.map_source]],
                                           self.source_scale[self.map_source])

                        self.menu_button.add(*self.battle_setup_button)
                        self.main_ui.add(*self.battle_setup_button, self.map_option_box, self.enactment_tick_box,
                                         self.source_list_box,
                                         self.source_scroll, self.army_stat)

                elif self.menu_state == "battlemapset":
                    if mouse_left_up or mouse_left_down:
                        if mouse_left_up:
                            for this_team in self.team_coa:  # User select any team by clicking on coat of arm
                                if this_team.rect.collidepoint(self.mouse_pos):
                                    self.team_selected = this_team.team
                                    this_team.change_select(True)

                                    # Reset team selected on team user not currently selected
                                    for this_team2 in self.team_coa:
                                        if self.team_selected != this_team2.team and this_team2.selected:
                                            this_team2.change_select(False)
                                    break

                            for index, name in enumerate(self.source_namegroup):  # user select source
                                if name.rect.collidepoint(self.mouse_pos):  # click on source name
                                    self.map_source = index
                                    self.change_source(
                                        [self.source_scale_text[self.map_source], self.source_text[self.map_source]],
                                        self.source_scale[self.map_source])
                                    break

                            for box in self.tick_box:
                                if box in self.main_ui and box.rect.collidepoint(self.mouse_pos):
                                    if box.tick is False:
                                        box.change_tick(True)
                                    else:
                                        box.change_tick(False)
                                    if box.option == "enactment":
                                        self.enactment = box.tick

                        if self.source_scroll.rect.collidepoint(self.mouse_pos):  # click on subsection list scroll
                            self.current_source_row = self.source_scroll.user_input(
                                self.mouse_pos)  # update the scroll and get new current subsection
                            setup_list(self.screen_scale, menu.NameList, self.current_source_row, self.source_list,
                                       self.source_namegroup,
                                       self.source_list_box, self.main_ui)
                    if self.source_list_box.rect.collidepoint(self.mouse_pos):
                        self.current_source_row = list_scroll(self.screen_scale, mouse_scroll_up, mouse_scroll_down,
                                                              self.source_scroll, self.source_list_box,
                                                              self.current_source_row, self.source_list,
                                                              self.source_namegroup, self.main_ui)

                    if self.map_back_button.event or esc_press:
                        self.menu_state = self.last_select
                        self.map_back_button.event = False
                        self.main_ui.remove(*self.menu_button, self.map_listbox, self.map_option_box,
                                            self.enactment_tick_box,
                                            self.source_list_box, self.source_scroll, self.source_description)
                        self.menu_button.remove(*self.menu_button)

                        # v Reset selected team
                        for team in self.team_coa:
                            team.change_select(False)
                        self.team_selected = 1
                        # ^ End reset selected team

                        self.map_source = 0
                        self.map_show.change_mode(0)  # revert map preview back to without unit dot

                        for group in (self.source_namegroup, self.army_stat):
                            for stuff in group:  # remove map name item
                                stuff.kill()
                                del stuff

                        if self.menu_state == "preset":  # regenerate map name list
                            setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.preset_map_list, self.map_namegroup, self.map_listbox,
                                       self.main_ui)
                        else:
                            setup_list(self.screen_scale, menu.NameList, self.current_map_row, self.custom_map_list, self.map_namegroup, self.map_listbox,
                                       self.main_ui)

                        self.menu_button.add(*self.map_select_button)
                        self.main_ui.add(*self.map_select_button, self.map_listbox, self.map_scroll, self.map_description)

                    elif self.start_button.event:  # start self button
                        self.start_button.event = False
                        self.battle_game.prepare_new_game(self.ruleset, self.ruleset_folder, self.team_selected,
                                                          self.enactment,
                                                          self.preset_map_folder[self.current_map_select],
                                                          self.map_source,
                                                          self.source_scale[self.map_source], "battle")
                        self.battle_game.run_game()
                        pygame.mixer.music.unload()
                        pygame.mixer.music.set_endevent(self.SONG_END)
                        pygame.mixer.music.load(self.music_list[0])
                        pygame.mixer.music.play(-1)
                        gc.collect()  # collect no longer used object in previous battle from memory

                elif self.menu_state == "gamecreator":
                    if self.editor_back_button.event or esc_press:
                        self.editor_back_button.event = False
                        self.back_mainmenu()

                    elif self.unit_edit_button.event:
                        self.unit_edit_button.event = False
                        self.battle_game.prepare_new_game(self.ruleset, self.ruleset_folder, 1, True, None, 1, (1, 1, 1, 1), "uniteditor")
                        self.battle_game.run_game()
                        pygame.mixer.music.unload()
                        pygame.mixer.music.set_endevent(self.SONG_END)
                        pygame.mixer.music.load(self.music_list[0])
                        pygame.mixer.music.play(-1)

                elif self.menu_state == "option":
                    for bar in self.resolution_bar:  # loop to find which resolution bar is selected, this happens outside of clicking check below
                        if bar.event:
                            bar.event = False

                            self.resolution_drop.change_state(bar.text)  # change button value based on new selected value
                            resolution_change = bar.text.split()
                            self.new_screen_width = resolution_change[0]
                            self.new_screen_height = resolution_change[2]

                            edit_config("DEFAULT", "screen_width", self.new_screen_width, "configuration.ini",
                                        self.config)
                            edit_config("DEFAULT", "screen_height", self.new_screen_height, "configuration.ini",
                                        self.config)
                            self.screen = pygame.display.set_mode(self.screen_rect.size,
                                                                  self.window_style | pygame.RESIZABLE, self.best_depth)

                            self.menu_button.remove(self.resolution_bar)

                            break

                    if self.back_button.event or esc_press:  # back to start_set menu
                        self.back_button.event = False

                        self.main_ui.remove(*self.option_icon_list, self.option_menu_slider, self.value_box)

                        self.back_mainmenu()

                    if mouse_left_up or mouse_left_down:
                        self.main_ui.remove(self.resolution_bar)

                        if self.resolution_drop.rect.collidepoint(self.mouse_pos):  # click on resolution bar
                            if self.resolution_bar in self.main_ui:  # remove the bar list if click again
                                self.main_ui.remove(self.resolution_bar)
                                self.menu_button.remove(self.resolution_bar)
                            else:  # add bar list
                                self.main_ui.add(self.resolution_bar)
                                self.menu_button.add(self.resolution_bar)

                        elif self.volume_slider.rect.collidepoint(self.mouse_pos) and (
                                mouse_left_down or mouse_left_up):  # mouse click on slider bar
                            self.volume_slider.user_input(self.mouse_pos,
                                                      self.value_box[0])  # update slider button based on mouse value
                            self.master_volume = float(
                                self.volume_slider.value / 100)  # for now only music volume slider exist
                            edit_config("DEFAULT", "master_volume", str(self.volume_slider.value), "configuration.ini",
                                        self.config)
                            pygame.mixer.music.set_volume(self.master_volume)

                elif self.menu_state == "encyclopedia":
                    command = self.lorebook_process(self.main_ui, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press)
                    if esc_press or command == "exit":
                        self.menu_state = "mainmenu"  # change menu back to default 0

            self.main_ui.draw(self.screen)
            pygame.display.update()
            self.clock.tick(60)
