import random


def find_melee_target(self, subunit_list):
    """Find close enemy subunit to move to fight"""
    close_list = {subunit: subunit.base_pos.distance_to(self.base_pos) for subunit in subunit_list}
    close_list = dict(sorted(close_list.items(), key=lambda item: item[1]))
    max_random = 3
    if len(close_list) < 4:
        max_random = len(close_list) - 1
        if max_random < 0:
            max_random = 0
    close_target = None
    if len(close_list) > 0:
        close_target = tuple(close_list.keys())[random.randint(0, max_random)]
        # if close_target.base_pos.distance_to(self.base_pos) < 20: # in case can't find close target
    return close_target
