import random
import pygame
import numpy as np

battle_side_cal = (1, 0.5, 0.1, 0.5)  # battle_side_cal is for melee combat side modifier
infinity = float("inf")


def change_leader(self, event):
    """Leader is subunit in arcode mode, so can't change to other subunit"""
    pass


def swap_equipment(self, new_weapon):
    """Swap weapon, reset base stat"""
    self.base_melee_def = self.original_melee_def
    self.base_range_def = self.original_range_def
    self.skill = self.original_skill
    self.trait = self.original_trait

    self.base_melee_def += self.weapon_data.weapon_data[new_weapon]["Defense"]
    self.base_range_def += self.weapon_data.weapon_data[new_weapon]["Defense"]

    self.skill += self.weapon_data.weapon_data[new_weapon]["Skill"]
    self.trait += self.weapon_data.weapon_data[new_weapon]["Trait"]

    self.trait = list(set([trait for trait in self.trait if trait != 0]))  # remove empty and duplicate traits
    if len(self.trait) > 0:
        self.trait = {x: self.troop_data.trait_list[x] for x in self.trait if
                      x in self.troop_data.trait_list}  # Any trait not available in ruleset will be ignored
        self.add_trait()

    self.skill = {x: self.troop_data.skill_list[x].copy() for x in self.skill if
                  x != 0 and x in self.troop_data.skill_list}  # grab skill stat into dict
    for skill in list(self.skill.keys()):  # remove skill if class mismatch
        skill_troop_cond = self.skill[skill]["Troop Type"]
        if skill_troop_cond == 0 or (self.subunit_type == 2 and skill_troop_cond == 2) or (self.subunit_type != 2 and skill_troop_cond != 2):
            pass
        else:
            self.skill.pop(skill)


def find_shooting_target(self, unit_state):
    """get nearby enemy base_target from list if not targeting anything yet"""
    self.attack_pos = list(self.unit.near_target.values())[0]  # replace attack_pos with enemy unit pos
    self.attack_target = list(self.unit.near_target.keys())[0]  # replace attack_target with enemy unit id
    for shoot_range in self.shoot_range:
        if shoot_range >= self.attack_pos.distance_to(self.base_pos):
            self.state = 11
            if unit_state in (1, 3, 5):  # Walk and shoot
                self.state = 12
            elif unit_state in (2, 4, 6):  # Run and shoot
                self.state = 13


