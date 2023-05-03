@staticmethod
def apply_status_to_nearby(nearby_list, aoe, effect):
    """
    apply status effect to nearby unit depending on aoe stat
    :param nearby_list: Dict of nearby units
    :param aoe: Area of effect distance
    :param effect: ID of status
    """

    for unit in nearby_list:
        if aoe >= unit[1]:  # only apply to exist and alive
            unit[0].apply_effect(effect, unit[0].status_list[effect], unit[0].status_effect,
                                 unit[0].status_duration)
        else:
            break
