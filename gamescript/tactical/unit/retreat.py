from gamescript.common import utility

rotation_xy = utility.rotation_xy


def retreat(self):
    if self.retreat_way is None:  # not yet start retreat or previous retreat way got blocked
        retreat_side = (
            sum(subunit.enemy_front != [] or subunit.enemy_side != [] for subunit in self.frontline_object[0] if
                subunit is not None) + 2,
            sum(subunit.enemy_front != [] or subunit.enemy_side != [] for subunit in self.frontline_object[1] if
                subunit is not None) + 1,
            sum(subunit.enemy_front != [] or subunit.enemy_side != [] for subunit in self.frontline_object[2] if
                subunit is not None) + 1,
            sum(subunit.enemy_front != [] or subunit.enemy_side != [] for subunit in self.frontline_object[3] if
                subunit is not None))

        this_index = retreat_side.index(
            min(retreat_side))  # find side with least subunit fighting to retreat, rear always prioritised
        if this_index == 0:  # front
            self.retreat_way = (self.base_pos[0], (self.base_pos[1] - self.base_height_box))  # find position to retreat
        elif this_index == 1:  # left
            self.retreat_way = (self.base_pos[0] - self.base_width_box, self.base_pos[1])  # find position to retreat
        elif this_index == 2:  # right
            self.retreat_way = (self.base_pos[0] + self.base_width_box, self.base_pos[1])  # find position to retreat
        else:  # rear
            self.retreat_way = (
            self.base_pos[0], (self.base_pos[1] + self.base_height_box))  # find rear position to retreat
        self.retreat_way = [rotation_xy(self.base_pos, self.retreat_way, self.radians_angle), this_index]
        base_target = self.base_pos + ((self.retreat_way[0] - self.base_pos) * 1000)

        self.process_retreat(base_target)
        # if random.randint(0, 100) > 99:  # change side via surrender or betrayal
        #     if self.team == 1:
        #         self.battle.allunitindex = self.switchfaction(self.battle.team1_unit, self.battle.team2_unit,
        #                                                         self.battle.team1_pos_list, self.battle.allunitindex,
        #                                                         self.battle.enactment)
        #     else:
        #         self.battle.allunitindex = self.switchfaction(self.battle.team2_unit, self.battle.team1_unit,
        #                                                         self.battle.team2_pos_list, self.battle.allunitindex,
        #                                                         self.battle.enactment)
        #     self.battle.event_log.addlog([0, str(self.leader[0].name) + "'s unit surrender"], [0, 1])
        #     self.battle.setuparmyicon()
