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
