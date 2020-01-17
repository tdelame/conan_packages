from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class Libiconv(ConanFile):
    description = "Convert text to and from Unicode"
    url = "https://www.gnu.org/software/libiconv/"
    license = "LGPL-2.1"
    name = "libiconv"
    version = "1.16"

    settings = "os"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    _source_subfolder = "source_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def source(self):
        """Retrieve source code."""
        directory = "libiconv-{}".format(self.version)
        url = "https://ftp.gnu.org/gnu/libiconv/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        """Build the elements to package."""
        parallel = "-j{}".format(tools.cpu_count())
        if self.options.shared:
            arguments = ["--enable-shared=yes", "--enable-static=no"]
        else:
            arguments = ["--enable-static=yes", "--enable-shared=no"]

        with tools.chdir(self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.fpic = True
            if find_executable("lld") is not None:
                autotools.link_flags.append("-fuse-ld=lld")
            autotools.cxx_flags.append("-O3")
            autotools.flags.append("-O3")
            autotools.configure(args=arguments)
            autotools.make(args=[parallel])
            autotools.install(args=[parallel])

    def package(self):
        self.copy("COPYING.LIB", dst="licenses", src=self._source_subfolder)
        rmtree(os.path.join(self.package_folder, "share"))
        for la in ["libiconv.la", "libcharset.la"]:
            os.remove(os.path.join(self.package_folder, "lib", la))

    def package_info(self):
        self.cpp_info.libs = ["iconv"]
        self.env_info.path.append(os.path.join(self.package_folder, "bin"))
