from engine.data import datastat
from engine import utility

load_images = utility.load_images


def make_faction_troop_leader_data(module_dir, screen_scale):
    # create troop data storage related object
    troop_data = datastat.TroopData()

    # create leader data storage object
    portrait_images = load_images(module_dir, screen_scale=screen_scale,
                                  subfolder=("leader", "preset", "portrait"))
    leader_data = datastat.LeaderData(portrait_images, troop_data)

    # create faction data storage object
    faction_data = datastat.FactionData()

    return troop_data, leader_data, faction_data
