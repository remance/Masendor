from math import cos, sin, atan2, degrees

from pygame import Vector2


def rotation_xy(origin, point, angle):
    """
    Rotate point to the new pos
    :param origin: origin pos
    :param point: target point pos
    :param angle: angle of rotation in radians
    :return: Rotated point pos
    """
    ox, oy = origin
    px, py = point
    x = ox + cos(angle) * (px - ox) - sin(angle) * (py - oy)
    y = oy + sin(angle) * (px - ox) + cos(angle) * (py - oy)
    return Vector2(x, y)


def set_rotate(self, base_target, convert=True, use_pos=False):
    """
    find angle using starting pos and base_target
    :param self: any object with base_pos or pos as position attribute
    :param base_target: pos for target position to rotate to
    :param convert: convert degree for rotation
    :param use_pos: use pos instead of base_pos
    :return: new angle
    """
    if not use_pos:
        my_radians = atan2(base_target[1] - self.base_pos[1], base_target[0] - self.base_pos[0])
    else:
        my_radians = atan2(base_target[1] - self.pos[1], base_target[0] - self.pos[0])
    new_angle = int(degrees(my_radians))
    if convert:
        # """upper left and upper right"""
        if -180 <= new_angle < 0:
            new_angle = -new_angle - 90

        # """lower right -"""
        elif 0 <= new_angle <= 90:
            new_angle = -(new_angle + 90)

        # """lower left +"""
        elif 90 < new_angle <= 180:
            new_angle = 270 - new_angle
    return new_angle


def convert_degree_to_360(angle):
    """Convert math.degrees to 360 degree with 0 at the top"""
    return 360 - (angle % 360)
