import csv
import os
import random
from pathlib import Path

import pygame
from gamescript import weather, battleui, lorebook, menu, uniteditor, datastat, popup, map
from gamescript.common import utility, animation
from gamescript.common.subunit import common_subunit_setup

make_sprite = common_subunit_setup.make_sprite
load_image = utility.load_image
load_images = utility.load_images
csv_read = utility.csv_read
make_bar_list = utility.make_bar_list
stat_convert = utility.stat_convert


def read_battle_list_data(main_dir, ruleset_folder):
    """Load battle map list"""
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
                if row[0] != "Name":
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
                if row[0] != "Name":
                    custom_map_list.append(row[0])
        edit_file.close()

    return preset_map_list, preset_map_folder, custom_map_list, custom_map_folder


def make_encyclopedia(main_dir, ruleset_folder, screen_scale, screen_rect):
    """Create Encyclopedia related objects"""
    lorebook.Lorebook.concept_stat = csv_read(main_dir, "concept_stat.csv",
                                              ["data", "ruleset", ruleset_folder, "lore"], header_key=True)
    lorebook.Lorebook.concept_lore = csv_read(main_dir, "concept_lore.csv", ["data", "ruleset", ruleset_folder, "lore"])
    lorebook.Lorebook.history_stat = csv_read(main_dir, "history_stat.csv",
                                              ["data", "ruleset", ruleset_folder, "lore"], header_key=True)
    lorebook.Lorebook.history_lore = csv_read(main_dir, "history_lore.csv", ["data", "ruleset", ruleset_folder, "lore"])

    encyclopedia_images = load_images(main_dir, screen_scale, ["ui", "lorebook_ui"], load_order=False)
    encyclopedia = lorebook.Lorebook(main_dir, screen_scale, screen_rect, encyclopedia_images["encyclopedia.png"])  # encyclopedia sprite
    lore_name_list = lorebook.SubsectionList(screen_scale, encyclopedia.rect.topleft, encyclopedia_images["section_list.png"])

    lore_button_images = load_images(main_dir, screen_scale, ["ui", "lorebook_ui", "button"], load_order=False)
    for image in lore_button_images:  # scale button image
        lore_button_images[image] = pygame.transform.scale(lore_button_images[image], (int(lore_button_images[image].get_width() * screen_scale[0]),
                                                   int(lore_button_images[image].get_height() * screen_scale[1])))
    lore_button_ui = [battleui.UIButton(lore_button_images["concept.png"], 0, 13),  # concept section button
                      battleui.UIButton(lore_button_images["history.png"], 1, 13),  # history section button
                      battleui.UIButton(lore_button_images["faction.png"], 2, 13),  # faction section button
                      battleui.UIButton(lore_button_images["troop.png"], 3, 13),  # troop section button
                      battleui.UIButton(lore_button_images["equipment.png"], 4, 13),  # troop equipment section button
                      battleui.UIButton(lore_button_images["status.png"], 5, 13),  # troop status section button
                      battleui.UIButton(lore_button_images["skill.png"], 6, 13),  # troop skill section button
                      battleui.UIButton(lore_button_images["property.png"], 7, 13),  # troop property section button
                      battleui.UIButton(lore_button_images["leader.png"], 8, 13),  # leader section button
                      battleui.UIButton(lore_button_images["terrain.png"], 9, 13),  # terrain section button
                      battleui.UIButton(lore_button_images["weather.png"], 10, 13),  # weather section button
                      battleui.UIButton(lore_button_images["close.png"], "close", 13),  # close button
                      battleui.UIButton(lore_button_images["previous.png"], "previous", 24),  # previous page button
                      battleui.UIButton(lore_button_images["next.png"], "next", 24)]  # next page button

    lore_button_ui[0].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() / 2),
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[1].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 1.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[2].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 2.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[3].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 3.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[4].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 4.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[5].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 5.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[6].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 6.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[7].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 7.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[8].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 8.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[9].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 9.5,
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[10].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 10.5,
                                   encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[11].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept.png"].get_width() * 1.1) * 11.5,
                                   encyclopedia.rect.topleft[1] - (lore_button_images["concept.png"].get_height() / 2)))
    lore_button_ui[12].change_pos((encyclopedia.rect.bottomleft[0] + (lore_button_images["previous.png"].get_width()),
                                   encyclopedia.rect.bottomleft[1] - lore_button_images["previous.png"].get_height()))
    lore_button_ui[13].change_pos((encyclopedia.rect.bottomright[0] - (lore_button_images["next.png"].get_width()),
                                   encyclopedia.rect.bottomright[1] - lore_button_images["next.png"].get_height()))
    page_button = (lore_button_ui[12], lore_button_ui[13])
    lore_scroll = battleui.UIScroller(lore_name_list.rect.topright, lore_name_list.image.get_height(),
                                          encyclopedia.max_subsection_show, layer=25)  # add subsection list scroller

    return encyclopedia, lore_name_list, lore_button_ui, page_button, lore_scroll


