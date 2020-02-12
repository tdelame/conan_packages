from conans import python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class LibPNG(pyreq.CMakeConanFile):
    description = "official PNG reference library"
    license = "libpng 2"
    url = "http://libpng.org"
    version = "1.6.37"
    name = "libpng"

    settings = "os"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os not in ["Linux", "Windows"]:
            raise RuntimeError("This recipe is only available for Linux and Windows")

    def requirements(self):
        """Define runtime requirements."""
        self.requires("zlib/1.2.11@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        self.download("http://prdownloads.sourceforge.net/libpng")

    def cmake_definitions(self):
        definition_dict = {
            "PNG_HARDWARE_OPTIMIZATIONS": True,
            "PNG_FRAMEWORK": False,
            "PNG_SHARED": self.options.shared,
            "PNG_STATIC": not self.options.shared,
            "PNG_DEBUG": False,
            "PNG_TESTS": False,

            "ZLIB_ROOT": self.deps_cpp_info["zlib"].rootpath
        }

        self.add_default_definitions(definition_dict)
        return definition_dict

    def package_info(self):
        """Edit package info."""
        super(LibPNG, self).package_info()
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["libpng16"]
        elif self.settings.os == "Linux":
            self.cpp_info.libs = ["png16", "m"]

