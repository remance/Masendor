import math

from gamescript.common import utility

rotation_xy = utility.rotation_xy
travel_to_map_border = utility.travel_to_map_border

retreat_angle = (math.radians(90), math.radians(270), math.radians(180), math.radians(0), math.radians(135),
                 math.radians(225), math.radians(45), math.radians(315))


def find_retreat_target(self):
    self.retreat_start = True
    retreat_score = [0, 0, 0, 0, 0, 0, 0, 0]  # retreat to path with the fewest enemies then closest to border
    retreat_target = []

    map_distance_score = (self.map_corner[0] + self.map_corner[1]) / 2

    for index, angle in enumerate(retreat_angle):  # find retreat angle from 8 directions
        base_target = travel_to_map_border(self.base_pos, angle, self.map_corner)
        retreat_score[index] += (
                    self.base_pos.distance_to(base_target) / map_distance_score)  # keep distance score as decimal
        retreat_target.append(base_target)
        for this_subunit in self.battle.active_subunit_list:
            if this_subunit.team != self.team:
                clip = this_subunit.rect.clipline(base_target, self.base_pos)
                if clip:
                    retreat_score[index] += 1

    self.command_target = retreat_target[retreat_score.index(min(retreat_score))]  # pick lowest score direction
