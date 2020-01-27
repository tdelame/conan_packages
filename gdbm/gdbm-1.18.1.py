from conans import python_requires

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class gdbm(pyreq.BaseConanFile):
    description = "GNU Database library"
    url = "https://www.gnu.org/software/gdbm/gdbm.html"
    license = "GNU General Public License, Version 3"
    name = "gdbm"
    version = "1.18.1"
    settings = "os"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os == "Windows":
            raise RuntimeError("This recipe is not available yet on Windows")

    def source(self):
        """Retrieve source code."""
        self.download("https://ftp.gnu.org/gnu/gdbm")

    def build(self):
        """Build elements to package."""
        arguments = [
            "--enable-libgdbm-compat"
        ]
        self.build_autotools(arguments)

    def package_info(self):
        """Edit package info."""
        super(gdbm, self).package_info()
        self.cpp_info.libs = ["gdbm", "gdbm_compat"]
