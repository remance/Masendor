from gamescript import battleui, popup
from gamescript.common import utility

load_images = utility.load_images


def make_popup_ui(main_dir, screen_rect, screen_scale, battle_ui_image):
    """Create Popup Ui"""
    popup.TerrainPopup.images = list(load_images(main_dir, screen_scale, ["ui", "popup_ui", "terrain_check"], load_order=False).values())
    popup.TerrainPopup.screen_rect = screen_rect

    troop_card_ui = battleui.TroopCard(battle_ui_image["troop_card.png"])

    # Button related to subunit card and command
    troop_card_button = [battleui.UIButton(battle_ui_image["troopcard_button1.png"], 0),  # subunit card description button
                         battleui.UIButton(battle_ui_image["troopcard_button2.png"], 1),  # subunit card stat button
                         battleui.UIButton(battle_ui_image["troopcard_button3.png"], 2),  # subunit card skill button
                         battleui.UIButton(battle_ui_image["troopcard_button4.png"], 3)]  # subunit card equipment button

    terrain_check = popup.TerrainPopup()  # popup box that show terrain information when right click on map
    button_name_popup = popup.TextPopup(screen_scale)  # popup box that show name when mouse over
    leader_popup = popup.TextPopup(screen_scale)  # popup box that show leader name when mouse over
    effect_popup = popup.EffectIconPopup()  # popup box that show skill/trait/status name when mouse over
    char_popup = popup.TextPopup(screen_scale)  # popup box that show leader name when mouse over

    return {"troop_card_ui": troop_card_ui, "troop_card_button": troop_card_button, "terrain_check": terrain_check,
            "button_name_popup": button_name_popup, "terrain_check": terrain_check, "button_name_popup": button_name_popup,
            "leader_popup": leader_popup, "effect_popup": effect_popup, "char_popup": char_popup}

