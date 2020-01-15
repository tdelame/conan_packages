import os
from conans import ConanFile, python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class catch2(ConanFile):
    description = "A modern, c++-native, header-only, test framework for utin-tests, TDD and BDD"
    url = "https://github.com/catchorg/Catch2"
    license = "Boost 1.0"
    version = "2.11.1"
    name = "catch2"

    def source(self):
        """Retrieve source code."""
        url = "{}/releases/download/v{}/catch.hpp".format(self.url, self.version)
        tools.download(url, "catch.hpp")
        tools.download("http://www.boost.org/LICENSE_1_0.txt", "LICENSE")

    def package(self):
        """Assemble the package."""
        pyreq.make_directory("licenses")
        pyreq.copy(
            os.path.join(self.build_folder, "catch.hpp"),
            os.path.join(self.package_folder, "include", "catch.hpp"))
        pyreq.copy(
            os.path.join(self.build_folder, "LICENSE"),
            os.path.join(self.package_folder, "licenses", "LICENSE"))
        
    def package_id(self):
        self.info.header_only()

