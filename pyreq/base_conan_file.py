from distutils.spawn import find_executable
from glob import glob
import shutil
import os

from conans import ConanFile, tools, AutoToolsBuildEnvironment, Meson
from utils import remove

class BaseConanFile(ConanFile):

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    options = {"shared": [True, False]}
    default_options = {"shared": True}

    def download(self, urlbase, directory=None, compression=None):
        if compression is None:
            compression = "tar.gz"
        if directory is None:
            directory = "{}-{}".format(self.name, self.version)
        url = "{}/{}.{}".format(urlbase, directory, compression)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def clean_package(self):
        """Remove unneeded files from the package directory."""
        lib_directory = os.path.join(self.package_folder, "lib")
        if tools.os_info.is_linux:
            if os.path.exists(lib_directory) and os.path.isdir(lib_directory):
                with tools.chdir(os.path.join(self.package_folder, "lib")):
                    for filename in glob("*.la"):
                        remove(filename)

                    patterns = ["*.a"] if self.options.shared else ["*.dylib", "*.so", "*.so.*"]
                    for pattern in patterns:
                        for filename in glob(pattern):
                            remove(filename)

            remove(os.path.join(self.package_folder, "share", "doc"))
            remove(os.path.join(self.package_folder, "share", "man"))
            remove(os.path.join(self.package_folder, "share", "gtk-doc"))

    def build_meson(self, arguments=None, definitions=None, directory=None):

        if directory is None:
            directory = self._source_subfolder
        abs_source_subfolder = os.path.abspath(directory)

        # use release build type if "build_type" not in recipe's settings
        build_type = self.settings.get_safe("build_type")
        if build_type is None:
            build_type = "Release"

        with tools.chdir(abs_source_subfolder):
            # configure script may rely on pkg-config files of dependence to correctly set compiler
            # and linker flags for us. We copy every pkg-config files of dependences to the source
            # folder and ask pkg-config to look into that folder for information.
            for dependence in self.deps_cpp_info.deps:
                dependence_root_path = self.deps_cpp_info[dependence].rootpath
                for directory, _, file_names in os.walk(dependence_root_path):
                    for file_name in file_names:
                        if file_name.endswith(".pc"):
                            shutil.copyfile(os.path.join(directory, file_name), file_name)
                            tools.replace_prefix_in_pc_file(file_name, dependence_root_path)      


            meson = Meson(self, backend="ninja", build_type=build_type)
            meson.configure(
                args=arguments, defs=definitions,
                source_folder=abs_source_subfolder, build_folder=self._build_subfolder,
                pkg_config_paths=abs_source_subfolder)
            meson.build()
            meson.install()

    def build_autotools(self, arguments=None, directory=None, parallel_make=True, parallel_install=True, include_paths=None):
        if not tools.os_info.is_linux:
            raise RuntimeError("build_autotools is meant to be called on Linux only")

        if arguments is None:
            arguments = []
        if self.options.shared:
            arguments.extend(["--enable-shared", "--disable-static"])
        else:
            arguments.extend(["--enable-static", "--disable-shared"])

        parallel = "-j{}".format(tools.cpu_count())

        if directory is None:
            directory = self._source_subfolder

        abs_source_subfolder = os.path.abspath(directory)

        with tools.chdir(abs_source_subfolder):
            # configure script may run compiled programs to test if everything is working. Such
            # programs may fail because the library loader does not find the dependence libraries.
            # We help the loaded by putting any library path of dependences into LD_LIBRARY_PATH.
            #
            # configure script may rely on pkg-config files of dependence to correctly set compiler
            # and linker flags for us. We copy every pkg-config files of dependences to the source
            # folder and ask pkg-config to look into that folder for information.
            ld_library_paths = []
            for dependence in self.deps_cpp_info.deps:
                ld_library_paths.extend(self.deps_cpp_info[dependence].lib_paths)
                dependence_root_path = self.deps_cpp_info[dependence].rootpath
                for directory, _, file_names in os.walk(dependence_root_path):
                    for file_name in file_names:
                        if file_name.endswith(".pc"):
                            shutil.copyfile(os.path.join(directory, file_name), file_name)
                            tools.replace_prefix_in_pc_file(file_name, dependence_root_path)

            with tools.environment_append({"LD_LIBRARY_PATH": ld_library_paths, "PKG_CONFIG_PATH": abs_source_subfolder}):
                autotools = AutoToolsBuildEnvironment(self)
                autotools.fpic = True
                autotools.cxx_flags.append("-O3")
                autotools.flags.append("-O3")
                if find_executable("lld") is not None:
                    autotools.link_flags.append("-fuse-ld=lld")

                if include_paths is not None:
                    autotools.include_paths += include_paths

                autotools.configure(args=arguments)
                autotools.make(args=[parallel] if parallel_make else None)
                autotools.install(args=[parallel] if parallel_install else None)

    def package_licenses(self):
        """Include any license into the package."""
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)

    def package(self):
        """Assemble the package."""
        self.package_licenses()
        self.clean_package()
