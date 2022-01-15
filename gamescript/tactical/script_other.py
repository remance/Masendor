import math
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

    screen_rect = game.screen_rect
    from gamescript import battleui, uniteditor, rangeattack, unit, subunit

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
    effect_images = load_images(game.main_dir, ["sprite", "effect"], load_order=False)
    # images = []
    # for images in imgsold:
    # x, y = images.get_width(), images.get_height()
    # images = pygame.transform.scale(images, (int(x ), int(y / 2)))
    # images.append(images)
    rangeattack.RangeArrow.images = [effect_images["arrow.png"]]
    # ^ End self effect

    ui_image = load_images(game.main_dir, ["tactical", "ui", "battle_ui"], load_order=False)
    icon_image = load_images(game.main_dir, ["tactical", "ui", "battle_ui", "commandbar_icon"], load_order=False)
    # Army select list ui
    game.unit_selector = battleui.ArmySelect((0, 0), ui_image["unit_select_box.png"])
    game.time_ui.change_pos((game.unit_selector.rect.topright), game.time_number)
    game.battle_ui.add(game.unit_selector)
    game.select_scroll = battleui.UIScroller(game.unit_selector.rect.topright, ui_image["unit_select_box.png"].get_height(),
                                             game.unit_selector.max_row_show)  # scroller for unit select ui

    game.command_ui = battleui.GameUI(image=ui_image["command_box.png"], icon=icon_image,
                                      ui_type="commandbar")  # Left top command ui with leader and unit behavious button
    game.command_ui.change_pos((ui_image["command_box.png"].get_size()[0] / 2,
                                       (ui_image["command_box.png"].get_size()[1] / 2) + game.unit_selector.image.get_height()))
    game.game_ui.add(game.command_ui)

    # Load all image of ui and icon from folder
    icon_image = load_images(game.main_dir, ["ui", "battle_ui", "topbar_icon"], load_order=False)

    game.col_split_button = battleui.UIButton((game.command_ui.pos[0] - 115, game.command_ui.pos[1] + 26), ui_image["colsplit_button.png"], 0)  # unit split by column button
    game.row_split_button = battleui.UIButton((game.command_ui.pos[0] - 115, game.command_ui.pos[1] + 56), ui_image["rowsplit_button.png"], 1)  # unit split by row button
    game.button_ui.add(game.col_split_button)
    game.button_ui.add(game.row_split_button)

    game.decimation_button = battleui.UIButton((game.command_ui.pos[0] + 100, game.command_ui.pos[1] + 56), ui_image["decimation.png"], 1)

    # Right top bar ui that show rough information of selected battalions
    game.unitstat_ui = battleui.GameUI(image=ui_image["topbar.png"], icon=icon_image, ui_type="topbar")
    game.unitstat_ui.change_pos((screen_rect.width - ui_image["topbar.png"].get_size()[0] / 2, ui_image["topbar.png"].get_size()[1] / 2))
    game.game_ui.add(game.unitstat_ui)
    game.unitstat_ui.unit_state_text = game.state_text

    game.inspect_ui_pos = [game.unitstat_ui.rect.bottomleft[0] - game.sprite_width / 1.25,
                           game.unitstat_ui.rect.bottomleft[1] - game.sprite_height / 3]

    # Subunit information card ui
    game.inspect_ui = battleui.GameUI(image=ui_image["army_inspect.png"], icon="", ui_type="unitbox")  # inspect ui that show subnit in selected unit
    game.inspect_ui.change_pos((screen_rect.width - ui_image["army_inspect.png"].get_size()[0] / 2, ui_image["topbar.png"].get_size()[1] * 4))
    game.game_ui.add(game.inspect_ui)
    # v Subunit shown in inspect ui
    width, height = game.inspect_ui_pos[0], game.inspect_ui_pos[1]
    sub_unit_number = 0  # Number of subunit based on the position in row and column
    imgsize = (game.sprite_width, game.sprite_height)
    game.inspect_subunit = []
    for this_subunit in list(range(0, 64)):
        width += imgsize[0]
        game.inspect_subunit.append(battleui.InspectSubunit((width, height)))
        sub_unit_number += 1
        if sub_unit_number == 8:  # Reach the last subunit in the row, go to the next one
            width = game.inspect_ui_pos[0]
            height += imgsize[1]
            sub_unit_number = 0
    # ^ End subunit shown

    game.troop_card_ui.change_pos((screen_rect.width - game.troop_card_ui.image.get_size()[0] / 2,
                              (game.unitstat_ui.image.get_size()[1] * 2.5) + game.troop_card_ui.image.get_size()[1]))

    # Behaviour button that once click switch to other mode for subunit behaviour
    skill_condition_button = [ui_image["skillcond_0.png"], ui_image["skillcond_1.png"], ui_image["skillcond_2.png"], ui_image["skillcond_3.png"]]
    shoot_condition_button = [ui_image["fire_0.png"], ui_image["fire_1.png"]]
    behaviour_button = [ui_image["hold_0.png"], ui_image["hold_1.png"], ui_image["hold_2.png"]]
    range_condition_button = [ui_image["minrange_0.png"], ui_image["minrange_1.png"]]
    arc_condition_button = [ui_image["arc_0.png"], ui_image["arc_1.png"], ui_image["arc_2.png"]]
    run_condition_button = [ui_image["runtoggle_0.png"], ui_image["runtoggle_1.png"]]
    melee_condition_button = [ui_image["meleeform_0.png"], ui_image["meleeform_1.png"], ui_image["meleeform_2.png"]]
    game.switch_button = [battleui.SwitchButton((game.command_ui.pos[0] - 40, game.command_ui.pos[1] + 96), skill_condition_button),  # skill condition button
                          battleui.SwitchButton((game.command_ui.pos[0] - 80, game.command_ui.pos[1] + 96), shoot_condition_button),  # fire at will button
                          battleui.SwitchButton((game.command_ui.pos[0], game.command_ui.pos[1] + 96), behaviour_button),  # behaviour button
                          battleui.SwitchButton((game.command_ui.pos[0] + 40, game.command_ui.pos[1] + 96), range_condition_button),  # shoot range button
                          battleui.SwitchButton((game.command_ui.pos[0] - 125, game.command_ui.pos[1] + 96), arc_condition_button),  # arcshot button
                          battleui.SwitchButton((game.command_ui.pos[0] + 80, game.command_ui.pos[1] + 96), run_condition_button),  # toggle run button
                          battleui.SwitchButton((game.command_ui.pos[0] + 120, game.command_ui.pos[1] + 96), melee_condition_button)]  # toggle melee mode

    game.inspect_button = battleui.UIButton((game.unitstat_ui.pos[0] - 206, game.unitstat_ui.pos[1] - 1), ui_image["army_inspect_button.png"], 1)  # unit inspect open/close button
    game.button_ui.add(game.inspect_button)

    game.battle_ui.add(game.log_scroll, game.select_scroll)

    game.inspect_selected_border = battleui.SelectedSquad((15000, 15000))  # yellow border on selected subnit in inspect ui
    game.main_ui.remove(game.inspect_selected_border)  # remove subnit border sprite from gamestart menu drawer
    # ^ End self ui

