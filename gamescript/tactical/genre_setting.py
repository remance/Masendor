"""For keeping variable related to genre specific"""

unit_size = (8, 8)
troop_size_adjustable = False  # troop always at size 1

unit_behaviour_wheel = {}  # player unit behaviour control via wheel ui, not used in tactical mode as it use different control and ui

# dict of variable that will get add into object in game
object_variable = {("self", "object"): {"add_troop_number_sprite": True,  # troop number sprite
                                        "char_select": False,
                                        # not include character screen, player control multiple units
                                        "leader_sprite": False,  # leader has its own animation sprite
                                        "troop_sprite_size": (200, 200),  # troop animation sprite size
                                        "troop_size_adjustable": troop_size_adjustable,
                                        "unit_size": unit_size,  # maximum array size unit can contain subunits
                                        "command_ui_type": "command",  # type of command bar, either hero or rts command
                                        },
                   ("battle_game", "self-object"): {"start_zoom_mode": "Free",  # rts style camera
                                                    "start_camera_zoom": 1,  # start with the furthest zoom
                                                    "max_camera_zoom": 10,  # maximum zoom level
                                                    "troop_size_adjustable": troop_size_adjustable,
                                                    "time_speed_scale": 10,  # how fast time fly in battle
                                                    "unit_behaviour_wheel": unit_behaviour_wheel,
                                                    # player unit behaviour control via wheel ui
                                                    "unit_size": unit_size,
                                                    # maximum array size unit can contain subunits
                                                    },
                   ("unit", "class"): {"unit_size": unit_size,  # maximum array size unit can contain subunits
                                       },
                   ("subunit", "class"): {"dmg_include_leader": True,  # include leader in damage calculation
                                          }
                   }

event_log_top = "page up"
event_log_bottom = "page down"
increase_game_time = "keypad plus"
decrease_game_time = "keypad minus"
pause_game_time = "p"
toggle_unit_number = "o"

up = "w"
down = "s"
left = "a"
right = "d"
command_menu = "q"
leader_skill = "r"
troop_skill = "t"
map_mode = "tab"
action_1 = "left mouse button"
action_2 = "right mouse button"
