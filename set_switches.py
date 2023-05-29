from set_groups import groups_2D
from get_sequence import s
from copy import deepcopy

# array rotation to the right by 1, the last limit switch will activate the sequence, together with the Start button
def rotate(array, n):
    return array[n:] + array[:n]

# the function set the switches labels, e.g. a0, a1, etc ..
def switches_labels():
    switch_labels = rotate(s, -1)
    switch_labels = [switch.lower() for switch in switch_labels]
    switch_labels = [words.replace("-", "0") for words in switch_labels]
    switch_labels = [words.replace("+", "1") for words in switch_labels]
    return switch_labels

# function to set the limit switches groups by copying the same format of the sequence's groups
def copy_array(array):
    new_array = deepcopy(groups_2D)
    z = 0
    for i in range(len(groups_2D)):
        for j in range(len(groups_2D[i])):
            new_array[i][j] = array[z]
            z += 1
    return new_array

class Switches():
    def __init__(self):
        self.run()

    def run(self):
        global limit_switches
        global limit_s_groups
        limit_switches = switches_labels()
        limit_s_groups = copy_array(limit_switches)

Switches()
