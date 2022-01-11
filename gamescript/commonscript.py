import ast
import csv
import datetime
import math
import os
import re
from pathlib import Path

import pygame
import pygame.freetype
from gamescript import readstat, map, lorebook, weather, drama, battleui, menu, faction, popup, uniteditor


def read_terrain_data(main_dir):
    """Read map data and create map texture and their default variables"""
    # read terrain feature list
    feature_list = []
    with open(os.path.join(main_dir, "data", "map", "unit_terrainbonus.csv"), encoding="utf-8", mode="r") as edit_file:
        rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
        for row in rd:
            feature_list.append(row[1])  # get terrain feature combination name for folder
    edit_file.close()
    feature_list = feature_list[1:]

    empty_image = load_image(main_dir, "empty.png", "map/texture")  # empty texture image
    map_texture = []
    texture_folder = []
    for feature in feature_list:
        texture_folder.append(feature.replace(" ", "").lower())  # convert terrain feature list to lower case with no space
    texture_folder = list(set(texture_folder))  # list of terrian folder to load
    texture_folder = [item for item in texture_folder if item != ""]  # For now remove terrain with no planned name/folder yet
    for index, folder in enumerate(texture_folder):
        imgs = load_images(main_dir, ["map", "texture", folder], load_order=False)
        map_texture.append(imgs)

    # read terrain feature mode
    feature_mod = {}
    with open(os.path.join(main_dir, "data", "map", "unit_terrainbonus.csv"), encoding="utf-8", mode="r") as edit_file:
        rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
        run = 0  # for skipping the first row
        for row in rd:
            for n, i in enumerate(row):
                if run != 0:
                    if n == 12:  # effect list is at column 12
                        if "," in i:
                            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
                        elif i.isdigit():
                            row[n] = [int(i)]

                    elif n in (2, 3, 4, 5, 6, 7):  # other modifer column
                        if i != "":
                            row[n] = float(i) / 100
                        else:  # empty row assign 1.0 default
                            row[n] = 1.0

                    elif i.isdigit() or "-" in i:  # modifer bonus (including negative) in other column
                        row[n] = int(i)

            run += 1
            feature_mod[row[0]] = row[1:]
    edit_file.close()

    # set up default
    map.FeatureMap.main_dir = main_dir
    map.FeatureMap.feature_mod = feature_mod
    map.BeautifulMap.main_dir = main_dir

    map.BeautifulMap.texture_images = map_texture
    map.BeautifulMap.load_texture_list = texture_folder
    map.BeautifulMap.empty_image = empty_image

    return feature_mod, feature_list


def read_weather_data(main_dir):
    """Create weather related class"""
    all_weather = csv_read(main_dir, "weather.csv", ["data", "map", "weather"])
    weather_list = [item[0] for item in all_weather.values()][2:]
    strength_list = ["Light ", "Normal ", "Strong "]
    new_weather_list = []
    for item in weather_list:  # list of weather with different strength
        for strength in strength_list:
            new_weather_list.append(strength + item)

    weather_matter_imgs = []
    for weather_sprite in ("0", "1", "2", "3"):  # Load weather matter sprite image
        imgs = load_images(main_dir, ["map", "weather", weather_sprite], load_order=False)
        weather_matter_imgs.append(imgs)

    weather_effect_imgs = []
    for weather_effect in ("0", "1", "2", "3", "4", "5", "6", "7"):  # Load weather effect sprite image
        imgs = load_images(main_dir, ["map", "weather", "effect", weather_effect], load_order=False)
        # imgs = []
        # for img in imgsold:
        #     img = pygame.transform.scale(img, (screen_rect.width, screen_rect.height))
        #     imgs.append(img)
        weather_effect_imgs.append(imgs)

    imgs = load_images(main_dir, ["map", "weather", "icon"], load_order=False)  # Load weather icon
    weather.Weather.images = imgs
    return all_weather, new_weather_list, weather_matter_imgs, weather_effect_imgs


