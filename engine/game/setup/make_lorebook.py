import pygame

from engine.uimenu.uimenu import MenuImageButton
from engine.uibattle.uibattle import UIScroll
from engine.lorebook.lorebook import Lorebook, SubsectionList
from engine.utility import load_images


def make_lorebook(self):
    """Create Encyclopedia related objects"""
    encyclopedia_images = load_images(self.module_dir, screen_scale=self.screen_scale, subfolder=("ui", "lorebook_ui"))
    encyclopedia = Lorebook(self, encyclopedia_images["encyclopedia"])  # encyclopedia sprite
    lore_name_list = SubsectionList(encyclopedia.rect.topleft, encyclopedia_images["section_list"])
    filter_tag_list = SubsectionList(
        (encyclopedia.rect.topright[0] + encyclopedia_images["section_list"].get_width(),
         encyclopedia.rect.topright[1]),
        pygame.transform.flip(encyclopedia_images["section_list"], True, False))
    lore_name_list.max_row_show = encyclopedia.max_row_show

    button_images = load_images(self.module_dir, screen_scale=self.screen_scale,
                                subfolder=("ui", "lorebook_ui", "button"))
    lore_buttons = {0: MenuImageButton((encyclopedia.rect.topleft[0] + (button_images["concept"].get_width() / 2),
                                        encyclopedia.rect.topleft[1] - (button_images["concept"].get_height() / 2)),
                                       [button_images["concept"]], layer=13),
                    1: MenuImageButton((encyclopedia.rect.topleft[0] + (encyclopedia.image.get_width() / 8.5),
                                        encyclopedia.rect.topleft[1] - (button_images["history"].get_height() / 2)),
                                       [button_images["history"]], layer=13),
                    2: MenuImageButton((encyclopedia.rect.topleft[0] + (encyclopedia.image.get_width() / 5),
                                        encyclopedia.rect.topleft[1] - (button_images["faction"].get_height() / 2)),
                                       [button_images["faction"]], layer=13),
                    3: MenuImageButton((encyclopedia.rect.topleft[0] + (encyclopedia.image.get_width() / 3.5),
                                        encyclopedia.rect.topleft[1] - (button_images["troop"].get_height() / 2)),
                                       [button_images["troop"]], layer=13),
                    4: MenuImageButton((encyclopedia.rect.topleft[0] + (encyclopedia.image.get_width() / 2.7),
                                        encyclopedia.rect.topleft[1] - (button_images["equipment"].get_height() / 2)),
                                       [button_images["equipment"]], layer=13),
                    5: MenuImageButton((encyclopedia.rect.topleft[0] + (encyclopedia.image.get_width() / 2.2),
                                        encyclopedia.rect.topleft[1] - (button_images["status"].get_height() / 2)),
                                       [button_images["status"]], layer=13),
                    6: MenuImageButton((encyclopedia.rect.topleft[0] + (encyclopedia.image.get_width() / 1.85),
                                        encyclopedia.rect.topleft[1] - (button_images["skill"].get_height() / 2)),
                                       [button_images["skill"]], layer=13),
                    7: MenuImageButton((encyclopedia.rect.topleft[0] + (encyclopedia.image.get_width() / 1.6),
                                        encyclopedia.rect.topleft[1] - (button_images["property"].get_height() / 2)),
                                       [button_images["property"]], layer=13),
                    8: MenuImageButton((encyclopedia.rect.topleft[0] + (encyclopedia.image.get_width() / 1.41),
                                        encyclopedia.rect.topleft[1] - (button_images["leader"].get_height() / 2)),
                                       [button_images["leader"]], layer=13),
                    9: MenuImageButton((encyclopedia.rect.topleft[0] + (encyclopedia.image.get_width() / 1.26),
                                        encyclopedia.rect.topleft[1] - (button_images["terrain"].get_height() / 2)),
                                       [button_images["terrain"]], layer=13),
                    10: MenuImageButton((encyclopedia.rect.topleft[0] + (encyclopedia.image.get_width() / 1.14),
                                         encyclopedia.rect.topleft[1] - (button_images["weather"].get_height() / 2)),
                                        [button_images["weather"]], layer=13),
                    "close": MenuImageButton((encyclopedia.rect.topleft[0] + (encyclopedia.image.get_width() / 1.04),
                                              encyclopedia.rect.topleft[1] - (button_images["close"].get_height() / 2)),
                                             [button_images["close"]], layer=13)}  # next page button

    UIScroll(lore_name_list, lore_name_list.rect.topright)  # add subsection list scroll
    UIScroll(filter_tag_list, filter_tag_list.rect.topright)  # add filter list scroll

    return encyclopedia, lore_name_list, filter_tag_list, lore_buttons
