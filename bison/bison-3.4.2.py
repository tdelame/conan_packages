import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class Bison(ConanFile):
    description = "GNU Parser Generator"
    license = "GNU GPL"
    url = "https://www.gnu.org/software/bison/"
    version = "3.4.2"
    settings = "os"
    name = "bison"

    _source_subfolder = "source_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def source(self):
        """Retrieve source code."""
        url = "http://ftp.gnu.org/gnu/bison/bison-{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename("bison-{}".format(self.version), self._source_subfolder)
    
    def build(self):
        """Build the elements to package."""
        with tools.chdir(self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.fpic = True
            autotools.configure(
                args=["--enable-relocatable"])
            # There is a bug in parallel build with version 3.4.X: use a monothreaded build.
            autotools.make(args=["-j1"])
            autotools.install(args=["-j1"])
    
    def package(self):
        """Assemble the package."""
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder, ignore_case=True, keep_path=True)
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.BISON_PKGDATADIR = os.path.join(self.package_folder, "share", "bison")
