
import os
import shutil
from glob import glob
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class libXxf86vm(pyreq.BaseConanFile):
    description = 'Xlib-based library for the XFree86-VidMode X extension'
    url = "https://www.x.org/"
    license = "X11"
    settings = "os"
    requires = ("libX11/1.6.8@tdelame/stable", "libXext/1.3.4@tdelame/stable")
    

    def config_options(self):
        if self.settings.os != "Linux":
            raise RuntimeError("X11 libraries are available on Linux only")

    def source(self):
        directory = "libXxf86vm-1.1.4"
        url = "https://www.x.org/archive/individual/lib/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        self.build_autotools()

    def package_info(self):
        self.cpp_info.libs = ["Xxf86vm"]

    
