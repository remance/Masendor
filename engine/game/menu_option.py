import pygame

from engine.common import utility

edit_config = utility.edit_config


def menu_option(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if self.back_button.event or esc_press:  # back to start_set menu
        self.back_button.event = False
        self.main_ui_updater.remove(*self.option_text_list, *self.option_menu_sliders.values(),
                                    *self.value_boxes.values())
        self.back_mainmenu()

    elif self.keybind_button.event:
        self.keybind_button.event = False
        self.menu_state = "keybind"

        if self.joysticks:
            if self.config["USER"]["control player 1"] == "joystick":
                self.control_switch.change_control("joystick1")
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

        else:  # no joystick, reset player 1 to keyboard
            self.config["USER"]["control player 1"] = "keyboard"
            edit_config("USER", "control player 1", "keyboard", "configuration.ini", self.config)
            self.control_switch.change_control("keyboard")
            for key, value in self.keybind_icon.items():
                if self.joysticks:
                    value.change_key(self.config["USER"]["control player 1"],
                                     self.player1_key_bind[self.config["USER"]["control player 1"]][key],
                                     self.joystick_bind_name[self.joystick_name[tuple(self.joystick_name.keys())[0]]])
                else:
                    value.change_key(self.config["USER"]["control player 1"],
                                     self.player1_key_bind[self.config["USER"]["control player 1"]][key],
                                     None)

        self.main_ui_updater.remove(*self.option_text_list, *self.option_menu_sliders.values(),
                                    *self.value_boxes.values(), self.option_menu_button)
        self.main_ui_updater.add(*self.keybind_text.values(), *self.keybind_icon.values(), self.control_switch,
                                 self.back_button, self.default_button)

    elif self.default_button.event:  # revert all setting to original
        self.default_button.event = False
        for setting in self.config["DEFAULT"]:
            if setting not in ("genre", "language", "player_name", "keybind"):
                edit_config("USER", setting, self.config["DEFAULT"][setting], "configuration.ini", self.config)

        change_resolution(self, (int(self.config["DEFAULT"]["screen_width"]), "",
                                 int(self.config["DEFAULT"]["screen_height"])))

    if mouse_left_up or mouse_left_down:
        for key, value in self.option_menu_sliders.items():
            if value.rect.collidepoint(self.mouse_pos) and (mouse_left_down or mouse_left_up):  # click on slider bar
                value.player_input(self.mouse_pos, self.value_boxes[key])  # update slider button based on mouse value
                edit_config("USER", key + "_volume", value.value, "configuration.ini",
                            self.config)
                self.change_sound_volume()

        if mouse_left_up:
            if self.resolution_drop.rect.collidepoint(self.mouse_pos):  # click on resolution bar
                if self.resolution_bar in self.main_ui_updater:  # remove the bar list if click again
                    self.main_ui_updater.remove(self.resolution_bar)
                    self.menu_button.remove(self.resolution_bar)
                else:  # add bar list
                    self.main_ui_updater.add(self.resolution_bar)
                    self.menu_button.add(self.resolution_bar)

            elif self.fullscreen_box.rect.collidepoint(self.mouse_pos):
                if self.fullscreen_box.tick is False:
                    self.fullscreen_box.change_tick(True)
                    self.full_screen = 1
                else:
                    self.fullscreen_box.change_tick(False)
                    self.full_screen = 0
                edit_config("USER", "full_screen", self.full_screen, "configuration.ini",
                            self.config)
                change_resolution(self, (self.screen_width, "", self.screen_height))

            else:
                for bar in self.resolution_bar:  # loop to find which resolution bar is selected, this happens outside of clicking check below
                    if bar.event:
                        bar.event = False
                        self.resolution_drop.change_state(bar.text)  # change button value based on new selected value
                        resolution_change = bar.text.split()
                        change_resolution(self, resolution_change)
                        break
                self.main_ui_updater.remove(self.resolution_bar)


def change_resolution(self, resolution_change):
    from engine import game
    self.screen_width = resolution_change[0]
    self.screen_height = resolution_change[2]

    edit_config("USER", "screen_width", self.screen_width, "configuration.ini",
                self.config)
    edit_config("USER", "screen_height", self.screen_height, "configuration.ini",
                self.config)

    pygame.time.wait(1000)
    if pygame.mixer:
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    pygame.quit()
    runmenu = game.Game(self.main_dir, self.error_log)  # restart game when change resolution
