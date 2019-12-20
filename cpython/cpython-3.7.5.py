import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

class Python(ConanFile):
    description = "open-source, cross-platform family of tools designed to build, test and package software"
    license = "Python Software Foundation License"
    url = "https://python.org"
    version = "3.7.5"
    name = "python"

    settings = "os"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    _source_subfolder = "source_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            # Have a look at https://github.com/lasote/conan-cpython/blob/master/conanfile.py for
            # a Windows version
            raise RuntimeError("This recipe is only available for Linux")

    def source(self):
        """Retrieve source code."""
        url = "https://github.com/python/cpython/archive/v{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename("cpython-{}".format(self.version), self._source_subfolder)

    def build(self):
        """Build the elements to package."""
        parallel = "-j{}".format(tools.cpu_count())

        with tools.chdir(self._source_subfolder):
            autotools = AutoToolsBuildEnvironment(self)
            autotools.link_flags.append("-fuse-ld=lld")
            autotools.fpic = True
            autotools.configure(
                args=[
                    # "--with-lto", "--enable-optimizations", # costly to build, ~10/20% perf gain at runtime
                    "--with-ipv6",
                    "--enable-big-digits=30", # by default on 64bits platform, but I want to be sure
                    "--enable-shared" if self.options.shared else "--disable-shared"
                ])
            autotools.make(args=[parallel])
            autotools.install(args=[parallel])

    def package(self):
        """Assemble the package."""
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder, ignore_case=True, keep_path=True)

    def package_info(self):
        """Edit package info."""
        self.cpp_info.includedirs = [ "include", "include/python3.7" ]
        self.cpp_info.libs.extend(["python3.7", "pthread", "dl", "util"])
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.PYTHONHOME = self.package_folder
        # not sure about that:
        # self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))

