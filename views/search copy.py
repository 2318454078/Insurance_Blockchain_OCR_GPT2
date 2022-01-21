import warnings
# Dash configuration
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import date

from server import app
from initialize_blockchain import *
blockchain = initialize_blockchain()
from load_blockchain import *
import pickle
import os
import pandas as pd

fpath_insurdb = os.path.join('.', 'insurdb.xlsx')
fpath_search_results = './search_results.xlsx'

options = [
    {"label":"Critical Illness Insurance", "value":"Critical Illness Insurance"}
]

# 保险产品搜索页面
layout = html.Div(children=[
    dcc.Location(id='url_search', refresh=True),
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

                                dcc.Markdown('''
                                    ### Tell us something about yourself
                                '''),

                                dcc.Dropdown(id="gender", options=[{'label':'M', 'value':'M'}, {'label':'F', 'value':'F'}], placeholder="Your Gender"),

                                html.Hr(),

                                dcc.Dropdown(id="age", options=[{'label':str(i), 'value':str(i)} for i in range(18, 61)], placeholder="Your Age"),

                                html.Hr(),

                                dcc.Dropdown(id="job", options=[{'label':str(i), 'value':str(i)} for i in range(18, 61)], placeholder="Your Job"),

                                html.Hr(),

                                dcc.Dropdown(id="smoke", options=[{'label':str(i), 'value':str(i)} for i in range(18, 61)], placeholder="Do you smoke?"),

                                html.Hr(),

                                dcc.Dropdown(
                                    id='insurance_options',
                                    options=options,
                                    placeholder="Select Type of Insurance"
                                ),

                                html.Hr(),

                                dcc.Markdown('''
                                    Coverage
                                '''),
                                dcc.RangeSlider(
                                    id='coverage',
                                    min=100000,
                                    max=1000000,
                                    value=[200000, 400000],
                                    tooltip={"placement": "bottom", "always_visible": False},
                                    marks={
                                        100000: {'label': '$100,000', 'style': {'color': '#77b0b1'}},
                                        # 200000: {'label': '$200,000'},
                                        # 400000: {'label': '$400,000'},
                                        500000: {'label': '$500,000'},
                                        1000000: {'label': '$1000,000', 'style': {'color': '#f50'}}
                                    }
                                    ),

                                html.Hr(),

                                html.Button('Retrive My Medical Record', id='retrive_record_button', n_clicks=0),

                                html.Div(id='status'),

                                html.Hr(),

                                html.Div([
                                    dcc.ConfirmDialogProvider(
                                        children=html.Button('Submit',),
                                        id='danger-danger-provider',
                                        message='Are you sure all inputs are correct?'
                                    ),
                                    html.Button(id='homepage3', children='Search', n_clicks=0),
                                    html.Button(id='homepage4', children='Homepage', n_clicks=0)
                                ]
                            )
                            ]
                        )
                    ]
                )
            )
        ]
    )
])

@app.callback(Output('url_search', 'pathname'),
              Input('danger-danger-provider', 'submit_n_clicks'),
              Input('retrive_record_button', 'n_clicks'),
              Input("age", 'value'),
              Input("gender", 'value'),
              Input("coverage", 'value'),
              Input('homepage3', 'n_clicks')
              )
def update_output(submit_n_clicks, retrive_record_n_clicks, age, gender, coverage, n_clciks_homepage3):

    # 跳转搜索结果页面
    if submit_n_clicks and submit_n_clicks > 0:
        df = pd.read_excel(fpath_insurdb)
        df['min_age'], df['max_age'] = df['Age_group'].apply(lambda x: int(x.split('-')[0])), df['Age_group'].apply(lambda x: int(x.split('-')[1]))
        df = df.loc[
            (df['Gender'] == gender) & 
            (df['min_age'] <= int(age)) &
            (df['max_age'] >= int(age)) &
            (coverage[0] <= df['Coverage']) &
            (coverage[1] >= df['Coverage']),
            :
        ]
        df.to_excel(fpath_search_results, index=False)
        return '/results'
    
    # 跳转首页
    if n_clciks_homepage3 and n_clciks_homepage3 > 0:
        return '/'

