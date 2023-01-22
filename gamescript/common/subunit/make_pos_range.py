def make_pos_range(self):
    """create range of sprite pos for pathfinding"""
    self.pos_range = (range(int(max(0, self.base_pos[0] - (self.hitbox_front_distance - 1))),
                            int(min(self.map_corner[0], self.base_pos[0] + self.hitbox_front_distance))),
                      range(int(max(0, self.base_pos[1] - (self.hitbox_front_distance - 1))),
                            int(min(self.map_corner[1], self.base_pos[1] + self.hitbox_front_distance))))
