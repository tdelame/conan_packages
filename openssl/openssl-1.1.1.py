import shutil
import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools

def __on_shutil_rmtree_error(func, path, exc_info):
    #pylint: disable=unused-argument
    os.chmod(path, stat.S_IWRITE)
    os.remove(path)


def remove_directory(directory_path):
    """Remove a directory, if it exists, as well as all of its content.
    """
    shutil.rmtree(directory_path, onerror=__on_shutil_rmtree_error)

class OpenSSL(ConanFile):
    description = "robust, commercial-grade, and full-featured toolkit for the TLS and SSL protocols"
    license = "Apache 2.0"
    url = "https://openssl.org"
    version = "1.1.1d"
    settings = "os"
    name = "openssl"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("This recipe is only available for Linux")

    def source(self):
        """Retrieve source code."""
        folder_name = "OpenSSL_1_1_1d"
        targz_file_name = "{}.tar.gz".format(folder_name)
        destination_folder = os.path.abspath("{}/{}".format(self.name, folder_name))
        url = "https://github.com/openssl/openssl/archive/{}".format(targz_file_name)

        tools.download(url, targz_file_name)
        tools.untargz(targz_file_name, self.name)
        os.rename("{}/openssl-{}".format(self.name, folder_name), destination_folder)
        os.symlink("config", "{}/configure".format(destination_folder))
        os.remove(targz_file_name)

    def build(self):
        """Build the elements to package."""
        autotools = AutoToolsBuildEnvironment(self)
        autotools.fpic = True
        autotools.configure(
            configure_dir="openssl/OpenSSL_1_1_1d",
            args=[
                "--release",
                "--prefix={}/to_copy".format(self.build_folder)])
        autotools.make(args=["-j{}".format(tools.cpu_count())])
        autotools.install(args=["-j{}".format(tools.cpu_count())])

    def package(self):
        """Assemble the package."""
        remove_directory("{}/to_copy/share".format(self.build_folder))
        self.copy("*", src="to_copy", dst="", keep_path=True)

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
