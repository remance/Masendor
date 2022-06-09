def remove_unit_ui(self):
    self.troop_card_ui.option = 1  # reset subunit card option
    self.battle_ui_updater.remove(self.inspect_ui, *self.inspect_subunit, self.command_ui, self.troop_card_ui,
                                  self.troop_card_button, self.inspect_button, self.col_split_button,
                                  self.row_split_button, self.unitstat_ui,
                                  *self.behaviour_switch_button)  # remove change behaviour button and inspect ui subunit
    self.inspect = False  # inspect ui close
    self.battle_ui_updater.remove(*self.leader_now)  # remove leader image from command ui
    self.subunit_selected = None  # reset subunit selected
    self.battle_ui_updater.remove(self.inspect_selected_border)  # remove subunit selected border sprite
    self.leader_now = []  # clear leader list in command ui
