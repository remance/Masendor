from math import radians, cos, sin

from pygame import Vector2

retreat_angle = (radians(90), radians(270), radians(180), radians(0), radians(135),
                 radians(225), radians(45), radians(315))


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
        for this_subunit in self.enemy_list:
            clip = this_subunit.rect.clipline(base_target, self.pos)
            if clip:
                retreat_score[index] += 1

    self.command_target = retreat_target[retreat_score.index(min(retreat_score))]  # pick lowest score direction


def travel_to_map_border(pos, angle, map_size):
    """
    Find target at border of map based on angle
    :param pos: Starting pos
    :param angle: Angle in radians
    :param map_size: Size of map (width, height)
    :return: target pos on map border
    """
    dx = cos(angle)
    dy = sin(angle)

    if dx < 1.0e-16:  # left border
        y = (-pos[0]) * dy / dx + pos[1]

        if 0 <= y <= map_size[1]:
            return Vector2((0, y))

    if dx > 1.0e-16:  # right border
        y = (map_size[0] - pos[0]) * dy / dx + pos[1]
        if 0 <= y <= map_size[1]:
            return Vector2((map_size[0], y))

    if dy < 1.0e-16:  # top border
        x = (-pos[1]) * dx / dy + pos[0]
        if 0 <= x <= map_size[0]:
            return Vector2((x, 0))

    if dy > 1.0e-16:  # bottom border
        x = (map_size[1] - pos[1]) * dx / dy + pos[0]
        if 0 <= x <= map_size[0]:
            return Vector2((x, map_size[1]))
