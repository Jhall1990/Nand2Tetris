import constants

LABEL = 0
FUNCTION = "Sys"


def get_label():
    global LABEL
    label = LABEL
    LABEL += 1
    return label


def set_function(function):
    global FUNCTION
    FUNCTION = function


class Bootstrap(object):
    def write(self):
        lines = ["// Bootstrap code"]
        lines += ["@256"]
        lines += ["D=A"]
        lines += ["@SP"]
        lines += ["M=D"]
        lines += CallCommand(FUNCTION, "Sys.init", 0).to_asm()
        return "\n".join(lines) + "\n"

class Command(object):
    # Mem segment pointers
    TEMP_REG = "@R15"
    MEM_POINT = {
        constants.MEM_LOCAL: "@LCL",
        constants.MEM_ARG: "@ARG",
        constants.MEM_THIS: "@THIS",
        constants.MEM_THAT: "@THAT",
        constants.MEM_TEMP: 5,
    }

    def __init__(self, filename=""):
        self.filename = filename

    def to_asm(self):
        raise NotImplemented("write must be implemented by subclasses")

    def write(self):
        return "\n".join(self.to_asm()) + "\n"


class MemoryCommand(Command):
    def __init__(self, filename, op, loc, addr):
        super().__init__(filename)
        self.op = op
        self.loc = loc
        self.addr = int(addr)

    def to_asm(self):
        handlers = {
            constants.PUSH_CMD: self._push,
            constants.POP_CMD: self._pop,
        }

        header = f"// {self.op} {self.loc} {self.addr}"
        handler = handlers.get(self.op)

        if not handler:
            raise ValueError(f"{self.op} is not a valid location to push/pop from")
        return handler([header])

    def _push(self, lines):
        mem_pntr = self._mem_pointer()            
        lines += [f"{mem_pntr}"]

        if self.loc == constants.MEM_CONSTANT:
            lines += ["D=A"]
        elif self.loc in [constants.MEM_TEMP, constants.MEM_POINTER, constants.MEM_STATIC]:
            lines += ["D=M"]
        else:
            lines += ["D=M"]
            lines += [f"@{self.addr}"]
            lines += ["A=D+A"]
            lines += ["D=M"]

        lines += ["@SP"]
        lines += ["A=M"]
        lines += ["M=D"]
        lines += ["@SP"]
        lines += ["M=M+1"]
        return lines

    def _pop(self, lines):
        mem_pntr = self._mem_pointer()
        lines += [f"{mem_pntr}"]

        if self.loc in [constants.MEM_TEMP, constants.MEM_POINTER, constants.MEM_STATIC]:
            lines += ["D=A"]
        else:
            lines += ["D=M"]
            lines += [f"@{self.addr}"]
            lines += ["D=D+A"]

        lines += [f"{self.TEMP_REG}"]
        lines += ["M=D"]
        lines += ["@SP"]
        lines += ["M=M-1"]
        lines += ["A=M"]
        lines += ["D=M"]
        lines += [f"{self.TEMP_REG}"]
        lines += ["A=M"]
        lines += ["M=D"]
        return lines

    def _mem_pointer(self):
        if self.loc == constants.MEM_CONSTANT:
            return f"@{self.addr}"
        elif self.loc == constants.MEM_STATIC:
            return f"@{self.filename}.{self.addr}"
        elif self.loc == constants.MEM_TEMP:
            return f"@{self.MEM_POINT[self.loc] + self.addr}"
        elif self.loc == constants.MEM_POINTER and self.addr == 0:
            return self.MEM_POINT[constants.MEM_THIS]
        elif self.loc == constants.MEM_POINTER and self.addr == 1:
            return self.MEM_POINT[constants.MEM_THAT]
        else:
            return self.MEM_POINT[self.loc]


class ArithmeticCommand(Command):
    def __init__(self, op):
        super().__init__()
        self.op = op

    def to_asm(self):
        header = f"// {self.op}"
        if self.op in [constants.OPR_ADD, constants.OPR_SUB,
                       constants.OPR_AND, constants.OPR_OR]:
            return self.handle_math([header])
        elif self.op in [constants.OPR_EQ, constants.OPR_GT, constants.OPR_LT]:
            return self.handle_logic([header])
        else:
            return self.handle_not_and_neg([header])

    def handle_math(self, lines):
        if self.op == constants.OPR_ADD:
            opr = "D=D+M"
        elif self.op == constants.OPR_SUB:
            opr = "D=M-D"
        elif self.op == constants.OPR_AND:
            opr = "D=M&D"
        else:
            opr = "D=M|D"

        lines += ["@SP"]
        lines += ["AM=M-1"]
        lines += ["D=M"]
        lines += ["@SP"]
        lines += ["M=M-1"]
        lines += ["A=M"]
        lines += [opr]
        lines += ["@SP"]
        lines += ["M=M+1"]
        lines += ["A=M-1"]
        lines += ["M=D"]
        return lines

    def handle_logic(self, lines):
        label = get_label()

        if self.op == constants.OPR_EQ:
            opr = "D;JEQ"
        elif self.op == constants.OPR_GT:
            opr = "D;JLT"
        else:
            opr = "D;JGT"

        lines += ["@SP"]
        lines += ["AM=M-1"]
        lines += ["D=M"]
        lines += ["@SP"]
        lines += ["AM=M-1"]
        lines += ["D=D-M"]
        lines += ["M=-1"]
        lines += [f"@TRUE.{label}"]
        lines += [opr]
        lines += ["@SP"]
        lines += ["A=M"]
        lines += ["M=0"]
        lines += [f"(TRUE.{label})"]
        lines += ["@SP"]
        lines += ["M=M+1"]
        return lines

    def handle_not_and_neg(self, lines):
        if self.op == constants.OPR_NOT:
            opr = "M=!M"
        else:
            opr = "M=-M"

        lines += ["@SP"]
        lines += ["A=M-1"]
        lines += [opr]
        return lines


