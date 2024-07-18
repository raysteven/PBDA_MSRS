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

from flask_login import current_user
from utils.login_handler import require_login


dash.register_page(__name__, path='/',name='PBDA: MSRS Reporting System',title='PBDA: MSRS Reporting System')
require_login(__name__)

pgnum = 0


current_directory = os.getcwd()
# Get the parent directory
parent_directory = os.path.dirname(current_directory)



def create_dataframe_from_json(base_dir=os.path.join(parent_directory,'Amino_Acid_Panel','Final_Report')):
    # Find all JSON files
    json_files = glob.glob(os.path.join(base_dir, '**', '*.json'), recursive=True)
    
    # Get file modification times
    files_with_mtime = [(file, os.path.getmtime(file)) for file in json_files]
    
    # Sort files by modification time (oldest first)
    files_with_mtime.sort(key=lambda x: x[1])
    
    # Read JSON files and extract data
    data = []
    for i, (file, _) in enumerate(files_with_mtime):
        with open(file, 'r') as f:
            json_data = json.load(f)
            json_data['Run No.'] = i + 1  # Add the numbering
            data.append(json_data)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Sort DataFrame by 'number' column in descending order
    df = df.sort_values(by='Run No.', ascending=False).reset_index(drop=True)
    
    # Move 'number' column to the first position
    cols = ['Run No.'] + [col for col in df.columns if col != 'Run No.']
    df = df[cols]
    
    return df

df = create_dataframe_from_json()
print(df)

# Home page layout

def layout():
    if not current_user.is_authenticated:
        return html.Div(["Please ", dcc.Link("login", href="/login"), " to continue"])
    

    layout = html.Div(
        children=[

                html.Div(
                    className="div-app",
                    id=f"div-app-{pgnum}",
                    children = [ #  app layout here

                        html.Div([
                            html.H5('Home Page', style={'margin-top':'20px'}),
                            html.Div([
                            html.P(['Welcome to the home page of this PBDA!', html.Br() ,'You can use the available tools from the navigation bar on the top right of the page.']),
                            ])
                        ], style={'margin-left':'20px', 'fontFamily':'Monaco, monospace'}),

                        html.Div([
                            html.H5('Example Input and Output Files'),
                            html.Div([
                            html.P([
                                    dcc.Download(id=f'download-file-{pgnum}'),
                                    
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