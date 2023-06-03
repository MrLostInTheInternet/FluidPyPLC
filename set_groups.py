# function that founds the number of block in the sequence
def number_of_blocks(s):
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
    def __init__(self, s):
        self.run(s)

    def run(self, s):
        seen = set()
        n_blocks = number_of_blocks(s)
        self.groups_2D = [[] for _ in range(n_blocks + 1)]
        z = 0
        for i in range(len(s)):
            if s[i][0] in seen:
                z += 1
                seen = set()
                self.groups_2D[z].append(s[i])
                seen.add(s[i][0])
            else:
                self.groups_2D[z].append(s[i])
                seen.add(s[i][0])
