def add_behaviour_ui(self, who_input, else_check=False):
    if who_input.player_control:
        # self.battle_ui.add(self.button_ui[7])  # add decimation button
        self.battle_ui_updater.add(*self.behaviour_switch_button[0:7])  # add unit behaviour change button
        self.behaviour_switch_button[0].event = who_input.skill_cond
        self.behaviour_switch_button[1].event = who_input.fire_at_will
        self.behaviour_switch_button[2].event = who_input.hold
        self.behaviour_switch_button[3].event = who_input.use_min_range
        self.behaviour_switch_button[4].event = who_input.shoot_mode
        self.behaviour_switch_button[5].event = who_input.run_toggle
        self.behaviour_switch_button[6].event = who_input.attack_mode
        who_input.check_split()  # check if selected unit can split, if yes draw button
    elif else_check:
        if self.row_split_button in self.battle_ui_updater:
            self.row_split_button.kill()
        if self.col_split_button in self.battle_ui_updater:
            self.col_split_button.kill()
        # self.battle_ui.remove(self.button_ui[7])  # remove decimation button
        self.battle_ui_updater.remove(*self.behaviour_switch_button[0:7])  # remove unit behaviour change button

    self.leader_now = who_input.leader
    self.battle_ui_updater.add(*self.leader_now)  # add leader portrait to draw
    self.unitstat_ui.value_input(who=who_input, split=self.split_happen)
    self.command_ui.value_input(who=who_input, split=self.split_happen)
