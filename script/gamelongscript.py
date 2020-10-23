import numpy as np
import pygame
import pygame.freetype
import csv
import random
import datetime

from RTS import mainmenu
from RTS.script import gamebattalion, gameleader, gamesquad

config = mainmenu.config
SoundVolume = mainmenu.Soundvolume
SCREENRECT = mainmenu.SCREENRECT
main_dir = mainmenu.main_dir

## Other battle script

def convertweathertime(weatherevent):
    for index, item in enumerate(weatherevent):
        newtime = datetime.datetime.strptime(item[1], '%H:%M:%S').time()
        newtime = datetime.timedelta(hours=newtime.hour, minutes=newtime.minute, seconds=newtime.second)
        weatherevent[index] = [item[0], newtime, item[2]]

## Battle Start related script

def addarmy(squadlist, position, gameid, colour, imagesize, leader, leaderstat, unitstat, control, coa, command=False, startangle=0):
    squadlist = squadlist[~np.all(squadlist == 0, axis=1)]
    squadlist = squadlist[:, ~np.all(squadlist == 0, axis=0)]
    army = gamebattalion.Unitarmy(startposition=position, gameid=gameid,
                                  squadlist=squadlist, imgsize=imagesize,
                                  colour=colour, control=control, coa=coa, commander=command, startangle=startangle)
    army.hitbox = [gamebattalion.Hitbox(army, 0, army.rect.width - 10, 2),
                   gamebattalion.Hitbox(army, 1, 2, army.rect.height - 10),
                   gamebattalion.Hitbox(army, 2, 2, army.rect.height - 10),
                   gamebattalion.Hitbox(army, 3, army.rect.width - 10, 2)]
    army.leader = [gameleader.Leader(leader[0], leader[4], 0, army, leaderstat),
                   gameleader.Leader(leader[1], leader[5], 1, army, leaderstat),
                   gameleader.Leader(leader[2], leader[6], 2, army, leaderstat),
                   gameleader.Leader(leader[3], leader[7], 3, army, leaderstat)]
    return army


def unitsetup(maingame):
    """squadindexlist is list of every squad index in the game for indexing the squad group"""
    # defaultarmy = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])
    letterboard = ("a", "b", "c", "d", "e", "f", "g", "h")
    numberboard = ("8", "7", "6", "5", "4", "3", "2", "1")
    boardpos = []
    for dd in numberboard:
        for ll in letterboard:
            boardpos.append(ll + dd)
    squadindexlist = []
    unitlist = []
    playercolour = (144, 167, 255)
    enemycolour = (255, 114, 114)
    """army num is list index for battalion in either player or enemy group"""
    playerstart, enemystart = 0, 0
    """squadindex is list index for all squad group"""
    squadindex = 0
    """firstsquad check if it the first ever in group"""
    squadgameid = 10000
    with open(main_dir + "\data\\ruleset" + maingame.rulesetfolder + "\map\\" + maingame.mapselected + "\\unit_pos.csv", 'r') as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit():
                    row[n] = int(i)
                if n in range(1, 12):
                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(',')]
            if row[0] < 2000:
                if row[0] == 1:
                    """First player battalion as commander"""
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   playercolour,
                                   (maingame.imagewidth, maingame.imageheight), row[10] + row[11], maingame.allleader, maingame.gameunitstat, True, maingame.coa[row[12]], True,
                                   startangle=row[13])
                else:
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   playercolour, (maingame.imagewidth, maingame.imageheight), row[10] + row[11], maingame.allleader, maingame.gameunitstat, True, maingame.coa[row[12]],
                                   startangle=row[13])
                maingame.playerarmy.append(army)
                playerstart += 1
            elif row[0] >= 2000:
                if row[0] == 2000:
                    """First enemy battalion as commander"""
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   enemycolour,
                                   (maingame.imagewidth, maingame.imageheight), row[10] + row[11], maingame.allleader, maingame.gameunitstat, maingame.enactment, maingame.coa[row[12]], True,
                                   startangle=row[13])
                elif row[0] > 2000:
                    army = addarmy(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                                   enemycolour,
                                   (maingame.imagewidth, maingame.imageheight), row[10] + row[11], maingame.allleader, maingame.gameunitstat, maingame.enactment, maingame.coa[row[12]], startangle=row[13])
                maingame.enemyarmy.append(army)
                enemystart += 1
            """armysquadindex is list index for squad list in a specific army"""
            armysquadindex = 0
            """Setup squad in army to squad group"""
            for squadnum in np.nditer(army.armysquad, op_flags=['readwrite'], order='C'):
                if squadnum != 0:
                    addsquad = gamesquad.Unitsquad(unitid=squadnum, gameid=squadgameid, weaponlist=maingame.allweapon, armourlist=maingame.allarmour,
                                                   statlist=maingame.gameunitstat,
                                                   battalion=army, position=army.squadpositionlist[armysquadindex], inspectuipos=maingame.inspectuipos)
                    maingame.squad.append(addsquad)
                    addsquad.boardpos = boardpos[armysquadindex]
                    squadnum[...] = squadgameid
                    army.squadsprite.append(addsquad)
                    squadindexlist.append(squadgameid)
                    squadgameid += 1
                    squadindex += 1
                armysquadindex += 1
    unitfile.close()
    return squadindexlist



