class Sequence:
    def __init__(self):
        self.alphabet = "abcdefghjklmnopqrstuvwyxz"
        self.symbols = "+-"
        self.sequence = []

    def run(self):
        while True:
            stroke = input("Insert stroke:")
            if stroke == "/" and self.close_sequence_handler():
                break

            stroke_check = self.stroke_handler(stroke)
            if stroke_check and self.sequence_handler(stroke):
                self.sequence_append(stroke)

    def stroke_handler(self, stroke):
        if len(stroke) != 2:
            print("[!] The piston stroke name must be exactly 2 characters (e.g., A+, B-).")
            return False
        elif stroke == "/":
            print("[!] The sequence is not completed.")
            return False
        elif stroke[0].lower() in self.alphabet and stroke[1] in self.symbols:
            return True
        else:
            print("[!] Invalid stroke format. Expected: LETTER+ or LETTER-.")
            return False

    def sequence_append(self, stroke):
        self.sequence.append(stroke.upper())

    def sequence_handler(self, stroke):
        stroke_upper = stroke.upper()
        if stroke_upper not in self.sequence:
            return True

        last_index = ''.join(self.sequence).rfind(stroke_upper[0]) // 2
        if self.sequence[last_index] == stroke_upper:
            print("[!] The piston is already in that position.")
            return False
        return True

    def close_sequence_handler(self):
        return len(self.sequence) % 2 == 0
