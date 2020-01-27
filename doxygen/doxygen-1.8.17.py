import os
from conans import ConanFile, python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class doxygen(pyreq.BaseConanFile):
    description = "de facto standard tool for generating documentation from annotated C++ sources"
    url = "http://www.doxygen.nl/"
    license = "GPL-2.0-only"
    
    name = "doxygen"
    version = "1.8.17"    

    settings = "os"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is not yet available for your OS")    

    def source(self):
        """Retrieve source code."""
        directory = "{}-{}".format(self.name, self.version)
        url = "{}/files/{}.linux.bin.tar.gz".format(self.url, directory)
        tools.download(url, "{}.tar".format(directory)) # there is a mistake on the file name, it is not gzip compressed
        self.run("tar xf {}.tar".format(directory))
        os.rename(directory, self._source_subfolder)
    
    def package(self):
        """Assemble the package."""
        pyreq.copy(
            os.path.join(self.build_folder, self._source_subfolder, "bin"),
            os.path.join(self.package_folder, "bin"))
        pyreq.copy(
            os.path.join(self.build_folder, self._source_subfolder, "LICENSE"),
            os.path.join(self.package_folder, "licenses", "LICENSE"))

