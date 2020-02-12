from conans import ConanFile, python_requires, tools
import os

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class alembic(pyreq.CMakeConanFile):
    description = "Alembic is an open framework for storing and sharing scene data that includes a C++ library, a file format, and client plugins and applications"
    license = " "
    url = "http://www.alembic.io/"

    name = "alembic"
    version = "1.7.10"

    settings = "os"

    def requirements(self):
        """Define runtime requirements."""
        self.requires("zlib/1.2.11@tdelame/stable")
        self.requires("IlmBase/2.3.0@tdelame/stable")
        self.requires("hdf5/1.8.21@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        directory = "{}-{}".format( self.name, self.version)
        tools.get("https://github.com/alembic/alembic/archive/{}.zip".format(self.version))
        os.rename(directory, self._source_subfolder)

    def cmake_definitions(self):
        """Setup CMake definitions."""
        ilmbase_root_dir = self.deps_cpp_info["IlmBase"].rootpath
        hdf5_root_dir = self.deps_cpp_info["hdf5"].rootpath
        zlib_root_dir = self.deps_cpp_info["zlib"].rootpath

        definition_dict = {
            "USE_HDF5": True,
            "USE_TESTS": False,

            # find our conan HDF5 installation
            "HDF5_ROOT": hdf5_root_dir,

            # find our conan Ilmbase installation
            "ILMBASE_ROOT": ilmbase_root_dir,

            # find our conan zlib installation
            "ZLIB_ROOT": zlib_root_dir,
        }

        self.add_default_definitions(definition_dict)
        return definition_dict

    def package_info(self):
        """Edit package info."""
        super(alembic, self).package_info()
        self.cpp_info.libs = ["Alembic"]
