import subprocess
import logging
import sys
import os

from .utils import execute_command

class PackageBuilder(object):

    def __init__(self, settings):
        self._settings = settings

    def _run_command(self, command, description):
        if self._settings.quiet:
            log_path = os.path.join(self._settings.tempdir, "command.log")
            if not execute_command(command, log_path):
                logging.error("{}: failed".format(description))
                with open(log_path, "r") as infile:
                    logging.error("command output:\n{}".format(infile.read()))
                    sys.exit(1)
        else:
            if subprocess.call(command, shell=True) != 0:
                logging.error("{}: failed".format(description))
                sys.exit(1)
        logging.info("{}: success".format(description))

    def _conan_recipe_path(self, package):
        return os.path.join(self._settings.root, package.recipe_path())

    def make(self, package, binary=False):
        build_package = self._settings.force_build or not package.exist_locally()
        if not build_package:
            logging.info("creating package {}: already exist locally".format(
                package.package_short_name()))
        else:
            recipe_path = self._conan_recipe_path(package)
            self._run_command(
                "conan {subcommand} {recipe_path} {package_command} {force}".format(
                    subcommand="export-pkg" if binary else "create",
                    recipe_path=recipe_path,
                    package_command=package.to_command(),
                    force="--force" if self._settings.force_build else ""),
                "building package {}".format(package.to_command()))

        upload_package = not self._settings.local and \
            (build_package or self._settings.force_upload or not package.exist_remotely(self._settings.repo_name))

        if upload_package:
            self._run_command(
                "conan upload {package_name} --all -r={repo_name} {force}".format(
                    package_name=package.package_name(),
                    repo_name=self._settings.repo_name,
                    force="--force" if self._settings.force_build or self._settings.force_upload else ""),
                "uploading all packages for {}".format(package.package_short_name()))
