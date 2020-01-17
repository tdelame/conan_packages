
import os
import shutil
from glob import glob
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class libfontenc(pyreq.BaseConanFile):
    description = 'X font encoding library'
    url = "https://www.x.org/"
    license = "X11"
    settings = "os"
    requires = ("xorgproto/2019.1@tdelame/stable", "util-macros/1.19.2@tdelame/stable", "zlib/1.2.11@tdelame/stable")
    

    def config_options(self):
        if self.settings.os != "Linux":
            raise RuntimeError("X11 libraries are available on Linux only")

    def source(self):
        directory = "libfontenc-1.1.4"
        url = "https://www.x.org/archive/individual/lib/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        self.build_autotools()

    def package_info(self):
        self.cpp_info.libs = ["fontenc"]

    
