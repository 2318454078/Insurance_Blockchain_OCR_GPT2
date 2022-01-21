import warnings
# Dash configuration
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from server import app

warnings.filterwarnings("ignore")

# 患者（投保人）登陆成功页面
layout = html.Div(children=[
    dcc.Location(id='url_login_success_patient', refresh=True),
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
                                html.Button(id='back-button', children='Logout', n_clicks=0),
                                html.Br(),
                                html.Button(id='shop-button', children='Go to InsurShop', n_clicks=0),
                                html.Br(),
                                html.Button(id='go-to-insurmanager', children='Go to InsurManager', n_clicks=0),
                                html.Br(),
                                html.Button(id='go-to-insurhelper', children='Go to InsurHelper', n_clicks=0),
                                html.Br(),
                                html.Button(id='go-to-insurOCR', children='Go to InsurOCR', n_clicks=0),
                            ]
                        )
                    ]
                )
            )
        ]
    )
])


@app.callback(Output('url_login_success_patient', 'pathname'),
              [Input('back-button', 'n_clicks'),
               Input('shop-button', 'n_clicks'),
               Input('go-to-insurmanager', 'n_clicks'),
               Input('go-to-insurhelper', 'n_clicks'),
               Input('go-to-insurOCR', 'n_clicks')])
def logout_dashboard(n_clicks, n_clicks_shop, n_clicks_insurmanager, n_clicks_insurhelper, n_clicks_insurOCR):
    if n_clicks > 0:

        # 返回首页
        return '/'
    elif n_clicks_shop and n_clicks_shop > 0:
        # 返回保险购买页面
        return '/shop'
    elif n_clicks_insurmanager and n_clicks_insurmanager > 0:
        # 返回保单管理页面
        return '/manager'
    elif n_clicks_insurhelper and n_clicks_insurhelper > 0:
        # 返回保单管理页面
        return '/helper'
    elif n_clicks_insurOCR and n_clicks_insurOCR > 0:
        # 返回保单管理页面
        return '/ocr'
