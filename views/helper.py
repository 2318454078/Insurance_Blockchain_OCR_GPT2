import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import torch
from ask_utils.utils import  GPT2Model, GPT2Tokenizer, ask_question
from server import app

def Header(name, app):
    title = html.H1(name, style={"margin-top": 5})
    return dbc.Row([dbc.Col(title, md=8)])


def textbox(text, box="AI", name="CHZMGL"):
    text = text.replace(f"{name}:", "").replace("You:", "")
    style = {
        "max-width": "30%",
        # "width": "max-content",
        "padding": "10px 10px",
        "border-radius": 20,
        "margin-bottom": 100,
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = 0

        return dbc.Card(text, style=style, body=True, color="primary", inverse=True)

    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "auto"

        thumbnail = html.Img(
            src=app.get_asset_url("CHZMGL.jpg"),
            style={
                "border-radius": 50,
                "height": 36,
                "margin-right": 5,
                "float": "left",
            },
        )
        textbox = dbc.Card(text, style=style, body=True, color="light", inverse=False)

        return html.Div([thumbnail, textbox])

    else:
        raise ValueError("Incorrect option for `box`.")


# load model and tokenizer
model = GPT2Model(
    vocab_size=30000,
    layer_size=12,
    block_size=1024,
    embedding_dropout=0.0,
    embedding_size=768,
    num_attention_heads=12,
    attention_dropout=0.0,
    residual_dropout=0.0)

state_dict = torch.load('./ask_utils/model.pth', map_location='cpu')
model.load_state_dict(state_dict)
model.eval()

tokenizer = GPT2Tokenizer(
    'ask_utils/bpe/vocab.json',
    'ask_utils/bpe/chinese_vocab.model',
    max_len=512)

# Define Layout
conversation = html.Div(
    html.Div(id="display-conversation"),
    style={
        "overflow-y": "auto",
        "display": "flex",
        "height": "calc(90vh - 132px)",
        "flex-direction": "column-reverse",
    },
)

controls = dbc.InputGroup(
    children=[
        dbc.Input(id="user-input", placeholder="Write to the chatbot...", type="text"),
        dbc.InputGroupAddon(dbc.Button("Submit", id="submit"), addon_type="append"),
    ]
)

layout = dbc.Container(
    fluid=False,
    children=[
        Header("Intelligent assistant", app),
        html.Hr(),
        dcc.Store(id="store-conversation", data=""),
        conversation,
        controls,
        dbc.Spinner(html.Div(id="loading-component")),
    ],
)


@app.callback(
    Output("display-conversation", "children"), [Input("store-conversation", "data")]
)
def update_display(chat_history):
    return [
        textbox(x, box="user") if i % 2 == 0 else textbox(x, box="AI")
        for i, x in enumerate(chat_history.split("<split>")[:-1])
    ]


@app.callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
)
def clear_input(n_clicks, n_submit):
    return ""


@app.callback(
    [Output("store-conversation", "data"), Output("loading-component", "children")],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-conversation", "data")],
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history):
    if n_clicks == 0 and n_submit is None:
        return "", None

    if user_input is None or user_input == "":
        return chat_history, None

    name = "CHZMGL"

    # First add the user input to the chat history
    chat_history += f"You: {user_input}<split>{name}:"

    model_input = user_input

    model_output = ask_question(model, tokenizer, model_input, max_len=40)

    chat_history += f"{model_output}<split>"

    return chat_history, None