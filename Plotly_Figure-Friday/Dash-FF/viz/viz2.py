import plotly.express as px
from datetime import date
import networkx as nx
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression

project = "Figure Friday 2025 - week 31"
project_title = "Candy Ranking: The FiveThirtyEight Experiment."
date = date(2025, 8, 8)
detail_project = (
    "What was the most desirable candy according to the FiveThirtyEight experiment?"
)
dataset_url = "https://community.plotly.com/t/figure-friday-2025-week-31/93506"

url = "dataset/candy-data.csv"


def graphNetwork(template):
    df = pd.read_csv(url)
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
            template=template,
            height=500,
            showlegend=False,
            hovermode="closest",
            margin=dict(t=50, b=20, l=20, r=20),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )
    return fig


def graphBar(template):
    df = pd.read_csv(url)
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
        template=template,
        height=500,
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=130, r=40, t=40, b=40),
    )
    fig.update_traces(
        texttemplate="%{x:.3f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Mutual Information: %{x:.3f}<extra></extra>",
        marker_line_width=0,
    )
    return fig


# Array de visualizaciones, cada una con su título, subtítulo y función de gráfico
plots = [
    {
        "title": "Candy Similarity and Influence Network Based on Ingredients and Popularity.",
        "subtitle": "Hierarchical visualization where node size reflects popularity (Win%) and node color indicates structural influence (PageRank) within the similarity network built from product ingredients and features.",
        "graph": graphNetwork,
    },
    {
        "title": "Feature importance for predicting candy popularity.",
        "subtitle": "Mutual information highlights which ingredients and factors are most related to the winning percentage (winpercent).",
        "graph": graphBar,
    },
]
