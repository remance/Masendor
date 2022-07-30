def issue_order(self, target_pos, run_command=False, revert_move=False, enemy=None, other_command=None):
    """Process input order into state and subunit base_target action"""
    if self.state not in (98, 99, 100):
        if other_command is None:  # move
            self.state = 1
            if run_command:
                self.state += 1  # run state

            self.command_target = self.base_target
            if revert_move:  # revert subunit without rotate, cannot run in this state
                self.set_target(target_pos)
            else:  # rotate unit only
                self.new_angle = self.set_rotate(target_pos)
                self.set_subunit_target()
        elif type(other_command) == str:
            if "Skill" in other_command:
                if "Charge" in other_command:  # also move when charge
                    self.state = 4
                    self.set_target(target_pos)
                    for subunit in self.alive_subunit_list:
                        subunit.command_action = (other_command, )
                        subunit.state = 4
                else:
                    for subunit in self.alive_subunit_list:
                        subunit.command_action = (other_command, )

            elif "Action" in other_command:  # for releasing attack after charging
                for subunit in self.alive_subunit_list:
                    subunit.command_action = (other_command, )
                    subunit.interrupt_animation = True
                    subunit.idle_action = ()

        self.command_state = self.state
