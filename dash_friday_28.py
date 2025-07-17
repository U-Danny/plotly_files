import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA


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

url = "https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2025/week-28/CPI-historical.csv"
df_hist = pd.read_csv(url)


def graphScatter():
    df = df_hist.copy()
    df_anim = []
    for year in sorted(df["Year"].unique()):
        df_year = df[df["Year"] == year].copy()
        df_year = df_year.sort_values(by="CPI score")
        df_year["r"] = df_year["CPI score"]
        df_year["theta"] = np.linspace(2, 1440, len(df_year), endpoint=False)
        df_anim.append(df_year)
    df_spiral = pd.concat(df_anim, ignore_index=True)
    df_spiral["size"] = 50
    fig = px.scatter_polar(
        df_spiral,
        r="r",
        theta="theta",
        color="Region",
        size="size",
        hover_name="Country / Territory",
        hover_data={"CPI score": True},
        animation_frame="Year",
        color_discrete_sequence=px.colors.qualitative.Prism,
        size_max=7,
    )
    fig.update_layout(
        template="plotly_dark",
        polar=dict(
            radialaxis=dict(
                visible=True,
                title="",
                showline=False,
                showticklabels=True,
                ticks="",
            ),
            angularaxis=dict(visible=False),
        ),
        showlegend=True,
        margin=dict(l=5, r=5, t=15, b=5),
        height=430,
        title="",
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                showline=False,
                title="",
                tickmode="array",
                tickvals=[0, 50, 90],
                ticktext=["0", "50", "90"],
                ticks="",
            ),
            angularaxis=dict(visible=False),
        )
    )
    return fig


def graphPCA():
    df = df_hist.copy()
    variables = ["CPI score", "Rank"]
    df = df.dropna(subset=variables)
    pca_results = pd.DataFrame()
    for year in sorted(df["Year"].unique()):
        df_year = df[df["Year"] == year].copy()
        X = df_year[variables].values
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X)
        df_year["PC1"] = X_pca[:, 0]
        df_year["PC2"] = X_pca[:, 1]
        pca_results = pd.concat([pca_results, df_year], axis=0)
    fig = px.scatter(
        pca_results,
        x="PC1",
        y="PC2",
        color="Region",
        animation_frame="Year",
        hover_name="Country / Territory",
        color_discrete_sequence=px.colors.qualitative.Prism,
        labels={
            "PC1": "Structural Gradient of Corruption",
            "PC2": "Relative Divergence of Rankings",
        },
    )
    fig.update_traces(marker=dict(size=8, line=dict(width=0.2, color="gray")))
    fig.update_layout(
        height=430, title="", template="plotly_dark", legend_title="Region"
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
                html.H6(
                    id="sub-title-plot",
                    className="px-2 my-0 py-0 text-wrap text-sm-nowrap",
                    style={"width": "1000px"},
                ),
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
                html.H3(
                    "How Has the Perception of Country-Level Corruption Changed Over Time?",
                    className="p-2",
                ),
                html.Span(
                    "STORY Week 28 FF 2025",
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
        html.Div([dcc.Graph(figure=graphScatter(), config=config)]),
        html.Div([dcc.Graph(figure=graphPCA(), config=config)]),
    ]
    text = [
        (
            "Global Spiral of Corruption Perception Over Time",
            "Visualizes the evolution of countries' CPI scores over time using a spiral layout. Radial distance represents corruption perception; colors denote regions.",
        ),
        (
            "Corruption Index vs. Ranking — PCA Spatial Representation",
            "Displays countries' CPI and rank compressed into two PCA components, revealing spatial patterns in corruption perception and standings.",
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
