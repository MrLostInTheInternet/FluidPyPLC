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

# class to define the plot rendering and opening window
class Window(Frame):
    def __init__(self,  master=None):
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=1)
        
        load = Image.open("./Plots/phases_diagram.png")
        render = ImageTk.PhotoImage(load)
        img = Label(self, image=render)
        img.image = render
        img.place(x=0, y=0)

# function to start the terminal version
def terminal():
    sequence = Sequence()
    s = sequence.s
    diagrams(s)
    Plc(s)

# show Diagram's fases
def show_plot():
    root = Tk()
    app = Window(root)
    root.wm_title("Diagram's fases")
    root.geometry("600x500")
    root.mainloop()

# args management
def main():
    parser = argparse.ArgumentParser(
        description='FluidPyPLC',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
        f.py --gui # to use the user interface mode
        f.py -t # to use the terminal version
        f.py --plot # to display the Diagrams's fases
        f.py --plc # to display the plc ST code
        ''')
    )
    parser.add_argument('-g', '--gui', action='store_true', help='gui mode')
    parser.add_argument('-t', '--terminal', action='store_true', help='terminal mode')
    parser.add_argument('--plot', action='store_true', help='show plot')
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
    elif args.plot:
        # show plot
        try:
            show_plot()
            exit(0)
        except:
            print("There is no folder Plots. Create one.")
    elif args.plc:
        try:
            # open plc ST code with notepad
            subprocess.call(['notepad.exe', './plc/plc.st'])
        except:
            print("There is a problem opening the file.")
    else:
        # default argument
        terminal()
        exit(0)

main()