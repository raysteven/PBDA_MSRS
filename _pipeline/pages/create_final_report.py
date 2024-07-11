import dash
from dash import dcc, html, callback, ctx, callback_context
from dash.dependencies import Input, Output, State
from dash import callback_context

import base64
import os
import shutil  # For file copying
import time
import threading

from datetime import datetime

import pandas as pd

from PBTK import *
from auto_aap import auto_aap

from flask_login import current_user
from utils.login_handler import require_login

dash.register_page(__name__, path='/generate/final-report',name='PBDA: MSRS Reporting System',title='PBDA: MSRS Reporting System')
require_login(__name__)

pgnum=2

current_directory = os.getcwd()
# Get the parent directory
parent_directory = os.path.dirname(current_directory)
input_temp_dir = os.path.join(os.getcwd(),'input_temp')


########################################################################################################################################################################################################

######################################## Pre-defined functions ########################################

########################################################################################################################################################################################################

def generate_report_async(runfolder, metadata_file_path, result_sheet_path):
    auto_aap(runfolder, metadata_file_path, result_sheet_path)
    print("Report Generation Done!")
    # Assuming report_data is a direct link to the downloadable file
    report_path = os.path.join(os.path.dirname(os.getcwd()),'_zips',f'{runfolder}.zip')
    print("Report Download Link:", report_path)
    return report_path

def log_current_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d || %H:%M:%S")
    displayed_str = f'[ {formatted_time} ]'

    return displayed_str

from time import sleep, time
from typing import List, Optional

from dash import callback_context
from dash.dependencies import ALL, Input, Output
from dash.exceptions import PreventUpdate


MULTIPLEXER_OUTPUTS = {}

def get_triggered() -> Optional[str]:
    ctx = callback_context
    if not ctx.triggered:
        return
    return ctx.triggered[0]['prop_id'].split('.')[0]

def create_multiplexer(output_component: str, output_field: str, count: int) -> List:
    store_component = f'{output_component}-{output_field}-store'

    @callback(
        Output(output_component, output_field),  # Output is an arbitrary dash component
        Input({'id': store_component, 'idx': ALL}, 'data'),  # Input is always a dcc.Store()
        prevent_initial_call=True
    )
    def multiplexer(_):
        triggered = get_triggered()
        if triggered is None:
            raise PreventUpdate

        inputs = callback_context.inputs
        for k, v in inputs.items():
            id_ = k.split('.')[0]
            if id_ == triggered:
                return v

        raise PreventUpdate

    return [dcc.Store({'id': store_component, 'idx': idx}, data=None) for idx in range(count)]


def MultiplexerOutput(output_component: str, output_field: str):
    store_component = f'{output_component}-{output_field}-store'
    MULTIPLEXER_OUTPUTS[store_component] = idx = MULTIPLEXER_OUTPUTS.setdefault(store_component, -1) + 1
    return Output({'id': store_component, 'idx': idx}, 'data')

########################################################################################################################################################################################################

######################################## Layout ########################################

