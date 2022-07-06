"""For keeping variable related to genre specific"""

unit_size = (5, 5)

unit_behaviour_wheel = {"Main": {"Skill": "Skill", "Shift Line": "Shift Line", "Range Attack": "Range Attack",
                                 "Behaviour": "Behaviour", "Command": "Command", "Formation": "Formation",
                                 "Equipment": "Equipment", "Setting": "Setting"},
                        "Skill": {"Leader Skill 1": "Leader Skill 1", "Leader Skill 2": "Leader Skill 2",
                                  "Troop Skill 1": "Troop Skill 1", "Troop Skill 2": "Troop Skill 2"},
                        "Shift Line": {"Front To Back": "Front To Back", "Left To Right": "Left To Right",
                                       "Back To Front": "Back To Front", "Right To Left": "Right To Left"},
                        "Range Attack": {"Manual Aim": "Manual Aim", "Fire At Will": "Fire At Will",
                                         "Volley": "Volley", "Manual Only": "Manual Only"},
                        "Behaviour": {"Hold": "Hold", "Follow": "Follow", "Free": "Free", "Retreat": "Retreat"},
                        "Command": {"Offensive": "Offensive", "Defensive": "Defensive", "Skirmish": "Skirmish",
                                    "Protect Me": "Protect Me", "Follow Unit": "Follow Unit", "Free": "Free",
                                    "Hold Location": "Hold Location"},
                        "Formation": {"Formation Style": "Formation Style", "Formation Phase": "Formation Phase",
                                      "Formation List": "Formation List", "Original": "Original",
                                      },
                        "Formation Phase": {"Skirmish Phase": "Skirmish Phase", "Melee Phase": "Melee Phase",
                                            "Bombard Phase": "Bombard Phase", "Heroic Phase": "Heroic Phase"
                                            },
                        "Formation Style": {"Infantry Inner": "Infantry Inner", "Cavalry Inner": "Cavalry Inner",
                                            "Infantry Flank": "Infantry Flank", "Cavalry Flank": "Cavalry Flank"},

                        "Equipment": {"Equip Primary": "Equip Primary", "Equip Secondary": "Equip Secondary",
                                      "Troop Equip Primary": "Troop Equip Primary",
                                      "Troop Equip Secondary": "Troop Equip Secondary",
                                      "Troop Equip Melee": "Troop Equip Melee",
                                      "Troop Equip Range": "Troop Equip Range"},
                        "Setting": {"Height Map": "Height Map", "UI Hide": "UI Hide", "UI Show": "UI Show"}}

# Dict of variable that will get add into object in game, key use two items tuple for indication of adding
# object is as implied will add variable to object with the name of first item, self-object will add to object in self,
# class will add variable to class in module file of the same name
object_variable = {("self", "object"): {"char_select": True,  # include character specific screen,
                                        "leader_sprite": True,  # leader has its own animation sprite
                                        "troop_sprite_size": (250, 250),  # troop animation sprite size
                                        "unit_size": unit_size  # maximum array size unit can contain subunits
                                        },
                   ("battle_game", "self-object"): {"start_zoom_mode": "Follow",  # one character control camera
                                                    "start_zoom": 10,  # start with the closest zoom
                                                    "troop_size_adjustable": True,  # troop can be different size and affect sprite size
                                                    "time_speed_scale": 30,  # how fast time fly in battle
                                                    "add_troop_number_sprite": False,  # troop number sprite not use in arcade mode
                                                    "unit_behaviour_wheel": unit_behaviour_wheel  # player unit behaviour control via wheel ui
                                                    },
                   ("unit", "class"): {"unit_size": unit_size,  # maximum array size unit can contain subunits
                                       },
                   ("subunit", "class"): {"dmg_include_leader": False,  # not include leader in damage calculation, leader is subunit
                                          "stat_use_troop_number": False,  # arcade mode count one subunit as one troop
                                          }
                   }

# Default keyboard binding
up = "w"
down = "s"
left = "a"
right = "d"
command_menu = "q"
leader_skill = "r"
troop_skill = "t"
map_mode = "tab"
action_0 = "left mouse button"
action_1 = "right mouse button"

# Default controller binding
controller_up = "w"
controller_down = "s"
controller_left = "a"
controller_right = "d"
controller_command_menu = "q"
controller_leader_skill = "r"
controller_troop_skill = "t"
controller_map_mode = "tab"
controller_action_0 = ""
controller_action_1 = ""
