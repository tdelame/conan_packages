import subprocess

def execute_command(command, output_file_path):
    with open(output_file_path, "w") as outfile:
        process = subprocess.Popen(command, stdout=outfile, stderr=outfile, shell=True)
        process.communicate()
        return process.returncode == 0
