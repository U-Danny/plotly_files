import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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

url = "Data.csv"
df_data = pd.read_csv(url)


def graphBarPolar():
    df = df_data.copy()
    df["Date"] = pd.to_datetime(df["Date"], format="%b %Y")
    df["Month_Name"] = df["Date"].dt.strftime("%b")
    df["Year"] = df["Date"].dt.year
    years = df["Year"].unique()
    month_order = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    all_months = pd.MultiIndex.from_product(
        [years, month_order], names=["Year", "Month_Name"]
    ).to_frame(index=False)
    polar_data = df.groupby(["Year", "Month_Name"])["Value"].sum().reset_index()
    polar_data = pd.merge(
        all_months, polar_data, on=["Year", "Month_Name"], how="left"
    ).fillna(0)
    polar_data["Month_Name"] = pd.Categorical(
        polar_data["Month_Name"], categories=month_order, ordered=True
    )
    polar_data.sort_values(by=["Year", "Month_Name"], inplace=True)
    max_value = polar_data["Value"].max()
    min_value = polar_data["Value"].min()

    fig = px.bar_polar(
        polar_data,
        r="Value",
        theta="Month_Name",
        color="Value",
        color_continuous_scale="blues",
        range_color=[min_value, max_value],
        animation_frame="Year",
        template="plotly_dark",
        labels={"r": "Valor", "theta": "Mes"},
        height=480,
    )

    fig.update_layout(
        margin=dict(l=50, t=20, r=50, b=20),
        polar=dict(
            radialaxis=dict(visible=False, range=[0, max_value * 1.1]),
            angularaxis=dict(
                visible=True,
                showgrid=True,
                direction="clockwise",
                tickvals=month_order,
                ticktext=month_order,
                showline=False,
            ),
        ),
        font=dict(color="white"),
    )
    return fig


def graphBar():
    df = df_data.copy()
    df["Date"] = pd.to_datetime(df["Date"], format="%b %Y")
    df["Year"] = df["Date"].dt.year

    traffic_by_year_border = (
        df.groupby(["Year", "Border", "Measure"])["Value"].sum().reset_index()
    )

    last_year = traffic_by_year_border["Year"].max()
    last_year_data = traffic_by_year_border[traffic_by_year_border["Year"] == last_year]
    measure_order = (
        last_year_data.groupby("Measure")["Value"]
        .sum()
        .sort_values(ascending=True)
        .index
    )

    traffic_by_year_border["Value_Plot"] = traffic_by_year_border.apply(
        lambda row: (
            row["Value"] if row["Border"] == "US-Mexico Border" else -row["Value"]
        ),
        axis=1,
    )

    max_value = traffic_by_year_border["Value"].max()
    x_range = [-max_value * 1.1, max_value * 1.1]

    border_colors = {
        "US-Mexico Border": "lightgreen",
        "US-Canada Border": "lightslategray",
    }

    fig = px.bar(
        traffic_by_year_border,
        x="Value_Plot",
        y="Measure",
        color="Border",
        color_discrete_map=border_colors,
        animation_frame="Year",
        labels={
            "Value_Plot": "Total Traffic",
            "Measure": "Traffic Measure",
            "Border": "Border",
        },
        category_orders={"Measure": measure_order},
        hover_name="Border",
        hover_data={"Value_Plot": True, "Measure": False, "Border": False},
        template="plotly_dark",
        orientation="h",
    )

    fig.update_layout(
        xaxis_title="Total Traffic",
        yaxis_title="Traffic Measure",
        xaxis_range=x_range,
        legend_title_text="Border",
        font_color="white",
        xaxis_tickprefix="",
        xaxis_showticklabels=False,
        margin=dict(l=50, r=50, t=30, b=10),
        height=480,
    )

    fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="white")
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
                    "Trends of Traffic at U.S. Borders",
                    className="p-2",
                ),
                html.Span(
                    "STORY Week 32 FF 2025",
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
        html.Div([dcc.Graph(figure=graphBarPolar(), config=config)]),
        html.Div([dcc.Graph(figure=graphBar(), config=config)]),
    ]
    text = [
        (
            "Seasonal Traffic Patterns.",
            "Visualization of how monthly traffic patterns evolve over the years.",
        ),
        (
            "Cross-Border Traffic Comparison by Year.",
            "Annual traffic volume between the US-Mexico and US-Canada borders, measured by type.",
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
