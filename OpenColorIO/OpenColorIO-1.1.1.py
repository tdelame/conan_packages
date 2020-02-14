import os
from conans import python_requires, tools, CMake
from distutils.spawn import find_executable

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class OpenColorIO(pyreq.CMakeConanFile):
    description = "Open Source Color Management"
    url = "https://opencolorio.org"
    license = ""
    name = "OpenColorIO"
    version = "1.1.1"

    settings = "os"

    def source(self):
        """Retrieve source code."""
        tools.get("https://github.com/AcademySoftwareFoundation/OpenColorIO/archive/v{}.tar.gz".format(self.version))
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

        with tools.chdir(os.path.join(self._source_subfolder, "src", "core")):
            tools.replace_in_file(
                "Config.cpp",
                "cacheidnocontext_ = cacheidnocontext_;",
                "cacheidnocontext_ = rhs.cacheidnocontext_;")

    def cmake_definitions(self):
        """Setup CMake definitions."""
        definitions = {
            "OCIO_BUILD_APPS": False,
            "OCIO_BUILD_DOCS": False,
            "OCIO_BUILD_JNIGLUE": False,
            "OCIO_BUILD_NUKE": False,
            "OCIO_BUILD_PYGLUE": False,
            "OCIO_BUILD_TESTS": False,
            "OCIO_BUILD_TRUELIGHT": False,
            "OCIO_BUILD_STATIC": not self.options.shared,
            "OCIO_BUILD_SHARED": self.options.shared,
        }

        if self.settings.os == "Linux":
            definitions["CMAKE_CXX_FLAGS"] = "-Wno-deprecated-declarations"

        self.add_default_definitions(definitions)
        return definitions

    def configure_cmake(self):
        """Override cmake configuration for in-source build without Ninja."""
        cmake = CMake(self, generator=None if self.settings.os != "Linux" else "Unix Makefiles")
        cmake.configure(defs=self.cmake_definitions(), source_folder=self._source_subfolder, build_folder=self._source_subfolder)
        return cmake

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["OpenColorIO"]
