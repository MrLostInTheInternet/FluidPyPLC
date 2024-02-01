alphabet = "abcdefghjklmnopqrstuvwyxz"
symbols = "+-"

# check the correct stroke label
def stroke_handler(stroke):
    if len(stroke) > 2 or len(stroke) <= 1:
        print("[!] The piston stroke name must be LETTER+ or LETTER-.")
        return False
    elif stroke == "/":
        print("[!] The sequence is not completed.")
        return False
    elif stroke[0].lower() in alphabet and stroke[1] in symbols:
        return True
    else:
        print("[!] The format of the inserted stroke is NOT correct! E.g. A+ or B- etc..")
        return False

# insert the stroke in the sequence
def sequence_append(stroke, s):
    s.append(stroke.upper())
        
# continuous check of the sequence, by checking if the strokes are inserted correctly or they are repeated in the same position as the last one
def sequence_handler(stroke, s):
    if stroke.upper() not in s:
        return True
    else:
        res = ''.join(s).rindex(stroke.upper()[0]) # reverse index of the last occurence of the stroke label
        if res != 0:
            last_index = round(res/2)
            if stroke.upper() == s[last_index]:
                print("[!] The piston is already in that position.")
                return False
            else:
                return True
        else:
            if stroke.upper() == s[res]:
                print("[!] The piston is already in that position.")
                return False
            else:
                return True

# last check before insertion, by checking if the sequence is completed or there are pistons left in NO-START position
def close_sequence_handler(s):
    return True if len(s)%2 == 0 else False

class Sequence():
    def __init__(self):
        self.run()
    def run(self):
        self.s = []
        stroke = ""
        while True:
            stroke = input("Insert stroke:")
            close_sequence = close_sequence_handler(self.s)
            if stroke == "/" and close_sequence:
                break
            check_stroke = stroke_handler(stroke)
            if check_stroke:
                check_sequence = sequence_handler(stroke, self.s)
            if check_stroke and check_sequence:
                sequence_append(stroke, self.s)
            else:
                continue