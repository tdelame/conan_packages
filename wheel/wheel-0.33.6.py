import os
from conans import ConanFile, tools

class wheel(ConanFile):

    python_shebang = "#!/usr/bin/env python3.7\n"
    license = "MIT"
    settings = "os"
    name = "wheel"
    version = "0.33.6"

    def requirements(self):
        """Define runtime requirements."""
        self.requires("cpython/3.7.5@tdelame/stable")

    def build(self):
        """Build the elements to package."""
        command = "python -m pip install {name}=={version} --target={package_folder}".format(
            name=self.name,
            version=self.version,
            package_folder=self.package_folder)
        self.run(command)

    def package(self):
        """Assemble the package."""

        # fix shebangs
        bin_directory = os.path.join(self.package_folder, "bin")
        if os.path.exists(bin_directory):
            with tools.chdir(bin_directory):
                for filename in [entry for entry in os.listdir(".") if os.path.isfile(entry)]:
                    with open(filename, "r") as infile:
                        lines = infile.readlines()
                    
                    if len(lines[0]) > 2 and lines[0].startswith("#!"):
                        lines[0] = self.python_shebang
                        with open(filename, "w") as outfile:
                            outfile.writelines(lines)
    
    def package_info(self):
        """Edit package info."""
        self.env_info.PYTHONPATH.append(self.package_folder)
        
        bin_directory = os.path.join(self.package_folder, "bin")
        if os.path.exists(bin_directory):
            self.env_info.PATH.append(bin_directory)

