#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import marshal
import argparse
import pymarshal
import sys
sys.path.insert(0, './archives')
import opmap

class PYCEncryptor(object):
    def __init__(self):
        self.pyc27_header = "\x03\xf3\x0d\x0a\x00\x00\x00\x00"
    def _decrypt_file(self, filename):
        os.path.splitext(filename)
        content = open(filename).read()
        try:
            m = pymarshal.loads(content)
        except:
            try:
                m = marshal.loads(content)
            except Exception as e:
                print("[!] error: %s" % str(e))
                return None
        return m.co_filename.replace('\\', '/'), pymarshal.dumps(m, opmap.decrypt_map)
    def decrypt_file(self, input_file, output_file=None):
        result = self._decrypt_file(input_file)
        if not result:
            return
        pyc_filename, pyc_content = result
        if not output_file:
            output_file = os.path.basename(pyc_filename) + '.pyc'
        with open(output_file, 'wb') as fd:
            fd.write(self.pyc27_header + pyc_content)
def main():
    parser = argparse.ArgumentParser(description='onmyoji py decrypt tool')
    parser.add_argument("INPUT_NAME", help='input file')
    parser.add_argument("OUTPUT_NAME", help='output file')
    args = parser.parse_args()
    encryptor = PYCEncryptor()
    encryptor.decrypt_file(args.INPUT_NAME, args.OUTPUT_NAME)
if __name__ == '__main__':
    main()