import pygame
import pygame.freetype

class Leader(pygame.sprite.Sprite):

    def __init__(self, leaderid, squadposition, armyposition, battalion, leaderstat):
        self._layer = 10
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.morale = 100
        stat = leaderstat.leaderlist[leaderid]
        self.gameid = leaderid  # Different than unit game id, leadergameid is only used as reference to the id data
        self.name = stat[0]
        self.health = stat[1]
        self.authority = stat[2]
        self.meleecommand = stat[3]
        self.rangecommand = stat[4]
        self.cavcommand = stat[5]
        self.combat = stat[6]
        self.social = leaderstat.leaderclass[stat[7]]
        self.description = stat[-1]
        self.squadpos = squadposition  # Squad position is the index of squad in squad sprite loop
        # self.trait = stat
        # self.skill = stat
        self.state = 0  ## 0 = alive, 96 = retreated, 97 = captured, 98 = missing, 99 = wound, 100 = dead
        if self.name == "none": self.state = 100  ## no leader is same as dead so no need to update
        self.battalion = battalion
        # self.mana = stat
        self.gamestart = 0
        self.armyposition = armyposition
        self.baseimgposition = [(134, 185), (80, 235), (190, 235), (134, 283)]
        self.imgposition = self.baseimgposition[self.armyposition]
        ## put leader image into leader slot
        try:
            self.fullimage = leaderstat.imgs[leaderstat.imgorder.index(leaderid)].copy()
        except:  ## Use Unknown leader image if there is none in list
            self.fullimage = leaderstat.imgs[-1].copy()
        self.image = pygame.transform.scale(self.fullimage, (int(self.fullimage.get_width() / 2), int(self.fullimage.get_height() / 2)))
        self.rect = self.image.get_rect(center=self.imgposition)
        self.image_original = self.image.copy()
        self.badmorale = (20, 30)  ## other position morale lost
        self.commander = False
        if self.armyposition == 0:
            squadpenal = int((self.squadpos / len(self.battalion.armysquad[0])) * 10) # Authority get reduced the further leader stay in the back line
            self.authority = self.authority - ((self.authority * squadpenal / 100) / 2)
            self.badmorale = (30, 50)  ## main general morale lost when die
            if self.battalion.commander:
                self.commander = True

    def poschangestat(self, leader):
        """Change stat that related to army position such as in leader dead event"""
        leader.badmorale = (20, 30)  ## sub general morale lost for bad event
        if leader.armyposition == 0:
            squadpenal = int((leader.squadpos / len(leader.battalion.armysquad[0])) * 10)
            leader.authority = leader.authority - ((leader.authority * squadpenal / 100) / 2)
            leader.badmorale = (30, 50)  ## main general morale lost for bad event

    def update(self):
        if self.gamestart == 0:
            self.squad = self.battalion.squadsprite[self.squadpos]
            self.gamestart = 1
        if self.state not in (96, 97, 98, 99, 100):
            if self.health <= 0:
                self.state = 100
                # if random.randint(0,1) == 1: self.state = 99 ## chance to become wound instead when hp reach 0
                if self.battalion.leader[1].state not in (96, 97, 98, 99, 100) and self.battalion.leader[1].name != "None":
                    self.battalion.leader.append(self.battalion.leader.pop(self.armyposition))  ## move leader to last of list when dead
                for squad in self.battalion.squadsprite:
                    squad.basemorale -= self.badmorale[1]  ## decrease all squad morale when leader die depending on position
                for index, leader in enumerate(self.battalion.leader):  ## also change army position of all leader in that battalion
                    leader.armyposition = index  ## change army position to new one
                    if self.battalion.commander and leader.armyposition == 0:
                        self.commander = True
                    leader.imgposition = leader.baseimgposition[leader.armyposition]
                    leader.rect = leader.image.get_rect(center=leader.imgposition)
                    self.poschangestat(leader)
                self.battalion.commandbuff = [(self.battalion.leader[0].meleecommand - 5) * 0.1, (self.battalion.leader[0].rangecommand - 5) * 0.1,
                                              (self.battalion.leader[0].cavcommand - 5) * 0.1]
                self.authority = 0
                self.meleecommand = 0
                self.rangecommand = 0
                self.cavcommand = 0
                self.combat = 0
                self.social = 0
                pygame.draw.line(self.image, (150, 20, 20), (5, 5), (45, 35), 5)
                self.battalion.leaderchange = True
