import os
import csv
import math
import argparse
import time

def setup_logging(output_file):
    """Set up a simple logging system that writes to a file."""
    log_file = output_file.replace('.csv', '.log')
    def log_message(message):
        with open(log_file, 'a') as f:
            f.write(message + '\n')
    return log_message

def convert_size(size_bytes):
    """Convert size in bytes to a more readable format (KB, MB, GB, TB)."""
    if size_bytes == 0:
        return "0B"
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    size = round(size_bytes / p, 2)
    return f"{size} {size_names[i]}"

def get_size(start_path, log):
    """Recursively get the size of a directory."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        log(f"Processing: {dirpath}")
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size

def get_all_sizes(start_path, log):
    """Get sizes of all folders and files starting from a directory."""
    all_sizes = []
    for dirpath, dirnames, filenames in os.walk(start_path):
        log(f"Calculating size for: {dirpath}")
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                all_sizes.append((fp, os.path.getsize(fp), convert_size(os.path.getsize(fp))))
        all_sizes.append((dirpath, get_size(dirpath, log), convert_size(get_size(dirpath, log))))
    return all_sizes

def save_to_csv(data, output_file):
    """Save the list of file and directory sizes to a CSV file."""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Path', 'Size (Bytes)', 'Readable Size'])
        csvwriter.writerows(data)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Description: \nGenerate a report of file and folder sizes.')
    parser.add_argument('directory', type=str, help='Directory to scan')
    default_output = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sizes.csv')
    parser.add_argument('--output', type=str, default=default_output, help='Output CSV file path and name')
    return parser.parse_args()

def main():
    print("PBTK: List Directory Content \nCreated by Ray Steven (2024)")
    args = parse_arguments()
    log = setup_logging(args.output)
    start_time = time.time()
    log("Start scanning...")
    all_sizes = get_all_sizes(args.directory, log)
    sorted_sizes = sorted(all_sizes, key=lambda x: x[1], reverse=True)
    save_to_csv(sorted_sizes, args.output)
    elapsed_time = time.time() - start_time
    log_message = f"Sizes saved to {args.output}. Elapsed time: {elapsed_time:.2f} seconds"
    print(log_message)
    log(log_message)

if __name__ == "__main__":
    main()
