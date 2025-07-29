import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from urllib.request import urlopen
import plotly.express as px
import re

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

url = "https://drive.google.com/uc?export=download&id=1ZdH5C3kWaiRR3fOotvdW8l351YrKQJgG"
df = pd.read_csv(url)


def graphParallel():
    cols = [
        "Fine Amount",
        "Penalty Amount",
        "Interest Amount",
        "Reduction Amount",
        "Payment Amount",
    ]
    df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")
    grouped = df.groupby(cols + ["Violation"]).size().reset_index(name="Count")
    grouped["Violation_Code"] = grouped["Violation"].astype("category").cat.codes
    fig = px.parallel_coordinates(
        grouped,
        dimensions=cols,
        color="Violation_Code",
        color_continuous_scale=px.colors.qualitative.Set3,
        labels={col: col.replace("_", " ") for col in cols},
    )
    fig.update_layout(
        template="plotly_dark",
        coloraxis_showscale=False,
    )
    return fig


def parse_violation_time(vtime):
    if isinstance(vtime, str):
        vtime = vtime.strip().upper().replace(" ", "")
        match = re.match(r"^(\d{1,2}):(\d{2})([AP])$", vtime)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            meridian = match.group(3)
            if meridian == "P" and hour != 12:
                hour += 12
            elif meridian == "A" and hour == 12:
                hour = 0
            return hour
    return None


def graphHeatmap():
    df["Violation Hour"] = df["Violation Time"].apply(parse_violation_time)
    df_grouped = (
        df.groupby(["Violation", "Violation Hour"]).size().reset_index(name="count")
    )
    df_pivot = df_grouped.pivot(
        index="Violation", columns="Violation Hour", values="count"
    ).fillna(0)
    df_pivot = df_pivot.reindex(columns=range(1, 25), fill_value=0)
    df_z = df_pivot.copy()
    df_z = (df_z - df_z.mean(axis=1).values.reshape(-1, 1)) / df_z.std(axis=1).replace(
        0, 1
    ).values.reshape(-1, 1)
    fig = px.imshow(
        df_z,
        labels=dict(x="Hour of Day (1-24)", y="Violation Type", color="Z-score"),
        color_continuous_scale="blues",
        template="plotly_dark",
        height=450,
    )

    fig.update_xaxes(tickmode="linear", dtick=1)
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
                                className="fa-solid fa-circle-arrow-left fa-2xl text-white",
                            ),
                            className="rounded-pill btn-link px-2 col",
                            outline=True,
                            id="prev",
                            n_clicks=0,
                        ),
                        dbc.Button(
                            html.I(
                                id="icon-next",
                                className="fa-solid fa-circle-arrow-right fa-3x text-white",
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
                html.H5(id="title-plot", className="px-2 my-0 py-0 text-white fw-bold"),
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
                html.H3("Open Parking and Camera Violations", className="p-2"),
                html.Span(
                    "STORY Week 24 FF 2025",
                    className="ms-auto",
                    style={"fontSize": "smaller", "color": "gray"},
                ),
            ],
            className="container text-center d-flex",
        ),
        html.Div(
            [slider_plot, carousel, sub_controls, plot], className="bg-dark container"
        ),
    ],
    fluid=True,
    className="bg-dark text-info vh-100",
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
        html.Div([dcc.Graph(figure=graphParallel(), config=config)]),
        html.Div([dcc.Graph(figure=graphHeatmap(), config=config)]),
    ]
    text = [
        (
            "Traffic Fines: Parallel Comparison of Monetary Amounts by Violation",
            "Each line represents a unique combination of monetary values and its corresponding violation type",
        ),
        (
            "Hourly Patterns of Traffic Violations",
            "Z-score by violation type across the day",
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