def attack_logic(self, dt, combat_timer, parent_state):
    from gamescript import rangeattack

    collide_list = []
    self.melee_target = None
    if self.enemy_front != [] or self.enemy_side != []:  # Check if in combat or not with collision
        collide_list = self.enemy_front + self.enemy_side
        for subunit in collide_list:
            if self.state not in (96, 98, 99):
                self.state = 10
                self.melee_target = subunit
                if self.enemy_front == []:  # no enemy in front try to rotate to enemy at side
                    # self.base_target = self.melee_target.base_pos
                    self.new_angle = self.set_rotate(self.melee_target.base_pos)
            else:  # no way to retreat, Fight to the death
                if self.enemy_front != [] and self.enemy_side != []:  # if both front and any side got attacked
                    if 9 not in self.status_effect:
                        self.status_effect[9] = self.status_list[9].copy()  # fight to the death status
            if parent_state not in (10, 96, 98, 99):
                parent_state = 10
                self.unit.state = 10
            if self.melee_target is not None:
                self.unit.attack_target = self.melee_target.unit
            break
    elif self.unit_leader is False:  # not in fight anymore, rotate and move back to original position
        self.close_target = None
        if self in self.battle.combat_path_queue:
            self.battle.combat_path_queue.remove(self)

        self.attack_target = None
        self.base_target = self.command_target
        self.new_angle = self.unit.angle
        self.state = 0
        if self.angle != self.unit.angle:  # reset angle
            self.new_angle = self.set_rotate()
            self.new_angle = self.unit.angle
    # TODO fix range attack later
    # if self.state != 10 and self.magazine_left > 0 and self.unit.fire_at_will == 0 and (self.arc_shot or self.frontline) and \
    #         self.charge_momentum == 1:  # Range attack when unit in melee state with arc_shot
    #     self.state = 11
    #     if self.unit.near_target != {} and (self.attack_target is None or self.attack_pos == 0):
    #         self.find_shooting_target(parent_state)
    # ^ End melee check

    # else:  # range attack
    #     if self in self.battle.combat_path_queue:
    #         self.battle.combat_path_queue.remove(self)
    #     self.attack_target = None
    #     self.combat_move_queue = []
    #
    #     # v Range attack function
    #     if parent_state == 11:  # Unit in range attack state
    #         self.state = 0  # Default state at idle
    #         if (self.magazine_left > 0 or self.ammo_now > 0) and self.attack_pos != 0 and \
    #                 self.shoot_range >= self.attack_pos.distance_to(self.base_pos):
    #             self.state = 11  # can shoot if troop have magazine_left and in shoot range, enter range combat state
    #
    #     elif self.magazine_left > 0 and self.unit.fire_at_will == 0 and \
    #             (self.state == 0 or (self.state not in (95, 96, 97, 98, 99) and
    #                                  parent_state in (1, 2, 3, 4, 5, 6) and self.shoot_move)):  # Fire at will
    #         if self.unit.near_target != {} and self.attack_target is None:
    #             self.find_shooting_target(parent_state)  # shoot the nearest target
    #
    # if self.state in (11, 12, 13) and self.magazine_left > 0 and self.ammo_now == 0:  # reloading magazine_left
    #     self.reload_time += dt
    #     if self.reload_time >= self.reload:
    #         self.ammo_now = self.magazine_size
    #         self.magazine_left -= 1
    #         self.reload_time = 0
    #     self.stamina = self.stamina - (dt * 2)  # use stamina while reloading
    # ^ End range attack function

    if combat_timer >= 0.5:  # combat is calculated every 0.5 second in self time
        if self.state == 10:  # if melee combat (engaging anyone on any side)
            collide_list = [subunit for subunit in self.enemy_front]
            for subunit in collide_list:
                angle_check = abs(self.angle - subunit.angle)  # calculate which side arrow hit the subunit
                if angle_check >= 135:  # front
                    hit_side = 0
                elif angle_check >= 45:  # side
                    hit_side = 1
                else:  # rear
                    hit_side = 2
                self.dmg_cal(subunit, 0, hit_side, self.battle.troop_data.status_list, combat_timer)
                self.stamina = self.stamina - (combat_timer * 5)

        elif self.state in (11, 12, 13):  # range combat
            if self.attack_target is not None:  # For fire at will
                if self.attack_target not in self.battle.alive_unit_list:  # enemy dead
                    self.attack_pos = 0  # reset attack_pos to 0
                    self.attack_target = None  # reset attack_target to 0

                    for target, pos in self.unit.near_target.items():  # find other nearby base_target to shoot
                        self.attack_pos = pos
                        self.attack_target = target
                        break  # found new target, break loop
            elif self.attack_target is None:
                self.attack_target = self.unit.attack_target

            if self.ammo_now > 0 and ((self.attack_target is not None and self.attack_target.state != 100) or
                                      (self.attack_target is None and self.attack_pos != 0)) \
                    and (self.arc_shot or (self.arc_shot is False and self.unit.shoot_mode != 1)):
                # can shoot if reload finish and base_target existed and not dead. Non arc_shot cannot shoot if forbid
                # TODO add line of sight for range attack
                rangeattack.RangeArrow(self, self.base_pos.distance_to(self.attack_pos), self.shoot_range, self.zoom)  # Shoot
                self.ammo_now -= 1  # use 1 magazine_left in magazine
            elif self.attack_target is not None and self.attack_target.state == 100:  # if base_target destroyed when it about to shoot
                self.unit.range_combat_check = False
                self.unit.attack_target = 0  # reset range combat check and base_target

    return parent_state, collide_list


