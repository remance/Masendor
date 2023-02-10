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
            self.leader.alive_leader_subordinate.remove(self)
        else:
            self.leader.alive_troop_subordinate.remove(self)
            self.leader.find_formation_size()
            self.leader.dead_change = True  # leader require formation change

    if self.sprite_indicator is not None:
        self.sprite_indicator.who = None
        self.sprite_indicator.kill()
        self.sprite_indicator = None

    if len(self.alive_troop_subordinate) > 0:
        for group in (self.alive_troop_subordinate, self.alive_leader_subordinate):
            for this_subunit in group:
                if self.leader is not None:  # move subordinate to its higher leader
                    this_subunit.leader = self.leader
                    if this_subunit.is_leader:
                        self.leader.alive_leader_subordinate.append(self)
                    else:
                        this_subunit.command_buff = this_subunit.leader.leader_command_buff[this_subunit.subunit_type] * 100
                        this_subunit.leader.alive_troop_subordinate.append(self)
                        this_subunit.leader.find_formation_size()
                        this_subunit.leader.dead_change = True  # new leader require formation change
                else:  # no higher leader to move, assign None
                    this_subunit.leader = None
                    this_subunit.command_buff = 0
                    self.leader_social_buff = 0
                    if this_subunit.is_leader is False:
                        if this_subunit.check_special_effect("Unbreakable") is False:  # broken from no leader
                            subunit.broken = True
                            subunit.retreat_start = True

    self.alive_troop_subordinate = []
    self.alive_leader_subordinate = []

    self.battle.all_team_subunit["alive"].remove(self)
    self.battle.all_team_subunit[self.team].remove(self)

    if how == "dead":
        if self in self.battle.battle_camera:
            self.battle.battle_camera.change_layer(sprite=self, new_layer=1)

            self.command_action = die_command_action
            self.top_interrupt_animation = True
            self.current_action = self.command_action  # replace any current action
            self.pick_animation()

    self.battle.event_log.add_log((0, str(self.name)
                                   + "'s unit is destroyed"))  # add log to say this leader is destroyed

    if self in self.battle.active_subunit_list:
        self.battle.subunit_pos_list.pop(self.battle.active_subunit_list.index(self))
        self.battle.active_subunit_list.remove(self)

    if self.player_manual_control:
        self.battle.camera_mode = "Free"  # camera become free when player char die so can look over the battle
