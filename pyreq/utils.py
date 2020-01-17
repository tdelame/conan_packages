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

def make_directory(directory_path):
    """Create a directory if it does not exist. If the argument is None, this function does
    nothing.
    """
    if directory_path is not None and not os.path.exists(directory_path):
        os.makedirs(directory_path)

def copy(source, destination):
    """Copy a file. If the destination directory does not exist, this function creates it."""
    make_directory(os.path.dirname(destination))
    if os.path.isdir(source):
        shutil.copytree(source, destination)
    else:
        shutil.copy(source, destination)