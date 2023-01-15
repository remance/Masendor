def state_reset_logic(self):
    if self.state not in (98, 99):  # not in retreat or broken state
        self.state = 0  # unit state change to idle every reset first

