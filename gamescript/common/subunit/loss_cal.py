import random

infinity = float("inf")


def loss_cal(self, target, final_dmg, final_morale_dmg, leader_dmg, element_effect):
    """
    :param self: Attacker Subunit object
    :param target: Damage receiver Subunit object
    :param final_dmg: Damage value to health
    :param final_morale_dmg: Damage value to morale
    :param leader_dmg: Damage value to leader inside target subunit
    :param element_effect: Dict of element effect inflict to target
    """
    if final_dmg > target.subunit_health:  # dmg cannot be higher than remaining health
        final_dmg = target.subunit_health

    if final_dmg > target.max_health5:  # play damaged animation
        target.interrupt_animation = True
        target.command_action = ("Damaged", "uninterruptible")
        if final_dmg > target.max_health10:
            target.command_action = ("HeavyDamaged", "uninterruptible")

    target.subunit_health -= final_dmg
    health_check = 0.1
    if target.max_health != infinity:
        health_check = 1 - (target.subunit_health / target.max_health)
    target.base_morale -= (final_morale_dmg + self.morale_dmg_bonus) * target.mental * health_check
    target.stamina -= self.stamina_dmg_bonus

    if target.red_border is False:  # add red corner to indicate combat
        target.block.blit(target.subunit_ui_images["subunit_combat"], target.corner_image_rect)
        target.red_border = True

    for key, value in element_effect.items():
        target.element_status_check[key] += round(final_dmg * value * (100 - target.element_resistance[key] / 100))

    self.base_morale += round((final_morale_dmg / 5))  # recover some morale when deal morale dmg to enemy

    if target.leader is not None and target.leader.health > 0 and random.randint(0, 10) > 9:  # dmg on subunit leader, only 10% chance
        final_leader_dmg = round(leader_dmg - (leader_dmg * target.leader.combat / 101))
        if final_leader_dmg > target.leader.health:
            final_leader_dmg = target.leader.health
        target.leader.health -= final_leader_dmg