def make_battle_ui(battle_ui_image, battle_icon_image):
    time_ui = battleui.TimeUI(battle_ui_image["timebar.png"])
    time_number = battleui.Timer(time_ui.rect.topleft)  # time number on time ui
    speed_number = battleui.SpeedNumber(1)  # self speed number on the time ui

    image = pygame.Surface((battle_ui_image["timebar.png"].get_width(), 15))
    scale_ui = battleui.ScaleUI(image)

    time_button = [battleui.UIButton(battle_ui_image["pause.png"], "pause"),  # time pause button
                        battleui.UIButton(battle_ui_image["timedec.png"], "decrease"),  # time decrease button
                        battleui.UIButton(battle_ui_image["timeinc.png"], "increase")]  # time increase button

    # Army select list ui
    unit_selector = battleui.UnitSelector((0, 0), battle_ui_image["unit_select_box.png"])
    unit_selector_scroll = battleui.UIScroller(unit_selector.rect.topright,
                                               battle_ui_image["unit_select_box.png"].get_height(),
                                               unit_selector.max_row_show)  # scroll for unit select ui

    # Right top bar ui that show rough information of selected battalions
    unitstat_ui = battleui.TopBar(battle_ui_image["topbar.png"], battle_icon_image)

    return {"time_ui": time_ui, "time_number": time_number, "speed_number": speed_number, "scale_ui": scale_ui,
            "time_button": time_button, "unit_selector": unit_selector, "unit_selector_scroll": unit_selector_scroll,
            "unitstat_ui": unitstat_ui}


