
import os
import shutil
from glob import glob
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class xcbutilkeysyms(pyreq.BaseConanFile):
    description = 'Library for handling standard X key constants and conversion to/from keycodes.'
    url = "https://www.x.org/"
    license = "X11"
    settings = "os"
    requires = ("libxcb/1.13.1@tdelame/stable")
    

    def config_options(self):
        if self.settings.os != "Linux":
            raise RuntimeError("X11 libraries are available on Linux only")

    def source(self):
        directory = "xcb-util-keysyms-0.4.0"
        url = "https://www.x.org/archive/individual/xcb/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        self.build_autotools()

    def package_info(self):
        self.cpp_info.libs = ["xcb-keysyms"]

    
