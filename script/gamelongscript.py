import numpy as np
import pygame
import pygame.freetype

from RTS import mainmenu
from RTS.script import gamebattalion

config = mainmenu.config
SoundVolume = mainmenu.SoundVolume
SCREENRECT = mainmenu.SCREENRECT
main_dir = mainmenu.main_dir


def die(battle, who, group, enemygroup):
    """remove battalion,hitbox when it dies"""
    battle.deadindex += 1
    if who.commander:  ## more morale penalty if the battalion is a command battalion
        for army in group:
            for squad in army.squadsprite:
                squad.basemorale -= 30
    for hitbox in who.hitbox:
        battle.allcamera.remove(hitbox)
        battle.hitboxs.remove(hitbox)
        hitbox.kill()
    battle.allunitlist.remove(who)
    battle.allunitindex.remove(who.gameid)
    group.remove(who)
    battle.deadunit.add(who)
    battle.allcamera.change_layer(sprite=who, new_layer=1)
    who.gotkilled = 1
    for thisarmy in enemygroup:  ## get bonus authority to the another army
        thisarmy.authority += 5
    for thisarmy in group:  ## morale dmg to every squad in army when allied battalion destroyed
        for squad in thisarmy.squadsprite:
            squad.basemorale -= 20

def splitunit(battle, who, how, gameleader):
    """split battalion either by row or column into two seperate battalion"""
    if how == 0:  ## split by row
        newarmysquad = np.array_split(who.armysquad, 2)[1]
        who.armysquad = np.array_split(who.armysquad, 2)[0]
        who.squadalive = np.array_split(who.squadalive, 2)[0]
        newpos = who.allsidepos[3] - ((who.allsidepos[3] - who.basepos) / 2)
        who.basepos = who.allsidepos[0] - ((who.allsidepos[0] - who.basepos) / 2)
    else:  ## split by column
        newarmysquad = np.array_split(who.armysquad, 2, axis=1)[1]
        who.armysquad = np.array_split(who.armysquad, 2, axis=1)[0]
        who.squadalive = np.array_split(who.squadalive, 2, axis=1)[0]
        newpos = who.allsidepos[2] - ((who.allsidepos[2] - who.basepos) / 2)
        who.basepos = who.allsidepos[1] - ((who.allsidepos[1] - who.basepos) / 2)
    if who.leader[1].squad.gameid not in newarmysquad:  ## move leader if squad not in new one
        if who.leader[1].squad.unittype in (1, 3, 5, 6, 7, 10, 11):  ## if squad type melee move to front
            leaderreplace = [np.where(who.armysquad == who.leader[1].squad.gameid)[0][0],
                             np.where(who.armysquad == who.leader[1].squad.gameid)[1][0]]
            leaderreplaceflat = np.where(who.armysquad.flat == who.leader[1].squad.gameid)[0]
            who.armysquad[leaderreplace[0]][leaderreplace[1]] = newarmysquad[0][int(len(newarmysquad[0]) / 2)]
            newarmysquad[0][int(len(newarmysquad[0]) / 2)] = who.leader[1].squad.gameid
        else:  ## if not move to center of battalion
            leaderreplace = [np.where(who.armysquad == who.leader[1].squad.gameid)[0][0],
                             np.where(who.armysquad == who.leader[1].squad.gameid)[1][0]]
            leaderreplaceflat = np.where(who.armysquad.flat == who.leader[1].squad.gameid)[0]
            who.armysquad[leaderreplace[0]][leaderreplace[1]] = newarmysquad[int(len(newarmysquad) / 2)][int(len(newarmysquad[0]) / 2)]
            newarmysquad[int(len(newarmysquad) / 2)][int(len(newarmysquad[0]) / 2)] = who.leader[1].squad.gameid
        who.squadalive[leaderreplace[0]][leaderreplace[1]] = \
            [0 if who.armysquad[leaderreplace[0]][leaderreplace[1]] == 0 else 1 if who.squadsprite[leaderreplaceflat[0]].state == 100 else 2][0]
    squadsprite = [squad for squad in who.squadsprite if squad.gameid in newarmysquad]  ## list of sprite not sorted yet
    newsquadsprite = []
    for squadindex in newarmysquad.flat:  ## sort so the new leader squad position match what set before
        for squad in squadsprite:
            if squad.gameid == squadindex:
                newsquadsprite.append(squad)
                break
    who.squadsprite = [squad for squad in who.squadsprite if squad.gameid in who.armysquad]
    for thissprite in (who.squadsprite, newsquadsprite):  ## reset position in inspectui for both battalion
        width, height = 0, 0
        squadnum = 0
        for squad in thissprite:
            width += battle.imagewidth
            if squadnum >= len(who.armysquad[0]):
                width = 0
                width += battle.imagewidth
                height += battle.imageheight
                squadnum = 0
            squad.inspposition = (width + battle.inspectuipos[0], height + battle.inspectuipos[1])
            squad.rect = squad.image.get_rect(topleft=squad.inspposition)
            squad.pos = pygame.Vector2(squad.rect.centerx, squad.rect.centery)
            squadnum += 1
    newleader = [who.leader[1], gameleader.Leader(0, 0, 1, who, battle.allleader), gameleader.Leader(0, 0, 2, who, battle.allleader),
                 gameleader.Leader(0, 0, 3, who, battle.allleader)]
    who.leader = [who.leader[0], who.leader[2], who.leader[3], gameleader.Leader(0, 0, 3, who, battle.allleader)]
    for index, leader in enumerate(who.leader):  ## also change army position of all leader in that battalion
        leader.armyposition = index  ## change army position to new one
        leader.imgposition = leader.baseimgposition[leader.armyposition]
        leader.rect = leader.image.get_rect(center=leader.imgposition)
    coa = who.coa
    who.recreatesprite()
    who.makeallsidepos()
    who.setuparmy()
    who.setupfrontline()
    who.viewmode = battle.camerascale
    who.changescale()
    who.height = who.gamemapheight.getheight(who.basepos)
    for thishitbox in who.hitbox: thishitbox.kill()
    who.hitbox = [gamebattalion.Hitbox(who, 0, who.rect.width - (who.rect.width * 0.1), 1),
                  gamebattalion.Hitbox(who, 1, 1, who.rect.height - (who.rect.height * 0.1)),
                  gamebattalion.Hitbox(who, 2, 1, who.rect.height - (who.rect.height * 0.1)),
                  gamebattalion.Hitbox(who, 3, who.rect.width - (who.rect.width * 0.1), 1)]
    who.rotate()
    who.newangle = who.angle
    ## need to recal max stat again for the original battalion
    maxhealth = []
    maxstamina = []
    maxmorale = []
    for squad in who.squadsprite:
        maxhealth.append(squad.maxtroop)
        maxstamina.append(squad.maxstamina)
        maxmorale.append(squad.maxmorale)
    maxhealth = sum(maxhealth)
    maxstamina = sum(maxstamina) / len(maxstamina)
    maxmorale = sum(maxmorale) / len(maxmorale)
    who.maxhealth, who.health75, who.health50, who.health25, = maxhealth, round(maxhealth * 75 / 100), round(
        maxhealth * 50 / 100), round(maxhealth * 25 / 100)
    who.maxstamina, who.stamina75, who.stamina50, who.stamina25, = maxstamina, round(maxstamina * 75 / 100), round(
        maxstamina * 50 / 100), round(maxstamina * 25 / 100)
    who.maxmorale = maxmorale
    ## start making new battalion
    if who.gameid < 2000:
        playercommand = True
        newgameid = battle.playerarmy[-1].gameid + 1
        colour = (144, 167, 255)
        army = gamebattalion.Unitarmy(startposition=newpos, gameid=newgameid,
                                      squadlist=newarmysquad, imgsize=(battle.imagewidth, battle.imageheight),
                                      colour=colour, control=playercommand, coa=coa, commander=False)
        battle.playerarmy.append(army)
    else:
        playercommand = battle.enactment
        newgameid = battle.enemyarmy[-1].gameid + 1
        colour = (255, 114, 114)
        army = gamebattalion.Unitarmy(startposition=newpos, gameid=newgameid,
                                      squadlist=newarmysquad, imgsize=(battle.imagewidth, battle.imageheight),
                                      colour=colour, control=playercommand, coa=coa, commander=False, startangle=who.angle)
        battle.enemyarmy.append(army)
    army.leader = newleader
    army.squadsprite = newsquadsprite
    for squad in army.squadsprite:
        squad.battalion = army
    for index, leader in enumerate(army.leader):  ## change army position of all leader in new battalion
        if how == 0:
            leader.squadpos -= newarmysquad.size  ## just minus the row gone to find new position
        else:
            for index, squad in enumerate(army.squadsprite):  ## loop to find new squad pos based on new squadsprite list
                if squad.gameid == leader.squad.gameid:
                    leader.squadpos = index
                break
        leader.battalion = army  ## set leader battalion to new one
        leader.armyposition = index  ## change army position to new one
        leader.imgposition = leader.baseimgposition[leader.armyposition]  ## change image pos
        leader.rect = leader.image.get_rect(center=leader.imgposition)
        leader.poschangestat(leader)  ## change stat based on new army position
    army.commandbuff = [(army.leader[0].meleecommand - 5) * 0.1, (army.leader[0].rangecommand - 5) * 0.1, (army.leader[0].cavcommand - 5) * 0.1]
    army.leadersocial = army.leader[0].social
    army.authrecal()
    battle.allunitlist.append(army)
    battle.allunitindex.append(army.gameid)
    army.newangle = army.angle
    army.rotate()
    army.viewmode = battle.camerascale
    army.changescale()
    army.makeallsidepos()
    army.terrain, army.feature = army.getfeature(army.basepos, army.gamemap)
    army.sidefeature = [army.getfeature(army.allsidepos[0], army.gamemap), army.getfeature(army.allsidepos[1], army.gamemap),
                        army.getfeature(army.allsidepos[2], army.gamemap), army.getfeature(army.allsidepos[3], army.gamemap)]
    army.hitbox = [gamebattalion.Hitbox(army, 0, army.rect.width - (army.rect.width * 0.1), 1),
                   gamebattalion.Hitbox(army, 1, 1, army.rect.height - (army.rect.height * 0.1)),
                   gamebattalion.Hitbox(army, 2, 1, army.rect.height - (army.rect.height * 0.1)),
                   gamebattalion.Hitbox(army, 3, army.rect.width - (army.rect.width * 0.1), 1)]
    army.autosquadplace = False


