import pygame
from gamescript import datastat
from gamescript.common import utility

load_images = utility.load_images


def make_faction_troop_leader_data(main_dir, screen_scale, ruleset, ruleset_folder, language):
    # create troop data storage related object
    weapon_images = load_images(main_dir, screen_scale=screen_scale, subfolder=("ui", "subunit_ui", "weapon"),
                                load_order=True)

    troop_data = datastat.TroopData(main_dir, weapon_images, ruleset, ruleset_folder, language)

    # create leader data storage object
    portrait_images = load_images(main_dir, screen_scale=screen_scale,
                                  subfolder=("ruleset", ruleset_folder, "leader", "portrait"))
    leader_data = datastat.LeaderData(main_dir, portrait_images, troop_data, ruleset, ruleset_folder, language)

    # create faction data storage object
    faction_data = datastat.FactionData(main_dir, ruleset_folder, screen_scale, language)

    return troop_data, leader_data, faction_data
