from conans import ConanFile, python_requires, tools, CMake
import shutil
import os

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class openimageio(pyreq.CMakeConanFile):
    description = "library for reading and writing images, and a bunch of related classes, utilities, and applications."
    license = "BSD 3-Clause License"
    url = "https://sites.google.com/site/openimageio/"

    name = "openimageio"
    version = "2.1.10.1"

    settings = "os"

    def build_requirements(self):
        """Define build-time requirements."""
        self.requires("boost-headers/1.70.0@tdelame/stable")
        super(openimageio, self).build_requirements()

    def requirements(self):
        """Define runtime requirements."""
        self.requires("openEXR/2.4.0@tdelame/stable")
        self.requires("tiff/4.1.0@tdelame/stable")
        self.requires("libjpeg/9c@tdelame/stable")
        self.requires("libpng/1.6.37@tdelame/stable")
        self.requires("zlib/1.2.11@tdelame/stable")
        self.requires("boost-filesystem/1.70.0@tdelame/stable")
        self.requires("boost-thread/1.70.0@tdelame/stable")
        self.requires("TBB/2019-U6@tdelame/stable")
        self.requires("bzip2/1.0.8@tdelame/stable")
        self.requires("freetype/2.9.1@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        url = "https://github.com/OpenImageIO/oiio/archive/Release-{}.tar.gz".format(self.version)
        directory = "oiio-Release-{}".format(self.version)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def cmake_definitions(self):
        """Setup CMake definitions."""
        boost_lib_paths = []
        boost_libs = []
        for component in ["filesystem", "thread"]:
            dep = self.deps_cpp_info["boost-{}".format(component)]
            boost_lib_paths.extend(dep.lib_paths)
            boost_libs.extend(dep.libs)
        
        definition_dict = {
            "OIIO_BUILD_TESTS": False,
            "OIIO_BUILD_TOOLS": False,
            "OIIO_THREAD_ALLOW_DCLP": True,
            
            "EMBEDPLUGINS": True,
            "INSTALL_DOCS": False,
            "BUILD_DOCS": False,
            "USE_STD_REGEX": True,

            "USE_PYTHON": False,
            "USE_HDF5": False,
            "USE_OpenColorIO": False,
            "USE_OpenCV": False,
            "USE_DCMTK": False,
            "USE_Field3D": False,
            "USE_Libheif": False,
            "USE_LibRaw": False,
            "USE_Webp": False,
            "USE_Nuke": False,
            "USE_R3DSDK": False,
            "USE_OpenGL": False,
            "USE_OpenVDB": False,
            "USE_PTex": False,
            "USE_Qt5": False,
            "USE_Libsquish": False,
            "USE_OpenJpeg": False,
            "USE_FFmpeg": False,
            "USE_GIF": False,
            "USE_JPEGTurbo": False,

            "BOOST_CUSTOM": True,
            "Boost_VERSION": "1.70.0",
            "Boost_INCLUDE_DIRS": self.deps_cpp_info["boost-headers"].include_paths[0],
            "Boost_LIBRARY_DIRS": ";".join(["{}".format(path) for path in boost_lib_paths]),
            "Boost_LIBRARIES": ";".join(["{}".format(lib) for lib in boost_libs]),

            "ZLIB_ROOT": self.deps_cpp_info["zlib"].rootpath,
            
            "PNG_ROOT": self.deps_cpp_info["libpng"].rootpath,

            "TIFF_ROOT": self.deps_cpp_info["tiff"].rootpath,

            "Freetype_ROOT": self.deps_cpp_info["freetype"].rootpath,

            "BZip2_ROOT": self.deps_cpp_info["bzip2"].rootpath,


            "OpenEXR_ROOT": self.deps_cpp_info["openEXR"].rootpath,

            "JPEG_ROOT": self.deps_cpp_info["libjpeg"].rootpath,

            "CMAKE_CXX_FLAGS": "-fPIC -Wno-error=deprecated -m64 -O3"
        }


        self.add_default_definitions(definition_dict)
        return definition_dict

    def build(self):
        # this project expect is very picky about cmake invocation...
        build_dir = os.path.join(self._source_subfolder, "build")
        package_dir = os.path.abspath(self.package_folder)
        os.makedirs(build_dir)
        os.makedirs(package_dir)

        compile_command = 'cmake ../ -G"Ninja" -DCMAKE_INSTALL_PREFIX="{package_folder}" {definitions}'.format(
            package_folder=package_dir,
            definitions=" ".join(['-D{0}="{1}"'.format(key, value) for key, value in self.cmake_definitions().items()]))

        install_command = 'ninja install'

        with tools.chdir(build_dir):
            self.run(compile_command)
            self.run(install_command)

    def package(self):
        os.rename(
            os.path.join(self.package_folder, "lib64"),
            os.path.join(self.package_folder, "lib"))
        self.package_licenses()
        self.clean_package()          
   
    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["OpenImageIO", "OpenImageIO_Util"]
