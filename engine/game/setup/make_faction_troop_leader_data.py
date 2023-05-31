from engine.data.datastat import TroopData, LeaderData, FactionData
from engine.utility import load_images


def make_faction_troop_leader_data(module_dir, screen_scale):
    # create troop data storage related object
    troop_data = TroopData()

    # create leader data storage object
    portrait_images = load_images(module_dir, screen_scale=screen_scale,
                                  subfolder=("leader", "preset", "portrait"))
    leader_data = LeaderData(portrait_images, troop_data)

    # create faction data storage object
    faction_data = FactionData()

    return troop_data, leader_data, faction_data
