from engine.data import datastat
from engine import utility

load_images = utility.load_images


def make_faction_troop_leader_data(data_dir, module_dir, screen_scale, language):
    # create troop data storage related object
    troop_data = datastat.TroopData(data_dir, module_dir, language)

    # create leader data storage object
    portrait_images = load_images(module_dir, screen_scale=screen_scale,
                                  subfolder=("leader", "preset", "portrait"))
    leader_data = datastat.LeaderData(module_dir, portrait_images, troop_data, language)

    # create faction data storage object
    faction_data = datastat.FactionData(module_dir, screen_scale, language)

    return troop_data, leader_data, faction_data
