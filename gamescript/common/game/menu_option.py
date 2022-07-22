import pygame

from gamescript.common import utility

edit_config = utility.edit_config


def menu_option(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if self.back_button.event or esc_press:  # back to start_set menu
        self.back_button.event = False

        self.main_ui_updater.remove(*self.option_icon_list, self.option_menu_slider, self.value_box)

        self.back_mainmenu()

    if mouse_left_up or mouse_left_down:
        if self.volume_slider.rect.collidepoint(self.mouse_pos) and (
                mouse_left_down or mouse_left_up):  # mouse click on slider bar
            self.volume_slider.player_input(self.mouse_pos,
                                            self.value_box[0])  # update slider button based on mouse value
            self.master_volume = float(
                self.volume_slider.value / 100)  # for now only music volume slider exist
            edit_config("DEFAULT", "master_volume", str(self.volume_slider.value), "configuration.ini",
                        self.config)
            pygame.mixer.music.set_volume(self.master_volume)

        if mouse_left_up:
            if self.resolution_drop.rect.collidepoint(self.mouse_pos):  # click on resolution bar
                if self.resolution_bar in self.main_ui_updater:  # remove the bar list if click again
                    self.main_ui_updater.remove(self.resolution_bar)
                    self.menu_button.remove(self.resolution_bar)
                else:  # add bar list
                    self.main_ui_updater.add(self.resolution_bar)
                    self.menu_button.add(self.resolution_bar)

            else:
                for bar in self.resolution_bar:  # loop to find which resolution bar is selected, this happens outside of clicking check below
                    if bar.event:
                        bar.event = False
                        self.resolution_drop.change_state(bar.text)  # change button value based on new selected value
                        resolution_change = bar.text.split()
                        self.new_screen_width = resolution_change[0]
                        self.new_screen_height = resolution_change[2]

                        edit_config("DEFAULT", "screen_width", self.new_screen_width, "configuration.ini",
                                    self.config)
                        edit_config("DEFAULT", "screen_height", self.new_screen_height, "configuration.ini",
                                    self.config)
                        self.screen = pygame.display.set_mode(self.screen_rect.size,
                                                              self.window_style | pygame.RESIZABLE, self.best_depth)
                        break
                self.main_ui_updater.remove(self.resolution_bar)
