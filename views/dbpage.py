import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import date

from server import app
from initialize_blockchain import *
blockchain = initialize_blockchain()
from load_blockchain import *
import pickle

submit_n_clicks_last = 0

options = [
    {"label":"Normal", "value":"value"},
    {"label":"Adenoid Cystic Carcinoma", "value": "Adenoid Cystic Carcinoma"},
    {"label":"Adrenal Gland Cancer", "value": "Adrenal Gland Cancer"},
    {"label":"Amyloidosis", "value": "Amyloidosis"},
    {"label":"Anal Cancer", "value": "Anal Cancer"},
    {"label":"Ataxia-Telangiectasia", "value": "Ataxia-Telangiectasia"},
    {"label":"Atypical Mole Syndrome", "value": "Atypical Mole Syndrome"},
    {"label":"Basal Cell Carcinoma", "value": "Basal Cell Carcinoma"},
    {"label":"Bile Duct Cancer", "value": "Bile Duct Cancer"},
    {"label":"Birt Hogg Dube Syndrome", "value": "Birt Hogg Dube Syndrome"},
    {"label":"Bladder Cancer", "value": "Bladder Cancer"},
    {"label":"Bone Cancer", "value": "Bone Cancer"},
    {"label":"Brain Tumor", "value": "Brain Tumor"},
    {"label":"Breast Cancer", "value": "Breast Cancer"},
    {"label":"Breast Cancer in Men", "value": "Breast Cancer in Men"},
    {"label":"Carcinoid Tumor", "value": "Carcinoid Tumor"},
    {"label":"Cervical Cancer", "value": "Cervical Cancer"},
    {"label":"Colorectal Cancer", "value": "Colorectal Cancer"},
    {"label":"Ductal Carcinoma", "value": "Ductal Carcinoma"},
    {"label":"Endometrial Cancer", "value": "Endometrial Cancer"},
    {"label":"Esophageal Cancer", "value": "Esophageal Cancer"},
    {"label":"Gastric Cancer", "value": "Gastric Cancer"},
    {"label":"Gastrontestinal Stromal Tumor - GIST", "value": "Gastrontestinal Stromal Tumor - GIST"},
    {"label":"HER2-Positive Breast Cancer", "value": "HER2-Positive Breast Cancer"},
    {"label":"Islet Cell Tumor", "value": "Islet Cell Tumor"},
    {"label":"Juvenile Polyposis Syndrome", "value": "Juvenile Polyposis Syndrome"},
    {"label":"Kidney Cancer", "value": "Kidney Cancer"},
    {"label":"Laryngeal Cancer", "value": "Laryngeal Cancer"},
    {"label":"Leukemia - Acute Lymphoblastic Leukemia", "value": "Leukemia - Acute Lymphoblastic Leukemia"},
    {"label":"Leukemia - Acute Lymphocytic (ALL)", "value": "Leukemia - Acute Lymphocytic (ALL)"},
    {"label":"Leukemia - Acute Myeloid AML", "value": "Leukemia - Acute Myeloid AML"},
    {"label":"Leukemia - Adult", "value": "Leukemia - Adult"},
    {"label":"Leukemia - Childhood", "value": "Leukemia - Childhood"},
    {"label":"Leukemia - Chronic Lymphocytic - CLL", "value": "Leukemia - Chronic Lymphocytic - CLL"},
    {"label":"Leukemia - Chronic Myeloid - CML", "value": "Leukemia - Chronic Myeloid - CML"},
    {"label":"Liver Cancer", "value": "Liver Cancer"},
    {"label":"Lobular Carcinoma", "value": "Lobular Carcinoma"},
    {"label":"Lung Cancer", "value": "Lung Cancer"},
    {"label":"Lung Cancer - Small Cell", "value": "Lung Cancer - Small Cell"},
    {"label":"Lymphoma - Hodgkin's", "value": "Lymphoma - Hodgkin's"},
    {"label":"Lymphoma - Non-Hodgkin's", "value": "Lymphoma - Non-Hodgkin's"},
    {"label":"Malignant Glioma", "value": "Malignant Glioma"},
    {"label":"Melanoma", "value": "Melanoma"},
    {"label":"Meningioma", "value": "Meningioma"},
    {"label":"Multiple Myeloma", "value": "Multiple Myeloma"},
    {"label":"Myelodysplastic Syndrome (MDS)", "value": "Myelodysplastic Syndrome (MDS)"},
    {"label":"Nasopharyngeal Cancer", "value": "Nasopharyngeal Cancer"},
    {"label":"Neuroendocrine Tumor", "value": "Neuroendocrine Tumor"},
    {"label":"Oral Cancer", "value": "Oral Cancer"},
    {"label":"Osteosarcoma", "value": "Osteosarcoma"},
    {"label":"Ovarian Cancer", "value": "Ovarian Cancer"},
    {"label":"Pancreatic Cancer", "value": "Pancreatic Cancer"},
    {"label":"Pancreatic Neuroendocrine Tumors", "value": "Pancreatic Neuroendocrine Tumors"},
    {"label":"Parathyroid Cancer", "value": "Parathyroid Cancer"},
    {"label":"Penile Cancer", "value": "Penile Cancer"},
    {"label":"Peritoneal Cancer", "value": "Peritoneal Cancer"},
    {"label":"Peutz-Jeghers Syndrome", "value": "Peutz-Jeghers Syndrome"},
    {"label":"Pituitary Gland Tumor", "value": "Pituitary Gland Tumor"},
    {"label":"Polycythemia Vera", "value": "Polycythemia Vera"},
    {"label":"Prostate Cancer", "value": "Prostate Cancer"},
    {"label":"Renal Cell Carcinoma", "value": "Renal Cell Carcinoma"},
    {"label":"Retinoblastoma", "value": "Retinoblastoma"},
    {"label":"Salivary Gland Cancer", "value": "Salivary Gland Cancer"},
    {"label":"Sarcoma", "value": "Sarcoma"},
    {"label":"Sarcoma - Kaposi", "value": "Sarcoma - Kaposi"},
    {"label":"Skin Cancer", "value": "Skin Cancer"},
    {"label":"Small Intestine Cancer", "value": "Small Intestine Cancer"},
    {"label":"Stomach Cancer", "value": "Stomach Cancer"},
    {"label":"Testicular Cancer", "value": "Testicular Cancer"},
    {"label":"Thymoma", "value": "Thymoma"},
    {"label":"Thyroid Cancer", "value": "Thyroid Cancer"},
    {"label":"Uterine (Endometrial) Cancer", "value": "Uterine (Endometrial) Cancer"},
    {"label":"Vaginal Cancer", "value": "Vaginal Cancer"},
    {"label":"Wilms' Tumor", "value": "Wilms' Tumor"}
]

