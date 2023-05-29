from get_sequence import s
import numpy as np

# function that founds the number of block in the sequence
def number_of_blocks():
    seen = set()
    z = 0
    for i in range(len(s)):
        if s[i][0] in seen:
            z += 1
            seen = set()
            seen.add(s[i][0])
        else:
            seen.add(s[i][0])
    return z

# class that creates the sequence's groups
class Groups():
    def __init__(self):
        self.run()

    def run(self):
        global groups_2D
        seen = set()
        n_blocks = number_of_blocks()
        groups_2D = [[] for _ in range(n_blocks + 1)]
        z = 0
        for i in range(len(s)):
            if s[i][0] in seen:
                z += 1
                seen = set()
                groups_2D[z].append(s[i])
                seen.add(s[i][0])
            else:
                groups_2D[z].append(s[i])
                seen.add(s[i][0])

Groups()