"""
Realized by Davide Lisi, EPFL
Contact: davide.lisi@epfl.ch
"""

import os
import shutil
import json
import csv

output_jsonfolder_settings = 'modifiedJSON'
output_bgifolder_settings = 'modifiedBGI'
output_unmodified_bgifolder_settings = 'unmodifiedBGI'
output_bgdfolder_settings = 'modifiedBGD'
output_unmodified_bgdfolder_settings = 'unmodifiedBGD'
output_simulation_folder = 'Simulations'


def save_json(output_jsonPath, data_dict):
    """
    Saves the dictionary into a JSON file.
    """
    os.chdir("D:\\")
    with open(output_jsonPath, 'w') as json_file:
        json.dump(data_dict, json_file, indent=4)
    return

def read_json_file(file_path):
    """
    Reads a JSON file and returns its content as a dictionary.
    
    :param file_path: Path to the JSON file.
    :return: Dictionary containing the JSON file content.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def read_txt_file(file_path):
    """
    Reads a text file and returns its content as a list of lines.
    
    :param file_path: Path to the text file.
    :return: List of lines from the text file.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines



def list_folders(directory_path):
    """
    Lists all folders inside the given directory.
    
    :param directory_path: Path to the directory.
    :return: List of folder names inside the directory.
    """
    return [name for name in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, name))]

def send_commands(process, commands):
    for command in commands:
        print(f'>>>  {command}')
        process.stdin.write(command + "\n")
        process.stdin.flush()

def read_output(process):
    while True:
        output_line = process.stdout.readline()
        if not output_line:
            break
        print(output_line.strip())

def list_elements(file_path):
# given a comma separated file at "file_path", the function retrieves all the elements contained and returns the first one of each line

    # Initialize an empty list to store the data
    data = []

    # Open the CSV file and read its content
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        
        # Iterate over each row in the CSV file
        for row in reader:
            data.append(row)
    
    res = []
    for row in data:
        res.append(row[0])

    return res

def append_text(template_file, new_file,trigger_strings, replacement_text):

    replacement_text = replacement_text+"\n"

    # Read the contents of the file
    with open(template_file, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    jump = False
    for line in lines:
        if(jump==False):
            flag = True
            for trigger_string in trigger_strings:
                if flag == True and line.rstrip().startswith(trigger_string):
                    modified_lines.append(trigger_string+replacement_text)
                    flag = False
                    jump = line.rstrip().endswith("\\")
            if flag == True:
                modified_lines.append(line)
        else:
            jump = False

    with open(new_file, 'w') as file:
        file.writelines(modified_lines)

def replace_text(template_file, new_file,trigger_strings, replacement_text):

    replacement_text = replacement_text+"\n"

    # Read the contents of the file
    with open(template_file, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    jump = False
    for line in lines:
        if(jump==False):
            flag = True
            for trigger_string in trigger_strings:
                if flag == True and line.rstrip().startswith(trigger_string):
                    modified_lines.append(replacement_text)
                    flag = False
                    jump = line.rstrip().endswith("\\")
            if flag == True:
                modified_lines.append(line)
        else:
            jump = False
    with open(new_file, 'w') as file:
        file.writelines(modified_lines)


def Create_Folder(Path):
    """Creates a new folder at the specified path.

    Args:
        Path: The path where the new folder should be created.

    Returns:
        True if the folder was created successfully, False otherwise.
    """
    try:
        os.makedirs(Path, exist_ok=True)  # exist_ok=True prevents error if folder already exists
        return True
    except OSError as e:
        print(f"Error creating folder: {e}")
        return False

def Copy_File(initial_position, final_position):
    """Copies a file from the initial position to the final position.

    Args:
        initial_position: The path of the file to be copied.
        final_position: The path where the file should be copied.

    Returns:
        True if the file was copied successfully, False otherwise.
    """
    try:
        shutil.copy2(initial_position, final_position) # copy2 preserves metadata
        return True
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return False
    except shutil.Error as e:
        print(f"Error copying file: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def Create_Project_Folder(Project_Name = "Database_Test_1",
                          Project_Folder = "D:\Davide",
                          default_geometry_path = 'defaultBGI\\LUS_General_OnlySpan0_Copy.bgi',
                          output_jsonfolder = output_jsonfolder_settings,
                          output_bgifolder = output_bgifolder_settings,
                          output_unmodified_bgifolder = output_unmodified_bgifolder_settings,
                          output_bgdfolder = output_bgdfolder_settings,
                          output_unmodified_bgdfolder = output_unmodified_bgdfolder_settings):
    
    Projec_Folder_path = f"{Project_Folder}\\{Project_Name}"
    Create_Folder(Projec_Folder_path)
    Create_Folder(f"{Projec_Folder_path}\\defaultBGI")
    Copy_File(default_geometry_path,f"{Projec_Folder_path}\\defaultBGI")
    Create_Folder(f"{Projec_Folder_path}\\{output_jsonfolder}")
    Create_Folder(f"{Projec_Folder_path}\\{output_bgifolder}")
    Create_Folder(f"{Projec_Folder_path}\\{output_unmodified_bgifolder}")
    Create_Folder(f"{Projec_Folder_path}\\{output_bgdfolder}")
    Create_Folder(f"{Projec_Folder_path}\\{output_unmodified_bgdfolder}")
    Create_Folder(f"{Projec_Folder_path}\\{output_simulation_folder}")

    return Projec_Folder_path

def copy_bgd_for_simulation(starting_path, final_path):
    """Lists all files in starting_path and copies .bgd files to final_path using Copy_File."""
    
    filenames = []

    if not os.path.exists(starting_path):
        print(f"Error: Starting path '{starting_path}' does not exist.")
        return

    if not os.path.exists(final_path):
        os.makedirs(final_path)

    for filename in os.listdir(starting_path):
        if filename.endswith(".bgd"):
            source_path = os.path.join(starting_path, filename)
            destination_path = os.path.join(final_path, filename)
            if Copy_File(source_path, destination_path):
                print(f"Copied '{filename}' to '{final_path}'")
                filenames.append(filename)

    names = [filename.removesuffix('.bgd') for filename in filenames]
    
    return names

