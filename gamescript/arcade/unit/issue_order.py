def issue_order(self, target_pos, run_command=False, revert_move=False, enemy=None, other_command=None):
    """Process input order into state and subunit base_target action"""
    if self.state not in (98, 99, 100):
        if other_command is None:  # move
            self.state = 1
            if run_command:
                self.state += 1  # run state

            self.command_target = self.base_target
            if revert_move:  # move subunit without rotate entire unit first
                self.set_target(target_pos)
            else:  # rotate unit only
                self.new_angle = self.set_rotate(target_pos)
                self.set_subunit_target()

        elif type(other_command) == str:
            if "Skill" in other_command:
                if "Charge" in other_command:  # also move when charge
                    self.state = 4
                    self.set_target(target_pos)
                    for this_subunit in self.alive_subunit_list:
                        if "uninterruptible" not in this_subunit.command_action:
                            if this_subunit.weapon_type[this_subunit.equipped_weapon][
                                int(other_command[-1])] == "ranged" and \
                                    this_subunit.weapon_type[
                                        this_subunit.swap_weapon_list[this_subunit.equipped_weapon]][
                                        int(other_command[-1])] == "melee":
                                this_subunit.swap_weapon(this_subunit.swap_weapon_list[
                                    this_subunit.equipped_weapon])  # swap to melee weapon for charge
                            this_subunit.command_action = {"name": other_command}
                            this_subunit.state = 4
                else:
                    for this_subunit in self.alive_subunit_list:
                        if "uninterruptible" not in this_subunit.command_action:
                            this_subunit.command_action = {"name": other_command}

            elif "Action" in other_command:  # for releasing attack after charging
                for this_subunit in self.alive_subunit_list:
                    if "uninterruptible" not in this_subunit.command_action:
                        this_subunit.command_action = {"name": other_command}
                        this_subunit.interrupt_animation = True
                        this_subunit.idle_action = {}

        self.command_state = self.state
