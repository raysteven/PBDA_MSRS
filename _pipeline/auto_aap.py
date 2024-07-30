import sys
import os
import time

from PBTK import *
from json_create import json_create
from json_to_pdf import json_to_pdf
from utils.utils import zip_folder

import pandas as pd
from copy import deepcopy

aap_dir = os.path.join(os.getcwd(), 'assets','_results','Amino_Acid_Panel','Final_Report')

db_path = os.path.join(os.getcwd(),'database_aap_v1.1.0.csv')
#print("=====> DB PATH:",db_path)

def result_csv_create(aap_dir, runfolder, report_df):
    report_df = deepcopy(report_df)
    report_df = report_df[['lab_number','nama','usia','gender','ref_number','ASP','SER','GLN','GLY','CYS','THR','CIT','GLU','ALA','PRO','ORN','HIS','LYS','ARG','VAL','MET','TYR','ILE','LEU','PHE','TRP']]
    report_df = report_df.rename(columns={'lab_number':'No Lab','nama':'Nama','usia':'Usia','gender':'Jenis Kelamin','ref_number':'Pengirim'})
    report_df.index = report_df.index + 1
    report_df.index.name = "No"
    report_df.to_csv(f'{aap_dir}/{runfolder}/Result_AminoAcidPanel_{runfolder}.csv', index=True)


def auto_aap(runfolder,sample_sheet_path, result_sheet_path):
    print('auto_aap: Defining stuffs')
    aap_db = loadDF(file_path=db_path, file_type='csv')
    
    aap_db = aap_db.set_index('acronym')
    aap_db

    sample_sheet = loadDF(file_path=sample_sheet_path, file_type='csv')
    sample_sheet


    print('auto_aap: Creating DFs')
    #Load the result sheet using PBTK loadDF
    print('auto_aap: Load DFs')
    result_sheet = loadDF(file_path=result_sheet_path, file_type='xlsx', sheet_name='Sheet1')

    print('auto_aap: col_len_index')
    # Assuming `df` is your DataFrame and `n` is the index of the column you want to switch
    col_len_index = len(result_sheet.columns)  # Example column index

    print('auto_aap: loop col_len_index')
    for n in range(8,col_len_index):
    # Step 1: Get the value from the first row for the column at index `n`
        current_column_label = result_sheet.columns[n]
        result_sheet.iloc[0, n] = current_column_label
        result_sheet.columns.values[n] = result_sheet.iloc[0, n] 
        # Optional Step 3: Remov
    result_sheet
    
    print('auto_aap: drop col result_sheet')
    #Drop the first two columns that are empty
    result_sheet = result_sheet.drop(result_sheet.columns[[0, 1]], axis=1)

    print('auto_aap: new header result_sheet')
    #Switch the column names with the first row
    new_header = result_sheet.iloc[0]  # Grab the first row for the header
    result_sheet.columns = new_header  # Set the first row as the header
    result_sheet = result_sheet[1:]  # Take the data less the header row

    print('auto_aap: reset_index result_sheet')
    #Reset the index
    result_sheet.reset_index(drop=True, inplace=True)

    print('auto_aap: change_name result_sheet')
    #Change "Name" column to "patient_id"
    result_sheet.rename(columns={'Name':'patient_id'}, inplace=True)

    print('auto_aap: remove result')
    #Remove "Result" in column name
    for column_name in result_sheet.columns:
        if 'Results' in column_name:
            new_column_name = column_name.replace('Results', '').replace(" ",'')  # Remove 'Results' from column name
            result_sheet.rename(columns={column_name: new_column_name}, inplace=True)
    result_sheet

    print('auto_aap: report_df')

    report_df = pd.merge(sample_sheet, result_sheet, on='patient_id', how='inner')
    report_df

    runfolder_dir = os.path.join(aap_dir, runfolder)

    

    print('auto_aap: Result CSV')
    result_csv_create(aap_dir, runfolder, report_df)

    print('auto_aap: JSON Create')
    json_create(report_df=report_df, ref_db=aap_db, runfolder=runfolder, workdir=aap_dir)

    print('auto_aap: JSON PDF')
    json_to_pdf(report_df=report_df, runfolder=runfolder,workdir=aap_dir)

    print('auto_aap: Zip Folder')
    zip_folder(runfolder_dir, os.path.join(aap_dir,f"{runfolder.replace(' ','_')}.zip"))