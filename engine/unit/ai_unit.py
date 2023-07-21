from operator import itemgetter

from engine.utility import rotation_xy


def ai_unit(self):
    self.near_enemy = sorted(
        {key.attacker: key.attacker.base_pos.distance_to(self.base_pos) for key in self.enemy_list}.items(),
        key=lambda item: item[1])  # sort the closest enemy, saved as hitbox in that list so need to get attacker
    self.near_ally = sorted({key: key.base_pos.distance_to(self.base_pos) for key in self.ally_list}.items(),
                            key=lambda item: item[1])  # sort the closest friend
    # self.near_visible_enemy = {key: value for key, value in self.near_enemy if self.sight > key.hidden + value}
    #
    # self.nearest_enemy = None
    # if self.near_visible_enemy:
    #     self.nearest_enemy = self.near_visible_enemy[0]
    self.nearest_enemy = self.near_enemy[0]
    self.nearest_ally = self.near_ally[0]

    if not self.is_leader:
        layer = int(self.base_pos[0] + (self.base_pos[1] * 10))
        if layer < 2:  # layer 1 is for hitbox
            layer = 2
        if self._layer != layer:
            self.battle.battle_camera.change_layer(self, layer)

    else:
        self.ai_issued_charge = False
        self.group_too_far = False
        self.army_too_far = False
        if self.move_speed:  # find new follow point based on formation for subordinate
            for unit in self.alive_troop_follower:
                if unit in self.troop_distance_list:
                    new_target = rotation_xy(self.base_pos, self.base_pos +
                                             self.troop_distance_list[unit], self.radians_angle)
                    self.troop_pos_list[unit][0] = new_target[0]
                    self.troop_pos_list[unit][1] = new_target[1]
            for leader in self.alive_leader_follower:
                if leader in self.group_distance_list:
                    new_target = rotation_xy(self.base_pos, self.base_pos +
                                             self.group_distance_list[leader], self.radians_angle)
                    self.group_pos_list[leader][0] = new_target[0]
                    self.group_pos_list[leader][1] = new_target[1]

    if self.is_group_leader and not self.player_control:  # run leader planning
        self.ai_leader()