class ControlCommand(Command):
    def __init__(self, filename, command, name):
        super().__init__(filename)
        self.cmd = command
        self.name = name
        self.label = self.create_label(name)

    def to_asm(self):
        header = f"// {self.cmd} {self.name}"

        if self.cmd == constants.LABEL_CMD:
            return self.handle_label([header])
        elif self.cmd == constants.GOTO_CMD:
            return self.handle_goto([header])
        else:
            return self.handle_if_goto([header])

    def handle_label(self, lines):
        lines += [f"({self.label})"]
        return lines

    def handle_goto(self, lines):
        lines += [f"@{self.label}"]
        lines += ["0;JMP"]
        return lines
    
    def handle_if_goto(self, lines):
        lines += ["@SP"]
        lines += ["AM=M-1"]
        lines += ["D=M"]
        lines += [f"@{self.label}"]
        lines += ["D;JNE"]
        return lines

    def create_label(self, label):
        return f"{FUNCTION}${label}"

class FuncCallAndReturnCommand(Command):
    def push(self, addr, comp):
        lines = [f"@{addr}"]
        lines += [f"D={comp}"]
        lines += ["@SP"]
        lines += ["A=M"]
        lines += ["M=D"]
        lines += ["@SP"]
        lines += ["M=M+1"]
        return lines


class FunctionCommand(FuncCallAndReturnCommand):
    def __init__(self, filename, name, nargs):
        super().__init__(filename)
        self.name = name
        self.nargs = int(nargs)
        set_function(name)
        self.label = self.create_label()

    def to_asm(self):
        lines = [f"// function {self.name} {self.nargs}"]
        lines += [f"({self.label})"]
        for i in range(self.nargs):
            lines += self.push(0, "A")
        return lines

    def create_label(self):
        if self.name.startswith(self.filename):
            return f"{self.name}"
        return f"{self.filename}.{self.name}"


class CallCommand(FuncCallAndReturnCommand):
    def __init__(self, filename, name, nargs):
        super().__init__(filename)
        self.name = name
        self.nargs = int(nargs)
        self.call_label = self.create_call_label()
        self.return_label = self.create_return_label()

    def to_asm(self):
        lines = [f"// call {self.name} {self.nargs}"]

        # Push return addr, lcl, arg, this, that
        lines += self.push(self.return_label, "A")
        lines += self.push("LCL", "M")
        lines += self.push("ARG", "M")
        lines += self.push("THIS", "M")
        lines += self.push("THAT", "M")

        # arg = SP - 5 - nargs
        lines += ["@SP"]
        lines += ["D=M"]
        lines += ["@5"]
        lines += ["D=D-A"]
        lines += [f"@{self.nargs}"]
        lines += ["D=D-A"]
        lines += ["@ARG"]
        lines += ["M=D"]

        # LCL = SP
        lines += ["@SP"]
        lines += ["D=M"]
        lines += ["@LCL"]
        lines += ["M=D"]

        # Hand control to function
        lines += [f"@{self.call_label}"]
        lines += ["0;JMP"]

        # Return address
        lines += [f"({self.return_label})"]

        return lines

    def create_call_label(self):
        return f"{self.name}"

    def create_return_label(self):
        label = get_label()
        if FUNCTION.startswith(self.filename):
            return f"{FUNCTION}$ret.{label}"
        return f"{self.filename}.{FUNCTION}$ret.{label}"

class ReturnCommand(FuncCallAndReturnCommand):
    def to_asm(self):
        label = get_label()
        lines = [f"// return"]

        # Endframe = LCL
        lines += ["@LCL"]
        lines += ["D=M"]
        lines += [f"@ENDFRAME.{label}"]
        lines += ["M=D"]

        # retaddr = *(endframe-5)
        lines += ["@5"]
        lines += ["AD=D-A"]
        lines += ["D=M"]
        lines += [f"@RETADDR.{label}"]
        lines += ["M=D"]

        # *ARG = pop()
        lines += ["@SP"]
        lines += ["A=M-1"]
        lines += ["D=M"]
        lines += ["@ARG"]
        lines += ["A=M"]
        lines += ["M=D"]
        lines += ["@SP"]
        lines += ["M=M-1"]

        # SP = ARG + 1
        lines += ["@ARG"]
        lines += ["D=M"]
        lines += ["@SP"]
        lines += ["M=D+1"]

        # THAT/THIS/ARG/LCL = *(endframe - 1/2/3/4)
        for offset, loc in enumerate(("THAT", "THIS", "ARG", "LCL")):
            lines += [f"@ENDFRAME.{label}"]
            lines += ["D=M"]
            lines += [f"@{offset + 1}"]
            lines += ["A=D-A"]
            lines += ["D=M"]
            lines += [f"@{loc}"]
            lines += ["M=D"]

        # Goto retaddr
        lines += [f"@RETADDR.{label}"]
        lines += ["A=M"]
        lines += ["0;JMP"]

        return lines