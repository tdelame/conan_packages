import os
from conans import python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

CMAKE_WRAPPER = """
project(wrapper)
add_subdirectory("${CMAKE_SOURCE_DIR}/build/cmake")
"""

class zstd(pyreq.CMakeConanFile):
    description = "Fast real-time compression algorithm"
    url = "https://github.com/facebook/zstd"
    license = "BSD-3-Clause"
    name = "zstd"
    version = "1.4.4"
    settings = "os"

    def source(self):
        """Retrieve source code."""
        self.download("https://github.com/facebook/zstd/releases/download/v1.4.4")

        with open(os.path.join(self._source_subfolder, "CMakeLists.txt"), "w") as outfile:
            outfile.write(CMAKE_WRAPPER)

    def cmake_definitions(self):
        definition_dict = {
            "ZSTD_MULTITHREAD_SUPPORT": True,
            "ZSTD_BUILD_PROGRAMS": False,
            "ZSTD_BUILD_TESTS": False,
            "ZSTD_BUILD_STATIC": not self.options.shared,
            "ZSTD_BUILD_SHARED": self.options.shared
        }
        self.add_default_definitions(definition_dict)
        return definition_dict

    def package_info(self):
        super(zstd, self).package_info()
        self.cpp_info.libs = ["zstd"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
