import plotly.express as px
from datetime import date
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA


project = "Figure Friday 2025 - week 28"
project_title = "How Has the Perception of Country-Level Corruption Changed Over Time?"
date = date(2025, 7, 18)
detail_project = "How has the perception of country-level corruption changed over time?"
dataset_url = "https://community.plotly.com/t/figure-friday-2025-week-28/93088"

url = "dataset/CPI-historical.csv"


def graphScatter(template):
    df = pd.read_csv(url)
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
        template=template,
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
        height=500,
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


def graphPCA(template):
    df = pd.read_csv(url)
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
    fig.update_layout(height=500, title="", template=template, legend_title="Region")
    return fig


# Array de visualizaciones, cada una con su título, subtítulo y función de gráfico
plots = [
    {
        "title": "Global Spiral of Corruption Perception Over Time.",
        "subtitle": "Visualizes the evolution of countries' CPI scores over time using a spiral layout. Radial distance represents corruption perception; colors denote regions.",
        "graph": graphScatter,
    },
    {
        "title": "Corruption Index vs. Ranking — PCA Spatial Representation.",
        "subtitle": "Displays countries' CPI and rank compressed into two PCA components, revealing spatial patterns in corruption perception and standings.",
        "graph": graphPCA,
    },
]