# Battle Start related gamescript


# Battle related gamescript

def set_rotate(self, set_target=None):
    """set base_target and new angle for sprite rotation"""
    if set_target is None:  # For auto chase rotate
        my_radians = math.atan2(self.base_target[1] - self.base_pos[1], self.base_target[0] - self.base_pos[0])
    else:  # Command move or rotate
        my_radians = math.atan2(set_target[1] - self.base_pos[1], set_target[0] - self.base_pos[0])
    new_angle = math.degrees(my_radians)

    # """upper left -"""
    if -180 <= new_angle <= -90:
        new_angle = -new_angle - 90

    # """upper right +"""
    elif -90 < new_angle < 0:
        new_angle = (-new_angle) - 90

    # """lower right -"""
    elif 0 <= new_angle <= 90:
        new_angle = -(new_angle + 90)

    # """lower left +"""
    elif 90 < new_angle <= 180:
        new_angle = 270 - new_angle

    return round(new_angle)


def loss_cal(attacker, defender, hit, defence, dmgtype, defside=None):
    """Calculate dmg, type 0 is melee attack and will use attacker subunit stat,
    type that is not 0 will use the type object stat instead (mostly used for range attack)"""
    who = attacker
    target = defender

    height_advantage = who.height - target.height
    if dmgtype != 0:
        height_advantage = int(height_advantage / 2)  # Range attack use less height advantage
    hit += height_advantage

    if defence < 0 or who.ignore_def:  # Ignore def trait
        defence = 0

    hit_chance = hit - defence
    if hit_chance < 0:
        hit_chance = 0
    elif hit_chance > 80:  # Critical hit
        hit_chance *= who.crit_effect  # modify with crit effect further
        if hit_chance > 200:
            hit_chance = 200
    else:  # infinity number can cause nan value
        hit_chance = 200

    combat_score = round(hit_chance / 100, 1)
    if combat_score == 0 and random.randint(0, 10) > 9:  # Final chance to not miss
        combat_score = 0.1

    if combat_score > 0:
        leader_dmg_bonus = 0
        if who.leader is not None:
            leader_dmg_bonus = who.leader.combat  # Get extra dmg from leader combat stat

        if dmgtype == 0:  # Melee melee_dmg
            dmg = random.uniform(who.melee_dmg[0], who.melee_dmg[1])
            if who.charge_skill in who.skill_effect:  # Include charge in melee_dmg if attacking
                if who.ignore_chargedef is False:  # Ignore charge defence if have ignore trait
                    side_cal = battlesidecal[defside]
                    if target.fulldef or target.temp_full_def:  # defence all side
                        side_cal = 1
                    dmg = dmg + ((who.charge - (target.charge_def * side_cal)) * 2)
                    if (target.charge_def * side_cal) >= who.charge / 2:
                        who.charge_momentum = 1  # charge get stopped by charge def
                    else:
                        who.charge_momentum -= (target.charge_def * side_cal) / who.charge
                else:
                    dmg = dmg + (who.charge * 2)
                    who.charge_momentum -= 1 / who.charge

            if target.charge_skill in target.skill_effect:  # Also include charge_def in melee_dmg if enemy charging
                if target.ignore_chargedef is False:
                    charge_def_cal = who.charge_def - target.charge
                    if charge_def_cal < 0:
                        charge_def_cal = 0
                    dmg = dmg + (charge_def_cal * 2)  # if charge def is higher than enemy charge then deal back additional melee_dmg
            elif who.charge_skill not in who.skill_effect:  # not charging or defend from charge, use attack speed roll
                dmg += sum([random.uniform(who.melee_dmg[0], who.melee_dmg[1]) for x in range(who.melee_speed)])

            penetrate = who.melee_penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmg * penetrate * combat_score

        else:  # Range Damage
            penetrate = dmgtype.penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmgtype.dmg * penetrate * combat_score

        leader_dmg = dmg
        unit_dmg = (dmg * who.troop_number) + leader_dmg_bonus  # dmg on subunit is dmg multiply by troop number with addition from leader combat
        if (who.anti_inf and target.subunit_type in (1, 2)) or (who.anti_cav and target.subunit_type in (4, 5, 6, 7)):  # Anti trait dmg bonus
            unit_dmg = unit_dmg * 1.25

        morale_dmg = dmg / 50

        # Damage cannot be negative (it would heal instead), same for morale and leader dmg
        if unit_dmg < 0:
            unit_dmg = 0
        if leader_dmg < 0:
            leader_dmg = 0
        if morale_dmg < 0:
            morale_dmg = 0
    else:  # complete miss
        unit_dmg = 0
        leader_dmg = 0
        morale_dmg = 0

    return unit_dmg, morale_dmg, leader_dmg


