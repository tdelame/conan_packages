import os
from conans import python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class pyside2(pyreq.BaseConanFile):
    description = "Qt for Python"
    license = "LGPL-3.0"
    url = "https://doc.qt.io/qtforpython"
    version = "5.14.0"
    name = "pyside2"

    settings = "os"

    # Note: make sure you have libclang available in your LD_LIBRARY_PATH. I could make a recipe
    # for this dependence but since I compile everything with clang, I already have this build
    # dependence on all my machines.

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is not yet available for your OS")
    
    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("cmake/3.15.4@tdelame/stable")
        self.build_requires("ninja/1.9.0@tdelame/stable")

    def requirements(self):
        """Define runtime requirements."""
        self.requires("cpython/3.7.5@tdelame/stable")
        self.requires("qt/5.14.0@tdelame/stable")
    
    def source(self):
        """Retrieve source code."""
        self.download(
            "https://download.qt.io/official_releases/QtForPython/pyside2/PySide2-5.14.0-src",
            directory="pyside-setup-opensource-src-{}".format(self.version),
            compression="zip")

    def build(self):
        """Build the elements to package."""
        environment = {"PYSIDE_DISABLE_INTERNAL_QT_CONF": "1"}

        if self.settings.os == "Linux":
            environment = {"LDFLAGS": "-fuse-ld=lld"}

        arguments = [
            "--qmake={}".format(os.path.join(self.deps_cpp_info["qt"].rootpath, "bin", "qmake")),
            "--cmake={}".format(os.path.join(self.deps_cpp_info["cmake"].rootpath, "bin", "cmake")),
            "--build-type=all", "--skip-docs",
            "--prefix={}".format(self.package_folder),
            "--parallel={}".format(tools.cpu_count())
        ]
        
        with self.managed_load_library_paths():
            with tools.environment_append(environment):
                with tools.chdir(self._source_subfolder):
                    self.run("python setup.py install {}".format(" ".join(arguments)))

    def package(self):
        """Assemble the package."""
        self.copy(pattern="LICENSE.LGPLv3", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        """Edit package info."""
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.LD_LIBRARY_PATH.extend(self.deps_cpp_info["qt"].lib_paths)
        self.env_info.PYTHONPATH.append(os.path.join(self.package_folder, "lib", "python3.7", "site-packages"))
