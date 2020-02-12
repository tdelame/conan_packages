import os
from conans import python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class rumba_python_dev(pyreq.PythonPackages):
    description = "List of python packages used to develop Rumba."
    name = "rumba-python-dev"
    version = "1.0"

    packages = [
        ("pyinstaller", "3.6"),
        ("pytest", "5.3.4"),
        ("pylint", "2.4.4"),
        ("doxypypy", "0.8.8.6"),
        ("conan", "1.21.1")
    ]
