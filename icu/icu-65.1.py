from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class ICU(ConanFile):
    description = "ICU is a mature, widely used set of C/C++ and Java libraries providing Unicode and Globalization support for software applications. ICU is widely portable and gives applications the same results on all platforms and between C/C++ and Java software"
    license = "ICU"
    url = "http://site.icu-project.org"
    version = "65.1"
    name = "icu"

    settings = "os"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def source(self):
        """Retrieve source code."""
        url = "https://github.com/unicode-org/icu/releases/download/release-65-1/icu4c-65_1-src.tgz"
        tools.get(url)
        os.rename("icu", self._source_subfolder)

    def build(self):
        """Build the elements to package."""
        parallel = "-j{}".format(tools.cpu_count())

        with tools.chdir(os.path.join(self._source_subfolder, "source")):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.fpic = True
            if self.settings.os == "Linux" and find_executable("lld") is not None:
                autotools.link_flags.append("-fuse-ld=lld")
            autotools.flags = ["-O3"]
            autotools.cxx_flags = ["-O3"]
            autotools.configure(args=[
                "--disable-fuzzer", "--disable-tests", "--disable-samples", "--disable-layoutex",
                "--enable-release", "--disable-debug", "--with-library-bits=64",
                "--enable-shared" if self.options.shared else "--disable-shared",
                "--disable-static" if self.options.shared else "--enable-static"
            ])
            autotools.make(args=[parallel])
            autotools.install(args=[parallel])

    def package(self):
        """Assemble the package."""
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder, ignore_case=True, keep_path=True)

        # purge unneeded directories
        rmtree(os.path.join(self.package_folder, "share"))
        rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmtree(os.path.join(self.package_folder, "lib", "icu"))

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["icui18n", "icuio", "icutest", "icutu", "icuuc", "icudata"]
