from conans import python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class Gperf(pyreq.BaseConanFile):
    description = "perfect hash function generator"
    url = "https://www.gnu.org/software/gperf"
    license = "GPL-3.0"
    name = "gperf"
    version = "3.1"

    settings = "os"

    _source_subfolder = "source_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def source(self):
        """Retrieve source code."""
        self.download("https://ftp.gnu.org/pub/gnu/gperf")

    def build(self):
        """Build the elements to package."""
        self.build_autotools()
