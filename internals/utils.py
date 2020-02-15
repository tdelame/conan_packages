from contextlib import contextmanager
import subprocess
import shutil
import stat
import os

def execute_command(command, output_file_path):
    with open(output_file_path, "w") as outfile:
        process = subprocess.Popen(command, stdout=outfile, stderr=outfile, shell=True)
        process.communicate()
        return process.returncode == 0

@contextmanager
def current_directory(directory):
    previous_directory = os.getcwd()
    try:
        os.chdir(os.path.expanduser(directory))
        yield
    finally:
        os.chdir(previous_directory)

def make_symlink(source, destination):
    """Make a symbolic link from source to destination. If destination already exists, it will
    be removed.
    """
    remove(destination)
    os.symlink(source, destination)

def remove(path):
    """Remove a file or a directory. If the path does not exist, this function does nothing. If
    the path points to a non empty directory, this function remove the directory content as well
    as the directory itself.
    """
    if os.path.lexists(path):
        if os.path.islink(path):
            os.unlink(path)
        elif os.path.isdir(path):
            remove_directory(path)
        else:
            os.remove(path)

def __on_shutil_rmtree_error(func, path, exc_info):
    #pylint: disable=unused-argument
    os.chmod(path, stat.S_IWRITE)
    os.remove(path)

def make_directory(directory_path):
    """Create a directory if it does not exist. If the argument is None, this function does
    nothing.
    """
    if directory_path is not None and not os.path.exists(directory_path):
        os.makedirs(directory_path)

def remove_directory(directory_path):
    """Remove a directory, if it exists, as well as all of its content.
    """
    shutil.rmtree(directory_path, onerror=__on_shutil_rmtree_error)            