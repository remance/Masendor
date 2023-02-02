from gamescript import battleui
from gamescript.common import utility

load_images = utility.load_images


def make_genre_specific_ui(main_dir, screen_scale, genre, command_ui_type):
    genre_battle_ui_image = load_images(main_dir, screen_scale=screen_scale, subfolder=(genre, "ui", "battle_ui"))

    genre_icon_image = load_images(main_dir, screen_scale=screen_scale,
                                   subfolder=(genre, "ui", "battle_ui", "commandbar_icon"))
    if command_ui_type == "hero":
        command_ui = battleui.HeroUI(screen_scale)  # hero ui that show leader weapon, health, and portrait
    elif command_ui_type == "command":
        command_ui = battleui.CommandUI(screen_scale)  # Command ui with leader and unit behaviours button
        command_ui.load_sprite(genre_battle_ui_image["command_box"], genre_icon_image)

    col_split_button = battleui.UIButton(genre_battle_ui_image["colsplit_button"],
                                         0)  # unit split by column button
    row_split_button = battleui.UIButton(genre_battle_ui_image["rowsplit_button"], 1)  # unit split by row button

    decimation_button = battleui.UIButton(genre_battle_ui_image["decimation"], 1)

    # Unit inspect information ui
    inspect_button = battleui.UIButton(genre_battle_ui_image["army_inspect_button"],
                                       1)  # unit inspect open/close button

    inspect_ui = battleui.InspectUI(
        genre_battle_ui_image["army_inspect"])  # inspect ui that show subunit in selected unit

    skill_condition_button = [genre_battle_ui_image["skillcond_0"], genre_battle_ui_image["skillcond_1"],
                              genre_battle_ui_image["skillcond_2"], genre_battle_ui_image["skillcond_3"]]
    shoot_condition_button = [genre_battle_ui_image["fire_0"], genre_battle_ui_image["fire_1"]]
    behaviour_button = [genre_battle_ui_image["hold_0"], genre_battle_ui_image["hold_1"],
                        genre_battle_ui_image["hold_2"]]
    range_condition_button = [genre_battle_ui_image["minrange_0"], genre_battle_ui_image["minrange_1"]]
    arc_condition_button = [genre_battle_ui_image["arc_0"], genre_battle_ui_image["arc_1"],
                            genre_battle_ui_image["arc_2"]]
    run_condition_button = [genre_battle_ui_image["runtoggle_0"], genre_battle_ui_image["runtoggle_1"]]
    melee_condition_button = [genre_battle_ui_image["meleeform_0"], genre_battle_ui_image["meleeform_1"],
                              genre_battle_ui_image["meleeform_2"]]
    behaviour_switch_button = [battleui.SwitchButton(skill_condition_button),  # skill condition button
                               battleui.SwitchButton(shoot_condition_button),  # fire at will button
                               battleui.SwitchButton(behaviour_button),  # behaviour button
                               battleui.SwitchButton(range_condition_button),  # shoot range button
                               battleui.SwitchButton(arc_condition_button),  # arc_shot button
                               battleui.SwitchButton(run_condition_button),  # toggle run button
                               battleui.SwitchButton(melee_condition_button)]  # toggle melee mode

    return {"command_ui": command_ui, "col_split_button": col_split_button, "row_split_button": row_split_button,
            "decimation_button": decimation_button, "inspect_button": inspect_button, "inspect_ui": inspect_ui,
            "behaviour_switch_button": behaviour_switch_button}
