import argparse
import marshal
from dis import dis


def recursive_dis(co):
    if hasattr(co, 'co_code'):
        print(co.co_name)
        dis(co.co_code)
        for x in co.co_consts:
            recursive_dis(x)


parser = argparse.ArgumentParser()
parser.add_argument('input')
parser.add_argument('--skip_pyc_head', action="store_true")
args = parser.parse_args()

pyc = open(args.input).read()
if args.skip_pyc_head:
    pyc = pyc[8:]
co = marshal.loads(pyc)
recursive_dis(co)
