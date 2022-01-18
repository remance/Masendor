import math
import numpy as np
import pygame
import pygame.freetype
from gamescript import script_common

load_image = script_common.load_image
load_images = script_common.load_images
csv_read = script_common.csv_read

"""This file contains fuctions of various purposes"""

# Default self mechanic value

infinity = float("inf")

# Data Loading gamescript

def load_game_data(game):
    """Load various self data"""

    screen_rect = game.screen_rect
    from gamescript import battleui, uniteditor, rangeattack, unit, subunit

    # v Game Effect related class
    effect_images = load_images(game.main_dir, ["sprite", "effect"], load_order=False)
    # images = []
    # for images in imgsold:
    # x, y = images.get_width(), images.get_height()
    # images = pygame.transform.scale(images, (int(x ), int(y / 2)))
    # images.append(images)
    rangeattack.RangeArrow.images = [effect_images["arrow.png"]]
    # ^ End self effect

    ui_image = load_images(game.main_dir, ["tactical", "ui", "battle_ui"], load_order=False)
    icon_image = load_images(game.main_dir, ["tactical", "ui", "battle_ui", "commandbar_icon"], load_order=False)
    # Army select list ui
    game.unit_selector = battleui.ArmySelect((0, 0), ui_image["unit_select_box.png"])
    game.time_ui.change_pos((game.unit_selector.rect.topright), game.time_number)
    game.battle_ui.add(game.unit_selector)
    game.select_scroll = battleui.UIScroller(game.unit_selector.rect.topright, ui_image["unit_select_box.png"].get_height(),
                                             game.unit_selector.max_row_show)  # scroller for unit select ui

    game.command_ui = battleui.GameUI(image=ui_image["command_box.png"], icon=icon_image,
                                      ui_type="commandbar")  # Left top command ui with leader and unit behavious button
    game.command_ui.change_pos((ui_image["command_box.png"].get_size()[0] / 2,
                                       (ui_image["command_box.png"].get_size()[1] / 2) + game.unit_selector.image.get_height()))
    game.game_ui.add(game.command_ui)

    # Load all image of ui and icon from folder
    icon_image = load_images(game.main_dir, ["ui", "battle_ui", "topbar_icon"], load_order=False)

    game.col_split_button = battleui.UIButton((game.command_ui.pos[0] - 115, game.command_ui.pos[1] + 26), ui_image["colsplit_button.png"], 0)  # unit split by column button
    game.row_split_button = battleui.UIButton((game.command_ui.pos[0] - 115, game.command_ui.pos[1] + 56), ui_image["rowsplit_button.png"], 1)  # unit split by row button
    game.button_ui.add(game.col_split_button)
    game.button_ui.add(game.row_split_button)

    game.decimation_button = battleui.UIButton((game.command_ui.pos[0] + 100, game.command_ui.pos[1] + 56), ui_image["decimation.png"], 1)

    # Right top bar ui that show rough information of selected battalions
    game.unitstat_ui = battleui.GameUI(image=ui_image["topbar.png"], icon=icon_image, ui_type="topbar")
    game.unitstat_ui.change_pos((screen_rect.width - ui_image["topbar.png"].get_size()[0] / 2, ui_image["topbar.png"].get_size()[1] / 2))
    game.game_ui.add(game.unitstat_ui)
    game.unitstat_ui.unit_state_text = game.state_text

    game.inspect_ui_pos = [game.unitstat_ui.rect.bottomleft[0] - game.icon_sprite_width / 1.25,
                           game.unitstat_ui.rect.bottomleft[1] - game.icon_sprite_height / 3]

    # Subunit information card ui
    game.inspect_ui = battleui.GameUI(image=ui_image["army_inspect.png"], icon="", ui_type="unitbox")  # inspect ui that show subnit in selected unit
    game.inspect_ui.change_pos((screen_rect.width - ui_image["army_inspect.png"].get_size()[0] / 2, ui_image["topbar.png"].get_size()[1] * 4))
    game.game_ui.add(game.inspect_ui)
    # v Subunit shown in inspect ui
    width, height = game.inspect_ui_pos[0], game.inspect_ui_pos[1]
    sub_unit_number = 0  # Number of subunit based on the position in row and column
    imgsize = (game.icon_sprite_width, game.icon_sprite_height)
    game.inspect_subunit = []
    for this_subunit in list(range(0, 64)):
        width += imgsize[0]
        game.inspect_subunit.append(battleui.InspectSubunit((width, height)))
        sub_unit_number += 1
        if sub_unit_number == 8:  # Reach the last subunit in the row, go to the next one
            width = game.inspect_ui_pos[0]
            height += imgsize[1]
            sub_unit_number = 0
    # ^ End subunit shown

    game.troop_card_ui.change_pos((screen_rect.width - game.troop_card_ui.image.get_size()[0] / 2,
                              (game.unitstat_ui.image.get_size()[1] * 2.5) + game.troop_card_ui.image.get_size()[1]))

    # Behaviour button that once click switch to other mode for subunit behaviour
    skill_condition_button = [ui_image["skillcond_0.png"], ui_image["skillcond_1.png"], ui_image["skillcond_2.png"], ui_image["skillcond_3.png"]]
    shoot_condition_button = [ui_image["fire_0.png"], ui_image["fire_1.png"]]
    behaviour_button = [ui_image["hold_0.png"], ui_image["hold_1.png"], ui_image["hold_2.png"]]
    range_condition_button = [ui_image["minrange_0.png"], ui_image["minrange_1.png"]]
    arc_condition_button = [ui_image["arc_0.png"], ui_image["arc_1.png"], ui_image["arc_2.png"]]
    run_condition_button = [ui_image["runtoggle_0.png"], ui_image["runtoggle_1.png"]]
    melee_condition_button = [ui_image["meleeform_0.png"], ui_image["meleeform_1.png"], ui_image["meleeform_2.png"]]
    game.switch_button = [battleui.SwitchButton((game.command_ui.pos[0] - 40, game.command_ui.pos[1] + 96), skill_condition_button),  # skill condition button
                          battleui.SwitchButton((game.command_ui.pos[0] - 80, game.command_ui.pos[1] + 96), shoot_condition_button),  # fire at will button
                          battleui.SwitchButton((game.command_ui.pos[0], game.command_ui.pos[1] + 96), behaviour_button),  # behaviour button
                          battleui.SwitchButton((game.command_ui.pos[0] + 40, game.command_ui.pos[1] + 96), range_condition_button),  # shoot range button
                          battleui.SwitchButton((game.command_ui.pos[0] - 125, game.command_ui.pos[1] + 96), arc_condition_button),  # arc_shot button
                          battleui.SwitchButton((game.command_ui.pos[0] + 80, game.command_ui.pos[1] + 96), run_condition_button),  # toggle run button
                          battleui.SwitchButton((game.command_ui.pos[0] + 120, game.command_ui.pos[1] + 96), melee_condition_button)]  # toggle melee mode

    game.inspect_button = battleui.UIButton((game.unitstat_ui.pos[0] - 206, game.unitstat_ui.pos[1] - 1), ui_image["army_inspect_button.png"], 1)  # unit inspect open/close button
    game.button_ui.add(game.inspect_button)

    game.battle_ui.add(game.log_scroll, game.select_scroll)

    game.inspect_selected_border = battleui.SelectedSquad((15000, 15000))  # yellow border on selected subnit in inspect ui
    game.main_ui.remove(game.inspect_selected_border)  # remove subnit border sprite from gamestart menu drawer
    # ^ End self ui
