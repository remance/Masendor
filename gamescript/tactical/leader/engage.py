import pygame

from gamescript.common.ui import selector

setup_unit_icon = selector.setup_unit_icon

def pos_change_stat(self, leader):
    """Change stat that related to army position such as in leader dead event"""
    leader.bad_morale = (20, 30)  # sub general morale lost for bad event
    if leader.army_position == 0:  # if leader become unit commander
        try:
            squad_penal = int(
                (leader.subunit_pos / len(leader.unit.subunit_list[
                                              0])) * 10)  # recalculate authority penalty based on subunit position
        except:
            squad_penal = 0
        leader.authority = leader.authority - (
                (leader.authority * squad_penal / 100) / 2)  # recalculate total authority
        leader.bad_morale = (30, 50)  # start_set general morale lost for bad event

        if leader.unit.commander:  # become army commander
            which_army = leader.battle.team1_unit  # team1
            if leader.unit.team == 2:  # team2
                which_army = self.battle.team2_unit
            for army in which_army:
                army.team_commander = leader
                army.auth_recal()


def gone(self, event_text={96: "retreating", 97: "captured", 98: "missing", 99: "wounded", 100: "dead"}):
    """leader no longer in command due to death or other events"""
    if self.commander and self.unit.leader[3].state not in (96, 97, 98, 99, 100) and self.unit.leader[3].name != "None":
        # If commander destroyed will use strategist as next commander first
        self.unit.leader[0], self.unit.leader[3] = self.unit.leader[3], self.unit.leader[0]
    elif self.army_position + 1 != 4 and self.unit.leader[self.army_position + 1].state not in (96, 97, 98, 99, 100) and \
            self.unit.leader[self.army_position + 1].name != "None":
        self.unit.leader.append(self.unit.leader.pop(self.army_position))  # move leader to last of list when dead

    this_bad_morale = self.bad_morale[0]

    if self.state == 99:  # wounded inflict less morale penalty
        this_bad_morale = self.bad_morale[1]

    for subunit in self.unit.subunit_sprite:
        subunit.base_morale -= (this_bad_morale * subunit.mental)  # decrease all subunit morale when leader destroyed depending on position
        subunit.morale_regen -= (0.3 * subunit.mental)  # all subunit morale regen slower per leader dead

    if self.commander:  # reduce morale to whole army if commander destroyed from the melee_dmg (leader destroyed cal is in leader.py)
        self.battle.drama_text.queue.append(str(self.name) + " is " + event_text[self.state])
        event_map_id = "ld0"  # read ld0 event log for special log when team 1 commander destroyed, not used for other leader
        which_army = self.battle.team1_unit
        if self.unit.team == 2:
            which_army = self.battle.team2_unit
            event_map_id = "ld1"  # read ld1 event log for special log when team 2 commander destroyed, not used for other leader

        if self.original_commander and self.state == 100:
            self.battle.event_log.add_log([0, "Commander " + str(self.name) + " is " + event_text[self.state]], [0, 1, 2], event_map_id)
        else:
            self.battle.event_log.add_log([0, "Commander " + str(self.name) + " is " + event_text[self.state]], [0, 1, 2])

        for army in which_army:
            for subunit in army.subunit_sprite:
                subunit.base_morale -= (200 * subunit.mental)  # all subunit morale -100 when commander destroyed
                subunit.morale_regen -= (1 * subunit.mental)  # all subunit morale regen even slower per commander dead

    else:
        self.battle.event_log.add_log([0, str(self.name) + " is " + event_text[self.state]], [0, 2])

    # v change army position of all leader in that unit
    for index, leader in enumerate(self.unit.leader):
        leader.army_position = index  # change army position to new one
        if leader.army_position == 0:  # new start_set general
            self.subunit.unit_leader = False
            if self.unit.commander:
                leader.commander = True

            self.unit.leader_subunit = leader.subunit
            leader.subunit.unit_leader = True

        leader.image_position = leader.leader_pos[leader.army_position]
        leader.rect = leader.image.get_rect(center=leader.image_position)
        self.pos_change_stat(leader)
    # ^ End change position

    self.unit.command_buff = [(self.unit.leader[0].melee_command - 5) * 0.1, (self.unit.leader[0].range_command - 5) * 0.1,
                              (self.unit.leader[0].cav_command - 5) * 0.1]  # reset command buff to new leader
    self.authority = 0
    self.melee_command = 0
    self.range_command = 0
    self.cav_command = 0
    self.combat = 0

    pygame.draw.line(self.image, (150, 20, 20), (5, 5), (45, 35), 5)  # draw dead cross on leader image
    setup_unit_icon(self.battle.unit_selector, self.battle.unit_icon,
                    self.battle.team_unit_dict[self.battle.player_team_check], self.battle.unit_selector_scroll)
    self.unit.leader_change = True  # initiate leader change stat recalculation for unit
