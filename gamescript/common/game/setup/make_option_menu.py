from gamescript import menu
from gamescript.common import utility

load_image = utility.load_image
load_images = utility.load_images
make_bar_list = utility.make_bar_list


def make_option_menu(main_dir, screen_scale, screen_rect, screen_width, screen_height, image_list, volume,
                    updater, config, keybind, battle_select_image):
    # Create option menu button and icon
    font_size = int(36 * screen_scale[1])
    
    back_button = menu.MenuButton(screen_scale, image_list, (screen_rect.width / 3, screen_rect.height / 1.2),
                                  updater, text="Back")
    keybind_button = menu.MenuButton(screen_scale, image_list, (screen_rect.width / 2, screen_rect.height / 1.2),
                                  updater, text="Keybind")
    default_button = menu.MenuButton(screen_scale, image_list, (screen_rect.width / 1.5, screen_rect.height / 1.2),
                                     updater, text="Default")

    fullscreen_box = menu.TickBox((screen_rect.width / 2, screen_rect.height / 6.5),
                                  battle_select_image["untick"], battle_select_image["tick"], "fullscreen")
    if config["full_screen"] == 1:
        fullscreen_box.change_tick(True)

    fullscreen_text = menu.OptionMenuText(
        (fullscreen_box.pos[0] - (fullscreen_box.pos[0] / 4.5), fullscreen_box.pos[1]),
        "Full Screen", font_size)

    # Volume change scroll bar
    esc_menu_images = load_images(main_dir, screen_scale=screen_scale, subfolder=("ui", "battlemenu_ui", "slider"))
    scroller_images = (esc_menu_images["scroller_box"], esc_menu_images["scroller"])
    scroll_button_images = (esc_menu_images["scroll_button_normal"], esc_menu_images["scroll_button_click"])
    volume_slider = {"master": menu.SliderMenu(scroller_images, scroll_button_images,
                                               (screen_rect.width / 2, screen_rect.height / 4), volume["master"]),
                     "music": menu.SliderMenu(scroller_images, scroll_button_images,
                                              (screen_rect.width / 2, screen_rect.height / 3), volume["music"]),
                     "voice": menu.SliderMenu(scroller_images, scroll_button_images,
                                              (screen_rect.width / 2, screen_rect.height / 2.4), volume["voice"]),
                     "effect": menu.SliderMenu(scroller_images, scroll_button_images,
                                               (screen_rect.width / 2, screen_rect.height / 2), volume["effect"]),
                     }
    value_box = {key: menu.ValueBox(esc_menu_images["value"],
                                    (volume_slider[key].rect.topright[0] * 1.1, volume_slider[key].rect.center[1]),
                                    volume_slider[key].value, int(26 * screen_scale[1])) for key in volume_slider}

    volume_text = {key: menu.OptionMenuText((volume_slider[key].pos[0] - (volume_slider[key].pos[0] / 4.5),
                                             volume_slider[key].pos[1]), key.capitalize() + " Volume",
                                            font_size) for key in volume_slider}

    # Resolution changing bar that fold out the list when clicked
    image = load_image(main_dir, screen_scale, "drop_normal.jpg", ("ui", "mainmenu_ui"))
    image2 = image
    image3 = load_image(main_dir, screen_scale, "drop_click.jpg", ("ui", "mainmenu_ui"))
    image_list = [image, image2, image3]
    resolution_drop = menu.MenuButton(screen_scale, image_list, (screen_rect.width / 2, screen_rect.height / 1.8),
                                      updater, text=str(screen_width) + " x " + str(screen_height),
                                      size=int(30 * screen_scale[1]))
    resolution_list = ("2560 x 1440", "2048 x 1152", "1920 x 1080", "1600 x 900", "1366 x 768",
                       "1280 x 720", "1136 x 640", "1024 x 600", "960 x 540", "848 x 480")  # add more here
    resolution_bar = make_bar_list(main_dir, screen_scale, resolution_list, resolution_drop, updater)

    resolution_text = menu.OptionMenuText((resolution_drop.pos[0] - (resolution_drop.pos[0] / 4.5),
                                           resolution_drop.pos[1]), "Display Resolution", font_size)

    keybind_text = {"Main Weapon Attack": menu.OptionMenuText((screen_rect.width / 4, screen_rect.height / 5),
                                                                 "Main Weapon Attack", font_size),
                       "Sub Weapon Attack": menu.OptionMenuText((screen_rect.width / 4, screen_rect.height / 3.5),
                                                                "Sub Weapon Attack", font_size),
                       "Move Left": menu.OptionMenuText((screen_rect.width / 4, screen_rect.height / 2.5),
                                                        "Move Left", font_size),
                       "Move Right": menu.OptionMenuText((screen_rect.width / 4, screen_rect.height / 2),
                                                         "Move Right", font_size),
                       "Move Up": menu.OptionMenuText((screen_rect.width / 4, screen_rect.height / 1.7),
                                                      "Move Up", font_size),
                       "Move Down": menu.OptionMenuText((screen_rect.width / 2, screen_rect.height / 5),
                                                        "Move Down", font_size),
                       "Menu/Cancel": menu.OptionMenuText((screen_rect.width / 2, screen_rect.height / 3.5),
                                                          "Menu/Cancel", font_size),
                       "Order Menu": menu.OptionMenuText((screen_rect.width / 2, screen_rect.height / 2.5),
                                                         "Order Menu", font_size),
                       "Run Input": menu.OptionMenuText((screen_rect.width / 2, screen_rect.height / 2),
                                                        "Run Input", font_size),
                       "Skill 1": menu.OptionMenuText((screen_rect.width / 2, screen_rect.height / 1.7),
                                                      "Skill 1", font_size),
                       "Skill 2": menu.OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 5),
                                                      "Skill 2", font_size),
                       "Skill 3": menu.OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 3.5),
                                                      "Skill 3", font_size),
                       "Skill 4": menu.OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 2.5),
                                                      "Skill 4", font_size),
                       "Swap Weapon Set 1": menu.OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 2),
                                                                "Swap Weapon Set 1", font_size),
                       "Swap Weapon Set 2": menu.OptionMenuText((screen_rect.width / 1.2, screen_rect.height / 1.7),
                                                                "Swap Weapon Set 2", font_size)}

    control_type = "keyboard"
    keybind = keybind[control_type]

    keybind_icon = {"Main Weapon Attack": menu.KeybindIcon((screen_rect.width / 3, screen_rect.height / 5),
                                                                 font_size, control_type,
                                                                 keybind["Main Weapon Attack"]),
                       "Sub Weapon Attack": menu.KeybindIcon((screen_rect.width / 3, screen_rect.height / 3.5),
                                                                font_size, control_type,
                                                                keybind["Sub Weapon Attack"]),
                       "Move Left": menu.KeybindIcon((screen_rect.width / 3, screen_rect.height / 2.5), font_size,
                                                        control_type, keybind["Move Left"]),
                       "Move Right": menu.KeybindIcon((screen_rect.width / 3, screen_rect.height / 2), font_size,
                                                         control_type, keybind["Move Right"]),
                       "Move Up": menu.KeybindIcon((screen_rect.width / 3, screen_rect.height / 1.7), font_size,
                                                      control_type, keybind["Move Up"]),
                       "Move Down": menu.KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 5), font_size,
                                                        control_type, keybind["Move Down"]),
                       "Menu/Cancel": menu.KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 3.5), font_size,
                                                          control_type, keybind["Menu/Cancel"]),
                       "Order Menu": menu.KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 2.5), font_size,
                                                         control_type, keybind["Order Menu"]),
                       "Run Input": menu.KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 2), font_size,
                                                        control_type, keybind["Run Input"]),
                       "Skill 1": menu.KeybindIcon((screen_rect.width / 1.7, screen_rect.height / 1.7), font_size,
                                                      control_type, keybind["Skill 1"]),
                       "Skill 2": menu.KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 5), font_size,
                                                      control_type, keybind["Skill 2"]),
                       "Skill 3": menu.KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 3.5), font_size,
                                                      control_type, keybind["Skill 3"]),
                       "Skill 4": menu.KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 2.5), font_size,
                                                      control_type, keybind["Skill 4"]),
                       "Swap Weapon Set 1": menu.KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 2),
                                                                font_size, control_type,
                                                                keybind["Swap Weapon Set 1"]),
                       "Swap Weapon Set 2": menu.KeybindIcon((screen_rect.width / 1.12, screen_rect.height / 1.7),
                                                                font_size, control_type,
                                                                keybind["Swap Weapon Set 2"])}

    return {"back_button": back_button, "keybind_button": keybind_button, "default_button": default_button,
            "resolution_drop": resolution_drop,
            "resolution_bar": resolution_bar, "resolution_text": resolution_text, "volume_sliders": volume_slider,
            "value_boxes": value_box, "volume_texts": volume_text, "fullscreen_box": fullscreen_box,
            "fullscreen_text": fullscreen_text, "keybind_text": keybind_text, "keybind_icon": keybind_icon}
