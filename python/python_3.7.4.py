import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class Python(ConanFile):
    description = "open-source, cross-platform family of tools designed to build, test and package software"
    license = "Python Software Foundation License"
    url = "https://python.org"
    version = "3.7.5"
    settings = "os"
    name = "python"

    _source_subfolder = "source_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def source(self):
        """Retrieve source code."""
        url = "https://github.com/python/cpython/archive/v{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename("cpython-{}".format(self.version))

    def build(self):
        """Build the elements to package."""
        with tools.chdir(self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.fpic = True
            autotools.link_flags.append("-fuse-ld=lld")


    def package(self):
        """Assemble the package."""
        self.copy("*", src="to_copy", dst="", keep_path=True)

    def package_info(self):
        """Edit package info."""
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.CMAKE_ROOT = self.package_folder
        self.env_info.CMAKE_MODULE_PATH = os.path.join(self.package_folder, "share", "cmake-3.15", "Modules")
