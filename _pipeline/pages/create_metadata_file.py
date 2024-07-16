import dash
from dash import dcc, html, dash_table, callback
from dash.dependencies import Input, Output, State
from dash import callback_context
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import base64
import os
import shutil  # For file copying
import time
import threading


from PBTK import *
from lkj_to_metadata import lkj_to_metadata

from flask_login import current_user
from utils.login_handler import require_login

dash.register_page(__name__, path='/generate/metadata-file',name='PBDA: MSRS Reporting System',title='PBDA: MSRS Reporting System')
require_login(__name__)

pgnum=1

current_directory = os.getcwd()
# Get the parent directory
parent_directory = os.path.dirname(current_directory)
input_temp_dir = os.path.join(os.getcwd(),'input_temp')

#print(current_user.id)

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
                                    html.Div([
                                        html.H5('Runfolder', style={'font-weight': 'bold', 'fontFamily':'Montserrat, sans-serif', 'margin':'0'}),
                                        html.P("Please input in YYYYMMDD format. (For example: 20230714)", style={'margin':'0', 'fontFamily':'Montserrat, sans-serif'}),
                                        html.Div([
                                            dcc.Input(
                                            id='input-runfolder',
                                            type='text',
                                            placeholder='Enter Runfolder Name',
                                            required=True,
                                            style={
                                                'width': '300px',  # Adjust the width as needed
                                                'margin': '10px auto',  # Center the input box horizontally with margin
                                                'padding': '10px',  # Add padding to the input box
                                                'border': '1px solid #ccc',  # Add a border with a lighter color
                                                'borderRadius': '5px',  # Add rounded corners
                                                'boxSizing': 'border-box',  # Ensure the padding and border are included in the width
                                                'fontFamily':'Montserrat, sans-serif',
                                                }
                                            )
                                        ])

                                    ], style={'margin':3}),


                                    html.Div([
                                        html.Div([
                                            html.Br()
                                        ])
                                    ]),

                                    html.Div([
                                    html.H5('LKJ File', style={'font-weight': 'bold', 'margin':'0'}),
                                    html.P("Please input only a XLS file.", style={'margin':'0', 'fontFamily':'Montserrat, sans-serif'}),
                                    dcc.Upload(
                                        id='upload-lkj-file',
                                        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                                        style={
                                            'width': '100%', 'height': '60px', 'lineHeight': '60px',
                                            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                                            'textAlign': 'center', 'margin': '10px'
                                            },
                                            multiple=False
                                        ),
                                    ], style={'display': 'inline-block', 'width': '45%', 'margin':'20'}),
                                    
                                    html.Button('Generate Metadata File!', id='button-generate-metadata-file', n_clicks=0, style={
                                        'margin': '50px',
                                        'padding': '10px 20px',
                                        'background-color': '#4CAF50',
                                        'color': 'white',
                                        'border': 'none',
                                        'border-radius': '5px',
                                        'cursor': 'pointer',
                                        'transition': 'background-color 0.3s ease',
                                    }),

                                    html.Br(),

                                    # Interval component for polling metadata status
                                    dcc.Interval(
                                        id='interval-metadata-file-check',
                                        interval=5000,  # in milliseconds, adjust as needed (5000ms = 5s)
                                        n_intervals=0,
                                        disabled=True,  # Start disabled and enable after metadata generation is triggered
                                    ),

                                    dcc.Store(id='metadata-file-store'),
                                    dcc.Download(id='download-metadata-file'),

                                    html.Div([
                                        html.H5('Notification',style={'font-weight':'bold'}),
                                        html.Div(id='notification-container-generate-metadata-file', style={"border": "0px solid black", "padding":"10px", "width":"97.5%"})
                                    ], style={'fontFamily':'Montserrat, sans-serif'})



                                ], style={'margin':'20px'})

                    ]
                )
            ]
        )
    return layout

    #@dash_app.callback(
    #    Output('page-1-content', 'children'),
    #    Input('page-1-button', 'n_clicks')
    #)
    #def update_output(n_clicks):
    #    return f"Button has been clicked {n_clicks} times." if n_clicks else "Button not clicked yet."
