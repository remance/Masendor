from pygame import Vector2

from math import cos, sin, radians
infinity = float("inf")


def cal_loss(self, final_dmg, impact, final_morale_dmg, element_effect, hit_angle):
    """
    :param self: Damage receiver Subunit object
    :param final_dmg: Damage value to health
    :param impact: Impact value affecting if the target will start damaged or knockdown animation
    :param final_morale_dmg: Damage value to morale
    :param element_effect: Dict of element effect inflict to target
    :param hit_angle: Angle of hitting side
    """
    if final_dmg > self.health:  # dmg cannot be higher than remaining health
        final_dmg = self.health

    impact_check = impact - self.troop_mass

    if impact_check > self.max_health50:
        self.interrupt_animation = True
        self.command_action = self.knockdown_command_action
        self.move_speed = impact_check
        self.momentum = 0
        self.charging = False
        self.forced_target = Vector2(self.base_pos[0] - (impact_check / 2 * sin(radians(hit_angle))),
                                       self.base_pos[1] - (impact_check / 2 * cos(radians(hit_angle))))
        self.battle.add_sound_effect_queue(self.sound_effect_pool["KnockDown"][0], self.base_pos,
                                           self.knock_down_sound_distance,
                                           self.knock_down_sound_shake,
                                           volume_mod=self.hit_volume_mod)  # larger size play louder sound

    elif impact_check > self.max_health20:
        self.interrupt_animation = True
        self.command_action = self.heavy_damaged_command_action
        self.move_speed = self.walk_speed
        self.momentum = 0
        self.charging = False
        self.forced_target = Vector2(self.base_pos[0] - (impact_check * sin(radians(hit_angle))),
                                       self.base_pos[1] - (impact_check * cos(radians(hit_angle))))
        self.battle.add_sound_effect_queue(self.sound_effect_pool["HeavyDamaged"][0], self.base_pos,
                                           self.heavy_dmg_sound_distance,
                                           self.heavy_dmg_sound_shake,
                                           volume_mod=self.hit_volume_mod)

    elif impact_check > self.max_health10:  # play damaged animation
        self.interrupt_animation = True
        self.command_action = self.damaged_command_action
        self.move_speed = self.walk_speed
        self.momentum = 0
        self.charging = False
        self.forced_target = Vector2(self.base_pos[0] - (impact_check * sin(radians(hit_angle))),
                                       self.base_pos[1] - (impact_check * cos(radians(hit_angle))))

        self.battle.add_sound_effect_queue(self.sound_effect_pool["Damaged"][0], self.base_pos,
                                           self.dmg_sound_distance,
                                           self.dmg_sound_shake,
                                           volume_mod=self.hit_volume_mod)

    elif not self.player_control:  # AI subunit take damage but not high enough to play animation
        self.angle = self.set_rotate(self.nearest_enemy[0].base_pos)
        if self.available_damaged_skill and not self.current_action and not self.command_action:  # use damaged skill
            self.skill_command_input(0, self.available_damaged_skill, pos_target=self.base_pos)

    self.health -= final_dmg
    health_check = 0.1
    if self.max_health != infinity:
        health_check = 1 - (self.health / self.max_health)
    self.base_morale -= final_morale_dmg * self.mental * health_check
    self.stamina -= self.stamina_dmg_bonus

    for key, value in element_effect.items():
        self.element_status_check[key] += round(final_dmg * value * (100 - self.element_resistance[key] / 100))

    # self.base_morale += round((final_morale_dmg / 5))  # recover some morale when deal morale dmg to enemy
