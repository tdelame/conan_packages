from conans import python_requires
import os
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class ncurses(pyreq.BaseConanFile):
    description = "System V release 4.0 curses emulation library"
    homepage = "https://invisible-island.net/ncurses/ncurses.html"
    license = "MIT"
    name = "ncurses"
    version = "6.1"

    settings = "os"

    def source(self):
        """Retrieve source code."""
        self.download("https://ftp.gnu.org/pub/gnu/ncurses")

    def configure(self):
        self.options.shared = True

    def build(self):
        """Build the elements to package."""
        arguments = [
            "--without-manpages", "--without-tests", "--without-profile", "--without-debug", "--without-ada",
            "--with-shared", "--with-normal", "--with-cxx-binding", "--with-cxx-shared", "--with-termlib", "--without-normal",
             "--enable-pc-files", "--enable-sp-funcs", "--enable-overwrite",
            "--disable-echo",
            '--with-pkg-config-libdir=${prefix}/lib/pkgconfig'
        ]
        self.build_autotools(arguments)

    def package_info(self):
        """Edit package info."""
        super(ncurses, self).package_info()
        self.cpp_info.libs = ["form", "menu", "ncurses", "ncurses++", "panel", "tinfo"]
