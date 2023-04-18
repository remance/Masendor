from gamescript.common import utility

edit_config = utility.edit_config


def assign_key(self, key_assign):
    if key_assign not in self.player1_key_binding[self.config["USER"]["control player 1"]].values():
        print("hm")
        self.player1_key_binding[self.config["USER"]["control player 1"]][
            self.input_popup[1]] = key_assign
        edit_config("USER", "keybinding player 1", self.player1_key_binding,
                    "configuration.ini", self.config)
        for key, value in self.keybinding_icon.items():
            print(key, self.input_popup[1])
            if key == self.input_popup[1]:
                value.change_key(self.config["USER"]["control player 1"], key_assign)

        self.input_box.text_start("")
        self.input_popup = (None, None)
        self.main_ui_updater.remove(*self.input_ui_popup, *self.confirm_ui_popup, *self.inform_ui_popup)

    else:  # key already exist, confirm to swap key between two actions
        old_action = tuple(self.player1_key_binding[
                               self.config["USER"]["control player 1"]].values()).index(
            key_assign)
        old_action = \
            tuple(self.player1_key_binding[self.config["USER"]["control player 1"]].keys())[
                old_action]
        self.confirm_ui.change_instruction("Swap key with " + old_action + " ?")
        self.input_popup = (
            "confirm_input", ("replace key", self.input_popup[1], old_action))
        self.main_ui_updater.remove(*self.input_ui_popup, *self.confirm_ui_popup, *self.inform_ui_popup)
        self.main_ui_updater.add(self.confirm_ui_popup)
