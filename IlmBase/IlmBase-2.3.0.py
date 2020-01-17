from conans import ConanFile, python_requires, tools
import os

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class IlmBase(pyreq.BaseConanFile):
    description = "IlmBase is a component of OpenEXR. OpenEXR is a high dynamic-range (HDR) image file format developed by Industrial Light & Magic for use in computer imaging applications."
    url = "https://www.openexr.com/"
    license = "BSD"
    name = "IlmBase"
    version = "2.3.0"

    settings = "os"

    def source(self):
        """Retrieve source code."""
        self.download(
            "https://github.com/AcademySoftwareFoundation/openexr/releases/download/v{}".format(self.version),
            directory="ilmbase-{}".format(self.version))

    def cmake_definitions(self):
        """Setup CMake definitions."""
        definition_dict = {
            "NAMESPACE_VERSIONING": False,
            "OPENEXR_BUILD_SHARED": self.options.shared,
            "OPENEXR_BUILD_STATIC": not self.options.shared
        }
        self.add_default_definitions(definition_dict)
        return definition_dict

    def build(self):
        arguments = ["--disable-namespaceversioning"]
        self.build_autotools(arguments)

    def package(self):
        """Assemble the package."""
        super(IlmBase, self).package()

        # move headers out of OpenEXR/
        with tools.chdir(os.path.join(self.package_folder, "include")):
            for header in [entry for entry in os.listdir("OpenEXR")]:
                os.rename(os.path.join("OpenEXR", header), header)
            pyreq.remove("OpenEXR")

        # fix pkg-config file
        with tools.chdir(os.path.join(self.package_folder, "lib", "pkgconfig")):
            tools.replace_in_file("IlmBase.pc", """include/OpenEXR""", "include")

    def package_info(self):
        """Edit package info."""
        self.cpp_info.libs = ["Imath, IexMath", "Half", "Iex", "IlmThread"]
        if self.settings.os == "Linux":
            self.cpp_info.cppflags = ["-pthread"]
        elif self.options.shared:
            self.cpp_info.defines.append("OPENEXR_DLL")
