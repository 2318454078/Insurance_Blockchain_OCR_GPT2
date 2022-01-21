# index page
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from server import app, server

# 用户登陆模块
from flask_login import logout_user, current_user
# 各功能模块
from views import success_patient, success_doctor, login, login_fd, logout, dbpage, search, results, transactions, manager, helper, OCR

# 网页Header设置
header = html.Div(
    className='header',
    children=html.Div(
        className='container-width',
        style={'height': '100%'},
        children=[
            html.Img(
                src='assets/dash-logo-stripe.svg',
                className='logo'
            ),
            html.Div(className='links', children=[
                html.Div(id='user-name', className='link'),
                html.Div(id='logout', className='link')
            ])
        ]
    )
)

app.layout = html.Div(
    [
        header,
        html.Div([
            html.Div(
                html.Div(id='page-content', className='content'),
                className='content-container'
            ),
        ], className='container-width'),
        dcc.Location(id='url', refresh=False),
    ]
)
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])

# 网页A返回网址-->根据返回的网址跳转到对应的网址B
def display_page(pathname):
    # 跳转至登陆页面
    if pathname == '/' or pathname == '/login':
        return login.layout
    
    # 跳转至用户登陆成功/失败页
    elif pathname == '/success_patient':
        if current_user.is_authenticated:
            return success_patient.layout
        else:
            return login_fd.layout

    # 跳转至医生登陆成功/失败页
    elif pathname == '/success_doctor':
        if current_user.is_authenticated:
            return success_doctor.layout
        else:
            return login_fd.layout
    # 跳转至logout页面
    elif pathname == '/logout':
        if current_user.is_authenticated:
            logout_user()
            return logout.layout
        else:
            return logout.layout
    
    # 跳转至就诊记录页面
    elif pathname == '/database':
        return dbpage.layout
    
    # 跳转至保险购买页面
    elif pathname == '/shop':
        return search.layout
    
    # 跳转至推荐助手页面
    elif pathname == '/results':
        return results.layout

    # 跳转至购买结果页面
    elif pathname == '/transaction':
        return transactions.layout

    # 跳转至保单管理页面
    elif pathname == '/manager':
        return manager.layout

    # 跳转至智能问答页面
    elif pathname == '/helper':
        return helper.layout

    # 跳转至OCR页面
    elif pathname == '/ocr':
        return OCR.layout

    # 其他：404
    else:
        return '404'

# Header部分的内容
@app.callback(
    Output('user-name', 'children'),
    [Input('page-content', 'children')])
def cur_user(input1):
    if current_user.is_authenticated:
        return html.Div('Current user: ' + current_user.username)
        # 'User authenticated' return username in get_id()
    else:
        return ''

# Header部分的内容
@app.callback(
    Output('logout', 'children'),
    [Input('page-content', 'children')])
def user_logout(input1):
    if current_user.is_authenticated:
        return html.A('Logout', href='/logout')
    else:
        return ''

if __name__ == '__main__':
    app.run_server(debug=True)
