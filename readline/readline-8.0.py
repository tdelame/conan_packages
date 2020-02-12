from distutils.spawn import find_executable
from conans import python_requires, tools, AutoToolsBuildEnvironment
import os
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class readline(pyreq.BaseConanFile):
    description = "GNU readline library"
    homepage = "https://tiswww.case.edu/php/chet/readline/rltop.html"
    license = "GPL"
    name = "readline"
    version = "8.0"

    settings = "os"

    def source(self):
        """Retrieve source code."""
        self.download("https://ftp.gnu.org/gnu/readline")
        with pyreq.change_current_directory(self._source_subfolder):
            tools.replace_in_file("Makefile.in", "@TERMCAP_LIB@", "-ltermcap")

    def requirements(self):
        """Define runtime requirements."""
        self.requires("termcap/1.3.1@tdelame/stable")

    def build(self):
        """Build the elements to package."""
        arguments = ["--with-ncurses"]
        if self.options.shared:
            arguments.extend(["--enable-shared", "--disable-static"])
        else:
            arguments.extend(["--enable-static", "--disable-shared"])

        parallel = "-j{}".format(tools.cpu_count())

        abs_source_subfolder = os.path.abspath(self._source_subfolder)
        with self.managed_load_library_paths():
            with self.managed_pkg_config_paths(abs_source_subfolder):
                with tools.chdir(abs_source_subfolder):
                    autotools = AutoToolsBuildEnvironment(self)
                    autotools.fpic = True
                    autotools.cxx_flags.append("-O3")
                    autotools.flags.append("-O3")
                    if find_executable("lld") is not None:
                        autotools.link_flags.append("-fuse-ld=lld")

                    autotools.configure(args=arguments)
                    tools.replace_in_file(
                        os.path.join("shlib", "Makefile"),
                        "-o $@ $(SHARED_OBJ) $(SHLIB_LIBS)",
                        "-o $@ $(SHARED_OBJ) $(SHLIB_LIBS) -ltermcap")
                    autotools.make(args=[parallel])
                    autotools.install(args=[parallel])

    def package_info(self):
        """Edit package info."""
        super(readline, self).package_info()
        self.cpp_info.libs = ["history", "readline"]
