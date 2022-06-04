import marshal
import zlib

def init_rotor():
    asdf_dn = 'j2h56ogodh3se'
    asdf_dt = '=dziaq.'
    asdf_df = '|os=5v7!"-234'
    asdf_tm = asdf_dn * 4 + (asdf_dt + asdf_dn + asdf_df) * 5 + '!' + '#' + asdf_dt * 7 + asdf_df * 2 + '*' + '&' + "'"
    import rotor
    rot = rotor.newrotor(asdf_tm)
    return rot


def _reverse_string(s):
    l = list(s)
    l = map(lambda x: chr(ord(x) ^ 154), l[0:128]) + l[128:]
    l.reverse()
    return ''.join(l)


class NpkImporter(object):
    rotor = init_rotor()
    ext = '.nxs'

    def __init__(self, path):
        self._path = path

    def find_module(self, fullname, path = None):
        import C_file
        if path is None:
            path = self._path
        fullname = fullname.replace('.', '/')
        pkg_name = fullname + '/__init__' + NpkImporter.ext
        if C_file.find_file(pkg_name, path):
            return self
        else:
            fullname += NpkImporter.ext
            if C_file.find_file(fullname, path):
                return self
            return

    def load_module(self, fullname):
        import C_file
        is_pkg = True
        mod_path = fullname.replace('.', '/') + '/__init__'
        mod_name = fullname
        if not C_file.find_file(mod_path + NpkImporter.ext, self._path):
            is_pkg = False
            mod_path = fullname.replace('.', '/')
            mod_name = fullname
        data = C_file.get_file(mod_path + NpkImporter.ext, self._path)
        data = NpkImporter.rotor.decrypt(data)
        data = zlib.decompress(data)
        data = _reverse_string(data)
        data = marshal.loads(data)
        path = None
        if is_pkg:
            path = [self._path]
        m = C_file.new_module(mod_name, data, path)
        return m


import sys
sys.path_hooks.append(NpkImporter)