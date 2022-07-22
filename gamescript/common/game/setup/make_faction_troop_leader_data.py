import pygame
from gamescript import datastat
from gamescript.common import utility

load_images = utility.load_images


def make_faction_troop_leader_data(main_dir, screen_scale, ruleset, ruleset_folder):

    # create troop data storage related object
    weapon_images = load_images(main_dir, screen_scale, ["ui", "unit_ui", "weapon"])
    for image in weapon_images:
        x, y = weapon_images[image].get_width(), weapon_images[image].get_height()
        weapon_images[image] = pygame.transform.scale(weapon_images[image],
                                     (int(x / 1.7), int(y / 1.7)))  # scale 1.7 seem to be most fitting as a placeholder

    troop_data = datastat.TroopData(main_dir, weapon_images, ruleset, ruleset_folder)

    # create leader data storage object
    images = load_images(main_dir, screen_scale, ["ruleset", ruleset_folder, "leader", "portrait"], load_order=False)
    leader_data = datastat.LeaderData(main_dir, images, ruleset, ruleset_folder)

    # create faction data storage object
    faction_data = datastat.FactionData(main_dir, ruleset_folder, screen_scale)

    return troop_data, leader_data, faction_data


