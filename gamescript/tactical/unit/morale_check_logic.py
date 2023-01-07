def morale_check_logic(self):
    if self.morale <= 10:  # Retreat state when morale lower than 10
        self.broken = True
        for this_subunit in self.alive_subunit_list:
            if this_subunit.broken is False:  # unit not broken yet since there is subunit not broken
                self.broken = False
        if self.state not in (98, 99):
            self.state = 98
        if self.retreat_start is False:
            self.retreat_start = True

    elif self.retreat_start and self.broken is False and self.morale >= 50:  # quit retreat when morale reach increasing limit
        self.retreat_start = False
        self.retreat_way = None
        self.issue_order(self.base_pos, False, False, other_command="Stop")

    if self.retreat_start and self.state != 96:
        self.retreat()
