
import os
import shutil
from glob import glob
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class libXaw(pyreq.BaseConanFile):
    description = 'X Athena Widget Set, based on the X Toolkit Intrinsics (Xt) Library'
    url = "https://www.x.org/"
    license = "X11"
    settings = "os"
    requires = ("libXmu/1.1.3@tdelame/stable", "libXpm/3.5.12@tdelame/stable")
    

    def config_options(self):
        if self.settings.os != "Linux":
            raise RuntimeError("X11 libraries are available on Linux only")

    def source(self):
        directory = "libXaw-1.0.13"
        url = "https://www.x.org/archive/individual/lib/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        self.build_autotools()

    def package_info(self):
        self.cpp_info.libs = ["Xaw6", "Xaw7"]

    
