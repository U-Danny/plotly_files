import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from urllib.request import urlopen
import json
import plotly.express as px

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
    "toImageButtonOptions": {
        "format": "png",
        "filename": "I-Digital",
        "height": 500,
        "width": 700,
        "scale": 1,
    },
}


df_employer = pd.read_csv(
    "https://raw.githubusercontent.com/U-Danny/test-dataset/refs/heads/main/employers_years.csv"
)
with urlopen(
    "https://raw.githubusercontent.com/U-Danny/test-dataset/refs/heads/main/countries.geo.json"
) as response:
    countries = json.load(response)
df_nationality = pd.read_csv(
    "https://raw.githubusercontent.com/U-Danny/test-dataset/refs/heads/main/beneficiary_origin.csv"
)


def graphEmployer():
    fig = px.scatter(
        df_employer,
        x="employer_name",
        y="value",
        animation_frame="lottery_year",
        animation_group="employer_name",
        size="value",
        hover_name="employer_name",
        size_max=60,
    )
    fig.update_yaxes(title="Beneficiary registration")
    fig.update_xaxes(visible=False, showticklabels=False, showgrid=False, title="")
    fig.update_layout(
        showlegend=False, autosize=True, margin={"r": 40, "t": 40, "l": 60, "b": 40}
    )
    return fig


def graphMap():
    fig = px.choropleth_mapbox(
        df_nationality,
        geojson=countries,
        color="value",
        locations="country_of_nationality",
        opacity=1,
        mapbox_style="carto-positron",
        zoom=1,
        custom_data=["country", "value"],
        color_continuous_scale="dense",
        height=450,
        animation_frame="lottery_year",
    )
    fig.update_layout(autosize=True, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.layout.coloraxis.colorbar.title = "Beneficiary <br>"
    fig.layout.coloraxis.colorbar.ticksuffix = ""
    fig.layout.coloraxis.colorbar.lenmode = "fraction"
    fig.layout.coloraxis.colorbar.len = 0.9
    fig.layout.coloraxis.colorbar.bgcolor = "rgba(255,255,255,0.85)"
    fig.layout.coloraxis.colorbar.thickness = 5
    fig.layout.coloraxis.colorbar.x = 0.5
    fig.layout.coloraxis.colorbar.y = 0
    fig.layout.coloraxis.colorbar.orientation = "h"
    fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}")
    return fig


# Create the Dash app
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
                html.H3("H-1B visas in the US (2021-2024)", className="p-2"),
                html.Span(
                    "STORY Week 38 FF",
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
    className="bg-light vh-100",
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
        html.Div([dcc.Graph(figure=graphEmployer(), config=config)]),
        html.Div([dcc.Graph(figure=graphMap(), config=config)]),
    ]
    text = [
        ("Employer", "Beneficiary registration submitted"),
        ("Beneficiary", "Beneficiary's country of nationality"),
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
    app.run_server(debug=True)
