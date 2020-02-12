from shutil import copyfile, copy
import os
from conans import python_requires, ConanFile, CMake, tools

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class FreeType(pyreq.CMakeConanFile):
    description = "freely available software library to render fonts"
    license = "FTL"
    url = "https://www.freetype.org"
    version = "2.9.1"
    name = "freetype"

    settings = "os"

    def requirements(self):
        """Define runtime requirements."""
        self.requires("libpng/1.6.37@tdelame/stable")
        self.requires("zlib/1.2.11@tdelame/stable")
        self.requires("bzip2/1.0.8@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        self.download("https://download.savannah.gnu.org/releases/freetype")

    def cmake_definitions(self):
        definition_dict = {
            # help cmake to find our libpng
            "CMAKE_PREFIX_PATH": self.deps_cpp_info["libpng"].rootpath,

            # do not even try to find HarfBuzz or BZip2
            "CMAKE_DISABLE_FIND_PACKAGE_HarfBuzz": True,

            # help cmake to find our zlib
            "ZLIB_ROOT": self.deps_cpp_info["zlib"].rootpath,

            # help cmake to find our bzip2
            "BZIP2_INCLUDE_DIR": self.deps_cpp_info["bzip2"].include_paths[0],
            "BZIP2_LIBRARIES": os.path.join(self.deps_cpp_info["bzip2"].lib_paths[0], "libbz2.so"),

            "BUILD_SHARED_LIBS": self.options.shared,

            # configure freetype options
            "FT_WITH_HARFBUZZ": False,
            "FT_WITH_BZIP2": True,
            "FT_WITH_ZLIB": True,
            "FT_WITH_PNG": True,
        }

        self.add_default_definitions(definition_dict)
        return definition_dict

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

    def package(self):
        """Assemble the package."""
        super(FreeType, self).package()
        self.copy("FTL.txt", src=os.path.join(self._source_subfolder, "docs"), dst="licenses", ignore_case=True, keep_path=False)
        self._make_freetype_config()

        # some configure scripts look for 'freetype' instead of 'freetype2'.
        copyfile(
            os.path.join(self.package_folder, "lib", "pkgconfig", "freetype2.pc"),
            os.path.join(self.package_folder, "lib", "pkgconfig", "freetype.pc"))

    def package_info(self):
        """Edit package info."""
        super(FreeType, self).package_info()
        self.cpp_info.libs == ["freetype"]
        self.cpp_info.includedirs = [os.path.join("include", "freetype2")]

