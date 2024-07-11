import dash
from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

dash.register_page(__name__)
from dash_iconify import DashIconify

big_button_style_enabled = {
    'background-color': '#2d82b5', 
    'color': 'white',  # Text color
    'border':'solid',
    'border-width': '1px',
    'border-color': '#A9A9A9',
    'padding': '6px 20px',  # Padding to adjust button size
    'text-align': 'center',
    'text-decoration': 'none',
    'display': 'inline-block',
    'font-size': '14px',  # Decreased font size
    'width':'100%',
    'margin-top':'20px',
}



# Login screen
layout = dmc.Center(
    dmc.Paper(
        html.Form(
            [
                dmc.Title("MSRS Dashboard Login", order=2, id="h3", style={"textAlign": "center"}),
                dmc.Space(h=30),
                dmc.TextInput(placeholder="Enter your username", id="uname-box", label="Username", required=True, name='username'),
                dmc.PasswordInput(placeholder="Enter your password", id="pwd-box", label="Password", required=True, name='password', leftSection=DashIconify(icon="bi:shield-lock")),
                html.Button("Login", id="login-button", type="submit", style=big_button_style_enabled),
                dmc.Text("", id="output-state")
            ],
            method='POST',
            action='/login',
            style={"width": "100%"}
        ),
        withBorder=True,
        shadow="sm",
        radius="md",
        p="lg",
        style={"width": "400px"} # ", textAlign": "center"
    ),
    style={"height": "50vh", "display": "flex", "alignItems": "center", "justifyContent": "center"}
)