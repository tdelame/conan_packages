import os
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class gettext(pyreq.BaseConanFile):
    description = "internationalization and localization system for multilingual programs"
    url = "https://www.gnu.org/software/gettext"
    license = "GPL-3.0"
    settings = "os"

    def requirements(self):
        self.requires("libiconv/1.16@tdelame/stable")
        self.requires("libxml2/2.9.9@tdelame/stable")

    def config_options(self):
        if self.settings.os != "Linux":
            raise RuntimeError("libxml2 is available on Linux only")

    def source(self):
        directory = "{}-{}".format(self.name, self.version)
        url = "https://ftp.gnu.org/pub/gnu/gettext/{}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        arguments = [
            "--disable-c++", "--disable-csharp", "--disable-java",
            "--enable-relocatable"]
        self.build_autotools(arguments)

    def package_info(self):
        ld_library_paths = []
        for dependence in self.deps_cpp_info.deps:
            ld_library_paths.extend(self.deps_cpp_info[dependence].lib_paths)
        ld_library_paths.append(os.path.join(self.package_folder, "lib"))

        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.LD_LIBRARY_PATH.extend(ld_library_paths)
