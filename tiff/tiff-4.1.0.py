from conans import python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class tiff(pyreq.BaseConanFile):
    description = "TIFF Library and Utilities"
    license = "BSD-like"
    url = "http://www.libtiff.org/"
    name = "tiff"
    version = "4.1.0"

    settings = "os"

    def requirements(self):
        """Define runtime requirements."""
        self.requires("zlib/1.2.11@tdelame/stable")
        self.requires("zstd/1.4.4@tdelame/stable")
        self.requires("lzma/5.2.4@tdelame/stable")
        self.requires("libjpeg/9c@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        self.download("http://download.osgeo.org/libtiff")
    
    def build(self):
        """Build the elements to package."""
        "zlib, jpeg, lzma, zstd "
        self.build_autotools()

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["tiff", "tiffxx"]
