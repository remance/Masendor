import pygame
import pygame.freetype


class Leader(pygame.sprite.Sprite):
    battle = None

    def __init__(self, leader_id, position, army_position, unit, leader_stat):
        self._layer = 15
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.morale = 100
        stat = leader_stat.leader_list[leader_id]
        self.leader_id = leader_id  # Different from self id, leader_id is only used as reference to the data
        self.name = stat["Name"]
        self.health = stat["Health"]
        self.authority = stat["Authority"]
        self.melee_command = stat["Melee Command"]
        self.range_command = stat["Range Command"]
        self.cav_command = stat["Cavalry Command"]
        self.combat = stat["Combat"] * 2
        self.social = leader_stat.leader_class[stat["Social Class"]]
        self.description = stat["Description"]

        self.subunit_pos = position  # Squad position is the index of subunit in subunit sprite loop
        # self.trait = stat
        # self.skill = stat
        self.state = 0  ## 0 = alive, 96 = retreated, 97 = captured, 98 = missing, 99 = wound, 100 = dead

        if self.name == "None":  # None leader is considered dead by default, function the same way as dead one
            self.health = 0
            self.state = 100  ## no leader is same as dead so no need to update

        self.unit = unit
        # self.mana = stat
        self.army_position = army_position  # position in the unit (i.e. general (0) or sub-general (1, 2) or advisor (3))
        self.base_image_position = [(134, 185), (80, 235), (190, 235), (134, 283)]  # leader image position in command ui
        self.image_position = self.base_image_position[self.army_position]  # image position based on army_position

        try:  # Put leader image into leader slot
            image_name = str(leader_id) + ".png"
            self.full_image = leader_stat.images[image_name].copy()
        except:  # Use Unknown leader image if there is none in list
            self.full_image = leader_stat.images["9999999.png"].copy()
            font = pygame.font.SysFont("timesnewroman", 300)
            text_image = font.render(str(self.leader_id), True, pygame.Color("white"))
            text_rect = text_image.get_rect(center=(self.full_image.get_width() / 2, self.full_image.get_height() / 1.3))
            self.full_image.blit(text_image, text_rect)

        self.image = pygame.transform.scale(self.full_image, (50, 50))
        self.rect = self.image.get_rect(center=self.image_position)
        self.image_original = self.image.copy()

        self.bad_morale = (20, 30)  # other position morale lost
        self.commander = False  # army commander
        self.original_commander = False  # the first army commander at the start of battle

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
            leader.bad_morale = (30, 50)  # gamestart general morale lost for bad event

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
            if leader.army_position == 0:  # new gamestart general
                self.subunit.unit_leader = False
                if self.unit.commander:
                    leader.commander = True

                self.unit.leader_subunit = leader.subunit
                leader.subunit.unit_leader = True

            leader.image_position = leader.base_image_position[leader.army_position]
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
        self.battle.setup_unit_icon()
        self.unit.leader_change = True  # initiate leader change stat recalculation for unit

    def gamestart(self):
        row = int(self.subunit_pos / 8)
        column = self.subunit_pos - (row * 8)
        self.subunit = self.unit.subunit_sprite[self.subunit_pos]  # setup subunit that leader belong
        self.subunit.leader = self  # put in leader to subunit with the set pos
        if self.army_position == 0:  # unit leader
            self.unit.leader_subunit = self.subunit  # TODO add this to when change leader or gamestart leader move ot other subunit
            # self.unit.leader_subunit - self.unit.base_pos
            self.subunit.unit_leader = True

            squad_penal = int(
                (self.subunit_pos / len(self.unit.subunit_list[0])) * 10)  # Authority get reduced the further leader stay in the back line
            self.authority = self.authority - ((self.authority * squad_penal / 100) / 2)
            self.bad_morale = (30, 50)  # gamestart general morale lost when destroyed
            if self.unit.commander:
                self.commander = True
                self.original_commander = True

    def update(self):
        if self.state not in (96, 97, 98, 99, 100):
            if self.health <= 0:  # health reach 0, destroyed. may implement wound state chance later
                self.health = 0
                self.state = 100
                # if random.randint(0,1) == 1: self.state = 99 ## chance to become wound instead when hp reach 0
                self.gone()

    def delete(self, local=False):
        """delete reference when del is called"""
        if local:
            print(locals())
        else:
            del self.unit
