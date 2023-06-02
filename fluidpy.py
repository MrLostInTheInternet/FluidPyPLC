from tkinter import *
from PIL import Image, ImageTk

from get_sequence import Sequence
from diagrams import diagrams
from plc import Plc
from GUI import Gui

import argparse
import subprocess
import textwrap

# class to define the plot rendering and opening window
class Window(Frame):
    def __init__(self,  master=None):
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=1)
        
        load = Image.open("./Plots/diagram_fases.png")
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
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='FluidPy 2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example:
        fluid.py --gui # to use the user interface mode
        fluid.py -t # to use the terminal version
        fluid.py --plot # to display the Diagrams's fases
        fluid.py --plc # to display the plc ST code
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
    elif args.terminal:
        # terminal mode
        terminal()
    elif args.plot:
        # show plot
        show_plot()
    elif args.plc:
        try:
            # open plc ST code with notepad
            subprocess.call(['notepad.exe', './plc/plc.txt'])
        except:
            print("There is a problem opening the file.")
    else:
        # default argument
        terminal()