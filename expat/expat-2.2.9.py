from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import ConanFile, CMake, tools

class Expat(ConanFile):
    description = "Fast streaming XML parser written in C"
    license = "MIT like"
    url = "https://libexpat.github.io"
    version = "2.2.9"
    name = "expat"

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
        url = "https://github.com/libexpat/libexpat/releases/download/R_2_2_9/expat-2.2.9.tar.gz"
        tools.get(url)
        os.rename("expat-2.2.9", self._source_subfolder)

    def _configure_cmake(self):
        definition_dict = {
            "CMAKE_BUILD_TYPE": "Release",
            "EXPAT_BUILD_DOCS": False,
            "EXPAT_BUILD_EXAMPLES": False,
            "EXPAT_BUILD_FUZZERS": False,
            "EXPAT_BUILD_TESTS": False,
            "EXPAT_BUILD_TOOLS": False,
            "EXPAT_SHARED_LIBS": self.options.shared
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
        """Assemble the package."""
        self.copy("COPYING", src=os.path.join(self._source_subfolder, "expat"), dst="licenses", ignore_case=True, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

        # purge unneeded directories
        rmtree(os.path.join(self.package_folder, "lib", "cmake"))
        rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmtree(os.path.join(self.package_folder, "share"))

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs == ["expat"]
