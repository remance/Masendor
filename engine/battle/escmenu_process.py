from pygame import Vector2

from pygame.mixer import music

from engine.utility import edit_config


def escmenu_process(self, esc_press: bool):
    """
    User interaction processing for ESC menu during battle
    :param self: Battle object
    :param esc_press: esc button
    :return: special command that process in battle loop
    """

    command = None
    if esc_press and self.battle_menu.mode in ("menu", "option"):  # in menu or option
        back_to_battle_state(self)

    elif self.battle_menu.mode == "menu":  # esc menu
        for button in self.battle_menu_button:
            if button.event_press:
                if button.text == "Resume":  # resume battle
                    back_to_battle_state(self)

                elif button.text == "Encyclopedia":  # open encyclopedia
                    self.battle_menu.change_mode("encyclopedia")  # change to enclycopedia mode
                    self.add_ui_updater(self.encyclopedia_stuff)  # add sprite related to encyclopedia
                    self.encyclopedia.change_section(0, self.lore_name_list, self.subsection_name,
                                                     self.tag_filter_name,
                                                     self.lore_name_list.scroll, self.filter_tag_list,
                                                     self.filter_tag_list.scroll)
                    self.remove_ui_updater(self.battle_menu, self.battle_menu_button, self.esc_slider_menu,
                                           self.esc_value_boxes)  # remove menu sprite

                elif button.text == "Option":  # open option menu TODO remake this
                    self.battle_menu.change_mode("option")  # change to option menu mode
                    self.remove_ui_updater(self.battle_menu_button)  # remove start_set esc menu button
                    self.add_ui_updater(self.esc_option_menu_button, self.esc_slider_menu,
                                        self.esc_value_boxes)
                    self.old_setting = self.esc_slider_menu[0].value  # Save previous setting for in case of cancel

                elif button.text == "End Battle":  # back to start_set menu
                    self.exit_battle()
                    command = "end_battle"

                elif button.text == "Desktop":  # quit self
                    self.activate_input_popup(("confirm_input", "quit"), "Quit Game?", self.confirm_ui_popup)
                break  # found clicked button, break loop
            else:
                button.image = button.images[0]

    elif self.battle_menu.mode == "encyclopedia":  # esc menu
        command = self.lorebook_process(esc_press)
        if command == "exit":
            self.battle_menu.change_mode("menu")  # go back to start_set esc menu
            self.add_ui_updater(self.battle_menu_button)  # add start_set esc menu buttons back

    elif self.battle_menu.mode == "option":  # option menu
        for button in self.esc_option_menu_button:  # check if any button get collided with mouse or clicked
            if button.event_press:
                if button.text == "Confirm":  # confirm button, save the setting and close option menu
                    self.old_setting = self.master_volume  # save mixer volume

                    self.change_sound_volume()

                    edit_config("USER", "master_volume", self.esc_slider_menu[0].value, "configuration.ini",
                                self.config)  # save to config file
                    self.battle_menu.change_mode("menu")  # go back to start_set esc menu
                    self.remove_ui_updater(self.esc_option_menu_button, self.esc_slider_menu,
                                           self.esc_value_boxes)  # remove option menu sprite
                    self.add_ui_updater(self.battle_menu_button)  # add start_set esc menu buttons back

                elif button.text == "Apply":  # apply button, save the setting
                    self.old_setting = self.master_volume  # save mixer volume
                    music.set_volume(self.master_volume)  # set new music player volume
                    edit_config("USER", "master_volume", self.esc_slider_menu[0].value, "configuration.ini",
                                self.config)  # save to config file

                elif button.text == "Cancel":  # cancel button, revert the setting to the last saved one
                    self.master_volume = self.old_setting  # revert to old setting
                    music.set_volume(self.master_volume)  # set new music player volume
                    self.esc_slider_menu[0].player_input(self.esc_value_boxes[0],
                                                         forced_value=True)  # update slider bar
                    self.battle_menu.change_mode("menu")  # go back to start_set esc menu
                    self.remove_ui_updater(self.esc_option_menu_button, self.esc_slider_menu,
                                           self.esc_value_boxes)  # remove option menu sprite
                    self.add_ui_updater(self.battle_menu_button)  # add start_set esc menu buttons back

    return command


def back_to_battle_state(self):
    if self.battle_menu.mode == "option":  # option menu
        self.master_volume = self.old_setting
        music.set_volume(self.master_volume)
        self.esc_slider_menu[0].player_input(self.esc_value_boxes[0], forced_value=True)
        self.battle_menu.change_mode("menu")
    self.remove_ui_updater(self.battle_menu, self.battle_menu_button, self.esc_option_menu_button,
                           self.esc_slider_menu, self.esc_value_boxes, self.cursor)
    self.game_state = "battle"

    self.add_ui_updater(self.player1_battle_cursor)

    if self.player1_key_control != "keyboard":
        self.player1_battle_cursor.pos = Vector2(self.screen_rect.width / 2, self.screen_rect.height / 2)
