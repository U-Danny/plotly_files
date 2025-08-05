import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.feature_selection import mutual_info_regression


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

url = "https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2025/week-31/candy-data.csv"
df_candy = pd.read_csv(url)


def graphNetwork():
    df = df_candy.copy()
    features = [
        "chocolate",
        "fruity",
        "caramel",
        "peanutyalmondy",
        "nougat",
        "crispedricewafer",
        "hard",
        "bar",
        "pluribus",
        "sugarpercent",
        "pricepercent",
    ]
    X = df[features].values
    sim_matrix = cosine_similarity(X)
    threshold = 0.85
    G = nx.Graph()
    for i, row in df.iterrows():
        G.add_node(i, label=row["competitorname"], winpercent=row["winpercent"])

    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            if sim_matrix[i, j] > threshold:
                G.add_edge(i, j, weight=sim_matrix[i, j])

    pagerank = nx.pagerank(G)
    num_nodes = len(G.nodes)
    angle_step = 2 * np.pi / num_nodes
    node_pos = {
        n: (np.cos(i * angle_step), np.sin(i * angle_step))
        for i, n in enumerate(G.nodes)
    }
    node_x, node_y, node_text, node_color, node_size = [], [], [], [], []
    for n in G.nodes():
        x, y = node_pos[n]
        node_x.append(x)
        node_y.append(y)
        label = G.nodes[n]["label"]
        winp = G.nodes[n]["winpercent"]
        node_text.append(
            f"<b>{label}</b><br>Win%: {winp:.2f}<br>PageRank: {pagerank[n]:.4f}"
        )
        node_color.append(pagerank[n])

        size = 10 + 40 * (
            (winp - df["winpercent"].min())
            / (df["winpercent"].max() - df["winpercent"].min())
        )
        node_size.append(size)
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = node_pos[edge[0]]
        x1, y1 = node_pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color="#BBB"),
        hoverinfo="none",
        mode="lines",
    )
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="tealrose",
            color=node_color,
            size=node_size,
            colorbar=dict(title="PageRank"),
            line_width=1.5,
        ),
        text=node_text,
    )
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            titlefont_size=18,
            template="plotly_dark",
            height=450,
            showlegend=False,
            hovermode="closest",
            margin=dict(t=50, b=20, l=20, r=20),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )
    return fig


def graphBar():
    df = df_candy.copy()
    features = [
        "chocolate",
        "fruity",
        "caramel",
        "peanutyalmondy",
        "nougat",
        "crispedricewafer",
        "hard",
        "bar",
        "pluribus",
        "sugarpercent",
        "pricepercent",
    ]
    X = df[features]
    y = df["winpercent"]
    mi = mutual_info_regression(X, y, discrete_features=[True] * 9 + [False, False])
    mi_df = pd.DataFrame({"feature": features, "mutual_info": mi}).sort_values(
        by="mutual_info", ascending=True
    )
    brown_scale_dark = [
        [0.0, "#381a0a"],
        [0.3, "#6f3f18"],
        [0.6, "#a56a34"],
        [1.0, "#d9a15a"],
    ]
    fig = px.bar(
        mi_df,
        x="mutual_info",
        y="feature",
        orientation="h",
        color="mutual_info",
        color_continuous_scale=brown_scale_dark,
        labels={"mutual_info": "Mutual Information", "feature": "Feature"},
        template="plotly_dark",
        height=450,
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=130, r=40, t=80, b=40),
    )
    fig.update_traces(
        texttemplate="%{x:.3f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Mutual Information: %{x:.3f}<extra></extra>",
        marker_line_width=0,
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
                    "Candy Ranking: The FiveThirtyEight Experiment",
                    className="p-2",
                ),
                html.Span(
                    "STORY Week 31 FF 2025",
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
        html.Div([dcc.Graph(figure=graphNetwork(), config=config)]),
        html.Div([dcc.Graph(figure=graphBar(), config=config)]),
    ]
    text = [
        (
            "Candy Similarity and Influence Network Based on Ingredients and Popularity.",
            "Hierarchical visualization where node size reflects popularity (Win%) and node color indicates structural influence (PageRank) within the similarity network built from product ingredients and features.",
        ),
        (
            "Feature importance for predicting candy popularity.",
            "Mutual information highlights which ingredients and factors are most related to the winning percentage (winpercent).",
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
