def state_reset_logic(self):
    """Check if any subunit still fighting, if not change to idle state"""
    if self.state == 10:
        stop_fight = True
        for subunit in self.alive_subunit_list:
            if subunit.state == 10:
                stop_fight = False
                break
        if stop_fight:
            self.state = 0
