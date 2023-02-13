def troop_ai_logic(self):
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

    self.taking_damage_angle = None

    if self.player_manual_control is False:
        if self.not_broken:
            self.combat_ai_logic()
            self.move_ai_logic()
        else:
            self.retreat_ai_logic()
