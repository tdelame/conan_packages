import subprocess
import logging
import sys
import os

from .utils import execute_command
from .downloader import PackageDownloader
from .builder import PackageBuilder
from .package import Package

class PackageManager(object):
    """Build, Upload and/or download packages depending on command line arguments."""

    def __init__(self, settings):
        self._settings = settings
        self._list = []        
        if self._settings.download:
            self._internal = PackageDownloader(settings)
        else:
            self._internal = PackageBuilder(settings)

    def _make_pkg(self, name, version, settings, options):
        return Package(
            name, version, self._settings.repo_user, self._settings.repo_channel,
            self._settings.build_type, settings, options)

    def manage(self, name, version, binary=False, settings=None, options=None):
        package = self._make_pkg(name, version, settings, options)
        if self._settings.download:
            self._list.append(package)
        else:
            self._internal.make(package, binary=binary)

    def finish(self):
        if self._list:
            self._internal.download(self._list)
            