
def skirmish(self):
    """Skirmishing logic where unit automatically move away from the closest enemy using its minimum attack range"""
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
