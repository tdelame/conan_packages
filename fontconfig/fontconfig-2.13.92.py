from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class Fontconfig(ConanFile):
    description = "library for configuring and customizing font access"
    url = "https://www.fontconfig.org"
    license = "MIT"
    name = "fontconfig"
    version = "2.13.92"

    settings = "os"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    _source_subfolder = "source_subfolder"

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

    def source(self):
        """Retrieve source code."""
        directory = "fontconfig-{}".format(self.version)
        url = "https://www.freedesktop.org/software/fontconfig/release/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        """Build the elements to package."""
        parallel = "-j{}".format(tools.cpu_count())
        freetype_lib_path = self.deps_cpp_info["freetype"].lib_paths[0]
        libpng_lib_path = self.deps_cpp_info["libpng"].lib_paths[0]
        arguments = [
            "--disable-dependency-tracking",
            "--disable-rpath",
            "--disable-docs",
            "FREETYPE_CFLAGS=\"-I{}\"".format(self.deps_cpp_info["freetype"].include_paths[0]),
            "FREETYPE_LIBS=\"-L{} -lfreetype\"".format(freetype_lib_path)
        ]

        if self.options.shared:
            arguments.extend(["--enable-shared=yes", "--enable-static=no"])
        else:
            arguments.extend(["--enable-static=yes", "--enable-shared=no"])

        # I do not want to pollute the environment variables with a long LD_LIBRARY_PATH. So I did
        # not set the library paths of libpng and freetype into LD_LIBRARY_PATH. Instead, we extend
        # it here to build this recipe. Note: when I tried to combine the two following contexts
        # into the same line, it did not work.
        with tools.environment_append({"LD_LIBRARY_PATH": [freetype_lib_path, libpng_lib_path]}):
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
        """Assemble the package."""
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        os.remove(os.path.join(self.package_folder, "lib", "libfontconfig.la"))

    def package_info(self):
        """Edit package info."""
        tools.collect_libs(self)
        self.cpp_info.libs = ["fontconfig", "m", "pthread"]
