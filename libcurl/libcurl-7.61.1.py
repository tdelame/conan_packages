from distutils.spawn import find_executable
import shutil
import os
from conans import ConanFile, CMake, tools

class Curl(ConanFile):
    description = "command line tool and library for transferring data with URLs"
    url = "https://openssl.org"
    version = "7.61.1"
    name = "libcurl"
    license = "MIT"

    settings = "os"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    # nice idea (among other things) taken from bincrafters (https:://github.com/bincrafters/conan-libcurl)
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def requirements(self):
        """Define runtime requirements."""
        self.requires("OpenSSL/1.1.1d@tdelame/stable")
        self.requires("zlib/1.2.11@tdelame/stable")

    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("cmake/3.15.4@tdelame/stable")
        self.build_requires("ninja/1.9.0@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        url = "https://github.com/curl/curl/releases/download/curl-{}/curl-{}.tar.gz".format(
            self.version.replace(".", "_"),
            self.version)
        tools.get(url)
        os.rename("curl-{}".format(self.version), self._source_subfolder)

        tools.download("https://curl.haxx.se/ca/cacert.pem", "cacert.pem", verify=True)

    def _configure_cmake(self):
        definition_dict = {
            "BUILD_TESTING": False,
            "BUILD_CURL_EXE": False,
            "CURL_DISABLE_LDAP": True,
            "BUILD_SHARED_LIBS": self.options.shared,
            "CURL_STATICLIB": not self.options.shared,
            "CMAKE_DEBUG_POSTFIX": "",
            "CMAKE_USE_LIBSSH2": False,
            "CMAKE_USE_OPENSSL": True,
            "OPENSSL_ROOT_DIR": os.path.join(self.deps_cpp_info["OpenSSL"].include_paths[0], "../")
        }

        if self.settings.os == "Linux" and find_executable("lld") is not None:
            definition_dict["CMAKE_SHARER_LINKER_FLAGS"] = "-fuse-ld=lld"
            definition_dict["CMAKE_EXE_LINKER_FLAGS"] = "-fuse-ld=lld"

        cmake = CMake(self, generator="Ninja")
        cmake.configure(
            defs=definition_dict,
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder)
        return cmake

    def build(self):
        """Build the elements to package."""
        with tools.chdir(self._source_subfolder):
            tools.replace_in_file("CMakeLists.txt", "include(CurlSymbolHiding)", "")

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        """Assemble the package."""
        self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder, ignore_case=True, keep_path=True)
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        self.copy("cacert.pem", keep_path=True)
        shutil.rmtree(os.path.join(self.package_folder, "share", "man"), ignore_errors=True)
        for binary in ["curl", "curl.exe"]:
            binary_path = os.path.join(self.package_folder, "bin", binary)
            if os.path.isfile(binary_path):
                os.remove(binary_path)

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["curl", "rt", "pthread"]
