from copy import deepcopy

# array rotation to the right by 1, the last limit switch will activate the sequence, together with the Start button
def rotate(array, n):
    return array[n:] + array[:n]

# the function set the switches labels, e.g. a0, a1, etc ..
def switches_labels(s):
    switch_labels = rotate(s, -1)
    switch_labels = [switch.lower() for switch in switch_labels]
    switch_labels = [words.replace("-", "0") for words in switch_labels]
    switch_labels = [words.replace("+", "1") for words in switch_labels]
    return switch_labels

# function to set the limit switches groups by copying the same format of the sequence's groups
def copy_array(array, groups):
    new_array = deepcopy(groups)
    z = 0
    for i in range(len(groups)):
        for j in range(len(groups[i])):
            new_array[i][j] = array[z]
            z += 1
    return new_array

class Switches():
    def __init__(self, s, g):
        self.run(s, g)

    def run(self, s, g):
        self.limit_switches = switches_labels(s)
        self.limit_s_groups = copy_array(self.limit_switches, g)
