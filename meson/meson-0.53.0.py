import os
from conans import python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

BASH_WRAPPER = """#!/usr/bin/env bash
this_directory=$(dirname "$0")
exec "${this_directory}/meson.py" "$@"
"""

BAT_WRAPPER = """@echo off
CALL python %-dp0/meson.py %*
"""

class meson(pyreq.BaseConanFile):
    description = "project to create the best possible next-generation build system"
    url = "https://github.com/mesonbuild/meson"
    license = "Apache-2.0"
    version = "0.53.0"
    name = "meson"

    settings = "os"
   
    def requirements(self):
        """Define runtime requirements."""
        self.requires("ninja/1.9.0@tdelame/stable")
        self.requires("cpython/3.7.5@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        directory = "{}-{}".format(self.name, self.version)
        url = "https://github.com/mesonbuild/meson/archive/{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

        wrapper_path = os.path.join(self._source_subfolder, "meson")
        with open(wrapper_path, "w") as outfile:
            outfile.write(BASH_WRAPPER if self.settings.os == "Linux" else BAT_WRAPPER)
        pyreq.set_executable_bit(wrapper_path)

    def package(self):
        """Assemble the package."""
        self.copy(pattern="*", dst="bin", src=self._source_subfolder)
        base_path = os.path.join(self.package_folder, "bin")
        for element in [
            ".coveragerc", ".editorconfig", ".flake8", ".github", ".mailmap", ".pylintrc", ".travis.yml", "README.md",
            "azure-pipelines.yml", "ci", "ciimage", "contributing.md", "cross", "docs", "ghwt.py", "graphics", "lgtm.yml",
            "man", "manual tests", "msi", "test cases"]:
            pyreq.remove(os.path.join(base_path, element))
        super(meson, self).package()

    def package_id(self):
        self.info.header_only()