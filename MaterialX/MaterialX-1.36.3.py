import os
from conans import python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class materialx(pyreq.CMakeConanFile):
    description = "Open standard for transfer of rich material and lookd-development content between applications and renderer"
    url = "https://www.materialx.org"
    license = ""
    name = "MaterialX"
    version = "1.36.3"

    settings = "os"

    def configure(self):
        self.options.shared = False

    def requirements(self):
        """Define runtime requirements."""
        self.requires("libXext/1.3.4@tdelame/stable")
        self.requires("libXt/1.2.0@tdelame/stable")
        self.requires("GLU/9.0.0@tdelame/stable")
        self.requires("libX11/1.6.8@tdelame/stable")
        self.requires("libSM/1.2.3@tdelame/stable")
        self.requires("libICE/1.0.10@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        tools.get("https://github.com/materialx/MaterialX/archive/v{}.tar.gz".format(self.version))
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def cmake_definitions(self):
        """Setup CMake definitions."""
        definitions = {
            "MATERIALX_BUILD_PYTHON": False,
            "MATERIALX_BUILD_VIEWER": False,
            "MATERIALX_BUILD_DOCS": False,
            "PTEX_SHA": "1b8bc985a71143317ae9e4969fa08e164da7c2e5",
            "PTEX_VER": self.version,
            "PTEX_BUILD_SHARED_LIBS": self.options.shared,
            "PTEX_BUILD_STATIC_LIBS": not self.options.shared
        }

        if self.settings.os == "Linux":
            # rely on macros defined in the patched FindX11.cmake to find conan packages
            definitions["CONAN_X11_INC_SEARCH_PATH"] = "{};{};{}".format(
                ";".join(self.deps_cpp_info["libXext"].include_paths),
                ";".join(self.deps_cpp_info["libXt"].include_paths),
                ";".join(self.deps_cpp_info["libX11"].include_paths))

            definitions["CONAN_X11_LIB_SEARCH_PATH"] = "{};{};{}".format(
                ";".join(self.deps_cpp_info["libXext"].lib_paths),
                ";".join(self.deps_cpp_info["libXt"].lib_paths),
                ";".join(self.deps_cpp_info["libX11"].lib_paths))

            includes = []
            for dep in ["libXt", "GLU", "libSM", "libICE"]:
                includes += ["-I " + i for i in self.deps_cpp_info[dep].include_paths]
            definitions["CMAKE_CXX_FLAGS"] = " ".join(includes)

        self.add_default_definitions(definitions)
        return definitions

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = [
            "MaterialXCore", "MaterialXFormat",
            "MaterialXGenGlsl", "MaterialXGenOsl", "MaterialXGenShader",
            "MaterialXRender", "MaterialXRenderOsl", "MaterialXRenderHw", "MaterialXRenderGlsl"]
