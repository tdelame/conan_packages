from shutil import rmtree
import os
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")


class LibJpeg(pyreq.BaseConanFile):
    description = "IJG is an informal group that writes and distributes a widely used free library for JPEG image compression"
    url = "http://ijg.org"
    name = "libjpeg"
    version = "9c"
    license = " "

    settings = "os"


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
        self.build_autotools()

    def package(self):
        """Assemble the package."""
        self.copy("README", dst="licenses", src=self._source_subfolder, ignore_case=True, keep_path=True)
        rmtree(os.path.join(self.package_folder, "share"))
        rmtree(os.path.join(self.package_folder, "bin"))

    def package_info(self):
        """Edit package info."""
        super(LibJpeg, self).package_info()
        self.cpp_info.libs = ["jpeg"]