def read_map_data(main_dir, ruleset_folder):

    # Load map list
    read_folder = Path(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "map"))
    subdirectories = [x for x in read_folder.iterdir() if x.is_dir()]

    for index, file_map in enumerate(subdirectories):
        if "custom" in str(file_map):  # remove custom from this folder list to load
            subdirectories.pop(index)
            break

    preset_map_list = []  # map name list for map selection list
    preset_map_folder = []  # folder for reading later

    for file_map in subdirectories:
        preset_map_folder.append(str(file_map).split("\\")[-1])
        with open(os.path.join(str(file_map), "info.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[0] != "name":
                    preset_map_list.append(row[0])
        edit_file.close()

    # Load custom map list
    read_folder = Path(os.path.join(main_dir, "data", "ruleset", ruleset_folder, "map", "custom"))
    subdirectories = [x for x in read_folder.iterdir() if x.is_dir()]

    custom_map_list = []
    custom_map_folder = []

    for file_map in subdirectories:
        custom_map_folder.append(str(file_map).split("\\")[-1])
        with open(os.path.join(str(file_map), "info.csv"), encoding="utf-8", mode="r") as edit_file:
            rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
            for row in rd:
                if row[0] != "name":
                    custom_map_list.append(row[0])
        edit_file.close()

    return preset_map_list, preset_map_folder, custom_map_list, custom_map_folder


def read_faction_data(main_dir, ruleset_folder):
    faction.FactionData.main_dir = main_dir
    all_faction = faction.FactionData(option=ruleset_folder)
    imgs_old = load_images(main_dir, ["ruleset", ruleset_folder, "faction", "coa"],
                           load_order=False)  # coa_list images list
    imgs = []
    for img in imgs_old:
        imgs.append(img)
    coa = imgs
    faction_list = [item[0] for item in all_faction.faction_list.values()][1:]
    return all_faction, coa, faction_list


def make_encyclopedia_ui(main_dir, ruleset_folder, screen_scale, screen_rect):

    # v Encyclopedia related objects
    lorebook.Lorebook.concept_stat = csv_read(main_dir, "concept_stat.csv", ["data", "ruleset", ruleset_folder, "lore"])
    lorebook.Lorebook.concept_lore = csv_read(main_dir, "concept_lore.csv", ["data", "ruleset", ruleset_folder, "lore"])
    lorebook.Lorebook.history_stat = csv_read(main_dir, "history_stat.csv", ["data", "ruleset", ruleset_folder, "lore"])
    lorebook.Lorebook.history_lore = csv_read(main_dir, "history_lore.csv", ["data", "ruleset", ruleset_folder, "lore"])

    imgs = load_images(main_dir, ["ui", "lorebook_ui"], load_order=False)
    encyclopedia = lorebook.Lorebook(main_dir, screen_scale, screen_rect, imgs[0])  # encyclopedia sprite
    lore_name_list = lorebook.SubsectionList(screen_scale, encyclopedia.rect.topleft, imgs[1])

    imgs = load_images(main_dir, ["ui", "lorebook_ui", "button"], load_order=False)
    for index, img in enumerate(imgs):
        imgs[index] = pygame.transform.scale(img, (int(img.get_width() * screen_scale[0]),
                                                   int(img.get_height() * screen_scale[1])))
    lore_button_ui = [
        battleui.UIButton(encyclopedia.rect.topleft[0] + (imgs[0].get_width() + 5), encyclopedia.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[0], 0, 13),  # concept section button
        battleui.UIButton(encyclopedia.rect.topleft[0] + (imgs[0].get_width() + 5) * 2,
                          encyclopedia.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[1], 1, 13),  # history section button
        battleui.UIButton(encyclopedia.rect.topleft[0] + (imgs[0].get_width() + 5) * 3,
                          encyclopedia.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[2], 2, 13),  # faction section button
        battleui.UIButton(encyclopedia.rect.topleft[0] + (imgs[0].get_width() + 5) * 4,
                          encyclopedia.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[3], 3, 13),  # troop section button
        battleui.UIButton(encyclopedia.rect.topleft[0] + (imgs[0].get_width() + 5) * 5,
                          encyclopedia.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[4], 4, 13),  # troop equipment section button
        battleui.UIButton(encyclopedia.rect.topleft[0] + (imgs[0].get_width() + 5) * 6,
                          encyclopedia.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[5], 5, 13),  # troop status section button
        battleui.UIButton(encyclopedia.rect.topleft[0] + (imgs[0].get_width() + 5) * 7,
                          encyclopedia.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[6], 6, 13),  # troop skill section button
        battleui.UIButton(encyclopedia.rect.topleft[0] + (imgs[0].get_width() + 5) * 8,
                          encyclopedia.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[7], 7, 13),  # troop property section button
        battleui.UIButton(encyclopedia.rect.topleft[0] + (imgs[0].get_width() + 5) * 9,
                          encyclopedia.rect.topleft[1] - (imgs[0].get_height() / 2),
                          imgs[8], 8, 13),  # leader section button
        battleui.UIButton(encyclopedia.rect.topleft[0] + (imgs[0].get_width() + 5) * 10,
                          encyclopedia.rect.topleft[1] - (imgs[0].get_height() / 2), imgs[9], 9, 13),  # terrain section button
        battleui.UIButton(encyclopedia.rect.topleft[0] + (imgs[0].get_width() + 5) * 11,
                          encyclopedia.rect.topleft[1] - (imgs[0].get_height() / 2), imgs[10], 10, 13),  # weather section button
        battleui.UIButton(encyclopedia.rect.topleft[0] + (imgs[0].get_width() + 5) * 13,
                          encyclopedia.rect.topleft[1] - (imgs[0].get_height() / 2), imgs[12], 19, 13),  # close button
        battleui.UIButton(encyclopedia.rect.bottomleft[0] + (imgs[13].get_width()), encyclopedia.rect.bottomleft[1] - imgs[13].get_height(),
                          imgs[13], 20, 24),  # previous page button
        battleui.UIButton(encyclopedia.rect.bottomright[0] - (imgs[14].get_width()), encyclopedia.rect.bottomright[1] - imgs[14].get_height(),
                          imgs[14], 21, 24)]  # next page button
    page_button = (lore_button_ui[12], lore_button_ui[13])
    lore_scroll = battleui.UIScroller(lore_name_list.rect.topright, lore_name_list.image.get_height(),
                                          encyclopedia.max_subsection_show, layer=25)  # add subsection list scroller

    return encyclopedia, lore_name_list, lore_button_ui, page_button, lore_scroll


def make_editor_ui(main_dir, screen_scale, screen_rect, imgs, image_list):
    """Army editor ui and button"""

    bottom_height = screen_rect.height - image_list[0].get_height()
    box_img = load_image(main_dir, "unit_presetbox.png", "ui\\mainmenu_ui")
    unit_listbox = menu.ListBox(screen_scale, (0, screen_rect.height / 2.2),
                                box_img)  # box for showing unit preset list
    unit_presetname_scroll = battleui.UIScroller(unit_listbox.rect.topright, unit_listbox.image.get_height(),
                                                 unit_listbox.max_show, layer=14)  # preset name scroll
    preset_select_border = uniteditor.SelectedPresetBorder(unit_listbox.image.get_width() - int(15 * screen_scale[0]),
                                                           int(25 * screen_scale[1]))

    troop_listbox = menu.ListBox(screen_scale, (screen_rect.width / 1.19, 0), imgs[0])

    troop_scroll = battleui.UIScroller(troop_listbox.rect.topright, troop_listbox.image.get_height(),
                                       troop_listbox.max_show, layer=14)

    unit_delete_button = menu.MenuButton(screen_scale, image_list,
                                              pos=(image_list[0].get_width() / 2, bottom_height),
                                              text="Delete")
    unit_save_button = menu.MenuButton(screen_scale, image_list,
                                            pos=((screen_rect.width - (screen_rect.width - (image_list[0].get_width() * 1.7))),
                                                 bottom_height),
                                            text="Save")

    popup_listbox = menu.ListBox(screen_scale, (0, 0), box_img, 15)  # popup box need to be in higher layer
    popup_listscroll = battleui.UIScroller(popup_listbox.rect.topright,
                                           popup_listbox.image.get_height(),
                                           popup_listbox.max_show,
                                           layer=14)

    box_img = load_image(main_dir, "map_change.png", "ui\\mainmenu_ui")
    terrain_change_button = uniteditor.PreviewChangeButton(screen_scale, (screen_rect.width / 3, screen_rect.height), box_img,
                                                                "Temperate")  # start with temperate terrain
    feature_change_button = uniteditor.PreviewChangeButton(screen_scale, (screen_rect.width / 2, screen_rect.height), box_img,
                                                                "Plain")  # start with plain feature
    weather_change_button = uniteditor.PreviewChangeButton(screen_scale, (screen_rect.width / 1.5, screen_rect.height), box_img,
                                                                "Light Sunny")  # start with light sunny
    box_img = load_image(main_dir, "filter_box.png", "ui\\mainmenu_ui")  # filter box ui in editor
    filter_box = uniteditor.FilterBox(screen_scale, (screen_rect.width / 2.5, 0), box_img)
    img1 = load_image(main_dir, "team1_button.png", "ui\\mainmenu_ui")  # change unit slot to team 1 in editor
    img2 = load_image(main_dir, "team2_button.png", "ui\\mainmenu_ui")  # change unit slot to team 2 in editor
    team_change_button = battleui.SwitchButton(filter_box.rect.topleft[0] + 220, filter_box.rect.topleft[1] + 30,
                                               [img1, img2])
    img1 = load_image(main_dir, "show_button.png", "ui\\mainmenu_ui")  # show unit slot ui in editor
    img2 = load_image(main_dir, "hide_button.png", "ui\\mainmenu_ui")  # hide unit slot ui in editor
    slot_display_button = battleui.SwitchButton(filter_box.rect.topleft[0] + 80, filter_box.rect.topleft[1] + 30,
                                                [img1, img2])
    img1 = load_image(main_dir, "deploy_button.png",
                      "ui\\mainmenu_ui")  # deploy unit in unit slot to test map in editor
    deploy_button = battleui.UIButton(filter_box.rect.topleft[0] + 150, filter_box.rect.topleft[1] + 90, img1, 0)
    img1 = load_image(main_dir, "test_button.png", "ui\\mainmenu_ui")  # start test button in editor
    img2 = load_image(main_dir, "end_button.png", "ui\\mainmenu_ui")  # stop test button
    test_button = battleui.SwitchButton(155, 125, [img1, img2])  # TODO change later
    img1 = load_image(main_dir, "tick_box_no.png", "ui\\mainmenu_ui")  # start test button in editor
    img2 = load_image(main_dir, "tick_box_yes.png", "ui\\mainmenu_ui")  # stop test button
    filter_tick_box = [menu.TickBox(screen_scale, (filter_box.rect.bottomright[0] / 1.26,
                                                             filter_box.rect.bottomright[1] / 8), img1, img2, "meleeinf"),
                            menu.TickBox(screen_scale, (filter_box.rect.bottomright[0] / 1.26,
                                                             filter_box.rect.bottomright[1] / 1.7), img1, img2, "rangeinf"),
                            menu.TickBox(screen_scale, (filter_box.rect.bottomright[0] / 1.11,
                                                             filter_box.rect.bottomright[1] / 8), img1, img2, "meleecav"),
                            menu.TickBox(screen_scale, (filter_box.rect.bottomright[0] / 1.11,
                                                             filter_box.rect.bottomright[1] / 1.7), img1, img2, "rangecav")]
    warning_msg = uniteditor.WarningMsg(screen_scale, (test_button.rect.bottomleft[0], test_button.rect.bottomleft[1]))

    return unit_listbox, unit_presetname_scroll, preset_select_border, troop_listbox, troop_scroll, \
           unit_delete_button, unit_save_button, popup_listbox, popup_listscroll, terrain_change_button, \
           feature_change_button, weather_change_button, filter_box, team_change_button, slot_display_button, \
           deploy_button, test_button, filter_tick_box, warning_msg


def make_input_box(main_dir, screen_scale, screen_rect, image_list):
    """Input box popup"""
    input_ui_img = load_image(main_dir, "input_ui.png", "ui\\mainmenu_ui")
    input_ui = menu.InputUI(screen_scale, input_ui_img,
                                 (screen_rect.width / 2, screen_rect.height / 2))  # user text input ui box popup
    input_ok_button = menu.MenuButton(screen_scale, image_list,
                                           pos=(input_ui.rect.midleft[0] + image_list[0].get_width(),
                                                input_ui.rect.midleft[1] + image_list[0].get_height()),
                                           text="Confirm", layer=31)
    input_cancel_button = menu.MenuButton(screen_scale, image_list,
                                               pos=(input_ui.rect.midright[0] - image_list[0].get_width(),
                                                    input_ui.rect.midright[1] + image_list[0].get_height()),
                                               text="Cancel", layer=31)

    input_box = menu.InputBox(screen_scale, input_ui.rect.center, input_ui.image.get_width())  # user text input box

    confirm_ui = menu.InputUI(screen_scale, input_ui_img,
                                   (screen_rect.width / 2, screen_rect.height / 2))  # user confirm input ui box popup

    return input_ui, input_ok_button, input_cancel_button, input_box, confirm_ui


def load_game_data(self):
    """Load various self data and encyclopedia object"""
    main_dir = self.main_dir
    screen_rect = self.screen_rect
    Soundvolume = self.Soundvolume

    # v create subunit related class
    imgsold = load_images(self.main_dir, ["ui", "unit_ui", "weapon"])
    imgs = []
    for img in imgsold:
        x, y = img.get_width(), img.get_height()
        img = pygame.transform.scale(img,
                                     (int(x / 1.7), int(y / 1.7)))  # scale 1.7 seem to be most fitting as a placeholder
        imgs.append(img)
    self.allweapon = readstat.Weaponstat(self.main_dir, imgs, self.ruleset)  # Create weapon class

    imgs = load_images(self.main_dir, ["ui", "unit_ui", "armour"])
    self.allarmour = readstat.Armourstat(main_dir, imgs, self.ruleset)  # Create armour class

    self.status_imgs = load_images(self.main_dir, ["ui", "status_icon"], load_order=False)
    self.role_imgs = load_images(self.main_dir, ["ui", "role_icon"], load_order=False)
    self.trait_imgs = load_images(self.main_dir, ["ui", "trait_icon"], load_order=False)
    self.skill_imgs = load_images(self.main_dir, ["ui", "skill_icon"], load_order=False)

    cooldown = pygame.Surface((self.skill_imgs[0].get_width(), self.skill_imgs[0].get_height()), pygame.SRCALPHA)
    cooldown.fill((230, 70, 80, 200))  # red colour filter for skill cooldown timer
    battleui.SkillCardIcon.cooldown = cooldown

    active_skill = pygame.Surface((self.skill_imgs[0].get_width(), self.skill_imgs[0].get_height()), pygame.SRCALPHA)
    active_skill.fill((170, 220, 77, 200))  # green colour filter for skill active timer
    battleui.SkillCardIcon.active_skill = active_skill

    self.troop_data = readstat.Unitstat(main_dir, self.ruleset, self.ruleset_folder)

    # v create leader list
    imgs, order = load_images(self.main_dir, ["ruleset", self.ruleset_folder, "leader", "portrait"], load_order=False,
                              return_order=True)
    self.leader_stat = readstat.Leaderstat(main_dir, imgs, order, option=self.ruleset_folder)
    # ^ End leader

    # v Create gamebattle self ui objects
    self.mini_map = battleui.Minimap((screen_rect.width, screen_rect.height))

    # Popup Ui
    imgs = load_images(self.main_dir, ["ui", "popup_ui", "terrain_check"], load_order=False)
    popup.TerrainPopup.images = imgs
    popup.TerrainPopup.screen_rect = screen_rect
    imgs = load_images(self.main_dir, ["ui", "popup_ui", "drama_text"], load_order=False)
    drama.TextDrama.images = imgs

    topimage = load_images(self.main_dir, ["ui", "battle_ui"])

    self.eventlog = battleui.EventLog(topimage[23], (0, screen_rect.height))
    self.trooplog_button = battleui.UIButton(self.eventlog.pos[0] + (topimage[24].get_width() / 2), self.eventlog.pos[1] -
                                             self.eventlog.image.get_height() - (topimage[24].get_height() / 2), topimage[24], 0)  # troop tab log

    self.eventlog_button = [
        battleui.UIButton(self.trooplog_button.pos[0] + topimage[24].get_width(), self.trooplog_button.pos[1], topimage[25], 1),
        # army tab log button
        battleui.UIButton(self.trooplog_button.pos[0] + (topimage[24].get_width() * 2), self.trooplog_button.pos[1], topimage[26], 2),
        # leader tab log button
        battleui.UIButton(self.trooplog_button.pos[0] + (topimage[24].get_width() * 3), self.trooplog_button.pos[1],
                          topimage[27], 3),
        # subunit tab log button
        battleui.UIButton(self.trooplog_button.pos[0] + (topimage[24].get_width() * 5), self.trooplog_button.pos[1],
                          topimage[28], 4),
        # delete current tab log button
        battleui.UIButton(self.trooplog_button.pos[0] + (topimage[24].get_width() * 6), self.trooplog_button.pos[1],
                          topimage[29], 5)]
    # delete all log button

    self.eventlog_button = [self.trooplog_button] + self.eventlog_button
    self.button_ui.add(self.eventlog_button)

    self.log_scroll = battleui.UIScroller(self.eventlog.rect.topright, topimage[23].get_height(),
                                          self.eventlog.max_row_show)  # event log scroller
    self.eventlog.log_scroll = self.log_scroll  # Link scroller to ui since it is easier to do here with the current order

    self.troopcard_ui = battleui.GameUI(x=screen_rect.width - topimage[2].get_size()[0] / 2,
                                        y=(topimage[0].get_size()[1] * 2.5) + topimage[5].get_size()[1],
                                        image=topimage[2], icon="", ui_type="troopcard")
    self.game_ui.add(self.troopcard_ui)
    self.troopcard_ui.feature_list = self.feature_list  # add terrain feature list name to subunit card

    # Button related to subunit card and command
    self.troopcard_button = [battleui.UIButton(self.troopcard_ui.x - 152, self.troopcard_ui.y + 10, topimage[3], 0),
                             # subunit card description button
                             battleui.UIButton(self.troopcard_ui.x - 152, self.troopcard_ui.y - 70, topimage[4], 1),
                             # subunit card stat button
                             battleui.UIButton(self.troopcard_ui.x - 152, self.troopcard_ui.y - 30, topimage[7], 2),
                             # subunit card skill button
                             battleui.UIButton(self.troopcard_ui.x - 152, self.troopcard_ui.y + 50, topimage[22],
                                               3)]  # subunit card equipment button

    self.button_ui.add(self.troopcard_button)

    self.terrain_check = popup.TerrainPopup()  # popup box that show terrain information when right click on map
    self.button_name_popup = popup.OneLinePopup()  # popup box that show button name when mouse over
    self.leader_popup = popup.OneLinePopup()  # popup box that show leader name when mouse over
    self.effect_popup = popup.EffectIconPopup()  # popup box that show skill/trait/status name when mouse over

    drama.TextDrama.screen_rect = screen_rect
    self.drama_text = drama.TextDrama()  # message at the top of screen that show up for important event

    self.fps_count = battleui.FPScount()  # FPS number counter

    self.battledone_box = battleui.BattleDone(self.screen_scale, (self.screen_width / 2, self.screen_height / 2),
                                              topimage[-3], topimage[-4])
    self.gamedone_button = battleui.UIButton(self.battledone_box.pos[0],
                                             self.battledone_box.box_image.get_height() * 0.8, topimage[-2], layer=19)

    # v Esc menu related objects
    imgs = load_images(self.main_dir, ["ui", "battlemenu_ui"], load_order=False)
    menu.EscBox.images = imgs  # Create ESC Menu box
    menu.EscBox.screen_rect = screen_rect
    self.battle_menu = menu.EscBox()

    button_image = load_images(self.main_dir, ["ui", "battlemenu_ui", "button"], load_order=False)
    menu_rect_center0 = self.battle_menu.rect.center[0]
    menu_rect_center1 = self.battle_menu.rect.center[1]

    self.battle_menu_button = [
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 - 100), text="Resume", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 - 50), text="Encyclopedia", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1), text="Option", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 + 50), text="End Battle", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 + 100), text="Desktop", size=14)]

    self.esc_option_menu_button = [
        menu.EscButton(button_image, (menu_rect_center0 - 50, menu_rect_center1 + 70), text="Confirm", size=14),
        menu.EscButton(button_image, (menu_rect_center0 + 50, menu_rect_center1 + 70), text="Apply", size=14),
        menu.EscButton(button_image, (menu_rect_center0 + 150, menu_rect_center1 + 70), text="Cancel", size=14)]

    slider_image = load_images(self.main_dir, ["ui", "battlemenu_ui", "slider"], load_order=False)
    self.esc_slider_menu = [menu.SliderMenu(slider_image[0], slider_image[1:3],
                                            (menu_rect_center0 * 1.1, menu_rect_center1), Soundvolume, 0)]
    self.esc_value_box = [
        menu.ValueBox(slider_image[3], (self.battle_menu.rect.topright[0] * 1.2, menu_rect_center1), Soundvolume)]
    # ^ End esc menu objects

    # v profile box
    self.profile_name = self.profile_name
    img = load_image(self.main_dir, "profile_box.png", "ui\\mainmenu_ui")
    self.profile_box = menu.ProfileBox(self.screen_scale, img, (self.screen_width, 0),
                                       self.profile_name)  # profile name box at top right of screen at gamestart menu screen
    # ^ End profile box


