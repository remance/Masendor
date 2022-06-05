from gamescript.common import utility

rotation_xy = utility.rotation_xy


def make_front_pos(self):
    """create new pos for front side of sprite"""
    front_pos = (self.base_pos[0], (self.base_pos[1] - self.image_height))  # generate front side position
    front_pos = rotation_xy(self.base_pos, front_pos,
                            self.radians_angle)  # rotate the new front side according to sprite rotation

    return front_pos