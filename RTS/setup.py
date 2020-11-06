import sys
from cx_Freeze import setup, Executable

setup(
    name = "Masendor",
    version = "0.5.1",
    description = "Test EXE",
    executables = [Executable("main.py", base = "Win32GUI")])