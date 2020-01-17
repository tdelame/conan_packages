import os
from conans import python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class pyinstaller(pyreq.PythonPackage):
    name = "pyinstaller"
    version = "3.6"