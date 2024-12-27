"""
Realized by Davide Lisi, EPFL
Contact: davide.lisi@epfl.ch
"""

import subprocess
from pathlib import Path

def run_command(full_command, directory, show_cmd=False):
    """Runs a command in the terminal in a specified directory, optionally showing the command prompt.

    Args:
        full_command: The command to run. String
        directory: The directory where the command should be executed. String
        show_cmd: Whether to show the command prompt window (True/False). Defaults to False.

    Returns:
        The return code of the command.  Returns 1 if the directory is invalid or other errors occur.
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        print(f"Error: Invalid directory path: {directory}")
        return 1

    try:
        creationflags = 0  # Default: Don't show the window
        if show_cmd:
            creationflags = subprocess.CREATE_NEW_CONSOLE  # Show the window. This functionality right now does not work.

        process = subprocess.Popen(full_command, shell=True, cwd=str(dir_path), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creationflags)
        stdout, stderr = process.communicate()
        if stdout:
            print(f"Command output:\n{stdout}\n------------------------------------------")
        if stderr:
            print(f"Command error:\n{stderr}\n------------------------------------------")
        return process.returncode
    except FileNotFoundError:
        print("Command not found. Please check the command and your system's PATH environment variable.\n---------------------------------------------")
        return 1
    except Exception as e:
        print(f"An error occurred: {e}\n------------------------------------------")
        return 1
