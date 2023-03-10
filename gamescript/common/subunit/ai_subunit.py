from gamescript.common import utility

rotation_xy = utility.rotation_xy


def ai_subunit(self):
    nearest_enemy = {key: key.base_pos.distance_to(self.base_pos) for team in
                     self.battle.all_team_subunit for key in self.battle.all_team_subunit[team] if team != self.team}
    nearest_friend = {key: key.base_pos.distance_to(self.base_pos) for key in
                      self.battle.all_team_subunit[self.team]}
    self.near_enemy = sorted(nearest_enemy.items(),
                             key=lambda item: item[1])  # sort the closest enemy
    self.near_ally = sorted(nearest_friend.items(),
                            key=lambda item: item[1])  # sort the closest friend

    self.nearest_enemy = self.near_enemy[0]
    self.nearest_ally = self.near_ally[0]

    if not self.player_control:
        layer = int(self.base_pos[0] + (self.base_pos[1] * 10))
        if layer < 2:
            layer = 2
        if self._layer != layer:
            self.battle.battle_camera.change_layer(self, layer)

    if self.is_leader and self.move_speed:  # find new follow point for subordinate
        for subunit in self.alive_troop_follower:
            new_target = rotation_xy(self.base_pos, self.base_pos +
                                     self.troop_distance_list[subunit], self.radians_angle)
            self.troop_pos_list[subunit][0] = new_target[0]
            self.troop_pos_list[subunit][1] = new_target[1]
        for leader in self.alive_leader_follower:
            new_target = rotation_xy(self.base_pos, self.base_pos +
                                     self.unit_distance_list[leader], self.radians_angle)
            self.unit_pos_list[leader][0] = new_target[0]
            self.unit_pos_list[leader][1] = new_target[1]

    if self.is_unit_leader:  # run leader planning
        self.ai_leader()
