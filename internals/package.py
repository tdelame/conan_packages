import os
import tempfile
from .utils import execute_command

class Package(object):

    temporary_directory = tempfile.mkdtemp(prefix="conan_package")

    def __init__(self, name, version, repo_user, repo_channel, default_build_type, settings=None, options=None):
        self._name = name
        self._version = version
        self._repo_user = repo_user
        self._repo_channel = repo_channel
        self._settings = settings
        self._options = options

        if self._settings is None:
            self._settings = {}
        if "build_type" not in self._settings:
            self._settings["build_type"] = default_build_type
        if "os" not in self._settings:
            self._settings["os"] = "Windows" if os.name == "nt" else "Linux"
        
        if self._options is None:
            self._options = {}
        
    def to_command(self):
        string = self.package_name()
        for key, value in self._settings.items():
            string += " -s {}={}".format(key, value)
        for key, value in self._options.items():
            string += " -o {}={}".format(key, value)
        return string

    def name(self):
        return self._name

    def package_name(self):
        return "{}/{}@{}/{}".format(self._name, self._version, self._repo_user, self._repo_channel)

    def package_short_name(self):
        return "{}/{}".format(self._name, self._version)

    def exist_locally(self):
        check_log_path = os.path.join(self.temporary_directory, "check_locally.log")
        command = "conan search {}".format(self.package_name())
        if execute_command(command, check_log_path):
            with open(check_log_path, "r") as infile:
                return infile.read().find("There are no packages for reference") == -1
        return False

    def recipe_path(self):
        return os.path.join(self._name, "{}-{}.py".format(self._name, self._version))

    def exist_remotely(self, repo_name):
        check_log_path = os.path.join(self.temporary_directory, "check_remotely.log")
        command = "conan search {} -r {}".format(self.package_name(), repo_name)
        if execute_command(command, check_log_path):
            with open(check_log_path, "r") as infile:
                return infile.read().find("There are no packages for reference") == -1
        return False        