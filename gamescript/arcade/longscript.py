import csv
import math
import os
import random

import numpy as np
import pygame
import pygame.freetype
from gamescript import commonscript

load_image = commonscript.load_image
load_images = commonscript.load_images
csv_read = commonscript.csv_read

"""This file contains fuctions of various purposes"""

# Default self mechanic value

battlesidecal = (1, 0.5, 0.1, 0.5)  # battlesidecal is for melee combat side modifier
infinity = float("inf")

letterboard = ("a", "b", "c", "d", "e", "f", "g", "h")  # letter according to subunit position in inspect ui similar to chess board
numberboard = ("8", "7", "6", "5", "4", "3", "2", "1")  # same as above
boardpos = []
for dd in numberboard:
    for ll in letterboard:
        boardpos.append(ll + dd)


# Data Loading gamescript

def load_game_data(game):
    """Load various self data"""

    main_dir = game.main_dir
    SCREENRECT = game.screen_rect
    from gamescript import battleui, uniteditor
    from gamescript.arcade import unit, subunit, rangeattack
    unit.Unit.status_list = game.troop_data.status_list
    rangeattack.RangeArrow.height_map = game.battle_map_height

    imgs = load_images(game.main_dir, ["ui", "unit_ui"])
    subunit.Subunit.images = imgs
    subunit.Subunit.base_map = game.battle_map_base  # add gamebattle map to all parentunit class
    subunit.Subunit.feature_map = game.battle_map_feature  # add gamebattle map to all parentunit class
    subunit.Subunit.height_map = game.battle_map_height
    subunit.Subunit.weapon_list = game.allweapon
    subunit.Subunit.armour_list = game.allarmour
    subunit.Subunit.stat_list = game.troop_data
    subunit.Subunit.eventlog = game.eventlog  # Assign eventlog to subunit class to broadcast event to the log

    skill_header = game.troop_data.skill_list_header
    status_header = game.troop_data.status_list_header

    # v Get index of effect column for skill and status
    subunit.Subunit.skill_trooptype = skill_header['Troop Type']
    subunit.Subunit.skill_type = skill_header['Type']
    subunit.Subunit.skill_aoe = skill_header['Area of Effect']
    subunit.Subunit.skill_duration = skill_header['Duration']
    subunit.Subunit.skill_cd = skill_header['Cooldown']
    subunit.Subunit.skill_restriction = skill_header['Restriction']
    subunit.Subunit.skill_condition = skill_header['Condition']
    subunit.Subunit.skill_discipline_req = skill_header['Discipline Requirement']
    subunit.Subunit.skill_stamina_cost = skill_header['Stamina Cost']
    subunit.Subunit.skill_mana_cost = skill_header['Mana Cost']
    subunit.Subunit.skill_melee_attack = skill_header['Melee Attack Effect']
    subunit.Subunit.skill_melee_defence = skill_header['Melee Defence Effect']
    subunit.Subunit.skill_range_defence = skill_header['Ranged Defence Effect']
    subunit.Subunit.skill_speed = skill_header['Speed Effect']
    subunit.Subunit.skill_accuracy = skill_header['Accuracy Effect']
    subunit.Subunit.skill_range = skill_header['Range Effect']
    subunit.Subunit.skill_reload = skill_header['Reload Effect']
    subunit.Subunit.skill_charge = skill_header['Charge Effect']
    subunit.Subunit.skill_charge_defence = skill_header['Charge Defence Bonus']
    subunit.Subunit.skill_hp_regen = skill_header['HP Regeneration Bonus']
    subunit.Subunit.skill_stamina_regen = skill_header['Stamina Regeneration Bonus']
    subunit.Subunit.skill_morale = skill_header['Morale Bonus']
    subunit.Subunit.skill_discipline = skill_header['Discipline Bonus']
    subunit.Subunit.skill_critical = skill_header['Critical Effect']
    subunit.Subunit.skill_damage = skill_header['Damage Effect']
    subunit.Subunit.skill_sight = skill_header['Sight Bonus']
    subunit.Subunit.skill_hide = skill_header['Hidden Bonus']
    subunit.Subunit.skill_status = skill_header['Status']
    subunit.Subunit.skill_staminadmg = skill_header['Stamina Damage']
    subunit.Subunit.skill_moraledmg = skill_header['Morale Damage']
    subunit.Subunit.skill_enemy_status = skill_header['Enemy Status']
    subunit.Subunit.skill_element = skill_header['Element']

    subunit.Subunit.status_effect = status_header['Special Effect']
    subunit.Subunit.status_conflict = status_header['Status Conflict']
    subunit.Subunit.status_duration = status_header['Duration']
    subunit.Subunit.status_melee_attack = status_header['Melee Attack Effect']
    subunit.Subunit.status_melee_defence = status_header['Melee Defence Effect']
    subunit.Subunit.status_range_defence = status_header['Ranged Defence Effect']
    subunit.Subunit.status_armour = status_header['Armour Effect']
    subunit.Subunit.status_speed = status_header['Speed Effect']
    subunit.Subunit.status_accuracy = status_header['Accuracy Effect']
    subunit.Subunit.status_reload = status_header['Reload Effect']
    subunit.Subunit.status_charge = status_header['Charge Effect']
    subunit.Subunit.status_charge_defence = status_header['Charge Defence Bonus']
    subunit.Subunit.status_hp_regen = status_header['HP Regeneration Bonus']
    subunit.Subunit.status_stamina_regen = status_header['Stamina Regeneration Bonus']
    subunit.Subunit.status_morale = status_header['Morale Bonus']
    subunit.Subunit.status_discipline = status_header['Discipline Bonus']
    subunit.Subunit.status_sight = status_header['Sight Bonus']
    subunit.Subunit.status_hide = status_header['Hidden Bonus']
    subunit.Subunit.status_temperature = status_header['Temperature Change']
    # ^ End get index

    uniteditor.Unitbuildslot.images = imgs
    uniteditor.Unitbuildslot.weapon_list = game.allweapon
    uniteditor.Unitbuildslot.armour_list = game.allarmour
    uniteditor.Unitbuildslot.stat_list = game.troop_data
    uniteditor.Unitbuildslot.skill_trooptype = skill_header['Troop Type']

    game.sprite_width, game.sprite_height = 100, 100  # size of subnit image per slot
    # ^ End subunit class

    # v Game Effect related class
    imgs = load_images(game.main_dir, ["effect"], loadorder=False)
    # imgs = []
    # for img in imgsold:
    # x, y = img.get_width(), img.get_height()
    # img = pygame.transform.scale(img, (int(x ), int(y / 2)))
    # imgs.append(img)
    rangeattack.RangeArrow.images = [imgs[0]]
    # ^ End self effect

    # Load all image of ui and icon from folder
    topimage = load_images(game.main_dir, ["ui", "battle_ui"])
    iconimage = load_images(game.main_dir, ["ui", "battle_ui", "topbar_icon"])

    # Time bar ui
    game.time_ui = battleui.TimeUI((game.screen_width - topimage[31].get_width(), 0), topimage[31])
    game.time_number = battleui.Timer(game.time_ui.rect.topleft)  # time number on time ui

    image = pygame.Surface((topimage[31].get_width(), 15))
    game.scale_ui = battleui.ScaleUI(game.time_ui.rect.bottomleft, image)

    # Right top bar ui that show rough information of selected battalions
    game.unitstat_ui = battleui.GameUI(x=SCREENRECT.width - topimage[0].get_size()[0] / 2, y=topimage[0].get_size()[1] / 2, image=topimage[0],
                                       icon=iconimage, ui_type="topbar")
    game.game_ui.add(game.unitstat_ui)
    game.unitstat_ui.unit_state_text = game.state_text

    game.inspect_button = battleui.UIButton(game.unitstat_ui.x - 206, game.unitstat_ui.y - 1, topimage[6], 1)  # unit inspect open/close button
    game.button_ui.add(game.inspect_button)

    game.battle_ui.add(game.log_scroll)
    # ^ End self ui


