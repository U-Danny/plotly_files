import plotly.express as px
from datetime import date
import plotly.graph_objects as go
import pandas as pd
from urllib.request import urlopen
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy.stats import zscore


project = "Figure Friday 2025 - week 26"
project_title = (
    "Tracing Inequality: From the Global Labor Market to the Gender Pay Gap."
)
date = date(2025, 7, 4)
detail_project = "How has the unemployment rate changed over time? What has happened to the gender pay gap?"
dataset_url = "https://community.plotly.com/t/figure-friday-2025-week-28/93088"


def graphKuznetsCurve(template):
    df_gender = pd.read_csv("dataset/gender-parity-in-managerial-positions.csv")
    df_paygap = pd.read_csv("dataset/gender-pay-gap.csv")
    df_productivity = pd.read_csv("dataset/labor-productivity.csv")
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
    for df in [df_gender, df_paygap, df_productivity]:
        df["Year"] = df["Year"].astype(int)
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
        template=template,
        xaxis_title="Labor productivity (global)",
        yaxis_title="Gender pay gap (%)",
        showlegend=False,
        height=500,
        annotations=annotations,
        margin=dict(t=10),
    )
    return fig


def graphCompesationTheory(template):
    df_productivity = pd.read_csv("dataset/labor-productivity.csv")
    df_unemployment = pd.read_csv("dataset/unemployment.csv")
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

    for df in [df_productivity, df_unemployment]:
        df["Year"] = df["Year"].astype(int)

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
        template=template,
        xaxis_title="Year",
        yaxis_title="Structural Compensation Index (Z-Productivity − Z-Unemployment)",
        height=500,
        legend=dict(title="Region", orientation="h", y=1.1),
        margin=dict(t=50, l=60, r=40, b=50),
    )

    return fig


def graphParityProjection(template):
    df_gender = pd.read_csv("dataset/gender-parity-in-managerial-positions.csv")
    for df in [df_gender]:
        df["Year"] = df["Year"].astype(int)
    df_gender.columns = ["Year", "Management_F", "Employment_F", "WorkingAge_F"]
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
        template=template,
        xaxis_title="Year",
        yaxis_title="Female share in management (%)",
        showlegend=False,
        height=500,
        annotations=annotations,
        margin=dict(t=10),
    )
    return fig


# Array de visualizaciones, cada una con su título, subtítulo y función de gráfico
plots = [
    {
        "title": "Gender Pay Gap Kuznets Curve",
        "subtitle": "Represents how the gender pay gap changes by income level across regions, revealing an inverted Kuznets curve: inequality rises with mid development and decreases afterward.",
        "graph": graphKuznetsCurve,
    },
    {
        "title": "Structural Compensation Index by Region (Normalized)",
        "subtitle": "Compares standardized productivity and unemployment by region over time, showing structural imbalances. High values suggest efficiency with low unemployment; low values, misalignment.",
        "graph": graphCompesationTheory,
    },
    {
        "title": "Global Managerial Parity Projection",
        "subtitle": "Shows female participation in management relative to employment and population, projecting convergence toward parity. While valid, true parity depends on structural factors like equal employment access.",
        "graph": graphParityProjection,
    },
]
