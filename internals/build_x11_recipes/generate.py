from json import load as parse_json
import os

TEMPLATE = """
import os
import shutil
from glob import glob
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class {classname}({baseclass}):
    description = '{description}'
    url = "https://www.x.org/"
    license = "X11"
    settings = "os"
    {requirements}
    {build_requirements}

    def config_options(self):
        if self.settings.os != "Linux":
            raise RuntimeError("X11 libraries are available on Linux only")

    def source(self):
        directory = "{name}-{version}"
        url = "https://www.x.org/archive/individual/{namespace}/{{}}.tar.gz".format(directory)
        tools.get(url)
        os.rename(directory, self._source_subfolder)

    def build(self):
        self.build_autotools()

    def package_info(self):
        self.cpp_info.libs = [{libs}]

    {package_id}
"""

PACKAGE_ID_HEADERONLY_TEMPLATE = """
    def package_id(self):
        self.info.header_only()
"""

THIS_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ROOT_DIRECTORY = os.path.abspath(os.path.join(THIS_DIRECTORY, "..", ".."))

def get_file_path(name, version):
    directory = os.path.join(ROOT_DIRECTORY, name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return os.path.join(directory, "{}-{}.py".format(name, version))

def main():
    x11_libraries = parse_json(open(os.path.join(THIS_DIRECTORY, "data.json")))
    x11_versions = {}
    for library in x11_libraries:
        x11_versions[library["name"]] = library["version"]

    print("    # X11 libraries for Linux\n    if settings.linux:")
    for library in x11_libraries:
        name = library["name"]
        classname = name.replace("-", "")
        baseclass = "pyreq.BaseConanFile"
        description = library["description"]
        builder_requires = []
        if "requires" in library:
            requires = []
            for require in library["requires"]:
                if not "@" in require:
                    requires.append('"{}/{}@tdelame/stable"'.format(require, x11_versions[require]))
                    builder_requires.append(require)
                else:
                    requires.append('"{}"'.format(require))
                    builder_requires.append(require[:require.find("/")])
            requires = 'requires = ({})'.format(", ".join(requires))
        else:
            requires = ""

        if "build_requires" in library:
            build_requires = []
            for brequire in library["build_requires"]:
                if not "@" in brequire:
                    build_requires.append('"{}/{}@tdelame/stable"'.format(brequire, x11_versions[brequire]))
                    builder_requires.append(brequire)
                else:
                    build_requires.append('"{}"'.format(brequire))
                    builder_requires.append(brequire[:brequire.find("/")])
            build_requires = "build_requires = ({})".format(", ".join(build_requires))
        else:
            build_requires = ""

        version = x11_versions[name]
        namespace = library.get("namespace", "lib")
        libs = ""
        package_id = ""
        header_only = library.get("header-only", False)
        if "libs" in library:
            libs = ", ".join(['"{}"'.format(lib) for lib in library["libs"]])
        elif not header_only:
            libs = '"{}"'.format(name[3:])

        if header_only:
            package_id = PACKAGE_ID_HEADERONLY_TEMPLATE

        with open(get_file_path(name, version), "w") as outfile:
            outfile.write(TEMPLATE.format(
                classname=classname, name=name, baseclass=baseclass, description=description,
                requirements=requires, build_requirements=build_requires, version=version,
                namespace=namespace, libs=libs, package_id=package_id))

        padding = 25 - len(str(version)) - len(str(name))
        if padding < 0:
            padding = 0

        if not builder_requires:
            builder_requires = "no deps"
        else:
            builder_requires = ", ".join(builder_requires)
        print('        manager.manage("{}", "{}"){}# {}'.format(name, version, " " * padding, builder_requires))

if __name__ == "__main__":
    main()

