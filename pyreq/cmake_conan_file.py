from distutils.spawn import find_executable
from base_conan_file import BaseConanFile
from conans import CMake

class CMakeConanFile(BaseConanFile):
    
    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("cmake/3.15.4@tdelame/stable")
        self.build_requires("ninja/1.9.0@tdelame/stable")

    def add_default_definitions(self, defs):
        if self.settings.os == "Linux":
            if find_executable( "lld" ) is not None:
                defs[ "CMAKE_SHARED_LINKER_FLAGS" ] = "-fuse-ld=lld"
                defs[ "CMAKE_EXE_LINKER_FLAGS"    ] = "-fuse-ld=lld"

            if self.settings.get_safe("build_type") is None:
                defs["CMAKE_BUILD_TYPE"] = "Release"
                defs["CMAKE_CXX_FLAGS"] = "{} -m64 -fPIC -O3".format(defs.get("CMAKE_CXX_FLAGS", ""))

            defs["CMAKE_POSITION_INDEPENDENT_CODE"] = True

    def cmake_definitions(self):
        """Return a definition dict to be used by configure_cmake()."""
        raise RuntimeError("You have to override 'cmake_definition()' in your derived class")

    def configure_cmake(self):
        """Configure and return a CMake build helper."""
        cmake = CMake(self, generator="Ninja")
        cmake.configure(
            defs=self.cmake_definitions(),
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder)
        return cmake

    def build(self):
        """Build the elements to package."""
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        """Assemble the package."""
        cmake = self.configure_cmake()
        cmake.install()
        super(CMakeConanFile, self).package()