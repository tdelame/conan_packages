from distutils.spawn import find_executable
from shutil import rmtree, copyfile
import os
from conans import python_requires, ConanFile, AutoToolsBuildEnvironment, tools

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class Fontconfig(pyreq.BaseConanFile):
    description = "library for configuring and customizing font access"
    url = "https://www.fontconfig.org"
    license = "MIT"
    name = "fontconfig"
    version = "2.13.92"

    settings = "os"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os == "Windows":
            raise RuntimeError("Fontconfig is not supported on Windows")

    def requirements(self):
        """Define runtime requirements."""
        self.requires("freetype/2.9.1@tdelame/stable")
        self.requires("expat/2.2.9@tdelame/stable")

    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("gperf/3.1@tdelame/stable")
        self.requires("bzip2/1.0.8@tdelame/stable") #helps autotools to find bzip2

    def source(self):
        """Retrieve source code."""
        directory = "fontconfig-{}".format(self.version)
        url = "https://www.freedesktop.org/software/fontconfig/release/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        """Build the elements to package."""
        # replace libtool number with freetype version number
        with tools.chdir(self._source_subfolder):
            tools.replace_in_file("configure", "21.0.15", "2.8.1")

        arguments = [
            "--disable-dependency-tracking",
            "--disable-rpath",
            "--disable-docs",
        ]
        # the autotools script does not like we do not have a pkg-config file for bzip2, so we trick it:
        with tools.environment_append({"FREETYPE_CFLAGS": "-I.", "FREETYPE_LIBS": "-lfreetype -lpng -lbz2 -lz"}):
            self.build_autotools(arguments)

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["fontconfig"]
        self.cpp_info.system_libs = ["m", "pthread"]
