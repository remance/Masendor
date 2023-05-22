from engine import utility

edit_config = utility.edit_config


def assign_key(self, key_assign):  # TODO prevent player from input right hat joystick (use only for mouse pos)
    if key_assign not in self.player1_key_bind[self.config["USER"]["control player 1"]].values():
        self.player1_key_bind[self.config["USER"]["control player 1"]][
            self.input_popup[1]] = key_assign
        edit_config("USER", "keybind player 1", self.player1_key_bind,
                    "configuration.ini", self.config)
        for key, value in self.keybind_icon.items():
            if key == self.input_popup[1]:
                if self.joysticks:
                    print(self.joystick_name)
                    value.change_key(self.config["USER"]["control player 1"], key_assign,
                                     self.joystick_bind_name[self.joystick_name[tuple(self.joystick_name.keys())[0]]])
                else:
                    value.change_key(self.config["USER"]["control player 1"], key_assign, None)

        self.input_box.text_start("")
        self.input_popup = None
        self.remove_ui_updater(*self.input_ui_popup, *self.confirm_ui_popup, *self.inform_ui_popup)

    else:  # key already exist, confirm to swap key between two actions
        old_action = tuple(self.player1_key_bind[
                               self.config["USER"]["control player 1"]].values()).index(
            key_assign)
        old_action = \
            tuple(self.player1_key_bind[self.config["USER"]["control player 1"]].keys())[
                old_action]
        self.confirm_ui.change_instruction("Swap key with " + old_action + " ?")
        self.input_popup = (
            "confirm_input", ("replace key", self.input_popup[1], old_action))
        self.remove_ui_updater(*self.input_ui_popup, *self.confirm_ui_popup, *self.inform_ui_popup)
        self.add_ui_updater(self.confirm_ui_popup)
