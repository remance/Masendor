import pygame
from gamescript import datastat
from gamescript.common import utility

load_images = utility.load_images


def make_faction_troop_leader_equipment_data(main_dir, screen_scale, ruleset, ruleset_folder):

    # create troop data storage related object
    images = load_images(main_dir, screen_scale, ["ui", "unit_ui", "weapon"])
    for image in images:
        x, y = images[image].get_width(), images[image].get_height()
        images[image] = pygame.transform.scale(images[image],
                                     (int(x / 1.7), int(y / 1.7)))  # scale 1.7 seem to be most fitting as a placeholder
    weapon_data = datastat.WeaponData(main_dir, images, ruleset)  # Create weapon class

    images = load_images(main_dir, screen_scale, ["ui", "unit_ui", "armour"])
    armour_data = datastat.ArmourData(main_dir, images, ruleset)  # Create armour class
    troop_data = datastat.TroopData(main_dir, ruleset, ruleset_folder)

    # create leader data storage object
    images = load_images(main_dir, screen_scale, ["ruleset", ruleset_folder, "leader", "portrait"], load_order=False)
    leader_data = datastat.LeaderData(main_dir, images, ruleset, ruleset_folder)

    # create faction data storage object
    faction_data = datastat.FactionData(main_dir, ruleset_folder, screen_scale)

    return weapon_data, armour_data, troop_data, leader_data, faction_data


