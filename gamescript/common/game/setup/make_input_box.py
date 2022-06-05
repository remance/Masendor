from gamescript import menu
from gamescript.common import utility

load_image = utility.load_image


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