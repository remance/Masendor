import pygame
import pygame.freetype

"""This file contains leader class entity that contain attribute and most function related to it"""

class Leader(pygame.sprite.Sprite):
    maingame = None

    def __init__(self, leaderid, position, armyposition, battalion, leaderstat):
        self._layer = 15
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.morale = 100
        stat = leaderstat.leaderlist[leaderid]
        self.gameid = leaderid  # Different than subunit game id, leadergameid is only used as reference to the id data
        self.name = stat[0]
        self.health = stat[1]
        self.authority = stat[2]
        self.meleecommand = stat[3]
        self.rangecommand = stat[4]
        self.cavcommand = stat[5]
        self.combat = stat[6] * 10
        self.social = leaderstat.leaderclass[stat[7]]
        self.description = stat[-1]

        self.subunitpos = position  # Squad position is the index of subunit in subunit sprite loop
        # self.trait = stat
        # self.skill = stat
        self.state = 0  ## 0 = alive, 96 = retreated, 97 = captured, 98 = missing, 99 = wound, 100 = dead

        if self.name == "None": # None leader is considered dead by default, function the same way as dead one
            self.health = 0
            self.state = 100  ## no leader is same as dead so no need to update

        self.parentunit = battalion
        # self.mana = stat
        self.gamestart = False
        self.armyposition = armyposition # position in the parentunit (e.g. general or sub-general)
        self.baseimgposition = [(134, 185), (80, 235), (190, 235), (134, 283)] # leader image position in command ui
        self.imgposition = self.baseimgposition[self.armyposition] # image position based on armyposition

        try:  # Put leader image into leader slot
            self.fullimage = leaderstat.imgs[leaderstat.imgorder.index(leaderid)].copy()
        except:  # Use Unknown leader image if there is none in list
            self.fullimage = leaderstat.imgs[-1].copy()

        self.image = pygame.transform.scale(self.fullimage, (50, 50))
        self.rect = self.image.get_rect(center=self.imgposition)
        self.image_original = self.image.copy()

        self.badmorale = (20, 30)  ## other position morale lost
        self.commander = False # army commander
        self.originalcommander = False # the first army commander at the start of battle

    def poschangestat(self, leader):
        """Change stat that related to army position such as in leader dead event"""
        leader.badmorale = (20, 30)  # sub general morale lost for bad event
        if leader.armyposition == 0: # if leader become parentunit commander
            squadpenal = int((leader.subunitpos / len(leader.parentunit.armysquad[0])) * 10) # recalculate authority penalty based on subunit position
            leader.authority = leader.authority - ((leader.authority * squadpenal / 100) / 2) # recalculate total authority
            leader.badmorale = (30, 50)  ## main general morale lost for bad event

            if leader.parentunit.commander: ## become army commander
                whicharmy = leader.maingame.team1army # team1
                if leader.parentunit.team == 2:  # team2
                    whicharmy = self.maingame.team2army
                for army in whicharmy:
                    army.teamcommander = leader
                    army.authrecal()

    def gone(self,eventtext = {96:"retreat",97:"captured",98:"missing",99:"wounded",100:"dead"}):
        """leader no longer in command due to death or other events"""
        if self.commander and self.parentunit.leader[3].state not in (96, 97, 98, 99, 100) and self.parentunit.leader[3].name != "None":
            ## If commander die will use strategist as next commander first
            self.parentunit.leader[0], self.parentunit.leader[3] = self.parentunit.leader[3], self.parentunit.leader[0]
        elif self.armyposition + 1 != 4 and self.parentunit.leader[self.armyposition + 1].state not in (96, 97, 98, 99, 100) and self.parentunit.leader[self.armyposition + 1].name != "None":
            self.parentunit.leader.append(self.parentunit.leader.pop(self.armyposition))  ## move leader to last of list when dead

        thisbadmorale = self.badmorale[0]

        if self.state == 99: # wounded inflict less morale penalty
            thisbadmorale = self.badmorale[1]

        for subunit in self.parentunit.subunitsprite:
            subunit.basemorale -= (thisbadmorale * subunit.mental)  # decrease all subunit morale when leader die depending on position
            subunit.moraleregen -= (0.3 * subunit.mental) # all subunit morale regen slower per leader dead

        if self.commander:  # reduce morale to whole army if commander die from the dmg (leader die cal is in gameleader.py)
            self.maingame.textdrama.queue.append(str(self.name) + " is " + eventtext[self.state])
            eventmapid = "ld0" # read ld0 event log for special log when team 1 commander die, not used for other leader
            whicharmy = self.maingame.team1army
            if self.parentunit.team == 2:
                whicharmy = self.maingame.team2army
                eventmapid = "ld1" # read ld1 event log for special log when team 2 commander die, not used for other leader

            if self.originalcommander and self.state == 100:
                self.maingame.eventlog.addlog([0, "Commander " + str(self.name) + " is " + eventtext[self.state]], [0, 1, 2], eventmapid)
            else: self.maingame.eventlog.addlog([0, "Commander " + str(self.name) + " is " + eventtext[self.state]], [0, 1, 2])

            for army in whicharmy:
                for subunit in army.subunitsprite:
                    subunit.basemorale -= (200 * subunit.mental) # all subunit morale -100 when commander die
                    subunit.moraleregen -= (1 * subunit.mental)  #  all subunit morale regen even slower per commander dead

        else:
            self.maingame.eventlog.addlog([0, str(self.name) + " is " + eventtext[self.state]], [0, 2])

        #v change army position of all leader in that parentunit
        for index, leader in enumerate(self.parentunit.leader):
            leader.armyposition = index  ## change army position to new one
            if self.parentunit.commander and leader.armyposition == 0:
                self.commander = True
            leader.imgposition = leader.baseimgposition[leader.armyposition]
            leader.rect = leader.image.get_rect(center=leader.imgposition)
            self.poschangestat(leader)
        #^ End change position

        self.parentunit.commandbuff = [(self.parentunit.leader[0].meleecommand - 5) * 0.1, (self.parentunit.leader[0].rangecommand - 5) * 0.1,
                                       (self.parentunit.leader[0].cavcommand - 5) * 0.1] # reset command buff to new leader
        self.authority = 0
        self.meleecommand = 0
        self.rangecommand = 0
        self.cavcommand = 0
        self.combat = 0
        self.social = 0

        pygame.draw.line(self.image, (150, 20, 20), (5, 5), (45, 35), 5) # draw dead cross on leader image
        self.maingame.setuparmyicon()
        self.parentunit.leaderchange = True # initiate leader change stat recalculation for parentunit

    def update(self):
        if self.gamestart == False:
            row = int(self.subunitpos/8)
            column = self.subunitpos - (row*8)
            self.subunit = self.parentunit.subunitsprite[self.subunitpos] # setup subunit that leader belong
            self.gamestart = True

            if self.armyposition == 0:  # parentunit leader
                squadpenal = int(
                    (self.subunitpos / len(self.parentunit.armysquad[0])) * 10)  # Authority get reduced the further leader stay in the back line
                self.authority = self.authority - ((self.authority * squadpenal / 100) / 2)
                self.badmorale = (30, 50)  ## main general morale lost when die
                if self.parentunit.commander:
                    self.commander = True
                    self.originalcommander = True

        if self.state not in (96, 97, 98, 99, 100):
            if self.health <= 0: # health reach 0, die. may implement wound state chance later
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

        
