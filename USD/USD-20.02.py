import os
from conans import python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class USD(pyreq.CMakeConanFile):
    description = "Universal scene description"
    url = "http://www.openusd.org"
    license = "Modified Apache 2.0 License"
    name = "USD"
    version = "20.02"

    settings = "os"

    def requirements(self):
        """Define runtime requirements."""
        # no OSL, no RenderMan, no Maya, no Katana, no Houdini, no Draco, no usdview (uses python2), no embree (uses embree2)
        self.requires("rumba-python/1.0.0@tdelame/stable")
        self.requires("boost-headers/1.70.0@tdelame/stable")
        self.requires("boost-program-options/1.70.0@tdelame/stable")
        self.requires("boost-python/1.70.0@tdelame/stable")
        self.requires("TBB/2019-U6@tdelame/stable")
        self.requires("OpenSubdiv/3.4.0@tdelame/stable")
        self.requires("GLEW/2.1.0@tdelame/stable")
        self.requires("OpenImageIO/2.1.10.1@tdelame/stable")
        self.requires("OpenColorIO/1.1.1@tdelame/stable")
        self.requires("ptex/2.3.2@tdelame/stable")
        self.requires("alembic/1.7.10@tdelame/stable")
        self.requires("OpenEXR/2.4.0@tdelame/stable")
        self.requires("MaterialX/1.36.3@tdelame/stable")
        self.requires("libXext/1.3.4@tdelame/stable")
        self.requires("libX11/1.6.8@tdelame/stable")
        self.requires("xproto/7.0.31@tdelame/stable")
        self.requires("GLU/9.0.0@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        # USD repository still uses python2. I do not want to make a cpython/2.7 package to be 
        # able to use USD. Instead, I rely on a patch made by NVIDIA.
        # tools.get("https://github.com/PixarAnimationStudios/USD/archive/v{}.tar.gz".format(self.version))
        # os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)
        sha = "4fc4c6a82c75d87e96e259393db0a49b70a5ff57"
        tools.get("https://github.com/NVIDIAGameWorks/USD/archive/{}.zip".format(sha))
        os.rename("{}-{}".format(self.name, sha), self._source_subfolder)

        # FindBoost.cmake caches search directories such that we cannot simply put libraries in different folders.
        # The following reset the cache between the two calls to FindBoost.cmake.
        with pyreq.change_current_directory(os.path.join(self._source_subfolder, "cmake", "defaults")):
            tools.replace_in_file(
                "Packages.cmake",
                """    find_package(Boost
        COMPONENTS
            program_options
            ${BOOST_PYTHON_COMPONENT_NAME}
        REQUIRED
    )""",
                """   find_package(Boost COMPONENTS program_options REQUIRED)
       unset(Boost_LIBRARY_DIR_RELEASE CACHE)
       find_package(Boost COMPONENTS ${BOOST_PYTHON_COMPONENT_NAME} REQUIRED)"""
            )

        # FindMaterialX.cmake does not have suffix paths for linux
        with pyreq.change_current_directory(os.path.join(self._source_subfolder, "cmake", "modules")):
            tools.replace_in_file("FindMaterialX.cmake", "documents/Libraries", """documents/Libraries
    libraries/stdlib""")

    def cmake_definitions(self):
        """Setup CMake definitions."""
        defs = {
            # configure build type
            "BUILD_SHARED_LIBS": self.options.shared,

            # configure plugins
            "PXR_BUILD_OPENIMAGEIO_PLUGIN": True,
            "PXR_BUILD_OPENCOLORIO_PLUGIN": True,
            "PXR_BUILD_MATERIALX_PLUGIN": True,
            "PXR_BUILD_ALEMBIC_PLUGIN": True,
            "PXR_ENABLE_HDF5_SUPPORT": True,
            "PXR_BUILD_EMBREE_PLUGIN": False,
            "PXR_BUILD_HOUDINI_PLUGIN": False,
            "PXR_BUILD_KATANA_PLUGIN": False,
            "PXR_BUILD_DRACO_PLUGIN": False,
            "PXR_BUILD_PRMAN_PLUGIN": False,

            # configure components
            "PXR_BUILD_DOCUMENTATION": False,
            "PXR_BUILD_TESTS": False,
            "PXR_BUILD_USD_IMAGING": True,
            "PXR_BUILD_IMAGING": True,
            "PXR_BUILD_USDVIEW": False, # cannot build it in conan since it relies on deprecated python 2

            # feature support in plugins
            "PXR_ENABLE_HDF5_SUPPORT": True,
            "PXR_ENABLE_OSL_SUPPORT": False,
            "PXR_ENABLE_PTEX_SUPPORT": True,

            # help cmake to find our conan packages
            "PXR_PYTHON_MAJOR_3": True,
            "PYTHON_VERSION_NODOT": "37",
            "BOOST_INCLUDEDIR": self.deps_cpp_info["boost-headers"].include_paths[0],
            "BOOST_LIBRARYDIR": "{};{}".format(self.deps_cpp_info["boost-program-options"].lib_paths[0], self.deps_cpp_info["boost-python"].lib_paths[0]),
            "TBB_INCLUDE_DIR": self.deps_cpp_info["TBB"].include_paths[0],
            "TBB_LIBRARY": self.deps_cpp_info["TBB"].lib_paths[0],
            "OPENSUBDIV_ROOT_DIR": self.deps_cpp_info["OpenSubdiv"].rootpath,
            "GLEW_LOCATION": self.deps_cpp_info["GLEW"].rootpath,
            "OIIO_BASE_DIR": self.deps_cpp_info["OpenImageIO"].rootpath,
            "OCIO_BASE_DIR": self.deps_cpp_info["OpenColorIO"].rootpath,
            "PTEX_LOCATION": self.deps_cpp_info["ptex"].rootpath,
            "ALEMBIC_DIR": self.deps_cpp_info["alembic"].rootpath,
            "OPENEXR_LOCATION": self.deps_cpp_info["OpenEXR"].rootpath,
            "HDF5_ROOT": self.deps_cpp_info["hdf5"].rootpath,
            "MATERIALX_ROOT": self.deps_cpp_info["MaterialX"].rootpath,
            "OPENGL_gl_LIBRARY": self.deps_cpp_info["GLU"].lib_paths[0],
        }

        if self.settings.os == "Linux":
            # rely on macros defined in the patched FindX11.cmake to find conan packages
            defs["CONAN_X11_INC_SEARCH_PATH"] = "{};{};{}".format(
                ";".join(self.deps_cpp_info["libXext"].include_paths),
                ";".join(self.deps_cpp_info["xproto"].include_paths),
                ";".join(self.deps_cpp_info["libX11"].include_paths))

            defs["CONAN_X11_LIB_SEARCH_PATH"] = "{};{}".format(
                ";".join(self.deps_cpp_info["libXext"].lib_paths),
                ";".join(self.deps_cpp_info["libX11"].lib_paths))

            # FindOpenGL.cmake always believe GLU is in system path
            includes = []
            for dep in ["GLU"]:
                includes += ["-I " + i for i in self.deps_cpp_info[dep].include_paths]
            defs["CMAKE_CXX_FLAGS"] = " ".join(includes)                

        self.add_default_definitions(defs)
        return defs

    def package(self):
        """Assemble the package."""
        super(USD, self).package()
        pyreq.fix_shebangs_in_directory(os.path.join(self.package_folder, "bin"), "python3.7")

    def package_info(self):
        """Edit package info."""
        super(USD, self).package_info()
        self.env_info.PXR_PLUGINPATH_NAME = os.path.join(self.package_folder, "plugin", "usd")
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python"))

