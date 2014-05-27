import sys
import os
from zipfile import ZipFile
from glob import glob

ALL = ['Map', 'Mod', 'Map-Mod', 'Other']
MAP, MAP_MOD, MOD, OTHER = ALL


def scope(*params):
    def wrapper(funct):
        def new(*args):
            return funct(*args)
        for arg in params:
            setattr(new, arg, True)
        return new
    return wrapper


class Checker310(object):
    forbidden_files = ['Thumbs.db', 'Desktop.ini', '.DS_Store']
    forbidden_extension = ['.bak', '.tmp', '.wz', '.zip', '.js']
    required_extensions = ['.gam', '.bjo', '.map', '.ttp']

    def __init__(self, path_to_file, name=None, addon_type=None):
        self.addon_type = addon_type
        self.full_path = path_to_file
        self.path = os.path.basename(self.full_path)
        self.name, self.ext = os.path.splitext(self.path if name is None else name)
        self.zip = ZipFile(path_to_file, mode='r')
        self.names = self.zip.namelist()

        tests = [getattr(self, attr) for attr in dir(self) if attr.startswith('test_')]
        if addon_type:
            errors = [test() for test in tests if getattr(test, addon_type, False)]
        else:
            errors = [test() for test in tests]
        self.test_length = len(errors)
        self.errors = filter(bool, errors)

    def get_message(self):
        msg = '%s, errors: %s/%s\n' % (self.addon_type or 'All', len(self.errors), self.test_length)
        if self.errors:
            msg += '%s' % '\n\t\t'.join(self.errors)
        return msg

    def print_result(self):
        msg = ('Testing %s' % self.name).ljust(30)
        msg += '\n\t\t' + self.get_message()
        print msg

    @scope(MAP, MAP_MOD)
    def test_lev(self):
        for name in self.names:
            if name.lower().startswith(self.name.lower()) and name.endswith('.lev'):
                return None  # not error
        return "Not %s.*.lev file in in root path of %s" % (self.name, self.path)

    @scope(*ALL)
    def test_extension(self):
        if self.ext != '.wz':
            return "Expect %s.wz got %s " % (self.name, self.path)

    @scope(*ALL)
    def test_dumb_files(self):
        errors = [name for name in self.names if os.path.basename(name) in self.forbidden_files]
        if errors:
            return 'Forbidden files %s' % (', '.join(errors))

    @scope(MAP, MAP_MOD, MOD)
    def test_forbidden_extensions(self):
        errors = [name for name in self.names if os.path.splitext(name)[-1] in self.forbidden_extension]
        if errors:
            return 'Files with forbidden extensions %s' % (', '.join(errors))

    @scope(MAP)
    def test_forbidden_extensions(self):
        errors = [name for name in self.names if os.path.splitext(name)[-1] == '.js']
        if errors:
            return 'JS files forbidden for maps %s' % (', '.join(errors))

    @scope(MAP, MAP_MOD)
    def test_required_extensions(self):
        exts = [os.path.splitext(name)[-1] for name in self.names]
        errors = [ext for ext in self.required_extensions if not ext in exts]
        if errors:
            return 'Files with this extensions %s not present in archive' % (', '.join(errors))

    @scope(MAP, MAP_MOD)
    def test_has_map_folder(self):
        if not "multiplay/maps/" in self.names:
            print self.names
            return "Map has no multiplay/map folder"

    @scope(MAP, MAP_MOD)
    def test_has_one_map_file(self):
        maps = [name for name in self.names if name.endswith('.map')]
        if len(maps) > 1:
            return "Not too many map files %s" % ', '.join(maps)

if __name__ == '__main__':
    folder = os.path.dirname(__file__)
    if len(sys.argv) > 2:
        folder = sys.argv[1]

    maps = glob(os.path.join(folder, '*.wz'))
    for file in maps:
        Checker310(file).print_result()

