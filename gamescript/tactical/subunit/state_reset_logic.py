def state_reset_logic(self, unit_state):
    if unit_state in (1, 2, 3, 4):
        self.attacking = True
    elif self.attacking and unit_state not in (
    1, 2, 3, 4, 10):  # cancel charge when no longer move to melee or in combat
        self.attacking = False
    if self.state not in (95, 97, 98, 99) and unit_state in (0, 1, 2, 3, 4, 5, 6, 95, 96, 97, 98, 99):
        self.state = unit_state  # Enforce unit state to subunit when moving and breaking
    self.attack_target = self.unit.attack_target
    self.attack_pos = self.unit.base_attack_pos