## Battle related script

def squadselectside(targetside, side, position):
    """side 0 is left 1 is right"""
    thisposition = position
    if side == 0:
        max = 0
        while targetside[thisposition] <= 1 and thisposition != max:
            thisposition -= 1
    else:
        max = 7
        while targetside[thisposition] <= 1 and thisposition != max:
            thisposition += 1
    if thisposition < 0:
        thisposition = 0
    elif thisposition > 7:
        thisposition = 7
    if targetside[thisposition] != 0:
        fronttarget = targetside[thisposition]
    else:
        fronttarget = 0
    return fronttarget

def changecombatside(side, position):
    """position is attacker position against defender 0 = front 1 = left 2 = rear 3 = right"""
    """side is side of attack for rotating to find the correct side the defender got attack accordingly (e.g. left attack on right side is front)"""
    subposition = position
    if subposition == 2:
        subposition = 3
    elif subposition == 3:
        subposition = 2
    changepos = 1
    if subposition == 2:
        changepos = -1
    finalposition = subposition + changepos  ## right
    if side == 0: finalposition = subposition - changepos  ## left
    if finalposition == -1:
        finalposition = 3
    elif finalposition == 4:
        finalposition = 0
    return finalposition

def losscal(who, target, hit, defense, type):
    heightadventage = who.battalion.height - target.battalion.height
    whotrait = who.trait
    if type == 1: heightadventage = int((who.battalion.height - target.battalion.height)/2)
    hit += heightadventage
    if hit < 0: hit = 0
    if defense < 0 or 30 in whotrait: defense = 0 ## Ignore def trait
    hitchance = hit - defense
    combatscore = round(hitchance/20, 1)
    if combatscore == 0 and random.randint(0, 10) > 9: ## Final chence to not miss
        combatscore = 0.1
    leaderdmgbonus = 0
    if who.leader is not None: leaderdmgbonus = who.leader.combat * 10
    if type == 0:  # Melee damage
        dmg = who.dmg
        """include charge in dmg if charging, ignore charge defense if have ignore trait"""
        if who.charging:
            if 29 not in whotrait:
                dmg = round(dmg + (who.charge / 10) - (target.chargedef / 10))
            elif 29 in whotrait:
                dmg = round(dmg + (who.charge / 10))
        leaderdmg = round((dmg * ((100 - (target.armour * ((100 - who.penetrate) / 100))) / 100) * combatscore) / 5)
        dmg = round(((leaderdmg * who.troopnumber) + leaderdmgbonus)/5)
        if target.state in (1, 2, 3, 4, 5, 6, 7, 8, 9): dmg = dmg * 5
    elif type == 1:  # Range Damage
        leaderdmg = round(who.rangedmg * ((100 - (target.armour * ((100 - who.rangepenetrate) / 100))) / 100) * combatscore)
        dmg = round((leaderdmg * who.troopnumber) + leaderdmgbonus)
    if (21 in whotrait and target.type in (1, 2)) or (23 in whotrait and target.type in (4, 5, 6, 7)):  # Anti trait dmg bonus
        dmg = dmg * 1.25
    if dmg > target.unithealth:
        dmg = target.unithealth
    moraledmg = round(dmg / 100)
    return dmg, moraledmg, leaderdmg

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