def make_long_text(surface, text, pos, font, color=pygame.Color("black")):
    """Blit long text into separate row of text"""
    words = [word.split(" ") for word in text.splitlines()]  # 2D array where each row is a list of words
    space = font.size(" ")[0]  # the width of a space
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # reset x
                y += word_height  # start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # reset x
        y += word_height  # start on new row


def make_bar_list(main_dir, screen_scale, list_to_do, menu_image):
    """Make a drop down bar list option button"""
    bar_list = []
    img = load_image(main_dir, "bar_normal.jpg", "ui\\mainmenu_ui")
    img2 = load_image(main_dir, "bar_mouse.jpg", "ui\\mainmenu_ui")
    img3 = img2
    for index, bar in enumerate(list_to_do):
        bar_image = (img.copy(), img2.copy(), img3.copy())
        bar = menu.MenuButton(screen_scale, images=bar_image,
                              pos=(menu_image.pos[0], menu_image.pos[1] + img.get_height() * (index + 1)), text=bar)
        bar_list.append(bar)
    return bar_list


def load_base_button(main_dir):
    img = load_image(main_dir, "idle_button.png", ["ui", "mainmenu_ui"])
    img2 = load_image(main_dir, "mouse_button.png", ["ui", "mainmenu_ui"])
    img3 = load_image(main_dir, "click_button.png", ["ui", "mainmenu_ui"])
    return [img, img2, img3]