# 就诊记录页面
layout = html.Div(children=[
    dcc.Location(id='url_database', refresh=True),
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
                                dcc.Input(id="patient_name", type="text", placeholder="Patient Name"),
                                dcc.Input(id="patient_id", type="text", placeholder="Patient ID"),
                                dcc.Dropdown(
                                    id='diagnosis',
                                    options=options,
                                    placeholder="Diagnosis"
                                ),
                                dcc.DatePickerSingle(
                                    id='date',
                                    min_date_allowed=date(1995, 8, 5),
                                    max_date_allowed=date.today(),
                                    initial_visible_month=date.today(),
                                    date=date.today()
                                ),
                                html.Hr(),
                                html.Div(id="number-out"),
                            ]
                        ),
                        html.Div(
                            className="two columns",

                            children=[
                                dcc.ConfirmDialogProvider(
                                    children=html.Button('Submit',),
                                    id='danger-danger-provider',
                                    message='Are you sure all inputs are correct?'
                                )
                                # html.Div(id='output-provider')
                            ]
                        )
                    ]
                )
            ), 
            html.Div(id='output-provider')
        ]
    )
])

@app.callback(Output('output-provider', 'children'),
              Input('danger-danger-provider', 'submit_n_clicks'),
              Input('danger-danger-provider', 'submit_n_clicks_timestamp'),
              Input("patient_name", 'value'),
              Input("patient_id", 'value'),
              Input("diagnosis", 'value'),
              Input("date","value")
              )

# 将输入的数据转换为Hash代码，保存至区块链，并将区块链保存至本地
def update_output(submit_n_clicks, submit_n_clicks_timestamp, patient_name, patient_id, diagnosis, date):
    if not submit_n_clicks:
        return ''

    global submit_n_clicks_last
    
    if submit_n_clicks > submit_n_clicks_last:

        submit_n_clicks_last += 1

        # 导入区块链
        blockchain = load_blockchain()

        # 将数据转译为Hash，保存至区块
        transaction = MedicalRecord(patient_name=patient_name, patient_id=patient_id, diagnosis=diagnosis, date=date)
        block = Block(
            transactions=[transaction],
            prev_hash=blockchain.get_latest_block().hash)

        block.mine(difficulty=4)

        blockchain.add_block_to_chain(block)

        # 将区块导入区块链
        with open('bc.txt', 'wb') as f:
            pickle.dump(blockchain, f)

        return f"""A new block is added to blockchain.
                    Hash of the block:
                    {blockchain.chain[-1].hash}
        """
