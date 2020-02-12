
import os
import shutil
from glob import glob
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class utilmacros(pyreq.BaseConanFile):
    description = 'GNU autoconf macros shared across X.Org projects'
    url = "https://www.x.org/"
    license = "X11"
    settings = "os"
    
    

    def config_options(self):
        if self.settings.os != "Linux":
            raise RuntimeError("X11 libraries are available on Linux only")

    def source(self):
        directory = "util-macros-1.19.2"
        url = "https://www.x.org/archive/individual/util/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        self.build_autotools()

    def package_info(self):
        self.cpp_info.libs = []

    
    def package_id(self):
        self.info.header_only()
