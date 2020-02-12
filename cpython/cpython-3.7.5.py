import os
from conans import python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class Python(pyreq.BaseConanFile):
    description = "open-source, cross-platform family of tools designed to build, test and package software"
    license = "Python Software Foundation License"
    url = "https://python.org"
    version = "3.7.5"
    name = "cpython"

    settings = "os"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            # Have a look at https://github.com/lasote/conan-cpython/blob/master/conanfile.py for
            # a Windows version
            raise RuntimeError("This recipe is only available for Linux")

    def requirements(self):
        """Define runtime requirements."""
        self.requires("OpenSSL/1.1.1d@tdelame/stable")
        self.requires("expat/2.2.9@tdelame/stable")
        self.requires("lzma/5.2.4@tdelame/stable")
        self.requires("libuuid/1.0.3@tdelame/stable")
        self.requires("bzip2/1.0.8@tdelame/stable")
        self.requires("libffi/3.2.1@tdelame/stable")
        self.requires("zlib/1.2.11@tdelame/stable")
        self.requires("gdbm/1.18.1@tdelame/stable")
        self.requires("sqlite3/3.30.1@tdelame/stable")
        self.requires("ncurses/6.1@tdelame/stable")
        self.requires("readline/8.0@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        url = "https://github.com/python/cpython/archive/v{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename("cpython-{}".format(self.version), self._source_subfolder)
        # I have got too many issues with this test during the PGO:
        pyreq.remove(os.path.join(self._source_subfolder, "Lib", "test", "test_socket.py"))

    def build(self):
        """Build the elements to package."""
        arguments = [
            # optimizations: costly to build, but ~10/20% perf gain at runtime
            "--with-lto", "--enable-optimizations",
            # manage dependences
            "--with-system-expat", "--with-openssl={}".format(self.deps_cpp_info["OpenSSL"].rootpath),
            # manage features
            "--enable-ipv6", "--with-ensurepip",
            "--enable-big-digits=30", # by default on 64bits platform, but I want to be sure
            # manage build
            "--enable-shared" if self.options.shared else "--disable-shared", "--without-pybdebug", "--without-assertions"
        ]

        # setup.py does not try very hard to find libbuid headers, so we have to hack the include
        # flags to make sure setup.py will find this header.
        libuuid = self.deps_cpp_info["libuuid"]
        include_paths = [os.path.join(libuuid.rootpath, "include", "uuid")]

        # cannot use parallel make with --enable-optimizations :-{
        self.build_autotools(arguments, parallel_make=False, include_paths=include_paths)

    def package(self):
        """Assemble the package."""
        super(Python, self).package()

        with tools.chdir(os.path.join(self.package_folder, "bin")):
            # patch binaries shebangs
            python_shebang = "#!/usr/bin/env python3.7\n"
            for name in ["2to3-3.7", "idle3.7", "pydoc3.7", "pyvenv-3.7", "pip3", "pip3.7"]:
                with open(name, "r") as infile:
                    lines = infile.readlines()

                lines[0] = python_shebang

                with open(name, "w") as outfile:
                    outfile.writelines(lines)

            # create an alias for 'python'
            os.symlink("python3.7", "python")

    def package_info(self):
        """Edit package info."""
        super(Python, self).package_info()
        self.cpp_info.includedirs = ["include", "include/python3.7m"]
        self.cpp_info.libs.extend(["python3.7m", "pthread", "dl", "util"])
        # python binaries know the installation directory
        self.env_info.PYTHONHOME = self.package_folder

# Python build finished successfully!
# The necessary bits to build these optional modules were not found:
# _tkinter
# To find the necessary bits, look in setup.py in detect_modules() for the module's name.


# The following modules found by detect_modules() in setup.py, have been
# built by the Makefile instead, as configured by the Setup files:
# _abc                  atexit                pwd
# time
