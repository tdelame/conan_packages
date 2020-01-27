from contextlib import contextmanager
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

@contextmanager
def change_current_directory(directory_path):
    old_current_directory = os.getcwd()
    os.chdir(directory_path)
    try:
        yield
    finally:
        os.chdir(old_current_directory)

def executable_in_directory(directory_path):
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return False

    with change_current_directory(directory_path):
        for filename in [entry for entry in os.listdir(".") if os.path.isfile(entry)]:
            if os.access(filename, os.X_OK):
                return True
    return False


def library_in_directory(directory_path):
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return False

    with change_current_directory(directory_path):
        patterns = [".so", ".a"] if os.name != "nt" else [".dll", ".lib"]
        for filename in [entry for entry in os.listdir(".") if os.path.isfile(entry)]:
            for pattern in patterns:
                if filename.endswith(pattern):
                    return True
    return False