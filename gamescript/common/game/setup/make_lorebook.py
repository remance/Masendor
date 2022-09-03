import pygame
from gamescript import battleui, lorebook
from gamescript.common import utility

load_image = utility.load_image
load_images = utility.load_images
csv_read = utility.csv_read


def make_lorebook(main_dir, ruleset_folder, screen_scale, screen_rect):
    """Create Encyclopedia related objects"""
    lorebook.Lorebook.concept_stat = csv_read(main_dir, "concept_stat.csv",
                                              ["data", "ruleset", ruleset_folder, "lore"], header_key=True)
    lorebook.Lorebook.concept_lore = csv_read(main_dir, "concept_lore.csv", ["data", "ruleset", ruleset_folder, "lore"])
    lorebook.Lorebook.history_stat = csv_read(main_dir, "history_stat.csv",
                                              ["data", "ruleset", ruleset_folder, "lore"], header_key=True)
    lorebook.Lorebook.history_lore = csv_read(main_dir, "history_lore.csv", ["data", "ruleset", ruleset_folder, "lore"])

    encyclopedia_images = load_images(main_dir, screen_scale, ["ui", "lorebook_ui"], load_order=False)
    encyclopedia = lorebook.Lorebook(main_dir, screen_scale, screen_rect,
                                     encyclopedia_images["encyclopedia"])  # encyclopedia sprite
    lore_name_list = lorebook.SubsectionList(encyclopedia.rect.topleft, encyclopedia_images["section_list"])
    lore_name_list.max_row_show = encyclopedia.max_row_show

    lore_button_images = load_images(main_dir, screen_scale, ["ui", "lorebook_ui", "button"], load_order=False)
    for image in lore_button_images:  # scale button image
        lore_button_images[image] = pygame.transform.scale(lore_button_images[image], (
        int(lore_button_images[image].get_width() * screen_scale[0]),
        int(lore_button_images[image].get_height() * screen_scale[1])))
    lore_button_ui = [battleui.UIButton(lore_button_images["concept"], 0, 13),  # concept section button
                      battleui.UIButton(lore_button_images["history"], 1, 13),  # history section button
                      battleui.UIButton(lore_button_images["faction"], 2, 13),  # faction section button
                      battleui.UIButton(lore_button_images["troop"], 3, 13),  # troop section button
                      battleui.UIButton(lore_button_images["equipment"], 4, 13),  # troop equipment section button
                      battleui.UIButton(lore_button_images["status"], 5, 13),  # troop status section button
                      battleui.UIButton(lore_button_images["skill"], 6, 13),  # troop skill section button
                      battleui.UIButton(lore_button_images["property"], 7, 13),  # troop property section button
                      battleui.UIButton(lore_button_images["leader"], 8, 13),  # leader section button
                      battleui.UIButton(lore_button_images["terrain"], 9, 13),  # terrain section button
                      battleui.UIButton(lore_button_images["weather"], 10, 13),  # weather section button
                      battleui.UIButton(lore_button_images["close"], "close", 13),  # close button
                      battleui.UIButton(lore_button_images["previous"], "previous", 24),  # previous page button
                      battleui.UIButton(lore_button_images["next"], "next", 24)]  # next page button

    lore_button_ui[0].change_pos((encyclopedia.rect.topleft[0] + (lore_button_images["concept"].get_width() / 2),
                                  encyclopedia.rect.topleft[1] - (lore_button_images["concept"].get_height() / 2)))
    lore_button_ui[1].change_pos(
        (encyclopedia.rect.topleft[0] + (lore_button_images["concept"].get_width() * 1.1) * 1.5,
         encyclopedia.rect.topleft[1] - (lore_button_images["concept"].get_height() / 2)))
    lore_button_ui[2].change_pos(
        (encyclopedia.rect.topleft[0] + (lore_button_images["concept"].get_width() * 1.1) * 2.5,
         encyclopedia.rect.topleft[1] - (lore_button_images["concept"].get_height() / 2)))
    lore_button_ui[3].change_pos(
        (encyclopedia.rect.topleft[0] + (lore_button_images["concept"].get_width() * 1.1) * 3.5,
         encyclopedia.rect.topleft[1] - (lore_button_images["concept"].get_height() / 2)))
    lore_button_ui[4].change_pos(
        (encyclopedia.rect.topleft[0] + (lore_button_images["concept"].get_width() * 1.1) * 4.5,
         encyclopedia.rect.topleft[1] - (lore_button_images["concept"].get_height() / 2)))
    lore_button_ui[5].change_pos(
        (encyclopedia.rect.topleft[0] + (lore_button_images["concept"].get_width() * 1.1) * 5.5,
         encyclopedia.rect.topleft[1] - (lore_button_images["concept"].get_height() / 2)))
    lore_button_ui[6].change_pos(
        (encyclopedia.rect.topleft[0] + (lore_button_images["concept"].get_width() * 1.1) * 6.5,
         encyclopedia.rect.topleft[1] - (lore_button_images["concept"].get_height() / 2)))
    lore_button_ui[7].change_pos(
        (encyclopedia.rect.topleft[0] + (lore_button_images["concept"].get_width() * 1.1) * 7.5,
         encyclopedia.rect.topleft[1] - (lore_button_images["concept"].get_height() / 2)))
    lore_button_ui[8].change_pos(
        (encyclopedia.rect.topleft[0] + (lore_button_images["concept"].get_width() * 1.1) * 8.5,
         encyclopedia.rect.topleft[1] - (lore_button_images["concept"].get_height() / 2)))
    lore_button_ui[9].change_pos(
        (encyclopedia.rect.topleft[0] + (lore_button_images["concept"].get_width() * 1.1) * 9.5,
         encyclopedia.rect.topleft[1] - (lore_button_images["concept"].get_height() / 2)))
    lore_button_ui[10].change_pos(
        (encyclopedia.rect.topleft[0] + (lore_button_images["concept"].get_width() * 1.1) * 10.5,
         encyclopedia.rect.topleft[1] - (lore_button_images["concept"].get_height() / 2)))
    lore_button_ui[11].change_pos(
        (encyclopedia.rect.topleft[0] + (lore_button_images["concept"].get_width() * 1.1) * 11.5,
         encyclopedia.rect.topleft[1] - (lore_button_images["concept"].get_height() / 2)))
    lore_button_ui[12].change_pos((encyclopedia.rect.bottomleft[0] + (lore_button_images["previous"].get_width()),
                                   encyclopedia.rect.bottomleft[1] - lore_button_images["previous"].get_height()))
    lore_button_ui[13].change_pos((encyclopedia.rect.bottomright[0] - (lore_button_images["next"].get_width()),
                                   encyclopedia.rect.bottomright[1] - lore_button_images["next"].get_height()))
    page_button = (lore_button_ui[12], lore_button_ui[13])
    battleui.UIScroll(lore_name_list, lore_name_list.rect.topright)  # add subsection list scroll

    return encyclopedia, lore_name_list, lore_button_ui, page_button
