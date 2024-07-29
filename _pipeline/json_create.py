from PBTK import *
import json
import numpy as np
import os
import matplotlib.pyplot as plt
import numpy as np

import matplotlib
matplotlib.use('Agg')

import time
from datetime import datetime

def calculate_age(birth_date_str):
    # Parse the birth date string to a datetime object
    birth_date = datetime.strptime(birth_date_str, "%d-%m-%Y")
    
    # Get the current date
    current_date = datetime.now()
    
    # Calculate the difference in years
    years_difference = current_date.year - birth_date.year
    
    # Calculate the difference in months
    months_difference = current_date.month - birth_date.month
    
    # Calculate the difference in days
    days_difference = current_date.day - birth_date.day
    
    # Adjust the months and days difference
    if days_difference < 0:
        months_difference -= 1
        days_difference += (birth_date.replace(year=current_date.year, month=current_date.month) - birth_date.replace(year=current_date.year, month=current_date.month-1)).days
    
    if months_difference < 0:
        years_difference -= 1
        months_difference += 12
    
    # Calculate the age in decimal
    age_decimal = years_difference + (months_difference / 12) + (days_difference / 365.25)
    
    return age_decimal


age_class_dict = {
    "class_1":{"bottom":"reference_range_bottom_anak_1","up":"reference_range_up_anak_1"},
    "class_2":{"bottom":"reference_range_bottom_anak_2","up":"reference_range_up_anak_2"},
    "class_3":{"bottom":"reference_range_bottom_anak_3","up":"reference_range_up_anak_3"},
    "class_4":{"bottom":"reference_range_bottom_dewasa","up":"reference_range_up_dewasa"}
}


def determine_age_class(age):
    if age < 1/12:
        age_class = "class_1"
    elif 1/12 <= age <= 12/12:
        age_class = "class_2"
    elif  12/12 < age <= 19:
        age_class = "class_3"
    elif age > 19:
        age_class = "class_4"
    else:
        age_class = "class_4" 
    return age_class


