import csv
import os


def save_custom_unit_preset(self):
    with open(os.path.join("profile", "unitpreset", str(self.ruleset), "custom_unitpreset.csv"), "w", encoding='utf-8', newline="") as csvfile:
        filewriter = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        save_list = self.custom_unit_preset_list.copy()
        del save_list["New Preset"]
        final_save = [["presetname", "subunitline1", "subunitline2", "subunitline3", "subunitline4", "subunitline5", "subunitline6",
                       "subunitline7", "subunitline8", "leader", "leaderposition", "faction"]]
        for item in list(save_list.items()):
            sub_item = [small_item for small_item in item[1]]
            item = [item[0]] + sub_item
            final_save.append(item)
        for row in final_save:
            filewriter.writerow(row)
        csvfile.close()