import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from urllib.request import urlopen
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
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

url = "https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2025/week-25/Building_Permits_Issued_Past_180_Days.csv"
df = pd.read_csv(url)

if "applieddate" in df.columns and "issueddate" in df.columns:
    df["applieddate"] = pd.to_datetime(df["applieddate"], errors="coerce")
    df["issueddate"] = pd.to_datetime(df["issueddate"], errors="coerce")
    df["days_to_issue"] = (df["issueddate"] - df["applieddate"]).dt.days

df["days_to_issue"] = (df["issueddate"] - df["applieddate"]).dt.days


def graphBoxplot():
    df_plot = df[df["days_to_issue"] > 0].copy()
    fig = go.Figure()
    fig.add_trace(
        go.Box(
            y=df_plot["workclass"],
            x=df_plot["days_to_issue"],
            boxpoints="outliers",
            orientation="h",
            marker_color="#36a4d4",
            name="",
            showlegend=False,
            boxmean=True,
        )
    )
    fig.update_layout(
        template="plotly_dark",
        xaxis_type="log",
        xaxis_title="Approval Time (Days, Log Scale)",
        yaxis_title="Type of Work (Workclass)",
        height=450,
        margin=dict(t=50, b=50, l=50, r=50),
    )
    return fig


def graphNPL():
    """
    - **X-axis:** "Key word usage frequency" — measures how frequently important words appear in permit descriptions.
    - **Y-axis:** "Textual structure and linguistic patterns" — captures the complexity and variation in the writing style.

    | Quadrant        | Position        | Interpretation                                                                                     |
    |-----------------|-----------------|--------------------------------------------------------------------------------------------------|
    | **Quadrant I**  | X > 0, Y > 0    | Descriptions with high frequency of key words and complex or varied textual structure. These likely include detailed or technical language. |
    | **Quadrant II** | X < 0, Y > 0    | Descriptions with low frequency of common key words but complex linguistic structure. Possibly creative or less technical language with elaborate phrasing. |
    | **Quadrant III**| X < 0, Y < 0    | Texts with low frequency of key words and simple, direct structure. These are likely clear, standard, or concise descriptions, which may facilitate faster approvals. |
    | **Quadrant IV** | X > 0, Y < 0    | Descriptions with high frequency of key words but simple or less varied structure. This could represent repetitive technical language or frequent terminology with minimal complexity. |

    This interpretation helps to understand how language patterns in permit descriptions relate to approval times and can guide further analysis or improvements in the permitting process.
    """

    df_nlp = df[
        ["description", "workclass", "days_to_issue", "estprojectcost"]
    ].dropna()
    df_nlp = df_nlp[df_nlp["days_to_issue"] > 0]
    q1 = df_nlp["days_to_issue"].quantile(0.33)
    q2 = df_nlp["days_to_issue"].quantile(0.66)

    def classify_speed(days):
        if days <= q1:
            return "fast"
        elif days <= q2:
            return "average"
        else:
            return "slow"

    df_nlp["approval_speed"] = df_nlp["days_to_issue"].apply(classify_speed)
    vectorizer = TfidfVectorizer(max_features=500, stop_words="english")
    X_tfidf = vectorizer.fit_transform(df_nlp["description"])
    pca = PCA(n_components=2)
    X_reduced = pca.fit_transform(X_tfidf.toarray())
    df_nlp["x"] = X_reduced[:, 0]
    df_nlp["y"] = X_reduced[:, 1]
    df_nlp["cost_scaled"] = df_nlp["estprojectcost"] / df_nlp["estprojectcost"].max()
    fig = px.scatter(
        df_nlp,
        x="x",
        y="y",
        color="approval_speed",
        size="cost_scaled",
        hover_data=[
            "description",
            "days_to_issue",
            "approval_speed",
            "workclass",
            "estprojectcost",
        ],
        labels={
            "x": "Key word usage frequency",
            "y": "Textual structure and linguistic patterns",
            "approval_speed": "Approval Speed",
            "workclass": "Work Type",
            "estprojectcost": "Estimated Cost",
        },
        template="plotly_dark",
    )
    fig.update_traces(marker=dict(opacity=0.7, line=dict(width=0)))
    fig.update_layout(
        xaxis=dict(
            range=[-0.5, 0.7],
            zeroline=True,
            zerolinewidth=3,
            zerolinecolor="gray",
            showgrid=False,
        ),
        yaxis=dict(
            range=[-0.5, 0.7],
            zeroline=True,
            zerolinewidth=3,
            zerolinecolor="gray",
            showgrid=False,
        ),
        height=450,
        showlegend=True,
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
                    "Raleigh, Construction Permits Issued in the Last 180 Days",
                    className="p-2",
                ),
                html.Span(
                    "STORY Week 25 FF 2025",
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
        html.Div([dcc.Graph(figure=graphBoxplot(), config=config)]),
        html.Div([dcc.Graph(figure=graphNPL(), config=config)]),
    ]
    text = [
        (
            "Permit Approval Time by Work Type",
            "Analysis of the distribution of days taken to approve permits across work categories (log scale).",
        ),
        (
            "Permit Description Similarity and Approval Speed",
            "Each point represents a permit description embedded using TF-IDF and reduced via PCA. The axes reflect differences in language patterns; clusters suggest shared linguistic structures.",
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