# Custom serializer for non-serializable data types
def custom_serializer(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def determine_result(amino_acid, measured_result, ref_db, age_class):
    index = amino_acid
    
    optimal_bottom = ref_db.at[index,age_class_dict[age_class]["bottom"]]
    optimal_up = ref_db.at[index,age_class_dict[age_class]["up"]]
    
    if optimal_bottom <= measured_result <= optimal_up:
        interpretation_result = ref_db.at[index,'result_optimal']
    elif measured_result < optimal_bottom :
        interpretation_result = ref_db.at[index,'result_low']
    elif measured_result > optimal_up :
        interpretation_result = ref_db.at[index,'result_high']

    return interpretation_result

def normalize_value(x, a, b, c, d):
    """
    Normalize a value x with a custom scheme where a maps to 0, b to 25, c to 75, and d to 100.
    
    Parameters:
    - x: The value to normalize.
    - a, b, c, d: Defines the original range and key points for normalization.
    
    Returns:
    - The normalized value of x according to the custom scheme.
    """

    if x < a or x > d:
        raise ValueError("The value x must be within the range [a, d].")
    
    if x <= b:
        # Normalize between 0 and 25 for x in [a, b]
        return 15 * (x - a) / (b - a)
    elif x <= c:
        # Normalize between 25 and 75 for x in [b, c]
        return 15 + 70 * (x - b) / (c - b)
    else:
        # Normalize between 75 and 100 for x in [c, d]
        return 85 + 15 * (x - c) / (d - c)

def create_gauge_chart(age_class, measured_result, amino_acid, ref_db, outdir_path):
    index = amino_acid

    #menyesuaikan chartnya dengan kebutuhan Lab MS dimana kalau value terukur masih dalam reference range, sebenarnya masih hijau tapi mepet di perbatasan.
    #batas atas dan bawah dilebihi 30% -> batas atas * 1,3 & batas bawah * 0.7 

    reference_range_bottom = ref_db.at[index,'linearity_bottom']
    optimal_bottom = ref_db.at[index,age_class_dict[age_class]["bottom"]]
    optimal_up = ref_db.at[index,age_class_dict[age_class]["up"]]
    reference_range_up = ref_db.at[index,'linearity_top']

    #real_optimal_bottom = ref_db.at[index,'optimal_bottom']
    #real_optimal_up = ref_db.at[index,'optimal_up']

    value = measured_result
    
    normalized_reference_range_bottom = normalize_value(reference_range_bottom, a=reference_range_bottom, b=optimal_bottom, c=optimal_up, d=reference_range_up)
    normalized_optimal_bottom = normalize_value(optimal_bottom, a=reference_range_bottom, b=optimal_bottom, c=optimal_up, d=reference_range_up)
    normalized_optimal_up = normalize_value(optimal_up, a=reference_range_bottom, b=optimal_bottom, c=optimal_up, d=reference_range_up)
    normalized_reference_range_up = normalize_value(reference_range_up, a=reference_range_bottom, b=optimal_bottom, c=optimal_up, d=reference_range_up)
    normalized_value = normalize_value(max(min(value,reference_range_up), reference_range_bottom), a=reference_range_bottom, b=optimal_bottom, c=optimal_up, d=reference_range_up)

    #normalized_real_optimal_bottom = normalize_value(real_optimal_bottom, a=reference_range_bottom, b=optimal_bottom, c=optimal_up, d=reference_range_up)
    #normalized_real_optimal_up = normalize_value(real_optimal_up, a=reference_range_bottom, b=optimal_bottom, c=optimal_up, d=reference_range_up)

    ### logic perbatasan/dipepet ###
    #if normalized_optimal_bottom <= normalized_value <= normalized_real_optimal_bottom:
    #    normalized_value = normalized_optimal_bottom
    #elif normalized_real_optimal_up >= normalized_value >= normalized_optimal_up:
    #    normalized_value = normalized_optimal_up
    ### logic perbatasan/dipepet ###

    reference_range_bottom = normalized_reference_range_bottom
    optimal_bottom = normalized_optimal_bottom
    optimal_up = normalized_optimal_up
    reference_range_up = normalized_reference_range_up

    regions = {
        "Low": {"range": [reference_range_bottom, optimal_bottom], "color": "#ff0404"},
        "Optimal": {"range": [optimal_bottom, optimal_up], "color": "#70b344"}, #85e62c
        "High": {"range": [optimal_up, reference_range_up], "color": "#ff0404"},
    }

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 1.5))
    ax.set_xlim(reference_range_bottom-2, reference_range_up+2)
    ax.set_ylim(0, 1)

    # Remove y-axis and unnecessary spines
    ax.yaxis.set_visible(False)
    ax.spines[['top', 'right', 'left']].set_visible(False)  # Keep bottom spine for X axis

    # Plot each region
    for region in regions.values():
        ax.barh(0.5, region["range"][1]-region["range"][0], left=region["range"][0], color=region["color"], height=0.5)

    # Set ticks for the region boundaries
    #boundaries = [0] + [region["range"][1] for region in regions.values()]
    #boundaries = [region["range"][1] for region in regions.values()]
    
    boundaries = [reference_range_bottom] + [region["range"][1] for region in regions.values()]
    ax.set_xticks(boundaries)
    ax.set_xticklabels(['','','',''])

    #ax.xaxis.set_visible(False)

    # Assuming the rest of your plot setup code remains the same
    # Determine the minimum and maximum thresholds
    #min_threshold = regions["Low"]["range"][0]
    #max_threshold = regions["High"]["range"][1]

    # Adjust the current value if it's outside the thresholds
    #adjusted_value = max(min(normalized_value, reference_range_up), reference_range_bottom)
    adjusted_value = normalized_value

    # Calculate total x-axis range
    total_range = reference_range_up - reference_range_bottom  # Since your x-axis goes from 0 to 100

    # Determine marker width as a percentage of the total range
    # For example, making the marker's width 1% of the total range
    marker_width_percent = 1
    #marker_width = (total_range / 100) * marker_width_percent
    marker_width = 1
    # Adjust marker position and width dynamically
    # Note: You might need to adjust the marker's center position slightly to ensure it aligns properly with the value
    
    square_left = adjusted_value - (marker_width / 2)
    triangle_points = [[adjusted_value - (marker_width / 2), 0.25], [adjusted_value + (marker_width / 2), 0.25], [adjusted_value, 0.05]]


    # Create a square with a triangle at the bottom pointing downwards using the dynamic width
    # Square
    ax.add_patch(plt.Rectangle((square_left, 0.25), marker_width, 0.5, color='black'))
    # Triangle pointing downwards
    ax.add_patch(plt.Polygon(triangle_points, color='black'))


    # Display the current value above the marker
    #ax.text(adjusted_value, 1.05, f'Your Result', ha='center', va='center', color='black', fontsize=15)
    ax.text(adjusted_value, 1, value, ha='center', va='center', color='black', fontsize=15, weight='bold')

    ax.text((reference_range_bottom+optimal_bottom)/2, -0.45, 'Low', ha='center', fontsize=15) 
    ax.text((optimal_bottom+optimal_up)/2, -0.45, 'Optimal', ha='center', fontsize=15)
    ax.text((optimal_up+reference_range_up)/2, -0.45, 'High', ha='center', fontsize=15)


    #plt.tight_layout()
    #plt.show()

    image_save_path = os.path.join(outdir_path, amino_acid+"_graph.png")
    print('image_save_path:',image_save_path)
    plt.savefig(image_save_path, dpi=400, bbox_inches='tight')
    plt.close(fig)  # Close the figure to release memory

