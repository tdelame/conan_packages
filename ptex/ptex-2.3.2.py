import os
from conans import python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class ptex(pyreq.CMakeConanFile):
    description = "Per-Face Texture Mapping for Production Rendering"
    url = "https://github.com/wdas/ptex"
    license = "Apache 2.0"
    name = "ptex"
    version = "2.3.2"

    settings = "os"

    def requirements(self):
        """Define runtime requirements."""
        self.requires("zlib/1.2.11@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        tools.get("https://github.com/wdas/ptex/archive/v{}.tar.gz".format(self.version))
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def cmake_definitions(self):
        """Setup CMake definitions."""
        definitions = {
            "PTEX_SHA": "1b8bc985a71143317ae9e4969fa08e164da7c2e5",
            "PTEX_VER": self.version,
            "PTEX_BUILD_SHARED_LIBS": self.options.shared,
            "PTEX_BUILD_STATIC_LIBS": not self.options.shared
        }
        self.add_default_definitions(definitions)
        return definitions

    def build(self):
        """Build the elements to package."""
        abs_source_subfolder = os.path.abspath(self._source_subfolder)
        with self.managed_pkg_config_paths(abs_source_subfolder):
            super(ptex, self).build()

    def package_info(self):
        """Edit package info."""
        super(ptex, self).package_info()
        self.cpp_info.libs = ["Ptex"]
