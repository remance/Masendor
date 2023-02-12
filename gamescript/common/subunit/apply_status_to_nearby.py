def apply_status_to_nearby(self, nearby_list, aoe, effect):
    """
    apply status effect to nearby subunit depending on aoe stat
    :param self: Subunit object
    :param nearby_list: Dict of nearby subunits
    :param aoe: Area of effect distance
    :param effect: ID of status
    """

    for subunit in nearby_list:
        if aoe >= subunit[1]:  # only apply to exist and alive
            subunit[0].apply_effect(effect, subunit[0].status_list[effect], subunit[0].status_effect,
                                    subunit[0].status_duration)
        else:
            break
