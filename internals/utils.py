from contextlib import contextmanager
import subprocess
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