def state_reset_logic(self, unit_state):
    """Simply reset to idle state for arcade mode as it use independent action"""
    if self.state not in (95, 97, 98, 99) and unit_state in (0, 1, 2, 3, 4, 5, 6, 95, 96, 97, 98, 99):
        self.state = unit_state  # Enforce unit state to subunit when moving and breaking

    self.melee_target = None
    # if self.state == 0:
    #     if self.base_target != self.command_target:
    #         self.base_target = self.command_target
    #         self.new_angle = self.set_rotate(self.base_target)
    #     elif self.angle != self.unit.angle:  # reset angle
    #         self.new_angle = self.unit.angle
