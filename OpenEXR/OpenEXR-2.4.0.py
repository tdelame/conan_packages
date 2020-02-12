import os
from conans import python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class openEXR(pyreq.CMakeConanFile):
    description = "specification and reference implementation of the EXR file format"
    license = "BSD-3-Clause"
    url = "https://www.openexr.com/"
    version = "2.4.0"
    name = "OpenEXR"

    settings = "os"

    def requirements(self):
        """Define runtime requirements."""
        self.requires("zlib/1.2.11@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        url = "https://github.com/AcademySoftwareFoundation/openexr/archive/v{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename("openexr-{}".format(self.version), self._source_subfolder)

    def cmake_definitions(self):
        """Setup CMake definitions."""
        definition_dict = {
            "NAMESPACE_VERSIONING": False,
            "PYILMBASE_ENABLE": False,
            "OPENEXR_VIEWERS_ENABLE": False,
            "BUILD_TESTING": False,
            "OPENEXR_BUILD_UTILS": False,

            "ZLIB_ROOT": self.deps_cpp_info["zlib"].rootpath,
        }

        self.add_default_definitions(definition_dict)
        return definition_dict       

    def package_info(self):
        """Edit package info."""
        super(openEXR, self).package_info()
        self.cpp_info.libs = ["Half", "Iex", "IexMath", "IlmImf", "IlmImfUtil", "IlmThread", "Imath"]
        self.cpp_info.includedirs = ["include", "include/OpenEXR"]
