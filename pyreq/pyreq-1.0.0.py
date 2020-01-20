from conans import ConanFile

from utils import *
from base_conan_file import *
from cmake_conan_file import *
from python_package import *
from python_packages import *


class pyreq(ConanFile):
    description = "Common python definition for conan packages"
    license = " "
    url = " "

    version = "1.0.0"
    name = "pyreq"
    exports = ["utils.py", "base_conan_file.py", "python_package.py", "cmake_conan_file.py", "python_packages.py"]
