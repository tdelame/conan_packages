import shutil
import os

def remove(*paths):
    """Remove file or directory without failing.
    :param paths: path of file or directory to remove.
    """
    for path in paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

def set_executable_bit(file_path):
    """Set the executable bit of a file on Linux.
    :param file_path: str, path to the file."""
    if os.name == "posix":
        os.chmod(file_path, os.stat(file_path).st_mode | 0o111)
