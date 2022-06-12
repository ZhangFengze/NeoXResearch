import sys
import decrypt_buffer
import nxs2pyc
import decrypt_pyc
import decompile_pyc
import pathlib2

if __name__ == "__main__":
    files = pathlib2.Path(sys.argv[1]).glob("*")
    files = sorted(files, key=lambda file: file.stat().st_size)
    for file in files:
        if file.name == "redirect.nxs":
            continue

        with open(str(file), "rb") as infile:

            data = infile.read()
            data = decrypt_buffer.Decrypt(data)
            data = nxs2pyc.nxs2pyc(data)
            filename, data = decrypt_pyc.decrypt_pyc(data)
            try:
                data = decompile_pyc.decompile_pyc(data)
            except KeyboardInterrupt as k:
                raise k
            except Exception as e:
                print("decompile %s %s failed" % (file, filename))
                continue

            outputPath = pathlib2.Path(sys.argv[2])/filename
            outputPath.parent.mkdir(exist_ok=True, parents=True)
            with open(str(outputPath), "wb") as outfile:
                outfile.write(data)