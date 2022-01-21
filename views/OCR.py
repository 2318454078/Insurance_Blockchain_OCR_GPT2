import base64
import datetime
import io
import os.path
from io import StringIO

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from server import app
from flask_login import logout_user, current_user
import requests
import csv


filepath = './policy.jpg'

layout = html.Div(children=[
    dcc.Location(id='url_OCR', refresh=True),
    html.Div(
    className="container",
    children=[
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select the policy file '),'for OCR scanning (JPG\PNG\JPEG\BMP format)'
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Hr(),
    html.Button(id='go-to-homepage4', children='homepage', n_clicks=0),
    html.Div(id='output-data-upload'),
    html.Hr(),
    dcc.ConfirmDialogProvider(
        children=html.Button('Store electronic insurance policies',),
        id='store',
        message='Archived successfully!'
    ),
    html.Div(id='store_out')

    ])
])

result_company = ''
result_InsBilNo = ''
result_InsBilTim = ''
result_InsTolAmt = ''
result_InsCltNa1 = ''
result_InsIdcNb1 = ''
result_InsIdcTy1 = ''
result_InsCltNa2 = ''
result_InsIdcNb2 = ''
result_InsBthDa2 = ''
result_InsIdcTy2 = ''
result_InsCovDur = ''
result_InsIcvAmt = ''
result_InsPayDur = ''
result_InsPayFeq = ''
result_InsPerAmt = ''
result_InsPrdNam = ''
result_BenCltNa = ''

def parse_contents(contents, filename, date):
    try:
        if 'jpg' in filename or 'jpeg' in filename or 'png' in filename or 'bmp' in filename:
            # 解析PDF文件内容
            content_type, content_string = contents.split(',')
            filedata = base64.b64decode(content_string)
            with open(filepath, 'wb') as out_file:
                out_file.write(filedata)
            request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/insurance_documents"
            # 二进制方式打开图片文件
            f = open(filepath, 'rb')
            image = base64.b64encode(f.read())
            host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=GGj6SdRY7FhrGZPYkpLouwEi&client_secret=q9W3bKfG8oPlqjT1NX0WGKdQmbIIPH9e'
            response = requests.get(host)
            params = {"image": image}
            access_token_json = response.json()
            access_token = access_token_json["access_token"]
            request_url = request_url + "?access_token=" + access_token
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(request_url, data=params, headers=headers)
            # 保存OCR数据
            if response:
                result_data = response.json()['words_result']
                global result_company
                global result_InsBilNo
                global result_InsBilTim
                global result_InsTolAmt
                global result_InsCltNa1
                global result_InsIdcNb1
                global result_InsIdcTy1
                global result_InsCltNa2
                global result_InsIdcNb2
                global result_InsBthDa2
                global result_InsIdcTy2
                global result_InsCovDur
                global result_InsIcvAmt
                global result_InsPayDur
                global result_InsPayFeq
                global result_InsPerAmt
                global result_InsPrdNam
                global result_BenCltNa
                result_company = result_data.get('InsBilCom')
                result_InsBilNo = result_data.get('InsBilNo')
                result_InsBilTim = result_data.get('InsBilTim')
                result_InsTolAmt = result_data.get('InsTolAmt')
                result_InsCltNa1 = result_data.get('InsCltNa1')
                result_InsIdcNb1 = result_data.get('InsIdcNb1')
                result_InsIdcTy1 = result_data.get('InsIdcTy1')
                result_InsCltNa2 = result_data.get('InsPerLst')[0].get('InsCltNa2')
                result_InsIdcNb2 = result_data.get('InsPerLst')[0].get('InsCltNb2')
                result_InsBthDa2 = result_data.get('InsPerLst')[0].get('InsBthDa2')
                result_InsIdcTy2 = result_data.get('InsPerLst')[0].get('InsIdcTy2')
                result_InsCovDur = result_data.get('InsPrdList')[0].get('InsCovDur')
                result_InsIcvAmt = result_data.get('InsPrdList')[0].get('InsIcvAmt')
                result_InsPayDur = result_data.get('InsPrdList')[0].get('InsPayDur')
                result_InsPayFeq = result_data.get('InsPrdList')[0].get('InsPayFeq')
                result_InsPerAmt = result_data.get('InsPrdList')[0].get('InsPerAmt')
                result_InsPrdNam = result_data.get('InsPrdList')[0].get('InsPrdNam')
                result_BenCltNa = result_data.get('BenPerLst')[0].get('BenCltNa')

                # 根据提取内容制作表格，返回值为html.table
                row1 = html.Tr([html.Td("Company Name"), html.Td(result_company)])
                row2 = html.Tr(
                    [html.Td("Insurance policy number"), html.Td(result_InsBilNo)])
                row3 = html.Tr(
                    [html.Td("Insured amount"), html.Td(result_InsTolAmt)])
                row4 = html.Tr([html.Td("Policyholder"), html.Td(result_InsCltNa1)])
                row5 = html.Tr([html.Td("Effective date of the policy"),
                                html.Td(result_InsBilTim)])
                row6 = html.Tr([html.Td("ID number of the Policyholder"),
                                html.Td(result_InsIdcNb1)])
                row7 = html.Tr([html.Td("Type of Policyholder's Document"),
                                html.Td(result_InsIdcTy1)])

                row8 = html.Tr([html.Td("The insured"), html.Td(result_InsCltNa2)])
                row9 = html.Tr(
                    [html.Td("ID number of the insured"), html.Td(result_InsIdcNb2)])
                row9_1 = html.Tr([html.Td("Date of Birth of the Insured"),
                                  html.Td(result_InsBthDa2)])
                row9_2 = html.Tr([html.Td("Type of Insured's Document"),
                                  html.Td(result_InsIdcTy2)])

                row10 = html.Tr(
                    [html.Td("Insurance period"), html.Td(result_InsCovDur, style={"word-break": "break-all"})])
                row11 = html.Tr(
                    [html.Td("Basic insurance amount"), html.Td(result_InsIcvAmt, style={"word-break": "break-all"})])
                row12 = html.Tr(
                    [html.Td("Payment period"), html.Td(result_InsPayDur, style={"word-break": "break-all"})])
                row13 = html.Tr(
                    [html.Td("Frequency of payment"), html.Td(result_InsPayFeq, style={"word-break": "break-all"})])
                row14 = html.Tr([html.Td("Amount of payment per period"),
                                 html.Td(result_InsPerAmt, style={"word-break": "break-all"})])
                row15 = html.Tr([html.Td("Product name"), html.Td(result_InsPrdNam, style={"word-break": "break-all"})])

                row16 = html.Tr(
                    [html.Td("Beneficiary's name"), html.Td(result_BenCltNa, style={"word-break": "break-all"})])

                table_body1 = [html.Tbody([row1, row2, row3, row4, row5, row6, row7])]
                table1 = dbc.Table(table_body1, bordered=True)

                table_body2 = [html.Tbody([row8, row9, row9_1, row9_2])]
                table2 = dbc.Table(table_body2, bordered=True)

                table_body3 = [html.Tbody([row15, row10, row11, row12, row13, row14])]
                table3 = dbc.Table(table_body3, bordered=True)

                table_body4 = [html.Tbody([row16])]
                table4 = dbc.Table(table_body4, bordered=True)
        else:
            return html.Div([
                dbc.Alert("Please upload pictures in jpg/jpeg/png/bmp format", color="danger")
            ])
    except Exception as e:
        print(e)
        return html.Div([
            dbc.Alert('There was an error processing this file.', color="danger")
        ])

    return html.Div([
        html.H2('basic information'),
        html.Hr(),
        table1,
        html.H2('Insured Information'),
        html.Hr(),
        table2,
        html.H2('Insurance information'),
        html.Hr(),
        table3,
        html.H2('Beneficiary information'),
        html.Hr(),
        table4,
    ]
    )


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(Output('url_OCR', 'pathname'),
              [Input('go-to-homepage4', 'n_clicks')])
