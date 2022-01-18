import csv
import math
import os
import random

import numpy as np
import pygame
import pygame.freetype
from gamescript import script_common

load_image = script_common.load_image
load_images = script_common.load_images
csv_read = script_common.csv_read

"""This file contains fuctions of various purposes"""

# Default self mechanic value

battlesidecal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier
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

    SCREENRECT = game.screen_rect
    from gamescript import battleui, uniteditor, rangeattack
    from gamescript.tactical import unit, subunit

    unit.Unit.status_list = game.troop_data.status_list
    rangeattack.RangeArrow.height_map = game.battle_height_map

    imgs = load_images(game.main_dir, ["ui", "unit_ui"])
    subunit.Subunit.images = imgs
    subunit.Subunit.base_map = game.battle_base_map  # add battle map to all unit class
    subunit.Subunit.feature_map = game.battle_feature_map  # add battle map to all unit class
    subunit.Subunit.height_map = game.battle_height_map
    subunit.Subunit.weapon_list = game.all_weapon
    subunit.Subunit.armour_list = game.all_armour
    subunit.Subunit.stat_list = game.troop_data
    subunit.Subunit.event_log = game.event_log  # Assign event_log to subunit class to broadcast event to the log

    skill_header = game.troop_data.skill_list_header
    status_header = game.troop_data.status_list_header

    # v Get index of effect column for skill and status
    subunit.Subunit.skill_troop_type = skill_header['Troop Type']
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
    subunit.Subunit.skill_stamina_dmg = skill_header['Stamina Damage']
    subunit.Subunit.skill_morale_dmg = skill_header['Morale Damage']
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

    uniteditor.UnitBuildSlot.images = imgs
    uniteditor.UnitBuildSlot.weapon_list = game.all_weapon
    uniteditor.UnitBuildSlot.armour_list = game.all_armour
    uniteditor.UnitBuildSlot.stat_list = game.troop_data
    uniteditor.UnitBuildSlot.skill_troop_type = skill_header['Troop Type']
    # ^ End subunit class

    # v Game Effect related class
    imgs = load_images(game.main_dir, ["effect"], load_order=False)
    # images = []
    # for images in imgsold:
    # x, y = images.get_width(), images.get_height()
    # images = pygame.transform.scale(images, (int(x ), int(y / 2)))
    # images.append(images)
    rangeattack.RangeArrow.images = [imgs[0]]
    # ^ End self effect

    topimage = load_images(game.main_dir, ["ui", "battle_ui"])
    iconimage = load_images(game.main_dir, ["ui", "battle_ui", "commandbar_icon"])
    # Army select list ui
    game.unit_selector = battleui.ArmySelect((0, 0), topimage[30])
    game.select_scroll = battleui.UIScroller(game.unit_selector.rect.topright, topimage[30].get_height(),
                                             game.unit_selector.max_row_show)  # scroller for unit select ui

    game.command_ui = battleui.GameUI(x=topimage[1].get_size()[0] / 2, y=(topimage[1].get_size()[1] / 2) + game.unit_selector.image.get_height(),
                                      image=topimage[1], icon=iconimage,
                                      ui_type="commandbar")  # Left top command ui with leader and unit behavious button
    game.game_ui.add(game.command_ui)

    # Load all image of ui and icon from folder
    iconimage = load_images(game.main_dir, ["ui", "battle_ui", "topbar_icon"])

    game.col_split_button = battleui.UIButton(game.command_ui.x - 115, game.command_ui.y + 26, topimage[8], 0)  # unit split by column button
    game.row_split_button = battleui.UIButton(game.command_ui.x - 115, game.command_ui.y + 56, topimage[9], 1)  # unit split by row button
    game.button_ui.add(game.col_split_button)
    game.button_ui.add(game.row_split_button)

    game.decimation_button = battleui.UIButton(game.command_ui.x + 100, game.command_ui.y + 56, topimage[14], 1)

    # Time bar ui
    game.time_ui = battleui.TimeUI(game.unit_selector.rect.topright, topimage[31])
    game.time_number = battleui.Timer(game.time_ui.rect.topleft)  # time number on time ui
    game.speed_number = battleui.SpeedNumber((game.time_ui.rect.center[0] + 40, game.time_ui.rect.center[1]),
                                             1)  # self speed number on the time ui

    image = pygame.Surface((topimage[31].get_width(), 15))
    game.scale_ui = battleui.ScaleUI(game.time_ui.rect.bottomleft, image)

    game.time_button = [battleui.UIButton(game.time_ui.rect.center[0] - 30, game.time_ui.rect.center[1], topimage[32], 0),  # time pause button
                        battleui.UIButton(game.time_ui.rect.center[0], game.time_ui.rect.center[1], topimage[33], 1),  # time decrease button
                        battleui.UIButton(game.time_ui.rect.midright[0] - 60, game.time_ui.rect.center[1], topimage[34], 2)]  # time increase button
    game.battle_ui.add(*game.time_button)

    # Right top bar ui that show rough information of selected battalions
    game.unitstat_ui = battleui.GameUI(x=SCREENRECT.width - topimage[0].get_size()[0] / 2, y=topimage[0].get_size()[1] / 2, image=topimage[0],
                                       icon=iconimage, ui_type="topbar")
    game.game_ui.add(game.unitstat_ui)
    game.unitstat_ui.unit_state_text = game.state_text

    game.inspect_ui_pos = [game.unitstat_ui.rect.bottomleft[0] - game.icon_sprite_width / 1.25,
                           game.unitstat_ui.rect.bottomleft[1] - game.icon_sprite_height / 3]

    # Subunit information card ui
    game.inspect_ui = battleui.GameUI(x=SCREENRECT.width - topimage[5].get_size()[0] / 2, y=topimage[0].get_size()[1] * 4,
                                      image=topimage[5], icon="", ui_type="unitbox")  # inspect ui that show subnit in selected unit
    game.game_ui.add(game.inspect_ui)
    # v Subunit shown in inspect ui
    width, height = game.inspect_ui_pos[0], game.inspect_ui_pos[1]
    subunitnum = 0  # Number of subnit based on the position in row and column
    imgsize = (game.icon_sprite_width, game.icon_sprite_height)
    game.inspect_subunit = []
    for this_subunit in list(range(0, 64)):
        width += imgsize[0]
        game.inspect_subunit.append(battleui.InspectSubunit((width, height)))
        subunitnum += 1
        if subunitnum == 8:  # Reach the last subnit in the row, go to the next one
            width = game.inspect_ui_pos[0]
            height += imgsize[1]
            subunitnum = 0
    # ^ End subunit shown

    # Behaviour button that once click switch to other mode for subunit behaviour
    game.switch_button = [battleui.SwitchButton(game.command_ui.x - 40, game.command_ui.y + 96, topimage[10:14]),  # skill condition button
                          battleui.SwitchButton(game.command_ui.x - 80, game.command_ui.y + 96, topimage[15:17]),  # fire at will button
                          battleui.SwitchButton(game.command_ui.x, game.command_ui.y + 96, topimage[17:20]),  # behaviour button
                          battleui.SwitchButton(game.command_ui.x + 40, game.command_ui.y + 96, topimage[20:22]),  # shoot range button
                          battleui.SwitchButton(game.command_ui.x - 125, game.command_ui.y + 96, topimage[35:38]),  # arc_shot button
                          battleui.SwitchButton(game.command_ui.x + 80, game.command_ui.y + 96, topimage[38:40]),  # toggle run button
                          battleui.SwitchButton(game.command_ui.x + 120, game.command_ui.y + 96, topimage[40:43])]  # toggle melee mode

    game.inspect_button = battleui.UIButton(game.unitstat_ui.x - 206, game.unitstat_ui.y - 1, topimage[6], 1)  # unit inspect open/close button
    game.button_ui.add(game.inspect_button)

    game.battle_ui.add(game.log_scroll, game.select_scroll)

    battleui.SelectedSquad.image = topimage[-1]  # subunit border image always the last one
    game.inspect_selected_border = battleui.SelectedSquad((15000, 15000))  # yellow border on selected subnit in inspect ui
    game.main_ui.remove(game.inspect_selected_border)  # remove subnit border sprite from gamestart menu drawer

    # ^ End self ui


