import subprocess
import sys

def run_program(program_path, args=None):
    """ run program runs a program as it is called from commandline
    """
    if args is None:
        args = []
    default_args = [sys.executable, program_path]
    process = subprocess.Popen(
        default_args + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return (stdout, stderr, process.returncode)
