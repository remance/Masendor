def state_reset_logic(self, parent_state):
    """Simply reset to idle state for arcade mode as it use independent action"""
    if self.state not in (95, 97, 98, 99) and parent_state in (0, 1, 2, 3, 4, 5, 6, 95, 96, 97, 98, 99):
        self.state = parent_state  # Enforce unit state to subunit when moving and breaking
