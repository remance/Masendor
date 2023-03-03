from pygame import Vector2

from math import cos, sin, radians
infinity = float("inf")


def cal_loss(self, target, final_dmg, impact, final_morale_dmg, element_effect, hit_angle):
    """
    :param self: Attacker Subunit object
    :param target: Damage receiver Subunit object
    :param final_dmg: Damage value to health
    :param impact: Impact value affecting if the target will start damaged or knockdown animation
    :param final_morale_dmg: Damage value to morale
    :param element_effect: Dict of element effect inflict to target
    :param hit_angle: Angle of hitting side
    """
    if final_dmg > target.health:  # dmg cannot be higher than remaining health
        final_dmg = target.health

    impact_check = impact - target.troop_mass

    if impact_check > target.max_health50:
        target.interrupt_animation = True
        target.command_action = self.knockdown_command_action
        target.move_speed = impact_check
        target.momentum = 0
        target.charging = False
        target.forced_target = Vector2(target.base_pos[0] - (impact_check / 2 * sin(radians(hit_angle))),
                                       target.base_pos[1] - (impact_check / 2 * cos(radians(hit_angle))))
        self.battle.add_sound_effect_queue(self.sound_effect_pool["KnockDown"][0], target.base_pos,
                                           target.knock_down_sound_distance,
                                           target.knock_down_sound_shake,
                                           volume_mod=target.hit_volume_mod)  # larger size play louder sound

    elif impact_check > target.max_health20:
        target.interrupt_animation = True
        target.command_action = self.heavy_damaged_command_action
        target.move_speed = target.walk_speed
        target.momentum = 0
        target.charging = False
        target.forced_target = Vector2(target.base_pos[0] - (impact_check * sin(radians(hit_angle))),
                                       target.base_pos[1] - (impact_check * cos(radians(hit_angle))))
        self.battle.add_sound_effect_queue(self.sound_effect_pool["HeavyDamaged"][0], target.base_pos,
                                           target.heavy_dmg_sound_distance,
                                           target.heavy_dmg_sound_shake,
                                           volume_mod=target.hit_volume_mod)

    elif impact_check > target.max_health10:  # play damaged animation
        target.interrupt_animation = True
        target.command_action = self.damaged_command_action
        target.move_speed = target.walk_speed
        target.momentum = 0
        target.charging = False
        target.forced_target = Vector2(target.base_pos[0] - (impact_check * sin(radians(hit_angle))),
                                       target.base_pos[1] - (impact_check * cos(radians(hit_angle))))

        self.battle.add_sound_effect_queue(self.sound_effect_pool["Damaged"][0], target.base_pos,
                                           target.dmg_sound_distance,
                                           target.dmg_sound_shake,
                                           volume_mod=target.hit_volume_mod)

    else:  # take damage but not high enough to play animation
        self.angle = self.set_rotate(self.nearest_enemy[0].base_pos)
        if self.available_damaged_skill and not self.current_action and not self.command_action:  # use damaged skill
            self.command_action = {"skill": self.available_damaged_skill[0]}

    target.health -= final_dmg
    health_check = 0.1
    if target.max_health != infinity:
        health_check = 1 - (target.health / target.max_health)
    target.base_morale -= final_morale_dmg * target.mental * health_check
    target.stamina -= self.stamina_dmg_bonus

    for key, value in element_effect.items():
        target.element_status_check[key] += round(final_dmg * value * (100 - target.element_resistance[key] / 100))

    # self.base_morale += round((final_morale_dmg / 5))  # recover some morale when deal morale dmg to enemy
