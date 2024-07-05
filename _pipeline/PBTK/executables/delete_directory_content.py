import os
import shutil
import argparse
import time

def delete_contents(dir_path):
    # Check if the directory exists
    if not os.path.exists(dir_path):
        print(f"The directory {dir_path} does not exist.")
        return

    # Iterate over each item in the directory
    for item_name in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item_name)
        try:
            # Check if it's a file or directory and remove accordingly
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
                print(f"Removed file: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Removed directory and its contents: {item_path}")
        except Exception as e:
            print(f"Error deleting {item_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Delete all folders and files in the specified directory.")
    parser.add_argument("dir_path", type=str, help="Path to the directory whose contents are to be deleted.")
    
    args = parser.parse_args()

    # Capture start time
    start_time = time.time()
    print(f"Process started at {time.ctime(start_time)}")

    delete_contents(args.dir_path)

    # Calculate and print the duration
    end_time = time.time()
    duration = end_time - start_time
    print(f"Process completed. Duration: {duration:.2f} seconds")

if __name__ == "__main__":
    main()
