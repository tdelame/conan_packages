from distutils.spawn import find_executable
from shutil import rmtree
import os
from conans import ConanFile, CMake, tools


class OpenAL(ConanFile):
    description = "OpenAL Soft is a software implementation of the OpenAL 3D audio API."
    url = "https://www.openal.org"
    license = "MIT"
    name = "openal"
    version = "1.20.0"

    settings = "os"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("cmake/3.15.4@tdelame/stable")
        self.build_requires("ninja/1.9.0@tdelame/stable")

        # as a build requirement because we do not want to have hard link on such library: the
        # system one must be used instead.
        if self.settings.os == "Linux":
            self.build_requires("libalsa/1.2.1.2@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        directory = "openal-soft-openal-soft-{}".format(self.version)
        url = "https://github.com/kcat/openal-soft/archive/openal-soft-{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def _configure_cmake(self):
        definition_dict = {
            "ALSOFT_UTILS": False,
            "ALSOFT_NO_CONFIG_UTIL": True,
            "ALSOFT_EXAMPLES": False,
            "ALSOFT_TESTS": False,
            "ALSOFT_CONFIG": False,
            "ALSOFT_HRTF_DEFS": False,
            "ALSOFT_AMBDEC_PRESETS": False,
            "CMAKE_DISABLE_FIND_PACKAGE_SoundIO": False,
            "LIBTYPE": "SHARED" if self.options.shared else "STATIC",
        }

        if self.settings.os == "Linux":

            alsa_library = os.path.join(self.deps_cpp_info["libalsa"].lib_paths[0], "libasound")
            alsa_library = "{}.{}".format(alsa_library, "so" if self.options["libalsa"].shared else "a")

            definition_dict["ALSA_INCLUDE_DIR"] = self.deps_cpp_info["libalsa"].include_paths[0]
            definition_dict["ALSA_LIBRARY"] = alsa_library

            if find_executable("lld") is not None:
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
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        rmtree(os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmtree(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        super(OpenAL, self).package_info()
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["OpenAL32", 'winmm']

        if self.settings.os == 'Linux':
            self.cpp_info.system_libs.extend(['dl', 'm'])
            self.cpp_info.libs = ["openal"]

        self.cpp_info.includedirs = ["include", "include/AL"]

        if not self.options.shared:
            self.cpp_info.defines.append('AL_LIBTYPE_STATIC')
