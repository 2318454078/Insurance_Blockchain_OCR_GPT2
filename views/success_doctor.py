import warnings
# Dash configuration
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from server import app

warnings.filterwarnings("ignore")

# 医生登陆成功页面
layout = html.Div(children=[
    dcc.Location(id='url_login_success_doctor', refresh=True),
    html.Div(
        className="container",
        children=[
            html.Div(
                html.Div(
                    className="row",
                    children=[
                        html.Div(
                            className="ten columns",
                            children=[
                                html.Br(),
                                html.Div('Login successfull'),
                            ]
                        ),
                        html.Div(
                            className="two columns",
                            # children=html.A(html.Button('LogOut'), href='/')
                            children=[
                                html.Br(),
                                html.Button(id='back-button', children='Back', n_clicks=0),
                                html.Br(),
                                html.Button(id='database-button', children='Database', n_clicks=0)
                            ]
                        )
                    ]
                )
            )
        ]
    )
])


@app.callback(Output('url_login_success_doctor', 'pathname'),
              [Input('back-button', 'n_clicks'), 
              Input('database-button', 'n_clicks')]
            )
def logout_dashboard(n_clicks_back, n_clicks_database):
    if n_clicks_back and n_clicks_back > 0:

        # 返回首页
        return '/'
    elif n_clicks_database and n_clicks_database > 0:

        # 返回就诊记录页面
        return '/database'