def text_objects(text, font):
    text_surface = font.render(text, True, (200, 200, 200))
    return text_surface, text_surface.get_rect()


def load_image(main_dir, file, subfolder=""):
    """loads an image, prepares it for play"""
    new_subfolder = subfolder
    if isinstance(new_subfolder, list):
        new_subfolder = ""
        for folder in subfolder:
            new_subfolder = os.path.join(new_subfolder, folder)
    this_file = os.path.join(main_dir, "data", new_subfolder, file)
    surface = pygame.image.load(this_file).convert_alpha()
    return surface


def load_images(main_dir, subfolder=None, load_order=True, return_order=False):
    """loads all images(files) in folder using loadorder list file use only png file"""
    imgs = []
    dir_path = os.path.join(main_dir, "data")
    if subfolder is not None:
        for folder in subfolder:
            dir_path = os.path.join(dir_path, folder)

    if load_order:  # load in the order of load_order file
        load_order_file = open(os.path.join(dir_path, "load_order.txt"), "r")
        load_order_file = ast.literal_eval(load_order_file.read())
        for file in load_order_file:
            imgs.append(load_image(main_dir, file, dir_path))
    else:  # load every file
        load_order_file = [f for f in os.listdir(dir_path) if f.endswith("." + "png")]  # read all file
        load_order_file.sort(key=lambda var: [int(x) if x.isdigit() else x for x in re.findall(r"[^0-9]|[0-9]+", var)])
        for file in load_order_file:
            imgs.append(load_image(main_dir, file, dir_path))

    if return_order is False:
        return imgs
    else:  # return order of the file as list
        load_order_file = [int(name.replace(".png", "")) for name in load_order_file]
        return imgs, load_order_file


