import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import pandas as pd
from pathlib import PosixPath
import pathlib

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH: PosixPath = PATH.joinpath('../../pdf_files/jszwfw').resolve()

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)


def get_dept_list():
    res = list()
    for child in DATA_PATH.iterdir():
        dept_name = child.name
        for file in child.iterdir():
            if file.suffix == '.csv':
                res.append(dept_name)
                continue
    return res


dept_list = get_dept_list()


def get_all_dept():
    print('='*10)
    print(DATA_PATH)
    for child in DATA_PATH.iterdir():
        dept_name = child.name
        print(' ' * 6, child.name)
        for file in child.iterdir():
            if file.suffix == '.csv':
                print('csv', file)
                return to_df(dept_name, file)
        print(child)


def to_df(dept_name, csv_file):
    df = pd.read_csv(csv_file, index_col=0)
    return df


def description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Clinical Analytics"),
            html.H3("Welcome to the Clinical Analytics Dashboard"),
            html.Div(
                id="intro",
                children="Explore clinic patient volume by time of day, waiting time, and care score. Click on the heatmap to visualize patient experience at different time points.",
            ),
        ],
    )


def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.P("Select Department"),
            dcc.Dropdown(
                id="dept-select",
                options=[{"label": i, "value": i} for i in dept_list],
                value=dept_list[0],
            ),
            html.Br()

        ],
    )


def generate_table(dataframe: pd.DataFrame, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


def run():
    get_all_dept()
    pass


# app.layout = html.Div(children=[
#     html.H4(children='US Agriculture Exports (2011)'),
#     generate_table(get_all_dept())
# ])

app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            className="budget-banner",
            id="banner",
            children=[
                html.A(
                    id="dashbudget-logo",
                    children=[
                        html.Img(src=app.get_asset_url("dashbudget_logo_transparent.png"))
                    ],
                    href="/Portal",
                ),
                html.H2("政府部门预算公开"),
                html.A(
                    id="gh-link",
                    children=["View on GitHub"],
                    href="https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-pk-calc",
                    style={"color": "white", "border": "solid 1px white"},
                ),
                html.Img(src=app.get_asset_url("GitHub-Mark-Light-64px.png")),
            ],
        ),
        # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=[description_card(), generate_control_card()]
        ),
        # Right column
        html.Div(
            id="right-column",
            className="eight columns",
            children=[

            ],
        ),
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
