    # libXext, libXrender, libX11,  libXcursor, libalsa, libXrandr, libXinerama, libxkbcommon
    # no: wayland, wayland-protocols, libxss, libibus
    # not now: libpulse, jack
import os
from conans import python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class SDL2(pyreq.CMakeConanFile):
    description = "Simple DirectMedia Layer"
    url = "https://libsdl.org"
    license = "zlib"
    name = "SDL2"
    version = "2.0.10"

    settings = "os"

    def build_requirements(self):
        """Define runtime requirements."""
        super(SDL2, self).build_requirements()
        # no wayland, wayland-protocols, libxss or libibus
        # not yet: libpulse, jack
        self.build_requires("libXext/1.3.4@tdelame/stable")
        self.build_requires("libXrender/0.9.10@tdelame/stable")
        self.build_requires("libX11/1.6.8@tdelame/stable")
        self.build_requires("libXcursor/1.2.0@tdelame/stable")
        self.build_requires("libalsa/1.2.1.2@tdelame/stable")
        self.build_requires("libXrandr/1.5.2@tdelame/stable")
        self.build_requires("libXinerama/1.1.4@tdelame/stable")
        self.build_requires("libxkbcommon/0.9.1@tdelame/stable")

    def source(self):
        self.download("https://www.libsdl.org/release")

    def cmake_definitions(self):
        """Setup CMake definitions."""
        defs = {
            "SDL_STATIC": not self.options.shared,
            "SDL_DLOPEN": True,
            "ARTS": False,
            "ESD": False,
            "ASLA": True,
            "RPATH": False,
            "CLOCK_GETTIME": True,
        }
        self.add_default_definitions(defs)
        return defs

    def package_info(self):
        """Edit package info."""
        super(SDL2, self).package_info()
        self.cpp_info.libs = ["SDL2"]
        self.cpp_info.system_libs = ["dl", "m", "rt", "pthread"]
