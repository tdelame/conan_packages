import shutil
import stat
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

def __on_shutil_rmtree_error(func, path, exc_info):
    #pylint: disable=unused-argument
    os.chmod(path, stat.S_IWRITE)
    os.remove(path)


def remove_directory(directory_path):
    """Remove a directory, if it exists, as well as all of its content.
    """
    shutil.rmtree(directory_path, onerror=__on_shutil_rmtree_error)

class OpenSSL(ConanFile):
    description = "robust, commercial-grade, and full-featured toolkit for the TLS and SSL protocols"
    license = "Apache 2.0"
    url = "https://openssl.org"
    version = "1.1.1d"
    settings = "os"
    name = "OpenSSL"

    options = {"shared": [True, False]}
    default_options = {"shared": True}

    _source_subfolder = "source_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def source(self):
        """Retrieve source code."""
        folder_name = "OpenSSL_1_1_1d"
        url = "https://github.com/openssl/openssl/archive/{}.tar.gz".format(folder_name)
        tools.get(url)
        os.rename("openssl-{}".format(folder_name), self._source_subfolder)

    def requirements(self):
        """Define runtime requirements."""
        self.requires("zlib/1.2.11@tdelame/stable")

    def _get_configuration_string(self):
        autotools = AutoToolsBuildEnvironment(self)
        autotools.fpic = True

        cflags = " ".join(autotools.flags)
        cxxflags = cflags + " " + " ".join(autotools.cxx_flags)

        ar = ""
        cc = ""
        cxx = ""
        lflags = " ".join(autotools.link_flags)
        ranlib = ""
        defines = " ".join(autotools.defines)
        includes = ", ".join(['"{}"'.format(include) for include in autotools.include_paths])

        if "AR" in os.environ:
            ar = "ar => \"{}\",".format(os.environ["AR"])
        if "CC" in os.environ:
            cc = "cc => \"{}\",".format(os.environ["CC"])
        if "CXX" in os.environ:
            cxx = "cxx => \"{}\",".format(os.environ["CXX"])
        if "RANLING" in os.environ:
            cxx = "ranlib => \"{}\",".format(os.environ["RANLIB"])
        if defines:
            defines = "defines => add(\"{}\"),".format(defines)

        return """my %targets = (
    "my_custom_target" => {{
        inherit_from => [ "linux-x86_64" ],
        cflags => add("{cflags}"),
        cxxflags => add("{cxxflags}"),
        {defines}
        includes => add({includes}),
        lflags => add("{lflags}"),
        {CC}
        {CXX}
        {AR}
        {RANLIB}
    }},
);
""".format(
    cflags=cflags, cxxflags=cxxflags, defines=defines, includes=includes, lflags=lflags, AR=ar,
    CC=cc, CXX=cxx, RANLIB=ranlib)

    def _get_configure_args(self):
        # openssldir = self.options.openssldir if self.options.openssldir else os.path.join(self.package_folder, "res")
        # args = ["--openssldir=%s" % openssldir]
        zlib_deps = self.deps_cpp_info["zlib"]
        return [
            '"my_custom_target"', "no-tests", "PERL=perl", "-fPIC", "no-unit-test", "--release",
            "--prefix={}".format(self.package_folder),
            "shared" if self.options.shared else "no-shared",
            "--with-zlib-include=\"{}\"".format(zlib_deps.include_paths[0]),
            "--with-zlib-lib=\"{}\"".format(zlib_deps.lib_paths[0])
        ]

    def build(self):
        """Build the elements to package."""
        # I had a lot of issues to build this package with different compilers on different
        # machines, so I looked at
        # https://github.com/conan-io/conan-center-index/blob/master/recipes/openssl what the clever
        # people from conan have done to support a wider range of options/settings than I need.
        # However it dit not solved my crash when compiling with clang on the docker image. So I let
        # my modifications here for more tuning in the future.
        tools.save(
            os.path.join(self._source_subfolder, "Configurations", "20-conan.conf"),
            self._get_configuration_string())

        with tools.chdir(self._source_subfolder):
            # workaround for MinGW (https://github.com/openssl/openssl/issues/7653)
            if not os.path.isdir(os.path.join(self.package_folder, "bin")):
                os.makedirs(os.path.join(self.package_folder, "bin"))

            self.run("perl ./Configure {}".format(" ".join(self._get_configure_args())))
            make_program = tools.get_env("CONAN_MAKE_PROGRAM", tools.which("make"))
            parallel = "-j{}".format(tools.cpu_count())
            self.run("{} {}".format(make_program, parallel))
            self.run("{} install_sw".format(make_program))

    def package(self):
        """Assemble the package."""
        self.copy(src=self._source_subfolder, pattern="*LICENSE", dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        """Edit package info."""
        self.cpp_info.name = "OpenSSL"
        self.cpp_info.libs = ["ssl", "crypto"]
        if self.settings.os == "Windows":
            self.cpp_info.libs.extend(["crypt32", "msi", "ws2_32", "advapi32", "user32", "gdi32"])
        elif self.settings.os == "Linux":
            self.cpp_info.libs.extend(["dl", "pthread"])
