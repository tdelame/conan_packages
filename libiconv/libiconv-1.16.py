from conans import python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class Libiconv(pyreq.BaseConanFile):
    description = "Convert text to and from Unicode"
    url = "https://www.gnu.org/software/libiconv/"
    license = "LGPL-2.1"
    name = "libiconv"
    version = "1.16"

    settings = "os"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def source(self):
        """Retrieve source code."""
        self.download("https://ftp.gnu.org/gnu/libiconv/")

    def build(self):
        """Build the elements to package."""
        self.build_autotools()

    def package_info(self):
        super(Libiconv, self).package_info()
        self.cpp_info.libs = ["iconv"]
