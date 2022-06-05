
def chase(self):
    """Chase unit in base_target and rotate accordingly"""
    if self.state in (3, 4, 5, 6, 10) and self.command_state in (3, 4, 5, 6) and self.attack_target is not None and self.hold == 0:
        if self.attack_target.state != 100:
            if self.collide is False:
                self.state = self.command_state  # resume melee_attack command
                if self.base_pos.distance_to(self.attack_target.base_pos) < 10:
                    self.set_target(self.attack_target.leader_subunit.base_pos)  # set base_target to cloest enemy's side
                else:
                    self.set_target(self.attack_target.base_pos)
                self.base_attack_pos = self.base_target
                self.new_angle = self.set_rotate()  # keep rotating while chasing
        else:  # enemy dead stop chasing
            self.attack_target = None
            self.base_attack_pos = None
            self.process_command(self.front_pos, other_command=1)
