from conans import ConanFile, tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")
import os

class Spdlog(ConanFile):
    
    description = "Very fast, header only, C++ logging library. Customized for Rumba"
    url = "https://github.com/gabime/spdlog"
    license = "MIT"
    name = "spdlog-rumba"
    version = "1.5.0"   

    exports_sources = ["tweakme.h"]
    _source_subfolder = "source_subfolder"

    def source(self):
        """Retrieve source code."""
        url = "https://github.com/gabime/spdlog/archive/v{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename("spdlog-{}".format(self.version), self._source_subfolder)

    def package(self):
        """Assemble the package."""
        pyreq.copy(
            os.path.join(self.source_folder, self._source_subfolder, "include", "spdlog"),
            os.path.join(self.package_folder, "include", "spdlog"))
        self.copy("tweakme.h", dst="include/spdlog")

    def package_id(self):
        self.info.header_only()