@callback(
    Output('upload-lkj-file', 'children'),
    [Input('upload-lkj-file', 'filename')],
    [State('upload-lkj-file', 'contents')],
    allow_duplicate=True
)
def update_lkj_file(lkj_filename, lkj_contents):
    if lkj_filename is not None:
        print(lkj_filename)
        extension = '.xls'
        if extension not in lkj_filename:
            return html.Div(['Please input XLS file only!'], style={'backgroundColor': 'red', 'color': 'white'})
        sample_file_path = os.path.join('input_temp', lkj_filename)
        with open(sample_file_path, 'wb') as f:
            f.write(base64.b64decode(lkj_contents.split(",")[1]))
        print('Upload success: {}'.format(sample_file_path))
        # Return updated Upload components with file names and blue background
        return html.Div([lkj_filename], style={'backgroundColor': '#2d82b5', 'color': 'white'})
    return html.Div(['Drag and Drop or ', html.A('Select Files')])

def generate_metadata_async(runfolder, lkj_file_path, runfolder_dir):
    lkj_df = lkj_to_metadata(lkj_file_path)
    metadata_path = os.path.join(runfolder_dir, f'Metadata_AminoAcidPanel_{runfolder}.csv')
    lkj_df.to_csv(metadata_path, index=False)

    print("Metadata Generation Done!")

    return metadata_path

@callback(
    [Output('notification-container-generate-metadata-file', 'children'),
    Output('interval-metadata-file-check', 'disabled'),
    Output('metadata-file-store', 'data'),
    Output('download-metadata-file', 'data')],  # Add this line for dcc.Download
    [Input('button-generate-metadata-file', 'n_clicks'),
    Input('interval-metadata-file-check', 'n_intervals')],
    [State('upload-lkj-file', 'filename'),
    State('input-runfolder', 'value'),
    State('metadata-file-store', 'data'),
    ],
)
def unified_callback(n_clicks, n_intervals, lkj_file_filename, runfolder, metadata_data):
    triggered_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'button-generate-metadata-file':
        if n_clicks > 0:
            missing_components = []
            if not runfolder:
                missing_components.append('Runfolder')
            if not lkj_file_filename:
                missing_components.append('LKJ File')

            
            if missing_components:
                return (f'Missing component(s): {", ".join(missing_components)}. Please complete all required fields to generate the metadata.', 
                        dash.no_update,  # This output does not change
                        dash.no_update,
                        dash.no_update)
            
            ###>>>>>>>>>>>>>>>>>>>>>>>>> FILE MOVING
            print(runfolder)
            runfolder_dir = os.path.join(parent_directory, '_lkj_metadata' ,runfolder)
            # Ensure the destination directory exists
            if not os.path.exists(runfolder_dir):
                os.makedirs(runfolder_dir, exist_ok=True)

            # Get a list of all files and directories in the source directory
            input_temp_files = os.listdir(input_temp_dir)
            print('Moving files...')

            # Move each file and directory from the source to the destination
            for item in input_temp_files:
                source_item_path = os.path.join(input_temp_dir, item)
                destination_item_path = os.path.join(runfolder_dir, item)
                
                # If the destination item exists and is a directory, remove it if you want to overwrite
                if os.path.exists(destination_item_path):
                    if os.path.isdir(destination_item_path):
                        shutil.rmtree(destination_item_path)
                    else:
                        os.remove(destination_item_path)

                # Now move the item to the destination
                if os.path.isdir(source_item_path):
                    shutil.copytree(source_item_path, destination_item_path)
                    shutil.rmtree(source_item_path)  # Remove the source directory after copying
                else:
                    shutil.move(source_item_path, destination_item_path)

            lkj_file_path = os.path.join(runfolder_dir,lkj_file_filename)

            print(lkj_file_path)
            ###<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< FILE MOVING
            
            metadata_path = generate_metadata_async(runfolder, lkj_file_path, runfolder_dir)
            return 'Metadata generation finished. Please wait for the file to be downloaded. Do not refresh the webpage!', False, metadata_path, dash.no_update
        else:
            return 'All file has been uploaded. Generating metadata file. Do not refresh the webpage!', True, None, None

    elif triggered_id == 'interval-metadata-file-check':
        metadata_path = metadata_data
        if n_intervals > 0 and metadata_path:
            # Assuming metadata_data is a direct link to the downloadable file
            return ['File has been downloaded', True, metadata_data, dcc.send_file(metadata_data)]
        else:
            return 'metadata generation in progress...', True, metadata_data, dash.no_update  # Keep the download data unchanged if not ready
        
    # Default return statement to avoid Dash callback exceptions
    return 'Please upload the necessary files and enter the Runfolder name to generate the metadata file', True, None, None

