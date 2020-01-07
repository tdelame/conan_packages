
import os
import shutil
from glob import glob
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class xkeyboardconfig(pyreq.BaseConanFile):
    description = 'keyboard configuration database for the X Window System.'
    url = "https://www.x.org/"
    license = "X11"
    settings = "os"
    requires = ("xproto/7.0.31@tdelame/stable", "libX11/1.6.8@tdelame/stable")
    

    def config_options(self):
        if self.settings.os != "Linux":
            raise RuntimeError("X11 libraries are available on Linux only")

    def source(self):
        directory = "xkeyboard-config-2.28"
        url = "https://www.x.org/archive/individual/data/xkeyboard-config/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        self.build_autotools()

    def package_info(self):
        self.cpp_info.libs = []

    
    def package_id(self):
        self.info.header_only()

