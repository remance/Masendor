import pygame

from engine.utility import edit_config


def menu_keybind(self, esc_press):
    if self.back_button.event or esc_press:  # back to start_set menu
        self.back_button.event = False

        self.menu_state = "option"
        self.remove_ui_updater(*self.keybind_text.values(), self.keybind_icon.values(), self.control_switch)
        self.add_ui_updater(*self.option_menu_button, *self.option_menu_sliders.values(), *self.value_boxes.values())
        self.add_ui_updater(*self.option_text_list)

    elif self.default_button.event:  # revert all keybind to original
        self.default_button.event = False
        for setting in self.config["DEFAULT"]:
            if setting == "keybind":
                edit_config("USER", setting, self.config["DEFAULT"][setting], "configuration.ini", self.config)
        control_type = self.config["USER"]["control player 1"]
        for key, value in self.keybind_icon.items():
            if self.joysticks:
                value.change_key(control_type, self.config["USER"]["keybind player 1"][control_type][key],
                                 self.joystick_bind_name[self.joystick_name[tuple(self.joystick_name.keys())[0]]])
            else:
                value.change_key(control_type, self.config["USER"]["keybind player 1"][control_type][key], None)

    if self.control_switch.event_press:
        if self.joysticks:
            if self.config["USER"]["control player 1"] == "keyboard":
                self.config["USER"]["control player 1"] = "joystick"
                self.control_switch.change_control("joystick1")
            else:
                # if self.config["USER"]["control player 2"] == "joystick"
                self.config["USER"]["control player 1"] = "keyboard"
                self.control_switch.change_control("keyboard")
            self.player1_key_control = self.config["USER"]["control player 1"]
            self.player1_battle_cursor.change_input(self.player1_key_bind)
            edit_config("USER", "control player 1", self.config["USER"]["control player 1"],
                        "configuration.ini", self.config)
            for key, value in self.keybind_icon.items():
                if self.joysticks:
                    value.change_key(self.config["USER"]["control player 1"],
                                     self.player1_key_bind[self.config["USER"]["control player 1"]][key],
                                     self.joystick_bind_name[
                                         self.joystick_name[tuple(self.joystick_name.keys())[0]]])
                else:
                    value.change_key(self.config["USER"]["control player 1"],
                                     self.player1_key_bind[self.config["USER"]["control player 1"]][key],
                                     None)

        else:
            self.activate_input_popup(("confirm_input", "warning"),
                                      "No joysticks detected", self.inform_ui_popup)

    else:
        for key, value in self.keybind_icon.items():
            if value.event_press:
                self.activate_input_popup(("keybind_input", key),
                                          "Assign key for " + key, self.inform_ui_popup)
                current_key = self.player1_key_bind[self.config["USER"]["control player 1"]][key]
                if type(current_key) == int:
                    current_key = pygame.key.name(current_key)
                self.input_box.text_start("Current Key: " + current_key)
