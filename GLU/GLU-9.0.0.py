from conans import python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class GLU(pyreq.BaseConanFile):
    license = "SGI FREE SOFTWARE LICENSE B"
    description = " "
    version = "9.0.0"
    settings = "os"
    name = "GLU"
    url = " "

    exports_sources = ["glu.h", "glu_mangle.h", "libGLU.so", "libGLU.so.1", "libGLU.so.1.3.1"]

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def package(self):
        self.copy("*.h", dst="include/GL")
        self.copy("*.so*", dst="lib")

    def package_info(self):
        super(GLU, self).package_info()
        self.cpp_info.libs = ["GLU"]
        self.cpp_info.includedirs = ["include"]