def logout_dashboard(n_clicks_homepage):
    if n_clicks_homepage and n_clicks_homepage > 0:

        # 返回首页
        return '/'

@app.callback(Output('store_out', 'children'),
              [Input('store', 'submit_n_clicks')])
def store(n_clicks_store):
    global username
    if n_clicks_store and n_clicks_store > 0:
        if current_user.is_authenticated:
            username = current_user.username
        f_out = open('./'+username+'_policy.csv', 'a+', encoding='utf-8-sig')
        csv_writer = csv.writer(f_out)
        if os.path.getsize('./'+username+'_policy.csv'):
            csv_writer.writerow([username, result_company, result_InsBilNo, result_InsTolAmt, result_InsCltNa1, result_InsBilTim,
                                 result_InsIdcNb1, result_InsIdcTy1, result_InsCltNa2, result_InsIdcNb2,
                                 result_InsBthDa2, result_InsIdcTy2, result_InsCovDur, result_InsIcvAmt,
                                 result_InsPayDur, result_InsPayFeq, result_InsPerAmt, result_InsPrdNam,
                                 result_BenCltNa])
        else:
            csv_writer.writerow(["username", "Company Name", "Insurance policy number", "Insured amount", 'Policyholder', 'Effective date of the policy' ,'ID number of the Policyholder ', 'Type of Policyholder\'s Document', 'The insured', 'ID number of the insured', 'Date of Birth of the Insured', 'Type of Insured\'s Document', 'Insurance period', 'Basic insurance amount', 'Payment period', 'Frequency of payment', 'Amount of payment per period', 'Product name', 'Beneficiary\'s name'])
            csv_writer.writerow([username, result_company, result_InsBilNo, result_InsTolAmt, result_InsCltNa1, result_InsBilTim,
                                 result_InsIdcNb1, result_InsIdcTy1, result_InsCltNa2, result_InsIdcNb2,
                                 result_InsBthDa2, result_InsIdcTy2, result_InsCovDur, result_InsIcvAmt,
                                 result_InsPayDur, result_InsPayFeq, result_InsPerAmt, result_InsPrdNam,
                                 result_BenCltNa])

        # 返回OK
        return ''

