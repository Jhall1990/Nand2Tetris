class Writer(object):
    def __init__(self, out_file, parser):
        self.out_file = out_file
        self.parser = parser
        self.write()

    def write(self):
        with open(self.out_file, "w") as out_file:
            for command in self.parser.commands:
                out_file.write(command.write())
