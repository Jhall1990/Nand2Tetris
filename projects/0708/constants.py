COMMENT = "//"

# Memory operations
PUSH_CMD = "push"
POP_CMD = "pop"

# Memory locations
MEM_LOCAL = "local"
MEM_ARG = "argument"
MEM_THIS = "this"
MEM_THAT = "that"
MEM_CONSTANT = "constant"
MEM_STATIC = "static"
MEM_TEMP = "temp"
MEM_POINTER = "pointer"

# Mem segment pointers
TEMP_REG = "@R15"
MEM_POINT = {
    MEM_LOCAL: "@LCL",
    MEM_ARG: "@ARG",
    MEM_THIS: "@THIS",
    MEM_THAT: "@THAT",
    MEM_TEMP: 5,
}

# Arthmetic operations
OPR_ADD = "add"
OPR_SUB = "sub"
OPR_NEG = "neg"
OPR_EQ = "eq"
OPR_GT = "gt"
OPR_LT = "lt"
OPR_AND = "and"
OPR_OR = "or"
OPR_NOT = "not"
ALL_OPRS = (OPR_ADD, OPR_SUB, OPR_NEG, OPR_EQ, OPR_GT,
            OPR_LT, OPR_AND, OPR_OR, OPR_NOT)

# Program control operations
LABEL_CMD = "label"
GOTO_CMD = "goto"
IFGOTO_CMD = "if-goto"
ALL_CTRLS = (LABEL_CMD, GOTO_CMD, IFGOTO_CMD)

# Function operations
FUNC_CMD = "function"
CALL_CMD = "call"
RET_CMD = "return"