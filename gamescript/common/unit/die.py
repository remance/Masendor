from gamescript import unit

die_command_action = unit.die_command_action


def die(self, how):
    """Unit left battle, either dead or flee"""
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
        if self.leader:
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

        for group in (self.alive_troop_follower, self.alive_leader_follower):  # change follower in to new leader
            for this_unit in group:
                if self.leader:  # move subordinate to its higher leader
                    this_unit.leader = self.leader
                    if this_unit.is_leader:  # leader follower
                        self.leader.alive_leader_follower.append(this_unit)
                        self.leader.find_formation_size(leader=True)
                        self.leader.group_add_change = True
                    else:  # troop follower
                        this_unit.add_leader_buff()
                        self.leader.alive_troop_follower.append(this_unit)
                        self.leader.find_formation_size(troop=True)
                        self.leader.troop_add_change = True  # new leader require formation change

                else:  # no higher leader to move, assign None
                    this_unit.leader = None
                    this_unit.command_buff = 1
                    this_unit.leader_social_buff = 0
                    this_unit.authority = 0
                    if not this_unit.is_leader:  # troop become broken from no leader
                        this_unit.group_leader = None
                        if not this_unit.check_special_effect("Unbreakable"):  # broken if no unbreakable
                            this_unit.not_broken = False
                            this_unit.find_retreat_target()

        if not self.leader:  # is unit leader
            for leader in self.alive_leader_follower:  # reassign unit leader
                leader.group_leader = leader  # 2nd highest leader become its own unit leader
                leader.is_group_leader = True

            for this_unit in self.battle.all_team_unit[self.team]:  # get all follower in unit in battle
                if this_unit.group_leader is self:
                    while this_unit.group_leader.leader:  # get the highest new leader of the unit
                        this_unit.group_leader = this_unit.group_leader.leader

    else:  # troop die
        if self.leader:  # has leader
            self.leader.troop_dead_list[self.troop_id] += 1

    self.alive_troop_follower = []
    self.alive_leader_follower = []

    if self in self.battle.troop_ai_logic_queue:
        self.battle.troop_ai_logic_queue.remove(self)

    self.battle.all_team_unit[self.team].remove(self)
    for team in self.battle.all_team_enemy:
        if team != self.team:
            self.battle.all_team_enemy[team].remove(self)
    self.battle.active_unit_list.remove(self)

    if how == "dead":
        if self.is_leader:
            if self.leader is None:
                self.battle.drama_text.queue.append(str(self.name) + " is Dead")  # play drama text when unit leader die
            event_check = {value["Who"]: key for key, value in self.battle.event_log.map_event.items()}
            if self.troop_id in event_check:  # check if specific dead event for leader exist
                self.battle.event_log.add_log((0, self.battle.event_log.map_event[event_check[self.troop_id]]["Text"]))
            else:
                self.battle.event_log.add_log((0, str(self.name) + " is Dead."))  # add log to say this leader is dead

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

    if len([key for key, value in self.battle.all_team_unit.items() if len(value) > 0]) <= 1:
        self.battle.game_state = "end"
        self.battle.game_speed = 0

    if self.player_control:
        self.battle.camera_mode = "Free"  # camera become free when player unit die so can look over the battle
