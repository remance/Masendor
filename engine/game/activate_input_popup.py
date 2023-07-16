def activate_input_popup(self, input_popup, instruction, input_ui_list):
    self.remove_ui_updater(self.all_input_ui_popup)  # remove any previous input ui first
    self.change_pause_update(True, except_list=self.all_input_ui_popup)

    self.input_popup = input_popup
    self.input_ui.change_instruction(instruction)
    self.add_ui_updater(input_ui_list)
