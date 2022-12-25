def start_retreat(self, pos):
    self.state = 96  # controlled retreat state (not same as 98)
    self.command_state = self.state  # command retreat
    self.leader[0].authority -= self.auth_penalty  # retreat reduce enter_battle leader authority
    if self.charging:  # change order when attacking will cause authority penalty
        self.leader[0].authority -= self.auth_penalty
    self.authority_recalculation()
    self.retreat_start = True  # start retreat process
    self.set_target(pos)
    self.revert_move()
    self.command_target = self.base_target
