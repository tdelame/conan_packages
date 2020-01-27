from conans import python_requires

pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class LibSndFile(pyreq.BaseConanFile):
    description = "C library for reading and writing files containing samples audio data"
    url = "http://www.mega-nerd.com/libsndfile/"
    license = "LGPL"
    name = "libsndfile"
    version = "1.0.28"
    settings = "os", "build_type"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""        
        if self.settings.os == "Windows":
            raise RuntimeError("This recipe is not available yet on Windows. Use libsndfile/1.0.29 instead")

    def source(self):
        """Retrieve source code."""
        self.download("{}/files".format(self.url))

    def build(self):
        """Build elements to package."""
        arguments = [
            "--disable-sqlite",
            # no FLAC, Ogg and Vorbis since we do not have requests nor requirements for these formats
            "--disable-external-libs"
        ]
        self.build_autotools(arguments)

    def package_info(self):
        """Edit package info."""
        super(LibSndFile, self).package_info()
        self.cpp_info.libs = ["sndfile"]
