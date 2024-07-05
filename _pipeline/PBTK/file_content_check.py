import pandas as pd
import gzip
from io import StringIO
import os
import re

from .data_validation import *
from .data_manipulation import *
from .file_manipulation import *

def get_size(start_path):
    """Calculate the total size of a directory."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size

def list_dir_contents(directory_path):
    """List contents of the directory along with their sizes."""
    if not os.path.isdir(directory_path):
        raise ValueError(f"{directory_path} is not a valid directory")

    contents = []

    # List subdirectories and their sizes
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):
            size = get_size(item_path)
            contents.append({'Type': 'Folder', 'Name': item, 'Size (Bytes)': size})
        elif os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            contents.append({'Type': 'File', 'Name': item, 'Size (Bytes)': size})

    return contents

def get_subdirectories(directory_path):
    """Get a list of subdirectories in the given directory."""
    if not os.path.isdir(directory_path):
        raise ValueError(f"{directory_path} is not a valid directory")

    subdirectories = [d for d in os.listdir(directory_path) 
                      if os.path.isdir(os.path.join(directory_path, d))]
    return subdirectories

def filt_list_regex(in_list, in_pattern):
    
    pattern = re.compile(in_pattern)

    # Filter the list
    filtered_list = [item for item in in_list if pattern.match(item)]
    return filtered_list


def file_content_check(in_dir, filt_pattern, out_file):
    #filt_pattern = '\d\d\d\d\d\d_[a-zA-Z]*'
    #filt_pattern: regex pattern to filter the desired subdirectories

    file_content_check_directory_path = in_dir  # Replace with your directory path
    in_pattern = filt_pattern
    
    subdirs_list = get_subdirectories(file_content_check_directory_path)
    subdirs_list = filt_list_regex(in_list = subdirs_list, in_pattern = in_pattern)
    
    print(subdirs_list)
    
    save_to_excel_dict = {}
    for dir_path in subdirs_list:
        print(dir_path)
        dir_path_contents = list_dir_contents(os.path.join(file_content_check_directory_path, dir_path))
        globals()[f"{dir_path}_df"] = pd.DataFrame(dir_path_contents)
        print(globals()[f"{dir_path}_df"])

        # Print total size of the directory
        globals()[f"{dir_path}_total_size"] = get_size(os.path.join(file_content_check_directory_path, dir_path))
        print("Total size of the directory (Bytes)", globals()[f"{dir_path}_total_size"])
        globals()[f"{dir_path}_df"]['Total Size'] = globals()[f"{dir_path}_total_size"]

        save_to_excel_dict[dir_path[:30]] = globals()[f"{dir_path}_df"]
    
    save_to_excel(out_file, save_to_excel_dict)
    return save_to_excel_dict


if __name__ == "__main__":
    pass