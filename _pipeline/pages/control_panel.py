import dash
from dash import dcc, html, dash_table, callback
from dash.dependencies import Input, Output, State
from dash import callback_context
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import os

from flask_login import current_user
from utils.login_handler import require_login

import psutil
import plotly.graph_objects as go


dash.register_page(__name__, path='/control-panel',name='PBDA: MSRS Reporting System',title='PBDA: MSRS Reporting System')
require_login(__name__)

pgname = __name__

def get_disk_usage():
    partitions = psutil.disk_partitions()
    for partition in partitions:
        if partition.mountpoint == '/':  # use '/' in Ubuntu OS, use 'C:\\' in Windows
            usage = psutil.disk_usage(partition.mountpoint)
            total_gb = usage.total / (1024 ** 3)  # total space in GB
            used_gb = usage.used / (1024 ** 3)    # used space in GB
            free_gb = usage.free / (1024 ** 3)    # free space in GB
            return total_gb, used_gb, free_gb

total, used, free = get_disk_usage()
labels = ['Used Disk Space', 'Free Disk Space']
values = [round(used,2), round(free,2)]

# Define custom colors
colors = ['#EE4E4E', '#A1DD70']  # Example colors: Tomato for used space, LimeGreen for free space

# Create the pie chart
fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.65, 
                             marker=dict(colors=colors),
                             textinfo='text+value',
                             textfont=dict(size=12))])

# Add title and update layout
#fig.update_layout(title_text='Disk Space Usage (GB)',
#                  title_font=dict(size=24),
#                  title_x=0.5)

class FileTree:

    def __init__(self, filepath: os.PathLike, name: str):
        """
        Usage: component = FileTree('Path/to/my/File', 'file_tree').render()
        """
        self.filepath = filepath
        self.name = name

    def render(self) -> dmc.Accordion:
        return dmc.Accordion(
            children=self.build_tree(self.filepath, isRoot=True), multiple=True, id=self.name)

    def flatten(self, l):
        return [item for sublist in l for item in sublist]

    def make_file(self, file_name):
        return dmc.Text(
            [DashIconify(icon="akar-icons:file"), " ", file_name], style={"paddingTop": '5px'}
        )

    def make_folder(self, folder_name):
        return [DashIconify(icon="akar-icons:folder"), " ", folder_name]

    def build_tree(self, path, isRoot=False):
        d = []
        if os.path.isdir(path):
            children = self.flatten([self.build_tree(os.path.join(path, x))
                                     for x in os.listdir(path)])
            if isRoot:
                d.append(
                    dmc.AccordionItem([
                        dmc.AccordionControl(self.make_folder(os.path.basename(path))),
                        dmc.AccordionPanel(children=children)
                    ], value=str(path))
                )
            else:
                d.append(
                    dmc.AccordionItem([
                        dmc.AccordionControl(self.make_folder(os.path.basename(path))),
                        dmc.AccordionPanel(children=children)
                    ], value=str(path))
                )
        else:
            d.append(self.make_file(os.path.basename(path)))
        return d

#tree = FileTree("..", "file_tree").render() # "../_zips"

def layout():
    if not current_user.is_authenticated:
        return html.Div(["Please ", dcc.Link("login", href="/login"), " to continue"])
    

    layout = dmc.MantineProvider(
        html.Div(
            [
                dmc.Space(h=50),
                dmc.Grid([
                    dmc.GridCol(dmc.Title(f"File Tree Viewer", order=3), span=7),
                    dmc.GridCol(dmc.Title(f"Storage Disk Viewer (GB)", order=3), span=4)
                ],styles={"root": {"justify": "center", 'fontFamily': 'Monaco, monospace','grow':True,'gap':'xl','textAlign': "left",'topMargin':'10px','padding-left':'30px'}}),
                dmc.Grid([
                    dmc.GridCol(html.Div(id="file_tree_container", children=[FileTree("..", "file_tree").render()]), span=7),
                    dmc.GridCol(dcc.Graph(figure=fig), span=4)
                ],styles={"root": {"justify": "center", 'fontFamily': 'Monaco, monospace','grow':True,'gap':'xl','textAlign': "left",'padding-left':'30px'}})

            ]
        )
    )

    return layout
#