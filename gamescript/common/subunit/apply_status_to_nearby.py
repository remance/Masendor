def apply_status_to_nearby(self, nearby_list, aoe, status_id):
    """apply status effect to nearby subunit depending on aoe stat"""
    for subunit in nearby_list:
        if aoe >= subunit[1]:  # only apply to exist and alive squads
            subunit[0].apply_effect(status_id, subunit[0].status_list, subunit[0].status_effect,
                                    subunit[0].status_duration)
        else:
            break