def make_editor_ui(main_dir, screen_scale, screen_rect, listbox_image, image_list, scale_ui, colour, updater):
    """Create army editor ui and button"""

    bottom_height = screen_rect.height - image_list[0].get_height()
    box_image = load_image(main_dir, screen_scale, "unit_presetbox.png", "ui\\mainmenu_ui")
    unit_listbox = menu.ListBox(screen_scale, (0, screen_rect.height / 2.2),
                                box_image)  # box for showing unit preset list
    unit_preset_name_scroll = battleui.UIScroller(unit_listbox.rect.topright, unit_listbox.image.get_height(),
                                                  unit_listbox.max_row_show, layer=14)  # preset name scroll
    preset_select_border = uniteditor.SelectedPresetBorder((unit_listbox.image.get_width() * 0.96, int(30 * screen_scale[1])))

    troop_listbox = menu.ListBox(screen_scale, (screen_rect.width / 1.19, 0), listbox_image)

    troop_scroll = battleui.UIScroller(troop_listbox.rect.topright, troop_listbox.image.get_height(),
                                       troop_listbox.max_row_show, layer=14)

    unit_delete_button = menu.MenuButton(screen_scale, image_list, (image_list[0].get_width() / 2, bottom_height),
                                         updater, text="Delete")
    unit_save_button = menu.MenuButton(screen_scale, image_list,
                                       ((screen_rect.width - (screen_rect.width - (image_list[0].get_width() * 1.7))),
                                                 bottom_height), updater, text="Save")

    popup_listbox = menu.ListBox(screen_scale, (0, 0), box_image, 15)  # popup box need to be in higher layer
    popup_list_scroll = battleui.UIScroller(popup_listbox.rect.topright,
                                            popup_listbox.image.get_height(),
                                            popup_listbox.max_row_show,
                                            layer=14)

    box_image = load_image(main_dir, screen_scale, "map_change.png", "ui\\mainmenu_ui")
    terrain_change_button = menu.TextBox(screen_scale, box_image.copy(), (screen_rect.width / 3, screen_rect.height - box_image.get_height()),
                                                                "Temperate")  # start with temperate terrain
    feature_change_button = menu.TextBox(screen_scale, box_image.copy(), (screen_rect.width / 2, screen_rect.height - box_image.get_height()),
                                                                "Plain")  # start with plain feature
    weather_change_button = menu.TextBox(screen_scale, box_image.copy(), (screen_rect.width / 1.5, screen_rect.height - box_image.get_height()),
                                                                "Light Sunny")  # start with light sunny
    box_image = load_image(main_dir, screen_scale, "filter_box.png", "ui\\mainmenu_ui")  # filter box ui in editor
    filter_box = uniteditor.FilterBox(screen_scale, (screen_rect.width / 2.5, 0), box_image)
    image1 = load_image(main_dir, screen_scale, "team1_button.png", "ui\\mainmenu_ui")  # change unit slot to team 1 in editor
    image2 = load_image(main_dir, screen_scale, "team2_button.png", "ui\\mainmenu_ui")  # change unit slot to team 2 in editor
    team_change_button = battleui.SwitchButton([image1, image2])
    team_change_button.change_pos((filter_box.rect.topleft[0] + 220, filter_box.rect.topleft[1] + 30))
    image1 = load_image(main_dir, screen_scale, "show_button.png", "ui\\mainmenu_ui")  # show unit slot ui in editor
    image2 = load_image(main_dir, screen_scale, "hide_button.png", "ui\\mainmenu_ui")  # hide unit slot ui in editor
    slot_display_button = battleui.SwitchButton([image1, image2])
    slot_display_button.change_pos((filter_box.rect.topleft[0] + 80, filter_box.rect.topleft[1] + 30))
    image1 = load_image(main_dir, screen_scale, "deploy_button.png",
                      "ui\\mainmenu_ui")  # deploy unit in unit slot to test map in editor
    deploy_button = battleui.UIButton(image1, 0)
    deploy_button.change_pos((filter_box.rect.topleft[0] + 150, filter_box.rect.topleft[1] + 90))
    image1 = load_image(main_dir, screen_scale, "test_button.png", "ui\\mainmenu_ui")  # start test button in editor
    image2 = load_image(main_dir, screen_scale, "end_button.png", "ui\\mainmenu_ui")  # stop test button
    test_button = battleui.SwitchButton([image1, image2])
    test_button.change_pos((scale_ui.rect.bottomleft[0] + 55, scale_ui.rect.bottomleft[1] + 25))  # TODO change later
    image1 = load_image(main_dir, screen_scale, "tick_box_no.png", "ui\\mainmenu_ui")  # start test button in editor
    image2 = load_image(main_dir, screen_scale, "tick_box_yes.png", "ui\\mainmenu_ui")  # stop test button
    filter_tick_box = [menu.TickBox(screen_scale, (filter_box.rect.bottomright[0] / 1.26,
                                                   filter_box.rect.bottomright[1] / 8), image1, image2, "meleeinf"),
                       menu.TickBox(screen_scale, (filter_box.rect.bottomright[0] / 1.26,
                                                   filter_box.rect.bottomright[1] / 1.7), image1, image2, "rangeinf"),
                       menu.TickBox(screen_scale, (filter_box.rect.bottomright[0] / 1.11,
                                                   filter_box.rect.bottomright[1] / 8), image1, image2, "meleecav"),
                       menu.TickBox(screen_scale, (filter_box.rect.bottomright[0] / 1.11,
                                                   filter_box.rect.bottomright[1] / 1.7), image1, image2, "rangecav")]
    warning_msg = uniteditor.WarningMsg(screen_scale, test_button.rect.bottomleft)

    unit_build_slot = uniteditor.UnitBuildSlot(1, colour[0])

    return {"unit_listbox": unit_listbox, "unit_preset_name_scroll": unit_preset_name_scroll, "preset_select_border": preset_select_border,
            "troop_listbox": troop_listbox, "troop_scroll": troop_scroll, "unit_delete_button": unit_delete_button,
            "unit_save_button": unit_save_button, "popup_listbox": popup_listbox, "popup_list_scroll": popup_list_scroll,
            "terrain_change_button": terrain_change_button, "feature_change_button": feature_change_button,
            "weather_change_button": weather_change_button, "filter_box": filter_box, "team_change_button": team_change_button,
            "slot_display_button": slot_display_button, "deploy_button": deploy_button, "test_button": test_button,
            "filter_tick_box": filter_tick_box, "warning_msg": warning_msg, "unit_build_slot": unit_build_slot}


