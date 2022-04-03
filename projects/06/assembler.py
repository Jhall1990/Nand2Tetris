import sys

import constants

class HackAssembler(object):
    def __init__(self, lines):
        # List of file lines read from the input file
        self.lines = self.sanitize_lines(lines)

        # Map of symbol to decimal value
        self.symbol_table = {}

        # List of compiled lines
        self.compiled = []

        # Value to assign to a new variable, increment each
        # time a new variable is seen.
        self.var_addr = 16

        self.init_symbol_table()

    def init_symbol_table(self):
        for key, val in constants.PRE_DEF_SYMBOLS.items():
            self.symbol_table[key] = val

    def sanitize_lines(self, lines):
        """
        Remove any non-code lines from the input. Code lines are
        (<symbol>), @<val>, and c instructions
        """
        sanitized = []

        for line in lines:
            strp_line = line.strip()

            # // or empty strings are ignored
            if not strp_line or strp_line.startswith("//"):
                continue
            sanitized.append(self.read_ins(strp_line))
        return sanitized

    def read_ins(self, line):
        """
        Read until whitespace or comment. All end of line character should have
        been stripped prior to this,
        """
        ins = []

        for c in line:
            if c in [ "/", " " ]:
                break
            ins.append(c)
        return "".join(ins)

    def compile(self):
        labels = self.first_pass()
        self.remove_labels(labels)
        self.second_pass()

    def first_pass(self):
        labels = []
        for idx, line in enumerate(self.lines):
            if self.is_label_sym(line):
                labels.append(line)
                label = line.strip("()")
                self.symbol_table[label] = idx + 1 - len(labels)
        return labels
    
    def second_pass(self):
        for line in self.lines:
            if self.is_label_sym(line):
                continue
            elif self.is_a_ins(line):
                self.handle_a_ins(line)
            else:
                self.handle_c_ins(line)

    def remove_labels(self, labels):
        for label in labels:
            self.lines.remove(label)

    def write(self, outfile):
        with open(outfile, "w") as f:
            f.write("\n".join(self.compiled))

    def is_label_sym(self, line):
        return line.startswith("(")

    def is_a_ins(self, line):
        return line.startswith("@")

    def handle_a_ins(self, line):
        # Strip of the @
        fmt_line = line[1:]

        # If the value is a number just add the a ins normally.
        # If it's a variable see if it's in the symbol table, if it
        # is use the previous address, otherwise add a new symbol
        # to the table.
        if fmt_line.isdigit():
            self.add_a_ins(int(fmt_line))
        else:
            if fmt_line not in self.symbol_table:
                self.add_variable(fmt_line)
            self.add_a_ins(self.symbol_table[fmt_line])

    def add_a_ins(self, val):
        val_bin = str(bin(int(val)))[2:]
        self.compiled.append(f"{constants.A_PREFIX}{val_bin:0>15}")
    
    def handle_c_ins(self, line):
        # C instructions come in 3 flavors
        # dest=comp;jump
        # dest=comp
        # comp;jump
        if "=" in line and ";" in line:
            dest, rest = line.split("=", 1)
            comp, jump = rest.split(";", 1)
        elif "=" in line:
            dest, comp = line.split("=", 1)
            jump = constants.C_JUMP_NULL
        else:
            comp, jump = line.split(";", 1)
            dest = constants.C_DEST_NULL

        # Make sure each part is valid
        if dest not in constants.C_DEST:
            raise ValueError(f"invalid dest: {dest}")
        if comp not in constants.C_COMP:
            raise ValueError(f"invalid comp: {comp}")
        if jump not in constants.C_JUMP:
            raise ValueError(f"invalid jump: {jump}")

        self.add_c_ins(dest, comp, jump)

    def add_c_ins(self, dest, comp, jump):
        # Get the parts
        dest_bits = constants.C_DEST.get(dest)
        comp_bits = constants.C_COMP.get(comp)
        jump_bits = constants.C_JUMP.get(jump)

        self.compiled.append(f"{constants.C_PREFIX}{comp_bits}{dest_bits}{jump_bits}")

    def add_variable(self, val):
        self.symbol_table[val] = self.var_addr
        self.var_addr += 1

def read_file(filename):
    with open(filename, "r") as f:
        return f.readlines()

if __name__ == "__main__":
    infile = sys.argv[1]
    outfile = sys.argv[2]

    lines = read_file(infile)
    asm = HackAssembler(lines)
    asm.compile()
    asm.write(outfile)