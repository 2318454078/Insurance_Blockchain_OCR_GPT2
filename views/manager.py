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

# 导入本地已购买保单
fpath_insurmanager = os.path.join('./', 'insurmanager.xlsx')
df = pd.read_excel(fpath_insurmanager)
df = df[df.columns[1:]]

# 保单管理
layout = html.Div(children=[
    dcc.Location(id='url_tmp', refresh=True),
    html.Div(
        className="container",
        children=[
            dcc.Markdown('''
                My insurance
            '''),
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'id': c, 'name': c} for c in df.columns],
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items()
                    } for row in df.to_dict('records')
                ],
                css=[{
                    'selector': '.dash-table-tooltip',
                    'rule': 'background-color: grey; font-family: monospace; color: white'
                }],

                tooltip_delay=0,
                tooltip_duration=None
            ),
            html.Button(id='homepage2', children='Homepage', n_clicks=0)
        ]
    )
])

# 返回首页
@app.callback(Output('url_tmp', 'pathname'),
              [Input('homepage2', 'n_clicks')])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return '/'
