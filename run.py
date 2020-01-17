#!/usr/bin/env python
"""Create or update conan packages."""
import argparse
import logging
import tempfile
import sys
import os

from internals.utils import execute_command
from internals.manager import PackageManager

def extract_settings(argument_list=None):
    if argument_list is None:
        argument_list = sys.argv[1 :]

    parser = argparse.ArgumentParser(
        prog="Make Conan Packages",
        description="Create or update conan packages")

    parser.add_argument(
        "--download", action="store_true",
        help="download packages from remote instead of building them.")

    parser.add_argument(
        "--force-build", action="store_true",
        help="erase existing local packages")

    parser.add_argument(
        "--force-upload", action="store_true",
        help="erase existing remote packages")

    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="turn off command output when successful")

    parser.add_argument(
        "--local", action="store_true",
        help="do not upload built packages")

    parser.add_argument(
        "--no-sudo", action="store_true",
        help="prevent the use of sudo in commands")

    parser.add_argument(
        "-b", "--build-type", type=str, default="Release", choices=["Debug", "Release"],
        help="build type for the packages that will be created")

    parser.add_argument(
        "--repo-url", type=str, default="https://api.bintray.com/conan/tdelame/conan_packages",
        help="URL of the conan repository to use for fetching and uploading packages")

    parser.add_argument(
        "--repo-key", type=str,
        help="API key to upload to the conan repository")

    parser.add_argument(
        "--repo-name", type=str, default="conan_packages",
        help="Name of the conan repository used to upload packages to")

    parser.add_argument(
        "--repo-channel", type=str, default="stable",
        help="Name of the conan repository channel used to upload packages to")

    parser.add_argument(
        "--repo-user", type=str, default="tdelame",
        help="Name of the conan repository owner used to upload packages to")

    settings = parser.parse_args(argument_list)
    setattr(settings, "tempdir", tempfile.mkdtemp(prefix="make_conan_packages"))
    setattr(settings, "root", os.path.abspath(sys.path[0]))
    setattr(settings, "linux", os.name != "nt")
    setattr(settings, "windows", not settings.linux)

    return settings

def update_repo(settings):
    log_path = os.path.join(settings.tempdir, "conan_remote.log")
    if settings.repo_url:
        execute_command(
            "conan remote add {} {}".format(settings.repo_name, settings.repo_url),
            log_path)

    if not settings.local and settings.repo_key:
            execute_command(
                "conan user -p {} -r {} {}".format(settings.repo_key, settings.repo_name, settings.repo_user),
                log_path)

