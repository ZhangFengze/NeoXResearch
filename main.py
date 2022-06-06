import sys
import decrypt_buffer
import nxs2pyc
import decrypt_pyc
import decompile_pyc

if __name__ == "__main__":
    with open(sys.argv[1], "rb") as infile:
        data = infile.read()
        data = decrypt_buffer.Decrypt(data)
        data = nxs2pyc.nxs2pyc(data)
        filename, data = decrypt_pyc.decrypt_pyc(data)
        print(filename)
        data = decompile_pyc.decompile_pyc(data)
        with open(sys.argv[2], "wb") as outfile:
            outfile.write(data)
