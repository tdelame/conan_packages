import os
from conans import ConanFile, python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class pybind11(ConanFile):
    description = "Seamless operability between C++11 and Python"
    url = "https://github.com/pybind/pybind11"
    license = "BSD-style"
    version = "2.4.3"
    name = "pybind11"

    _source_subfolder = "source_subfolder"
    
    def source(self):
        """Retrieve source code."""
        url = "{}/archive/v{}.tar.gz".format(self.url, self.version)
        tools.get(url)
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def package(self):
        """Assemble the package."""
        pyreq.make_directory("licenses")
        pyreq.copy(
            os.path.join(self.build_folder, self._source_subfolder, "include"),
            os.path.join(self.package_folder, "include"))
        pyreq.copy(
            os.path.join(self.build_folder, self._source_subfolder, "LICENSE"),
            os.path.join(self.package_folder, "licenses", "LICENSE"))
        
    def package_id(self):
        self.info.header_only()
