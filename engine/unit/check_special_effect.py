def check_special_effect(self, effect, weapon=None):
    """
    :param self: Unit object
    :param effect: Effect name
    :param weapon: Weapon index for effect that involve specific weapon like when attacking
    :return: Boolean
    """
    if True in self.special_effect[effect][0]:
        return True
    elif weapon is not None and self.special_effect[effect][1][weapon]:
        return True
    else:
        return False
