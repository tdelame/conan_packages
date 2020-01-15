from conans import ConanFile, python_requires, tools
import os

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class embree(pyreq.CMakeConanFile):
    description = "The embree ray tracing library"
    url = "https://github.com/embree/embree"
    license = "Apache 2.0"
    name = "embree"

    version = "3.3.0"
    settings = "os", "build_type"

    def requirements(self):
        """Define runtime requirements."""
        self.requires("TBB/2019-U6@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        directory = "{}-{}".format(self.name, self.version)
        tools.get("https://github.com/embree/embree/archive/v{}.zip".format(self.version))
        os.rename(directory, self._source_subfolder)

    def cmake_definitions(self):
        """Setup CMake definitions."""
        definition_dict = {
            "CMAKE_BUILD_TYPE": self.settings.build_type,
            "BUILD_SHARED_LIBS": self.options.shared,
            "EMBREE_STATIC_LIB": not self.options.shared,
            "EMBREE_TUTORIALS": False,
            "EMBREE_TASKING_SYSTEM": "TBB",
            "EMBREE_MAX_ISA": "AVX512SKX",
            "EMBREE_ISPC_SUPPORT": False,

            "TBB_INCLUDE_DIR"   : self.deps_cpp_info[ "TBB" ].include_paths[ 0 ],
            "TBB_LIBRARY"       : os.path.join( self.deps_cpp_info[ "TBB" ].lib_paths[ 0 ], "libtbb.so" ),
            "TBB_LIBRARY_MALLOC": os.path.join( self.deps_cpp_info[ "TBB" ].lib_paths[ 0 ], "libtbbmalloc.so" )
        }

        self.add_default_definitions(definition_dict)
        return definition_dict

    def package(self):
        """Assemble the package."""
        super(embree, self).package()
        # make sure we get more than what's actually packaged by the cmake build system
        self.copy("*.h", src="embree/include", dst="include", keep_path=True)
        self.copy("*.isph", src="embree/include", dst="include", keep_path=True)
        self.copy("*.h", src="embree/kernels", dst="kernels", keep_path=True)
        self.copy("*.h", src="embree/common", dst="common" , keep_path=True)

        # remove unneeded directories/files
        with tools.chdir(self.package_folder):
            pyreq.remove("bin")
            pyreq.remove("share")

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["embree3"]
        self.cpp_info.includedirs = ["include", "kernels"]
        self.cpp_info.defines.append("TASKING_TBB")
