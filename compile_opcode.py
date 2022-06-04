import marshal


def CompileAndDump(script, outputPath):
    with open(outputPath, 'wb') as out:
        codeObject = compile(script, '', 'exec')
        marshal.dump(codeObject, out)


opcode = open('pyopcode.py').read()
CompileAndDump(opcode, "pyopcode.pyc")
opcode_division = opcode[2:]
CompileAndDump(opcode_division, "pyopcode_division.pyc")