def main():
    logging.basicConfig(
        format="%(asctime)s.%(msecs)03d | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG)
    logging.info("application started")

    settings = extract_settings()
    update_repo(settings)
    if settings.no_sudo:
        os.environ["CONAN_SYSREQUIRES_SUDO"] = "False"

    manager = PackageManager(settings)

    # the deps on the three following packages are ignored after for brevity
    manager.manage("pyreq", "1.0.0")                   # no deps
    manager.manage("ninja", "1.9.0")                   # no deps
    manager.manage("cmake", "3.15.4")                  # no deps

    # header-only libraries
    manager.manage("fontstash", "1.0.1")
    manager.manage("rapidjson", "1.1.0")
    manager.manage("GSL", "2.1.0")
    manager.manage("pybind11", "2.4.3")
    manager.manage("catch2", "2.11.1")
    manager.manage("boost-headers", "1.70.0")
    manager.manage("spdlog-rumba", "1.5.0")

    manager.manage("GLU", "9.0.0")                     # no deps
    manager.manage("IlmBase", "2.3.0")                 # no deps
    manager.manage("TBB", "2019-U6")                   # no deps
    manager.manage("doxygen", "1.8.17")                # no deps
    manager.manage("gperf", "3.1")                     # no deps
    manager.manage("libunwind", "1.3.1")               # no deps
    manager.manage("libffi", "3.2.1")                  # no deps
    manager.manage("libjpeg", "9c")                    # no deps
    manager.manage("libuuid", "1.0.3")                 # no deps
    manager.manage("bison", "3.4.2")                   # no deps
    manager.manage("libiconv", "1.16")                 # no deps
    manager.manage("zlib", "1.2.11")                   # no deps
    manager.manage("lzma", "5.2.4")                    # no deps    
    manager.manage("bzip2", "1.0.8")                   # no deps
    manager.manage("expat", "2.2.9")                   # no deps
    manager.manage("icu", "65.1")                      # no deps
    manager.manage("zstd", "1.4.4")                    # no deps
    manager.manage("double-conversion", "3.1.5")       # no deps
    manager.manage("libsndfile", "1.0.29")             # no deps
    manager.manage("boost-atomic", "1.70.0")           # boost-headers
    manager.manage("boost-filesystem", "1.70.0")       # boost-headers
    manager.manage("boost-date-time", "1.70.0")        # boost-headers
    manager.manage("boost-chrono", "1.70.0")           # boost-headers
    manager.manage("boost-thread", "1.70.0")           # boost-headers
    manager.manage("embree", "3.3.0")                  # TBB
    manager.manage("flex", "2.6.4")                    # bison
    manager.manage("OpenSSL", "1.1.1d")                # zlib
    manager.manage("libpng", "1.6.37")                 # zlib
    manager.manage("hdf5", "1.8.21")                   # zlib
    manager.manage("OpenEXR", "2.4.0")                 # zlib
    manager.manage("freetype", "2.9.1")                # zlib, libpng
    manager.manage("libcurl", "7.61.1")                # zlib, OpenSSL
    manager.manage("alembic", "1.7.10")                # zlib, hdf5, OpenEXR
    manager.manage("fontconfig", "2.13.92")            # expat, freetype, gperf
    manager.manage("libxml2", "2.9.9")                 # icu, zlib, libiconv
    manager.manage("gettext", "0.20.1")                # libiconv, libxml2
    manager.manage("GLEW", "2.1.0")                    # GLU
    manager.manage("cpython", "3.7.5")                 # OpenSSL, expat, lzma, libuuid, bzip2, libffi
    manager.manage("OpenSubdiv", "3.4.0")              # zlib, TBB, GLEW    
    manager.manage("tiff", "4.1.0")                    # zlib, zstd, lzma, libjpeg
    manager.manage("OpenImageIO", "2.1.10.1")          # zlib, tiff, OpenEXR, libjpeg, libpng, boost-filesystem, boost-thread, TBB, bzip2, freetype
    manager.manage("meson", "0.53.0")                  # cpython
    manager.manage("libalsa", "1.2.1.2")               # cpython
    manager.manage("PortAudio", "2018-12-24")          # libalsa
    manager.manage("openal", "1.20.0")                 # libalsa
    
    # X11 libraries for Linux
    if settings.linux:
        manager.manage("util-macros", "1.19.2")        # no deps
        manager.manage("xorgproto", "2019.1")          # no deps
        manager.manage("glproto", "1.4.17")            # no deps
        manager.manage("dri2proto", "2.8")             # no deps
        manager.manage("dri3proto", "1.0")             # no deps
        manager.manage("xtrans", "1.4.0")              # no deps
        manager.manage("libpthread-stubs", "0.1")      # no deps
        manager.manage("libpciaccess", "0.16")         # no deps
        manager.manage("xproto", "7.0.31")             # no deps
        manager.manage("libXdmcp", "1.1.3")            # xproto
        manager.manage("libXau", "1.0.9")              # xorgproto
        manager.manage("xcb-proto", "1.13")            # cpython
        manager.manage("libxcb", "1.13.1")             # xcb-proto, util-macros, libXau, libpthread-stubs, libXdmcp
        manager.manage("libX11", "1.6.8")              # xorgproto, xtrans, libxcb
        manager.manage("libXext", "1.3.4")             # libX11
        manager.manage("libFS", "1.0.8")               # xtrans, xorgproto, util-macros
        manager.manage("libICE", "1.0.10")             # xtrans, xorgproto, util-macros
        manager.manage("libSM", "1.2.3")               # libICE
        manager.manage("libXScrnSaver", "1.2.3")       # libX11, libXext
        manager.manage("libXt", "1.2.0")               # libSM, libX11
        manager.manage("libXmu", "1.1.3")              # libXt, libXext
        manager.manage("libXpm", "3.5.12")             # libX11, gettext
        manager.manage("libXaw", "1.0.13")             # libXmu, libXpm
        manager.manage("libXfixes", "5.0.3")           # libX11
        manager.manage("libXcomposite", "0.4.5")       # libXfixes
        manager.manage("libXrender", "0.9.10")         # libX11
        manager.manage("libXcursor", "1.2.0")          # libXfixes, libXrender
        manager.manage("libXdamage", "1.1.5")          # libXfixes
        manager.manage("libfontenc", "1.1.4")          # xorgproto, util-macros, zlib
        manager.manage("libXfont2", "2.0.3")           # libfontenc, xtrans, freetype
        manager.manage("libXft", "2.3.3")              # libXrender, freetype, fontconfig
        manager.manage("libXi", "1.7.10")              # libXext, libXfixes
        manager.manage("libXinerama", "1.1.4")         # libXext, libXfixes
        manager.manage("libXrandr", "1.5.2")           # libXrender, libXext
        manager.manage("libXres", "1.2.0")             # libX11, libXext
        manager.manage("libXtst", "1.2.3")             # libXi
        manager.manage("libXv", "1.0.11")              # libX11, libXext
        manager.manage("libXvMC", "1.0.11")            # libXv
        manager.manage("libXxf86dga", "1.1.5")         # libX11, libXext
        manager.manage("libXxf86vm", "1.1.4")          # libX11, libXext
        manager.manage("libdmx", "1.1.4")              # libX11, libXext
        manager.manage("libxkbfile", "1.1.0")          # libX11
        manager.manage("libxshmfence", "1.3")          # xorgproto, util-macros
        manager.manage("xcb-util", "0.4.0")            # libxcb
        manager.manage("xcb-util-wm", "0.4.0")         # libxcb
        manager.manage("xcb-util-image", "0.4.0")      # xcb-util
        manager.manage("xcb-util-keysyms", "0.4.0")    # libxcb
        manager.manage("xcb-util-renderutil", "0.3.9") # libxcb
        manager.manage("xkeyboard-config", "2.28")     # xproto, libX11
        manager.manage("libxkbcommon", "0.9.1")        # meson, bison, xkeyboard-config, libxcb

    manager.manage("qt", "5.14.0")                     # bison, flex, fontconfig, gperf, libalsa, libXext, libXi, libXrender, libX11, libxcb, libxkbcommon, libpng, libjpeg, zlib, openssl, cpython, freetype, expat, zstd, openal, icu
    manager.manage("pyside2", "5.14.0")                # cpython, qt

    manager.manage("wheel", "0.33.6")                  # cpython
    manager.manage("pyinstaller", "3.6")        
    manager.finish()

if __name__ == "__main__":
    main()
