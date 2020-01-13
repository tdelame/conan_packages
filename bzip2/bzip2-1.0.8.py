import os
import shutil
from glob import glob
from distutils.spawn import find_executable
from conans import tools, CMake, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

# adapted from https://github.com/conan-io/conan-center-index/blob/master/recipes/bzip2/1.0.8/CMakeLists.txt
CMAKE_LIST_CONTENT = """
cmake_minimum_required(VERSION 3.1.2)
project(bzip2 C)

include(GNUInstallDirs)

if(MSVC OR MSVC90 OR MSVC10)
    set(MSVC ON)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

set(SOURCE_SUBFOLDER ${{CMAKE_CURRENT_SOURCE_DIR}}/source_subfolder)
set(BZ2_LIBRARY bz2)
set(BZ2_NAMESPACE BZip2)
set(BZ2_CONFIG ${{BZ2_NAMESPACE}}Config)

add_library(${{BZ2_LIBRARY}} {SHARED_OR_STATIC} 
    blocksort.c bzlib.c compress.c crctable.c decompress.c
    huffman.c randtable.c bzlib.h bzlib_private.h)
target_include_directories(${{BZ2_LIBRARY}} PRIVATE ${{CMAKE_CURRENT_SOURCE_DIR}})

add_executable(${{CMAKE_PROJECT_NAME}} bzip2.c)
target_link_libraries(${{CMAKE_PROJECT_NAME}} ${{BZ2_LIBRARY}})
target_include_directories(${{CMAKE_PROJECT_NAME}} PRIVATE ${{CMAKE_CURRENT_SOURCE_DIR}})

set_target_properties(${{BZ2_LIBRARY}} PROPERTIES VERSION "1.0.8" SOVERSION "1")

export(TARGETS ${{BZ2_LIBRARY}}
       NAMESPACE ${{BZ2_NAMESPACE}}::
       FILE "${{CMAKE_CURRENT_BINARY_DIR}}/${{BZ2_CONFIG}}.cmake")

install(TARGETS ${{BZ2_LIBRARY}}
        EXPORT ${{BZ2_CONFIG}}
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)


install(TARGETS ${{CMAKE_PROJECT_NAME}}
        EXPORT ${{BZ2_CONFIG}}
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

install(FILES bzlib.h DESTINATION include)

install(EXPORT ${{BZ2_CONFIG}}
        DESTINATION "${{CMAKE_INSTALL_LIBDIR}}/cmake/${{CMAKE_PROJECT_NAME}}"
        NAMESPACE ${{BZ2_LIBRARY}}::)
"""


class bzip2(pyreq.BaseConanFile):
    description = "free and open-source file compression program that uses the Burrows Wheeler algorithm"
    url = "http://www.bzip.org"
    license = "bzip2-1.0.8"
    
    name = "bzip2"
    version = "1.0.8"
    settings = "os"
    
    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""        
        if self.settings.os != "Linux":
            raise RuntimeError("bzip2 recipe is not available yet for your OS")

    def source(self):
        """Retrieve source code."""
        directory = "bzip2-{}".format(self.version)
        url = "https://sourceware.org/pub/bzip2/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

        with open("{}/CMakeLists.txt".format(self._source_subfolder), "w") as outfile:
            outfile.write(CMAKE_LIST_CONTENT.format(
                SHARED_OR_STATIC="SHARED" if self.options.shared else "STATIC"))

    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("cmake/3.15.4@tdelame/stable")
        self.build_requires("ninja/1.9.0@tdelame/stable")        

    def build(self):
        """Build the elements to package."""

        definition_dict = {}

        if self.settings.os == "Linux" and find_executable("lld") is not None:
            definition_dict["CMAKE_SHARER_LINKER_FLAGS"] = "-fuse-ld=lld"
            definition_dict["CMAKE_EXE_LINKER_FLAGS"] = "-fuse-ld=lld"

        cmake = CMake(self, generator="Ninja")
        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        cmake.build()
        cmake.install()

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["bz2"]
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))        