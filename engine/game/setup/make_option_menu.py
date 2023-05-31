from engine.uimenu.uimenu import MenuButton, TickBox, OptionMenuText, SliderMenu, ValueBox, ControllerIcon, KeybindIcon
from engine.utility import load_image, load_images, make_bar_list


def make_option_menu(main_dir, screen_scale, screen_rect, screen_width, screen_height, image_list,
                     config, keybind, battle_select_image):
    """
    This method create UI in option menu and keybinding menu

    :param main_dir: main directory
    :param screen_scale:
    :param screen_rect:
    :param screen_width: width of game screen
    :param screen_height: height of game screen
    :param image_list:
    :param updater:
    :param config: config
    :param keybind:
    :param battle_select_image:
    :return: dict of objects
    """
    # Create option menu button and icon
    from engine.game import game
    localisation = game.Game.localisation
    resolution_list = game.Game.resolution_list
    font_size = int(32 * screen_scale[1])

    back_button = MenuButton(image_list, (screen_rect.width / 3, screen_rect.height / 1.2),
                             key_name="back_button")
    keybind_button = MenuButton(image_list, (screen_rect.width / 2, screen_rect.height / 1.2),
                                key_name="option_menu_keybind")
    default_button = MenuButton(image_list, (screen_rect.width / 1.5, screen_rect.height / 1.2),
                                key_name="option_menu_default")

    fullscreen_box = TickBox((screen_rect.width / 2, screen_rect.height / 6.5),
                             battle_select_image["untick"], battle_select_image["tick"], "fullscreen")

    if int(config["full_screen"]) == 1:
        fullscreen_box.change_tick(True)

    fullscreen_text = OptionMenuText(
        (fullscreen_box.pos[0] - (fullscreen_box.pos[0] / 4.5), fullscreen_box.pos[1]),
        localisation.grab_text(key=("ui", "option_full_screen",)), font_size)

    # Volume change scroll bar
    option_menu_images = load_images(main_dir, screen_scale=screen_scale, subfolder=("ui", "option_ui", "slider"))
    scroller_images = (option_menu_images["scroller_box"], option_menu_images["scroller"])
    scroll_button_images = (option_menu_images["scroll_button_normal"], option_menu_images["scroll_button_click"])
    volume_slider = {"master": SliderMenu(scroller_images, scroll_button_images,
                                          (screen_rect.width / 2, screen_rect.height / 4),
                                          float(config["master_volume"])),
                     "music": SliderMenu(scroller_images, scroll_button_images,
                                         (screen_rect.width / 2, screen_rect.height / 3),
                                         float(config["music_volume"])),
                     "voice": SliderMenu(scroller_images, scroll_button_images,
                                         (screen_rect.width / 2, screen_rect.height / 2.4),
                                         float(config["voice_volume"])),
                     "effect": SliderMenu(scroller_images, scroll_button_images,
                                          (screen_rect.width / 2, screen_rect.height / 2),
                                          float(config["effect_volume"])),
                     }
    value_box = {key: ValueBox(option_menu_images["value"],
                               (volume_slider[key].rect.topright[0] * 1.1, volume_slider[key].rect.center[1]),
                               volume_slider[key].value, int(26 * screen_scale[1])) for key in volume_slider}

    volume_texts = {key: OptionMenuText((volume_slider[key].pos[0] - (volume_slider[key].pos[0] / 4.5),
                                         volume_slider[key].pos[1]),
                                        localisation.grab_text(key=("ui", "option_" + key + "_volume",)),
                                        font_size) for key in volume_slider}

    # Resolution changing bar that fold out the list when clicked
    image = load_image(main_dir, screen_scale, "drop_normal.jpg", ("ui", "mainmenu_ui"))
    image2 = image
    image3 = load_image(main_dir, screen_scale, "drop_click.jpg", ("ui", "mainmenu_ui"))
    image_list = [image, image2, image3]
    resolution_drop = MenuButton(image_list, (screen_rect.width / 2, screen_rect.height / 1.8),
                                 key_name=str(screen_width) + " x " + str(screen_height),
                                 font_size=int(30 * screen_scale[1]))

    resolution_bar = make_bar_list(main_dir, screen_scale, resolution_list, resolution_drop)

    resolution_text = OptionMenuText((resolution_drop.pos[0] - (resolution_drop.pos[0] / 4.5),
                                      resolution_drop.pos[1]),
                                     localisation.grab_text(key=("ui", "option_display_resolution",)),
                                     font_size)

    keybind_text = {"Main Weapon Attack": OptionMenuText((screen_rect.width / 4, screen_rect.height / 5),
                                                         localisation.grab_text(
                                                             key=("ui", "keybind_main_weapon_attack",)), font_size),
                    "Sub Weapon Attack": OptionMenuText((screen_rect.width / 4, screen_rect.height / 3.5),
                                                        localisation.grab_text(
                                                            key=("ui", "keybind_sub_weapon_attack",)), font_size),
                    "Move Left": OptionMenuText((screen_rect.width / 4, screen_rect.height / 2.5),
                                                localisation.grab_text(key=("ui", "keybind_move_left",)), font_size),
                    "Move Right": OptionMenuText((screen_rect.width / 4, screen_rect.height / 2),
                                                 localisation.grab_text(key=("ui", "keybind_move_right",)), font_size),
                    "Move Up": OptionMenuText((screen_rect.width / 4, screen_rect.height / 1.7),
                                              localisation.grab_text(key=("ui", "keybind_move_up",)), font_size),
                    "Move Down": OptionMenuText((screen_rect.width / 4, screen_rect.height / 1.5),
                                                localisation.grab_text(key=("ui", "keybind_move_down",)), font_size),
                    "Menu/Cancel": OptionMenuText((screen_rect.width / 2, screen_rect.height / 5),
                                                  localisation.grab_text(key=("ui", "keybind_menu",)), font_size),
                    "Order Menu": OptionMenuText((screen_rect.width / 2, screen_rect.height / 3.5),
                                                 localisation.grab_text(key=("ui", "keybind_order_menu",)), font_size),
                    "Run Input": OptionMenuText((screen_rect.width / 2, screen_rect.height / 2.5),
                                                localisation.grab_text(key=("ui", "keybind_run_input",)), font_size),
                    "Skill 1": OptionMenuText((screen_rect.width / 2, screen_rect.height / 2),
                                              localisation.grab_text(key=("ui", "keybind_skill1",)), font_size),
                    "Skill 2": OptionMenuText((screen_rect.width / 2, screen_rect.height / 1.7),
                                              localisation.grab_text(key=("ui", "keybind_skill2",)), font_size),
                    "Skill 3": OptionMenuText((screen_rect.width / 2, screen_rect.height / 1.5),
                                              localisation.grab_text(key=("ui", "keybind_skill3",)), font_size),
                    "Skill 4": OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 5),
                                              localisation.grab_text(key=("ui", "keybind_skill4",)), font_size),
                    "Swap Weapon Set 1": OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 3.5),
                                                        localisation.grab_text(key=("ui", "keybind_swap_weapon_set1",)),
                                                        font_size),
                    "Swap Weapon Set 2": OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 2.5),
                                                        localisation.grab_text(key=("ui", "keybind_swap_weapon_set2",)),
                                                        font_size),
                    "Toggle Run": OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 2),
                                                 localisation.grab_text(key=("ui", "keybind_toggle_run",)), font_size),
                    "Auto Move": OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 1.7),
                                                localisation.grab_text(key=("ui", "keybind_auto_move",)), font_size)}

    control_type = "keyboard"  # make default keyboard for now, get changed later when player enter keybind menu
    keybind = keybind[control_type]

    control_images = load_images(main_dir, screen_scale=screen_scale, subfolder=("ui", "option_ui"))
    control_switch = ControllerIcon((screen_rect.width / 2, screen_rect.height * 0.1),
                                    control_images, control_type)

    keybind_icon = {"Main Weapon Attack": KeybindIcon((screen_rect.width / 3, screen_rect.height / 5),
                                                      font_size, control_type,
                                                      keybind["Main Weapon Attack"]),
                    "Sub Weapon Attack": KeybindIcon((screen_rect.width / 3, screen_rect.height / 3.5),
                                                     font_size, control_type,
                                                     keybind["Sub Weapon Attack"]),
                    "Move Left": KeybindIcon((screen_rect.width / 3, screen_rect.height / 2.5), font_size,
                                             control_type, keybind["Move Left"]),
                    "Move Right": KeybindIcon((screen_rect.width / 3, screen_rect.height / 2), font_size,
                                              control_type, keybind["Move Right"]),
                    "Move Up": KeybindIcon((screen_rect.width / 3, screen_rect.height / 1.7), font_size,
                                           control_type, keybind["Move Up"]),
                    "Move Down": KeybindIcon((screen_rect.width / 3, screen_rect.height / 1.5), font_size,
                                             control_type, keybind["Move Down"]),
                    "Menu/Cancel": KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 5), font_size,
                                               control_type, keybind["Menu/Cancel"]),
                    "Order Menu": KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 3.5), font_size,
                                              control_type, keybind["Order Menu"]),
                    "Run Input": KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 2.5), font_size,
                                             control_type, keybind["Run Input"]),
                    "Skill 1": KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 2), font_size,
                                           control_type, keybind["Skill 1"]),
                    "Skill 2": KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 1.7), font_size,
                                           control_type, keybind["Skill 2"]),
                    "Skill 3": KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 1.5), font_size,
                                           control_type, keybind["Skill 3"]),
                    "Skill 4": KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 5), font_size,
                                           control_type, keybind["Skill 4"]),
                    "Swap Weapon Set 1": KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 3.5),
                                                     font_size, control_type,
                                                     keybind["Swap Weapon Set 1"]),
                    "Swap Weapon Set 2": KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 2.5),
                                                     font_size, control_type,
                                                     keybind["Swap Weapon Set 2"]),
                    "Toggle Run": KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 2),
                                              font_size, control_type,
                                              keybind["Toggle Run"]),
                    "Auto Move": KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 1.7),
                                             font_size, control_type,
                                             keybind["Auto Move"])}

    return {"back_button": back_button, "keybind_button": keybind_button, "default_button": default_button,
            "resolution_drop": resolution_drop,
            "resolution_bar": resolution_bar, "resolution_text": resolution_text, "volume_sliders": volume_slider,
            "value_boxes": value_box, "volume_texts": volume_texts, "fullscreen_box": fullscreen_box,
            "fullscreen_text": fullscreen_text, "keybind_text": keybind_text, "keybind_icon": keybind_icon,
            "control_switch": control_switch}
