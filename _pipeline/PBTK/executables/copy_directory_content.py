import os
import shutil
import sys
import re
import argparse
import time
from datetime import datetime, timedelta


def copy_directory_contents(source_dir, destination_dir, reverse_alphabetical=False, folder_filter=None):
    try:
        pattern = re.compile(folder_filter) if folder_filter else None

        for root, dirs, files in os.walk(source_dir):
            # Get the relative path from the source directory
            relative_dir_path = os.path.relpath(root, source_dir)

            # Apply the regex filter only at the first level
            if relative_dir_path == '.':
                # We are in the source directory, filter its immediate subdirectories
                if pattern:
                    dirs[:] = [d for d in dirs if pattern.search(d)]

            if reverse_alphabetical:
                dirs.sort(reverse=True)
                files.sort(reverse=True)

            # Copy files from this directory
            for file in files:
                source_file = os.path.join(root, file)
                relative_file_path = os.path.relpath(source_file, source_dir)
                destination_file = os.path.join(destination_dir, relative_file_path)

                # Ensure the destination directory structure exists
                os.makedirs(os.path.dirname(destination_file), exist_ok=True)

                # Check if the file already exists in the destination directory
                if os.path.exists(destination_file):
                    # Check if the file sizes match
                    if os.path.getsize(source_file) == os.path.getsize(destination_file):
                        print(f"Skipped (already exists with the same size): {source_file} -> {destination_file}")
                        continue  # Skip if the file already exists with the same size

                # Copy the file
                print(f"Processing: {source_file}")
                shutil.copy2(source_file, destination_file)
                print(f"Copied: {source_file} -> {destination_file}")

        print("Copy completed successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("PBTK: Copy Directory Content \nCreated by Ray Steven (2024)")
    parser = argparse.ArgumentParser(description='Copy contents of a directory with various options.')

    parser.add_argument('--source', '-s', required=True, help='Source directory path')
    parser.add_argument('--destination', '-d', required=True, help='Destination directory path')
    parser.add_argument('--reverse', '-r', action='store_true', help='Reverse the order of files and directories alphabetically')
    parser.add_argument('--filter', '-f', help='Regex pattern to filter directories')

    args = parser.parse_args()
    # Record the start time
    start_time = time.time()
    start_date = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Start Date: {start_date}") 

    copy_directory_contents(
        source_dir=args.source,
        destination_dir=args.destination,
        reverse_alphabetical=args.reverse,
        folder_filter=args.filter
    )

    # Record the end time
    end_time = time.time()

    # Calculate the duration
    duration_seconds = end_time - start_time
    duration_timedelta = timedelta(seconds=duration_seconds)

    # Format the start and end date for better readability
    start_date = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    end_date = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')

    # Print the start date, end date, and duration in days, hours, minutes, and seconds
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")
    print("Duration: {} days, {} hours, {} minutes, {} seconds".format(
        duration_timedelta.days,
        duration_timedelta.seconds // 3600,
        (duration_timedelta.seconds // 60) % 60,
        duration_timedelta.seconds % 60
    ))