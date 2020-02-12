from conans import python_requires, tools
import os
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class termcap(pyreq.BaseConanFile):
    description = "Enables programs to use display terminals in a terminal-independent manner"
    homepage = "https://www.gnu.org/software/termcap"
    license = "GPL-2.0"
    name = "termcap"
    version = "1.3.1"

    settings = "os"

    def configure(self):
        self.options.shared = False

    def source(self):
        """Retrieve source code."""
        self.download("https://ftp.gnu.org/gnu/termcap")
        with pyreq.change_current_directory(self._source_subfolder):
            tools.replace_in_file("Makefile.in", "CFLAGS = -g", "CFLAGS = -fPIC")

    def build(self):
        """Build the elements to package."""
        self.build_autotools()

    def package_info(self):
        """Edit package info."""
        super(termcap, self).package_info()
        self.cpp_info.libs = ["termcap"]
