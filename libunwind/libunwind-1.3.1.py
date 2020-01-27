from conans import python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class Libunwind(pyreq.BaseConanFile):
    """Conan recipe to build Libunwind."""
    description = "API to determine the call-chain of a program."
    license = "MIT"
    url = "https://www.nongnu.org/libunwind"
    settings = "os"
    name = "libunwind"
    version = "1.3.1"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def source(self):
        """Retrieve source code."""
        self.download("http://download.savannah.nongnu.org/releases/libunwind")

    def build(self):
        """Build the elements to package."""
        self.build_autotools()

    def package_info(self):
        super(Libunwind, self).package_info()
        self.cpp_info.libs = ["unwind-coredump", "unwind-generic", "unwind-ptrace", "unwind-setjmp", "unwind-x86_64", "unwind"] 
