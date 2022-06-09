def unit_ai(self):
    # Chase unit in base_target and rotate accordingly
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

    # Skirmishing logic where unit automatically move away from the closest enemy using its minimum attack range
    if self.hold == 1 and self.state not in (97, 98, 99):
        min_range = self.min_range  # run away from enemy that reach minimum range
        if min_range < 50:
            min_range = 50  # for in case min_range is 0 (melee troop only)
        target_list = list(self.near_target.values())
        if len(target_list) > 0 and target_list[0].distance_to(self.base_pos) <= min_range:  # if there is any enemy in minimum range
            self.state = 96  # retreating
            base_target = self.base_pos - ((list(self.near_target.values())[0] - self.base_pos) / 5)  # generate base_target to run away

            if base_target[0] < 1:  # can't run away when reach corner of map same for below if elif
                base_target[0] = 1
            elif base_target[0] > 999:
                base_target[0] = 999
            if base_target[1] < 1:
                base_target[1] = 1
            elif base_target[1] > 999:
                base_target[1] = 999

            self.process_command(base_target, True, True)  # set base_target position to run away
