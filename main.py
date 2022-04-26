import os.path
import sys
import traceback

from gamescript import start

main_dir = os.path.split(os.path.abspath(__file__))[0]

if __name__ == "__main__":
    try:  # for printing error log when error exception happen
        runmenu = start.Game(main_dir)
    except Exception:  # Save error output to txt file
        traceback.print_exc()
        f = open("error_report.txt", "w")
        sys.stdout = f
        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        print("".join("!! " + line for line in lines))  # Log it or whatever here
        f.close()
