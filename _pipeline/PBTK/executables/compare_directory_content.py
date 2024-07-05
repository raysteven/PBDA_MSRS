import os
import shutil
import sys
import re
import argparse
import time
from datetime import datetime, timedelta
import pandas as pd

sys.path.insert(0, 'W:\Bioinfo_Applications')
sys.path.insert(0, '/mnt/mol/Bioinfo_Applications')

from PBTK import *

#from ..data_validation import *
#from ..data_manipulation import *
#from ..file_manipulation import *
#from ..file_content_check import *


def compare_directory_contents(first_dir, second_dir, outdir, filt_pattern):
    filt_pattern = filt_pattern
    
    in_dir1 = first_dir
    name_dir1 = 'dir1'
    out_dir1 = os.path.join(outdir,os.path.basename(os.path.normpath(first_dir))+f'{name_dir1}contents.xlsx')

    in_dir2 = second_dir
    name_dir2 = 'dir2'
    out_dir2 = os.path.join(outdir,os.path.basename(os.path.normpath(second_dir))+f'{name_dir2}contents.xlsx')   

    file_content_check(in_dir1, filt_pattern, out_dir1)
    file_content_check(in_dir2, filt_pattern, out_dir2)

    file1_contents_df = loadDF(file_path=out_dir1)
    file2_contents_df = loadDF(file_path=out_dir2)

    sheet_name_list_1 = sheet_name_list(file_path=out_dir1)
    sheet_name_list_2 = sheet_name_list(file_path=out_dir2)

    save_to_excel_dict = {}

    list1 = sheet_name_list_1
    list2 = sheet_name_list_2

    # Find common elements
    common_elements = list(set(list1) & set(list2))

    # Find unique elements in each list
    unique_list1 = list(set(list1) - set(common_elements))
    unique_list2 = list(set(list2) - set(common_elements))

    # Ensure all lists have the same length by filling missing values with None
    max_length = max(len(common_elements), len(unique_list1), len(unique_list2))
    common_elements += [None] * (max_length - len(common_elements))
    unique_list1 += [None] * (max_length - len(unique_list1))
    unique_list2 += [None] * (max_length - len(unique_list2))

    # Create a DataFrame
    comparing_data_df = {'Common Elements': common_elements, f'Unique Elements in {name_dir1}': unique_list1, f'Unique Elements in {name_dir2}': unique_list2}
    common_and_unique_df = pd.DataFrame(comparing_data_df)

    save_to_excel_dict['compare_elements'] = common_and_unique_df

    def count_pattern_in_column(column):
        return column.str.contains("<NE>", case=False).sum()

    NE_counter = {}

    for elem in common_and_unique_df['Common Elements']:
        if type(elem) == str:
                globals()[f"{elem}_df_{name_dir1}"] = loadDF(file_path=out_dir1,file_type='xlsx',sheet_name=elem)
                globals()[f"{elem}_df_{name_dir2}"] = loadDF(file_path=out_dir2,file_type='xlsx',sheet_name=elem)
                globals()[f"{elem}_df_{name_dir1}"] = globals()[f"{elem}_df_{name_dir1}"].set_index('Unnamed: 0')
                globals()[f"{elem}_df_{name_dir2}"] = globals()[f"{elem}_df_{name_dir2}"].set_index('Unnamed: 0')

                globals()[f"{elem}_cross_validate_df"] = data_validation(A=globals()[f"{elem}_df_{name_dir1}"],B=globals()[f"{elem}_df_{name_dir2}"])

                globals()[f"{elem}_cross_validate_df_count_result"] = globals()[f"{elem}_cross_validate_df"].apply(count_pattern_in_column)
                NE_counter[elem] = pd.DataFrame(globals()[f"{elem}_cross_validate_df_count_result"])
                
                save_to_excel_dict[elem] = globals()[f"{elem}_cross_validate_df"]

    NE_counter_df = pd.DataFrame(list(NE_counter.items()), columns=['Sheet', 'NE count'])

    save_to_excel_dict_final = {}
    save_to_excel_dict_final['NE count'] = NE_counter_df
    save_to_excel_dict_final.update(save_to_excel_dict)

    save_to_excel(file_name=os.path.join(outdir,'file_check_content_cross_validate.xlsx'), dfs=save_to_excel_dict_final)


if __name__ == "__main__":
    print("PBTK: Compare Directory Content \nCreated by Ray Steven (2024)")
    parser = argparse.ArgumentParser(description='Compare contents of two directories.')

    parser.add_argument('--first', '-1', required=True, help='First directory path')
    parser.add_argument('--second', '-2', required=True, help='Second directory path')
    parser.add_argument('--outdir', '-o', required=True, help='The output directory for the report')
    parser.add_argument('--filter', '-f', help='Regex pattern to filter directories', default='.')

    args = parser.parse_args()
    # Record the start time
    start_time = time.time()
    start_date = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Start Date: {start_date}") 

    compare_directory_contents(
        first_dir=args.first,
        second_dir=args.second,
        outdir=args.outdir,
        filt_pattern=args.filter
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