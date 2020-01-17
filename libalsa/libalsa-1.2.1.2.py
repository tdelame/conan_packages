from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class Libalsa(ConanFile):
    description = "Advanced Linux Sound Architecture that provides audio and MIDI functionality to the Linux operating system"
    url = "https://alsa-project.org/"
    license = "LGPL-2.1"
    name = "libalsa"

    options = {"shared": [True, False]}
    default_options = {'shared': True}

    settings = "os"

    _source_subfolder = "source_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("cpython/3.7.5@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        directory = "alsa-lib-{}".format(self.version)
        url = "https://www.alsa-project.org/files/pub/lib/{}.tar.bz2".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        """Build the elements to package."""
        parallel = "-j{}".format(tools.cpu_count())
        arguments = ["--disable-python2"]
        if self.options.shared:
            arguments.extend(["--enable-shared=yes", "--enable-static=no"])
        else:
            arguments.extend(["--enable-static=yes", "--enable-shared=no"])

        with tools.chdir(self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.fpic = True
            autotools.cxx_flags.append("-O3")
            autotools.flags.append("-O3")
            if find_executable("lld") is not None:
                autotools.link_flags.append("-fuse-ld=lld")

            autotools.configure(args=arguments)
            autotools.make(args=[parallel])
            autotools.install(args=[parallel])

    def package(self):
        """Assemble the package."""
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        rmtree(os.path.join(self.package_folder, "share"))
        rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))
        for la in ["libasound.la", "libatopology.la"]:
            os.remove(os.path.join(self.package_folder, "lib", la))

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["asound"]
        self.cpp_info.system_libs = ["dl", "m", "rt", "pthread"]
