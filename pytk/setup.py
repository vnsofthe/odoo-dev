

from distutils.core import setup
import py2exe

setup(
    # The first three parameters are not required, if at least a
    # 'version' is given, then a versioninfo resource is built from
    # them and added to the executables.
    version = "0.5.0",
    description = "py2exe sample script",
    name = "py2exe samples",

    # targets to build
    windows = ["main.py"],

    )