# Battle Start related gamescript


def add_unit(subunitlist, position, gameid, colour, unitleader, leaderstat, control, coa, command, startangle, starthp, startstamina, team):
    """Create batalion object into the battle and leader of the parentunit"""
    from gamescript.arcade import unit, leader
    oldsubunitlist = subunitlist[~np.all(subunitlist == 0, axis=1)]  # remove whole empty column in subunit list
    subunitlist = oldsubunitlist[:, ~np.all(oldsubunitlist == 0, axis=0)]  # remove whole empty row in subunit list
    unit = unit.Unit(position, gameid, subunitlist, colour, control, coa, command, abs(360 - startangle), starthp, startstamina, team)

    # add leader
    unit.leader = leader.Leader(unitleader, unit, leaderstat)
    return unit


def generate_unit(gamebattle, whicharmy, row, control, command, colour, coa, subunitgameid):
    """generate unit data into self object
    row[1:9] is subunit troop id array, row[9][0] is leader id and row[9][1] is position of sub-unt the leader located in"""
    from gamescript.arcade import subunit
    this_unit = add_unit(np.array([row[1], row[2], row[3], row[4], row[5]]), (row[6][0], row[6][1]), row[0],
                         colour, row[7], gamebattle.leader_stat, control,
                         coa, command, row[8], row[9], row[10], row[11])
    whicharmy.add(this_unit)
    armysubunitindex = 0  # armysubunitindex is list index for subunit list in a specific army

    # v Setup subunit in unit to subunit group
    row, column = 0, 0
    maxcolumn = len(this_unit.armysubunit[0])
    for subunitnum in np.nditer(this_unit.armysubunit, op_flags=["readwrite"], order="C"):
        if subunitnum != 0:
            addsubunit = subunit.Subunit(subunitnum, subunitgameid, this_unit, this_unit.subunit_position_list[armysubunitindex],
                                         this_unit.start_hp, this_unit.startstamina)
            gamebattle.subunit.add(addsubunit)
            subunitnum[...] = subunitgameid
            this_unit.subunit_sprite_array[row][column] = addsubunit
            this_unit.subunit_sprite.append(addsubunit)
            subunitgameid += 1
        else:
            this_unit.subunit_sprite_array[row][column] = None  # replace numpy None with python None

        column += 1
        if column == maxcolumn:
            column = 0
            row += 1
        armysubunitindex += 1

    return subunitgameid


