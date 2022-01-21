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

fpath_insurdb = os.path.join('.', 'insurdb1.xlsx')
fpath_search_results = './search_results.xlsx'
fpath_jobtype = './job_type.xlsx'

jobs = pd.read_excel('job_type.xlsx')['Job']

options_jobs = [{'label':job, 'value':job} for job in jobs]
options_policy_period = [{'label': _, 'value': _} for _ in ['10 years', '20 years', '30 years', '35 years', '40', 'To 60 years old', 'To 65 years old', 'To 70 years old', 'To 75 years old', 'To 80 years old']]
options_payment_term = [{'label': _, 'value': _} for _ in ['pay off in one time', '5 years', '10 years', '15 years', '20 years', '30 years', '40 years', 'To 55 years old', 'To 60 years old', 'To 70 years old', 'To 75 years old']]

jobs = {}

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

                                dcc.Dropdown(id="gender", options=[{'label':'M', 'value':'M'}, {'label':'F', 'value':'F'}], placeholder="gender"),

                                html.Hr(),

                                dcc.Dropdown(id="age", options=[{'label':str(i), 'value':i} for i in range(0, 100)], placeholder="Age"),

                                html.Hr(),

                                dcc.Dropdown(id="job", options=options_jobs, placeholder="Occupation"),

                                html.Hr(),

                                dcc.Dropdown(id="smoke", options=[{'label':'Yes', 'value':'Yes'}, {'label':'No', 'value':'No'}], placeholder="Do you smoke?"),

                                html.Hr(),

                                dcc.Dropdown(
                                    id='insurance_options',
                                    options=[{"label":"Critical Illness Insurance", "value":"Critical Illness Insurance"}],
                                    placeholder="Select Type of Insurance"
                                ),

                                html.Hr(),

                                dcc.Markdown('''
                                    Maximum Coverage
                                '''),
                                dcc.RangeSlider(
                                    id='maximum_coverage',
                                    min=150,
                                    max=350,
                                    value=[200, 250],
                                    tooltip={"placement": "bottom", "always_visible": False},
                                    marks={
                                        150: {'label': '$1,500,000', 'style': {'color': '#77b0b1'}},
                                        250: {'label': '$2,500,000'},
                                        350: {'label': '$3,500,000', 'style': {'color': '#f50'}}
                                    }
                                    ),

                                html.Hr(),

                                dcc.Dropdown(id="policy_period", options=options_policy_period, placeholder="Select Policy Period"),

                                html.Hr(),

                                dcc.Dropdown(id="payment_term", options=options_payment_term, placeholder="Select Payment Term"),

                                html.Hr(),

                                html.Div([
                                    html.Button(id='search', children='Search', n_clicks=0),
                                    html.Button(id='homepage3', children='Homepage', n_clicks=0)
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
              Input('search', 'n_clicks'),
              Input("age", 'value'),
              Input("smoke", 'value'),
              Input("maximum_coverage", 'value'),
              Input("payment_term", 'value'),
              Input("policy_period", 'value'),
              Input('homepage3', 'n_clicks')
              )
def update_output(submit_n_clicks, age, smoke, maximum_coverage, payment_term, policy_period, n_clciks_homepage3):

    # 跳转搜索结果页面
    if submit_n_clicks and submit_n_clicks > 0:
        df = pd.read_excel(fpath_insurdb)
        df['min_age'], df['max_age'] = df['age_group'].apply(lambda x: int(x.split('~')[0])), df['age_group'].apply(lambda x: int(x.split('~')[1]))


        df = df.loc[
            (df['min_age'] <= age) &
            (df['max_age'] >= age) &
            (maximum_coverage[0] <= df['maximum_coverage']) &
            (maximum_coverage[1] >= df['maximum_coverage']) &
            (df['smoking_habit'] == smoke) &
            (df['payment_term'] == payment_term) &
            (df['policy_period'] == policy_period) &
            (df['intelligent_underwriting'] == 'Medical History') &
            (df['occupations'] == '1-4'),
            :
        ]

        with open('test.txt', 'w') as f:
            f.write(''.join([str(age), str(maximum_coverage[0]), str(maximum_coverage[1]), smoke, payment_term, policy_period]))

        if len(df) > 0:
            df.to_excel(fpath_search_results, index=False)
        else:
            df.DataFrame().to_excel(fpath_search_results, index=False)
        return '/results'
    
    # 跳转首页
    if n_clciks_homepage3 and n_clciks_homepage3 > 0:
        return '/'

