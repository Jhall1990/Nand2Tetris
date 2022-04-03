import os
import sys

import parser
import writer


if __name__ == "__main__":
    in_file = sys.argv[1]

    if os.path.isdir(in_file):
        files = [os.path.join(in_file, i) for i in os.listdir(in_file) if i.endswith(".vm")]
        out_file = f"{os.path.split(in_file)[1]}.asm"
        out_file = os.path.join(in_file, out_file)
    else:
        files = [in_file]
        out_file = in_file.replace(".vm", ".asm")

    p = parser.Parser(files)
    w = writer.Writer(out_file, p)