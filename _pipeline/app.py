import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, ALL
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

import base64
import os
import shutil  # For file copying
import time
import threading
import argparse



from PBTK import *

from utils.login_handler import restricted_page
from flask import Flask, request, redirect, session
from flask_login import login_user, LoginManager, UserMixin, logout_user, current_user

import dash_mantine_components as dmc


### MANDATORY FOR DMC ###
dash._dash_renderer._set_react_version('18.2.0')


######

# Exposing the Flask Server to enable configuring it for logging in
server = Flask(__name__)


@server.route('/login', methods=['POST'])
def login_button_click():
    if request.form:
        username = request.form['username']
        password = request.form['password']
        if VALID_USERNAME_PASSWORD.get(username) is None:
            return """invalid username and/or password <a href='/login'>login here</a>"""
        if VALID_USERNAME_PASSWORD.get(username) == password:
            login_user(User(username))
            if 'url' in session:
                if session['url']:
                    url = session['url']
                    session['url'] = None
                    return redirect(url) ## redirect to target url
            return redirect('/') ## redirect to home
        return """invalid username and/or password <a href='/login'>login here</a>"""

# Keep this out of source code repository - save in a file or a database
#  passwords should be encrypted
VALID_USERNAME_PASSWORD = {"admin": "admin", "Ray": "password"}


# Updating the Flask Server configuration with Secret Key to encrypt the user session cookie
#server.config.update(SECRET_KEY=os.getenv("SECRET_KEY"))
server.config.update(SECRET_KEY='SECRET_KEY')

# Login manager object will be used to login / logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/login"


class User(UserMixin):
    # User data model. It has to have at least self.id as a minimum
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(username):
    """This function loads the user by user id. Typically this looks up the user from a user database.
    We won't be registering or looking up users in this example, since we'll just login using LDAP server.
    So we'll simply return a User object with the passed in username.
    """
    return User(username)



######

current_directory = os.getcwd()
# Get the parent directory
parent_directory = os.path.dirname(current_directory)
input_temp_dir = os.path.join(os.getcwd(),'input_temp')


app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True, use_pages=True)
app.title = 'PBDA: Mass Spectrometry Reporting System (MSRS)'


navbar = dmc.Group(
    children=[
        dmc.Anchor(
            dmc.Button(
                "Home",
                styles={"root": {'fontFamily': 'Monaco, monospace', 'color': 'black', 'justifyContent': 'center', 'alignItems': 'center',}},
                variant="subtle"  # or another variant that suits your design
            ),
            href="/"
        ),
        dmc.Menu(
            [
                dmc.MenuTarget(dmc.Button("Generate Files", variant="subtle", c="black")),
                dmc.MenuDropdown(
                    [
                        dmc.MenuItem("Metadata File", href="/generate/metadata-file"),
                        dmc.MenuItem("Final Report", href="/generate/final-report"),
                    ]
                ),
            ],
            trigger="hover",
        ),
        
    ],
    align="center",
    gap="0",
    style={'zIndex': 1030, 'fontFamily': 'Monaco, monospace', 'color': 'black'} #, 'backgroundColor': '#FEF200'
)

app.layout = dmc.MantineProvider([
    html.Div([
    dcc.Location(id='url', refresh=False),

    # Header
    html.Div([
        # New div wrapping the image and text, with flex-grow style
        html.Div([
            html.Img(src='/assets/prodia-sulur.png', style={'height': '75px', 'marginRight': '15px'}),
            html.Div([
                html.H4('Mass Spectrometry Reporting System (MSRS)', style={'display': 'inline-block', 'verticalAlign': 'middle', 'margin':'0', 'font-weight':'bold'}),
                html.P('Prodia Bioinformatics Dashboard Application (PBDA)', style={'margin':'0', 'font-weight':'bold'})
            ], style={'display': 'inline-block', 'verticalAlign': 'middle'}),
        ], style={'display': 'flex', 'alignItems': 'center', 'flexGrow': '1'}), # This div will grow to take up available space
        html.Div(id='navbar'), #except the Profile and Logout button
        dmc.Group(id="user-status-header", styles={"root": {"paddingRight": 30, 'fontFamily': 'Monaco, monospace',}}),
    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-between', 'marginBottom': '20px', 'backgroundColor': '#FEF200', 'fontFamily':'Montserrat, sans-serif', 'overflow':'visible'}),
    

    #Page Content
    # Page Content
    dcc.Loading(
        id='loading-page-container',
        type='default',
        children=dash.page_container,
    ),
    html.Div(id='page-content'),
])
])

@app.callback(
    Output("user-status-header", "children"),
    Output('url','pathname'),
    Output("navbar","children"),
    Input("url", "pathname"),
    Input({'index': ALL, 'type':'redirect'}, 'n_intervals')
)
def update_authentication_status(path, n):
    ### logout redirect
    if n:
        if not n[0]:
            return '', dash.no_update, navbar
        else:
            return '', '/login', navbar

    ### test if user is logged in
    if current_user.is_authenticated:
        if path == '/login':
            return dmc.Group(children=[dcc.Link("Logout", href="/logout")]), '/', navbar
        profile_menu = dmc.Menu(
            [
                dmc.MenuTarget(dmc.Button("Profile", variant="subtle", c="black")),
                dmc.MenuDropdown(
                    [
                        dmc.Text(f"Hi, {current_user.id}!", ta="center", size="sm", fw=550),
                        dmc.MenuItem("Logout", href="/logout"),
                    ]
                ),
            ])
        #dmc.Group(children=[dmc.Text(f"Hi, {current_user.id}!"), dcc.Link("Logout", href="/logout")])
        return profile_menu, dash.no_update, navbar
    else:
        ### if page is restricted, redirect to login and save path
        if path in restricted_page:
            session['url'] = path
            return dcc.Link("Login", href="/login"), '/login', dash.no_update

    ### if path not login and logout display login link
    if current_user and path not in ['/login', '/logout']:
        return dcc.Link("Login", href="/login"), dash.no_update, navbar

    ### if path login and logout hide links
    if path in ['/login', '/logout']:
        return '', dash.no_update, dash.no_update

#dmc.Group(dmc.Text(f"Hi, {current_user.id}!"), )

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--host', type=str, default='192.168.101.44',
                        help='IP(v4) address of host machine where this Dashboard is hosted.')
    parser.add_argument('-p', '--port', type=str, default='9003',
                        help='Port to use')

    args = parser.parse_args()

    if args.host and args.port:
        app.run_server(host=args.host, port=args.port, debug=True)
    else:
        app.run_server(host='192.168.101.44', port='9003', debug=True)