def unitsetup(gamebattle):
    """read parentunit from unit_pos(source) file and create object with addunit function"""
    main_dir = gamebattle.main_dir
    # defaultunit = np.array([[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],
    # [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]])

    teamcolour = gamebattle.team_colour
    teamarmy = (gamebattle.team0_unit, gamebattle.team1_unit, gamebattle.team2_unit)

    with open(os.path.join(main_dir, "data", "ruleset", gamebattle.ruleset_folder, "map",
                           gamebattle.mapselected, gamebattle.source, gamebattle.genre, "unit_pos.csv"), encoding="utf-8", mode="r") as unitfile:
        rd = csv.reader(unitfile, quoting=csv.QUOTE_ALL)
        subunitgameid = 1
        for row in rd:
            for n, i in enumerate(row):
                if i.isdigit():
                    row[n] = int(i)
                if n in range(1, 12):
                    row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]

            control = False
            if gamebattle.playerteam == row[16] or gamebattle.enactment:  # player can control only his team or both in enactment mode
                control = True

            colour = teamcolour[row[16]]
            whicharmy = teamarmy[row[16]]

            command = False  # Not commander parentunit by default
            if len(whicharmy) == 0:  # First parentunit is commander
                command = True
            coa = pygame.transform.scale(gamebattle.coa_list[row[12]], (60, 60))  # get coa_list image and scale smaller to fit ui
            subunitgameid = generate_unit(gamebattle, whicharmy, row, control, command, colour, coa, subunitgameid)
            # ^ End subunit setup

    unitfile.close()


def convertedit_unit(gamebattle, whicharmy, row, colour, coa, subunitgameid):
    for n, i in enumerate(row):
        if type(i) == str and i.isdigit():
            row[n] = int(i)
        if n in range(1, 12):
            row[n] = [int(item) if item.isdigit() else item for item in row[n].split(",")]
    subunitgameid = generate_unit(gamebattle, whicharmy, row, True, True, colour, coa, subunitgameid)


# Battle related gamescript

def set_rotate(self, set_target=None, rotationlist=(-90, -120, -45, 0, 90, 45, 120, 180)):
    """set base_target and new angle for sprite rotation"""
    if set_target is None:  # For auto chase rotate
        myradians = math.atan2(self.base_target[1] - self.base_pos[1], self.base_target[0] - self.base_pos[0])
    else:  # Command move or rotate
        myradians = math.atan2(set_target[1] - self.base_pos[1], set_target[0] - self.base_pos[0])
    newangle = math.degrees(myradians)

    newangle = min(rotationlist,
                   key=lambda x: abs(x - newangle))  # find closest

    return newangle


