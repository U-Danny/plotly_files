import plotly.express as px
from datetime import date
import plotly.graph_objects as go
import pandas as pd
from urllib.request import urlopen
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA


project = "Figure Friday 2025 - week 25"
project_title = "Raleigh, Construction Permits Issued in the Last 180 Days."
date = date(2025, 6, 27)
detail_project = "Honoring our first Plotly Meetup in Raleigh NC, led by @ThomasD21M on June 25, we’ve decided to highlight a dataset from the city of Raleigh. The dataset includes all pending and approved permits related to buildings, as well as non-construction inspections permits (issued in the past 180 days)."
dataset_url = "https://community.plotly.com/t/figure-friday-2025-week-25/92773"

url = "dataset/Building_Permits_Issued_Past_180_Days.csv"


def graphBoxplot(template):
    df = pd.read_csv(url)
    if "applieddate" in df.columns and "issueddate" in df.columns:
        df["applieddate"] = pd.to_datetime(df["applieddate"], errors="coerce")
        df["issueddate"] = pd.to_datetime(df["issueddate"], errors="coerce")
        df["days_to_issue"] = (df["issueddate"] - df["applieddate"]).dt.days

    df["days_to_issue"] = (df["issueddate"] - df["applieddate"]).dt.days

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
        template=template,
        xaxis_type="log",
        xaxis_title="Approval Time (Days, Log Scale)",
        yaxis_title="Type of Work (Workclass)",
        height=500,
        margin=dict(t=50, b=50, l=150, r=50),
    )
    return fig


def graphNPL(template):
    df = pd.read_csv(url)
    if "applieddate" in df.columns and "issueddate" in df.columns:
        df["applieddate"] = pd.to_datetime(df["applieddate"], errors="coerce")
        df["issueddate"] = pd.to_datetime(df["issueddate"], errors="coerce")
        df["days_to_issue"] = (df["issueddate"] - df["applieddate"]).dt.days

    df["days_to_issue"] = (df["issueddate"] - df["applieddate"]).dt.days
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
        template=template,
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
        height=500,
        showlegend=True,
    )
    return fig


# Array de visualizaciones, cada una con su título, subtítulo y función de gráfico
plots = [
    {
        "title": "Permit Approval Time by Work Type",
        "subtitle": "Analysis of the distribution of days taken to approve permits across work categories (log scale).",
        "graph": graphBoxplot,
    },
    {
        "title": "Permit Description Similarity and Approval Speed",
        "subtitle": "Each point represents a permit description embedded using TF-IDF and reduced via PCA. The axes reflect differences in language patterns; clusters suggest shared linguistic structures.",
        "graph": graphNPL,
    },
]
