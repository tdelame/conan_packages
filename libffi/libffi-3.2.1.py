import os
import shutil
from glob import glob
from conans import tools, python_requires
pyreq = python_requires("pyreq/1.0.0@tdelame/stable")

class Libffi(pyreq.BaseConanFile):
    description = "portable, high level programming interface to various calling conventions"
    url = "https://sourceware.org/libffi/"
    license = "MIT"
    settings = "os", "compiler"

    name = "libffi"
    version = "3.2.1"

    def config_options(self):
        """Executed before the actual assignment of options. Use it to configure or constrain
        the available options in a package. You can read values of self.settings but you cannot
        read values of self.options."""        
        if self.settings.os != "Linux":
            raise RuntimeError("libffi recipe is not available yet for your OS")

        self._compiler = self.settings.compiler
        self._compiler_version = self.settings.compiler.version
        del self.settings.compiler

    def source(self):
        """Retrieve source code and patch it"""
        self.download("https://sourceware.org/pub/libffi")

        # adapted from here https://github.com/conan-io/conan-center-index/blob/master/recipes/libffi/all/conanfile.py
        configure_path = os.path.join(self._source_subfolder, "configure")
        tools.replace_in_file(configure_path,
                              "LIBTOOL='$(SHELL) $(top_builddir)/libtool'\n",
                              "LIBTOOL='$(SHELL) $(top_builddir)/libtool.sh'\n")
        tools.replace_in_file(configure_path,
                              "ofile=libtool\n",
                              "ofile=libtool.sh\n")

        tools.replace_in_file(os.path.join(self._source_subfolder, "src", "x86", "win64.S"),
                              "jmp\tSHORT",
                              "jmp")

        ffi_extern_src = "/* Need minimal decorations for DLLs to works on Windows. */\n" \
                         "/* GCC has autoimport and autoexport.  Rely on Libtool to */\n" \
                         "/* help MSVC export from a DLL, but always declare data   */\n" \
                         "/* to be imported for MSVC clients.  This costs an extra  */\n" \
                         "/* indirection for MSVC clients using the static version  */\n" \
                         "/* of the library, but don't worry about that.  Besides,  */\n" \
                         "/* as a workaround, they can define FFI_BUILDING if they  */\n" \
                         "/* *know* they are going to link with the static library. */\n" \
                         "#if defined _MSC_VER && !defined FFI_BUILDING\n" \
                         "#define FFI_EXTERN extern __declspec(dllimport)\n" \
                         "#else\n" \
                         "#define FFI_EXTERN extern\n" \
                         "#endif\n" \
                         "\n"
        ffi_extern_dst = "#if defined _MSC_VER\n" \
                         "#  if !defined FFI_STATIC\n" \
                         "#    if defined FFI_BUILDING\n" \
                         "#      define FFI_EXTERN __declspec(dllexport)\n" \
                         "#    else\n" \
                         "#      define FFI_EXTERN __declspec(dllimport)\n" \
                         "#    endif\n" \
                         "#  else\n" \
                         "#      define FFI_EXTERN extern\n" \
                         "#  endif\n" \
                         "#else\n" \
                         "#  define FFI_EXTERN extern\n" \
                         "#endif\n"

        ffi_h_in = os.path.join(self._source_subfolder, "include", "ffi.h.in")
        tools.replace_in_file(ffi_h_in, ffi_extern_src, "")
        tools.replace_in_file(ffi_h_in,
                              "#include <ffitarget.h>\n",
                              "#include <ffitarget.h>\n" \
                              "\n" \
                              "{}".format(ffi_extern_dst))

        functions = [
            "ffi_status ffi_prep_cif_core(",
            "void ffi_raw_call (",
            "void ffi_ptrarray_to_raw (",
            "void ffi_raw_to_ptrarray (",
            "size_t ffi_raw_size (",
            "void ffi_java_raw_call (",
            "void ffi_java_ptrarray_to_raw (",
            "void ffi_java_raw_to_ptrarray (",
            "size_t ffi_java_raw_size (",
            "void *ffi_closure_alloc (",
            "void ffi_closure_free (",
            "ffi_status\nffi_prep_closure (",
            "ffi_status\nffi_prep_closure_loc (",
            "ffi_status\nffi_prep_raw_closure (",
            "ffi_status\nffi_prep_raw_closure_loc (",
            "ffi_status\nffi_prep_java_raw_closure (",
            "ffi_status\nffi_prep_java_raw_closure_loc (",
            "ffi_status ffi_prep_cif(",
            "ffi_status ffi_prep_cif_var(",
            "void ffi_call(",
        ]

        for function in functions:
            tools.replace_in_file(ffi_h_in,
                                  function,
                                  "FFI_EXTERN {}".format(function))

        types_c_src = os.path.join(self._source_subfolder, "src", "types.c")
        tools.replace_in_file(types_c_src,
                              "#include <ffi_common.h>",
                              "#include <ffi_common.h>\n"
                              "\n"
                              "#include <complex.h>")
        tools.replace_in_file(types_c_src,
                              "FFI_COMPLEX_TYPEDEF(name, type, maybe_const)",
                              "FFI_COMPLEX_TYPEDEF(name, complex_type, maybe_const)")
        tools.replace_in_file(types_c_src,
                              "_Complex type",
                              "complex_type")
        tools.replace_in_file(types_c_src,
                              "#ifdef FFI_TARGET_HAS_COMPLEX_TYPE",
                              "#ifdef _MSC_VER"
                              "\n#  define FLOAT_COMPLEX _C_float_complex"
                              "\n#  define DOUBLE_COMPLEX _C_double_complex"
                              "\n#  define LDOUBLE_COMPLEX _C_ldouble_complex"
                              "\n#else"
                              "\n#  define FLOAT_COMPLEX float _Complex"
                              "\n#  define DOUBLE_COMPLEX double _Complex"
                              "\n#  define LDOUBLE_COMPLEX long double _Complex"
                              "\n#endif"
                              "\n"
                              "\n#ifdef FFI_TARGET_HAS_COMPLEX_TYPE")
        tools.replace_in_file(types_c_src,
                              "FFI_COMPLEX_TYPEDEF(float, float, const)",
                              "FFI_COMPLEX_TYPEDEF(float, FLOAT_COMPLEX, const)")
        tools.replace_in_file(types_c_src,
                              "FFI_COMPLEX_TYPEDEF(double, double, const)",
                              "FFI_COMPLEX_TYPEDEF(double, DOUBLE_COMPLEX, const)")
        tools.replace_in_file(types_c_src,
                              "FFI_COMPLEX_TYPEDEF(longdouble, long double, FFI_LDBL_CONST)",
                              "FFI_COMPLEX_TYPEDEF(longdouble, LDOUBLE_COMPLEX, FFI_LDBL_CONST)")
        if self.settings.os == "Macos":
            tools.replace_in_file(configure_path, r"-install_name \$rpath/", "-install_name ")

        if self._compiler == "clang" and float(str(self._compiler_version)) >= 7.0:
            # https://android.googlesource.com/platform/external/libffi/+/ca22c3cb49a8cca299828c5ffad6fcfa76fdfa77
            sysv_s_src = os.path.join(self._source_subfolder, "src", "arm", "sysv.S")
            tools.replace_in_file(sysv_s_src, "fldmiad", "vldmia")
            tools.replace_in_file(sysv_s_src, "fstmiad", "vstmia")
            tools.replace_in_file(sysv_s_src, "fstmfdd\tsp!,", "vpush")

            # https://android.googlesource.com/platform/external/libffi/+/7748bd0e4a8f7d7c67b2867a3afdd92420e95a9f
            tools.replace_in_file(sysv_s_src, "stmeqia", "stmiaeq")
                
    def _get_auto_tools(self):
        return AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

    def build(self):
        arguments = [ "--disable-debug"]
        self.build_autotools(arguments)

    def package_info(self):
        self.cpp_info.includedirs = [os.path.join("lib", "{}-{}".format(self.name, self.version), "include")]
        if not self.options.shared:
            self.cpp_info.defines += ["FFI_STATIC"]
        self.cpp_info.libs = ["ffi"]