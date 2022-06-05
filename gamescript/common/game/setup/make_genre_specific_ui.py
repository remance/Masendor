from gamescript import battleui
from gamescript.common import utility

load_images = utility.load_images


def make_genre_specific_ui(main_dir, screen_scale, genre):
    genre_battle_ui_image = load_images(main_dir, screen_scale, [genre, "ui", "battle_ui"], load_order=False)

    genre_icon_image = load_images(main_dir, screen_scale, [genre, "ui", "battle_ui",
                                                            "commandbar_icon"], load_order=False)
    command_ui = battleui.CommandBar()  # Command ui with leader and unit behaviours button
    command_ui.load_sprite(genre_battle_ui_image["command_box.png"], genre_icon_image)

    col_split_button = battleui.UIButton(genre_battle_ui_image["colsplit_button.png"],
                                              0)  # unit split by column button
    row_split_button = battleui.UIButton(genre_battle_ui_image["rowsplit_button.png"], 1)  # unit split by row button

    decimation_button = battleui.UIButton(genre_battle_ui_image["decimation.png"], 1)

    # Unit inspect information ui
    inspect_button = battleui.UIButton(genre_battle_ui_image["army_inspect_button.png"], 1)  # unit inspect open/close button

    inspect_ui = battleui.InspectUI(genre_battle_ui_image["army_inspect.png"])  # inspect ui that show subunit in selected unit

    skill_condition_button = [genre_battle_ui_image["skillcond_0.png"], genre_battle_ui_image["skillcond_1.png"],
                              genre_battle_ui_image["skillcond_2.png"], genre_battle_ui_image["skillcond_3.png"]]
    shoot_condition_button = [genre_battle_ui_image["fire_0.png"], genre_battle_ui_image["fire_1.png"]]
    behaviour_button = [genre_battle_ui_image["hold_0.png"], genre_battle_ui_image["hold_1.png"],
                        genre_battle_ui_image["hold_2.png"]]
    range_condition_button = [genre_battle_ui_image["minrange_0.png"], genre_battle_ui_image["minrange_1.png"]]
    arc_condition_button = [genre_battle_ui_image["arc_0.png"], genre_battle_ui_image["arc_1.png"],
                            genre_battle_ui_image["arc_2.png"]]
    run_condition_button = [genre_battle_ui_image["runtoggle_0.png"], genre_battle_ui_image["runtoggle_1.png"]]
    melee_condition_button = [genre_battle_ui_image["meleeform_0.png"], genre_battle_ui_image["meleeform_1.png"],
                              genre_battle_ui_image["meleeform_2.png"]]
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

