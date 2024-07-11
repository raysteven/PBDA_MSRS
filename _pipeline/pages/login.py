import dash
from dash import html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

dash.register_page(__name__)
from dash_iconify import DashIconify

# Login screen
layout = dmc.Center(
    dmc.Paper(
        html.Form(
            [
                dmc.Title("MSRS Dashboard Login", order=2, id="h3", style={"textAlign": "center"}),
                dmc.Space(h=30),
                dmc.TextInput(placeholder="Enter your username", id="uname-box", label="Username", required=True, name='username'),
                dmc.PasswordInput(placeholder="Enter your password", id="pwd-box", label="Password", required=True, name='password', leftSection=DashIconify(icon="bi:shield-lock")),
                html.Button("Login", id="login-button", type="submit", style={"width": "100%", "marginTop": "10px"}),
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