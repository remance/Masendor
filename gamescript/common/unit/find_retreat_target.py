import math

from gamescript.common import utility

rotation_xy = utility.rotation_xy
travel_to_map_border = utility.travel_to_map_border

retreat_angle = (math.radians(90), math.radians(270), math.radians(180), math.radians(0), math.radians(135),
                 math.radians(225), math.radians(45), math.radians(315))


def find_retreat_target(self):
    if self.retreat_way is False:  # not yet start retreat or previous retreat way got blocked
        retreat_score = [0, 0, 0, 0, 0, 0, 0, 0]  # retreat to path with the fewest enemies then closest to border
        retreat_target = []

        map_distance_score = (self.map_corner[0] + self.map_corner[1]) / 2

        for index, angle in enumerate(retreat_angle):  # find retreat angle from 8 directions
            base_target = travel_to_map_border(self.base_pos, angle, self.map_corner)
            retreat_score[index] += (
                        self.base_pos.distance_to(base_target) / map_distance_score)  # keep distance score as decimal
            retreat_target.append(base_target)
            for this_subunit in self.battle.battle_subunit_list:
                if this_subunit.team != self.team:
                    clip = this_subunit.hitbox_rect.clipline(base_target, self.base_pos)
                    if clip:
                        retreat_score[index] += 1
        print(retreat_score)
        print(retreat_target)
        base_target = retreat_target[retreat_score.index(min(retreat_score))]  # pick lowest score direction
        self.retreat_command(base_target, self.state)

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