def make_input_box(main_dir, screen_scale, screen_rect, image_list):
    """Input box popup"""
    input_ui_image = load_image(main_dir, screen_scale, "input_ui.png", "ui\\mainmenu_ui")
    input_ui = menu.InputUI(screen_scale, input_ui_image,
                                 (screen_rect.width / 2, screen_rect.height / 2))  # user text input ui box popup
    input_ok_button = menu.MenuButton(screen_scale, image_list,
                                      (input_ui.rect.midleft[0] + (image_list[0].get_width() / 1.2),
                                       input_ui.rect.midleft[1] + (image_list[0].get_height() / 1.3)),
                                      text="Confirm", layer=31)
    input_cancel_button = menu.MenuButton(screen_scale, image_list,
                                          (input_ui.rect.midright[0] - (image_list[0].get_width() / 1.2),
                                           input_ui.rect.midright[1] + (image_list[0].get_height() / 1.3)),
                                          text="Cancel", layer=31)

    input_box = menu.InputBox(screen_scale, input_ui.rect.center, input_ui.image.get_width())  # user text input box

    confirm_ui = menu.InputUI(screen_scale, input_ui_image,
                                   (screen_rect.width / 2, screen_rect.height / 2))  # user confirm input ui box popup

    return {"input_ui": input_ui, "input_ok_button": input_ok_button, "input_cancel_button": input_cancel_button,
            "input_box": input_box, "confirm_ui": confirm_ui}


def load_icon_data(main_dir, screen_scale):
    status_images = load_images(main_dir, screen_scale, ["ui", "status_icon"], load_order=False)
    role_images = load_images(main_dir, screen_scale, ["ui", "role_icon"], load_order=False)
    trait_images = load_images(main_dir, screen_scale, ["ui", "trait_icon"], load_order=False)
    skill_images = load_images(main_dir, screen_scale, ["ui", "skill_icon"], load_order=False)

    cooldown = pygame.Surface((skill_images["0.png"].get_width(), skill_images["0.png"].get_height()), pygame.SRCALPHA)
    cooldown.fill((230, 70, 80, 200))  # red colour filter for skill cooldown timer
    battleui.SkillCardIcon.cooldown = cooldown

    active_skill = pygame.Surface((skill_images["0.png"].get_width(), skill_images["0.png"].get_height()), pygame.SRCALPHA)
    active_skill.fill((170, 220, 77, 200))  # green colour filter for skill active timer
    battleui.SkillCardIcon.active_skill = active_skill

    return status_images, role_images, trait_images, skill_images


def load_battle_data(main_dir, screen_scale, ruleset, ruleset_folder):

    # create troop data storage related object
    images = load_images(main_dir, screen_scale, ["ui", "unit_ui", "weapon"])
    for image in images:
        x, y = images[image].get_width(), images[image].get_height()
        images[image] = pygame.transform.scale(images[image],
                                     (int(x / 1.7), int(y / 1.7)))  # scale 1.7 seem to be most fitting as a placeholder
    weapon_data = datastat.WeaponData(main_dir, images, ruleset)  # Create weapon class

    images = load_images(main_dir, screen_scale, ["ui", "unit_ui", "armour"])
    armour_data = datastat.ArmourData(main_dir, images, ruleset)  # Create armour class
    troop_data = datastat.TroopData(main_dir, ruleset, ruleset_folder)

    # create leader data storage object
    images = load_images(main_dir, screen_scale, ["ruleset", ruleset_folder, "leader", "portrait"], load_order=False)
    leader_data = datastat.LeaderData(main_dir, images, ruleset, ruleset_folder)

    # create faction data storage object
    faction_data = datastat.FactionData(main_dir, ruleset_folder, screen_scale)

    return weapon_data, armour_data, troop_data, leader_data, faction_data


def make_event_log(battle_ui_image, screen_rect):
    event_log = battleui.EventLog(battle_ui_image["event_log.png"], (0, screen_rect.height))
    troop_log_button = battleui.UIButton(battle_ui_image["event_log_button1.png"], 0)  # war tab log

    event_log_button = [
        battleui.UIButton(battle_ui_image["event_log_button2.png"], 1),  # army tab log button
        battleui.UIButton(battle_ui_image["event_log_button3.png"], 2),  # leader tab log button
        battleui.UIButton(battle_ui_image["event_log_button4.png"], 3),  # subunit tab log button
        battleui.UIButton(battle_ui_image["event_log_button5.png"], 4),  # delete current tab log button
        battleui.UIButton(battle_ui_image["event_log_button6.png"], 5)]  # delete all log button

    event_log_button = [troop_log_button] + event_log_button
    log_scroll = battleui.UIScroller(event_log.rect.topright, battle_ui_image["event_log.png"].get_height(),
                                          event_log.max_row_show)  # event log scroll
    event_log.log_scroll = log_scroll  # Link log scroll to ui since it is easier to do here with the current order

    return {"event_log": event_log, "troop_log_button": troop_log_button, "event_log_button": event_log_button, "log_scroll": log_scroll}


