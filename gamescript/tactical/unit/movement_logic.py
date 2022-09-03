def movement_logic(self):
    if self.state not in (0, 95) and self.front_pos.distance_to(
            self.command_target) < 2:  # reach destination and not in combat, use 2 for now as minimum (0 and 1 seem to cause unit to not stop properly sometimes)
        not_halt = False  # check if any subunit in combat
        for subunit in self.subunit_list:
            if subunit.state == 10:
                not_halt = True
            if subunit.unit_leader and subunit.state != 10:
                not_halt = False
                break
        if not_halt is False:
            self.retreat_start = False  # reset retreat
            self.revert = False  # reset revert order
            self.issue_order(self.base_target,
                             other_command="Stop")  # reset command base_target state will become 0 idle
