from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import python_requires, CMake, tools

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class DoubleConversion(pyreq.CMakeConanFile):
    description = "Efficient binary-decimal and decimal-binary conversion routines for IEEE doubles"
    license = "BSD 3"
    url = "https://github.com/google/double-conversion"
    version = "3.1.5"
    name = "double-conversion"

    settings = "os"

    def source(self):
        """Retrieve source code."""
        url = "https://github.com/google/double-conversion/archive/v{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename("double-conversion-{}".format(self.version), self._source_subfolder)

        with tools.chdir(self._source_subfolder):
            tools.replace_in_file(
                "CMakeLists.txt",
                "add_library(double-conversion",
                "add_library(double-conversion {}".format(
                    "SHARED" if self.options.shared else "STATIC"))

    def cmake_definitions(self):
        definition_dict = {
            "BUILD_TESTING": False
        }
        self.add_default_definitions(definition_dict)
        return definition_dict

    def package_info(self):
        """Edit package info."""
        super(DoubleConversion, self).package_info()
        self.cpp_info.libs == ["double-conversion"]
