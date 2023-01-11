def subunit_formation_change(self):
    self.setup_formation()
    self.set_subunit_target()
    if self.player_control:
        self.battle.change_inspect_subunit()
    self.input_delay = 0.5
