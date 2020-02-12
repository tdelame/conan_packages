
import os
from conans import python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class Curl(pyreq.CMakeConanFile):
    description = "command line tool and library for transferring data with URLs"
    url = "https://openssl.org"
    version = "7.61.1"
    name = "libcurl"
    license = "MIT"

    settings = "os"
    
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

    def source(self):
        """Retrieve source code."""
        url = "https://github.com/curl/curl/releases/download/curl-{}/curl-{}.tar.gz".format(
            self.version.replace(".", "_"),
            self.version)
        tools.get(url)
        os.rename("curl-{}".format(self.version), self._source_subfolder)

        tools.download("https://curl.haxx.se/ca/cacert.pem", "cacert.pem", verify=True)

        with tools.chdir(self._source_subfolder):
            tools.replace_in_file("CMakeLists.txt", "include(CurlSymbolHiding)", "")

    def cmake_definitions(self):
        definitions_dict = {
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
        self.add_default_definitions(definitions_dict)
        return definitions_dict

    def package(self):
        """Assemble the package."""
        super(Curl, self).package()
        self.copy("cacert.pem", keep_path=True)
        for binary in ["curl", "curl.exe"]:
            binary_path = os.path.join(self.package_folder, "bin", binary)
            if os.path.isfile(binary_path):
                os.remove(binary_path)

    def package_info(self):
        """Edit package info."""
        super(Curl, self).package_info()
        self.cpp_info.libs = ["curl", "rt", "pthread"]