def csv_read(maindir, file, subfolder=(), outputtype=0):
    """output type 0 = dict, 1 = list"""
    main_dir = maindir
    return_output = {}
    if outputtype == 1:
        return_output = []

    folder_dir = ""
    for folder in subfolder:
        folder_dir = os.path.join(folder_dir, folder)
    folder_dir = os.path.join(folder_dir, file)
    folder_dir = os.path.join(main_dir, folder_dir)
    with open(folder_dir, encoding="utf-8", mode="r") as edit_file:
        rd = csv.reader(edit_file, quoting=csv.QUOTE_ALL)
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit() or ("-" in i and re.search("[a-zA-Z]", i) is None):
                    row[n] = int(i)
            if outputtype == 0:
                return_output[row[0]] = row[1:]
            elif outputtype == 1:
                return_output.append(row)
        edit_file.close()
    return return_output


def load_sound(main_dir, file):
    file = os.path.join(main_dir, "data", "sound", file)
    sound = pygame.mixer.Sound(file)
    return sound


def edit_config(section, option, value, filename, config):
    config.set(section, option, value)
    with open(filename, "w") as configfile:
        config.write(configfile)


def trait_skill_blit(self):
    """For blitting skill and trait icon into subunit info ui"""
    screen_rect = self.screen_rect

    position = self.troopcard_ui.rect.topleft
    position = [position[0] + 70, position[1] + 60]  # start position
    start_row = position[0]

    for icon in self.skill_icon.sprites():
        icon.kill()

    for trait in self.troopcard_ui.value2[0]:
        self.skill_icon.add(
            battleui.SkillCardIcon(self.trait_imgs[0], (position[0], position[1]), 0,
                                   game_id=trait))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= screen_rect.width:
            position[1] += 30
            position[0] = start_row

    position = self.troopcard_ui.rect.topleft
    position = [position[0] + 70, position[1] + 100]
    start_row = position[0]

    for skill in self.troopcard_ui.value2[1]:
        self.skill_icon.add(
            battleui.SkillCardIcon(self.skill_imgs[0], (position[0], position[1]), 1,
                                   game_id=skill))  # For now use placeholder image 0
        position[0] += 40
        if position[0] >= screen_rect.width:
            position[1] += 30
            position[0] = start_row


