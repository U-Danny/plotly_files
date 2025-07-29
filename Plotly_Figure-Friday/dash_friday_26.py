import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from urllib.request import urlopen
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy.stats import zscore


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

df_gender = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2025/week-26/gender-parity-in-managerial-positions.csv"
)
df_paygap = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2025/week-26/gender-pay-gap.csv"
)
df_productivity = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2025/week-26/labor-productivity.csv"
)
df_unemployment = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2025/week-26/unemployment.csv"
)

df_gender.columns = ["Year", "Management_F", "Employment_F", "WorkingAge_F"]
df_paygap.columns = [
    "Year",
    "World",
    "Low_income",
    "Lower_middle",
    "Upper_middle",
    "High_income",
]
df_productivity.columns = [
    "Year",
    "World",
    "Africa",
    "Americas",
    "Arab_States",
    "Asia_Pacific",
    "Europe_CentralAsia",
]
df_unemployment.columns = [
    "Year",
    "Africa",
    "Americas",
    "Arab_States",
    "Asia_Pacific",
    "Europe_CentralAsia",
    "World",
]

for df in [df_gender, df_paygap, df_productivity, df_unemployment]:
    df["Year"] = df["Year"].astype(int)


def graphKuznetsCurve():
    df = df_gender.merge(df_paygap[["Year", "World"]], on="Year", how="left")
    df = df.merge(
        df_productivity[["Year", "World"]],
        on="Year",
        how="left",
        suffixes=("_PayGap", "_Productivity"),
    )
    df_clean = df.dropna()

    X = df_clean["World_Productivity"].values.reshape(-1, 1)
    y = df_clean["World_PayGap"].values

    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(X)
    model = LinearRegression().fit(X_poly, y)

    x_vals = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
    x_vals_poly = poly.transform(x_vals)
    y_pred = model.predict(x_vals_poly)

    key_points = [
        (X.min(), y[np.argmin(X)]),
        (
            X.mean(),
            model.predict(poly.transform([[X.mean()]]))[0],
        ),
        (X.max(), y[np.argmax(X)]),
    ]
    annotations = [
        dict(
            x=key_points[0][0],
            y=key_points[0][1],
            text="Start point",
            showarrow=True,
            arrowhead=2,
            font=dict(size=10, color="white"),
            ax=-40,
            ay=-40,
            bgcolor="rgba(0,0,0,0.6)",
        ),
        dict(
            x=key_points[1][0],
            y=key_points[1][1],
            text="Peak gap",
            showarrow=True,
            arrowhead=2,
            font=dict(size=10, color="white"),
            ax=40,
            ay=-30,
            bgcolor="rgba(0,0,0,0.6)",
        ),
        dict(
            x=key_points[2][0],
            y=key_points[2][1],
            text="End point",
            showarrow=True,
            arrowhead=2,
            font=dict(size=10, color="white"),
            ax=40,
            ay=30,
            bgcolor="rgba(0,0,0,0.6)",
        ),
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=X.flatten(),
            y=y,
            mode="markers",
            marker=dict(size=8, color="skyblue", line=dict(width=1, color="white")),
            hovertemplate="Productivity: %{x:.2f}<br>Pay Gap: %{y:.2f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x_vals.flatten(),
            y=y_pred,
            mode="lines",
            line=dict(color="magenta", width=2, dash="dash"),
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Labor productivity (global)",
        yaxis_title="Gender pay gap (%)",
        showlegend=False,
        height=450,
        annotations=annotations,
        margin=dict(t=10),
    )
    return fig


