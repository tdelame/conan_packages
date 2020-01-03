from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import ConanFile, CMake, tools

CMAKE_WRAPPER = """
project(wrapper)
add_subdirectory("${CMAKE_SOURCE_DIR}/build/cmake")
"""

class ZstdC(ConanFile):
    description = "Fast real-time compression algorithm"
    url = "https://github.com/facebook/zstd"
    license = "BSD-3-Clause"
    name = "zstd"
    version = "1.4.4"

    settings = "os"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("cmake/3.15.4@tdelame/stable")
        self.build_requires("ninja/1.9.0@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        directory = "zstd-{}".format(self.version)
        url = "https://github.com/facebook/zstd/releases/download/v1.4.4/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

        with open(os.path.join(self._source_subfolder, "CMakeLists.txt"), "w") as outfile:
            outfile.write(CMAKE_WRAPPER)

    def _configure_cmake(self):
        definition_dict = {
            "ZSTD_MULTITHREAD_SUPPORT": True,
            "ZSTD_BUILD_PROGRAMS": False,
            "ZSTD_BUILD_TESTS": False,
            "ZSTD_BUILD_STATIC": not self.options.shared,
            "ZSTD_BUILD_SHARED": self.options.shared
        }

        if self.settings.os == "Linux" and find_executable("lld") is not None:
            definition_dict["CMAKE_SHARER_LINKER_FLAGS"] = "-fuse-ld=lld"
            definition_dict["CMAKE_EXE_LINKER_FLAGS"] = "-fuse-ld=lld"

        cmake = CMake(self, generator="Ninja")
        cmake.configure(
            defs=definition_dict,
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder)
        return cmake


    def build(self):
        """Build the elements to package."""
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["zstd"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
