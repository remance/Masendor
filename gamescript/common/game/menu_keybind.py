import pygame

from gamescript.common import utility

edit_config = utility.edit_config


def menu_keybind(self, mouse_left_up, esc_press):
    if self.back_button.event or esc_press:  # back to start_set menu
        self.back_button.event = False

        self.menu_state = "option"
        self.main_ui_updater.remove(*self.keybind_text.values(), self.keybind_icon.values(), self.control_switch)
        self.main_ui_updater.add(*self.menu_button, *self.option_menu_sliders.values(), *self.value_boxes.values())
        self.main_ui_updater.add(*self.option_text_list)

    elif self.default_button.event:  # revert all keybind to original
        self.default_button.event = False
        for setting in self.config["DEFAULT"]:
            if setting == "keybind":
                edit_config("USER", setting, self.config["DEFAULT"][setting], "configuration.ini", self.config)
        control_type = self.config["USER"]["control player 1"]
        for key, value in self.keybind_icon.items():
            if self.joysticks:
                value.change_key(control_type, self.config["USER"]["keybind player 1"][control_type][key],
                                 self.joystick_bind_name[self.joystick_name[0]])
            else:
                value.change_key(control_type, self.config["USER"]["keybind player 1"][control_type][key], None)

    elif mouse_left_up:
        if self.control_switch.rect.collidepoint(self.mouse_pos):
            if self.joysticks:
                if self.config["USER"]["control player 1"] == "keyboard":
                    self.config["USER"]["control player 1"] = "joystick"
                    self.control_switch.change_control("joystick1")
                else:
                    # if self.config["USER"]["control player 2"] == "joystick"
                    self.config["USER"]["control player 1"] = "keyboard"
                    self.control_switch.change_control("keyboard")
                edit_config("USER", "control player 1", self.config["USER"]["control player 1"],
                            "configuration.ini", self.config)
                for key, value in self.keybind_icon.items():
                    if self.joysticks:
                        value.change_key(self.config["USER"]["control player 1"],
                                         self.player1_key_bind[self.config["USER"]["control player 1"]][key],
                                         self.joystick_bind_name[self.joystick_name[0]])
                    else:
                        value.change_key(self.config["USER"]["control player 1"],
                                         self.player1_key_bind[self.config["USER"]["control player 1"]][key],
                                         None)

            else:
                self.input_popup = ("confirm_input", "warning")
                self.input_ui.change_instruction("No joysticks detected")
                self.main_ui_updater.add(self.inform_ui_popup)

        else:
            for key, value in self.keybind_icon.items():
                if value.rect.collidepoint(self.mouse_pos):
                    self.input_popup = ("keybind_input", key)
                    self.input_ui.change_instruction("Assign key for " + key)
                    current_key = self.player1_key_bind[self.config["USER"]["control player 1"]][key]
                    if type(current_key) == int:
                        current_key = pygame.key.name(current_key)
                    self.input_box.text_start("Current Key: " + current_key)
                    self.main_ui_updater.add(self.inform_ui_popup)
