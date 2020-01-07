
import os
import shutil
from glob import glob
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class libXext(pyreq.BaseConanFile):
    description = 'Xlib-based library for common extensions to the X11 protocol'
    url = "https://www.x.org/"
    license = "X11"
    settings = "os"
    requires = ("libX11/1.6.8@tdelame/stable")
    

    def config_options(self):
        if self.settings.os != "Linux":
            raise RuntimeError("X11 libraries are available on Linux only")

    def source(self):
        directory = "libXext-1.3.4"
        url = "https://www.x.org/archive/individual/lib/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        self.build_autotools()

    def package_info(self):
        self.cpp_info.libs = ["Xext"]

    
