from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import ConanFile, CMake, tools

class DoubleConversion(ConanFile):
    description = "Efficient binary-decimal and decimal-binary conversion routines for IEEE doubles"
    license = "BSD 3"
    url = "https://github.com/google/double-conversion"
    version = "3.1.5"
    name = "double-conversion"

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
        url = "https://github.com/google/double-conversion/archive/v{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename("double-conversion-{}".format(self.version), self._source_subfolder)

        with tools.chdir(self._source_subfolder):
            tools.replace_in_file(
                "CMakeLists.txt",
                "add_library(double-conversion",
                "add_library(double-conversion {}".format(
                    "SHARED" if self.options.shared else "STATIC"))

    def _configure_cmake(self):
        definition_dict = {
            "BUILD_TESTING": False
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
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

        # purge unneeded directories
        rmtree(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs == ["double-conversion"]
