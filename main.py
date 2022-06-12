# -*- coding: utf-8 -*-
import os
import sys
import decrypt_buffer
import nxs2pyc
import decrypt_pyc
import decompile_pyc
import pathlib2

if __name__ == "__main__":
    failedFiles = []

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

            # uncompyle6 python2 docstring有问题，反编译挪到python3执行
            # try:
            #     data = decompile_pyc.decompile_pyc(data)
            # except KeyboardInterrupt as k:
            #     raise k
            # except Exception as e:
            #     print("decompile %s %s failed" % (file, filename))
            #     continue

            pycPath = pathlib2.Path(sys.argv[2])/(filename+"c")
            pycPath.parent.mkdir(exist_ok=True, parents=True)
            with open(str(pycPath), "wb") as outfile:
                outfile.write(data)

            # 注意用python3
            pyPath = pathlib2.Path(sys.argv[3])/filename
            decompileSuccess = os.system(
                "uncompyle6 -o %s %s" % (str(pyPath), str(pycPath)))
            if not decompileSuccess:
                failedFiles.append((str(file), str(pycPath)))

    print("failed with:")
    for fail in failedFiles:
        print(fail)

    with open("failed", "wb") as outfile:
        outfile.write(str(failedFiles))