def losscal(attacker, defender, hit, defence, dmgtype, defside=None):
    """Calculate melee_dmg, type 0 is melee attack and will use attacker subunit stat,
    type that is not 0 will use the type object stat instead (mostly used for range attack)"""
    who = attacker
    target = defender

    heightadventage = who.height - target.height
    if dmgtype != 0:
        heightadventage = int(heightadventage / 2)  # Range attack use less height advantage
    hit += heightadventage

    if defence < 0 or who.ignore_def:  # Ignore def trait
        defence = 0

    hitchance = hit - defence
    if hitchance < 0:
        hitchance = 0
    elif hitchance > 80:  # Critical hit
        hitchance *= who.crit_effect  # modify with crit effect further
        if hitchance > 200:
            hitchance = 200
    else:  # infinity number can cause nan value
        hitchance = 200

    combatscore = round(hitchance / 100, 1)
    if combatscore == 0 and random.randint(0, 10) > 9:  # Final chence to not miss
        combatscore = 0.1

    if combatscore > 0:
        leaderdmgbonus = 0
        if who.leader is not None:
            leaderdmgbonus = who.leader.combat  # Get extra melee_dmg from leader combat stat

        if dmgtype == 0:  # Melee melee_dmg
            dmg = random.uniform(who.melee_dmg[0], who.melee_dmg[1])
            if who.chargeskill in who.skill_effect:  # Include charge in melee_dmg if attacking
                if who.ignore_chargedef is False:  # Ignore charge defence if have ignore trait
                    sidecal = battlesidecal[defside]
                    if target.fulldef or target.temp_fulldef:  # defence all side
                        sidecal = 1
                    dmg = dmg + ((who.charge - (target.charge_def * sidecal)) * 2)
                    if (target.charge_def * sidecal) >= who.charge / 2:
                        who.charge_momentum = 1  # charge get stopped by charge def
                    else:
                        who.charge_momentum -= (target.charge_def * sidecal) / who.charge
                else:
                    dmg = dmg + (who.charge * 2)
                    who.charge_momentum -= 1 / who.charge

            if target.chargeskill in target.skill_effect:  # Also include charge_def in melee_dmg if enemy charging
                if target.ignore_chargedef is False:
                    chargedefcal = who.charge_def - target.charge
                    if chargedefcal < 0:
                        chargedefcal = 0
                    dmg = dmg + (chargedefcal * 2)  # if charge def is higher than enemy charge then deal back addtional melee_dmg
            elif who.chargeskill not in who.skill_effect:  # not charging or defend from charge, use attack speed roll
                dmg += sum([random.uniform(who.melee_dmg[0], who.melee_dmg[1]) for x in range(who.meleespeed)])

            penetrate = who.melee_penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmg * penetrate * combatscore

        else:  # Range Damage
            penetrate = dmgtype.penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmgtype.melee_dmg * penetrate * combatscore

        leaderdmg = dmg
        unitdmg = (
                              dmg * who.troop_number) + leaderdmgbonus  # melee_dmg on subunit is melee_dmg multiply by troop number with addition from leader combat
        if (who.anti_inf and target.subunit_type in (1, 2)) or (who.anti_cav and target.subunit_type in (4, 5, 6, 7)):  # Anti trait melee_dmg bonus
            unitdmg = unitdmg * 1.25
        # if type == 0: # melee do less melee_dmg per hit because the combat happen more frequently than range
        #     unitdmg = unitdmg / 20

        moraledmg = dmg / 50

        # Damage cannot be negative (it would heal instead), same for morale and leader melee_dmg
        if unitdmg < 0:
            unitdmg = 0
        if leaderdmg < 0:
            leaderdmg = 0
        if moraledmg < 0:
            moraledmg = 0
    else:  # complete miss
        unitdmg = 0
        leaderdmg = 0
        moraledmg = 0

    return unitdmg, moraledmg, leaderdmg


def applystatustoenemy(statuslist, inflictstatus, receiver, attackerside, receiverside):
    """apply aoe status effect to enemy subunits"""
    for status in inflictstatus.items():
        if status[1] == 1 and attackerside == 0:  # only front enemy
            receiver.status_effect[status[0]] = statuslist[status[0]].copy()
        elif status[1] == 2:  # aoe effect to side enemy
            receiver.status_effect[status[0]] = statuslist[status[0]].copy()
            if status[1] == 3:  # apply to corner enemy subunit (left and right of self front enemy subunit)
                corner_enemy_apply = receiver.nearby_subunit_list[0:2]
                if receiverside in (1, 2):  # attack on left/right side means corner enemy would be from front and rear side of the enemy
                    corner_enemy_apply = [receiver.nearby_subunit_list[2], receiver.nearby_subunit_list[5]]
                for this_subunit in corner_enemy_apply:
                    if this_subunit != 0:
                        this_subunit.status_effect[status[0]] = statuslist[status[0]].copy()
        elif status[1] == 3:  # whole parentunit aoe
            for this_subunit in receiver.parentunit.subunit_sprite:
                if this_subunit.state != 100:
                    this_subunit.status_effect[status[0]] = statuslist[status[0]].copy()


