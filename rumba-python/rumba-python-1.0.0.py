import os
from conans import python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class rumba_python(pyreq.PythonPackages):
    description = "List of python packages used by Rumba."
    name = "rumba-python"
    version = "1.0.0"

    packages = [
        ("numpy", "1.17.5"),
        ("psutil", "5.6.7"),
        ("pylint", "2.4.4"),
        ("Sphinx", "2.3.1"),
        ("recommonmark", "0.6.0"),
        ("sphinx-rtd-theme", "0.4.3"),
        ("sphinx-markdown-tables", "0.0.10"),
        ("pytest", "5.3.4")
    ]
