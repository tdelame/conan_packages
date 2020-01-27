from conans import ConanFile, python_requires, tools
import os

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")


class PortAudio(pyreq.CMakeConanFile):
    description = "Free, cross-platform, open-source, audio I/O library"
    url = "www.portaudio.com"
    license = " "
    name = "PortAudio"
    version = "2018-12-24"

    settings = "os", "build_type"

    def build_requirements(self):
        """Define build-time requirements."""
        super(PortAudio, self).build_requirements()
        if self.settings.os == "Linux":
            self.build_requires("libalsa/1.2.1.2@tdelame/stable" )

    def source(self):
        """Retrieve source code."""
        download_url = "https://app.assembla.com/spaces/portaudio/git/source/b7870b08f770c1e84b754e662c08b6942ff7d021?_format=zip"
        pyreq.make_directory(self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            tools.get(download_url, filename="root.zip")

    def cmake_definitions(self):
        """Setup CMake definitions."""
        definition_dict = {
            "CMAKE_BUILD_TYPE": self.settings.build_type,
            "PA_BUILD_SHARED": self.options.shared,
            "PA_BUILD_STATIC": not self.options.shared,
            "PA_ENABLE_DEBUG_OUTPUT": self.settings.build_type != "Release",
            "PA_LIBNAME_ADD_SUFFIX": self.settings.os == "Windows",
            "PA_BUILD_EXAMPLES": False,
            "PA_BUILD_TESTS": False,
            "PA_DLL_LINK_WITH_STATIC_RUNTIME": False
        }

        if self.settings.os == "Linux":
            alsa_info = self.deps_cpp_info["libalsa"]
            definition_dict["ALSA_INCLUDE_DIR"] = alsa_info.include_paths[0]
            definition_dict["ALSA_LIBRARY"] = os.path.join(alsa_info.lib_paths[0], "libasound.so")
            definition_dict["PA_USE_ALSA"] = True
            definition_dict["PA_USE_JACK"] = False

            if self.settings.build_type == "Release":
                definition_dict["CMAKE_C_FLAGS"] = "-fPIC -m64 -O3"
            else:
                definition_dict["CMAKE_C_FLAGS"] = "-fPIC -m64 -Og -g"

        elif self.settings.os == "Windows":
            definition_dict["PA_USE_MME"] = True
            definition_dict["PA_USE_WDMKS_DEVICE_INFO"] = False
            definition_dict["PA_UNICODE_BUILD"] = False
            definition_dict["PA_USE_WASAPI"] = False
            definition_dict["PA_USE_WDMKS"] = False
            definition_dict["PA_USE_ASIO"] = False
            definition_dict["PA_USE_DS"] = False

        self.add_default_definitions(definition_dict)
        return definition_dict

    def package(self):
        """Assemble the package."""
        if self.settings.os == "Linux":
            libpattern = "*.so*" if self.options.shared else "*.a"
            self.copy("portaudio.h", src="source_subfolder/include", dst="include" )
            self.copy("pa_linux_alsa.h", src="source_subfolder/include", dst="include" )
            self.copy(libpattern, dst ="lib", keep_path=False)
        elif self.settings.os == "Windows":
            self.copy("portaudio.h", src="source_subfolder/include", dst="include" )
            self.copy("pa_win_mme.h", src="source_subfolder/include", dst="include" )
            if self.options.shared:
                self.copy("*.dll", dst="lib", keep_path=False)
            self.copy("*.lib", dst="lib", keep_path=False)
        self.clean_package()
        self.package_licenses()

    def package_info(self):
        """Edit package info."""
        super(PortAudio, self).package_info()
        self.cpp_info.libs = ["portaudio"]