########################################################################################################################################################################################################
def layout():
    if not current_user.is_authenticated:
        return html.Div(["Please ", dcc.Link("login", href="/login"), " to continue"])


    layout = html.Div([
        *create_multiplexer('interval-report-check', 'disabled', 2),
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
                ,disabled=False),
                
            ])

        ], style={'margin':3}),

        html.Div([
            html.Div([
                html.Br()
            ])
        ]),

        # Body
        html.Div([
            html.Div([
                html.H5('Metadata File', style={'font-weight': 'bold', 'margin':'0'}),
                html.P("Please input only a CSV file.", style={'margin':'0', 'fontFamily':'Montserrat, sans-serif'}),
                dcc.Upload(
                    id='upload-metadata-file',
                    children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                    style={
                        'width': '100%', 'height': '60px', 'lineHeight': '60px',
                        'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                        'textAlign': 'center', 'margin': '10px'
                    },
                    multiple=False,
                    disabled=False
                ),
            ], style={'display': 'inline-block', 'width': '45%', 'margin':'20'}),

            html.Div([
                html.H5('Result Sheet', style={'font-weight': 'bold', 'margin':'0'}),
                html.P('Please input only a XLSX file that must contain a sheet named "Sheet1".', style={'margin':'0', 'fontFamily':'Montserrat, sans-serif'}),
                dcc.Upload(
                    id='upload-result-sheet',
                    children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                    style={
                        'width': '100%', 'height': '60px', 'lineHeight': '60px',
                        'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                        'textAlign': 'center', 'margin': '10px'
                    },
                    multiple=False,
                    disabled=False
                )
            ], style={'display': 'inline-block', 'width': '45%', 'marginRight': '1.5%'}),
        ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-between', 'fontFamily':'Montserrat, sans-serif'}),
        
        html.Button('Generate Final Report!', id='button-generate-report', n_clicks=0, style={
            'margin': '10px 0',
            'padding': '10px 20px',
            'background-color': '#4CAF50',
            'color': 'white',
            'border': 'none',
            'border-radius': '5px',
            'cursor': 'pointer',
            'transition': 'background-color 0.3s ease',
        }, disabled=False),
        
        html.Br(),
        html.Br(),

        # Interval component for polling report status
        dcc.Interval(
            id='interval-report-check',
            interval=5000,  # in milliseconds, adjust as needed (5000ms = 5s)
            n_intervals=0,
            disabled=True,  # Start disabled and enable after report generation is triggered
        ),

        dcc.Store(id='report-store'),
        dcc.Download(id='download-report'),
        


        html.Div([
            html.H5('Notification',style={'font-weight':'bold'}),
            html.Div(id='output-container', style={"border": "0px solid black", "padding":"10px", "width":"45%"}),
            
        dcc.Loading(
            id="loading-1",
            type="default",
            color="#2d82b5",
            children=html.Div(id='output-container-2', style={"border": "0px solid black", "padding":"10px", "width":"45%"})
        ),
        
        ], style={'fontFamily':'Montserrat, sans-serif'})

    ], style={'margin': '20px'})

    return layout
########################################################################################################################################################################################################

######################################## Callbacks ########################################

########################################################################################################################################################################################################

@callback(
    Output('upload-result-sheet', 'children'),
    [Input('upload-result-sheet', 'filename')],
    [State('upload-result-sheet', 'contents')],
    allow_duplicate=True
)
def update_result_sheet(result_filename, result_contents):
    if result_filename is not None:
        print(result_filename)
        extension = '.xlsx'
        if extension not in result_filename:
            return html.Div(['Please input XLSX file only!'], style={'backgroundColor': 'red', 'color': 'white'})

        metadata_file_path = os.path.join('input_temp', result_filename)
        with open(metadata_file_path, 'wb') as f:
            f.write(base64.b64decode(result_contents.split(",")[1]))

        print('Upload success: {}'.format(metadata_file_path))

        # Check if the file contains a sheet named "Sheet1"
        try:
            xls = pd.ExcelFile(metadata_file_path)
            if 'Sheet1' not in xls.sheet_names:
                return html.Div(['The Excel file must contain a sheet named "Sheet1".'], style={'backgroundColor': 'red', 'color': 'white'})
            xls.close()
        except Exception as e:
            print(f"Error reading the Excel file: {e}")
            return html.Div(['Error reading the Excel file. Please ensure it is a valid XLSX file.'], style={'backgroundColor': 'red', 'color': 'white'})

        # Return updated Upload components with file names and blue background
        return html.Div([result_filename], style={'backgroundColor': '#2d82b5', 'color': 'white'})

    return html.Div(['Drag and Drop or ', html.A('Select Files')])

@callback(
    Output('upload-metadata-file', 'children'),
    [Input('upload-metadata-file', 'filename')],
    [State('upload-metadata-file', 'contents')],
    allow_duplicate=True
)
def update_metadata_file(metadata_filename, metadata_contents):
    if metadata_filename is not None:
        extension = '.csv'
        if extension not in metadata_filename:
            return html.Div(['Please input CSV file only!'], style={'backgroundColor': 'red', 'color': 'white'})
        print(metadata_filename)
        metadata_file_path = os.path.join(input_temp_dir, metadata_filename)
        with open(metadata_file_path, 'wb') as f:
            f.write(base64.b64decode(metadata_contents.split(",")[1]))
        print('Upload success: {}'.format(metadata_file_path))
        # Return updated Upload components with file names and blue background
        return html.Div([metadata_filename], style={'backgroundColor': '#2d82b5', 'color': 'white'})
    return html.Div(['Drag and Drop or ', html.A('Select Files')])