def apply_status_to_enemy(status_list, inflict_status, receiver, attacker_side, receiver_side):
    """apply aoe status effect to enemy subunits"""
    for status in inflict_status.items():
        if status[1] == 1 and attacker_side == 0:  # only front enemy
            receiver.status_effect[status[0]] = status_list[status[0]].copy()
        elif status[1] == 2:  # aoe effect to side enemy
            receiver.status_effect[status[0]] = status_list[status[0]].copy()
            if status[1] == 3:  # apply to corner enemy subunit (left and right of self front enemy subunit)
                corner_enemy_apply = receiver.nearby_subunit_list[0:2]
                if receiver_side in (1, 2):  # attack on left/right side means corner enemy would be from front and rear side of the enemy
                    corner_enemy_apply = [receiver.nearby_subunit_list[2], receiver.nearby_subunit_list[5]]
                for this_subunit in corner_enemy_apply:
                    if this_subunit != 0:
                        this_subunit.status_effect[status[0]] = status_list[status[0]].copy()
        elif status[1] == 3:  # whole unit aoe
            for this_subunit in receiver.unit.subunit_sprite:
                if this_subunit.state != 100:
                    this_subunit.status_effect[status[0]] = status_list[status[0]].copy()


def complex_dmg_cal(attacker, receiver, dmg, morale_dmg, leader_dmg, dmg_effect, timer_mod):
    final_dmg = round(dmg * dmg_effect * timer_mod)
    final_morale_dmg = round(morale_dmg * dmg_effect * timer_mod)
    if final_dmg > receiver.unit_health:  # dmg cannot be higher than remaining health
        final_dmg = receiver.unit_health

    receiver.unit_health -= final_dmg
    health_check = 0.1
    if receiver.max_health != infinity:
        health_check = 1 - (receiver.unit_health / receiver.max_health)
    receiver.base_morale -= (final_morale_dmg + attacker.bonus_morale_dmg) * receiver.mental * health_check
    receiver.stamina -= attacker.bonus_stamina_dmg

    # v Add red corner to indicate combat
    if receiver.red_border is False:
        receiver.block.blit(receiver.images[11], receiver.corner_image_rect)
        receiver.red_border = True
    # ^ End red corner

    if attacker.elem_melee not in (0, 5):  # apply element effect if atk has element, except 0 physical, 5 magic
        receiver.elem_count[attacker.elem_melee - 1] += round(final_dmg * (100 - receiver.elem_res[attacker.elem_melee - 1] / 100))

    attacker.base_morale += round((final_morale_dmg / 5))  # recover some morale when deal morale dmg to enemy

    if receiver.leader is not None and receiver.leader.health > 0 and random.randint(0, 10) > 9:  # dmg on subunit leader, only 10% chance
        final_leader_dmg = round(leader_dmg - (leader_dmg * receiver.leader.combat / 101) * timer_mod)
        if final_leader_dmg > receiver.leader.health:
            final_leader_dmg = receiver.leader.health
        receiver.leader.health -= final_leader_dmg


