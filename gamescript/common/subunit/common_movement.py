rotation_list = (90, 120, 45, 0, -90, -45, -120, 180)
rotation_name = ("l_side", "l_sideup", "l_sidedown", "front", "r_side","r_sideup","r_sidedown", "back")
rotation_dict = {key: rotation_name[index] for index, key in enumerate(rotation_list)}
