from conans import ConanFile, tools
import shutil
import os

class boost_headers(ConanFile):
    description = "Boost filesystem library"
    license = "Boost Software License - Version 1.0. http://www.boost.org/LICENSE_1_0.txt"
    url = "https://www.boost.org/"
    version = "1.70.0"
    name = "boost-filesystem"

    settings = "os", "build_type"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    _source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires("boost-headers/1.70.0@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        url = "https://dl.bintray.com/boostorg/release/1.70.0/source/boost_1_70_0.tar.gz"
        tools.get(url)
        os.rename("boost_1_70_0", self._source_subfolder)

    def build(self):
        """Build the elements to package."""

        configure_command = "{bootstrap} --with-libraries={libraries_list}".format(
            bootstrap="bootstrap" if os.name == "nt" else "./bootstrap.sh",
            libraries_list="filesystem")
        
        build_command = "{b2} stage --stagedir={stage} threading=multi link={link} variant={variant}".format(
            b2="b2.exe" if os.name == "nt" else "./b2",
            stage=self.package_folder,
            link="shared" if self.options.shared else "static",
            variant="release" if self.settings.build_type == "Release" else "debug")

        with tools.chdir(os.path.join(self._source_subfolder)):
            self.run(configure_command)
            self.run(build_command)

    def package(self):
        """Assemble the package."""
        self.copy("LICENSE_1_0.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["boost_filesystem"]
        self.cpp_info.system_libs = ["m", "pthread"]
    