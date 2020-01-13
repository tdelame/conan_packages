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

    @contextmanager
    def use_gcc(self):
        log_path = os.path.join(self._settings.tempdir, "switch_compiler.log")
        switched = False

        try:
            if self._settings.default_compiler != "gcc":

                command = "conan profile update settings.compiler=gcc default"
                if not execute_command(command, log_path):
                    logging.error("failed to switch conan default compiler to gcc")
                    sys.exit(1)
                switched = True
                command = "conan profile update settings.compiler.version={} default".format(
                    self._settings.gcc_version)

                if not execute_command(command, log_path):
                    logging.error("failed to set gcc version in conan default profile")
                    sys.exit(1)

                command = "conan profile update env.CC=gcc default"
                if not execute_command(command, log_path):
                    logging.error("failed to set env.CC=gcc in default profile")
                    sys.exit(1)

                command = "conan profile update env.CXX=g++ default"
                if not execute_command(command, log_path):
                    logging.error("failed to set env.CXX=g++ in default profile")
                    sys.exit(1)
            yield
        finally:
            if switched:
                command = "conan profile update settings.compiler={} default".format(
                    self._settings.default_compiler)
                if not execute_command(command, log_path):
                    logging.error("failed to restore default conan compiler to {}".format(
                        self._settings.default_compiler))
                    sys.exit(1)

                command = "conan profile update settings.compiler.version={} default".format(
                    self._settings.default_compiler_version)
                if not execute_command(command, log_path):
                    logging.error("failed to restore default conan compiler version to {}".format(
                        self._settings.default_compiler_version))
                    sys.exit(1)

                if self._settings.default_cc_var is not None:
                    command = "conan profile update env.CC={} default".format(self._settings.default_cc_var)
                else:
                    command = "conan profile remove env.CC default"
                if not execute_command(command, log_path):
                    logging.error("failed to restore env.CC in default profile")
                    logging.debug("command = {}".format(command))
                    with open(log_path, "r") as infile:
                        logging.debug(infile.read())
                    sys.exit(1)

                if self._settings.default_cxx_var is not None:
                    command = "conan profile update env.CXX={} default".format(self._settings.default_cxx_var)
                else:
                    command = "conan profile remove env.CXX default"
                if not execute_command(command, log_path):
                    logging.error("failed to restore env.CXX in default profile")
                    logging.debug("command = {}".format(command))
                    with open(log_path, "r") as infile:
                        logging.debug(infile.read())
                    sys.exit(1)
