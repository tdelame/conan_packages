from conans import python_requires, tools, CMake
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")


class GLEW(pyreq.CMakeConanFile):
    description = "OpenGL Extension Wrangler Library"
    url = "https://glew.sourceforge.net/"
    version = "2.1.0"
    name = "GLEW"
    license = "MIT"

    settings = "os", "build_type"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("Your OS has not been tested for this recipe. Please, extend the recipe.")

    def requirements(self):
        """Define runtime requirements."""
        self.requires("GLU/9.0.0@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        self.download(
            "https://github.com/nigels-com/glew/releases/download/glew-{0}".format(self.version),
            directory="glew-{}".format(self.version), compression="tgz")

    def cmake_definitions(self):
        definition_dict = {
            "BUILD_UTILS": False,
            "GLEW_REGAL": False,
            "GLEW_OSMESA": False,
        }
        self.add_default_definitions(definition_dict)
        return definition_dict

    def configure_cmake(self):
        """Configure and return a CMake build helper."""
        cmake = CMake(self, generator="Ninja")
        cmake.configure(
            defs=self.cmake_definitions(),
            source_folder="{}/build/cmake".format(self._source_subfolder),
            build_folder=self._build_subfolder)
        return cmake

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
        super(GLEW, self).package_info()
        self.cpp_info.libs = ['GLEW']
        self.cpp_info.libs.append("GL")
        if self.settings.build_type == "Debug":
            self.cpp_info.libs[0] += "d"
