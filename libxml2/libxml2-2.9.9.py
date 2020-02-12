import os
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class libxml2(pyreq.BaseConanFile):
    description = "library for parsing XML documents"
    url = "https://xmlsoft.org"
    license = "MIT"
    settings = "os"

    def requirements(self):
        self.requires("zlib/1.2.11@tdelame/stable")
        self.requires("libiconv/1.16@tdelame/stable")
        self.requires("icu/65.1@tdelame/stable")

    def config_options(self):
        if self.settings.os != "Linux":
            raise RuntimeError("libxml2 is available on Linux only")

    def source(self):
        directory = "{}-{}".format(self.name, self.version)
        url = "http://xmlsoft.org/sources/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        arguments = [
            "--with-python=no", "--without-lzma",
            "--with-zlib", "--with-iconv", "--with-icu" ]
        self.build_autotools(arguments)

    def package_info(self):
        super(libxml2, self).package_info()
        self.cpp_info.libs = ["xml2"]
        self.cpp_info.system_libs = ["m"]
        if not self.options.shared:
            self.cpp_info.defines = ["LIBXML_STATIC"]
