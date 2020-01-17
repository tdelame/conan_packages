from distutils.spawn import find_executable
import os
from conans import ConanFile, CMake, tools

class GLEW(ConanFile):
    description = "OpenGL Extension Wrangler Library"
    url = "https://glew.sourceforge.net/"
    version = "2.1.0"
    name = "GLEW"
    license = "MIT"

    settings = "os", "build_type"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("Your OS has not been tested for this recipe. Please, extend the recipe.")

    def requirements(self):
        """Define runtime requirements."""
        self.requires("GLU/9.0.0@tdelame/stable")

    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("cmake/3.15.4@tdelame/stable")
        self.build_requires("ninja/1.9.0@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        url = "https://github.com/nigels-com/glew/releases/download/glew-{0}/glew-{0}.tgz".format(
            self.version)
        tools.get(url)
        os.rename("glew-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        definition_dict = {
            "BUILD_UTILS": False,
            "GLEW_REGAL": False,
            "GLEW_OSMESA": False,
        }

        if self.settings.os == "Linux" and find_executable("lld") is not None:
            definition_dict["CMAKE_SHARER_LINKER_FLAGS"] = "-fuse-ld=lld"
            definition_dict["CMAKE_EXE_LINKER_FLAGS"] = "-fuse-ld=lld"

        cmake = CMake(self, generator="Ninja")
        cmake.configure(
            source_folder="{}/build/cmake".format(self._source_subfolder),
            build_folder=self._build_subfolder)
        return cmake

    def build(self):
        """Build the elements to package."""
        cmake = self._configure_cmake()
        cmake.build()
        cmake.install()

    def package(self):
        """Assemble the package."""
        self.copy("include/*", ".", "%s" % self._source_subfolder, keep_path=True)
        self.copy("%s/license*" % self._source_subfolder, dst="licenses",  ignore_case=True, keep_path=False)
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

        if self.options.shared:
            self.copy(pattern="*.so", dst="lib", keep_path=False)
            self.copy(pattern="*.so.*", dst="lib", keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['GLEW']
        self.cpp_info.libs.append("GL")
        if self.settings.build_type == "Debug":
            self.cpp_info.libs[0] += "d"
