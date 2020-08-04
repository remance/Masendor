import random, os.path, glob, csv, math
import pygame
from pygame.transform import scale
import pygame.freetype
from RTS import maingame
import numpy as np

class arrow(pygame.sprite.Sprite):
    speed = 8
    images = []
    def __init__(self, shooter, range, maxrange):
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.arcshot = False
        if 16 in shooter.trait: self.arcshot = True
        self.image_original = self.image.copy()
        self.shooter = shooter
        self.accuracy = shooter.accuracy
        self.passwho = 0
        self.side = None
        # self.lastpasswho = 0
        randomposition1, randomposition2 = random.randint(0,1), random.randint(0,20)
        hitchance = round((100 - self.accuracy * random.randint(1,5)) / (maxrange / range))
        if randomposition1 == 0:
            self.target = pygame.Vector2(shooter.attackpos[0]-hitchance, shooter.attackpos[1]-hitchance)
        else:
            self.target = pygame.Vector2(shooter.attackpos[0]+hitchance, shooter.attackpos[1]+hitchance)
        myradians = math.atan2(self.target[1] - shooter.combatpos[1], self.target[0] - shooter.combatpos[0])
        self.angle = math.degrees(myradians)
        # """upper left -"""
        if self.angle >= -180 and self.angle <= -90:
            self.angle = -self.angle - 90
        # """upper right +"""
        elif self.angle > -90 and self.angle < 0:
            self.angle = (-self.angle) - 90
        # """lower right -"""
        elif self.angle >= 0 and self.angle <= 90:
            self.angle = -(self.angle + 90)
        # """lower left +"""
        elif self.angle > 90 and self.angle <= 180:
            self.angle = 270 - self.angle
        self.image = pygame.transform.rotate(self.image, self.angle)
        if randomposition1 == 0:
            self.rect = self.image.get_rect(midbottom=(shooter.combatpos[0]-randomposition2,shooter.combatpos[1]-randomposition2))
            self.pos = pygame.Vector2(shooter.combatpos[0]-randomposition2,shooter.combatpos[1]-randomposition2)
        else:
            self.rect = self.image.get_rect(midbottom=(shooter.combatpos[0]+randomposition2,shooter.combatpos[1]+randomposition2))
            self.pos = pygame.Vector2(shooter.combatpos[0]+randomposition2,shooter.combatpos[1]+randomposition2)
        self.mask = pygame.mask.from_surface(self.image)

    def rangedmgcal(self, who, target, targetside):
        """Calculate hitchance and defense chance"""
        if targetside == 2: targetside = 3
        elif targetside == 3: targetside = 2
        wholuck= random.randint(-20, 20)
        targetluck = random.randint(-20, 20)
        targetpercent = [1,0.7,0.4,0.7][targetside]
        whohit = float(self.accuracy) + wholuck
        if whohit < 0: whohit = 0
        targetdefense = float(target.rangedef * targetpercent) + targetluck
        if targetdefense < 0: targetdefense = 0
        whodmg, whomoraledmg = maingame.battle.losscal(maingame.battle, who=who, target=target, hit=whohit, defense=targetdefense, type='range')
        target.unithealth -= whodmg
        target.basemorale -= whomoraledmg

    def registerhit(self,who,target,squadlist,squadindexlist):
        """Calculatte damage when arrow reach target"""
        if self.arcshot == True:
            for unit in pygame.sprite.spritecollide(self, who, 0, collided=pygame.sprite.collide_mask):
                calsquadlist = np.where(unit.squadalive > 1, unit.armysquad, unit.squadalive).flat
                calsquadlist = np.delete(calsquadlist,
                                         (calsquadlist <= 1).nonzero()[0][:round((np.count_nonzero(calsquadlist <= 1)) * self.accuracy / 100)])
                squadhit = calsquadlist[random.randint(0, len(calsquadlist) - 1)]
                if squadhit not in [0, 1]:
                    squadhit = np.where(squadindexlist == squadhit)[0][0]
                    self.rangedmgcal(self.shooter, squadlist[squadhit], self.side)
            for unit in pygame.sprite.spritecollide(self, target, 0, collided=pygame.sprite.collide_mask):
                calsquadlist = np.where(unit.squadalive > 1, unit.armysquad, unit.squadalive).flat
                calsquadlist = np.delete(calsquadlist, (calsquadlist <= 1).nonzero()[0][:round(
                    (np.count_nonzero(calsquadlist <= 1)) * self.accuracy / 100)])
                squadhit = calsquadlist[random.randint(0, len(calsquadlist) - 1)]
                if squadhit not in [0, 1]:
                    squadhit = np.where(squadindexlist == squadhit)[0][0]
                    self.rangedmgcal(self.shooter, squadlist[squadhit], self.side)
        elif self.arcshot == False and self.passwho != 0:
            calsquadlist = self.passwho.frontline[self.side]
            calsquadlist = np.delete(calsquadlist, (calsquadlist == 0).nonzero()[0])
            calsquadlist = np.delete(calsquadlist, (calsquadlist <= 1).nonzero()[0][:round(
                (np.count_nonzero(calsquadlist <= 1)) * self.accuracy / 100)])
            squadhit = calsquadlist[random.randint(0, len(calsquadlist) - 1)]
            if squadhit not in [0, 1]:
                squadhit = np.where(squadindexlist == squadhit)[0][0]
                self.rangedmgcal(self.shooter, squadlist[squadhit], self.side)

    def update(self,who,target,hitbox,squadlist,squadindexlist,dt):
        """Who is the player battalion group, target is the enemy battalion group"""
        move = self.target - self.pos
        move_length = move.length()
        """Calculate which side arrow will hit when it pass unit"""
        for hitbox in pygame.sprite.spritecollide(self, hitbox, 0, collided=pygame.sprite.collide_mask):
            if hitbox.who.gameid != self.shooter.battalion.gameid:
                self.passwho = hitbox.who
                self.side = hitbox.side
                if self.arcshot == False:
                    print('id',self.passwho.gameid)
                    self.registerhit(who, target, squadlist, squadindexlist)
                    self.kill()
        if move_length >= self.speed:
            move.normalize_ip()
            move = move * self.speed * dt * 50
            self.pos += move
            self.rect.center = list(int(v) for v in self.pos)
            self.mask = pygame.mask.from_surface(self.image)
        elif move_length < self.speed:
            self.registerhit(who, target, squadlist, squadindexlist)
            self.kill()
