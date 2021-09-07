import pygame
import pygame.freetype


class Leader(pygame.sprite.Sprite):
    gamebattle = None
    gone_event_text = {96: "retreating", 97: "captured", 98: "missing", 99: "wounded", 100: "dead"}

    def __init__(self, leaderid, unit, leaderstat):
        self._layer = 15
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.player = False
        self.morale = 100
        stat = leaderstat.leader_list[leaderid]
        leader_header = leaderstat.leader_list_header
        self.leaderid = leaderid  # Different than game id, leaderid is only used as reference to the data
        self.name = stat[0]
        self.authority = stat[leader_header["Authority"]]
        self.meleecommand = stat[leader_header["Melee Command"]]
        self.rangecommand = stat[leader_header["Range Command"]]
        self.cavcommand = stat[leader_header["Cavalry Command"]]
        self.combat = stat[leader_header["Combat"]] * 2
        self.social = stat[leader_header["Social"]]
        self.description = stat[-1]

        # self.trait = stat
        # self.skill = stat
        self.state = 0  ## 0 = alive, 96 = retreated, 97 = captured, 98 = missing, 99 = wound, 100 = dead

        self.parentunit = unit
        # self.mana = stat

        try:  # Put leader image into leader slot
            self.fullimage = leaderstat.imgs[leaderstat.imgorder.index(leaderid)].copy()
        except:  # Use Unknown leader image if there is none in list)
            self.fullimage = leaderstat.imgs[-1].copy()
            font = pygame.font.SysFont("timesnewroman", 300)
            textimage = font.render(str(self.leaderid), True, pygame.Color("white"))
            textrect = textimage.get_rect(center=(self.fullimage.get_width() / 2, self.fullimage.get_height() / 1.3))
            self.fullimage.blit(textimage, textrect)

        self.image = pygame.transform.scale(self.fullimage, (50, 50))
        self.rect = self.image.get_rect(center=(250,250))
        self.image_original = self.image.copy()

        self.badmorale = (20, 30)  ## other position morale lost
        self.commander = False  # army commander
        self.originalcommander = False  # the first army commander at the start of battle

    def gone(self):
        """leader no longer in command due to death or other events"""
        thisbadmorale = self.badmorale[0]

        if self.state == 99:  # wounded inflict less morale penalty
            thisbadmorale = self.badmorale[1]

        for subunit in self.parentunit.subunit_sprite: # TODO maybe complete broken instead
            subunit.base_morale -= (thisbadmorale * subunit.mental)  # decrease all subunit morale when leader die depending on position
            subunit.moraleregen -= (0.3 * subunit.mental)  # all subunit morale regen slower per leader dead

        if self.commander:  # reduce morale to whole army if commander die from the dmg (leader die cal is in leader.py)
            self.gamebattle.textdrama.queue.append(str(self.name) + " is " + self.gone_event_text[self.state])
            eventmapid = "ld0"  # read ld0 event log for special log when team 1 commander die, not used for other leader
            whicharmy = self.gamebattle.team1unit
            if self.parentunit.team == 2:
                whicharmy = self.gamebattle.team2unit
                eventmapid = "ld1"  # read ld1 event log for special log when team 2 commander die, not used for other leader

            if self.originalcommander and self.state == 100:
                self.gamebattle.eventlog.addlog([0, "Commander " + str(self.name) + " is " + self.gone_event_text[self.state]], [0, 1, 2], eventmapid)
            else:
                self.gamebattle.eventlog.addlog([0, "Commander " + str(self.name) + " is " + self.gone_event_text[self.state]], [0, 1, 2])

            for army in whicharmy:
                for subunit in army.subunit_sprite:
                    subunit.base_morale -= (200 * subunit.mental)  # all subunit morale -100 when commander die
                    subunit.moraleregen -= (1 * subunit.mental)  # all subunit morale regen even slower per commander dead

        else:
            self.gamebattle.eventlog.addlog([0, str(self.name) + " is " + self.gone_event_text[self.state]], [0, 2])

        self.parentunit.commandbuff = [0, 0, 0]  # reset command buff to 0
        self.authority = 0
        self.meleecommand = 0
        self.rangecommand = 0
        self.cavcommand = 0
        self.combat = 0

        pygame.draw.line(self.image, (150, 20, 20), (5, 5), (45, 35), 5)  # draw dead cross on leader image
        self.gamebattle.setup_uniticon()

    def gamestart(self):
        row = int(self.subunitpos / 8)
        column = self.subunitpos - (row * 8)
        self.subunit = self.parentunit.subunit_sprite[self.subunitpos]  # setup subunit that leader belong
        self.subunit.leader = self  ## put in leader to subunit with the set pos
        self.parentunit.leadersubunit = self.subunit  # TODO add this to when change leader or gamestart leader move ot other subunit
        # self.parentunit.leadersubunit - self.parentunit.base_pos

        squadpenal = int(
            (self.subunitpos / len(self.parentunit.armysubunit[0])) * 10)  # Authority get reduced the further leader stay in the back line
        self.authority = self.authority - ((self.authority * squadpenal / 100) / 2)
        if self.parentunit.commander:
            self.commander = True
            self.originalcommander = True

    def update(self):
        if self.state not in (96, 97, 98, 99, 100):
            if self.health <= 0:  # health reach 0, die. may implement wound state chance later
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
