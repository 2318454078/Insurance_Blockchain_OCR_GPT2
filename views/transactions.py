import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import date

from server import app
from initialize_blockchain import *
blockchain = initialize_blockchain()
from load_blockchain import *
import pickle
import dash
import dash_table
import pandas as pd
from collections import OrderedDict
import os

# 打开本地保单管理文件
fpath_insurmanager = os.path.join('./', 'insurmanager.xlsx')

if not os.path.exists(fpath_insurmanager):
    pd.DataFrame(columns = ['User_id', 'Product', 'Insurance_company', 'Coverage']).to_excel(fpath_insurmanager)
df = pd.read_excel(fpath_insurmanager)

# 交易成功界面
layout = html.Div(children=[
    dcc.Location(id='url_transactions', refresh=True),
    html.Div(
        className="container",
        children=[
            dcc.Markdown('''
                Done! Staff from the insurance company would contact your soon. Please mind the SMSs and phone calls received.
            '''),
            html.Button(id='go-to-homepage1', children='homepage', n_clicks=0)
        ]
    )
])

@app.callback(Output('url_transactions', 'pathname'),
              [Input('go-to-homepage1', 'n_clicks')])
def logout_dashboard(n_clicks_homepage):
    if n_clicks_homepage and n_clicks_homepage > 0:

        # 返回首页
        return '/'
