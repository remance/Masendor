"""For keeping variable related to genre specific"""

unit_behaviour_wheel = {}  # player unit behaviour control via wheel ui, not used in tactical mode as it use different control and ui

# dict of variable that will get add into object in game
object_variable = {("self", "object"): {"char_select": False,  # not include character screen, player control multiple units
                                        "leader_sprite": False,  # leader has its own animation sprite
                                        "troop_sprite_size": (200, 200),  # troop animation sprite size
                                        },
                   ("battle_game", "self-object"): {"start_zoom_mode": "Free",  # rts style camera
                                                    "start_zoom": 1,  # start with the furthest zoom
                                                    "troop_size_adjustable": False,  # troop always at size 1
                                                    "time_speed_scale": 10,  # how fast time fly in battle
                                                    "add_troop_number_sprite": True,  # troop number sprite
                                                    "unit_behaviour_wheel": unit_behaviour_wheel  # player unit behaviour control via wheel ui
                                                    },
                   ("unit", "class"): {"unit_size": (8, 8)  # maximum array size unit can contain subunits
                                       },
                   ("subunit", "class"): {"dmg_include_leader": True,  # include leader in damage calculation
                                          "stat_use_troop_number": True  # calculate troop number in damage calculation
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
