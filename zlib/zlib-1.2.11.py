import os
from shutil import rmtree
from conans import ConanFile, tools, AutoToolsBuildEnvironment

class ZLib(ConanFile):
    description = "A Massively Spiffy Yet Delicately Unobtrusive Compression Library (Also Free, Not to Mention Unencumbered by Patents)"
    url = "https://zlib.net"
    license = "Zlib"
    name = "zlib"
    version = "1.2.11"

    settings = "os"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    _source_subfolder = "source_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux yet.")

    def source(self):
        """Retrieve source code."""
        url = "https://www.zlib.net/zlib-{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename("zlib-{}".format(self.version), self._source_subfolder)

    def build(self):
        """Build the elements to package"""

        with tools.chdir(self._source_subfolder):
            # seen the following patches at
            # https://github.com/conan-io/conan-center-index/blob/master/recipes/zlib/1.2.11/conanfile.py
            tools.replace_in_file('gzguts.h',
                                  '#if defined(_WIN32) || defined(__CYGWIN__)',
                                  '#if defined(_WIN32) || defined(__MINGW32__)')
            if self.settings.os == "iOS":
                tools.replace_in_file("gzguts.h", '#ifdef _LARGEFILE64_SOURCE',
                                      '#include <unistd.h>\n\n#ifdef _LARGEFILE64_SOURCE')
            for filename in ['zconf.h', 'zconf.h.cmakein', 'zconf.h.in']:
                tools.replace_in_file(filename,
                                      '#ifdef HAVE_UNISTD_H    '
                                      '/* may be set to #if 1 by ./configure */',
                                      '#if defined(HAVE_UNISTD_H) && (1-HAVE_UNISTD_H-1 != 0)')
                tools.replace_in_file(filename,
                                      '#ifdef HAVE_STDARG_H    '
                                      '/* may be set to #if 1 by ./configure */',
                                      '#if defined(HAVE_STDARG_H) && (1-HAVE_STDARG_H-1 != 0)')
            # configure passes CFLAGS to linker, should be LDFLAGS
            tools.replace_in_file("configure", "$LDSHARED $SFLAGS", "$LDSHARED $LDFLAGS")
            # same thing in Makefile.in, when building tests/example executables
            tools.replace_in_file("Makefile.in", "$(CC) $(CFLAGS) -o", "$(CC) $(LDFLAGS) -o")
            # end of patches

            target = "libz.so.{}".format(self.version) if self.options.shared else "libz.a"
            parallel = "-j{}".format(tools.cpu_count())

            autotools = AutoToolsBuildEnvironment(self)
            autotools.fpic = True
            autotools.configure()
            autotools.make(args=[parallel], target=target)
            autotools.install(args=[parallel])

    def package(self):
        "Assemble the package."""

        # very nice snippet found on
        # https://github.com/conan-io/conan-center-index/blob/master/recipes/zlib/1.2.11/conanfile.py
        # to extract the license from the header.
        with tools.chdir(os.path.join(self.source_folder, self._source_subfolder)):
            tmp = tools.load("zlib.h")
            license_contents = tmp[2:tmp.find("*/", 1)]
            tools.save("LICENSE", license_contents)

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

        # purge unneeded directories
        rmtree(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs.append("z")
        if self.settings.os == "Linux" and self.options.shared:
            self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
