import pygame


def change_follow_order(self, new_order, which):
    if which == "troop":
        self.troop_follow_order = new_order
        follower_list = self.alive_troop_follower
        follower_pos_list = self.troop_pos_list
    elif which == "unit":
        self.unit_follow_order = new_order
        follower_list = self.alive_leader_follower
        follower_pos_list = self.unit_pos_list

    if new_order == "Stay Here":  # assign current pos to current spot
        for who in follower_list:
            who.follow_target = pygame.Vector2(who.base_pos)

    else:  # find new pos from formation
        for who in follower_list:
            who.follow_target = follower_pos_list[who]
