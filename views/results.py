import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from server import app
import dash_table
import pandas as pd
import os
import json
from server import User

fpath_insurdb = os.path.join('./','insurdb1.xlsx')
fpath_insurmanager = os.path.join('./', 'insurmanager.xlsx')
fpath_search_results = './search_results.xlsx'

# 导入本地保存的保险公司/保单数据

# try:
#     df = pd.read_excel(fpath_search_results)[['company', 'insurance', 'maximum_coverage', 'policy_period', 'payment_term', 'intelligent_underwriting', 'features']]
# except Exception as e:
#     print(pd.read_excel(fpath_insurdb))
#     df = pd.read_excel(fpath_insurdb)[['company', 'insurance', 'maximum_coverage', 'policy_period', 'payment_term', 'intelligent_underwriting', 'features']]

df = pd.read_excel(fpath_search_results)[['company', 'insurance', 'maximum_coverage', 'policy_period', 'payment_term', 'intelligent_underwriting', 'features']]
df['id'] = range(len(df))
df['insurance'] = df['insurance'] + ',' + df['features']
df = df[['id','company', 'insurance']]
all_options = {
    i: df.loc[df['company'] == i, 'insurance'].values.tolist() for i in df['company'].values.tolist()
}


with open('./test.json', 'w+') as f:
    json.dump(all_options, f)

# 推荐助手
layout = html.Div(children=[
    dcc.Location(id='url_results', refresh=True),
    html.Div(
        className="container",
        children=[
            dash_table.DataTable(
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                data=df.to_dict('records'),
                columns=[{
                    'id': c,
                    'name': c
                } for c in df.columns],
                tooltip_data=[{
                    column: {
                        'value': str(value),
                        'type': 'markdown'
                    }
                    for column, value in row.items()
                } for row in df.to_dict('records')],
                css=[{
                    'selector':
                    '.dash-table-tooltip',
                    'rule':
                    'background-color: grey; font-family: monospace; color: white'
                }],
                tooltip_delay=0,
                tooltip_duration=None),

            dcc.RadioItems(
                id='countries-radio',
                options=[{'label': k, 'value': k} for k in all_options.keys()],
                value=list(all_options.keys())[0]
            ),

            # html.Button(id='Confirm', children='Confirm', n_clicks=0),

            html.Hr(),

            dcc.RadioItems(id='cities-radio'),

            html.Hr(),

            html.Div(id='display-selected-values'),

            html.Hr(),

            dcc.ConfirmDialogProvider(
                children=html.Button('Share Medical Record',),
                id='retrieve_record',
                message='Better terms and conditions can be provided if you allow us to verify your health coditions based on your medical record on blockchain.'
            ),

            html.Button(id='confirm', children='Confirm', n_clicks=0),

            html.Button(id='back-to-homepage', children='Homepage', n_clicks=0)    # id cannot be the same
        ])
])

# 选择保险公司
@app.callback(
    Output('cities-radio', 'options'),
    Input('countries-radio', 'value'))
def set_company_options(selected_company):
    return [{'label': i, 'value': i} for i in all_options[selected_company]]

# 选择已选保险公司下的险种
@app.callback(
    Output('cities-radio', 'value'),
    Input('cities-radio', 'options'))
def set_company_value(available_options):
    return available_options[0]['value']

# 显示选择结果
@app.callback(
    Output('display-selected-values', 'children'),
    Input('countries-radio', 'value'),
    Input('cities-radio', 'value'))
def set_display_children(selected_country, selected_city):
    return u'You selected "{}" from "{}"'.format(
        selected_city, selected_country,
    )

@app.callback(Output('url_results', 'pathname'),
              Input('confirm', 'n_clicks'), 
              Input('back-to-homepage', 'n_clicks'), 
              Input('countries-radio', 'value'),
              Input('cities-radio', 'value')
              )
def update_output(n_clicks_confirm, n_clicks_homepage, selected_company, selected_product):
    if n_clicks_confirm > 0:
        # # insurdb = pd.read_excel(fpath_insurdb)

        # # product_info = insurdb.loc[(insurdb['company'] == selected_company) & (insurdb['insurance'] == selected_product), :]
        # product_info = df.loc[(df['company'] == selected_company) & (df['insurance'] == selected_product), :]

        # insurance, company = product_info.iloc[0]['insurance'], product_info.iloc[0]['company']

        # if not os.path.exists(fpath_insurmanager):
        #     pd.DataFrame(columns = ['User_id', 'company', 'insurance']).to_excel(fpath_insurmanager)
        # insurmanager = pd.read_excel(fpath_insurmanager)

        # with open('./user.txt', 'r') as f:
        #     user = f.read()
        # log = pd.DataFrame({'User_id':[user], 'company':[company], 'insurance':[insurance]})
        # if not len(insurmanager):
        #     insurmanager = log.copy()
        # insurmanager=insurmanager.append(log)

        # # 将选择的保险产品记录至本地的保单管理文件
        # insurmanager.to_excel(fpath_insurmanager, index=False)

        # 跳转至交易成功页面
        return '/transaction'

    if n_clicks_homepage > 0:

        # 跳转至首页
        return '/'
