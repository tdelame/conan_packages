from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import ConanFile, CMake, tools

class FreeType(ConanFile):
    description = "freely available software library to render fonts"
    license = "FTL"
    url = "https://www.freetype.org"
    version = "2.9.1"
    name = "freetype"

    settings = "os"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("cmake/3.15.4@tdelame/stable")
        self.build_requires("ninja/1.9.0@tdelame/stable")

    def requirements(self):
        """Define runtime requirements."""
        self.requires("libpng/1.6.37@tdelame/stable")
        self.requires("zlib/1.2.11@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        directory_name = "freetype-{}".format(self.version)
        url = "https://download.savannah.gnu.org/releases/freetype/{}.tar.gz".format(directory_name)
        tools.get(url)
        os.rename(directory_name, self._source_subfolder)

    def _configure_cmake(self):
        definition_dict = {
            # help cmake to find our libpng
            "CMAKE_PREFIX_PATH": self.deps_cpp_info["libpng"].rootpath,

            # do not know if it's still necessary, but it cost nothing
            "CMAKE_BUILD_TYPE": "Release",

            # do not even try to find HarfBuzz or BZip2
            "CMAKE_DISABLE_FIND_PACKAGE_HarfBuzz": True,
            "CMAKE_DISABLE_FIND_PACKAGE_BZip2": True,

            # help cmake to find our zlib
            "ZLIB_ROOT": self.deps_cpp_info["zlib"].rootpath,

            "BUILD_SHARED_LIBS": self.options.shared,

            # configure freetype options
            "FT_WITH_HARFBUZZ": False,
            "FT_WITH_BZIP2": False,
            "FT_WITH_ZLIB": True,
            "FT_WITH_PNG": True,
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
        self.copy("FTL.txt", src=os.path.join(self._source_subfolder, "docs"), dst="licenses", ignore_case=True, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

        # purge unneeded directories
        rmtree(os.path.join(self.package_folder, "lib", "cmake"))
        rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs == ["freetype"]
        self.cpp_info.includedirs = [os.path.join("include", "freetype2")]
