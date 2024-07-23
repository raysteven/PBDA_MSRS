import sys
import os
workdir = os.getcwd()
from PBTK import *
from json_create import json_create
from json_to_pdf import json_to_pdf
from utils.utils import zip_folder

import pandas as pd
from copy import deepcopy

db_path = os.path.join(workdir,'database_aap_v1.1.0.csv')
#print("=====> DB PATH:",db_path)


def result_csv_create(wokdir_parent_directory, runfolder, report_df):
    report_df = deepcopy(report_df)
    report_df = report_df[['lab_number','nama','usia','gender','ref_number','ASP','SER','GLN','GLY','CYS','THR','CIT','GLU','ALA','PRO','ORN','HIS','LYS','ARG','VAL','MET','TYR','ILE','LEU','PHE','TRP']]
    report_df = report_df.rename(columns={'lab_number':'No Lab','nama':'Nama','usia':'Usia','gender':'Jenis Kelamin','ref_number':'Pengirim'})
    report_df.index = report_df.index + 1
    report_df.index.name = "No"
    report_df.to_csv(f'{wokdir_parent_directory}/{runfolder}/Result_AminoAcidPanel_{runfolder}.csv', index=True)


def get_parent_directory(path):
    return os.path.abspath(os.path.join(path, os.pardir))

def auto_aap(runfolder,sample_sheet_path, result_sheet_path):
    aap_db = loadDF(file_path=db_path, file_type='csv')
    
    aap_db = aap_db.set_index('acronym')
    aap_db

    sample_sheet = loadDF(file_path=sample_sheet_path, file_type='csv')
    sample_sheet

    #Load the result sheet using PBTK loadDF
    result_sheet = loadDF(file_path=result_sheet_path, file_type='xlsx', sheet_name='Sheet1')

    # Assuming `df` is your DataFrame and `n` is the index of the column you want to switch
    col_len_index = len(result_sheet.columns)  # Example column index

    for n in range(8,col_len_index):
    # Step 1: Get the value from the first row for the column at index `n`
        current_column_label = result_sheet.columns[n]
        result_sheet.iloc[0, n] = current_column_label
        result_sheet.columns.values[n] = result_sheet.iloc[0, n] 
        # Optional Step 3: Remov
    result_sheet
    
    #Drop the first two columns that are empty
    result_sheet = result_sheet.drop(result_sheet.columns[[0, 1]], axis=1)

    #Switch the column names with the first row
    new_header = result_sheet.iloc[0]  # Grab the first row for the header
    result_sheet.columns = new_header  # Set the first row as the header
    result_sheet = result_sheet[1:]  # Take the data less the header row

    #Reset the index
    result_sheet.reset_index(drop=True, inplace=True)

    #Change "Name" column to "patient_id"
    result_sheet.rename(columns={'Name':'patient_id'}, inplace=True)

    #Remove "Result" in column name
    for column_name in result_sheet.columns:
        if 'Results' in column_name:
            new_column_name = column_name.replace('Results', '').replace(" ",'')  # Remove 'Results' from column name
            result_sheet.rename(columns={column_name: new_column_name}, inplace=True)
    result_sheet

    report_df = pd.merge(sample_sheet, result_sheet, on='patient_id', how='inner')
    report_df

    wokdir_parent_directory = get_parent_directory(workdir)
    print(wokdir_parent_directory)
    runfolder_dir = os.path.join(wokdir_parent_directory, runfolder)
    print(runfolder_dir)

    result_csv_create(wokdir_parent_directory, runfolder, report_df)
    json_create(report_df=report_df, ref_db=aap_db, runfolder=runfolder, workdir=workdir)
    json_to_pdf(report_df=report_df, runfolder=runfolder,workdir=workdir)

    zip_folder(runfolder_dir, os.path.join(wokdir_parent_directory,'_zips',f"{runfolder}.zip"))