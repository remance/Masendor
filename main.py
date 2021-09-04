import configparser
import os.path
import sys
import traceback

import screeninfo
from gamescript import start

screen = screeninfo.get_monitors()[0]

screenWidth = int(screen.width)
screenHeight = int(screen.height)

config = configparser.ConfigParser()
try:
    config.read_file(open("configuration.ini"))  # read config file
except Exception:  # Create config file if not found with the default
    config = configparser.ConfigParser()
    config["DEFAULT"] = {"screenwidth": screenWidth, "screenheight": screenHeight, "fullscreen": "0",
                         "playername": "Noname", "soundvolume": "100.0", "musicvolume": "0.0",
                         "voicevolume": "0.0", "maxfps": "60", "ruleset": "1"}
    with open("configuration.ini", "w") as cf:
        config.write(cf)
    config.read_file(open("configuration.ini"))

if __name__ == "__main__":
    try:  # for printing error log when error exception happen
        main_dir = os.path.split(os.path.abspath(__file__))[0]
        runmenu = start.Mainmenu(main_dir, config)
        runmenu.run()
    except Exception:  # Save error output to txt file
        traceback.print_exc()
        f = open("error_report.txt", "w")
        sys.stdout = f
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print("".join("!! " + line for line in lines))  # Log it or whatever here
        f.close()
