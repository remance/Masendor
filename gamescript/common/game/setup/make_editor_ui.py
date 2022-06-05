from gamescript import battleui, menu, uniteditor
from gamescript.common import utility

load_image = utility.load_image


def make_editor_ui(main_dir, screen_scale, screen_rect, listbox_image, image_list, scale_ui, colour, updater):
    """Create army editor ui and button"""

    bottom_height = screen_rect.height - image_list[0].get_height()
    box_image = load_image(main_dir, screen_scale, "unit_presetbox.png", "ui\\mainmenu_ui")
    unit_preset_listbox = menu.ListBox(screen_scale, (0, screen_rect.height / 2.2), box_image)  # box for showing unit preset list
    battleui.UIScroll(unit_preset_listbox, unit_preset_listbox.rect.topright)  # preset name scroll
    preset_select_border = uniteditor.SelectedPresetBorder((unit_preset_listbox.image.get_width() * 0.96, int(30 * screen_scale[1])))

    troop_listbox = menu.ListBox(screen_scale, (screen_rect.width / 1.19, 0), listbox_image)

    battleui.UIScroll(troop_listbox, troop_listbox.rect.topright)

    unit_delete_button = menu.MenuButton(screen_scale, image_list, (image_list[0].get_width() / 2, bottom_height),
                                         updater, text="Delete")
    unit_save_button = menu.MenuButton(screen_scale, image_list,
                                       ((screen_rect.width - (screen_rect.width - (image_list[0].get_width() * 1.7))),
                                                 bottom_height), updater, text="Save")

    popup_listbox = menu.ListBox(screen_scale, (0, 0), box_image, 15)  # popup box need to be in higher layer
    battleui.UIScroll(popup_listbox, popup_listbox.rect.topright)

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

    return {"unit_listbox": unit_preset_listbox, "preset_select_border": preset_select_border,
            "troop_listbox": troop_listbox, "unit_delete_button": unit_delete_button,
            "unit_save_button": unit_save_button, "popup_listbox": popup_listbox,
            "terrain_change_button": terrain_change_button, "feature_change_button": feature_change_button,
            "weather_change_button": weather_change_button, "filter_box": filter_box, "team_change_button": team_change_button,
            "slot_display_button": slot_display_button, "deploy_button": deploy_button, "test_button": test_button,
            "filter_tick_box": filter_tick_box, "warning_msg": warning_msg, "unit_build_slot": unit_build_slot}
