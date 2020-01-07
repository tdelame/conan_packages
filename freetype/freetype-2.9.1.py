from distutils.spawn import find_executable
from shutil import rmtree, copyfile, copy
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

    def _make_freetype_config(self):
        # taken from https://github.com/bincrafters/conan-freetype/blob/testing/2.10.0/conanfile.py
        # CMake build is easier to configure for the freetype library, however freetype-config is
        # not easily built from CMake.
        freetype_config_in = os.path.join(self._source_subfolder, "builds", "unix", "freetype-config.in")
        if not os.path.isdir(os.path.join(self.package_folder, "bin")):
            os.makedirs(os.path.join(self.package_folder, "bin"))
        freetype_config = os.path.join(self.package_folder, "bin", "freetype-config")
        copy(freetype_config_in, freetype_config)
        libs = "-lfreetype"
        staticlibs = "-lm %s" % libs if self.settings.os == "Linux" else libs
        tools.replace_in_file(freetype_config, r"%PKG_CONFIG%", r"/bin/false")  # never use pkg-config
        tools.replace_in_file(freetype_config, r"%prefix%", r"$conan_prefix")
        tools.replace_in_file(freetype_config, r"%exec_prefix%", r"$conan_exec_prefix")
        tools.replace_in_file(freetype_config, r"%includedir%", r"$conan_includedir")
        tools.replace_in_file(freetype_config, r"%libdir%", r"$conan_libdir")
        tools.replace_in_file(freetype_config, r"%ft_version%", r"$conan_ftversion")
        tools.replace_in_file(freetype_config, r"%LIBSSTATIC_CONFIG%", r"$conan_staticlibs")
        tools.replace_in_file(freetype_config, r"-lfreetype", libs)
        tools.replace_in_file(freetype_config, r"export LC_ALL", """export LC_ALL
BINDIR=$(dirname $0)
conan_prefix=$(dirname $BINDIR)
conan_exec_prefix=${{conan_prefix}}/bin
conan_includedir=${{conan_prefix}}/include
conan_libdir=${{conan_prefix}}/lib
conan_ftversion={version}
conan_staticlibs="{staticlibs}"
""".format(version="22.1.16", staticlibs=staticlibs))
        # check libtool version number in doc/VERSION.TXT
        if self.settings.os == "Linux":
            os.chmod(freetype_config, os.stat(freetype_config).st_mode | 0o111)

    def build(self):
        """Build the elements to package."""
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        """Assemble the package."""
        self.copy("FTL.txt", src=os.path.join(self._source_subfolder, "docs"), dst="licenses", ignore_case=True, keep_path=False)
        cmake = self._configure_cmake()
        cmake.install()

        self._make_freetype_config()

        # some configure scripts look for 'freetype' instead of 'freetype2'.
        copyfile(
            os.path.join(self.package_folder, "lib", "pkgconfig", "freetype2.pc"),
            os.path.join(self.package_folder, "lib", "pkgconfig", "freetype.pc"))

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs == ["freetype"]
        self.cpp_info.includedirs = [os.path.join("include", "freetype2")]
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
