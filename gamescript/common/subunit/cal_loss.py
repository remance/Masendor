import random

infinity = float("inf")


def cal_loss(self, target, final_dmg, final_morale_dmg, element_effect):
    """
    :param self: Attacker Subunit object
    :param target: Damage receiver Subunit object
    :param final_dmg: Damage value to health
    :param final_morale_dmg: Damage value to morale
    :param element_effect: Dict of element effect inflict to target
    """
    if final_dmg > target.health:  # dmg cannot be higher than remaining health
        final_dmg = target.health

    if final_dmg > target.max_health10:
        target.interrupt_animation = True
        target.command_action = self.knockdown_command_action
        target.one_activity_limit = target.max_health / final_dmg

    elif final_dmg > target.max_health5:
        target.interrupt_animation = True
        target.command_action = self.heavy_damaged_command_action

    elif final_dmg > target.max_health1:  # play damaged animation
        target.interrupt_animation = True
        target.command_action = self.damaged_command_action

    target.health -= final_dmg
    health_check = 0.1
    if target.max_health != infinity:
        health_check = 1 - (target.health / target.max_health)
    target.base_morale -= final_morale_dmg * target.mental * health_check
    target.stamina -= self.stamina_dmg_bonus

    for key, value in element_effect.items():
        target.element_status_check[key] += round(final_dmg * value * (100 - target.element_resistance[key] / 100))

    # self.base_morale += round((final_morale_dmg / 5))  # recover some morale when deal morale dmg to enemy