def complex_dmg_cal(attacker, defender, hit, defence, dmg_type, def_side=None):
    """Calculate dmg, type 0 is melee attack and will use attacker subunit stat,
    type that is not 0 will use the type object stat instead (mostly used for range attack)"""
    who = attacker
    target = defender

    height_advantage = who.height - target.height
    if dmg_type != 0:
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
        if dmg_type == 0:  # Melee melee_dmg
            dmg = random.uniform(who.melee_dmg[0], who.melee_dmg[1])
            if who.charge_skill in who.skill_effect:  # Include charge in melee_dmg if attacking
                if who.ignore_charge_def is False:  # Ignore charge defence if have ignore trait
                    side_cal = battle_side_cal[def_side]
                    if target.full_def or target.temp_full_def:  # defence all side
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
                if target.ignore_charge_def is False:
                    charge_def_cal = who.charge_def - target.charge
                    if charge_def_cal < 0:
                        charge_def_cal = 0
                    dmg = dmg + (charge_def_cal * 2)  # if charge def is higher than enemy charge then deal back additional melee_dmg
            elif who.charge_skill not in who.skill_effect:  # not charging or defend from charge, use attack speed roll
                dmg += sum([random.uniform(who.melee_dmg[0], who.melee_dmg[1]) for x in range(who.weapon_speed)])

            penetrate = who.melee_penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmg * penetrate * combat_score

        else:  # Range Damage
            penetrate = dmg_type.penetrate / target.armour
            if penetrate > 1:
                penetrate = 1
            dmg = dmg_type.dmg * penetrate * combat_score

        unit_dmg = dmg * who.troop_number  # dmg on subunit is dmg multiply by troop number  # TODO change later
        if (who.anti_inf and target.subunit_type in (1, 2)) or (who.anti_cav and target.subunit_type in (4, 5, 6, 7)):  # Anti trait dmg bonus
            unit_dmg = unit_dmg * 1.25

        morale_dmg = dmg / 50

        # Damage cannot be negative (it would heal instead), same for morale dmg
        if unit_dmg < 0:
            unit_dmg = 0
        if morale_dmg < 0:
            morale_dmg = 0
    else:  # complete miss
        unit_dmg = 0
        morale_dmg = 0

    return unit_dmg, morale_dmg


def loss_cal(attacker, receiver, dmg, morale_dmg, dmg_effect, timer_mod):
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
        receiver.block.blit(receiver.unit_ui_images["ui_squad_combat.png"], receiver.corner_image_rect)
        receiver.red_border = True
    # ^ End red corner

    if attacker.elem_melee not in (0, 5):  # apply element effect if atk has element, except 0 physical, 5 magic
        receiver.elem_count[attacker.elem_melee - 1] += round(final_dmg * (100 - receiver.elem_res[attacker.elem_melee - 1] / 100))

    attacker.base_morale += round((final_morale_dmg / 5))  # recover some morale when deal morale dmg to enemy