def dmg_cal(attacker, target, attacker_side, target_side, status_list, combat_timer):
    """base_target position 0 = Front, 1 = Side, 3 = Rear, attacker_side and target_side is the side attacking and defending respectively"""
    who_luck = random.randint(-50, 50)  # attacker luck
    target_luck = random.randint(-50, 50)  # defender luck
    who_mod = battlesidecal[attacker_side]  # attacker attack side modifier

    """34 battlemaster fulldef or 91 allrounddef status = no flanked penalty"""
    if attacker.fulldef or 91 in attacker.status_effect:
        who_mod = 1
    target_percent = battlesidecal[target_side]  # defender defend side

    if target.fulldef or 91 in target.status_effect:
        target_percent = 1

    dmg_effect = attacker.front_dmg_effect
    target_dmg_effect = target.front_dmg_effect

    if attacker_side != 0 and who_mod != 1:  # if attack or defend from side will use discipline to help reduce penalty a bit
        who_mod = battlesidecal[attacker_side] + (attacker.discipline / 300)
        dmg_effect = attacker.side_dmg_effect  # use side dmg effect as some skill boost only front dmg
        if who_mod > 1:
            who_mod = 1

    if target_side != 0 and target_percent != 1:  # same for the base_target defender
        target_percent = battlesidecal[target_side] + (target.discipline / 300)
        target_dmg_effect = target.side_dmg_effect
        if target_percent > 1:
            target_percent = 1

    who_hit = float(attacker.attack * who_mod) + who_luck
    who_defence = float(attacker.melee_def * who_mod) + who_luck
    target_hit = float(attacker.attack * target_percent) + target_luck
    target_defence = float(target.melee_def * target_percent) + target_luck

    """33 backstabber ignore def when attack rear side, 55 Oblivious To Unexpected can't defend from rear at all"""
    if (attacker.backstab and target_side == 2) or (target.oblivious and target_side == 2) or (
            target.flanker and attacker_side in (1, 3)):  # Apply only for attacker
        target_defence = 0

    who_dmg, who_morale_dmg, who_leader_dmg = loss_cal(attacker, target, who_hit, target_defence, 0, target_side)  # get dmg by attacker
    target_dmg, target_morale_dmg, target_leader_dmg = loss_cal(target, attacker, target_hit, who_defence, 0, attacker_side)  # get dmg by defender

    timer_mod = combat_timer / 0.5  # Since the update happen anytime more than 0.5 second, high speed that pass by longer than x1 speed will become inconsistent
    complex_dmg_cal(attacker, target, who_dmg, who_morale_dmg, who_leader_dmg, dmg_effect, timer_mod)  # Inflict dmg to defender
    complex_dmg_cal(target, attacker, target_dmg, target_morale_dmg, target_leader_dmg, target_dmg_effect, timer_mod)  # Inflict dmg to attacker

    # v Attack corner (side) of self with aoe attack
    if attacker.corner_atk:
        loop_list = [target.nearby_subunit_list[2], target.nearby_subunit_list[5]]  # Side attack get (2) front and (5) rear nearby subunit
        if target_side in (0, 2):
            loop_list = target.nearby_subunit_list[0:2]  # Front/rear attack get (0) left and (1) right nearby subunit
        for this_subunit in loop_list:
            if this_subunit != 0 and this_subunit.state != 100:
                target_hit, target_defence = float(attacker.attack * target_percent) + target_luck, float(
                    this_subunit.melee_def * target_percent) + target_luck
                who_dmg, who_morale_dmg = loss_cal(attacker, this_subunit, who_hit, target_defence, 0)
                complex_dmg_cal(attacker, this_subunit, who_dmg, who_morale_dmg, who_leader_dmg, dmg_effect, timer_mod)
    # ^ End attack corner

    # v inflict status based on aoe 1 = front only 2 = all 4 side, 3 corner enemy subunit, 4 entire unit
    if attacker.inflict_status != {}:
        apply_status_to_enemy(status_list, attacker.inflict_status, target, attacker_side, target_side)
    if target.inflict_status != {}:
        apply_status_to_enemy(status_list, target.inflict_status, attacker, target_side, attacker_side)
    # ^ End inflict status