def make_esc_menu(main_dir, screen_rect, screen_scale, mixer_volume):
    """create Esc menu related objects"""
    menu.EscBox.images = load_images(main_dir, screen_scale, ["ui", "battlemenu_ui"], load_order=False)  # Create ESC Menu box
    menu.EscBox.screen_rect = screen_rect
    battle_menu = menu.EscBox()

    button_image = load_images(main_dir, screen_scale, ["ui", "battlemenu_ui", "button"], load_order=False)
    menu_rect_center0 = battle_menu.rect.center[0]
    menu_rect_center1 = battle_menu.rect.center[1]

    battle_menu_button = [
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 - 100), text="Resume", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 - 50), text="Encyclopedia", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1), text="Option", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 + 50), text="End Battle", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 + 100), text="Desktop", size=14)]

    esc_option_menu_button = [
        menu.EscButton(button_image, (menu_rect_center0 - button_image["0.png"].get_width() * 1.5, menu_rect_center1 * 1.3), text="Confirm", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 * 1.3), text="Apply", size=13),
        menu.EscButton(button_image, (menu_rect_center0 + button_image["0.png"].get_width() * 1.5, menu_rect_center1 * 1.3), text="Cancel", size=14)]

    esc_menu_images = load_images(main_dir, screen_scale, ["ui", "battlemenu_ui", "slider"], load_order=False)
    esc_slider_menu = [menu.SliderMenu([esc_menu_images["scroller_box.png"], esc_menu_images["scroller.png"]],
                                       [esc_menu_images["scroll_button_normal.png"], esc_menu_images["scroll_button_click.png"]],
                                       (menu_rect_center0, menu_rect_center1), mixer_volume)]
    esc_value_box = [menu.ValueBox(esc_menu_images["value.png"], (battle_menu.rect.topright[0] * 1.08, menu_rect_center1), mixer_volume)]

    return {"battle_menu": battle_menu, "battle_menu_button": battle_menu_button, "esc_option_menu_button": esc_option_menu_button,
            "esc_slider_menu": esc_slider_menu, "esc_value_box": esc_value_box}


def make_popup_ui(main_dir, screen_rect, screen_scale, battle_ui_image):
    """Create Popup Ui"""
    popup.TerrainPopup.images = list(load_images(main_dir, screen_scale, ["ui", "popup_ui", "terrain_check"], load_order=False).values())
    popup.TerrainPopup.screen_rect = screen_rect

    troop_card_ui = battleui.TroopCard(battle_ui_image["troop_card.png"])

    # Button related to subunit card and command
    troop_card_button = [battleui.UIButton(battle_ui_image["troopcard_button1.png"], 0),  # subunit card description button
                         battleui.UIButton(battle_ui_image["troopcard_button2.png"], 1),  # subunit card stat button
                         battleui.UIButton(battle_ui_image["troopcard_button3.png"], 2),  # subunit card skill button
                         battleui.UIButton(battle_ui_image["troopcard_button4.png"], 3)]  # subunit card equipment button

    terrain_check = popup.TerrainPopup()  # popup box that show terrain information when right click on map
    button_name_popup = popup.TextPopup(screen_scale)  # popup box that show name when mouse over
    leader_popup = popup.TextPopup(screen_scale)  # popup box that show leader name when mouse over
    effect_popup = popup.EffectIconPopup()  # popup box that show skill/trait/status name when mouse over
    char_popup = popup.TextPopup(screen_scale)  # popup box that show leader name when mouse over

    return {"troop_card_ui": troop_card_ui, "troop_card_button": troop_card_button, "terrain_check": terrain_check,
            "button_name_popup": button_name_popup, "terrain_check": terrain_check, "button_name_popup": button_name_popup,
            "leader_popup": leader_popup, "effect_popup": effect_popup, "char_popup": char_popup}


