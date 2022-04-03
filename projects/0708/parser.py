import os
import commands
import constants


class Parser(object):
    def __init__(self, files):
        self.files = files
        self.filename = ""

        if len(files) > 1:
            self.commands = [commands.Bootstrap()]
        else:
            self.commands = []

        self.find_commands()
    
    def read_file(self, file):
        self.filename = os.path.basename(file).split(".")[0]
        with open(file, "r") as in_file:
            return in_file.readlines()

    def find_commands(self):
        for file in self.files:
            lines = self.read_file(file)

            for line in lines:
                fmt_line = line.strip()
                if not fmt_line:
                    continue
                elif fmt_line.startswith(constants.COMMENT):
                    continue
                self.parse_command(fmt_line)

    def parse_command(self, command):
        if command.startswith((constants.PUSH_CMD, constants.POP_CMD)):
            self.add_mem_cmd(command)
        elif any(command.startswith(opr) for opr in constants.ALL_OPRS):
            self.add_math_cmd(command)
        elif command.startswith(constants.ALL_CTRLS):
            self.add_ctrl_cmd(command)
        elif command.startswith(constants.FUNC_CMD):
            self.add_func_cmd(command)
        elif command.startswith(constants.CALL_CMD):
            self.add_call_cmd(command)
        elif command.startswith(constants.RET_CMD):
            self.add_ret_cmd(command)
        else:
            raise ValueError(f"Invalid command {command}")

    def command_parts(self, command, parts):
        cmdSplit = command.split()
        return cmdSplit[0:parts]

    def add_mem_cmd(self, command):
        op, loc, addr = self.command_parts(command, 3)
        self.commands.append(commands.MemoryCommand(self.filename, op, loc, addr))

    def add_math_cmd(self, command):
        op, = self.command_parts(command, 1)
        self.commands.append(commands.ArithmeticCommand(op))

    def add_ctrl_cmd(self, command):
        cmd, label = self.command_parts(command, 2)
        self.commands.append(commands.ControlCommand(self.filename, cmd, label))

    def add_func_cmd(self, command):
        _, name, nargs = self.command_parts(command, 3)
        self.commands.append(commands.FunctionCommand(self.filename, name, nargs))

    def add_call_cmd(self, command):
        _, name, nargs = self.command_parts(command, 3)
        self.commands.append(commands.CallCommand(self.filename, name, nargs))

    def add_ret_cmd(self, command):
        self.commands.append(commands.ReturnCommand(self.filename))