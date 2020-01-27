from conans import python_requires, tools
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

CMAKE_CONTENT = """
project(sqlite3 C)

add_library(sqlite3 sqlite3.c sqlite3.h sqlite3ext.h)

if(WIN32 AND MSVC AND BUILD_SHARED_LIBS)
    set_target_properties(sqlite3 PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
endif()

target_compile_definitions(sqlite3
    PRIVATE
        SQLITE_ENABLE_JSON1
        SQLITE_ENABLE_COLUMN_METADATA
        SQLITE_ENABLE_FTS3
        SQLITE_ENABLE_FTS4
        SQLITE_ENABLE_FTS5
        SQLITE_ENABLE_RTREE
        HAVE_FDATASYNC
)

if(NOT WIN32)
    target_compile_definitions(sqlite3 
        PRIVATE 
            HAVE_GMTIME_R 
            HAVE_LOCALTIME_R 
            HAVE_POSIX_FALLOCATE 
            HAVE_STRERROR_R 
            HAVE_USLEEP
    )

    target_link_libraries(sqlite3 m)
endif()

install( TARGETS sqlite3
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib)

install( DIRECTORY "." DESTINATION include FILES_MATCHING PATTERN "*.h")
"""

class sqlite3(pyreq.CMakeConanFile):
    description = "Self-contained, serverless, in-process SQL database engine."
    homepage = "https://www.sqlite.org"
    license = "Public Domain"
    version = "3.30.1"
    name = "sqlite3"

    settings = "os"

    def source(self):
        """Retrieve source code."""
        directory = "sqlite-amalgamation-3300100"
        self.download("https://www.sqlite.org/2019", directory=directory, compression="zip")
        with tools.chdir(self._source_subfolder):
            with open("CMakeLists.txt", "w") as outfile:
                outfile.write(CMAKE_CONTENT)

    def cmake_definitions(self):
        """Configure cmake build."""
        definitions_dict = {}
        self.add_default_definitions(definitions_dict)
        return definitions_dict

    def package_info(self):
        """Edit package info."""
        super(sqlite3, self).package_info()
        self.cpp_info.libs = ["sqlite3"]
        self.cpp_info.system_libs = ["m"]
