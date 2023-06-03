import pygame

from engine.utility import edit_config


def menu_option(self, esc_press):
    bar_press = False
    for bar in self.resolution_bar:  # loop to find which resolution bar is selected, this happens outside of clicking check below
        if bar.event_press:
            self.resolution_drop.change_state(bar.text)  # change button value based on new selected value
            resolution_change = bar.text.split()
            change_resolution(self, resolution_change)
            self.remove_ui_updater(self.resolution_bar)
            bar_press = True
    if not bar_press and self.cursor.is_select_just_up:
        self.remove_ui_updater(self.resolution_bar)

    if self.back_button.event_press or esc_press:  # back to start_set menu
        self.remove_ui_updater(*self.option_menu_button, *self.option_text_list, *self.option_menu_sliders.values(),
                               *self.value_boxes.values(), self.resolution_bar, self.profile_box)
        self.back_mainmenu()

    elif self.keybind_button.event_press:
        self.menu_state = "keybind"

        if self.joysticks:
            if self.config["USER"]["control player 1"] == "joystick":  # player has joystick when first enter option
                self.control_switch.change_control("joystick1")
                self.player1_key_control = self.config["USER"]["control player 1"]
                self.player1_battle_cursor.change_input(self.player1_key_bind)
                for key, value in self.keybind_icon.items():
                    value.change_key(self.config["USER"]["control player 1"],
                                     self.player1_key_bind[self.config["USER"]["control player 1"]][key],
                                     self.joystick_bind_name[
                                         self.joystick_name[tuple(self.joystick_name.keys())[0]]])

        else:  # no joystick, reset player 1 to keyboard
            self.config["USER"]["control player 1"] = "keyboard"
            edit_config("USER", "control player 1", "keyboard", "configuration.ini", self.config)
            self.control_switch.change_control("keyboard")
            self.player1_key_control = self.config["USER"]["control player 1"]
            self.player1_battle_cursor.change_input(self.player1_key_bind)
            for key, value in self.keybind_icon.items():
                value.change_key(self.config["USER"]["control player 1"],
                                 self.player1_key_bind[self.config["USER"]["control player 1"]][key],
                                 None)

        self.remove_ui_updater(*self.option_text_list, *self.option_menu_sliders.values(),
                               *self.value_boxes.values(), self.option_menu_button)
        self.add_ui_updater(*self.keybind_text.values(), *self.keybind_icon.values(), self.control_switch,
                            self.back_button, self.default_button)

    elif self.default_button.event_press:  # revert all setting to original
        for setting in self.config["DEFAULT"]:
            if setting not in ("genre", "language", "player_name", "keybind"):
                edit_config("USER", setting, self.config["DEFAULT"][setting], "configuration.ini", self.config)

        change_resolution(self, (int(self.config["DEFAULT"]["screen_width"]), "",
                                 int(self.config["DEFAULT"]["screen_height"])))

    elif self.resolution_drop.event_press:  # click on resolution bar
        if self.resolution_bar in self.main_ui_updater:  # remove the bar list if click again
            self.remove_ui_updater(self.resolution_bar)
        else:  # add bar list
            self.add_ui_updater(self.resolution_bar)

    elif self.fullscreen_box.event_press:
        if self.fullscreen_box.tick is False:
            self.fullscreen_box.change_tick(True)
            self.full_screen = 1
        else:
            self.fullscreen_box.change_tick(False)
            self.full_screen = 0
        edit_config("USER", "full_screen", self.full_screen, "configuration.ini",
                    self.config)
        change_resolution(self, (self.screen_width, "", self.screen_height))

    elif self.profile_box.event_press:
        self.input_popup = ("text_input", "profile_name")
        self.input_box.text_start(self.profile_name)
        self.input_ui.change_instruction("Profile Name:")
        self.add_ui_updater(self.input_ui_popup)

    for key, value in self.option_menu_sliders.items():
        if value.event:  # press on slider bar
            value.player_input(self.value_boxes[key])  # update slider button based on mouse value
            edit_config("USER", key + "_volume", value.value, "configuration.ini",
                        self.config)
            self.change_sound_volume()


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
    game.game.Game(self.main_dir, self.error_log)  # restart game when change resolution
