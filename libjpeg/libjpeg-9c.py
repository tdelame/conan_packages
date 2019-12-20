from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class LibJpeg(ConanFile):
    description = "IJG is an informal group that writes and distributes a widely used free library for JPEG image compression"
    url = "http://ijg.org"
    name = "libjpeg"
    version = "9c"
    license = " "

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
        url = "http://ijg.org/files/jpegsrc.v{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename("jpeg-{}".format(self.version), self._source_subfolder)

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
        self.copy("README", dst="licenses", src=self._source_subfolder, ignore_case=True, keep_path=True)
        rmtree(os.path.join(self.package_folder, "share"))
        rmtree(os.path.join(self.package_folder, "bin"))

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["libjpeg"]
