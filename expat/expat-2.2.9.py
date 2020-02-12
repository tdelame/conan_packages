from conans import python_requires, CMake
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")


class Expat(pyreq.CMakeConanFile):
    description = "Fast streaming XML parser written in C"
    license = "MIT like"
    url = "https://libexpat.github.io"
    version = "2.2.9"
    name = "expat"

    settings = "os"

    def source(self):
        """Retrieve source code."""
        self.download("https://github.com/libexpat/libexpat/releases/download/R_2_2_9")

    def cmake_definitions(self):
        definition_dict = {
            "EXPAT_BUILD_DOCS": False,
            "EXPAT_BUILD_EXAMPLES": False,
            "EXPAT_BUILD_FUZZERS": False,
            "EXPAT_BUILD_TESTS": False,
            "EXPAT_BUILD_TOOLS": False,
            "EXPAT_SHARED_LIBS": self.options.shared
        }
        self.add_default_definitions(definition_dict)
        return definition_dict

    def package_info(self):
        """Edit package info."""
        super(Expat, self).package_info()
        self.cpp_info.libs == ["expat"]
