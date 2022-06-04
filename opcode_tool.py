import sys
sys.path.insert(0, './archives')
import opmap
import opcode


def help_as_standard(standard_op):
    try:
        neox_op = opmap.encrypt_map[standard_op]
        print(
            "std {0}:{1} -> neox {2}".format(opcode.opname[standard_op], standard_op, neox_op))
    except:
        print("unknown std opcode")


def help_as_neox(neox_op):
    try:
        standard_op = opmap.decrypt_map[neox_op]
        print("neox {0} -> std {1}:{2}".format(neox_op,
                                               standard_op, opcode.opname[standard_op]))
    except:
        print("unknown neox opcode")


op = sys.argv[1]
try:
    op = int(op)
    help_as_standard(op)
    help_as_neox(op)
except ValueError:
    op = opcode.opmap[op]
    help_as_standard(op)
