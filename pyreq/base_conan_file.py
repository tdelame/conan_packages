from distutils.spawn import find_executable
from glob import glob
import shutil
import os

from conans import ConanFile, tools, AutoToolsBuildEnvironment, Meson
from utils import remove, executable_in_directory, library_in_directory

class BaseConanFile(ConanFile):

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    options = {"shared": [True, False]}
    default_options = {"shared": True}

    add_bin_to_path = True
    add_lib_to_ld_path = True

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
            remove(os.path.join(self.package_folder, "share", "info"))
            remove(os.path.join(self.package_folder, "share", "man"))
            remove(os.path.join(self.package_folder, "share", "locale"))
            remove(os.path.join(self.package_folder, "share", "gtk-doc"))
            remove(os.path.join(self.package_folder, "share", "cmake"))
            remove(os.path.join(self.package_folder, "lib", "cmake"))

    def managed_load_library_paths(self):
        """Configure scripts or build scripts may rely on some libraries being available in the
        current LD_LIBRARY_PATH while we cannot specify additional paths to those scripts. This
        method returns a context that set LD_LIBRARY_PATH to contain all library paths of all 
        dependences."""
        ld_library_paths = []
        for dependence in self.deps_cpp_info.deps:
            ld_library_paths.extend(self.deps_cpp_info[dependence].lib_paths)
        return tools.environment_append({"LD_LIBRARY_PATH": ld_library_paths})

    def managed_pkg_config_paths(self, path):
        """Configure scripts may rely on pkg-config files of dependence to correctly set compiler
        and linker flags for us. We cannot always specify additional paths to those scripts. This
        method returns a context that set PKG_CONFIG_PATH to a path where we copied all pkg-config
        files of all dependences.
        :param path: str, path to the directory to use to store pkg-config files."""
        for dependence in self.deps_cpp_info.deps:
            dependence_root_path = self.deps_cpp_info[dependence].rootpath
            for directory, _, file_names in os.walk(dependence_root_path):
                for file_name in file_names:
                    if file_name.endswith(".pc"):
                        destination_file_path = os.path.join(path, file_name)
                        shutil.copyfile(os.path.join(directory, file_name), destination_file_path)
                        tools.replace_prefix_in_pc_file(destination_file_path, dependence_root_path)
        return tools.environment_append({"PKG_CONFIG_PATH": path})

    def build_meson(self, arguments=None, definitions=None, directory=None):

        if directory is None:
            directory = self._source_subfolder
        abs_source_subfolder = os.path.abspath(directory)

        # use release build type if "build_type" not in recipe's settings
        build_type = self.settings.get_safe("build_type")
        if build_type is None:
            build_type = "Release"

        with self.managed_pkg_config_paths(abs_source_subfolder):
            with tools.chdir(abs_source_subfolder):
                meson = Meson(self, backend="ninja", build_type=build_type)
                meson.configure(
                    args=arguments, defs=definitions,
                    source_folder=abs_source_subfolder, build_folder=self._build_subfolder,
                    pkg_config_paths=abs_source_subfolder)
                meson.build()
                meson.install()

    def build_autotools(
            self, arguments=None, directory=None,
            make_arguments=None, parallel_make=True,
            install_arguments=None, parallel_install=True,
            include_paths=None):
        if not tools.os_info.is_linux:
            raise RuntimeError("build_autotools is meant to be called on Linux only")

        if directory is None:
            directory = self._source_subfolder

        if arguments is None:
            arguments = []
        if self.options.shared:
            arguments.extend(["--enable-shared", "--disable-static"])
        else:
            arguments.extend(["--enable-static", "--disable-shared"])

        parallel = "-j{}".format(tools.cpu_count())
        if make_arguments is None:
            make_arguments = []
        if parallel_make:
            make_arguments.append(parallel)
        if install_arguments is None:
            install_arguments = []
        if parallel_install:
            install_arguments.append(parallel)

        abs_source_subfolder = os.path.abspath(directory)
        with self.managed_load_library_paths():
            with self.managed_pkg_config_paths(abs_source_subfolder):
                with tools.chdir(abs_source_subfolder):
                    autotools = AutoToolsBuildEnvironment(self)
                    autotools.fpic = True
                    autotools.cxx_flags.append("-O3")
                    autotools.flags.append("-O3")
                    if find_executable("lld") is not None:
                        autotools.link_flags.append("-fuse-ld=lld")

                    if include_paths is not None:
                        autotools.include_paths += include_paths

                    autotools.configure(args=arguments)
                    autotools.make(args=make_arguments)
                    autotools.install(args=install_arguments)

    def package_licenses(self):
        """Include any license into the package."""
        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)

    def package(self):
        """Assemble the package."""
        self.package_licenses()
        self.clean_package()

    def package_info(self):
        """Edit package info"""

        if os.name != "nt":
            bin_directory = os.path.join(self.package_folder, "bin")
            lib_directory = os.path.join(self.package_folder, "lib")

            if self.add_bin_to_path and executable_in_directory(bin_directory):
                self.env_info.PATH.append(bin_directory)

            if self.add_lib_to_ld_path and library_in_directory(lib_directory):
                self.env_info.LD_LIBRARY_PATH.append(lib_directory)
