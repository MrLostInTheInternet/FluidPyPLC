from get_sequence import Sequence
from set_groups import Groups
from set_switches import Switches
from data import Data
from diagrams import diagrams
from plc import Plc

def __main__():
    sequence = Sequence()
    s = sequence.s
    diagrams(s)
    Plc(s)
    
__main__() 