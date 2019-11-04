import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class Flex(ConanFile):
    description = "Fast Lexical Analyzer Generator"
    license = "BSD like"
    url = "https://www.gnu.org/software/flex/"
    version = "2.6.4"
    settings = "os"
    name = "flex"

    _source_subfolder = "source_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("bison/3.4.2@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        url = "https://github.com/westes/flex/files/981163/flex-2.6.4.tar.gz"
        tools.get(url)
        os.rename("flex-{}".format(self.version), self._source_subfolder)
    
    def build(self):
        """Build the elements to package."""
        with tools.chdir(self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.fpic = True
            autotools.configure()
            autotools.make(args=["-j{}".format(tools.cpu_count())])
            autotools.install(args=["-j{}".format(tools.cpu_count())])
    
    def package(self):
        """Assemble the package."""
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder, ignore_case=True, keep_path=True)
    
    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