# Battle Start related gamescript

def add_unit(subunitlist, position, gameid, colour, leaderlist, leaderstat, control, coa, command, startangle, starthp, startstamina, team):
    """Create batalion object into the battle and leader of the unit"""
    from gamescript.tactical import unit, leader
    oldsubunitlist = subunitlist[~np.all(subunitlist == 0, axis=1)]  # remove whole empty column in subunit list
    subunitlist = oldsubunitlist[:, ~np.all(oldsubunitlist == 0, axis=0)]  # remove whole empty row in subunit list
    unit = unit.Unit(position, gameid, subunitlist, colour, control, coa, command, abs(360 - startangle), starthp, startstamina, team)

    # add leader
    unit.leader = [leader.Leader(leaderlist[0], leaderlist[4], 0, unit, leaderstat),
                   leader.Leader(leaderlist[1], leaderlist[5], 1, unit, leaderstat),
                   leader.Leader(leaderlist[2], leaderlist[6], 2, unit, leaderstat),
                   leader.Leader(leaderlist[3], leaderlist[7], 3, unit, leaderstat)]
    return unit


def generate_unit(gamebattle, whicharmy, row, control, command, colour, coa, subunitgameid):
    """generate unit data into self object
    row[1:9] is subunit troop id array, row[9][0] is leader id and row[9][1] is position of sub-unt the leader located in"""
    from gamescript.tactical import unit, subunit
    this_unit = add_unit(np.array([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]), (row[9][0], row[9][1]), row[0],
                         colour, row[10] + row[11], gamebattle.leader_stat, control,
                         coa, command, row[13], row[14], row[15], row[16])
    whicharmy.add(this_unit)
    armysubunitindex = 0  # armysubunitindex is list index for subunit list in a specific army

    # v Setup subunit in unit to subunit group
    row, column = 0, 0
    maxcolumn = len(this_unit.subunit_list[0])
    for subunitnum in np.nditer(this_unit.subunit_list, op_flags=["readwrite"], order="C"):
        if subunitnum != 0:
            addsubunit = subunit.Subunit(subunitnum, subunitgameid, this_unit, this_unit.subunit_position_list[armysubunitindex],
                                         this_unit.start_hp, this_unit.start_stamina, gamebattle.unitscale)
            gamebattle.subunit.add(addsubunit)
            addsubunit.board_pos = boardpos[armysubunitindex]
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
    gamebattle.troop_number_sprite.add(unit.TroopNumber(gamebattle.screen_scale, this_unit))  # create troop number text sprite

    return subunitgameid


