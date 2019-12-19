import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

# Do not compile this package with clang, use GCC instead.

class Libunwind(ConanFile):
    """Conan recipe to build Libunwind."""
    description = "API to determine the call-chain of a program."
    license = "MIT"
    url = "https://www.nongnu.org/libunwind"
    settings = "os"
    name = "libunwind"
    version = "1.3.1"

    _source_subfolder = "source_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def source(self):
        """Retrieve source code."""
        download_url = "http://download.savannah.nongnu.org/releases/libunwind/{}-{}.tar.gz".format(
            self.name, self.version)
        tools.get(download_url)
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def build(self):
        """Build the elements to package."""
        with tools.chdir(self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.fpic = True
            autotools.configure()
            autotools.make(args=["-j{}".format(tools.cpu_count())])
            autotools.install(args=["-j{}".format(tools.cpu_count())])

    def package(self):
        """Assemble the package."""
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder, ignore_case=True, keep_path=True)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
