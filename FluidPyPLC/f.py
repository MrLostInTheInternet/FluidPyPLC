#!/usr/bin/env python3

from tkinter import *
from PIL import Image, ImageTk

from FluidPyPLC.get_sequence import Sequence
from FluidPyPLC.diagrams import diagrams
from FluidPyPLC.plc import Plc
from FluidPyPLC.GUI import Gui

import argparse
import subprocess
import textwrap

# function to start the terminal version
def terminal():
    sequence = Sequence()
    s = sequence.s
    diagrams(s)
    Plc(s)

# args management
def main():
    parser = argparse.ArgumentParser(
        description='FluidPyPLC',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
        f.py --gui # to use the user interface mode
        f.py -t # to use the terminal version
        f.py --plc # to display the plc ST code
        ''')
    )
    parser.add_argument('-g', '--gui', action='store_true', help='gui mode')
    parser.add_argument('-t', '--terminal', action='store_true', help='terminal mode')
    parser.add_argument('--plc', action='store_true', help='show plc code')
    args = parser.parse_args()
    if args.gui:
        # gui mode
        gui = Gui()
        gui.gui_mode()
        exit(0)
    elif args.terminal:
        # terminal mode
        terminal()
        exit(0)
    elif args.plc:
        try:
            # open plc ST code with notepad
            subprocess.call(['notepad.exe', './plc/plc.st'])
        except Exception as e:
            print("There is a problem opening the file:")
            print(e)
    else:
        # default argument
        terminal()
        exit(0)

main()