def make_genre_ui(main_dir, screen_scale, genre):
    genre_battle_ui_image = load_images(main_dir, screen_scale, [genre, "ui", "battle_ui"], load_order=False)

    genre_icon_image = load_images(main_dir, screen_scale, [genre, "ui", "battle_ui",
                                                            "commandbar_icon"], load_order=False)
    command_ui = battleui.CommandBar()  # Command ui with leader and unit behaviours button
    command_ui.load_sprite(genre_battle_ui_image["command_box.png"], genre_icon_image)

    col_split_button = battleui.UIButton(genre_battle_ui_image["colsplit_button.png"],
                                              0)  # unit split by column button
    row_split_button = battleui.UIButton(genre_battle_ui_image["rowsplit_button.png"], 1)  # unit split by row button

    decimation_button = battleui.UIButton(genre_battle_ui_image["decimation.png"], 1)

    # Unit inspect information ui
    inspect_button = battleui.UIButton(genre_battle_ui_image["army_inspect_button.png"], 1)  # unit inspect open/close button

    inspect_ui = battleui.InspectUI(genre_battle_ui_image["army_inspect.png"])  # inspect ui that show subunit in selected unit

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
    behaviour_switch_button = [battleui.SwitchButton(skill_condition_button),  # skill condition button
                               battleui.SwitchButton(shoot_condition_button),  # fire at will button
                               battleui.SwitchButton(behaviour_button),  # behaviour button
                               battleui.SwitchButton(range_condition_button),  # shoot range button
                               battleui.SwitchButton(arc_condition_button),  # arc_shot button
                               battleui.SwitchButton(run_condition_button),  # toggle run button
                               battleui.SwitchButton(melee_condition_button)]  # toggle melee mode

    return {"command_ui": command_ui, "col_split_button": col_split_button, "row_split_button": row_split_button,
            "decimation_button": decimation_button, "inspect_button": inspect_button, "inspect_ui": inspect_ui,
            "behaviour_switch_button": behaviour_switch_button}


def change_genre_ui(main_dir, screen_scale, genre, old_ui_dict):
    genre_battle_ui_image = load_images(main_dir, screen_scale, [genre, "ui", "battle_ui"], load_order=False)

    genre_icon_image = load_images(main_dir, screen_scale, [genre, "ui", "battle_ui",
                                                            "commandbar_icon"], load_order=False)
    old_ui_dict["command_ui"].load_sprite(genre_battle_ui_image["command_box.png"], genre_icon_image)

    old_ui_dict["col_split_button"].image = genre_battle_ui_image["colsplit_button.png"]
    old_ui_dict["row_split_button"].image = genre_battle_ui_image["rowsplit_button.png"]

    old_ui_dict["decimation_button"].image = genre_battle_ui_image["decimation.png"]

    # Unit inspect information ui
    old_ui_dict["inspect_button"].image = genre_battle_ui_image["army_inspect_button.png"]

    old_ui_dict["inspect_ui"].image = genre_battle_ui_image["army_inspect.png"]

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
        old_ui_dict["behaviour_switch_button"][index].change_genre(button_image)


def make_option_menu(main_dir, screen_scale, screen_rect, screen_width, screen_height, image_list, mixer_volume, updater):
    # v Create option menu button and icon
    back_button = menu.MenuButton(screen_scale, image_list, (screen_rect.width / 2, screen_rect.height / 1.2),
                                  updater, text="BACK")

    # Resolution changing bar that fold out the list when clicked
    image = load_image(main_dir, screen_scale, "drop_normal.jpg", "ui\\mainmenu_ui")
    image2 = image
    image3 = load_image(main_dir, screen_scale, "drop_click.jpg", "ui\\mainmenu_ui")
    image_list = [image, image2, image3]
    resolution_drop = menu.MenuButton(screen_scale, image_list, (screen_rect.width / 2, screen_rect.height / 2.3),
                                      updater, text=str(screen_width) + " x " + str(screen_height), size=30)
    resolution_list = ["1920 x 1080", "1600 x 900", "1366 x 768", "1280 x 720", "1024 x 768"]
    resolution_bar = make_bar_list(main_dir, screen_scale, resolution_list, resolution_drop, updater)
    image = load_image(main_dir, screen_scale, "resolution_icon.png", "ui\\mainmenu_ui")
    resolution_icon = menu.MenuIcon(image, (resolution_drop.pos[0] - (resolution_drop.pos[0] / 4.5), resolution_drop.pos[1]))
    # End resolution

    # Volume change scroll bar
    esc_menu_images = load_images(main_dir, screen_scale, ["ui", "battlemenu_ui", "slider"], load_order=False)
    volume_slider = menu.SliderMenu([esc_menu_images["scroller_box.png"], esc_menu_images["scroller.png"]],
                                    [esc_menu_images["scroll_button_normal.png"], esc_menu_images["scroll_button_click.png"]],
                                    (screen_rect.width / 2, screen_rect.height / 3), mixer_volume)
    value_box = [menu.ValueBox(esc_menu_images["value.png"], (volume_slider.rect.topright[0] * 1.1, volume_slider.rect.topright[1]),
                      mixer_volume)]

    image = load_image(main_dir, screen_scale, "volume_icon.png", "ui\\mainmenu_ui")
    volume_icon = menu.MenuIcon(image, (volume_slider.pos[0] - (volume_slider.pos[0] / 4.5), volume_slider.pos[1]))
    # End volume change
    return {"back_button": back_button, "resolution_drop": resolution_drop, "resolution_bar": resolution_bar,
            "resolution_icon": resolution_icon, "volume_slider": volume_slider, "value_box": value_box, "volume_icon": volume_icon}


