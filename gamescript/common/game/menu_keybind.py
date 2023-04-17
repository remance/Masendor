import pygame

from gamescript.common import utility

edit_config = utility.edit_config


def menu_keybind(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if self.back_button.event or esc_press:  # back to start_set menu
        self.back_button.event = False

        self.menu_state = "option"
        self.main_ui_updater.remove(*self.keybinding_text.values(), self.keybinding_icon.values())
        self.main_ui_updater.add(*self.menu_button, *self.option_menu_sliders.values(), *self.value_boxes.values())
        self.main_ui_updater.add(*self.option_text_list)

    elif self.default_button.event:  # revert all keybinding to original
        self.default_button.event = False
        for setting in self.config["DEFAULT"]:
            if setting == "keybinding":
                edit_config("USER", setting, self.config["DEFAULT"][setting], "configuration.ini", self.config)

    elif mouse_left_up:
        for key, value in self.keybinding_icon.items():
            if value.rect.collidepoint(self.mouse_pos):
                self.input_popup = ("keybinding_input", key)
                self.input_ui.change_instruction("Assign key for " + key)
                self.main_ui_updater.add(self.input_ui_popup)
