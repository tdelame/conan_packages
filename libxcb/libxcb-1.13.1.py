
import os
import shutil
from glob import glob
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class libxcb(pyreq.BaseConanFile):
    description = 'C interface to the X Window System protocol, which replaces the traditional Xlib interface'
    url = "https://www.x.org/"
    license = "X11"
    settings = "os"
    requires = ("xcb-proto/1.13@tdelame/stable", "util-macros/1.19.2@tdelame/stable", "libXau/1.0.9@tdelame/stable", "libpthread-stubs/0.1@tdelame/stable", "libXdmcp/1.1.3@tdelame/stable")
    

    def config_options(self):
        if self.settings.os != "Linux":
            raise RuntimeError("X11 libraries are available on Linux only")

    def source(self):
        directory = "libxcb-1.13.1"
        url = "https://www.x.org/archive/individual/xcb/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        self.build_autotools()

    def package_info(self):
        self.cpp_info.libs = ["xcb"]

    
