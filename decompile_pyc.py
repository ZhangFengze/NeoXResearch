import sys
import uncompyle6
import io
from backports import tempfile


def decompile_pyc(data):
    with tempfile.TemporaryDirectory() as dir:
        inpath = dir+"/in.pyc"
        with open(inpath, "wb") as infile:
            infile.write(data)

        outpath = dir+"out.pyc"
        with open(outpath, "w+b") as outfile:
            uncompyle6.decompile_file(inpath, outfile)
            outfile.seek(0)
            return outfile.read()


if __name__ == "__main__":
    with open(sys.argv[1], "rb") as infile:
        data = infile.read()
        data = decompile_pyc(data)
        with open(sys.argv[2], "wb") as outfile:
            outfile.write(data.encode("utf8"))
