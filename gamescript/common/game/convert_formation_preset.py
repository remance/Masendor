import numpy as np
import pygame
from PIL import Image


def convert_formation_preset(self):
    """
    Convert the default formation preset array to new one with the unit size according to the genre setting,
    use pillow image resize since it is too much trouble to do it manually.
    Also change placement score to make position near center and front has higher score
    :param self: Game object
    """
    self.troop_data.unit_formation_list = {}

    front_order_to_place, rear_order_to_place, flank_order_to_place, outer_order_to_place, inner_order_to_place = calculate_formation_priority(
        self)

    for key, value in self.troop_data.default_unit_formation_list.items():
        image = Image.fromarray(value)
        image = image.resize((self.unit_size[0], self.unit_size[1]))
        new_value = np.array(image)
        front_score = new_value.copy()
        rear_score = new_value.copy()
        flank_score = new_value.copy()
        outer_score = new_value.copy()
        inner_score = new_value.copy()
        for score, item in enumerate(front_order_to_place):
            front_score[item[0]][item[1]] = front_score[item[0]][item[1]] * (score + 2)
        for score, item in enumerate(rear_order_to_place):
            rear_score[item[0]][item[1]] = rear_score[item[0]][item[1]] * (score + 2)
        for score, item in enumerate(flank_order_to_place):
            flank_score[item[0]][item[1]] = flank_score[item[0]][item[1]] * (score + 2)
        for score, item in enumerate(outer_order_to_place):
            outer_score[item[0]][item[1]] = outer_score[item[0]][item[1]] * (score + 2)
        for score, item in enumerate(inner_order_to_place):
            inner_score[item[0]][item[1]] = inner_score[item[0]][item[1]] * (score + 2)
        self.troop_data.unit_formation_list[key] = {"original": new_value,
                                                    "center-front": front_score, "center-rear": rear_score,
                                                    "flank-front": flank_score + front_score,
                                                    "flank-rear": flank_score + rear_score,
                                                    "inner-front": inner_score + front_score,
                                                    "inner-rear": inner_score + rear_score,
                                                    "outer-front": outer_score + front_score,
                                                    "outer-rear": outer_score + rear_score}


def calculate_formation_priority(self):
    """
    Calculate priority of front and rear formation priority score
    :param self: Either Game or Unit object should work
    :return: front and rear position score list
    """
    center = (int(round(self.unit_size[0] / 2, 0)), int(round(self.unit_size[1] / 2, 0)))

    front_order_to_place = [list(range(0, self.unit_size[0])), [center[1]]]
    for occurrence, _ in enumerate(range(center[1] + 1, self.unit_size[1])):
        front_order_to_place[1].append(center[1] - (occurrence + 1))
        front_order_to_place[1].append(center[1] + (occurrence + 1))
    front_order_to_place = [(item1, item2) for item1 in front_order_to_place[0] for item2 in front_order_to_place[1]]

    rear_order_to_place = [list(range(0, self.unit_size[0])), [center[1]]]
    rear_order_to_place[0] = rear_order_to_place[0][int(len(rear_order_to_place[0]) / 2) + 1:] + list(
        reversed(rear_order_to_place[0][:int(len(rear_order_to_place[0]) / 2) + 1]))
    for occurrence, _ in enumerate(range(center[1] + 1, self.unit_size[1])):
        rear_order_to_place[1].append(center[1] - (occurrence + 1))
        rear_order_to_place[1].append(center[1] + (occurrence + 1))
    rear_order_to_place = [(item1, item2) for item1 in rear_order_to_place[0] for item2 in rear_order_to_place[1]]

    flank_order_to_place = [list(range(0, self.unit_size[0])), [center[1]]]
    for occurrence, _ in enumerate(range(center[1] + 1, self.unit_size[1])):
        flank_order_to_place[1].append(center[1] - (occurrence + 1))
        flank_order_to_place[1].append(center[1] + (occurrence + 1))
    flank_order_to_place = [(item1, item2) for item2 in flank_order_to_place[1] for item1 in flank_order_to_place[0]]

    outer_order_to_place = [list(range(0, self.unit_size[0])), list(range(0, self.unit_size[1]))]
    outer_order_to_place = min_max_order(outer_order_to_place, 0)
    outer_order_to_place = min_max_order(outer_order_to_place, 1)
    outer_order_to_place = [(item1, item2) for item2 in outer_order_to_place[1] for item1 in outer_order_to_place[0]]

    inner_order_to_place = [[center[0]], [center[1]]]
    for occurrence, _ in enumerate(range(center[0] + 1, self.unit_size[0])):
        inner_order_to_place[0].append(center[0] - (occurrence + 1))
        inner_order_to_place[0].append(center[0] + (occurrence + 1))
    for occurrence, _ in enumerate(range(center[1] + 1, self.unit_size[1])):
        inner_order_to_place[1].append(center[1] - (occurrence + 1))
        inner_order_to_place[1].append(center[1] + (occurrence + 1))

    inner_order_to_place = [pygame.Vector2(item1, item2) for item1 in inner_order_to_place[0] for item2 in
                            inner_order_to_place[1]]
    order_to_place = {index: value.distance_to(pygame.Vector2(center)) for index, value in
                      enumerate(inner_order_to_place)}  # calculate distance to center using pygame vector2 distance
    order_to_place = [key[0] for key in sorted(order_to_place.items(), key=lambda x: x[1])]  # get list index sorted
    inner_order_to_place[:] = [inner_order_to_place[i] for i in order_to_place]  # sort list based on order_to_place
    inner_order_to_place = [(int(item[0]), int(item[1])) for item in inner_order_to_place]

    return front_order_to_place, rear_order_to_place, flank_order_to_place, outer_order_to_place, inner_order_to_place


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
