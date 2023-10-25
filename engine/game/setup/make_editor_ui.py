from engine.uibattle.uibattle import UIScroll
from engine.uimenu.uimenu import ListBox, MenuButton
from engine.utils.data_loading import load_image


def make_editor_ui(main_dir, screen_scale, screen_rect, listbox_image, image_list, updater):
    """Create army editor ui and button"""

    bottom_height = screen_rect.height - image_list[0].get_height()
    box_image = load_image(main_dir, screen_scale, "unit_presetbox.png", ("ui", "mainmenu_ui"))
    unit_preset_listbox = ListBox((0, screen_rect.height / 2.2), box_image)  # box for showing unit preset list
    UIScroll(unit_preset_listbox, unit_preset_listbox.rect.topright)  # preset name scroll

    troop_listbox = ListBox((screen_rect.width / 1.19, 0), listbox_image)

    UIScroll(troop_listbox, troop_listbox.rect.topright)

    unit_delete_button = MenuButton(image_list, (image_list[0].get_width() / 2, bottom_height),
                                    key_name="delete_button")
    unit_save_button = MenuButton(image_list,
                                  ((screen_rect.width - (screen_rect.width - (image_list[0].get_width() * 1.7))),
                                   bottom_height), key_name="save_button")

    popup_listbox = ListBox((0, 0), box_image, 15)  # popup box need to be in higher layer
    UIScroll(popup_listbox, popup_listbox.rect.topright)

    return {"unit_listbox": unit_preset_listbox,
            "troop_listbox": troop_listbox, "unit_delete_button": unit_delete_button,
            "unit_save_button": unit_save_button, "popup_listbox": popup_listbox}
