def subunit_formation_change(self):
    self.setup_frontline()
    self.set_subunit_target()
    if self.control:
        self.battle.change_inspect_subunit()
    self.input_delay = 0.5
