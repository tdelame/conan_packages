from conans import python_requires

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class hdf5(pyreq.CMakeConanFile):
    description = "High-performance data management and storage suite. Compiled with thread safety, with C++ lib and with HL lib"
    license = "BSD"
    url = "https://www.hdfgroup.org/"
    name = "hdf5"
    version = "1.8.21"

    settings = "os"
    
    def requirements(self):
        """Define runtime requirements."""
        self.requires("zlib/1.2.11@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        self.download("https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.8/hdf5-1.8.21/src")

    def cmake_definitions(self):
        """Setup CMake definitions."""
        zlib_root_dir = self.deps_cpp_info["zlib"].rootpath

        definition_dict = {
            "HDF5_MEMORY_ALLOC_SANITY_CHECK": False,
            
            "HDF5_ENABLE_USING_MEMCHECKER": False,
            "HDF5_ENABLE_Z_LIB_SUPPORT": True,
            "HDF5_ENABLE_THREADSAFE": True,
            "HDF5_ENABLE_PARALLEL": False,
            "HDF5_ENABLE_COVERAGE": False,
            
            "HDF5_USE_18_API_DEFAULT": True,

            "BUILD_STATIC_EXECS": False,
            "BUILD_SHARED_LIBS": self.options.shared,
            "BUILD_TESTING": False,

            "HDF5_BUILD_GENERATORS": False,
            "HDF5_BUILD_EXAMPLES": False,
            "HDF5_BUILD_FORTRAN": False,
            "HDF5_BUILD_CPP_LIB": True,
            "HDF5_BUILD_HL_LIB": True,
            "HDF5_BUILD_TOOLS": False,
            "HDF5_BUILD_JAVA": False,
            
            "ALLOW_UNSUPPORTED": True,

            "HDF5_NO_PACKAGES": True,

            "ZLIB_ROOT": zlib_root_dir,
        }

        self.add_default_definitions(definition_dict)
        return definition_dict

    def package_info(self):
        """Edit package info."""
        super(hdf5, self).package_info()
        self.cpp_info.libs = ["hdf5", "hdf5_cpp", "hdf5_hl", "hdf5_hl_cpp"]
