from conans import ConanFile

from utils import *
from base_conan_file import *


class pyreq(ConanFile):
    description = "Common python definition for conan packages"
    license = " "
    url = " "

    version = "1.0.0"
    name = "pyreq"
    exports = ["utils.py", "base_conan_file.py"]
