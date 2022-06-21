def state_reset_logic(self):
    if self.state not in (98, 99):
        self.state = 0  # reset unit state to 0 idle by default