def add_new_unit(gamebattle, who, addunitlist=True):
    from gamescript import unit
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


def move_leader_subunit(this_leader, old_army_subunit, new_army_subunit, already_pick=()):
    """old_army_subunit is subunit_list list that the subunit currently in and need to be move out to the new one (new_army_subunit),
    already_pick is list of position need to be skipped"""
    replace = [np.where(old_army_subunit == this_leader.subunit.game_id)[0][0],
               np.where(old_army_subunit == this_leader.subunit.game_id)[1][0]]  # grab old array position of subunit
    new_row = int((len(new_army_subunit) - 1) / 2)  # set up new row subunit will be place in at the middle at the start
    new_place = int((len(new_army_subunit[new_row]) - 1) / 2)  # setup new column position
    place_done = False  # finish finding slot to place yet

    while place_done is False:
        if this_leader.subunit.unit.subunit_list.flat[new_row * new_place] != 0:
            for this_subunit in this_leader.subunit.unit.subunit_sprite:
                if this_subunit.game_id == this_leader.subunit.unit.subunit_list.flat[new_row * new_place]:
                    if this_subunit.leader is not None or (new_row, new_place) in already_pick:
                        new_place += 1
                        if new_place > len(new_army_subunit[new_row]) - 1:  # find new column
                            new_place = 0
                        elif new_place == int(
                                len(new_army_subunit[new_row]) / 2):  # find in new row when loop back to the first one
                            new_row += 1
                        place_done = False
                    else:  # found slot to replace
                        place_done = True
                        break
        else:  # fill in the subunit if the slot is empty
            place_done = True

    old_army_subunit[replace[0]][replace[1]] = new_army_subunit[new_row][new_place]
    new_army_subunit[new_row][new_place] = this_leader.subunit.game_id
    new_position = (new_place, new_row)
    return old_army_subunit, new_army_subunit, new_position


