from conans import ConanFile, tools
import os

class GLUConan(ConanFile):
    license = "SGI FREE SOFTWARE LICENSE B"
    description = " "
    version = "9.0.0"
    settings = "os"
    name = "GLU"
    url = " "

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def package(self):
        self.copy("*", src="include", dst="include")
        self.copy("*", src="lib", dst="lib")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
