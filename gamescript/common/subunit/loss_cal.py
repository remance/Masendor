import random

infinity = float("inf")


def loss_cal(self, target, dmg, morale_dmg, leader_dmg, dmg_effect):
    """
    :param self: Attacker object
    :param target: Damage receiver object
    :param dmg: Damage value to health
    :param morale_dmg: Damage value to morale
    :param leader_dmg: Damage value to leader inside target subunit
    :param dmg_effect: Damage multiplier effect
    :return:
    """
    final_dmg = round(dmg * dmg_effect)
    final_morale_dmg = round(morale_dmg * dmg_effect)
    if final_dmg > target.subunit_health:  # dmg cannot be higher than remaining health
        final_dmg = target.subunit_health

    target.subunit_health -= final_dmg
    health_check = 0.1
    if target.max_health != infinity:
        health_check = 1 - (target.subunit_health / target.max_health)
    target.base_morale -= (final_morale_dmg + self.bonus_morale_dmg) * target.mental * health_check
    target.stamina -= self.bonus_stamina_dmg

    # v Add red corner to indicate combat
    if target.red_border is False:
        target.block.blit(target.unit_ui_images["ui_squad_combat.png"], target.corner_image_rect)
        target.red_border = True
    # ^ End red corner

    if self.elem_melee not in (0, 5):  # apply element effect if atk has element, except 0 physical, 5 magic
        target.elem_count[self.elem_melee - 1] += round(final_dmg * (100 - target.elem_res[self.elem_melee - 1] / 100))

    self.base_morale += round((final_morale_dmg / 5))  # recover some morale when deal morale dmg to enemy

    if target.leader is not None and target.leader.health > 0 and random.randint(0, 10) > 9:  # dmg on subunit leader, only 10% chance
        final_leader_dmg = round(leader_dmg - (leader_dmg * target.leader.combat / 101))
        if final_leader_dmg > target.leader.health:
            final_leader_dmg = target.leader.health
        target.leader.health -= final_leader_dmg
