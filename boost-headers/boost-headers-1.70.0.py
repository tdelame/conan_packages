from conans import ConanFile, tools
import shutil
import os

class boost_headers(ConanFile):
    description = "Header only boost libraries"
    license = "Boost Software License - Version 1.0. http://www.boost.org/LICENSE_1_0.txt"
    url = "https://www.boost.org/"
    version = "1.70.0"
    name = "boost-headers"

    _source_subfolder = "source_subfolder"

    def source(self):
        """Retrieve source code."""
        url = "https://dl.bintray.com/boostorg/release/1.70.0/source/boost_1_70_0.tar.gz"
        tools.get(url)
        os.rename("boost_1_70_0", self._source_subfolder)

    def package(self):
        """Assemble the package."""
        shutil.copytree(
            os.path.join(self.source_folder, self._source_subfolder, "boost"),
            os.path.join(self.package_folder, "include", "boost"))

    def package_id(self):
        """Edit package ID."""
        self.info.header_only()
    