from gamescript import battleui, menu
from gamescript.common import utility

load_image = utility.load_image


def make_editor_ui(main_dir, screen_scale, screen_rect, listbox_image, image_list, updater):
    """Create army editor ui and button"""

    bottom_height = screen_rect.height - image_list[0].get_height()
    box_image = load_image(main_dir, screen_scale, "unit_presetbox.png", ("ui", "mainmenu_ui"))
    unit_preset_listbox = menu.ListBox(screen_scale, (0, screen_rect.height / 2.2),
                                       box_image)  # box for showing unit preset list
    battleui.UIScroll(unit_preset_listbox, unit_preset_listbox.rect.topright)  # preset name scroll
    preset_select_border = menu.SelectedPresetBorder(
        (unit_preset_listbox.image.get_width() * 0.96, int(30 * screen_scale[1])))

    troop_listbox = menu.ListBox(screen_scale, (screen_rect.width / 1.19, 0), listbox_image)

    battleui.UIScroll(troop_listbox, troop_listbox.rect.topright)

    unit_delete_button = menu.MenuButton(screen_scale, image_list, (image_list[0].get_width() / 2, bottom_height),
                                         updater, text="Delete")
    unit_save_button = menu.MenuButton(screen_scale, image_list,
                                       ((screen_rect.width - (screen_rect.width - (image_list[0].get_width() * 1.7))),
                                        bottom_height), updater, text="Save")

    popup_listbox = menu.ListBox(screen_scale, (0, 0), box_image, 15)  # popup box need to be in higher layer
    battleui.UIScroll(popup_listbox, popup_listbox.rect.topright)

    box_image = load_image(main_dir, screen_scale, "filter_box.png", ("ui", "mainmenu_ui"))  # filter box ui in editor
    filter_box = menu.FilterBox(screen_scale, (screen_rect.width / 2.5, 0), box_image)

    image1 = load_image(main_dir, screen_scale, "tick_box_no.png", ("ui", "mainmenu_ui"))
    image2 = load_image(main_dir, screen_scale, "tick_box_yes.png", ("ui", "mainmenu_ui"))
    filter_tick_box = [menu.TickBox((filter_box.rect.bottomright[0] / 1.26,
                                     filter_box.rect.bottomright[1] / 8), image1, image2, "meleeinf"),
                       menu.TickBox((filter_box.rect.bottomright[0] / 1.26,
                                     filter_box.rect.bottomright[1] / 1.7), image1, image2, "rangeinf"),
                       menu.TickBox((filter_box.rect.bottomright[0] / 1.11,
                                     filter_box.rect.bottomright[1] / 8), image1, image2, "meleecav"),
                       menu.TickBox((filter_box.rect.bottomright[0] / 1.11,
                                     filter_box.rect.bottomright[1] / 1.7), image1, image2, "rangecav")]

    return {"unit_listbox": unit_preset_listbox, "preset_select_border": preset_select_border,
            "troop_listbox": troop_listbox, "unit_delete_button": unit_delete_button,
            "unit_save_button": unit_save_button, "popup_listbox": popup_listbox, "filter_box": filter_box,
            "filter_tick_box": filter_tick_box}
