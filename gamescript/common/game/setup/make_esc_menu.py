from gamescript import menu
from gamescript.common import utility

load_images = utility.load_images


def make_esc_menu(main_dir, screen_rect, screen_scale, mixer_volume):
    """create Esc menu related objects"""
    menu.EscBox.images = load_images(main_dir, screen_scale, ["ui", "battlemenu_ui"],
                                     load_order=False)  # Create ESC Menu box
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
        menu.EscButton(button_image, (menu_rect_center0 - button_image["0"].get_width() * 1.5, menu_rect_center1 * 1.3),
                       text="Confirm", size=14),
        menu.EscButton(button_image, (menu_rect_center0, menu_rect_center1 * 1.3), text="Apply", size=13),
        menu.EscButton(button_image, (menu_rect_center0 + button_image["0"].get_width() * 1.5, menu_rect_center1 * 1.3),
                       text="Cancel", size=14)]

    esc_menu_images = load_images(main_dir, screen_scale, ["ui", "battlemenu_ui", "slider"], load_order=False)
    esc_slider_menu = [menu.SliderMenu([esc_menu_images["scroller_box"], esc_menu_images["scroller"]],
                                       [esc_menu_images["scroll_button_normal"],
                                        esc_menu_images["scroll_button_click"]],
                                       (menu_rect_center0, menu_rect_center1), mixer_volume)]
    esc_value_box = [
        menu.ValueBox(esc_menu_images["value"], (battle_menu.rect.topright[0] * 1.08, menu_rect_center1), mixer_volume)]

    return {"battle_menu": battle_menu, "battle_menu_button": battle_menu_button,
            "esc_option_menu_button": esc_option_menu_button,
            "esc_slider_menu": esc_slider_menu, "esc_value_box": esc_value_box}
