import sys
import uncompyle6
import tempfile
from io import StringIO


def decompile_pyc(data):
    with tempfile.TemporaryDirectory() as dir:
        tempPath = dir+"/temp.pyc"
        with open(tempPath, "wb") as f:
            f.write(data)
        out = StringIO()
        uncompyle6.decompile_file(tempPath, out)
        return out.getvalue()


if __name__ == "__main__":
    with open(sys.argv[1], "rb") as infile:
        data = infile.read()
        data = decompile_pyc(data)
        with open(sys.argv[2], "wb") as outfile:
            outfile.write(data.encode("utf8"))