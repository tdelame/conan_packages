from conans import python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")


class Flex(pyreq.BaseConanFile):
    description = "Fast Lexical Analyzer Generator"
    license = "BSD like"
    url = "https://www.gnu.org/software/flex/"
    version = "2.6.4"
    settings = "os"
    name = "flex"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("bison/3.4.2@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        self.download("https://github.com/westes/flex/files/981163")
    
    def build(self):
        """Build the elements to package."""
        self.build_autotools()