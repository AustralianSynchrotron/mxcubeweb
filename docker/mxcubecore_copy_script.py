import inspect
import os
from distutils.dir_util import copy_tree
from pathlib import Path

import mxcubecore

pkg_path = os.path.dirname(inspect.getfile(mxcubecore))
pkg_config_path = Path().joinpath(pkg_path, "configuration/ansto").as_posix()

copy_tree(pkg_config_path, "/opt/mxcube3/ANSTO")
