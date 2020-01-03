from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class Gperf(ConanFile):
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
        directory = "gperf-{}".format(self.version)
        url = "https://ftp.gnu.org/pub/gnu/gperf/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        """Build the elements to package."""
        parallel = "-j{}".format(tools.cpu_count())
        with tools.chdir(self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.fpic = True
            if find_executable("lld") is not None:
                autotools.link_flags.append("-fuse-ld=lld")
            autotools.configure()
            autotools.make(args=[parallel])
            autotools.install(args=[parallel])

    def package(self):
        """Assemble the package."""
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        rmtree(os.path.join(self.package_folder, "share"))

    def package_info(self):
        """Edit package info."""
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