@callback(
    [Output('output-container', 'children'),
     MultiplexerOutput('interval-report-check', 'disabled'),
     Output('input-runfolder', 'disabled'),
     Output('upload-metadata-file', 'disabled'),
     Output('upload-result-sheet', 'disabled'),
     Output('button-generate-report', 'disabled'),
     ],
    [Input('button-generate-report', 'n_clicks')],
    [State('upload-metadata-file', 'filename'),
     State('upload-result-sheet', 'filename'),
     State('input-runfolder', 'value')],
     allow_duplicate=True,
)
def generate_report_initiation(n_clicks, metadata_file_filename, result_sheet_filename, runfolder):
    if n_clicks > 0:
        missing_components = []
        if not runfolder:
            missing_components.append('Runfolder')
        if not metadata_file_filename:
            missing_components.append('Metadata File')
        if not result_sheet_filename:
            missing_components.append('Result Sheet')
        
        if missing_components:
            return (f'Missing component(s): {", ".join(missing_components)}. Please complete all required fields to generate the report.', 
                    dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update  # This output does not change
                    )
        
        ###>>>>>>>>>>>>>>>>>>>>>>>>> FILE MOVING
        print(runfolder)
        runfolder_dir = os.path.join(parent_directory, runfolder)
        # Check if the directory exists
        if os.path.exists(runfolder_dir):
            # Delete the directory
            shutil.rmtree(runfolder_dir)
        # Recreate the directory
        os.makedirs(runfolder_dir, exist_ok=True)

        # Get a list of all files and directories in the source directory
        input_temp_files = os.listdir(input_temp_dir)
        print('Moving files...')

        # Move each file and directory from the source to the destination
        for item in input_temp_files:
            if any(real_file in item for real_file in [metadata_file_filename,result_sheet_filename]):
                print(f'Moving: {item}')
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
    
        # Get the list of files and directories again after moving certain files
        input_temp_files = os.listdir(input_temp_dir)

        # After moving certain files, delete all remaining files and directories if any
        if input_temp_files:
            for item in input_temp_files:
                item_path = os.path.join(input_temp_dir, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)  # Remove the file or link
                        print(f'Unlinking: {item_path}')
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)  # Remove the directory and its contents
                        print(f'Removing unnecessary file: {item_path}')
                except Exception as e:
                    print(f'Failed to delete {item_path}. Reason: {e}')

        print(f'Directory {input_temp_dir} has been emptied.')



        ###<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< FILE MOVING

        # Delete existing ZIP file if it exists
        report_path = os.path.join(os.path.dirname(os.getcwd()), '_zips', f'{runfolder}.zip')
        if os.path.exists(report_path):
            os.remove(report_path)

        runfolder_dir = os.path.join(parent_directory, runfolder)
        metadata_file_path = os.path.join(runfolder_dir, metadata_file_filename)
        result_sheet_path = os.path.join(runfolder_dir, result_sheet_filename)


        threading.Thread(target=generate_report_async, args=(runfolder, metadata_file_path, result_sheet_path)).start()

        return f'{log_current_time()} All file has been uploaded. Generating the final report. Do not refresh the webpage!', False, True, True, True, True
    else:
        return 'Please upload the necessary files and enter the Runfolder name to generate the report.', True, dash.no_update, dash.no_update, dash.no_update, dash.no_update

# Callback to check report status and trigger download
@callback(
    [Output('output-container-2', 'children'),
     MultiplexerOutput('interval-report-check', 'disabled'),
     Output('download-report', 'data')],
    [Input('interval-report-check', 'n_intervals')],
    [State('upload-metadata-file', 'filename'),
     State('upload-result-sheet', 'filename'),
     State('input-runfolder', 'value')],
    prevent_initial_call=True
)
def download_report(n_intervals, metadata_file_filename, result_sheet_filename, runfolder):
    if n_intervals > 0:
        report_path = os.path.join(os.path.dirname(os.getcwd()), '_zips', f'{runfolder}.zip')

        if os.path.exists(report_path):
            return [f'{log_current_time()} Report generation is finished. The report has been downloaded; please check the Download directory. ', html.Br(), html.Br() ,html.B('You can refresh the page if you want to enter a new query.')], True, dcc.send_file(report_path)
        else:
            return f'{log_current_time()} Report is still being generated. Please wait...', False, dash.no_update
    else:
        return dash.no_update, True, dash.no_update

########################################################################################################################################################################################################
