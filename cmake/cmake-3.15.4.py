import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class CMake(ConanFile):
    description = "open-source, cross-platform family of tools designed to build, test and package software"
    license = "BSD-3-Clause-Clear"
    url = "https://cmake.org/"
    version = "3.15.4"
    settings = "os"
    name = "cmake"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def source(self):
        """Retrieve source code."""
        folder_name = "cmake-{}".format(self.version)
        targz_file_name = "{}.tar.gz".format(folder_name)
        url = "https://github.com/Kitware/CMake/releases/download/v{}/{}".format(self.version, targz_file_name)

        tools.download(url, targz_file_name)
        tools.untargz(targz_file_name, self.name)
        os.remove(targz_file_name)

    def build(self):
        """Build the elements to package."""
        autotools = AutoToolsBuildEnvironment(self)
        autotools.fpic = True
        autotools.link_flags.append("-fuse-ld=lld")
        autotools.configure(
            configure_dir="cmake/cmake-3.15.4",
            args=[
                "--parallel={}".format(tools.cpu_count()),
                "--no-system-libs",
                "--prefix={}/to_copy".format(self.build_folder)])
        autotools.make(args=["-j{}".format(tools.cpu_count())])
        autotools.install(args=["-j{}".format(tools.cpu_count())])

    def package(self):
        """Assemble the package."""
        self.copy("*", src="to_copy", dst="", keep_path=True)

    def package_info(self):
        """Edit package info."""
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.CMAKE_ROOT = self.package_folder
        self.env_info.CMAKE_MODULE_PATH = os.path.join(self.package_folder, "share", "cmake-3.15", "Modules")
