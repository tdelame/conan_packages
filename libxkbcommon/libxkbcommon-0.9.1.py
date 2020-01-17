import os
from conans import python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class libxkbcommon(pyreq.BaseConanFile):
    description = "keymap handling library for toolkits and window systems"
    url = "https://github.com/xkbcommon/libxkbcommon"
    license = "MIT"
    name = "libxkbcommon"
    version = "0.9.1"

    settings = "os"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""
        if self.settings.os != "Linux":
            raise RuntimeError("libxkbcommon is only compatible with Linux")

    def build_requirements(self):
        """Define build-time requirements."""
        self.build_requires("meson/0.53.0@tdelame/stable")
        self.build_requires("bison/3.4.2@tdelame/stable")

    def requirements(self):
        """Define runtime requirements."""
        self.requires("xkeyboard-config/2.28@tdelame/stable")
        self.requires("libxcb/1.13.1@tdelame/stable")

    def source(self):
        """Retrieve source code."""
        directory = "libxkbcommon-xkbcommon-{}".format(self.version)
        url = "https://github.com/xkbcommon/libxkbcommon/archive/xkbcommon-{}.tar.gz".format(self.version)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        """Build the elements to package."""
        definitions = {
            "libdir": os.path.join(self.package_folder, "lib"),
            "default_library": ("shared" if self.options.shared else "static"),
            "enable-wayland": False,
            "enable-docs": False,
            "enable-x11": True
        }
        self.build_meson(definitions=definitions)

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["xkbcommon", "xkbcommon-x11"]
