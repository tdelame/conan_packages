
import subprocess
import logging
import sys
import os

from .utils import execute_command, current_directory

class PackageDownloader(object):
    """Download a list of packages."""

    def __init__(self, settings):
        self._settings = settings

    def download(self, packages):
        """
        :param packages: a list Package"""
        conan_file_path = os.path.join(self._settings.tempdir, "conanfile.txt")
        with open(conan_file_path, "w") as outfile:
            outfile.write("[requires]\n")
            for package in packages:
                outfile.write("{}\n".format(package.package_name()))

        with current_directory(self._settings.tempdir):
            command = "conan install {}".format(conan_file_path)
            if self._settings.quiet:
                log_path = os.path.join(self._settings.tempdir, "command.log")

                if not execute_command(command, log_path):
                    logging.error("downloading packages: failed")
                    with open(log_path, "r") as infile:
                        logging.error("command output:\n{}".format(infile.read()))
                        sys.exit(1)
            else:
                if subprocess.call(command, shell=True) != 0:
                    logging.error("downloading packages: failed")
                    sys.exit(1)
            logging.info("dowloading packages: success")
        
