import os
import shutil
from glob import glob
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class ICU(pyreq.BaseConanFile):
    description = "ICU is a mature, widely used set of C/C++ and Java libraries providing Unicode and Globalization support for software applications. ICU is widely portable and gives applications the same results on all platforms and between C/C++ and Java software"
    license = "ICU"
    url = "http://site.icu-project.org"
    version = "65.1"
    name = "icu"

    settings = "os"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def source(self):
        """Retrieve source code."""
        url = "https://github.com/unicode-org/icu/releases/download/release-65-1/icu4c-65_1-src.tgz"
        tools.get(url)
        os.rename("icu", self._source_subfolder)

    def build(self):
        """Build the elements to package."""
        arguments = [
            "--disable-fuzzer", "--disable-tests", "--disable-samples", "--disable-layoutex",
            "--enable-release", "--disable-debug", "--with-library-bits=64"
        ]
        
        self.build_autotools(arguments, directory=os.path.join(self._source_subfolder, "source"))

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["icui18n", "icuio", "icutest", "icutu", "icuuc", "icudata"]
