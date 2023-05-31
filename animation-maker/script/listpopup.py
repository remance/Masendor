import os
import sys

from engine.uimenu.uimenu import NameList

current_dir = os.path.split(os.path.abspath(__file__))[0]
main_dir = current_dir[:current_dir.rfind("\\") + 1].split("\\")
main_dir = ''.join(stuff + "\\" for stuff in main_dir[:-2])  # one folder further back
sys.path.insert(1, main_dir)


def setup_list(item_class, current_row, show_list, item_group, box, ui_class,
               screen_scale, layer=1, remove_old=True, old_list=None):
    """generate list of list item"""
    width_adjust = screen_scale[0]
    height_adjust = screen_scale[1]
    row = 5 * height_adjust
    column = 5 * width_adjust
    pos = box.rect.topleft
    if current_row > len(show_list) - box.max_row_show:
        current_row = len(show_list) - box.max_row_show

    if len(item_group) > 0 and remove_old:  # remove previous sprite in the group before generate new one
        for stuff in item_group:
            stuff.kill()
            del stuff
    add_row = 0
    for index, item in enumerate(show_list):
        if index >= current_row:
            item_group.add(item_class(box, (pos[0] + column, pos[1] + row), item,
                                      layer=layer))  # add new subsection sprite to group
            row += (30 * height_adjust)  # next row
            add_row += 1
            if add_row > box.max_row_show:
                break  # will not generate more than space allowed

        ui_class.add(*item_group)
    if old_list is not None:
        for item in item_group:
            if item.name in old_list:
                item.select()


def list_scroll(mouse_scroll_up, mouse_scroll_down, listbox, current_row, name_list, name_group,
                ui_object, screen_scale, layer=19, old_list=None):
    if mouse_scroll_up:
        current_row -= 1
    elif mouse_scroll_down:
        current_row += 1

    if current_row < 0:
        current_row = 0
    elif current_row + listbox.max_row_show - 1 >= len(name_list):
        current_row -= 1
    else:
        setup_list(NameList, current_row, name_list, name_group, listbox, ui_object, screen_scale, layer=layer,
                   old_list=old_list)
        listbox.scroll.change_image(new_row=current_row, row_size=len(name_list))

    return current_row


def popup_list_open(popup_listbox, popup_namegroup, ui_class,
                    action, new_rect, new_list, ui_type, screen_scale, current_row=0):
    """Move popup_listbox and scroll sprite to new location and create new name list based on type"""

    if ui_type == "top":
        popup_listbox.rect = popup_listbox.image.get_rect(topleft=new_rect)
    elif ui_type == "bottom":
        popup_listbox.rect = popup_listbox.image.get_rect(bottomleft=new_rect)
    popup_listbox.namelist = new_list
    popup_listbox.action = action
    setup_list(NameList, current_row, new_list, popup_namegroup,
               popup_listbox, ui_class, screen_scale, layer=21)

    popup_listbox.scroll.pos = popup_listbox.rect.topright  # change position variable
    popup_listbox.scroll.rect = popup_listbox.scroll.image.get_rect(topleft=popup_listbox.rect.topright)
    popup_listbox.scroll.change_image(new_row=current_row, row_size=len(new_list))
    ui_class.add(popup_listbox, *popup_namegroup, popup_listbox.scroll)

    popup_listbox.type = ui_type
