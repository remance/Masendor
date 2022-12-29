import math
import random


def find_random_direction(self):
    """Find random target direction for the sprite to move to"""
    random_angle = math.radians(random.randint(0, 359))
    target_now = (self.base_pos[0] + 1000) * math.cos(random_angle), \
                 (self.base_pos[1] + 1000) * math.sin(random_angle)
    return target_now
