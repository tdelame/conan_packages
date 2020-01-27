import os
import shutil
import itertools
import subprocess
from conans import python_requires, tools
from conans.tools import os_info

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")


is_linux = os_info.is_linux
is_windows = os_info.is_windows

def extract_linker_flags(conanfile, dependence_name):
    flags = []
    dependences = [dependence_name]
    while dependences:
        this_dependence = dependences.pop()
        flags.extend(conanfile.deps_cpp_info[this_dependence].sharedlinkflags)
        flags.extend(["-l{}".format(name) for name in conanfile.deps_cpp_info[this_dependence].libs])

        for dependence in conanfile.deps_cpp_info[this_dependence].public_deps:
            dependences.append(dependence)

    seen = set()
    seen_add = seen.add
    return " ".join([x for x in flags if not (x in seen or seen_add(x))])

def extract_env_compilers():
    cc = os.getenv("CC", None)
    cxx = os.getenv("CXX", None)

    # uniformize paths on windows
    if is_windows:
        if cc is not None:
            cc = cc.replace("\\", "/")
            os.environ["CC"] = cc

        if cxx is not None:
            cxx = cxx.replace("\\", "/")
            os.environ["CXX"] = cxx

    return cc, cxx

def execute_command(command, output_file_path):
    with open(output_file_path, "w") as outfile:
        process = subprocess.Popen(command, stdout=outfile, stderr=outfile, shell=True)
        process.communicate()
        return process.returncode == 0

XCB_SHM_PATCH_IN = """#if (XCB_SHM_MAJOR_VERSION == 1 && XCB_SHM_MINOR_VERSION >= 2) || XCB_SHM_MAJOR_VERSION > 1
#define XCB_USE_SHM_FD
#endif"""

XCB_SHM_PATCH_OUT = """#undef XCB_USE_SHM_FD"""

