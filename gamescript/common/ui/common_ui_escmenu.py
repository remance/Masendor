import pygame
from gamescript import lorebook
from gamescript.common import utility

editconfig = utility.edit_config

lorebook_process = lorebook.lorebook_process


def escmenu_process(self, mouse_up: bool, mouse_leftdown: bool, esc_press: bool, mouse_scrollup: bool,
                    mouse_scrolldown: bool, uidraw: pygame.sprite.LayeredUpdates):
    """
    ESC menu user interaction
    :param self: self process object, battle
    :param mouse_up: mouse left click release
    :param mouse_leftdown: mouse hold left click
    :param esc_press: esc button
    :param mouse_scrollup: mouse wheel scroll up
    :param mouse_scrolldown: mouse wheel scroll down
    :param uidraw: ui drawer object
    :return: special command that process in battle loop
    """

    command = None
    if esc_press and self.battle_menu.mode in ("menu", "option"):  # in menu or option
        if self.battle_menu.mode == "option":  # option menu
            self.master_volume = self.old_setting
            pygame.mixer.music.set_volume(self.master_volume)
            self.esc_slider_menu[0].player_input(self.master_volume, self.esc_value_box[0], forced_value=True)
            self.battle_menu.change_mode("menu")
        self.battle_ui_updater.remove(self.battle_menu, *self.battle_menu_button, *self.esc_option_menu_button,
                                      *self.esc_slider_menu, *self.esc_value_box)
        self.game_state = self.previous_game_state

    elif self.battle_menu.mode == "menu":  # start_set esc menu
        for button in self.battle_menu_button:
            if button.rect.collidepoint(self.mouse_pos):
                button.image = button.images[1]  # change button image to mouse over one
                if mouse_up:  # click on button
                    button.image = button.images[2]  # change button image to clicked one
                    if button.text == "Resume":  # resume self
                        self.game_state = self.previous_game_state  # resume battle gameplay state
                        self.battle_ui_updater.remove(self.battle_menu, *self.battle_menu_button, *self.esc_slider_menu,
                                                      *self.esc_value_box)  # remove menu sprite

                    elif button.text == "Encyclopedia":  # open encyclopedia
                        self.battle_menu.change_mode("encyclopedia")  # change to enclycopedia mode
                        self.battle_ui_updater.add(self.encyclopedia, self.lore_name_list, self.lore_scroll,
                                                   *self.lore_button_ui)  # add sprite related to encyclopedia
                        self.encyclopedia.change_section(0, self.lore_name_list, self.subsection_name, self.lore_scroll,
                                                         self.page_button,
                                                         self.battle_ui_updater)
                        self.battle_ui_updater.remove(self.battle_menu, *self.battle_menu_button, *self.esc_slider_menu,
                                                      *self.esc_value_box)  # remove menu sprite

                    elif button.text == "Option":  # open option menu
                        self.battle_menu.change_mode("option")  # change to option menu mode
                        self.battle_ui_updater.remove(*self.battle_menu_button)  # remove start_set esc menu button
                        self.battle_ui_updater.add(*self.esc_option_menu_button, *self.esc_slider_menu, *self.esc_value_box)
                        self.old_setting = self.esc_slider_menu[0].value  # Save previous setting for in case of cancel

                    elif button.text == "End Battle":  # back to start_set menu
                        self.exit_battle()
                        command = "end_battle"

                    elif button.text == "Desktop":  # quit self
                        self.text_input_popup = ("confirm_input", "quit")
                        self.confirm_ui.change_instruction("Quit Game?")
                        self.battle_ui_updater.add(*self.confirm_ui_popup)
                    break  # found clicked button, break loop
            else:
                button.image = button.images[0]

    elif self.battle_menu.mode == "option":  # option menu
        for button in self.esc_option_menu_button:  # check if any button get collided with mouse or clicked
            if button.rect.collidepoint(self.mouse_pos):
                button.image = button.images[1]  # change button image to mouse over one
                if mouse_up:  # click on button
                    button.image = button.images[2]  # change button image to clicked one
                    if button.text == "Confirm":  # confirm button, save the setting and close option menu
                        self.old_setting = self.master_volume  # save mixer volume
                        pygame.mixer.music.set_volume(self.master_volume)  # set new music player volume
                        editconfig("DEFAULT", "master_volume", str(self.esc_slider_menu[0].value), "configuration.ini",
                                   self.config)  # save to config file
                        self.battle_menu.change_mode("menu")  # go back to start_set esc menu
                        self.battle_ui_updater.remove(*self.esc_option_menu_button, *self.esc_slider_menu,
                                                      *self.esc_value_box)  # remove option menu sprite
                        self.battle_ui_updater.add(*self.battle_menu_button)  # add start_set esc menu buttons back

                    elif button.text == "Apply":  # apply button, save the setting
                        self.old_setting = self.master_volume  # save mixer volume
                        pygame.mixer.music.set_volume(self.master_volume)  # set new music player volume
                        editconfig("DEFAULT", "master_volume", str(self.esc_slider_menu[0].value), "configuration.ini",
                                   self.config)  # save to config file

                    elif button.text == "Cancel":  # cancel button, revert the setting to the last saved one
                        self.master_volume = self.old_setting  # revert to old setting
                        pygame.mixer.music.set_volume(self.master_volume)  # set new music player volume
                        self.esc_slider_menu[0].player_input(self.master_volume, self.esc_value_box[0],
                                                       forced_value=True)  # update slider bar
                        self.battle_menu.change_mode("menu")  # go back to start_set esc menu
                        self.battle_ui_updater.remove(*self.esc_option_menu_button, *self.esc_slider_menu,
                                                      *self.esc_value_box)  # remove option menu sprite
                        self.battle_ui_updater.add(*self.battle_menu_button)  # add start_set esc menu buttons back

            else:  # no button currently collided with mouse
                button.image = button.images[0]  # revert button image back to the idle one

        for slider in self.esc_slider_menu:
            if slider.rect.collidepoint(self.mouse_pos) and (mouse_leftdown or mouse_up):  # mouse click on slider bar
                slider.player_input(self.mouse_pos, self.esc_value_box[0])  # update slider button based on mouse value
                self.master_volume = float(slider.value / 100)  # for now only music volume slider exist

    elif self.battle_menu.mode == "encyclopedia":  # Encyclopedia mode
        lore_command = lorebook_process(self, uidraw, mouse_up, mouse_leftdown, mouse_scrollup, mouse_scrolldown, esc_press)
        if esc_press or lore_command == "exit":
            self.battle_menu.change_mode("menu")  # change menu back to default 0
            self.game_state = self.previous_game_state  # resume gameplay
    return command