def effect_icon_blit(self):
    """For blitting all status effect icon"""
    screen_rect = self.screen_rect

    position = self.troopcard_ui.rect.topleft
    position = [position[0] + 70, position[1] + 140]
    start_row = position[0]

    for icon in self.effect_icon.sprites():
        icon.kill()

    for status in self.troopcard_ui.value2[4]:
        self.effect_icon.add(battleui.SkillCardIcon(self.status_imgs[0], (position[0], position[1]), 4, game_id=status))
        position[0] += 40
        if position[0] >= screen_rect.width:
            position[1] += 30
            position[0] = start_row


def countdown_skill_icon(self):
    """Count down timer on skill icon for activate and cooldown time"""
    for skill in self.skill_icon:
        if skill.icon_type == 1:  # only do skill icon not trait
            cd = 0
            active_time = 0
            if skill.game_id in self.troopcard_ui.value2[2]:
                cd = int(self.troopcard_ui.value2[2][skill.game_id])
            if skill.game_id in self.troopcard_ui.value2[3]:
                active_time = int(self.troopcard_ui.value2[3][skill.game_id][3])
            skill.icon_change(cd, active_time)
    # for effect in self.effect_icon:
    #     cd = 0
    #     if effect.id in self.troopcard_ui.value2[4]:
    #         cd = int(self.troopcard_ui.value2[4][effect.id][3])
    #     effect.iconchange(cd, 0)


