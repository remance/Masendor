from gamescript import subunit

die_command_action = subunit.die_command_action


def die(self, how):
    """Subunit left battle, either dead or flee"""
    self.charging = False
    self.skill_cooldown = {}  # remove all cooldown
    self.skill_effect = {}  # remove all skill effects

    self.battle.team_troop_number[self.team] -= 1
    if self.leader:  # remove self from leader's subordinate list
        if self.is_leader:
            self.leader.alive_leader_follower.remove(self)
        else:
            self.leader.alive_troop_follower.remove(self)

    self.hitbox.who = None
    self.hitbox.kill()
    self.hitbox = None
    self.effectbox.who = None
    self.effectbox.kill()
    self.effectbox = None

    self.current_effect = None

    if self.is_leader:  # leader die
        for group in (self.alive_troop_follower, self.alive_leader_follower):  # change follower in to new leader
            for this_subunit in group:
                if self.leader:  # move subordinate to its higher leader
                    this_subunit.leader = self.leader
                    if this_subunit.is_leader:  # leader follower
                        self.leader.alive_leader_follower.append(this_subunit)
                        self.leader.find_formation_size(leader=True)
                        self.leader.unit_add_change = True
                    else:  # troop follower
                        this_subunit.add_leader_buff()
                        self.leader.alive_troop_follower.append(this_subunit)
                        self.leader.find_formation_size(troop=True)
                        self.leader.formation_add_change = True  # new leader require formation change

                    for index in self.troop_reserve_list:
                        if index in self.leader.troop_reserve_list:
                            self.leader.troop_reserve_list[index] += self.troop_reserve_list[index]
                        else:
                            self.leader.troop_reserve_list[index] = self.troop_reserve_list[index]

                    for index in self.troop_dead_list:
                        if index in self.leader.troop_dead_list:
                            self.leader.troop_dead_list[index] += self.troop_dead_list[index]
                        else:
                            self.leader.troop_dead_list[index] = self.troop_dead_list[index]

                else:  # no higher leader to move, assign None
                    this_subunit.leader = None
                    this_subunit.command_buff = 1
                    this_subunit.leader_social_buff = 0
                    this_subunit.authority = 0
                    if not this_subunit.is_leader:  # troop become broken from no leader
                        this_subunit.unit_leader = None
                        if not this_subunit.check_special_effect("Unbreakable"):  # broken if no unbreakable
                            this_subunit.not_broken = False
                            this_subunit.find_retreat_target()

        if not self.leader:  # is unit leader
            for leader in self.alive_leader_follower:  # reassign unit leader
                leader.unit_leader = leader  # 2nd highest leader become its own unit leader
                leader.is_unit_leader = True

            for this_subunit in self.battle.all_team_subunit[self.team]:  # get all follower in unit in battle
                if this_subunit.unit_leader is self:
                    while this_subunit.unit_leader.leader:  # get the highest new leader of the unit
                        this_subunit.unit_leader = this_subunit.unit_leader.leader

    else:  # troop die
        if self.leader:  # has leader
            self.leader.troop_dead_list[self.troop_id] += 1

    self.alive_troop_follower = []
    self.alive_leader_follower = []

    self.battle.all_team_subunit[self.team].remove(self)
    self.battle.active_subunit_list.remove(self)

    if how == "dead":
        if self.is_leader and self.leader is None:
            self.battle.drama_text.queue.append(str(self.name) + " is Dead")  # play drama text when unit leader die

        if self in self.battle.battle_camera:
            self.current_action = die_command_action
            self.show_frame = 0
            self.frame_timer = 0
            self.pick_animation()
            self.battle.death_troop_number[self.team] += 1
    elif how == "flee":
        if self in self.battle.battle_camera:
            self.battle.battle_camera.remove(self)
            self.battle.flee_troop_number[self.team] += 1

    if len([key for key, value in self.battle.all_team_subunit.items() if len(value) > 0]) <= 1:
        self.battle.game_state = "end"
        self.battle.game_speed = 0

    if self.is_leader:
        self.battle.event_log.add_log((0, str(self.name) + " is Dead."))  # add log to say this leader is dead

    if self.player_control:
        self.battle.camera_mode = "Free"  # camera become free when player char die so can look over the battle