def unitsetup(gamebattle):
    """read unit from unit_pos(source) file and create object with addunit function"""
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

            command = False  # Not commander unit by default
            if len(whicharmy) == 0:  # First unit is commander
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

def losscal(attacker, defender, hit, defence, dmgtype, defside=None):
    """Calculate dmg, type 0 is melee attack and will use attacker subunit stat,
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
            leaderdmgbonus = who.leader.combat  # Get extra dmg from leader combat stat

        if dmgtype == 0:  # Melee melee_dmg
            dmg = random.uniform(who.melee_dmg[0], who.melee_dmg[1])
            if who.charge_skill in who.skill_effect:  # Include charge in melee_dmg if attacking
                if who.ignore_charge_def is False:  # Ignore charge defence if have ignore trait
                    sidecal = battlesidecal[defside]
                    if target.full_def or target.temp_full_def:  # defence all side
                        sidecal = 1
                    dmg = dmg + ((who.charge - (target.charge_def * sidecal)) * 2)
                    if (target.charge_def * sidecal) >= who.charge / 2:
                        who.charge_momentum = 1  # charge get stopped by charge def
                    else:
                        who.charge_momentum -= (target.charge_def * sidecal) / who.charge
                else:
                    dmg = dmg + (who.charge * 2)
                    who.charge_momentum -= 1 / who.charge

            if target.charge_skill in target.skill_effect:  # Also include charge_def in melee_dmg if enemy charging
                if target.ignore_charge_def is False:
                    chargedefcal = who.charge_def - target.charge
                    if chargedefcal < 0:
                        chargedefcal = 0
                    dmg = dmg + (chargedefcal * 2)  # if charge def is higher than enemy charge then deal back addtional melee_dmg
            elif who.charge_skill not in who.skill_effect:  # not charging or defend from charge, use attack speed roll
                dmg += sum([random.uniform(who.melee_dmg[0], who.melee_dmg[1]) for x in range(who.melee_speed)])

            penetrate = who.melee_penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmg * penetrate * combatscore

        else:  # Range Damage
            penetrate = dmgtype.penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmgtype.dmg * penetrate * combatscore

        leaderdmg = dmg
        unitdmg = (dmg * who.troop_number) + leaderdmgbonus  # dmg on subunit is dmg multiply by troop number with addition from leader combat
        if (who.anti_inf and target.subunit_type in (1, 2)) or (who.anti_cav and target.subunit_type in (4, 5, 6, 7)):  # Anti trait dmg bonus
            unitdmg = unitdmg * 1.25

        moraledmg = dmg / 50

        # Damage cannot be negative (it would heal instead), same for morale and leader dmg
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
        elif status[1] == 3:  # whole unit aoe
            for this_subunit in receiver.unit.subunit_sprite:
                if this_subunit.state != 100:
                    this_subunit.status_effect[status[0]] = statuslist[status[0]].copy()


def complexdmg(attacker, receiver, dmg, moraledmg, leaderdmg, dmgeffect, timermod):
    final_dmg = round(dmg * dmgeffect * timermod)
    final_moraledmg = round(moraledmg * dmgeffect * timermod)
    if final_dmg > receiver.unit_health:  # dmg cannot be higher than remaining health
        final_dmg = receiver.unit_health

    receiver.unit_health -= final_dmg
    health_check = 0.1
    if receiver.max_health != infinity:
        health_check = 1 - (receiver.unit_health / receiver.max_health)
    receiver.base_morale -= (final_moraledmg + attacker.bonus_morale_dmg) * receiver.mental * health_check
    receiver.stamina -= attacker.bonus_stamina_dmg

    # v Add red corner to indicate combat
    if receiver.red_border is False:
        receiver.block.blit(receiver.images[11], receiver.corner_image_rect)
        receiver.red_border = True
    # ^ End red corner

    if attacker.elem_melee not in (0, 5):  # apply element effect if atk has element, except 0 physical, 5 magic
        receiver.elem_count[attacker.elem_melee - 1] += round(final_dmg * (100 - receiver.elem_res[attacker.elem_melee - 1] / 100))

    attacker.base_morale += round((final_moraledmg / 5))  # recover some morale when deal morale dmg to enemy

    if receiver.leader is not None and receiver.leader.health > 0 and random.randint(0, 10) > 9:  # dmg on subunit leader, only 10% chance
        finalleaderdmg = round(leaderdmg - (leaderdmg * receiver.leader.combat / 101) * timermod)
        if finalleaderdmg > receiver.leader.health:
            finalleaderdmg = receiver.leader.health
        receiver.leader.health -= finalleaderdmg


def dmgcal(attacker, target, attackerside, targetside, statuslist, combattimer):
    """base_target position 0 = Front, 1 = Side, 3 = Rear, attacker_side and target_side is the side attacking and defending respectively"""
    wholuck = random.randint(-50, 50)  # attacker luck
    targetluck = random.randint(-50, 50)  # defender luck
    whopercent = battlesidecal[attackerside]  # attacker attack side modifier

    """34 battlemaster full_def or 91 allrounddef status = no flanked penalty"""
    if attacker.full_def or 91 in attacker.status_effect:
        whopercent = 1
    targetpercent = battlesidecal[targetside]  # defender defend side

    if target.full_def or 91 in target.status_effect:
        targetpercent = 1

    dmgeffect = attacker.front_dmg_effect
    targetdmgeffect = target.front_dmg_effect

    if attackerside != 0 and whopercent != 1:  # if attack or defend from side will use discipline to help reduce penalty a bit
        whopercent = battlesidecal[attackerside] + (attacker.discipline / 300)
        dmgeffect = attacker.side_dmg_effect  # use side dmg effect as some skill boost only front dmg
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

    whodmg, whomoraledmg, wholeaderdmg = losscal(attacker, target, whohit, targetdefence, 0, targetside)  # get dmg by attacker
    targetdmg, targetmoraledmg, targetleaderdmg = losscal(target, attacker, targethit, whodefence, 0, attackerside)  # get dmg by defender

    timermod = combattimer / 0.5  # Since the update happen anytime more than 0.5 second, high speed that pass by longer than x1 speed will become inconsistent
    complexdmg(attacker, target, whodmg, whomoraledmg, wholeaderdmg, dmgeffect, timermod)  # Inflict dmg to defender
    complexdmg(target, attacker, targetdmg, targetmoraledmg, targetleaderdmg, targetdmgeffect, timermod)  # Inflict dmg to attacker

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

    # v inflict status based on aoe 1 = front only 2 = all 4 side, 3 corner enemy subunit, 4 entire unit
    if attacker.inflict_status != {}:
        applystatustoenemy(statuslist, attacker.inflict_status, target, attackerside, targetside)
    if target.inflict_status != {}:
        applystatustoenemy(statuslist, target.inflict_status, attacker, targetside, attackerside)
    # ^ End inflict status


def die(who, battle, moralehit=True):
    """remove subunit when it dies"""
    if who.team == 1:
        group = battle.team1_unit
        enemygroup = battle.team2_unit
        battle.team1_pos_list.pop(who.game_id)
    else:
        group = battle.team2_unit
        enemygroup = battle.team1_unit
        battle.team2_pos_list.pop(who.game_id)

    if moralehit:
        if who.commander:  # more morale penalty if the unit is a command unit
            for army in group:
                for this_subunit in army.subunit_sprite:
                    this_subunit.base_morale -= 30

        for thisarmy in enemygroup:  # get bonus authority to the another army
            thisarmy.authority += 5

        for thisarmy in group:  # morale dmg to every subunit in army when allied unit destroyed
            for this_subunit in thisarmy.subunit_sprite:
                this_subunit.base_morale -= 20

    battle.all_unit_list.remove(who)
    battle.all_unit_index.remove(who.game_id)
    group.remove(who)
    who.got_killed = True


def change_leader(self, event):
    """Leader change subunit or gone/destroyed, event can be "destroyed" or "broken" """
    checkstate = [100]
    if event == "broken":
        checkstate = [99, 100]
    if self.leader is not None and self.leader.state != 100:  # Find new subunit for leader if there is one in this subunit
        for this_subunit in self.nearby_subunit_list:
            if this_subunit != 0 and this_subunit.state not in checkstate and this_subunit.leader is None:
                this_subunit.leader = self.leader
                self.leader.subunit = this_subunit
                for index, subunit2 in enumerate(self.unit.subunit_sprite):  # loop to find new subunit pos based on new subunit_sprite list
                    if subunit2 == self.leader.subunit:
                        self.leader.subunit_pos = index
                        if self.unit_leader:  # set leader subunit to new one
                            self.unit.leader_subunit = subunit2
                            subunit2.unit_leader = True
                            self.unit_leader = False
                        break

                self.leader = None
                break

        if self.leader is not None:  # if can't find near subunit to move leader then find from first subunit to last place in unit
            for index, this_subunit in enumerate(self.unit.subunit_sprite):
                if this_subunit.state not in checkstate and this_subunit.leader is None:
                    this_subunit.leader = self.leader
                    self.leader.subunit = this_subunit
                    this_subunit.leader.subunit_pos = index
                    self.leader = None
                    if self.unit_leader:  # set leader subunit to new one
                        self.unit.leader_subunit = this_subunit
                        this_subunit.unit_leader = True

                    break

            if self.leader is not None and event == "destroyed":  # Still can't find new subunit so leader disappear with chance of different result
                self.leader.state = random.randint(97, 100)  # captured, retreated, wounded, dead
                self.leader.health = 0
                self.leader.gone()

        self.unit_leader = False


def add_new_unit(gamebattle, who, addunitlist=True):
    from gamescript.tactical import unit
    # generate subunit sprite array for inspect ui
    who.subunit_sprite_array = np.empty((8, 8), dtype=object)  # array of subunit object(not index)
    foundcount = 0  # for subunit_sprite index
    foundcount2 = 0  # for positioning
    for row in range(0, len(who.subunit_list)):
        for column in range(0, len(who.subunit_list[0])):
            if who.subunit_list[row][column] != 0:
                who.subunit_sprite_array[row][column] = who.subunit_sprite[foundcount]
                who.subunit_sprite[foundcount].unit_position = (who.subunit_position_list[foundcount2][0] / 10,
                                                                who.subunit_position_list[foundcount2][1] / 10)  # position in unit sprite
                foundcount += 1
            else:
                who.subunit_sprite_array[row][column] = None
            foundcount2 += 1
    # ^ End generate subunit array

    for index, this_subunit in enumerate(who.subunit_sprite):  # reset leader subunitpos
        if this_subunit.leader is not None:
            this_subunit.leader.subunit_pos = index

    who.zoom = 11 - gamebattle.camera_scale
    who.new_angle = who.angle

    who.start_set(gamebattle.subunit)
    who.set_target(who.front_pos)

    numberpos = (who.base_pos[0] - who.base_width_box,
                 (who.base_pos[1] + who.base_height_box))
    who.number_pos = who.rotation_xy(who.base_pos, numberpos, who.radians_angle)
    who.change_pos_scale()  # find new position for troop number text

    for this_subunit in who.subunit_sprite:
        this_subunit.gamestart(this_subunit.zoom)

    if addunitlist:
        gamebattle.all_unit_list.append(who)
        gamebattle.all_unit_index.append(who.game_id)

    numberspite = unit.TroopNumber(gamebattle.screen_scale, who)
    gamebattle.troop_number_sprite.add(numberspite)


def move_leader_subunit(this_leader, oldarmysubunit, newarmysubunit, alreadypick=()):
    """old_army_subunit is subunit_list list that the subunit currently in and need to be move out to the new one (new_army_subunit),
    already_pick is list of position need to be skipped"""
    replace = [np.where(oldarmysubunit == this_leader.subunit.game_id)[0][0],
               np.where(oldarmysubunit == this_leader.subunit.game_id)[1][0]]  # grab old array position of subunit
    newrow = int((len(newarmysubunit) - 1) / 2)  # set up new row subunit will be place in at the middle at the start
    newplace = int((len(newarmysubunit[newrow]) - 1) / 2)  # setup new column position
    placedone = False  # finish finding slot to place yet

    while placedone is False:
        if this_leader.subunit.unit.subunit_list.flat[newrow * newplace] != 0:
            for this_subunit in this_leader.subunit.unit.subunit_sprite:
                if this_subunit.game_id == this_leader.subunit.unit.subunit_list.flat[newrow * newplace]:
                    if this_subunit.leader is not None or (newrow, newplace) in alreadypick:
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


def splitunit(battle, who, how):
    """split unit either by row or column into two seperate unit"""  # TODO check split when moving
    from gamescript.tactical import unit, leader

    if how == 0:  # split by row
        newarmysubunit = np.array_split(who.subunit_list, 2)[1]
        who.subunit_list = np.array_split(who.subunit_list, 2)[0]
        newpos = pygame.Vector2(who.base_pos[0], who.base_pos[1] + (who.base_height_box / 2))
        newpos = who.rotation_xy(who.base_pos, newpos, who.radians_angle)  # new unit pos (back)
        base_pos = pygame.Vector2(who.base_pos[0], who.base_pos[1] - (who.base_height_box / 2))
        who.base_pos = who.rotation_xy(who.base_pos, base_pos, who.radians_angle)  # new position for original unit (front)
        who.base_height_box /= 2

    else:  # split by column
        newarmysubunit = np.array_split(who.subunit_list, 2, axis=1)[1]
        who.subunit_list = np.array_split(who.subunit_list, 2, axis=1)[0]
        newpos = pygame.Vector2(who.base_pos[0] + (who.base_width_box / 3.3), who.base_pos[1])  # 3.3 because 2 make new unit position overlap
        newpos = who.rotation_xy(who.base_pos, newpos, who.radians_angle)  # new unit pos (right)
        base_pos = pygame.Vector2(who.base_pos[0] - (who.base_width_box / 2), who.base_pos[1])
        who.base_pos = who.rotation_xy(who.base_pos, base_pos, who.radians_angle)  # new position for original unit (left)
        who.base_width_box /= 2
        frontpos = (who.base_pos[0], (who.base_pos[1] - who.base_height_box))  # find new front position of unit
        who.front_pos = who.rotation_xy(who.base_pos, frontpos, who.radians_angle)
        who.set_target(who.front_pos)

    if who.leader[
        1].subunit.game_id not in newarmysubunit.flat:  # move the left sub-general leader subunit if it not in new one
        who.subunit_list, newarmysubunit, newposition = move_leader_subunit(who.leader[1], who.subunit_list,
                                                                            newarmysubunit)
        who.leader[1].subunit_pos = newposition[0] * newposition[1]
    who.leader[1].subunit.unit_leader = True  # make the sub-unit of this leader a gamestart leader sub-unit

    alreadypick = []
    for this_leader in (who.leader[0], who.leader[2], who.leader[3]):  # move other leader subunit to original one if they are in new one
        if this_leader.subunit.game_id not in who.subunit_list:
            newarmysubunit, who.subunit_list, newposition = move_leader_subunit(this_leader, newarmysubunit,
                                                                                who.subunit_list, alreadypick)
            this_leader.subunit_pos = newposition[0] * newposition[1]
            alreadypick.append(newposition)

    newleader = [who.leader[1], leader.Leader(1, 0, 1, who, battle.leader_stat), leader.Leader(1, 0, 2, who, battle.leader_stat),
                 leader.Leader(1, 0, 3, who, battle.leader_stat)]  # create new leader list for new unit

    who.subunit_position_list = []

    width, height = 0, 0
    subunitnum = 0  # Number of subunit based on the position in row and column
    for this_subunit in who.subunit_list.flat:
        width += who.image_size[0]
        who.subunit_position_list.append((width, height))
        subunitnum += 1
        if subunitnum >= len(who.subunit_list[0]):  # Reach the last subunit in the row, go to the next one
            width = 0
            height += who.image_size[1]
            subunitnum = 0

    # v Sort so the new leader subunit position match what set before
    subunitsprite = [this_subunit for this_subunit in who.subunit_sprite if
                     this_subunit.game_id in newarmysubunit.flat]  # new list of sprite not sorted yet
    new_subunit_sprite = []
    for thisid in newarmysubunit.flat:
        for this_subunit in subunitsprite:
            if thisid == this_subunit.game_id:
                new_subunit_sprite.append(this_subunit)

    subunitsprite = [this_subunit for this_subunit in who.subunit_sprite if
                     this_subunit.game_id in who.subunit_list.flat]
    who.subunit_sprite = []
    for thisid in who.subunit_list.flat:
        for this_subunit in subunitsprite:
            if thisid == this_subunit.game_id:
                who.subunit_sprite.append(this_subunit)
    # ^ End sort

    # v Reset position of sub-unit in inspect_ui for both old and new unit
    for sprite in (who.subunit_sprite, new_subunit_sprite):
        width, height = 0, 0
        subunitnum = 0
        for this_subunit in sprite:
            width += battle.icon_sprite_width

            if subunitnum >= len(who.subunit_list[0]):
                width = 0
                width += battle.icon_sprite_width
                height += battle.icon_sprite_height
                subunitnum = 0

            this_subunit.inspect_pos = (width + battle.inspect_ui_pos[0], height + battle.inspect_ui_pos[1])
            this_subunit.rect = this_subunit.image.get_rect(topleft=this_subunit.inspect_pos)
            this_subunit.pos = pygame.Vector2(this_subunit.rect.centerx, this_subunit.rect.centery)
            subunitnum += 1
    # ^ End reset position

    # v Change the original unit stat and sprite
    originalleader = [who.leader[0], who.leader[2], who.leader[3], leader.Leader(1, 0, 3, who, battle.leader_stat)]
    for index, this_leader in enumerate(originalleader):  # Also change army position of all leader in that unit
        this_leader.army_position = index  # Change army position to new one
        this_leader.img_position = this_leader.base_img_position[this_leader.army_position]
        this_leader.rect = this_leader.image.get_rect(center=this_leader.img_position)
    teamcommander = who.team_commander
    who.team_commander = teamcommander
    who.leader = originalleader

    add_new_unit(battle, who, False)
    # ^ End change original unit

    # v start making new unit
    if who.team == 1:
        whosearmy = battle.team1_unit
    else:
        whosearmy = battle.team2_unit
    newgameid = battle.all_unit_list[-1].game_id + 1

    newunit = unit.Unit(start_pos=newpos, gameid=newgameid, squadlist=newarmysubunit, colour=who.colour,
                        control=who.control, coa=who.coa_list, commander=False, startangle=who.angle, team=who.team)

    whosearmy.add(newunit)
    newunit.team_commander = teamcommander
    newunit.leader = newleader
    newunit.subunit_sprite = new_subunit_sprite

    for this_subunit in newunit.subunit_sprite:
        this_subunit.unit = newunit

    for index, this_leader in enumerate(newunit.leader):  # Change army position of all leader in new unit
        this_leader.unit = newunit  # Set leader unit to new one
        this_leader.army_position = index  # Change army position to new one
        this_leader.img_position = this_leader.base_img_position[this_leader.army_position]  # Change image pos
        this_leader.rect = this_leader.image.get_rect(center=this_leader.img_position)
        this_leader.poschangestat(this_leader)  # Change stat based on new army position

    add_new_unit(battle, newunit)

    # ^ End making new unit


# Other scripts

def playgif(imageset, framespeed=100):
    """framespeed in millisecond"""
    animation = {}
    frames = ["image1.png", "image2.png"]
