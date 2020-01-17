
import os
import shutil
from glob import glob
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class libX11(pyreq.BaseConanFile):
    description = 'Core X11 protocol client library (aka "Xlib")'
    url = "https://www.x.org/"
    license = "X11"
    settings = "os"
    requires = ("xorgproto/2019.1@tdelame/stable", "xtrans/1.4.0@tdelame/stable", "libxcb/1.13.1@tdelame/stable")
    

    def config_options(self):
        if self.settings.os != "Linux":
            raise RuntimeError("X11 libraries are available on Linux only")

    def source(self):
        directory = "libX11-1.6.8"
        url = "https://www.x.org/archive/individual/lib/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        self.build_autotools()

    def package_info(self):
        self.cpp_info.libs = ["X11"]

    
