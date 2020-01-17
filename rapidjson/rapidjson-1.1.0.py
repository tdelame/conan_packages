import os
from conans import ConanFile, python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class rapidjson(ConanFile):
    description = "fast JSON parser/generator for C++ with both SAX/DOM style API"
    url = "https://github.com/Tencent/rapidjson"
    license = "MIT"
    version = "1.1.0"
    name = "rapidjson"

    _source_subfolder = "source_subfolder"
    
    def source(self):
        """Retrieve source code."""
        # the 1.1.0 release on github miss the files we used to include.
        sha = "dfbe1db9da455552f7a9ad5d2aea17dd9d832ac1"
        url = "{}/archive/{}.zip".format(self.url, sha)
        tools.get(url)
        os.rename("{}-{}".format(self.name, sha), self._source_subfolder)

    def package(self):
        """Assemble the package."""
        pyreq.make_directory("licenses")
        pyreq.copy(
            os.path.join(self.build_folder, self._source_subfolder, "include"),
            os.path.join(self.package_folder, "include"))
        pyreq.copy(
            os.path.join(self.build_folder, self._source_subfolder, "license.txt"),
            os.path.join(self.package_folder, "licenses", "LICENSE"))
        
    def package_id(self):
        self.info.header_only()
