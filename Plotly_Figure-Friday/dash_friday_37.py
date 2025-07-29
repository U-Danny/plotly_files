from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dash import html, Input, Output
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

df = pd.read_csv("test-dataset/child-mortality.csv")
df = df.rename(columns={"Under-five mortality rate": "rate"})

tabs_styles = {"height": "44px"}
tab_style = {
    "borderBottom": "1px solid #d6d6d6",
    "padding": "6px",
    "fontWeight": "bold",
}

tab_selected_style = {
    "borderTop": "1px solid #d6d6d6",
    "borderBottom": "1px solid #d6d6d6",
    "backgroundColor": "#597b7d",
    "color": "white",
    "padding": "6px",
}

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

with urlopen("test-dataset/countries.geo.json") as response:
    countries = json.load(response)

app = Dash(__name__, external_stylesheets=external_stylesheets)


def mapMain(year=2021):
    fig = px.choropleth_mapbox(
        df[df["Year"] == year],
        geojson=countries,
        color="rate",
        locations="id",
        opacity=1,
        mapbox_style="carto-positron",
        zoom=1,
        custom_data=["Entity", "rate"],
        color_continuous_scale="turbid",
        height=550,
    )
    fig.update_layout(autosize=True, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.layout.coloraxis.colorbar.title = "Rate <br>" + str(year)
    fig.layout.coloraxis.colorbar.ticksuffix = " %"
    fig.layout.coloraxis.colorbar.lenmode = "fraction"
    fig.layout.coloraxis.colorbar.len = 0.9
    fig.layout.coloraxis.colorbar.bgcolor = "rgba(255,255,255,0.85)"
    fig.layout.coloraxis.colorbar.thickness = 5
    fig.layout.coloraxis.colorbar.x = 0.5
    fig.layout.coloraxis.colorbar.y = 0
    fig.layout.coloraxis.colorbar.orientation = "h"
    fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]} %")
    return fig


def lineChart(countries):
    fig = px.line(
        df[df["Entity"].isin(countries)],
        x="Year",
        y="rate",
        color="Entity",
        height=550,
        template="none",
    )
    fig.update_yaxes(
        visible=True, showticklabels=True, showgrid=True, title="Rate", ticksuffix="%"
    )
    fig.update_layout(
        yaxis_range=[0, 100],
        margin={"r": 80, "t": 100, "l": 80, "b": 100},
        title_text="<b>Child mortality rate</b> <br><sup>The estimated share of newborns who die before reaching the age of five.",
        title_x=0.5,
        title_y=0.95,
    )
    fig.update_xaxes(showgrid=True)
    return fig


def boxplotChart(year=2021):
    fig = px.box(
        df[df["Year"] == year],
        y="rate",
        height=600,
        template="seaborn",
        points="all",
    )
    fig.update_layout(
        title_text="Child mortality rate <br>" + str(year),
        title_x=0.5,
        title_y=0.95,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0)",
    )
    fig.update_yaxes(
        visible=True, showticklabels=True, showgrid=True, title="Rate", ticksuffix="%"
    )
    return fig


title = html.Div(
    [html.H5("Child mortality rate, 1751 to 2022", className="p-2 text-center")]
)

container_map = html.Div(
    [
        html.Div(
            [
                html.H6("Select Year"),
                dcc.Slider(
                    min(df["Year"]),
                    max(df["Year"]),
                    marks={
                        min(df["Year"]): {
                            "label": str(min(df["Year"])),
                            "style": {"color": "blue", "fontSize": "14px"},
                        },
                        1800: {
                            "label": "1800",
                            "style": {"color": "blue", "fontSize": "14px"},
                        },
                        1900: {
                            "label": "1900",
                            "style": {"color": "blue", "fontSize": "14px"},
                        },
                        2000: {
                            "label": "2000",
                            "style": {"color": "blue", "fontSize": "14px"},
                        },
                        max(df["Year"]): {
                            "label": str(max(df["Year"])),
                            "style": {"color": "blue", "fontSize": "14px"},
                        },
                    },
                    value=2021,
                    tooltip={
                        "always_visible": True,
                        "style": {"color": "LightSteelBlue", "fontSize": "12px"},
                    },
                    className="pt-5",
                    vertical=True,
                    verticalHeight=400,
                    id="id-slider",
                ),
            ],
            className="col-sm-1 text-center px-4",
        ),
        html.Div(
            [
                dcc.Graph(
                    id="id-map", figure=mapMain(), config=config, clear_on_unhover=True
                )
            ],
            className="col-sm-9",
        ),
        html.Div(
            [
                dcc.Graph(
                    id="id-box",
                    figure=boxplotChart(),
                    config=config,
                    clear_on_unhover=True,
                )
            ],
            className="col-sm-2",
        ),
    ],
    className="row p-2",
)

graph = html.Div(
    [
        dcc.Dropdown(
            list(set(df["Entity"])),
            [list(set(df["Entity"]))[0]],
            multi=True,
            id="id-drop",
            className="p-2",
        ),
        html.Div(
            [
                dcc.Graph(
                    id="graph-main",
                    figure=lineChart([list(set(df["Entity"]))[0]]),
                    config=config,
                )
            ]
        ),
    ],
    className="container",
)


tabs = html.Div(
    [
        dcc.Tabs(
            [
                dcc.Tab(
                    label=" Map",
                    children=[container_map],
                    className="bi bi-globe-americas fs-5",
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
                dcc.Tab(
                    label=" Chart",
                    children=[graph],
                    className="bi bi-graph-up-arrow fs-5",
                    style=tab_style,
                    selected_style=tab_selected_style,
                ),
            ],
            className="",
        )
    ]
)

app.layout = html.Div([title, tabs], className="bg-light vh-100")


@app.callback(
    Output("graph-main", "figure"), Input("id-drop", "value"), prevent_initial_call=True
)
def displayClick(value):
    return lineChart(value)


@app.callback(
    [Output("id-map", "figure"), Output("id-box", "figure")],
    Input("id-slider", "value"),
    prevent_initial_call=True,
)
def displayClick(value):
    return [mapMain(value), boxplotChart(value)]


if __name__ == "__main__":
    app.run_server(debug=True)
