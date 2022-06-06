# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, './archives')
import opmap
import marshal
import pymarshal
import pathlib

pyc27_header = "\x03\xf3\x0d\x0a\x00\x00\x00\x00"


def decrypt_pyc(data):
    try:
        m = pymarshal.loads(data)
    except:
        try:
            m = marshal.loads(data)
        except Exception as e:
            print("[!] error: %s" % str(e))
            return None
    return m.co_filename.replace('\\', '/'), pymarshal.dumps(m, opmap.decrypt_map)


if __name__ == '__main__':
    with open(sys.argv[1], "rb") as infile:
        data = infile.read()
        pyc_filename, pyc_content = decrypt_pyc(data)
        print(pyc_filename)
        with open(sys.argv[2], 'wb') as fd:
            fd.write(pyc27_header + pyc_content)
