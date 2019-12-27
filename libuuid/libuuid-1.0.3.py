from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class LibUUID(ConanFile):
    description = "Portable UUID C library"
    url = "https://sourceforge.net/projects/libuuid"
    license = "BSD"
    name = "libuuid"
    version = "1.0.3"

    settings = "os"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    _source_subfolder = "source_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os == "Windows":
            raise RuntimeError("Libuuid is not supported on Windows")

    def source(self):
        """Retrieve source code."""
        directory = "libuuid-{}".format(self.version)
        url = "https://downloads.sourceforge.net/project/libuuid/{}.tar.gz".format(directory)
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
            autotools.configure(args=arguments)
            autotools.make(args=[parallel])
            autotools.install(args=[parallel])

    def package(self):
        """Assemble the package."""
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.remove(os.path.join(self.package_folder, "lib", "libuuid.la"))

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["uuid"]