def json_create(report_df, ref_db, runfolder, workdir):
    print('Starting json_create!!!!!')
    
    print('loop report_df!!!!!')

    for i in report_df.index:
        
        
        print('Create metadata!!!!!')
        #####Create metadata
        report_dict = {'metadata':{},'test_result':{}}
        sample_enumerator = i
        report_dict['metadata']['Nama'] = report_df['nama'][sample_enumerator]
        patient_id = report_df['patient_id'][sample_enumerator]

        report_dict['metadata']['Age'] = report_df['usia'][sample_enumerator]
        report_dict['metadata']['Lab Number'] = report_df['lab_number'][sample_enumerator]
        report_dict['metadata']['Ref. Number'] = report_df['ref_number'][sample_enumerator]
        report_dict['metadata']['DoB'] = report_df['dob'][sample_enumerator]

        print('Birth and Age calculation!!!!!')
        birth_date_str = report_dict['metadata']['DoB']
        age = calculate_age(birth_date_str)
        age_class = determine_age_class(age)

        print('Create out_folder!!!!!')
        ##### Create out_folder
        out_folder = os.path.join(runfolder, patient_id)
        outdir_path = os.path.join(workdir, out_folder)
        
        print('Check if outdir_path folder already exists!!!!!')
        # Check if the folder already exists
        if not os.path.exists(outdir_path):
            # Create the folder
            os.makedirs(outdir_path)    

        #####Create test_result
        print('Create test_result!!!!!')
        print('Loop index ref_db!!!!!')
        for index in ref_db.index:
            report_dict['test_result'][index] = {"test_name":ref_db.at[index,'amino_acid']}
            report_dict['test_result'][index]['type'] = ref_db.at[index,'type']
            try: measured_value = int(report_df[index][sample_enumerator])
            except: measured_value = 0
            report_dict['test_result'][index]['measured_value'] = measured_value
            ref_value = str(ref_db.at[index,age_class_dict[age_class]["bottom"]]) + ' - '+ str(ref_db.at[index,age_class_dict[age_class]["up"]])
            report_dict['test_result'][index]['ref_value'] = ref_value
            report_dict['test_result'][index]['result_interpretation'] = determine_result(amino_acid=index, measured_result=measured_value, ref_db=ref_db, age_class=age_class)
            #print(f'create_gauge_chart!!!!! {index}')
            create_gauge_chart(age_class=age_class, measured_result=measured_value, amino_acid=index,ref_db=ref_db,outdir_path=outdir_path)

        print('CREATING JSON FILE!!!!!')

        #### Write JSON string to a file
        with open(f'{outdir_path}/{patient_id}_AminoAcidPanel.json', 'w') as file:
            json_str = json.dumps(report_dict, indent=4, default=custom_serializer)
            file.write(json_str)