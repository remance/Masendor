import pygame
from gamescript import commonscript, lorebook

editconfig = commonscript.edit_config

lorebook_process = lorebook.lorebook_process

def escmenu_process(self, mouse_up: bool, mouse_leftdown: bool, esc_press: bool, mouse_scrollup: bool,
                    mouse_scrolldown: bool, uidraw: pygame.sprite.LayeredUpdates):
    """
    ESC menu user interaction
    :param self: game process object, battle
    :param mouse_up: mouse left click release
    :param mouse_leftdown: mouse hold left click
    :param esc_press: esc button
    :param mouse_scrollup: mouse wheel scroll up
    :param mouse_scrolldown: mouse wheel scroll down
    :param uidraw: ui drawer object
    :return: special command that process in battle loop
    """

    command = None

    if esc_press and self.battle_menu.mode in (0, 1):  # in menu or option
        if self.battle_menu.mode == 1:  # option menu
            self.mixervolume = self.oldsetting
            pygame.mixer.music.set_volume(self.mixervolume)
            self.escslidermenu[0].update(self.mixervolume, self.escvaluebox[0], forcedvalue=True)
            self.battle_menu.change_mode(0)
        self.battleui.remove(self.battle_menu, *self.battle_menu_button, *self.escoptionmenubutton,
                             *self.escslidermenu, *self.escvaluebox)
        self.gamestate = self.previous_gamestate

    elif self.battle_menu.mode == 0:  # gamestart esc menu
        for button in self.battle_menu_button:
            if button.rect.collidepoint(self.mousepos):
                button.image = button.images[1]  # change button image to mouse over one
                if mouse_up:  # click on button
                    button.image = button.images[2]  # change button image to clicked one
                    if button.text == "Resume":  # resume game
                        self.gamestate = self.previous_gamestate  # resume battle gameplay state
                        self.battleui.remove(self.battle_menu, *self.battle_menu_button, *self.escslidermenu,
                                             *self.escvaluebox)  # remove menu sprite

                    elif button.text == "Encyclopedia":  # open encyclopedia
                        self.battle_menu.change_mode(2)  # change to enclycopedia mode
                        self.battleui.add(self.lorebook, self.lorenamelist, self.lorescroll,
                                          *self.lorebuttonui)  # add sprite related to encyclopedia
                        self.lorebook.change_section(0, self.lorenamelist, self.subsection_name, self.lorescroll, self.pagebutton,
                                                     self.battleui)
                        self.battleui.remove(self.battle_menu, *self.battle_menu_button, *self.escslidermenu,
                                             *self.escvaluebox)  # remove menu sprite
                        # self.lorebook.setupsubsectionlist(self.lorenamelist, listgroup)

                    elif button.text == "Option":  # open option menu
                        self.battle_menu.change_mode(1)  # change to option menu mode
                        self.battleui.remove(*self.battle_menu_button)  # remove gamestart esc menu button
                        self.battleui.add(*self.escoptionmenubutton, *self.escslidermenu, *self.escvaluebox)
                        self.oldsetting = self.escslidermenu[0].value  # Save previous setting for in case of cancel

                    elif button.text == "End Battle":  # back to gamestart menu
                        print('test')
                        self.exitbattle()
                        command = "end_battle"

                    elif button.text == "Desktop":  # quit game
                        self.textinputpopup = ("confirm_input", "quit")
                        self.confirmui.change_instruction("Quit Game?")
                        self.battleui.add(*self.confirmui_pop)
                    break  # found clicked button, break loop
            else:
                button.image = button.images[0]

    elif self.battle_menu.mode == 1:  # option menu
        for button in self.escoptionmenubutton:  # check if any button get collided with mouse or clicked
            if button.rect.collidepoint(self.mousepos):
                button.image = button.images[1]  # change button image to mouse over one
                if mouse_up:  # click on button
                    button.image = button.images[2]  # change button image to clicked one
                    if button.text == "Confirm":  # confirm button, save the setting and close option menu
                        self.oldsetting = self.mixervolume  # save mixer volume
                        pygame.mixer.music.set_volume(self.mixervolume)  # set new music player volume
                        editconfig("DEFAULT", "SoundVolume", str(self.escslidermenu[0].value), "configuration.ini",
                                   self.config)  # save to config file
                        self.battle_menu.change_mode(0)  # go back to gamestart esc menu
                        self.battleui.remove(*self.escoptionmenubutton, *self.escslidermenu,
                                             *self.escvaluebox)  # remove option menu sprite
                        self.battleui.add(*self.battle_menu_button)  # add gamestart esc menu buttons back

                    elif button.text == "Apply":  # apply button, save the setting
                        self.oldsetting = self.mixervolume  # save mixer volume
                        pygame.mixer.music.set_volume(self.mixervolume)  # set new music player volume
                        editconfig("DEFAULT", "SoundVolume", str(self.escslidermenu[0].value), "configuration.ini",
                                   self.config)  # save to config file

                    elif button.text == "Cancel":  # cancel button, revert the setting to the last saved one
                        self.mixervolume = self.oldsetting  # revert to old setting
                        pygame.mixer.music.set_volume(self.mixervolume)  # set new music player volume
                        self.escslidermenu[0].update(self.mixervolume, self.escvaluebox[0], forcedvalue=True)  # update slider bar
                        self.battle_menu.change_mode(0)  # go back to gamestart esc menu
                        self.battleui.remove(*self.escoptionmenubutton, *self.escslidermenu,
                                             *self.escvaluebox)  # remove option menu sprite
                        self.battleui.add(*self.battle_menu_button)  # add gamestart esc menu buttons back

            else:  # no button currently collided with mouse
                button.image = button.images[0]  # revert button image back to the idle one

        for slider in self.escslidermenu:
            if slider.rect.collidepoint(self.mousepos) and (mouse_leftdown or mouse_up):  # mouse click on slider bar
                slider.update(self.mousepos, self.escvaluebox[0])  # update slider button based on mouse value
                self.mixervolume = float(slider.value / 100)  # for now only music volume slider exist

    elif self.battle_menu.mode == 2:  # Encyclopedia mode
        lorecommand = lorebook_process(self, uidraw, mouse_up, mouse_leftdown, mouse_scrollup, mouse_scrolldown)
        if esc_press or lorecommand == "exit":
            self.battle_menu.change_mode(0)  # change menu back to default 0
            self.gamestate = self.previous_gamestate  # resume gameplay
    return command