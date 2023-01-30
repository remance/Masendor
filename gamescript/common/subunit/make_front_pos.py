from gamescript.common import utility

rotation_xy = utility.rotation_xy


def make_front_pos(self):
    """create new pos for front side of sprite"""
    front_pos = (self.base_pos[0], (self.base_pos[1] - self.hitbox_front_distance))  # generate front side position
    self.front_pos = rotation_xy(self.base_pos, front_pos,
                                 self.radians_angle)  # rotate the new front side according to sprite rotation
    self.front_height = self.height_map.get_height(self.front_pos)