def rotation_xy(origin, point, angle):
    ox, oy = origin
    px, py = point
    x = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    y = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return pygame.Vector2(x, y)


def convert_str_time(event):
    for index, item in enumerate(event):
        new_time = datetime.datetime.strptime(item[1], "%H:%M:%S").time()
        new_time = datetime.timedelta(hours=new_time.hour, minutes=new_time.minute, seconds=new_time.second)
        event[index] = [item[0], new_time]
        if len(item) == 3:
            event[index].append(item[2])


def kill_effect_icon(self):
    for icon in self.skill_icon.sprites():
        icon.kill()
        del icon
    for icon in self.effect_icon.sprites():
        icon.kill()
        del icon


def setup_list(screen_scale, item_class, current_row, show_list, item_group, box, ui_class, layer=15):
    """generate list of subsection of the left side of encyclopedia"""
    row = 5 * screen_scale[1]
    column = 5 * screen_scale[0]
    pos = box.rect.topleft
    if current_row > len(show_list) - box.max_show:
        current_row = len(show_list) - box.max_show

    if len(item_group) > 0:  # remove previous sprite in the group before generate new one
        for stuff in item_group:
            stuff.kill()
            del stuff

    for index, item in enumerate(show_list):
        if index >= current_row:
            item_group.add(item_class(screen_scale, box, (pos[0] + column, pos[1] + row), item,
                                      layer=layer))  # add new subsection sprite to group
            row += (30 * screen_scale[1])  # next row
            if len(item_group) > box.max_show:
                break  # will not generate more than space allowed

        ui_class.add(*item_group)


