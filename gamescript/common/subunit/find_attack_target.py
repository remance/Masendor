import random


def find_attack_target(self, subunit_list, check_line_of_sight=False):
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
        if check_line_of_sight is False:  # get randomly closest enemy
            close_target = tuple(close_list.keys())[random.randint(0, max_random)]
        else:  # check for line of sight of all subunit in list starting from closest
            for this_subunit in close_list:
                if self.check_line_of_sight(this_subunit.base_pos) is False:
                    close_target = this_subunit
                    break
    return close_target
