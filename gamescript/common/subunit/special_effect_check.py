def special_effect_check(self, effect, weapon=None):
    """
    :param self: Subunit object
    :param effect: Effect name
    :param weapon: Weapon index for effect that involve specific weapon like when attacking
    :return: Boolean
    """
    if True in self.special_effect[effect][0]:
        return True
    elif (weapon is not None and self.special_effect[effect][1][weapon]) or \
            True in self.special_effect[effect][1]:
        return True
    else:
        return False
