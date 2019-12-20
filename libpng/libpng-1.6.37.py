from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import ConanFile, CMake, tools

class LibPNG(ConanFile):
    description = "official PNG reference library"
    license = "libpng 2"
    url = "http://libpng.org"
    version = "1.6.37"
    name = "libpng"

    settings = "os"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os not in ["Linux", "Windows"]:
            raise RuntimeError("This recipe is only available for Linux and Windows")

    def requirements(self):
        """Define runtime requirements."""
        self.requires("zlib/1.2.11@tdelame/stable")

    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("cmake/3.15.4@tdelame/stable")
        self.build_requires("ninja/1.9.0@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        url = "http://prdownloads.sourceforge.net/libpng/libpng-1.6.37.tar.gz"
        tools.get(url)
        os.rename("libpng-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        definition_dict = {
            "PNG_HARDWARE_OPTIMIZATIONS": True,
            "PNG_FRAMEWORK": False,
            "PNG_SHARED": self.options.shared,
            "PNG_STATIC": not self.options.shared,
            "PNG_DEBUG": False,
            "PNG_TESTS": False,

            "ZLIB_ROOT": self.deps_cpp_info["zlib"].rootpath
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
        rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmtree(os.path.join(self.package_folder, "lib", "libpng"))
        rmtree(os.path.join(self.package_folder, "share"))

    def package_info(self):
        """Edit package info."""
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["libpng16"]
        elif self.settings.os == "Linux":
            self.cpp_info.libs = ["png16", "m"]
