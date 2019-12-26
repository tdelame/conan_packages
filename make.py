#!/usr/bin/env python
"""Create or update conan packages."""
import argparse
import logging
import tempfile
import sys
import os

from make_packages.utils import execute_command
from make_packages.builder import PackageBuilder

def _parse_compilers(tempdir):
    default_compiler = None
    default_compiler_version = None
    default_cc_var = None
    default_cxx_var = None
    gcc_version = None

    result_file = os.path.join(tempdir, "conan_profile.log")
    command = "conan profile get settings.compiler default"
    if execute_command(command, result_file):
        with open(result_file, "r") as infile:
            default_compiler = infile.read().strip()

        command = "conan profile get settings.compiler.version default"
        if execute_command(command, result_file):
            with open(result_file, "r") as infile:
                default_compiler_version = infile.read().strip()
        else:
            logging.error("cannot fetch default conan compiler version")
            sys.exit(1)
    else:
        logging.error("cannot fetch default conan compiler")
        sys.exit(1)

    if default_compiler != "gcc":
        command = "gcc --version"
        if execute_command(command, result_file):
            with open(result_file, "r") as infile:
                gcc_version = infile.read().strip()

            start_index = None
            end_index = None
            length = len(gcc_version)
            for i in range(0, length):
                if gcc_version[i].isdigit():
                    start_index = i
                    break

            if start_index is not None:
                for i in range(start_index, length):
                    if gcc_version[i] == '\n':
                        end_index = i
                        break

            if start_index is None or end_index is None:
                logging.error("cannot parse gcc version for '{}'".format(gcc_version))
                sys.exit(1)

            gcc_version = gcc_version[start_index : end_index]
            if gcc_version.count(".") > 1:
                first = gcc_version.find(".")
                second = gcc_version.find(".", first + 1)
                gcc_version = gcc_version[:second]
        else:
            logging.error("cannot fetch gcc version, make sure it is installed and in PATH")
            sys.exit(1)

    command = "conan profile get env.CC default"
    if execute_command(command, result_file):
        with open(result_file, "r") as infile:
            default_cc_var = infile.read().strip()

    command = "conan profile get env.CXX default"
    if execute_command(command, result_file):
        with open(result_file, "r") as infile:
            default_cxx_var = infile.read().strip()


    return default_compiler, default_compiler_version, default_cc_var, default_cxx_var, gcc_version

def extract_settings(argument_list=None):
    if argument_list is None:
        argument_list = sys.argv[1 :]

    parser = argparse.ArgumentParser(
        prog="Make Conan Packages",
        description="Create or update conan packages")

    parser.add_argument(
        "-f", "--force", action="store_true",
        help="erase existing local/remote packages")

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

    default_compiler, default_compiler_version, default_cc_var, default_cxx_var, gcc_version = _parse_compilers(settings.tempdir)
    setattr(settings, "default_compiler", default_compiler)
    setattr(settings, "default_compiler_version", default_compiler_version)
    setattr(settings, "default_cc_var", default_cc_var)
    setattr(settings, "default_cxx_var", default_cxx_var)
    setattr(settings, "gcc_version", gcc_version)

    return settings

def update_repo(settings):
    if not settings.local:
        log_path = os.path.join(settings.tempdir, "conan_remote.log")
        if settings.repo_url:
            execute_command(
                "conan remote add {} {}".format(settings.repo_name, settings.repo_url),
                log_path)

        if settings.repo_key:
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
    builder = PackageBuilder(settings)

    builder.make_and_upload("ninja", "1.9.0")            # no deps
    builder.make_and_upload("cmake", "3.15.4")           # no deps
    builder.make_and_upload("libunwind", "1.3.1")        # no deps
    builder.make_binary("GLU", "9.0.0")                  # no deps
    builder.make_and_upload("zlib", "1.2.11")            # no deps
    builder.make_and_upload("libjpeg", "9c")             # no deps
    # on some configurations with clang, the compilation of the following packages crashes. I do
    # not want to spend time on debugging to make the compilation works on any configurations, so
    # I switch to GCC instead.
    with builder.use_gcc():
        builder.make_and_upload("bison", "3.4.2")        # no deps
        builder.make_and_upload("OpenSSL", "1.1.1d")     # zlib
        builder.make_and_upload("icu", "65.1")           # cmake, ninja
        builder.make_and_upload("GLEW", "2.1.0")         # cmake, ninja, GLU
        builder.make_and_upload("cpython", "3.7.5")      # no deps

    builder.make_and_upload("flex", "2.6.4")             # bison
    builder.make_and_upload("libpng", "1.6.37")          # cmake, ninja, zlib
    builder.make_and_upload("curl", "7.61.1")            # cmake, ninja, zlib, OpenSLL
    builder.make_and_upload("double-conversion", "3.1.5")# cmake, ninja
if __name__ == "__main__":
    main()
