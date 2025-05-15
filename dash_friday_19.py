import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from urllib.request import urlopen
import json
import plotly.express as px
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
BS = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    dbc_css,
    BS,
    dbc.icons.FONT_AWESOME,
    dbc.icons.BOOTSTRAP,
]
config = {
    "displaylogo": False,
    "queueLength": 0,
    "responsive": True,
    "modeBarButtonsToRemove": [
        "zoom",
        "pan",
        "select",
        "zoomIn",
        "zoomOut",
        "autoScale",
        "resetScale",
        "lasso2d",
    ],
}

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2025/week-19/TLC_New_Driver_Application.csv"
)

status_map = {
    "Approved - License Issued": 1,
    "Denied": 0,
    "Incomplete": None,
    "Under Review": None,
}
df["Accepted"] = df["Status"].map(status_map)
df = df[df["Accepted"].notnull()]
cols = [
    "Drug Test",
    "WAV Course",
    "Defensive Driving",
    "Driver Exam",
    "Medical Clearance Form",
    # "FRU Interview Scheduled",
]
for col in cols:
    df[col] = df[col].map({"Complete": 1, "Needed": 0, "Not Applicable": 0})
df["App Date"] = pd.to_datetime(df["App Date"])
df["App Day"] = df["App Date"].dt.day
df["App Month"] = df["App Date"].dt.month
X = df[cols + ["App Day", "App Month"]]
y = df["Accepted"]

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

importances = model.feature_importances_
feat_df = pd.DataFrame({"Feature": X.columns, "Importance": importances}).sort_values(
    by="Importance", ascending=True
)


def graphBarForest():
    fig = px.bar(
        feat_df,
        x="Importance",
        y="Feature",
        orientation="h",
        color="Importance",
        color_continuous_scale="Viridis",
        template="seaborn",
        height=500,
    )
    fig.update_layout(showlegend=False, margin=dict(l=30, r=30, b=30, t=30))
    return fig


def graphHeatmap():
    cols = [
        "Drug Test",
        "WAV Course",
        "Defensive Driving",
        "Driver Exam",
        "Medical Clearance Form",
        # "App Day",
        "App Month",
        "Accepted",
    ]
    corr_matrix = df[cols].corr()

    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale="Blues",
        template="seaborn",
        aspect="auto",
        height=500,
    )

    fig.update_traces(texttemplate="%{text:.2f}")

    fig.update_layout(
        title="Mapa de calor de correlación entre variables y resultado Accepted",
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

carousel = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        dbc.Button(
                            html.I(
                                id="icon-prev",
                                className="fa-solid fa-circle-arrow-left fa-2xl text-dark",
                            ),
                            className="rounded-pill btn-link px-2 col",
                            outline=True,
                            id="prev",
                            n_clicks=0,
                        ),
                        dbc.Button(
                            html.I(
                                id="icon-next",
                                className="fa-solid fa-circle-arrow-right fa-3x text-dark",
                            ),
                            className="rounded-pill btn-link px-0 col my-0 py-0",
                            outline=True,
                            id="next",
                            n_clicks=0,
                        ),
                    ],
                    className="row py-0 my-0",
                ),
            ],
            className="p-1",
        ),
        html.Div(
            [
                html.H5(id="title-plot", className="px-2 my-0 py-0 text-dark fw-bold"),
                html.H6(id="sub-title-plot", className="px-2 my-0 py-0"),
            ],
            className="p-1 my-0 py-1",
        ),
    ],
    className="d-flex text-secondary my-0 py-0",
)

slider_plot = html.Div(
    [
        dbc.Progress(
            value=0,
            style={"height": "3px"},
            color="primary",
            className="mb-1 w-100",
            id="id-counter",
        ),
    ],
    className="my-0 py-0 w-100",
)

sub_controls = html.Div(
    [
        html.Div(
            [
                html.Small(
                    id="count-plot",
                    className="text-center mx-4 fw-bold my-0 py-0",
                    style={"fontSize": "smaller"},
                ),
            ],
            className="py-0 my-0",
        ),
    ],
    className="d-flex py-0 my-0",
)

plot = html.Div(
    [
        dcc.Loading(
            id="id-plots", color="#018E99", type="cube", style={"padding-top": "120px"}
        )
    ],
    className="my-0 py-0 border-top",
)

app.layout = dbc.Container(
    [
        html.Div(
            [
                html.H3("TLC Driver Application", className="p-2"),
                html.Span(
                    "STORY Week 19 FF 2025",
                    className="ms-auto",
                    style={"fontSize": "smaller", "color": "gray"},
                ),
            ],
            className="container text-center d-flex",
        ),
        html.Div(
            [slider_plot, carousel, sub_controls, plot], className="bg-light container"
        ),
    ],
    fluid=True,
    className="bg-white text-info vh-100",
)


@app.callback(
    [
        Output("id-plots", "children"),
        Output("title-plot", "children"),
        Output("sub-title-plot", "children"),
        Output("prev", "disabled"),
        Output("next", "disabled"),
        Output("count-plot", "children"),
        Output("prev", "n_clicks"),
        Output("next", "n_clicks"),
        Output("id-counter", "value"),
    ],
    [
        Input("prev", "n_clicks"),
        Input("next", "n_clicks"),
    ],
)
def display_click_data(prev, next):
    active_next = False
    active_prev = False
    plots = [
        html.Div([dcc.Graph(figure=graphBarForest(), config=config)]),
        html.Div([dcc.Graph(figure=graphHeatmap(), config=config)]),
    ]
    text = [
        (
            "Key Factors Determining the Approval of a TLC License",
            "Relative importance of each requirement in the prediction model based on historical applications.",
        ),
        (
            "Heatmap of Correlation Between Variables in the TLC License Approval Process",
            "Visualization of the statistical relationship between requirements, application date, and approval outcome.",
        ),
    ]

    if next - prev <= 0:
        active_prev = True
        prev = 0
        next = 0
        index = 0
    elif next - prev >= (len(text) - 1):
        active_next = True
        next = len(text) - 1
        prev = 0
        index = len(text) - 1
    else:
        index = next - prev
    counter = (100 / len(text)) * (index + 1)
    return [
        plots[index],
        text[index][0],
        text[index][1],
        active_prev,
        active_next,
        str(index + 1) + " de " + str(len(text)),
        prev,
        next,
        counter,
    ]


if __name__ == "__main__":
    app.run(debug=True)
