def process_command(self, target_pos, run_command=False, revert_move=False, enemy=None, other_command=None):
    """Process input order into state and subunit base_target action
    other_command parameter 0 is default command, 1 is natural pause, 2 is order pause"""
    if other_command is None:  # move or melee_attack command
        self.state = 1

        # if self.attack_place or (enemy is not None and (self.team != enemy.team)):  # melee_attack
        #     if self.ammo <= 0 or self.forced_melee:  # no magazine_left to shoot or forced melee_attack command
        #         self.state = 3  # move to melee
        #     elif self.ammo > 0:  # have magazine_left to shoot
        #         self.state = 5  # Move to range melee_attack
        #         self.attack_target = enemy
        #         self.base_attack_pos = enemy.base_pos
        #         self.set_target(self.base_attack_pos)
        #
        # else:

        if run_command:
            self.state += 1  # run state

        self.command_state = self.state

        self.range_combat_check = False
        self.command_target = self.base_target
        if revert_move:  # revert subunit without rotate, cannot run in this state
            self.set_target(target_pos)
        else:  # rotate unit only
            self.new_angle = self.set_rotate(target_pos)
            self.set_subunit_target()
    elif type(other_command) == str and "Troop Skill" in other_command:
        for subunit in self.subunits:
            subunit.current_action = other_command