def create_sprite_pool(self, direction_list, genre_sprite_size, screen_scale, who_todo, preview=False):
    # TODO maybe add body pos and size for check collide?
    animation_sprite_pool = {}  # TODO need to add for subunit creator
    weapon_common_type_list = list(set(["_" + value["Common"] + "_" for value in self.generic_action_data.values()]))  # list of all common type animation set
    weapon_attack_type_list = list(set(["_" + value["Attack"] + "_" for value in self.generic_action_data.values()]))  # list of all attack set
    for subunit_id, this_subunit in who_todo.items():
        if subunit_id not in animation_sprite_pool and subunit_id not in (0, "h1"):  # skip None troop
            animation_sprite_pool[subunit_id] = {}

            race = self.troop_data.race_list[this_subunit["Race"]]["Name"]
            mount_race = self.troop_data.mount_list[this_subunit["Mount"][0]]["Race"]

            this_subunit["Size"] = self.troop_data.race_list[this_subunit["Race"]]["Size"]  # TODO add mount

            primary_main_weapon = this_subunit["Primary Main Weapon"][0]
            primary_sub_weapon = this_subunit["Primary Sub Weapon"][0]
            secondary_main_weapon = this_subunit["Secondary Main Weapon"][0]
            secondary_sub_weapon = this_subunit["Secondary Sub Weapon"][0]
            armour = (self.armour_data.armour_list[this_subunit["Armour"][0]]["Name"],
                      self.troop_data.mount_armour_list[this_subunit["Mount"][2]]["Name"])
            subunit_weapon_list = [(self.weapon_data.weapon_list[primary_main_weapon]["Name"],
                                    self.weapon_data.weapon_list[primary_sub_weapon]["Name"])]

            weapon_common_action = [(self.generic_action_data[subunit_weapon_list[0][0]]["Common"],
                                     self.generic_action_data[subunit_weapon_list[0][1]]["Common"])]
            weapon_attack_action = [(self.generic_action_data[subunit_weapon_list[0][0]]["Attack"],
                                     self.generic_action_data[subunit_weapon_list[0][1]]["Attack"])]
            if (primary_main_weapon, primary_sub_weapon) != (secondary_main_weapon, secondary_sub_weapon):
                subunit_weapon_list = [subunit_weapon_list[0],
                                       (self.weapon_data.weapon_list[secondary_main_weapon]["Name"],
                                        self.weapon_data.weapon_list[secondary_sub_weapon]["Name"])]
                weapon_common_action = [weapon_common_action[0], (self.generic_action_data[subunit_weapon_list[1][0]]["Common"],
                                                                  self.generic_action_data[subunit_weapon_list[1][1]]["Common"])]
                weapon_attack_action = [weapon_attack_action[0], (self.generic_action_data[subunit_weapon_list[1][0]]["Attack"],
                                                                   self.generic_action_data[subunit_weapon_list[1][1]]["Attack"])]

            if preview:  # only create random right side sprite
                animation = [this_animation for this_animation in self.generic_animation_pool[0] if race in this_animation and "&" not in this_animation]  # TODO remove last condition when has mount
                animation = [this_animation for this_animation in animation
                             if (any(ext in this_animation for ext in weapon_common_type_list) is False or
                                 weapon_common_action[0][0] in this_animation) and
                             (any(ext in this_animation for ext in weapon_attack_type_list) is False or
                              (weapon_attack_action[0][0] in this_animation and ("Main", "Sub")[0] in this_animation))
                             and "Default" not in this_animation]  # get animation with weapon
                if len(animation) > 0:
                    animation = random.choice(animation)  # random animation
                else:
                    animation = race+"_Default"

                frame_data = random.choice(self.generic_animation_pool[1][animation])  # random frame
                animation_property = self.generic_animation_pool[0][animation][0]["animation_property"].copy()
                if type(subunit_id) == int:
                    sprite_data = self.troop_data.troop_sprite_list[str(subunit_id)]
                else:
                    leader_id = int(subunit_id.replace("h", ""))
                    if leader_id < 10000:
                        sprite_data = self.leader_data.leader_sprite_list[str(leader_id)]
                    else:  # common leader
                        sprite_data = self.leader_data.common_leader_sprite_list[str(leader_id)]
                sprite_dict = make_sprite(animation, this_subunit["Size"], frame_data,
                                          sprite_data, self.gen_body_sprite_pool,
                                          self.gen_weapon_sprite_pool,
                                          self.gen_armour_sprite_pool,
                                          self.effect_sprite_pool, animation_property,
                                          self.weapon_joint_list,
                                          (0, subunit_weapon_list[0]), armour,
                                          self.hair_colour_list, self.skin_colour_list,
                                          genre_sprite_size, screen_scale)

                animation_sprite_pool[subunit_id] = {"sprite": sprite_dict["sprite"],
                     "animation_property": sprite_dict["animation_property"],
                     "frame_property": sprite_dict["frame_property"]}
            else:
                for animation in self.generic_animation_pool[0]:  # use one side in the list for finding animation name
                    # only get animation with same race and mount after "&"
                    # if race in animation and ((mount_race == "Any" and "&" not in animation) or
                    #                           ("&" in animation and mount_race in animation.split("&")[1])):
                    if race in animation and "&" not in animation and "Preview" not in animation:
                        animation_property = self.generic_animation_pool[0][animation][0]["animation_property"].copy()
                        for weapon_set_index, weapon_set in enumerate(
                                subunit_weapon_list):  # create animation for each weapon set
                            for weapon_index, weapon in enumerate(weapon_set):
                                # first check if animation is common weapon type specific and match with weapon, then check if it is attack specific
                                if (any(ext in animation for ext in weapon_common_type_list) is False or
                                    weapon_common_action[weapon_set_index][weapon_index] in animation) and \
                                        (any(ext in animation for ext in weapon_attack_type_list) is False or (
                                                weapon_attack_action[weapon_set_index][weapon_index] in animation and
                                                ("Main", "Sub")[weapon_index] in animation)):
                                    if animation + "/" + str(weapon_set_index) not in animation_sprite_pool[subunit_id]:
                                        animation_sprite_pool[subunit_id][animation + "/" + str(weapon_set_index)] = {}
                                    for index, direction in enumerate(direction_list):
                                        new_direction = direction
                                        opposite_direction = None  # no opposite direction for front and back
                                        if direction == "side":
                                            new_direction = "r_side"
                                            opposite_direction = "l_side"
                                        elif direction == "sideup":
                                            new_direction = "r_sideup"
                                            opposite_direction = "l_sideup"
                                        elif direction == "sidedown":
                                            new_direction = "r_sidedown"
                                            opposite_direction = "l_sidedown"
                                        animation_sprite_pool[subunit_id][animation + "/" + str(weapon_set_index)][
                                            new_direction] = {}
                                        if opposite_direction is not None:
                                            animation_sprite_pool[subunit_id][animation + "/" + str(weapon_set_index)][
                                                opposite_direction] = {}
                                        for frame_num, frame_data in enumerate(
                                                self.generic_animation_pool[index][animation]):
                                            if type(subunit_id) == int:
                                                sprite_data = self.troop_data.troop_sprite_list[str(subunit_id)]
                                            else:
                                                leader_id = int(subunit_id.replace("h", ""))
                                                if leader_id < 10000:
                                                    sprite_data = self.leader_data.leader_sprite_list[str(leader_id)]
                                                else:  # common leader
                                                    sprite_data = self.leader_data.common_leader_sprite_list[str(leader_id)]
                                            sprite_dict = make_sprite(animation, this_subunit["Size"], frame_data,
                                                                      sprite_data, self.gen_body_sprite_pool,
                                                                      self.gen_weapon_sprite_pool,
                                                                      self.gen_armour_sprite_pool,
                                                                      self.effect_sprite_pool, animation_property,
                                                                      self.weapon_joint_list,
                                                                      (weapon_set_index, weapon_set), armour,
                                                                      self.hair_colour_list, self.skin_colour_list,
                                                                      genre_sprite_size, screen_scale)

                                            animation_sprite_pool[subunit_id][animation + "/" + str(weapon_set_index)][
                                                new_direction][
                                                frame_num] = \
                                                {"sprite": sprite_dict["sprite"],
                                                 "animation_property": sprite_dict["animation_property"],
                                                 "frame_property": sprite_dict["frame_property"]}
                                            if opposite_direction is not None:  # flip sprite for opposite direction
                                                animation_sprite_pool[subunit_id][
                                                    animation + "/" + str(weapon_set_index)][
                                                    opposite_direction][
                                                    frame_num] = {
                                                    "sprite": pygame.transform.flip(sprite_dict["sprite"].copy(), True,
                                                                                    False),
                                                    "animation_property": sprite_dict["animation_property"],
                                                    "frame_property": sprite_dict["frame_property"]}
    return animation_sprite_pool
