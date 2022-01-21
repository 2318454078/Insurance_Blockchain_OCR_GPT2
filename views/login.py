import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from server import app, User
from flask_login import login_user
from werkzeug.security import check_password_hash

is_logged_in = False

# 登陆页面
layout = html.Div(
    children=[
        html.Div(
            className="container",
            children=[
                dcc.Location(id='url_shop', refresh=True),
                dcc.Location(id='url_manager', refresh=True),
                dcc.Location(id='url_login', refresh=True),
                html.Div('''Please log in to continue:''', id='h1'),
                html.Div(
                    # method='Post',
                    children=[
                        dcc.Input(
                            placeholder='Enter your username',
                            n_submit=0,
                            type='text',
                            id='uname-box'
                        ),
                        dcc.Input(
                            placeholder='Enter your password',
                            n_submit=0,
                            type='password',
                            id='pwd-box'
                        ),
                        html.Button(
                            children='Login',
                            n_clicks=0,
                            type='submit',
                            id='login-button'
                        ),
                        dcc.Dropdown(
                            id='demo-dropdown',
                            options=[
                                {'label': 'I am a doctor', 'value': 'doctor'},
                                {'label': 'I am a patient', 'value': 'patient'}
                            ],
                            value='patient'
                        ),
                        html.Hr(),
                        html.Button(children='InsurShop', id = 'insurshop', n_clicks=0),
                        html.Button(children='InsurManager', id = 'insurmanager', n_clicks=0),
                        # html.Button(children='InsurHelper', id = 'insurhelper', n_clicks=0),
                        # html.Button(children='InsurOCR', id = 'OCR', n_clicks=0),
                        html.Div(id='dd-output-container'),
                        html.Div(children='', id='output-state')
                    ]
                ),
            ]
        )
    ]
)

# 返回登陆成功
@app.callback(Output('url_login', 'pathname'),
              [Input('login-button', 'n_clicks'),
              Input('uname-box', 'n_submit'),
               Input('pwd-box', 'n_submit'),
               Input('demo-dropdown', 'value')],
              [State('uname-box', 'value'),
               State('pwd-box', 'value')])
def success(n_clicks, n_submit_uname, n_submit_pwd, role, input1, input2):

    user = User.query.filter_by(username=input1).first()

    if user:
        if check_password_hash(user.password, input2):
            login_user(user)
            global is_logged_in
            is_logged_in = True
            if role=='doctor':
                return '/success_doctor'
            else:
                return '/success_patient'
        else:
            pass
    else:
        pass

# 登陆失败
@app.callback(Output('output-state', 'children'),
              [Input('login-button', 'n_clicks'),
               Input('uname-box', 'n_submit'),
               Input('pwd-box', 'n_submit')],
              [State('uname-box', 'value'),
               State('pwd-box', 'value')])
def update_output(n_clicks, n_submit_uname, n_submit_pwd, input1, input2):
    if n_clicks > 0 or n_submit_uname > 0 or n_submit_pwd > 0:
        user = User.query.filter_by(username=input1).first()
        with open('./user.txt', 'w') as f:
            f.write(str(user.id))
        if user:
            if check_password_hash(user.password, input2):
                return ''
            else:
                return 'Incorrect username or password'
        else:
            return 'Incorrect username or password'
    else:
        return ''

# 返回购买保险页面
@app.callback(Output('url_shop', 'pathname'), Input('insurshop', 'n_clicks'))
def update_output1(n_clicks):
    global is_logged_in
    if n_clicks > 0 and is_logged_in:
        return '/shop'

# 返回保单管理页面
@app.callback(Output('url_manager', 'pathname'), Input('insurmanager', 'n_clicks'))
def update_output2(n_clicks):
    global is_logged_in
    if n_clicks > 0 and is_logged_in:
        return '/manager'

# # 返回智能助手页面
# @app.callback(Output('url_helper', 'pathname'), Input('insurhelper', 'n_clicks'))
# def update_output3(n_clicks):
#     global is_logged_in
#     if n_clicks > 0 and is_logged_in:
#         return '/helper'

# # 返回OCR页面
# @app.callback(Output('url_ocr', 'pathname'), Input('OCR', 'n_clicks'))
# def update_output4(n_clicks):
#     global is_logged_in
#     if n_clicks > 0 and is_logged_in:
#         return '/ocr'
