import datetime
from inspect import stack
from pygame import sprite


def empty_method(self, *args):
    if hasattr(self, 'error_log'):
        error_text = "{0} -- {1}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                           "Empty method is called") + \
                     str(stack()[1][1]) + "At Line" + str(stack()[1][2]) + ":" + \
                     str(stack()[1][3])
        # print(error_text)
        self.error_log.write(error_text)


def change_group(item, group, change):
    """Change group of the item, use for multiple change in loop"""
    if change == "add":
        group.add(item)
    elif change == "remove":
        group.remove(item)


def clean_group_object(groups):
    """Clean all attributes of every object in group in list"""
    for group in groups:
        if len(group) > 0:
            if type(group) == sprite.Group or type(group) == list or type(group) == tuple:
                for stuff in group:
                    clean_object(stuff)
                group.empty()
            elif type(group) == dict:
                for stuff in group.values():
                    for item in stuff:
                        clean_object(item)
            else:
                group.kill()
                group.delete()
                del group


def clean_object(this_object):
    """Clean all attributes of the object and delete it"""
    this_object.kill()
    for attribute in tuple(this_object.__dict__.keys()):
        this_object.__delattr__(attribute)
    del this_object


def edit_config(section, option, value, filename, config):
    """
    Edit config file at specific section
    :param section: Section name
    :param option: Part that will be changed
    :param value: Changed value in string text
    :param filename: Config file name
    :param config: Config object
    :return:
    """
    config.set(section, option, str(value))
    with open(filename, "w") as configfile:
        config.write(configfile)
