from distutils.spawn import find_executable
from conans import ConanFile, python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")
import os, re, shutil, subprocess

class TBB(pyreq.CMakeConanFile):
    description = "Threading Building Blocks"
    license = "Apache 2.0"
    url = "https://github.com/01org/tbb"
    version = "2019-U6"
    name = "TBB"

    settings = "os", "build_type"
    _glibcxx_version = None
    
    def source(self):
        """Retrieve source code."""
        # Use the repository of Wenzel Jakob that adds a CMake layer over TBB code.
        commit = "20357d83871e4cb93b2c724fe0c337cd999fd14f"
        url = "https://github.com/wjakob/tbb/archive/{}.zip".format(commit)
        directory = "tbb-{}".format(commit)

        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def _get_glibcxx_version(self):
        if self._glibcxx_version is None and self.settings.os == "Linux" and find_executable("gcc") is not None:
            self._glibcxx_version = subprocess.check_output(["gcc", "-dumpversion"]).decode("utf-8")

            # Keep it simple to work on python 2.7 as well as on python 3+
            major, minor, build = 0, 0, 0
            version_numbers = re.findall(r"\d+", self._glibcxx_version)
            version_numbers_count = len(version_numbers)

            if version_numbers_count > 0:
                major = int(version_numbers[0])

            if version_numbers_count > 1:
                minor = int(version_numbers[1])

            if version_numbers_count > 2:
                build = int(version_numbers[2])

            self._glibcxx_version = major * 10000 + minor * 100 + build

        return self._glibcxx_version

    def cmake_definitions(self):
        # TBBMALLOC PROXY is not included into this package because:
        # - it prevent crashes when it is linked to, since it should be preloaded only to replace
        # allocators.
        # - it serves a different purpose and could be then included into another package if needed.

        definition_dict = {
          "CMAKE_BUILD_TYPE": self.settings.build_type,
          "TBB_BUILD_SHARED": self.options.shared,
          "TBB_BUILD_STATIC": not self.options.shared,
          "TBB_BUILD_TBBMALLOC": True,
          "TBB_BUILD_TBBMALLOC_PROXY": False,
          "TBB_BUILD_TESTS": False,
          "TBB_CI_BUILD": False
        }

        if self.settings.os == "Linux":
            glibcxx_version = self._get_glibcxx_version()
            if glibcxx_version:
                definition_dict["TBB_USE_GLIBCXX_VERSION"] = glibcxx_version

        # Normally not necessary, but it does not cost anything to enforce it.
        if self.settings.build_type == "Debug":
            definition_dict[ "CMAKE_CXX_FLAGS" ] = "-DTBB_USE_DEBUG=2"

        return definition_dict

    def package(self):
        """Assemble the package."""
        super(TBB, self).package()
        pyreq.remove(os.path.join(self.package_folder, "include", "tbb", "index.html"))

    def package_info(self):
        """Edit the package info."""
        self.cpp_info.libs = ["tbb", "tbbmalloc"]

        if self.settings.build_type == "Debug":
            self.cpp_info.defines.append( "TBB_USE_DEBUG=1" )
