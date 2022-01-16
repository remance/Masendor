import pygame
import pygame.freetype


class Leader(pygame.sprite.Sprite):
    gamebattle = None

    def __init__(self, leaderid, position, armyposition, unit, leaderstat):
        self._layer = 15
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.morale = 100
        stat = leaderstat.leader_list[leaderid]
        leader_header = leaderstat.leader_list_header
        self.leaderid = leaderid  # Different than self id, leaderid is only used as reference to the data
        self.name = stat[0]
        self.health = stat[leader_header["Health"]]
        self.authority = stat[leader_header["Authority"]]
        self.meleecommand = stat[leader_header["Melee Command"]]
        self.rangecommand = stat[leader_header["Range Command"]]
        self.cavcommand = stat[leader_header["Cavalry Command"]]
        self.combat = stat[leader_header["Combat"]] * 2
        self.social = leaderstat.leader_class[stat[leader_header["Social Class"]]]
        self.description = stat[-1]
        self.description = stat[-1]

        self.subunitpos = position  # Squad position is the index of subunit in subunit sprite loop
        # self.trait = stat
        # self.skill = stat
        self.state = 0  ## 0 = alive, 96 = retreated, 97 = captured, 98 = missing, 99 = wound, 100 = dead

        if self.name == "None":  # None leader is considered dead by default, function the same way as dead one
            self.health = 0
            self.state = 100  ## no leader is same as dead so no need to update

        self.parentunit = unit
        # self.mana = stat
        self.armyposition = armyposition  # position in the unit (i.e. general (0) or sub-general (1, 2) or advisor (3))
        self.baseimgposition = [(134, 185), (80, 235), (190, 235), (134, 283)]  # leader image position in command ui
        self.imgposition = self.baseimgposition[self.armyposition]  # image position based on armyposition

        try:  # Put leader image into leader slot
            image_name = str(leaderid) +".png"
            self.fullimage = leaderstat.images[image_name].copy()
        except:  # Use Unknown leader image if there is none in list)
            self.fullimage = leaderstat.images["9999999.png"].copy()
            font = pygame.font.SysFont("timesnewroman", 300)
            textimage = font.render(str(self.leaderid), True, pygame.Color("white"))
            textrect = textimage.get_rect(center=(self.fullimage.get_width() / 2, self.fullimage.get_height() / 1.3))
            self.fullimage.blit(textimage, textrect)

        self.image = pygame.transform.scale(self.fullimage, (50, 50))
        self.rect = self.image.get_rect(center=self.imgposition)
        self.image_original = self.image.copy()

        self.badmorale = (20, 30)  ## other position morale lost
        self.commander = False  # army commander
        self.originalcommander = False  # the first army commander at the start of battle

    def poschangestat(self, leader):
        """Change stat that related to army position such as in leader dead event"""
        leader.badmorale = (20, 30)  # sub general morale lost for bad event
        if leader.army_position == 0:  # if leader become unit commander
            try:
                squadpenal = int(
                    (leader.subunit_pos / len(leader.unit.subunit_list[
                                                  0])) * 10)  # recalculate authority penalty based on subunit position
            except:
                squadpenal = 0
            leader.authority = leader.authority - (
                        (leader.authority * squadpenal / 100) / 2)  # recalculate total authority
            leader.badmorale = (30, 50)  ## gamestart general morale lost for bad event

            if leader.unit.commander:  ## become army commander
                whicharmy = leader.battle.team1_unit  # team1
                if leader.unit.team == 2:  # team2
                    whicharmy = self.gamebattle.team2_unit
                for army in whicharmy:
                    army.team_commander = leader
                    army.auth_recal()

    def gone(self, eventtext={96: "retreating", 97: "captured", 98: "missing", 99: "wounded", 100: "dead"}):
        """leader no longer in command due to death or other events"""
        if self.commander and self.parentunit.leader[3].state not in (96, 97, 98, 99, 100) and self.parentunit.leader[3].name != "None":
            # If commander destroyed will use strategist as next commander first
            self.parentunit.leader[0], self.parentunit.leader[3] = self.parentunit.leader[3], self.parentunit.leader[0]
        elif self.armyposition + 1 != 4 and self.parentunit.leader[self.armyposition + 1].state not in (96, 97, 98, 99, 100) and \
                self.parentunit.leader[self.armyposition + 1].name != "None":
            self.parentunit.leader.append(self.parentunit.leader.pop(self.armyposition))  ## move leader to last of list when dead

        thisbadmorale = self.badmorale[0]

        if self.state == 99:  # wounded inflict less morale penalty
            thisbadmorale = self.badmorale[1]

        for subunit in self.parentunit.subunit_sprite:
            subunit.base_morale -= (thisbadmorale * subunit.mental)  # decrease all subunit morale when leader destroyed depending on position
            subunit.morale_regen -= (0.3 * subunit.mental)  # all subunit morale regen slower per leader dead

        if self.commander:  # reduce morale to whole army if commander destroyed from the melee_dmg (leader destroyed cal is in leader.py)
            self.gamebattle.drama_text.queue.append(str(self.name) + " is " + eventtext[self.state])
            eventmapid = "ld0"  # read ld0 event log for special log when team 1 commander destroyed, not used for other leader
            whicharmy = self.gamebattle.team1_unit
            if self.parentunit.team == 2:
                whicharmy = self.gamebattle.team2_unit
                eventmapid = "ld1"  # read ld1 event log for special log when team 2 commander destroyed, not used for other leader

            if self.originalcommander and self.state == 100:
                self.gamebattle.event_log.add_log([0, "Commander " + str(self.name) + " is " + eventtext[self.state]], [0, 1, 2], eventmapid)
            else:
                self.gamebattle.event_log.add_log([0, "Commander " + str(self.name) + " is " + eventtext[self.state]], [0, 1, 2])

            for army in whicharmy:
                for subunit in army.subunit_sprite:
                    subunit.base_morale -= (200 * subunit.mental)  # all subunit morale -100 when commander destroyed
                    subunit.morale_regen -= (1 * subunit.mental)  # all subunit morale regen even slower per commander dead

        else:
            self.gamebattle.event_log.add_log([0, str(self.name) + " is " + eventtext[self.state]], [0, 2])

        # v change army position of all leader in that unit
        for index, leader in enumerate(self.parentunit.leader):
            leader.army_position = index  ## change army position to new one
            if leader.army_position == 0:  # new gamestart general
                self.subunit.unit_leader = False
                if self.parentunit.commander:
                    leader.commander = True

                self.parentunit.leader_subunit = leader.subunit
                leader.subunit.unit_leader = True

            leader.img_position = leader.base_img_position[leader.army_position]
            leader.rect = leader.image.get_rect(center=leader.img_position)
            self.poschangestat(leader)
        # ^ End change position

        self.parentunit.commandbuff = [(self.parentunit.leader[0].meleecommand - 5) * 0.1, (self.parentunit.leader[0].rangecommand - 5) * 0.1,
                                       (self.parentunit.leader[0].cavcommand - 5) * 0.1]  # reset command buff to new leader
        self.authority = 0
        self.meleecommand = 0
        self.rangecommand = 0
        self.cavcommand = 0
        self.combat = 0

        pygame.draw.line(self.image, (150, 20, 20), (5, 5), (45, 35), 5)  # draw dead cross on leader image
        self.gamebattle.setup_unit_icon()
        self.parentunit.leader_change = True  # initiate leader change stat recalculation for unit

    def gamestart(self):
        row = int(self.subunitpos / 8)
        column = self.subunitpos - (row * 8)
        self.subunit = self.parentunit.subunit_sprite[self.subunitpos]  # setup subunit that leader belong
        self.subunit.leader = self  ## put in leader to subunit with the set pos
        if self.armyposition == 0:  # unit leader
            self.parentunit.leader_subunit = self.subunit  # TODO add this to when change leader or gamestart leader move ot other subunit
            # self.unit.leader_subunit - self.unit.base_pos
            self.subunit.unit_leader = True

            squadpenal = int(
                (self.subunitpos / len(self.parentunit.subunit_list[0])) * 10)  # Authority get reduced the further leader stay in the back line
            self.authority = self.authority - ((self.authority * squadpenal / 100) / 2)
            self.badmorale = (30, 50)  ## gamestart general morale lost when destroyed
            if self.parentunit.commander:
                self.commander = True
                self.originalcommander = True

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
            del self.parentunit
