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

    if not self.player_manual_control:
        layer = int(self.base_pos[0] + (self.base_pos[1] * 10))
        if layer < 2:
            layer = 2
        if self._layer != layer:
            self.battle.battle_camera.change_layer(self, layer)