# TODO:
# glib
# webengine: nss, dbus
# qt multimedia: gstreamer, pulseaudio
class qt(pyreq.BaseConanFile):
    description = "Cross-platform framework for graphical user interfaces"
    url = "https://www.qt.io"
    license = "LGPL-3.0"
    name = "qt"
    version = "5.14.0"

    settings = "os", "build_type", "compiler"

    options = {"shared": [True, False]}

    default_options = {"shared": True}

    _compiler = None
    _compiler_runtime = None
    _source_subfolder = "source_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        self._compiler = self.settings.compiler
        if self.settings.compiler == "Visual Studio":
            self._compiler_runtime = self.settings.compiler.runtime

        # I do not want to have to recompile Qt because the compiler is different. Binaries are
        # compatibles on any Linux distribution.
        if is_linux:
            del self.settings.compiler

    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("cmake/3.15.4@tdelame/stable")
        self.build_requires("ninja/1.9.0@tdelame/stable")

        # if qtwebengine: need gcc >= 5 and no static build (put it in configure())
        self.build_requires("bison/3.4.2@tdelame/stable")
        self.build_requires("flex/2.6.4@tdelame/stable")

        if is_linux:
            # Qt should use the fontconfig of the host but we need fontconfig right now to compile Qt
            self.build_requires("fontconfig/2.13.92@tdelame/stable")
            # qtwebengine
            self.build_requires("gperf/3.1@tdelame/stable")
            # Not shipped to the client: we want to use the client's libraries, plugins and configurations.
            self.build_requires("libalsa/1.2.1.2@tdelame/stable")

            self.build_requires("libXext/1.3.4@tdelame/stable")
            self.build_requires("libXi/1.7.10@tdelame/stable")
            self.build_requires("libXrender/0.9.10@tdelame/stable")
            self.build_requires("libX11/1.6.8@tdelame/stable")
            self.build_requires("libxcb/1.13.1@tdelame/stable")
            self.build_requires("libxkbcommon/0.9.1@tdelame/stable")

    def requirements(self):
        self.requires("libpng/1.6.37@tdelame/stable")
        self.requires("libjpeg/9c@tdelame/stable")
        self.requires("zlib/1.2.11@tdelame/stable")
        self.requires("OpenSSL/1.1.1d@tdelame/stable")
        self.requires("cpython/3.7.5@tdelame/stable")
        self.requires("freetype/2.9.1@tdelame/stable")
        self.requires("expat/2.2.9@tdelame/stable")
        self.requires("zstd/1.4.4@tdelame/stable")
        self.requires("openal/1.20.0@tdelame/stable")
        if self.settings.os == "Linux":
            self.requires("icu/65.1@tdelame/stable")

    def source(self):
        directory = "qt-everywhere-src-{}".format(self.version)
        url = "https://download.qt.io/archive/qt/5.14/5.14.0/single/qt-everywhere-src-5.14.0.tar.xz"

        # NOTE: cannot extract tar.xz with python2 by tools.get(url)
        # Also, LD_LIBRARY_PATH is modified by conan so we cannot call the system `tar` command 
        # without emptying the environment variable first
        tools.download(url, "{}.tar.xz".format(directory))
        log_file_path = "extract_file.log"
        with tools.environment_append({"LD_LIBRARY_PATH":None}):
            if not execute_command("tar -xJf {}.tar.xz".format(directory), log_file_path):
                with open(log_file_path, "r") as infile:
                    print("failed to extract source archive:\n{}".format(infile.read()))
        os.remove(log_file_path)            
        os.rename(directory, self._source_subfolder)

        if is_linux:
            # if the host has some newer version of XCB available, Qt libraries will have undefined
            # symbols, because they will be configured with the XCB versions of the host instead of
            # the embeeded XCB versions.
            with tools.chdir(os.path.join(self._source_subfolder, "qtbase", "src", "plugins", "platforms", "xcb")):
                tools.replace_in_file(
                    "qxcbbackingstore.cpp",
                    XCB_SHM_PATCH_IN,
                    XCB_SHM_PATCH_OUT)

    def build(self):
        args = [
            "-shared" if self.options.shared else "-static",
            "-confirm-license", "-opensource", "-prefix {}".format(self.package_folder),
            "-silent", "-nomake examples", "-nomake tests",
            "-sse2", "-sse3", "-avx", "-avx2", "-ltcg",
            "--qt3d-simd=avx2",

            # activate the dependences we already built
            "--zlib=system", "\"ZLIB_LIBS={}\"".format(extract_linker_flags(self, "zlib")),
            "--freetype=system", "\"FREETYPE_LIBS={}\"".format(extract_linker_flags(self, "freetype")),
            "--libjpeg=system", "\"LIBJPEG_LIBS={}\"".format(extract_linker_flags(self, "libjpeg")),
            "--libpng=system", "\"LIBPNG_LIBS={}\"".format(extract_linker_flags(self, "libpng")),
            "--zstd=yes", "\"ZSTD_LIBS={}\"".format(extract_linker_flags(self, "zstd")),
            "--alsa=yes", "\"ALSA_LIBS={}\"".format(extract_linker_flags(self, "libalsa")),
            "-openssl-{}".format("runtime" if self.options["OpenSSL"].shared else "linked"), "\"OPENSSL_LIBS={}\"".format(extract_linker_flags(self, "OpenSSL")),
            "-opengl desktop",
            "\"OPENAL_LIBS={}\"".format(extract_linker_flags(self, "openal")),

            # activate dependences that can be build by Qt
            "--harfbuzz=qt", "--pcre=qt", "--assimp=qt", "--tiff=qt", "--webp=qt",
            

            # deactivate dependences we do not want
            "--glib=no", #we do not plan to integrate glib based libraries in Qt
            "--sqlite=no", "--sql-mysql=no", "--sql-psql=no", "--sql-odbc=no", # no database support needed yet
        ]

        if self.settings.build_type == "Debug":
            args.append("-debug")
        elif self.settings.build_type == "Release":
            args.append("-release")
        elif self.settings.build_type == "RelWithDebInfo":
            args.append("-release")
            args.append("-force-debug-info")

        if is_linux:
            args.extend([
                "--fontconfig=yes", "\"FONTCONFIG_LIBS={}\"".format(extract_linker_flags(self, "fontconfig")),
                "--icu=yes", "--webengine-icu=system", "\"ICU_LIBS={}\"".format(extract_linker_flags(self, "icu")),
                "--xkbcommon=yes", "\"XKBCOMMON_LIBS={}\"".format(extract_linker_flags(self, "libxkbcommon")),
                "--xcb=qt", # build the required symbols to not have to install XCB libraries on host machines
                "-linker lld"
            ])
        elif is_windows and self._compiler == "Visual Studio" \
            and (self._compiler_runtime == "MT" or self._compiler_runtime == "MTd"):
            args.append("-static-runtime")

        for package in self.deps_cpp_info.deps:
            args += ["-I " + s for s in self.deps_cpp_info[package].include_paths]
            args += ["-D " + s for s in self.deps_cpp_info[package].defines]
            args += ["-L " + s for s in self.deps_cpp_info[package].lib_paths]

        if is_linux:
            args.append("-platform {}".format("linux-clang" if self._compiler == "clang" else "linux-g++"))
        elif is_windows:
            args.append("-platform {}".format({
                "Visual Studio": "win32-msvc",
                "gcc": "win32-g++",
                "clang": "win32-clang-g++"
            }.get(self._compiler)))

        cc, cxx = extract_env_compilers()
        if cc is None:
            cc = tools.which(self._compiler)

        if cxx is None:
            if self._compiler == "clang":
                cxx = tools.which("clang++")
            elif self._compiler == "gcc":
                cxx = tools.which("g++")
            else:
                cxx = tools.which("cl.exe")

        args += [
            'QMAKE_CC="{}"'.format(cc), 'QMAKE_LINK_C="{}"'.format(cc), 'QMAKE_LINK_C_SHLIB="{}"'.format(cc),
            'QMAKE_CXX="{}"'.format(cxx), 'QMAKE_LINK="{}"'.format(cxx), 'QMAKE_LINK_SHLIB="{}"'.format(cxx)]

        if is_linux and self._compiler == "clang":
            args += ['QMAKE_CXXFLAGS+="-ftemplate-depth=1024"']

        abs_source_subfolder = os.path.abspath(self._source_subfolder)
        with tools.chdir(abs_source_subfolder):

            with tools.vcvars(self.settings):
                build_env = {"PKG_CONFIG_PATH": [abs_source_subfolder]}

                if is_linux:
                    ld_library_paths = []
                    for dependence in self.deps_cpp_info.deps:
                        ld_library_paths.extend(self.deps_cpp_info[dependence].lib_paths)
                        dependence_root_path = self.deps_cpp_info[dependence].rootpath
                        for directory, _, file_names in os.walk(dependence_root_path):
                            for file_name in file_names:
                                if file_name.endswith(".pc"):
                                    shutil.copyfile(os.path.join(directory, file_name), file_name)
                                    tools.replace_prefix_in_pc_file(file_name, dependence_root_path)
                    build_env["LD_LIBRARY_PATH"] = ld_library_paths

                    # make our python package usable by Qt build system
                    cpython_dep_root = self.deps_cpp_info["cpython"].rootpath
                    build_env["PATH"] = [os.path.join(cpython_dep_root, "bin")]
                    build_env["PYTHONHOME"] = cpython_dep_root

                with tools.environment_append(build_env):
                    try:
                        self.run("./configure -recheck-all {}".format(" ".join(args)))
                    finally:
                        pass
                    if self._compiler == "Visual Studio":
                        make = "jom"
                    elif tools.os_info.is_windows:
                        make = "mingw32-make"
                    else:
                        # There is an error in the error message of a module we do not build...
                        # I failed to use conans.tools.replace_in_file for that, so I do it manually.
                        file_path = os.path.join(abs_source_subfolder, "qtwebengine", "src", "src.pro")
                        with open(file_path, "r") as infile:
                            file_content = infile.read()

                        new_content = file_content.replace(
                            """@echo Modules will not be built. $${skipBuildReason}""",
                            """@echo Modules will not be built because we do not want too.""")

                        with open(file_path, "w") as outfile:
                            outfile.write(new_content)

                        make = "make -j{}".format(tools.cpu_count())
                    self.run(make, run_environment=True)
                    self.run("%s install" % make)

    def package(self):
        """Assemble the package."""
        self.copy(pattern="LICENSE.LGPLv3", dst="licenses", src=self._source_subfolder)

  