def graphCompesationTheory():
    df1 = df_productivity[
        [
            "Year",
            "Africa",
            "Americas",
            "Arab_States",
            "Asia_Pacific",
            "Europe_CentralAsia",
        ]
    ].copy()
    df2 = df_unemployment[
        [
            "Year",
            "Africa",
            "Americas",
            "Arab_States",
            "Asia_Pacific",
            "Europe_CentralAsia",
        ]
    ].copy()

    merged = pd.merge(
        df1, df2, on="Year", suffixes=("_Productivity", "_Unemployment")
    ).dropna()

    regions = [
        "Africa",
        "Americas",
        "Arab_States",
        "Asia_Pacific",
        "Europe_CentralAsia",
    ]
    colors = ["#FFA07A", "#87CEFA", "#BA55D3", "#3CB371", "#FFD700"]
    prod_z = merged[[f"{r}_Productivity" for r in regions]].apply(zscore)
    unemp_z = merged[[f"{r}_Unemployment" for r in regions]].apply(zscore)
    index_z = prod_z.values - unemp_z.values
    df_index = pd.DataFrame(index_z, columns=regions)
    df_index["Year"] = merged["Year"]
    fig = go.Figure()
    for region, color in zip(regions, colors):
        fig.add_trace(
            go.Scatter(
                x=df_index["Year"],
                y=df_index[region],
                mode="lines+markers",
                name=region.replace("_", " "),
                line=dict(color=color, width=2),
                marker=dict(size=5),
                hovertemplate=f'{region.replace("_", " ")}<br>Year: %{{x}}<br>Index: %{{y:.2f}}<extra></extra>',
            )
        )
    event = {2001: "Dot-com crash", 2009: "Post crisis", 2020: "COVID-19"}
    for year, texto in event.items():
        fig.add_vline(
            x=year,
            line_width=1,
            line_dash="dot",
            line_color="gray",
            annotation_text=texto,
            annotation_position="top left",
            annotation_font=dict(color="lightgray", size=10),
            opacity=0.7,
        )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Year",
        yaxis_title="Structural Compensation Index (Z-Productivity − Z-Unemployment)",
        height=450,
        legend=dict(title="Region", orientation="h", y=1.1),
        margin=dict(t=50, l=60, r=40, b=50),
    )

    return fig


def graphParityProjection():
    df = df_gender.dropna(subset=["Management_F"])
    X = df["Year"].values.reshape(-1, 1)
    y = df["Management_F"].values
    model = LinearRegression().fit(X, y)
    future_years = np.arange(df["Year"].min(), 2051).reshape(-1, 1)
    y_pred = model.predict(future_years)
    pred_2050 = y_pred[-1]
    annotations = [
        dict(
            x=2050,
            y=pred_2050,
            text=f"Projection 2050:<br>{pred_2050:.1f}%",
            showarrow=True,
            arrowhead=2,
            font=dict(size=10, color="white"),
            ax=-50,
            ay=-30,
            bgcolor="rgba(0,0,0,0.6)",
        )
    ]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Year"],
            y=df["Management_F"],
            mode="lines+markers",
            line=dict(color="lightgreen"),
            hovertemplate="Year: %{x}<br>% Women: %{y:.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=future_years.flatten(),
            y=y_pred,
            mode="lines",
            line=dict(color="violet", dash="dash"),
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=future_years.flatten(),
            y=[50] * len(future_years),
            mode="lines",
            line=dict(color="gray", dash="dot"),
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Year",
        yaxis_title="Female share in management (%)",
        showlegend=False,
        height=450,
        annotations=annotations,
        margin=dict(t=10),
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
                    "Tracing Inequality: From the Global Labor Market to the Gender Pay Gap.",
                    className="p-2",
                ),
                html.Span(
                    "STORY Week 26 FF 2025",
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
        html.Div([dcc.Graph(figure=graphKuznetsCurve(), config=config)]),
        html.Div([dcc.Graph(figure=graphCompesationTheory(), config=config)]),
        html.Div([dcc.Graph(figure=graphParityProjection(), config=config)]),
    ]
    text = [
        (
            "Gender Pay Gap Kuznets Curve",
            "Represents how the gender pay gap changes by income level across regions, revealing an inverted Kuznets curve: inequality rises with mid development and decreases afterward.",
        ),
        (
            "Structural Compensation Index by Region (Normalized)",
            "Compares standardized productivity and unemployment by region over time, showing structural imbalances. High values suggest efficiency with low unemployment; low values, misalignment.",
        ),
        (
            "Global Managerial Parity Projection",
            "Shows female participation in management relative to employment and population, projecting convergence toward parity. While valid, true parity depends on structural factors like equal employment access.",
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
