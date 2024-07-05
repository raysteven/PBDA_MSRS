import os
from PBTK import *

def lkj_to_metadata(lkj_file_path):
    lkj_df = loadDF(lkj_file_path)
    #lkj_df
    lkj_df = lkj_df[['Unnamed: 1', 'Unnamed: 3', 'Unnamed: 7', 'Unnamed: 8', 'LEMBAR KERJA']]
    lkj_df = lkj_df.rename(columns={
                            'Unnamed: 1':'lab_number',
                            'Unnamed: 3':'name_dob',
                            'Unnamed: 7':'gender_test_name',
                            'Unnamed: 8':'age',
                            'LEMBAR KERJA':'ref_number'
                            })
    
    bottom_border_index = -2
    while True:
        test_list = [str(x) for x in (lkj_df.iloc[bottom_border_index].notnull())]
        if 'True' in test_list:
            bottom_border_index -= 1
        else:
            break

    lkj_df = lkj_df.iloc[6:bottom_border_index]
    lkj_df = lkj_df.dropna(how='all')
    #lkj_lab_number = zip(lkj_df['lab_number'])
    lkj_lab_number = lkj_df['lab_number'].dropna().tolist()

    lkj_name_dob = lkj_df['name_dob'].dropna().tolist()
    lkj_name = [s.strip() for s in lkj_name_dob[0::2]]
    lkj_dob = lkj_name_dob[1::2]

    lkj_gender_test_name = lkj_df['gender_test_name'].dropna().tolist()
    lkj_gender = lkj_gender_test_name[0::2]
    lkj_test_name = lkj_gender_test_name[1::2]

    lkj_age = lkj_df['age'].dropna().tolist()
    lkj_ref_number = lkj_df['ref_number'].dropna().tolist()

    lkj_df_cleaned = pd.DataFrame({
                                'lab_number':lkj_lab_number,
                                'nama':lkj_name,
                                'dob':lkj_dob,
                                'gender':lkj_gender,
                                'test_name':lkj_test_name,
                                'usia':lkj_age,
                                'ref_number':lkj_ref_number
                                })
    lkj_df_cleaned['patient_id'] = lkj_df_cleaned['lab_number'] + '-' + lkj_df_cleaned['ref_number']

    #moving the patient_id column into the first one (for convenient display purposes)
    lkj_df_cleaned = lkj_df_cleaned[['patient_id'] + [col for col in lkj_df_cleaned.columns if col != 'patient_id']]

    #only create metadata for Amino Profile 21
    lkj_df_cleaned = lkj_df_cleaned[lkj_df_cleaned['test_name'] == 'Aspartic Acid (ASP)-Amino Profile-21']
    return lkj_df_cleaned