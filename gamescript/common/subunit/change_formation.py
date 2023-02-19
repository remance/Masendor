import numpy as np
from PIL import Image


def change_formation(self, which, formation=None):
    """
    Change current formation to the new one, setup formation array
    :param self: Subunit object (subunit leader in particularly)
    :param which: troop or unit formation change
    :param formation: Name of new formation, None mean use current one
    """
    consider_flank = [False, False]
    if which == "troop":
        if formation:
            self.troop_formation = formation
        for leader in self.alive_leader_follower:  # leader follower change to match formation if can
            if formation in leader.formation_list:
                leader.change_formation("troop", formation=formation)
        for subunit in self.alive_troop_follower:
            if subunit.subunit_type < 2 and not consider_flank[0]:
                consider_flank[0] = True
            elif subunit.subunit_type >= 2 and not consider_flank[0]:
                consider_flank[1] = True
            if False not in consider_flank:
                break

        self.formation_consider_flank = False
        if False not in consider_flank:
            self.formation_consider_flank = True

        new_formation = self.all_formation_list[self.troop_formation].copy()
        self.troop_formation_preset = convert_formation_preset(self.troop_follower_size, new_formation)

    elif which == "unit":
        if formation:
            self.unit_formation = formation
        for leader in self.alive_leader_follower:
            if "cav" not in leader.unit_type and not consider_flank[0]:
                consider_flank[0] = True
            elif "cav" in leader.unit_type and not consider_flank[0]:
                consider_flank[1] = True
            if False not in consider_flank:
                break

        self.unit_consider_flank = False
        if False not in consider_flank:
            self.unit_consider_flank = True

        new_formation = self.all_formation_list[self.unit_formation].copy()
        self.unit_formation_preset = convert_formation_preset(self.leader_follower_size, new_formation)

    self.setup_formation(which)


def convert_formation_preset(follower_size, formation):
    """
    Convert the default formation preset array to new one with the current follower size,
    use pillow image resize since it is too much trouble to do it manually.
    Also change placement score to make position near center and front has higher score
    """
    front_order_to_place, rear_order_to_place, flank_order_to_place, center_order_to_place = calculate_formation_priority(follower_size)
    image = Image.fromarray((formation * 255).astype(np.uint8))
    image = image.resize((follower_size, follower_size))
    new_value = np.array(image)
    front_score = new_value.copy()
    rear_score = new_value.copy()
    flank_score = new_value.copy()
    center_score = new_value.copy()
    for item, score in front_order_to_place.items():
        front_score[item[0]][item[1]] *= score
    for item, score in rear_order_to_place.items():
        rear_score[item[0]][item[1]] *= score
    for item, score in flank_order_to_place.items():
        flank_score[item[0]][item[1]] *= score
    for item, score in center_order_to_place.items():
        center_score[item[0]][item[1]] *= score
    return {"original": new_value, "front": front_score, "rear": rear_score, "center-front": center_score + front_score,
            "center-rear": center_score + rear_score, "flank-front": flank_score + front_score,
            "flank-rear": flank_score + rear_score}


def calculate_formation_priority(follower_size):
    """Calculate priority of front, rear, flank, inner, outer formation priority score"""
    center = int(follower_size / 2)

    front_order_to_place = [list(range(0, follower_size)), list(range(0, follower_size))]
    true_front_order_to_place = {}
    score = 1
    for row in front_order_to_place[0]:
        for col in front_order_to_place[1]:
            true_front_order_to_place[(row, col)] = score
        score += 1

    rear_order_to_place = [list(range(0, follower_size)), list(range(0, follower_size))]
    rear_order_to_place[0] = rear_order_to_place[0][int(len(rear_order_to_place[0]) / 2) + 1:] + list(
        reversed(rear_order_to_place[0][:int(len(rear_order_to_place[0]) / 2) + 1]))

    true_rear_order_to_place = {}
    score = 1
    for row in rear_order_to_place[0]:
        for col in rear_order_to_place[1]:
            true_rear_order_to_place[(row, col)] = score
        score += 1

    flank_order_to_place = [list(range(0, follower_size)), list(range(0, follower_size))]
    flank_order_to_place[1].sort(key=lambda x: abs(center - x), reverse=True)
    true_flank_order_to_place = {}
    for row in flank_order_to_place[0]:
        score = 1
        for col in flank_order_to_place[1]:
            true_flank_order_to_place[(row, col)] = score
            score += 1

    center_order_to_place = [list(range(0, follower_size)), list(range(0, follower_size))]
    # center_order_to_place[0].sort(key=lambda x: abs(center - x))
    center_order_to_place[1].sort(key=lambda x: abs(center - x))
    true_center_order_to_place = {}
    for row in center_order_to_place[0]:
        score = 1
        for col in center_order_to_place[1]:
            true_center_order_to_place[(row, col)] = score
            score += 1

    return true_front_order_to_place, true_rear_order_to_place, true_flank_order_to_place, true_center_order_to_place


def min_max_order(order_list, how):
    """

    :param order_list: List to insert order number
    :param how: 0 for row, 1 for column
    :return:
    """
    run = 0
    for index, item in enumerate(list(reversed(order_list[how]))):
        order_list[how].insert(index + 1 + run, item)
        run += 1
    order_list[how] = order_list[how][:int(len(order_list[how]) / 2)]
    return order_list
