import pygame

from gamescript.common import utility

edit_config = utility.edit_config


def menu_option(self, mouse_left_up, mouse_left_down, mouse_scroll_up, mouse_scroll_down, esc_press):
    if self.back_button.event or esc_press:  # back to start_set menu
        self.back_button.event = False

        self.main_ui_updater.remove(*self.option_text_list, self.option_menu_slider, self.value_box)

        self.back_mainmenu()

    elif self.default_button.event:  # back to start_set menu
        self.back_button.event = False

        self.master_volume = float(self.config["DEFAULT"]["master_volume"])
        self.battle_game.master_volume = self.master_volume
        edit_config("USER", "master_volume", self.volume_slider.value, "configuration.ini",
                    self.config)
        pygame.mixer.music.set_volume(self.master_volume)

        if int(self.config["DEFAULT"]["screen_width"]) != self.screen_width or int(
                self.config["DEFAULT"]["screen_height"]) != self.screen_height:
            change_resolution(self, (int(self.config["DEFAULT"]["screen_width"]), "",
                                     int(self.config["DEFAULT"]["screen_height"])))

    if mouse_left_up or mouse_left_down:
        if self.volume_slider.rect.collidepoint(self.mouse_pos) and (
                mouse_left_down or mouse_left_up):  # mouse click on slider bar
            self.volume_slider.player_input(self.mouse_pos,
                                            self.value_box[0])  # update slider button based on mouse value
            self.master_volume = float(
                self.volume_slider.value / 100)  # for now only music volume slider exist
            self.battle_game.master_volume = self.master_volume
            edit_config("USER", "master_volume", self.volume_slider.value, "configuration.ini",
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

            elif self.animation_box.rect.collidepoint(self.mouse_pos):
                if self.animation_box.tick is False:
                    self.animation_box.change_tick(True)
                    self.play_troop_animation = 1
                else:
                    self.animation_box.change_tick(False)
                    self.play_troop_animation = 0
                self.battle_game.play_troop_animation = self.play_troop_animation
                edit_config("USER", "play_troop_animation", self.play_troop_animation, "configuration.ini",
                            self.config)
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
    from gamescript import game
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
