import sys
import marshal


def compare(cobj1, cobj2, opmap):

    codestr1 = bytearray(cobj1.co_code)
    codestr2 = bytearray(cobj2.co_code)

    if len(codestr1) != len(codestr2):
        print("two cobj has different length, skipping")
        return

    i = 0
    while i < len(codestr1):
        if codestr1[i] not in opmap:
            opmap[codestr1[i]] = codestr2[i]
        else:
            if opmap[codestr1[i]] != codestr2[i]:
                print("error: has wrong opcode")
                break
        if codestr1[i] < 90 and codestr2[i] < 90:
            i += 1
        elif codestr1[i] >= 90 and codestr2[i] >= 90:
            i += 3
        else:
            print("wrong opcode")

    for const1, const2 in zip(cobj1.co_consts, cobj2.co_consts):
        if hasattr(const1, 'co_code') and hasattr(const2, 'co_code'):
            compare(const1, const2, opmap)


def usage():
    print("Usage:\n" +
          "%s 1.pyc 1.pyc\n" +
          "%s 1-1.pyc 1-2.pyc 2-1.pyc 2-2.pyc\n")


def main():
    if len(sys.argv) != 3 and len(sys.argv) != 5:
        usage()
        return

    opmap = {}

    cobj1 = marshal.loads(open(sys.argv[1]).read())
    cobj2 = marshal.loads(open(sys.argv[2]).read())
    compare(cobj1, cobj2, opmap)

    if len(sys.argv) > 3:
        cobj3 = marshal.loads(open(sys.argv[3]).read())
        cobj4 = marshal.loads(open(sys.argv[4]).read())
        compare(cobj3, cobj4, opmap)

    print(opmap)


if __name__ == '__main__':
    main()