def complexdmg(attacker, receiver, dmg, moraledmg, leaderdmg, dmgeffect, timermod):
    final_dmg = round(dmg * dmgeffect * timermod)
    final_moraledmg = round(moraledmg * dmgeffect * timermod)
    if final_dmg > receiver.unit_health:  # melee_dmg cannot be higher than remaining health
        final_dmg = receiver.unit_health

    receiver.unit_health -= final_dmg
    health_check = 0.1
    if receiver.max_health != infinity:
        health_check = 1 - (receiver.unit_health / receiver.max_health)
    receiver.base_morale -= (final_moraledmg + attacker.bonus_morale_dmg) * receiver.mental * health_check
    receiver.stamina -= attacker.bonus_stamina_dmg

    # v Add red corner to indicate combat
    if receiver.red_border is False:
        receiver.imageblock.blit(receiver.images[11], receiver.corner_image_rect)
        receiver.red_border = True
    # ^ End red corner

    if attacker.elem_melee not in (0, 5):  # apply element effect if atk has element, except 0 physical, 5 magic
        receiver.elem_count[attacker.elem_melee - 1] += round(final_dmg * (100 - receiver.elem_res[attacker.elem_melee - 1] / 100))

    attacker.base_morale += round((final_moraledmg / 5))  # recover some morale when deal morale melee_dmg to enemy

    if receiver.leader is not None and receiver.leader.health > 0 and random.randint(0, 10) > 9:  # melee_dmg on subunit leader, only 10% chance
        finalleaderdmg = round(leaderdmg - (leaderdmg * receiver.leader.combat / 101) * timermod)
        if finalleaderdmg > receiver.leader.health:
            finalleaderdmg = receiver.leader.health
        receiver.leader.health -= finalleaderdmg


def dmgcal(attacker, target, attackerside, targetside, statuslist, combattimer):
    """base_target position 0 = Front, 1 = Side, 3 = Rear, attackerside and targetside is the side attacking and defending respectively"""
    wholuck = random.randint(-50, 50)  # attacker luck
    targetluck = random.randint(-50, 50)  # defender luck
    whopercent = battlesidecal[attackerside]  # attacker attack side modifier

    """34 battlemaster fulldef or 91 allrounddef status = no flanked penalty"""
    if attacker.fulldef or 91 in attacker.status_effect:
        whopercent = 1
    targetpercent = battlesidecal[targetside]  # defender defend side

    if target.fulldef or 91 in target.status_effect:
        targetpercent = 1

    dmgeffect = attacker.front_dmg_effect
    targetdmgeffect = target.front_dmg_effect

    if attackerside != 0 and whopercent != 1:  # if attack or defend from side will use discipline to help reduce penalty a bit
        whopercent = battlesidecal[attackerside] + (attacker.discipline / 300)
        dmgeffect = attacker.side_dmg_effect  # use side melee_dmg effect as some skill boost only front melee_dmg
        if whopercent > 1:
            whopercent = 1

    if targetside != 0 and targetpercent != 1:  # same for the base_target defender
        targetpercent = battlesidecal[targetside] + (target.discipline / 300)
        targetdmgeffect = target.side_dmg_effect
        if targetpercent > 1:
            targetpercent = 1

    whohit = float(attacker.attack * whopercent) + wholuck
    whodefence = float(attacker.melee_def * whopercent) + wholuck
    targethit = float(attacker.attack * targetpercent) + targetluck
    targetdefence = float(target.melee_def * targetpercent) + targetluck

    """33 backstabber ignore def when attack rear side, 55 Oblivious To Unexpected can't defend from rear at all"""
    if (attacker.backstab and targetside == 2) or (target.oblivious and targetside == 2) or (
            target.flanker and attackerside in (1, 3)):  # Apply only for attacker
        targetdefence = 0

    whodmg, whomoraledmg, wholeaderdmg = losscal(attacker, target, whohit, targetdefence, 0, targetside)  # get melee_dmg by attacker
    targetdmg, targetmoraledmg, targetleaderdmg = losscal(target, attacker, targethit, whodefence, 0, attackerside)  # get melee_dmg by defender

    timermod = combattimer / 0.5  # Since the update happen anytime more than 0.5 second, high speed that pass by longer than x1 speed will become inconsistent
    complexdmg(attacker, target, whodmg, whomoraledmg, wholeaderdmg, dmgeffect, timermod)  # Inflict melee_dmg to defender
    complexdmg(target, attacker, targetdmg, targetmoraledmg, targetleaderdmg, targetdmgeffect, timermod)  # Inflict melee_dmg to attacker

    # v Attack corner (side) of self with aoe attack
    if attacker.corner_atk:
        listloop = [target.nearby_subunit_list[2], target.nearby_subunit_list[5]]  # Side attack get (2) front and (5) rear nearby subunit
        if targetside in (0, 2):
            listloop = target.nearby_subunit_list[0:2]  # Front/rear attack get (0) left and (1) right nearbysubunit
        for this_subunit in listloop:
            if this_subunit != 0 and this_subunit.state != 100:
                targethit, targetdefence = float(attacker.attack * targetpercent) + targetluck, float(
                    this_subunit.melee_def * targetpercent) + targetluck
                whodmg, whomoraledmg = losscal(attacker, this_subunit, whohit, targetdefence, 0)
                complexdmg(attacker, this_subunit, whodmg, whomoraledmg, wholeaderdmg, dmgeffect, timermod)
    # ^ End attack corner

    # v inflict status based on aoe 1 = front only 2 = all 4 side, 3 corner enemy subunit, 4 entire parentunit
    if attacker.inflictstatus != {}:
        applystatustoenemy(statuslist, attacker.inflictstatus, target, attackerside, targetside)
    if target.inflictstatus != {}:
        applystatustoenemy(statuslist, target.inflictstatus, attacker, targetside, attackerside)
    # ^ End inflict status


