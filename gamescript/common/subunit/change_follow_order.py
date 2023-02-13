import pygame


def change_follow_order(self, new_order):
    self.follow_order = new_order
    if self.follow_order == "Stay Here":
        for subunit in self.alive_troop_subordinate:
            subunit.follow_target = pygame.Vector2(subunit.base_pos)

    else:  # find new pos from formation
        for subunit in self.alive_troop_subordinate:
            subunit.follow_target = self.formation_pos_list[subunit]
