from engine.uimenu.uimenu import SliderMenu, ValueBox
from engine.uibattle import uibattle
from engine.utility import load_images


def make_esc_menu(main_dir, screen_scale, mixer_volume):
    """create Esc menu related objects"""
    uibattle.EscBox.images = load_images(main_dir, screen_scale=screen_scale, subfolder=("ui", "battlemenu_ui"))
    battle_menu = uibattle.EscBox()  # Create ESC Menu box

    button_image = load_images(main_dir, screen_scale=screen_scale, subfolder=("ui", "battlemenu_ui", "button"))
    menu_rect_center0 = battle_menu.rect.center[0]
    menu_rect_center1 = battle_menu.rect.center[1]

    esc_button_text_size = int(22 * screen_scale[1])

    battle_menu_button = [
        uibattle.EscButton(button_image, (menu_rect_center0, menu_rect_center1 - 100), text="Resume",
                           text_size=esc_button_text_size),
        uibattle.EscButton(button_image, (menu_rect_center0, menu_rect_center1 - 50), text="Encyclopedia",
                           text_size=esc_button_text_size),
        uibattle.EscButton(button_image, (menu_rect_center0, menu_rect_center1), text="Option",
                           text_size=esc_button_text_size),
        uibattle.EscButton(button_image, (menu_rect_center0, menu_rect_center1 + 50), text="End Battle",
                           text_size=esc_button_text_size),
        uibattle.EscButton(button_image, (menu_rect_center0, menu_rect_center1 + 100), text="Desktop",
                           text_size=esc_button_text_size)]

    esc_option_menu_button = [
        uibattle.EscButton(button_image,
                           (menu_rect_center0 - button_image["0"].get_width() * 1.5, menu_rect_center1 * 1.3),
                           text="Confirm", text_size=esc_button_text_size),
        uibattle.EscButton(button_image, (menu_rect_center0, menu_rect_center1 * 1.3), text="Apply",
                           text_size=esc_button_text_size),
        uibattle.EscButton(button_image,
                           (menu_rect_center0 + button_image["0"].get_width() * 1.5, menu_rect_center1 * 1.3),
                           text="Cancel", text_size=esc_button_text_size)]

    option_menu_images = load_images(main_dir, screen_scale=screen_scale, subfolder=("ui", "option_ui", "slider"))
    esc_slider_menu = [SliderMenu([option_menu_images["scroller_box"], option_menu_images["scroller"]],
                                  [option_menu_images["scroll_button_normal"],
                                   option_menu_images["scroll_button_click"]],
                                  (menu_rect_center0, menu_rect_center1), mixer_volume)]
    esc_value_boxes = [
        ValueBox(option_menu_images["value"], (battle_menu.rect.topright[0] * 1.08, menu_rect_center1),
                 mixer_volume,
                 text_size=int(24 * screen_scale[1]))]

    return {"battle_menu": battle_menu, "battle_menu_button": battle_menu_button,
            "esc_option_menu_button": esc_option_menu_button,
            "esc_slider_menu": esc_slider_menu, "esc_value_boxes": esc_value_boxes}
