import dash
from dash import dcc, html, dash_table, callback
from dash.dependencies import Input, Output, State
from dash import callback_context
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import os
import glob
import json
import pandas as pd
import requests
import re
from datetime import datetime

from flask_login import current_user
from utils.login_handler import require_login

import dash_ag_grid as dag
import dash_mantine_components as dmc

dash.register_page(__name__, path='/',name='PBDA: MSRS Reporting System',title='PBDA: MSRS Reporting System')
require_login(__name__)

pgname = __name__.split('.')[-1]
rows_per_page = 10

current_directory = os.getcwd()
# Get the parent directory
parent_directory = os.path.dirname(current_directory)

result_dir = os.path.join(current_directory, 'assets','_results')


def calculate_processing_time(start_time_str):
    
    start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
    # Get the current time
    stop_time = datetime.now()

    # Calculate the duration
    duration = stop_time - start_time

    # Get the total duration in seconds
    duration_seconds = duration.total_seconds()

    # Get hours, minutes, and seconds
    hours, remainder = divmod(duration_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Print the results
    return f"Time elapsed: {int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds"


def create_dataframe_from_json(directories=None):
    
    if directories is None:
        directories = [os.path.join(result_dir, 'Amino_Acid_Panel', 'Final_Report'),
                       os.path.join(result_dir, 'Amino_Acid_Panel', 'LKJ_Metadata'),
                       os.path.join(result_dir, 'Cortisol', 'Final_Report'),
                       os.path.join(result_dir, 'Cortisol', 'LKJ_Metadata'),
                       ]
    
    # Initialize a list to store data from all JSON files
    data = []

    # Process each directory
    for base_dir in directories:
        # Find all JSON files in the current directory
        json_files = glob.glob(os.path.join(base_dir, '**', 'folder_identifier.json'), recursive=True)
        
        # Get file modification times
        files_with_mtime = [(file, os.path.getmtime(file)) for file in json_files]
        
        # Sort files by modification time (oldest first)
        files_with_mtime.sort(key=lambda x: x[1], reverse=True)
        
        # Read JSON files and extract data
        for i, (file, _) in enumerate(files_with_mtime):
            with open(file, 'r') as f:
                json_data = json.load(f)
                
                date_created = json_data['Date Created']
                time_created = json_data['Time Created']
                start_time_str = f"{date_created} {time_created}:00"

                # Modify the download link if the file does not exist
                download_link = json_data.get("Download Link", "")
                # Use a regular expression to find the URL
                match = re.search(r'\((http[^\)]+)\)', download_link)

                if match:
                    url = match.group(1)                

                if not file_exists(url):
                    duration_file_process = calculate_processing_time(start_time_str)
                    json_data["Download Link"] = f"File is being generated, please wait. | {duration_file_process}"
                
                # Add the numbering if needed
                # json_data['No'] = i + 1  
                
                data.append(json_data)
    
    # Create DataFrame from the collected data
    df = pd.DataFrame(data)
    return df

def file_exists(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        return False


def get_main_table(df):

    columnDefs = [
        {
        "field":"Date Created",
        "filter": "agDateColumnFilter",
        "checkboxSelection": True,
        "headerCheckboxSelection": True,
        "sort": "desc",  # Default sort direction to descending (newest to oldest)
        "width": 50, "maxWidth": 200
        },
        {"field":"Time Created","width": 50, "maxWidth": 200, "sort": "desc"},
        {"field":"User","width": 50, "maxWidth": 130},
        ] + [{"field": i,"width": 50, "maxWidth": 200} for i in ["Test Name","Result Type"]] + [
            {"field":"Runfolder Name","width": 50, "maxWidth": 300},
            {"field":"Download Link","cellRenderer": "markdown"},
            ]
    
    defaultColDef = {
        "flex": 1,
        #"minWidth": 10,
        #"filter": "agTextColumnFilter",
        "filter": True, 
        "sortable": True, "floatingFilter": True,
    }    
    
    main_table = dag.AgGrid(
        id="grid-filter-model-multiple-conditions",
        rowData=df.to_dict("records"),
        columnDefs=columnDefs,
        defaultColDef=defaultColDef,
        columnSize="sizeToFit",
        filterModel={},
        dashGridOptions={
                "rowSelection": "multiple",
                "pagination": True,
                "paginationAutoPageSize": True,
                "animateRows": True,}
    )

    return main_table
# Home page layout

def layout():
    if not current_user.is_authenticated:
        return html.Div(["Please ", dcc.Link("login", href="/login"), " to continue"])

    df = create_dataframe_from_json()
    #print(df)

    main_table = get_main_table(df)

    layout = html.Div(
        children=[

                html.Div(
                    className="div-app",
                    id=f"div-app-{pgname}",
                    children = [ #  app layout here
                        html.Div([
                            dmc.Title(f"History Table", order=3),
                            dmc.Space(h=20),
                            main_table,
                            dmc.Space(h=300),
                        ], style={'margin':'20px'}),


                        html.Div([
                            html.H5('Example Input and Output Files'),
                            html.Div([
                            html.P([
                                    dcc.Download(id=f'download-file-{pgname}'),
                                    
                                    html.A(
                                        'LKJ',
                                        id='download-link-lkj',
                                        href="/assets/LKJ_Example.zip",
                                    ),
                                    
                                    html.Br(),
                                    html.A(
                                        'Metadata',
                                        id='download-link-metadata',
                                        href="/assets/Metadata_Example.zip",
                                    ),
                                    
                                    html.Br(),
                                    html.A(
                                        'Result Raw',
                                        id='download-link-result-raw',
                                        href="/assets/Raw_Example.zip",
                                    ),
                                    
                                    html.Br(),
                                    html.A(
                                        'Report Zip',
                                        id='download-link-report-zip',
                                        href="/assets/Report_Example.zip",
                                    ),
                                    
                                    ]),
                            ], style={'margin':'0'})
                        ], style={'margin-top':'150px', 'margin-left':'20px','fontFamily':'Monaco, monospace'}),


                        html.Div([
                            html.H5('Version'),
                            html.Div([
                            html.P(['- ',html.B('1.0.1'),' : Result Graph Adjustment, Added ', html.U('Result CSV'),'  to the Result Zip, Backend Improvements',
                                    html.Br(),
                                    '- ',html.B('1.0.0'),' : Initial Stable Release',
                                    ]),
                            ], style={'margin':'0'})
                        ], style={'margin-top':'150px', 'margin-left':'20px','fontFamily':'Monaco, monospace'}),



                    ]
                )

            ]
        )

    return layout
#