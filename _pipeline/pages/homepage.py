import dash
from dash import dcc, html, dash_table, callback
from dash.dependencies import Input, Output, State
from dash import callback_context
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import os

dash.register_page(__name__, path='/',name='PBDA: MSRS Reporting System',title='PBDA: MSRS Reporting System')


pgnum = 0

# Home page layout
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


#