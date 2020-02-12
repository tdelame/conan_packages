import os
from conans import python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class opensubdiv(pyreq.CMakeConanFile):
    description = "High performance subdivision surface evaluation"
    url = "https://github.com/PixarAnimationStudios/OpenSubdiv"
    license = "Apache 2.0"
    name = "OpenSubdiv"
    version = "3.4.0"
    
    settings = "os"
    
    def requirements(self):
        """Define runtime requirements."""
        self.requires("zlib/1.2.11@tdelame/stable")
        self.requires("TBB/2019-U6@tdelame/stable")
        if self.settings.os == "Linux":
            self.requires("GLEW/2.1.0@tdelame/stable")


    def source(self):
        """Retrieve source code."""
        tools.get("https://github.com/PixarAnimationStudios/OpenSubdiv/archive/v3_4_0.tar.gz")
        os.rename("OpenSubdiv-3_4_0", self._source_subfolder)

        with tools.chdir(self._source_subfolder):
            # https://github.com/PixarAnimationStudios/OpenSubdiv/issues/1064
            tools.replace_in_file(
                "cmake/FindTBB.cmake",
                "tbbmalloc_proxy_debug", "")
            tools.replace_in_file(
                "cmake/FindTBB.cmake",
                "tbbmalloc_proxy", "")

            # do not want to compile stuff for regressions while I said to not compile regressions...
            tools.replace_in_file( 
                "CMakeLists.txt", 
                "if (NOT ANDROID", "if (FALSE")
        
    def cmake_definitions(self):
        """Setup CMake definitions."""
        definition_dict = {
            "BUILD_SHARED_LIBS": self.options.shared,

            "NO_REGRESSION": True,
            "NO_TUTORIALS": True,
            "NO_EXAMPLES": True,
            "NO_GLFW_X11": True,
            "NO_GLTESTS": True,
            "NO_OPENCL": True,
            "NO_TESTS": True,
            "NO_METAL": True,
            "NO_PTEX": True,            
            "NO_CLEW": True,
            "NO_GLFW": True,
            "NO_CUDA": True,
            "NO_OMP": True,
            "NO_DOC": True,
            "NO_DX": True,
            
            "TBB_LOCATION": os.path.join( self.deps_cpp_info[ "TBB" ].include_paths[ 0 ], "../" )
        }

        if self.settings.os == "Linux":
            definition_dict["GLEW_LOCATION"] = self.deps_cpp_info["GLEW"].rootpath
            definition_dict["CMAKE_CXX_FLAGS"] = "-I{}".format(self.deps_cpp_info["GLU" ].include_paths[0])

        self.add_default_definitions(definition_dict)
        return definition_dict 

    def package_info(self):
        """Edit package info."""
        super(opensubdiv, self).package_info()
        self.cpp_info.libs = ["osdCPU", "osdGPU"]