def die(who, battle, moralehit=True):
    """remove subunit when it dies"""
    if who.team == 1:
        group = battle.team1_unit
        enemygroup = battle.team2_unit
        battle.team1poslist.pop(who.game_id)
    else:
        group = battle.team2_unit
        enemygroup = battle.team1_unit
        battle.team2poslist.pop(who.game_id)

    if moralehit:
        if who.commander:  # more morale penalty if the parentunit is a command parentunit
            for army in group:
                for this_subunit in army.subunit_sprite:
                    this_subunit.base_morale -= 30

        for thisarmy in enemygroup:  # get bonus authority to the another army
            thisarmy.authority += 5

        for thisarmy in group:  # morale melee_dmg to every subunit in army when allied parentunit destroyed
            for this_subunit in thisarmy.subunit_sprite:
                this_subunit.base_morale -= 20

    battle.allunitlist.remove(who)
    battle.allunitindex.remove(who.game_id)
    group.remove(who)
    who.got_killed = True


def move_leader_subunit(this_leader, oldarmysubunit, newarmysubunit, alreadypick=()):
    """oldarmysubunit is armysubunit list that the subunit currently in and need to be move out to the new one (newarmysubunit),
    alreadypick is list of position need to be skipped"""
    replace = [np.where(oldarmysubunit == this_leader.subunit.game_id)[0][0],
               np.where(oldarmysubunit == this_leader.subunit.game_id)[1][0]]  # grab old array position of subunit
    newrow = int((len(newarmysubunit) - 1) / 2)  # set up new row subunit will be place in at the middle at the start
    newplace = int((len(newarmysubunit[newrow]) - 1) / 2)  # setup new column position
    placedone = False  # finish finding slot to place yet

    while placedone is False:
        if this_leader.subunit.parentunit.armysubunit.flat[newrow * newplace] != 0:
            for this_subunit in this_leader.subunit.parentunit.subunit_sprite:
                if this_subunit.game_id == this_leader.subunit.parentunit.armysubunit.flat[newrow * newplace]:
                    if this_subunit.this_leader is not None or (newrow, newplace) in alreadypick:
                        newplace += 1
                        if newplace > len(newarmysubunit[newrow]) - 1:  # find new column
                            newplace = 0
                        elif newplace == int(
                                len(newarmysubunit[newrow]) / 2):  # find in new row when loop back to the first one
                            newrow += 1
                        placedone = False
                    else:  # found slot to replace
                        placedone = True
                        break
        else:  # fill in the subunit if the slot is empty
            placedone = True

    oldarmysubunit[replace[0]][replace[1]] = newarmysubunit[newrow][newplace]
    newarmysubunit[newrow][newplace] = this_leader.subunit.game_id
    newposition = (newplace, newrow)
    return oldarmysubunit, newarmysubunit, newposition


# Other scripts

def generate_animation_pool():
    return
