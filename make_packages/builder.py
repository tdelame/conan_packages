from contextlib import contextmanager
import subprocess
import logging
import sys
import os

from .utils import execute_command

class PackageBuilder(object):

    def __init__(self, settings):
        self._settings = settings

    def _exist_locally(self, name, version):
        check_log_path = os.path.join(self._settings.tempdir, "check_locally.log")
        command = "conan search {}".format(self.conan_package_name(name, version))
        if execute_command(command, check_log_path):
            with open(check_log_path, "r") as infile:
                return infile.read().find("There are no packages for reference") == -1
        return False

    def _exist_remotely(self, name, version):
        check_log_path = os.path.join(self._settings.tempdir, "check_remotely.log")
        command = "conan search {} -r {}".format(
            self.conan_package_name(name, version),
            self._settings.repo_name)
        if execute_command(command, check_log_path):
            with open(check_log_path, "r") as infile:
                return infile.read().find("There are no packages for reference") == -1
        return False

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

    def conan_package_name(self, name, version):
        return "{}/{}@{}/{}".format(
            name, version, self._settings.repo_user, self._settings.repo_channel)

    def conan_recipe_path(self, name, version):
        return os.path.join(self._settings.root, name, "{}-{}.py".format(name, version))

    def make_binary(self, name, version):
        if not self._settings.force_build and self._exist_locally(name, version):
            logging.info("creating binary package {}/{}: already exist locally".format(
                name, version))
            return

        package_directory = os.path.join(self._settings.root, name, "package")
        package_name = self.conan_package_name(name, version)

        os.chdir(package_directory)

        self._run_command(
            "conan export-pkg {} {} {} -s os=Linux".format(
                self.conan_recipe_path(name, version),
                package_name,
                "--force" if self._settings.force_build else ""),
            "building binary package {}/{}".format(name, version))

        if not self._settings.local:
            self._run_command(
                "conan upload {} --all -r={} {}".format(
                    package_name, self._settings.repo_name,
                    "--force" if self._settings.force_upload else ""),
                "uploading package {}/{}".format(name, version))

    def make(self, name, version, settings=None, options=None):
        if not self._settings.force_build and self._exist_locally(name, version):
            logging.info("creating package {}/{}: already exist locally".format(
                name, version))
            return

        if settings is None:
            settings = {}
        if "build_type" not in settings:
            settings["build_type"] = self._settings.build_type
        settings["os"] = "Linux"

        settings_string = ""
        for key, value in settings.items():
            settings_string += " -s {}={}".format(key, value)

        if options is None:
            options = {}
        options_string = ""
        for key, value in options.items():
            options_string += " -o {}={}".format(key, value)

        package_name = self.conan_package_name(name, version)
        recipe_path = self.conan_recipe_path(name, version)
        self._run_command(
            "conan create {} {} {} {}".format(
                recipe_path,
                package_name,
                settings_string,
                options_string),
            "creating package {}/{}, settings={}{}".format(
                name, version, settings, "" if not options else ", options={}".format(options)))

    def upload(self, name, version):
        if not self._settings.local and \
            (self._settings.force_build or self._settings.force_upload or not self._exist_remotely(name, version)):
            self._run_command(
                "conan upload {} --all -r={} {}".format(
                    self.conan_package_name(name, version),
                    self._settings.repo_name,
                    "--force" if self._settings.force_build or self._settings.force_upload else ""),
                "uploading all packages {}/{}".format(name, version))

    def make_and_upload(self, name, version, settings=None, options=None):
        self.make(name, version, settings, options)
        self.upload(name, version)