def list_scroll(screen_scale, mouse_scroll_up, mouse_scroll_down, scroll, box, current_row, name_list, group, ui_class, layer=15):
    if mouse_scroll_up:
        current_row -= 1
        if current_row < 0:
            current_row = 0
        else:
            setup_list(screen_scale, menu.NameList, current_row, name_list, group, box, ui_class, layer=layer)
            scroll.change_image(new_row=current_row, log_size=len(name_list))

    elif mouse_scroll_down:
        current_row += 1
        if current_row + box.max_show - 1 < len(name_list):
            setup_list(screen_scale, menu.NameList, current_row, name_list, group, box, ui_class, layer=layer)
            scroll.change_image(new_row=current_row, log_size=len(name_list))
        else:
            current_row -= 1
    return current_row


def popout_lorebook(self, section, game_id):
    """open and draw enclycopedia at the specified subsection,
    used for when user right click at icon that has encyclopedia section"""
    self.game_state = 0
    self.battle_menu.mode = 2
    self.battle_ui.add(self.lorebook, self.lore_name_list, self.lore_scroll, *self.lore_button_ui)

    self.lorebook.change_section(section, self.lore_name_list, self.subsection_name, self.lore_scroll, self.page_button,
                                 self.battle_ui)
    self.lorebook.change_subsection(game_id, self.page_button, self.battle_ui)
    self.lore_scroll.change_image(new_row=self.lorebook.current_subsection_row)


def popup_list_open(self, new_rect, new_list, ui_type):
    """Move popup_listbox and scroll sprite to new location and create new name list baesd on type"""
    self.current_popup_row = 0

    if ui_type == "leader" or ui_type == "genre":
        self.popup_listbox.rect = self.popup_listbox.image.get_rect(topleft=new_rect)
    else:
        self.popup_listbox.rect = self.popup_listbox.image.get_rect(midbottom=new_rect)

    setup_list(self.screen_scale, menu.NameList, 0, new_list, self.popup_namegroup,
               self.popup_listbox, self.battle_ui, layer=19)

    self.popup_listscroll.pos = self.popup_listbox.rect.topright  # change position variable
    self.popup_listscroll.rect = self.popup_listscroll.image.get_rect(topleft=self.popup_listbox.rect.topright)  #
    self.popup_listscroll.change_image(new_row=0, log_size=len(new_list))

    if ui_type == "genre":
        self.main_ui.add(self.popup_listbox, *self.popup_namegroup, self.popup_listscroll)
    else:
        self.battle_ui.add(self.popup_listbox, *self.popup_namegroup, self.popup_listscroll)  # add the option list to screen

    self.popup_listbox.type = ui_type
