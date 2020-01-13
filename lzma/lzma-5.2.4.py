import os
import shutil
from glob import glob
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class LZMA(pyreq.BaseConanFile):
    description = "LZMA library is part of XZ Utils"
    url = "https://tukaani.org"
    license = "Public Domain"
    
    name = "lzma"
    version = "5.2.4"
    settings = "os"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""        
        if self.settings.os != "Linux":
            raise RuntimeError("lzma recipe is not available yet for your OS")

    def source(self):
        """Retrieve source code."""
        directory = "xz-{}".format(self.version)
        url = "https://tukaani.org/xz/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        """Build the elements to package."""
        arguments = [
            '--disable-xz', '--disable-xzdec', '--disable-lzmadec',
            '--disable-lzmainfo', '--disable-scripts', '--disable-doc']
        self.build_autotools(arguments)

    def package_info(self):
        """Edit package info."""
        if not self.options.shared:
            self.cpp_info.defines.append('LZMA_API_STATIC')
        self.cpp_info.libs = ["lzma"]
        