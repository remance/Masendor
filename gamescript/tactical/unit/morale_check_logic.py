def morale_check_logic(self):
    if self.morale <= 10:  # Retreat state when morale lower than 10
        if self.state not in (98, 99):
            self.state = 98
        if self.retreat_start is False:
            self.retreat_start = True

    elif self.state == 98 and self.morale >= 50:  # quit retreat when morale reach increasing limit
        self.state = 0  # become idle, not resume previous command
        self.retreat_start = False
        self.retreat_way = None
        self.process_command(self.base_pos, False, False, other_command="Stop")

    if self.retreat_start and self.state != 96:
        self.retreat()
