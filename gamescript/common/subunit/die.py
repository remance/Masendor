from gamescript import subunit

die_command_action = subunit.die_command_action


def die(self, how):
    """Subunit left battle, either dead or flee"""
    self.last_health_state = 0
    self.skill_cooldown = {}  # remove all cooldown
    self.skill_effect = {}  # remove all skill effects

    self.battle.team_troop_number[self.team] -= 1
    if self.leader is not None:  # remove self from leader's subordinate list
        if self.is_leader:
            self.leader.alive_leader_follower.remove(self)
        else:
            self.leader.alive_troop_follower.remove(self)

    self.hitbox.who = None
    self.hitbox.kill()
    self.hitbox = None

    for group in (self.alive_troop_follower, self.alive_leader_follower):  # change subordinate in list
        for this_subunit in group:
            if self.leader is not None:  # move subordinate to its higher leader
                this_subunit.leader = self.leader
                if this_subunit.is_leader:
                    self.leader.alive_leader_follower.append(this_subunit)
                    self.leader.find_formation_size(leader=True)
                    self.leader.unit_add_change = True
                else:
                    this_subunit.add_leader_buff()
                    self.leader.alive_troop_follower.append(this_subunit)
                    self.leader.find_formation_size(troop=True)
                    self.leader.formation_add_change = True  # new leader require formation change
            else:  # no higher leader to move, assign None
                this_subunit.leader = None
                this_subunit.command_buff = 1
                this_subunit.leader_social_buff = 0
                this_subunit.authority = 0
                if this_subunit.is_leader is False:  # troop become broken from no leader
                    if this_subunit.check_special_effect("Unbreakable") is False:  # broken if no unbreakable
                        this_subunit.not_broken = False
                        this_subunit.find_retreat_target()

    self.alive_troop_follower = []
    self.alive_leader_follower = []

    self.battle.all_team_subunit[self.team].remove(self)
    self.battle.active_subunit_list.remove(self)

    if how == "dead":
        if self in self.battle.battle_camera:
            self.battle.battle_camera.change_layer(sprite=self, new_layer=1)

            self.current_action = die_command_action
            self.show_frame = 0
            self.animation_timer = 0
            self.pick_animation()
    elif how == "flee":
        if self in self.battle.battle_camera:
            self.battle.battle_camera.remove(self)

    if len([key for key, value in self.battle.all_team_subunit.items() if len(value) > 0]) <= 1:
        self.battle.game_state = "end"
        self.battle.game_speed = 0

    if self.is_leader:
        self.battle.event_log.add_log((0, str(self.name) + " is Dead."))  # add log to say this leader is destroyed

    if self.player_manual_control:
        self.battle.camera_mode = "Free"  # camera become free when player char die so can look over the battle