def split_unit(battle, who, how):
    """split unit either by row or column into two seperate unit"""  # TODO check split when moving
    from gamescript import unit, leader

    if how == 0:  # split by row
        new_army_subunit = np.array_split(who.subunit_list, 2)[1]
        who.subunit_list = np.array_split(who.subunit_list, 2)[0]
        new_pos = pygame.Vector2(who.base_pos[0], who.base_pos[1] + (who.base_height_box / 2))
        new_pos = who.rotation_xy(who.base_pos, new_pos, who.radians_angle)  # new unit pos (back)
        base_pos = pygame.Vector2(who.base_pos[0], who.base_pos[1] - (who.base_height_box / 2))
        who.base_pos = who.rotation_xy(who.base_pos, base_pos, who.radians_angle)  # new position for original unit (front)
        who.base_height_box /= 2

    else:  # split by column
        new_army_subunit = np.array_split(who.subunit_list, 2, axis=1)[1]
        who.subunit_list = np.array_split(who.subunit_list, 2, axis=1)[0]
        new_pos = pygame.Vector2(who.base_pos[0] + (who.base_width_box / 3.3), who.base_pos[1])  # 3.3 because 2 make new unit position overlap
        new_pos = who.rotation_xy(who.base_pos, new_pos, who.radians_angle)  # new unit pos (right)
        base_pos = pygame.Vector2(who.base_pos[0] - (who.base_width_box / 2), who.base_pos[1])
        who.base_pos = who.rotation_xy(who.base_pos, base_pos, who.radians_angle)  # new position for original unit (left)
        who.base_width_box /= 2
        frontpos = (who.base_pos[0], (who.base_pos[1] - who.base_height_box))  # find new front position of unit
        who.front_pos = who.rotation_xy(who.base_pos, frontpos, who.radians_angle)
        who.set_target(who.front_pos)

    if who.leader[
        1].subunit.game_id not in new_army_subunit.flat:  # move the left sub-general leader subunit if it not in new one
        who.subunit_list, new_army_subunit, new_position = move_leader_subunit(who.leader[1], who.subunit_list, new_army_subunit)
        who.leader[1].subunit_pos = new_position[0] * new_position[1]
    who.leader[1].subunit.unit_leader = True  # make the sub-unit of this leader a gamestart leader sub-unit

    already_pick = []
    for this_leader in (who.leader[0], who.leader[2], who.leader[3]):  # move other leader subunit to original one if they are in new one
        if this_leader.subunit.game_id not in who.subunit_list:
            new_army_subunit, who.subunit_list, new_position = move_leader_subunit(this_leader, new_army_subunit,
                                                                                who.subunit_list, already_pick)
            this_leader.subunit_pos = new_position[0] * new_position[1]
            already_pick.append(new_position)

    new_leader = [who.leader[1], leader.Leader(1, 0, 1, who, battle.leader_stat), leader.Leader(1, 0, 2, who, battle.leader_stat),
                 leader.Leader(1, 0, 3, who, battle.leader_stat)]  # create new leader list for new unit

    who.subunit_position_list = []

    width, height = 0, 0
    subunit_number = 0  # Number of subunit based on the position in row and column
    for this_subunit in who.subunit_list.flat:
        width += who.image_size[0]
        who.subunit_position_list.append((width, height))
        subunit_number += 1
        if subunit_number >= len(who.subunit_list[0]):  # Reach the last subunit in the row, go to the next one
            width = 0
            height += who.image_size[1]
            subunit_number = 0

    # v Sort so the new leader subunit position match what set before
    subunit_sprite = [this_subunit for this_subunit in who.subunit_sprite if
                     this_subunit.game_id in new_army_subunit.flat]  # new list of sprite not sorted yet
    new_subunit_sprite = []
    for this_id in new_army_subunit.flat:
        for this_subunit in subunit_sprite:
            if this_id == this_subunit.game_id:
                new_subunit_sprite.append(this_subunit)

    subunit_sprite = [this_subunit for this_subunit in who.subunit_sprite if
                     this_subunit.game_id in who.subunit_list.flat]
    who.subunit_sprite = []
    for this_id in who.subunit_list.flat:
        for this_subunit in subunit_sprite:
            if this_id == this_subunit.game_id:
                who.subunit_sprite.append(this_subunit)
    # ^ End sort

    # v Reset position of subunit in inspect_ui for both old and new unit
    for sprite in (who.subunit_sprite, new_subunit_sprite):
        width, height = 0, 0
        subunit_number = 0
        for this_subunit in sprite:
            width += battle.sprite_width

            if subunit_number >= len(who.subunit_list[0]):
                width = 0
                width += battle.sprite_width
                height += battle.sprite_height
                subunit_number = 0

            this_subunit.inspect_pos = (width + battle.inspect_ui_pos[0], height + battle.inspect_ui_pos[1])
            this_subunit.rect = this_subunit.image.get_rect(topleft=this_subunit.inspect_pos)
            this_subunit.pos = pygame.Vector2(this_subunit.rect.centerx, this_subunit.rect.centery)
            subunit_number += 1
    # ^ End reset position

    # v Change the original unit stat and sprite
    original_leader = [who.leader[0], who.leader[2], who.leader[3], leader.Leader(1, 0, 3, who, battle.leader_stat)]
    for index, this_leader in enumerate(original_leader):  # Also change army position of all leader in that unit
        this_leader.army_position = index  # Change army position to new one
        this_leader.img_position = this_leader.base_img_position[this_leader.army_position]
        this_leader.rect = this_leader.image.get_rect(center=this_leader.img_position)
    team_commander = who.team_commander
    who.team_commander = team_commander
    who.leader = original_leader

    add_new_unit(battle, who, False)
    # ^ End change original unit

    # v start making new unit
    if who.team == 1:
        whose_army = battle.team1_unit
    else:
        whose_army = battle.team2_unit
    new_game_id = battle.all_unit_list[-1].game_id + 1

    new_unit = unit.Unit(start_pos=new_pos, gameid=new_game_id, squadlist=new_army_subunit, colour=who.colour,
                         control=who.control, coa=who.coa_list, commander=False, startangle=who.angle, team=who.team)

    whose_army.add(new_unit)
    new_unit.team_commander = team_commander
    new_unit.leader = new_leader
    new_unit.subunit_sprite = new_subunit_sprite

    for this_subunit in new_unit.subunit_sprite:
        this_subunit.unit = new_unit

    for index, this_leader in enumerate(new_unit.leader):  # Change army position of all leader in new unit
        this_leader.unit = new_unit  # Set leader unit to new one
        this_leader.army_position = index  # Change army position to new one
        this_leader.img_position = this_leader.base_img_position[this_leader.army_position]  # Change image pos
        this_leader.rect = this_leader.image.get_rect(center=this_leader.img_position)
        this_leader.poschangestat(this_leader)  # Change stat based on new army position

    add_new_unit(battle, new_unit)

    # ^ End making new unit