def dmg_cal(attacker, target, attacker_side, target_side, status_list, combat_timer):
    """base_target position 0 = Front, 1 = Side, 3 = Rear, attacker_side and target_side is the side attacking and defending respectively"""
    who_luck = random.randint(-50, 50)  # attacker luck
    target_luck = random.randint(-50, 50)  # defender luck
    who_mod = battle_side_cal[attacker_side]  # attacker attack side modifier

    """34 battlemaster full_def or 91 allrounddef status = no flanked penalty"""
    if attacker.full_def or 91 in attacker.status_effect:
        who_mod = 1
    target_percent = battle_side_cal[target_side]  # defender defend side

    if target.full_def or 91 in target.status_effect:
        target_percent = 1

    dmg_effect = attacker.front_dmg_effect
    target_dmg_effect = target.front_dmg_effect

    if attacker_side != 0 and who_mod != 1:  # if attack or defend from side will use discipline to help reduce penalty a bit
        who_mod = battle_side_cal[attacker_side] + (attacker.discipline / 300)
        dmg_effect = attacker.side_dmg_effect  # use side dmg effect as some skill boost only front dmg
        if who_mod > 1:
            who_mod = 1

    if target_side != 0 and target_percent != 1:  # same for the base_target defender
        target_percent = battle_side_cal[target_side] + (target.discipline / 300)
        target_dmg_effect = target.side_dmg_effect
        if target_percent > 1:
            target_percent = 1

    who_hit = float(attacker.melee_attack * who_mod) + who_luck
    target_defence = float(target.melee_def * target_percent) + target_luck

    """backstabber ignore def when attack rear side, Oblivious To Unexpected can't defend from rear at all"""
    if (attacker.backstab and target_side == 2) or (target.oblivious and target_side == 2) or (
            target.flanker and attacker_side in (1, 3)):  # Apply only for attacker
        target_defence = 0

    who_dmg, who_morale_dmg = complex_dmg_cal(attacker, target, who_hit, target_defence, 0, target_side)  # get dmg by attacker

    timer_mod = combat_timer / 0.5  # Since the update happen anytime more than 0.5 second, high speed that pass by longer than x1 speed will become inconsistent
    loss_cal(attacker, target, who_dmg, who_morale_dmg, dmg_effect, timer_mod)  # Inflict dmg to defender

    if target.reflect:
        target_dmg = who_dmg / 10
        target_morale_dmg = who_dmg / 50
        if target.full_reflect:
            target_dmg = who_dmg
            target_morale_dmg = who_dmg / 10
        loss_cal(target, attacker, target_dmg, target_morale_dmg, target_dmg_effect, timer_mod)  # Inflict dmg to attacker

    # v Attack corner (side) of self with aoe attack
    if attacker.corner_atk:
        loop_list = [target.nearby_subunit_list[2], target.nearby_subunit_list[5]]  # Side attack get (2) front and (5) rear nearby subunit
        if target_side in (0, 2):
            loop_list = target.nearby_subunit_list[0:2]  # Front/rear attack get (0) left and (1) right nearby subunit
        for this_subunit in loop_list:
            if this_subunit != 0 and this_subunit.state != 100:
                target_hit, target_defence = float(attacker.melee_attack * target_percent) + target_luck, float(
                    this_subunit.melee_def * target_percent) + target_luck
                who_dmg, who_morale_dmg = complex_dmg_cal(attacker, this_subunit, who_hit, target_defence, 0)
                loss_cal(attacker, this_subunit, who_dmg, who_morale_dmg, dmg_effect, timer_mod)
    # ^ End attack corner

    # Inflict status based on aoe 1 = front only 2 = all 4 side, 3 corner enemy subunit, 4 entire unit
    if attacker.inflict_status != {}:
        apply_status_to_enemy(status_list, attacker.inflict_status, target, attacker_side, target_side)


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
            for this_subunit in receiver.unit.subunits:
                if this_subunit.state != 100:
                    this_subunit.status_effect[status[0]] = status_list[status[0]].copy()


def die(self):
    self.image_original3.blit(self.health_image_list[5], self.health_image_rect)  # blit white hp bar
    self.block_original.blit(self.health_image_rect[5], self.health_block_rect)
    self.zoom_scale()
    self.last_health_state = 0
    self.skill_cooldown = {}  # remove all cooldown
    self.skill_effect = {}  # remove all skill effects

    self.block.blit(self.block_original, self.corner_image_rect)
    self.red_border = True  # to prevent red border appear when dead

    self.unit.dead_change = True

    if self in self.battle.battle_camera:
        self.battle.battle_camera.change_layer(sprite=self, new_layer=1)
    self.battle.alive_subunit_list.remove(self)
    self.unit.subunits.remove(self)

    for subunit in self.unit.subunit_list.flat:  # remove from index array
        if subunit == self.game_id:
            self.unit.subunit_list = np.where(self.unit.subunit_list == self.game_id, 0, self.unit.subunit_list)
            break

    if self.unit_leader:  # leader dead, all subunit enter broken state
        for subunit in self.unit.subunits:
            subunit.state = 99  # Broken state

            corner_list = [[0, subunit.base_pos[1]], [1000, subunit.base_pos[1]], [subunit.base_pos[0], 0],
                           [subunit.base_pos[0], 1000]]
            which_corner = [subunit.base_pos.distance_to(corner_list[0]), subunit.base_pos.distance_to(corner_list[1]),
                            subunit.base_pos.distance_to(corner_list[2]),
                            subunit.base_pos.distance_to(corner_list[3])]  # find the closest map corner to run to
            found_corner = which_corner.index(min(which_corner))
            subunit.base_target = pygame.Vector2(corner_list[found_corner])
            subunit.command_target = subunit.base_target
            subunit.new_angle = subunit.set_rotate()

    self.battle.event_log.add_log([0, str(self.board_pos) + " " + str(self.name)
                                   + " in " + self.unit.leader[0].name
                                   + "'s unit is destroyed"], [3])  # add log to say this subunit is destroyed in subunit tab
