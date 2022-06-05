def switch_faction(self, old_group, new_group, old_pos_list, enactment):
    """Change army group and game_id when change side"""
    self.colour = (144, 167, 255)  # team1 colour
    self.control = True  # TODO need to change later when player can choose team

    if self.team == 2:
        self.team = 1  # change to team 1
    else:  # originally team 1, new team would be 2
        self.team = 2  # change to team 2
        self.colour = (255, 114, 114)  # team2 colour
        if enactment is False:
            self.control = False

    old_group.remove(self)  # remove from old team group
    new_group.append(self)  # add to new team group
    old_pos_list.pop(self.game_id)  # remove from old pos list
    # self.changescale() # reset scale to the current zoom
    self.icon.change_image(change_side=True)  # change army icon to new team
