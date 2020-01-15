import os
from conans import ConanFile, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class fontstash(ConanFile):
    description = "light-weight online font texture atlas builder written in C"
    url = "https://github.com/memononen/fontstash"
    license = "zlib"
    version = "1.0.1"
    name = "fontstash"
    
    def source(self):
        """Retrieve source code."""
        self.run("git clone {url} {destination}".format(
            url=self.url,
            destination=self.source_folder))

    def package(self):
        """Assemble the package."""
        pyreq.make_directory("licenses")
        pyreq.copy(
            os.path.join(self.build_folder, "src"),
            os.path.join(self.package_folder, "include"))
        pyreq.copy(
            os.path.join(self.build_folder, "LICENSE.txt"),
            os.path.join(self.package_folder, "licenses", "LICENSE"))
        
    def package_id(self):
        self.info.header_only()