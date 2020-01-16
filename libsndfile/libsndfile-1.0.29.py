from conans import ConanFile, python_requires, tools
import os, shutil

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class LibSndFile(pyreq.CMakeConanFile):
    description = "C library for reading and writing files containing samples audio data"
    url = "http://www.mega-nerd.com/libsndfile/"
    license = "LGPL"
    name = "libsndfile"
    version = "1.0.29"
    
    settings = "os", "build_type"
    
    def source(self):
        """Retrieve source code."""
        sha = "1a87c443fe37bd67c8d1e2d2b4c8b0291806eb90"
        download_url = "https://github.com/erikd/libsndfile/archive/{}.zip".format(sha)
        zipped_folder_name = "libsndfile-{}.zip".format(sha)

        tools.download(download_url, zipped_folder_name)
        tools.unzip(zipped_folder_name)
        os.rename("libsndfile-{}".format(sha), self._source_subfolder)
        os.remove(zipped_folder_name)

        if self.settings.os == "Windows":
            with tools.chdir(os.path.join(self._source_subfolder, "src")):
                tools.replace_in_file(
                    "common.c", 
                    "#if HAVE_UNISTD_H", 
                    '''#undef HAVE_UNISTD_H
#if HAVE_UNISTD_H''')

    def cmake_definitions(self):
        """Setup CMake definitions."""
        #Note: I do not add ogg, flac, and vorbis dependences here since we do
        # not have requests nor requirements for these formats.
        definition_dict = {
            "CMAKE_BUILD_TYPE": "RELEASE" if self.settings.build_type == "Release" else "DEBUG",
            "ENABLE_COMPATIBLE_LIBSNDFILE_NAME": True,
            "BUILD_SHARED_LIBS": self.options.shared,
            "ENABLE_PACKAGE_CONFIG": False,
            "ENABLE_BOW_DOCS": False,
            "BUILD_PROGRAMS": False,
            "BUILD_EXAMPLES": False,
            "BUILD_TESTING": False,
            "BUILD_REGTEST": False,
        }

        if self.settings.os == "Linux":

            if self.settings.build_type == "Release":
                definition_dict[ "CMAKE_C_FLAGS" ] = "-fPIC -m64 -O3"
            else:
                definition_dict[ "CMAKE_C_FLAGS" ] = "-fPIC -m64 -Og -g"

        self.add_default_definitions(definition_dict)
        return definition_dict

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["sndfile"]
