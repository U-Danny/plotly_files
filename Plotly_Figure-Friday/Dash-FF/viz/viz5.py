import plotly.express as px
from datetime import date
import plotly.graph_objects as go
import pandas as pd
import re


project = "Figure Friday 2025 - week 24"
project_title = "Open Parking and Camera Violations"
date = date(2025, 6, 20)
detail_project = "What’s the average penalty or fine for open parking and camera violations? What months or days of the week see the highest amount of violations?"
dataset_url = "https://community.plotly.com/t/figure-friday-2025-week-24/92687"

url = "dataset/Open_Parking_and_Camera_Violations.parquet"


def graphParallel(template):
    df = pd.read_parquet(url, engine="pyarrow")
    cols = [
        "Fine Amount",
        "Penalty Amount",
        "Interest Amount",
        "Reduction Amount",
        "Payment Amount",
    ]
    df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")
    grouped = df.groupby(cols + ["Violation"]).size().reset_index(name="Count")
    grouped["Violation_Code"] = grouped["Violation"].astype("category").cat.codes
    fig = px.parallel_coordinates(
        grouped,
        dimensions=cols,
        color="Violation_Code",
        color_continuous_scale=px.colors.qualitative.Set3,
        labels={col: col.replace("_", " ") for col in cols},
    )
    fig.update_layout(
        template=template,
        coloraxis_showscale=False,
        height=500,
    )
    return fig


def parse_violation_time(vtime):
    if isinstance(vtime, str):
        vtime = vtime.strip().upper().replace(" ", "")
        match = re.match(r"^(\d{1,2}):(\d{2})([AP])$", vtime)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            meridian = match.group(3)
            if meridian == "P" and hour != 12:
                hour += 12
            elif meridian == "A" and hour == 12:
                hour = 0
            return hour
    return None


def graphHeatmap(template):
    df = pd.read_parquet(url, engine="pyarrow")
    df["Violation Hour"] = df["Violation Time"].apply(parse_violation_time)
    df_grouped = (
        df.groupby(["Violation", "Violation Hour"]).size().reset_index(name="count")
    )
    df_pivot = df_grouped.pivot(
        index="Violation", columns="Violation Hour", values="count"
    ).fillna(0)
    df_pivot = df_pivot.reindex(columns=range(1, 25), fill_value=0)
    df_z = df_pivot.copy()
    df_z = (df_z - df_z.mean(axis=1).values.reshape(-1, 1)) / df_z.std(axis=1).replace(
        0, 1
    ).values.reshape(-1, 1)
    fig = px.imshow(
        df_z,
        labels=dict(x="Hour of Day (1-24)", y="Violation Type", color="Z-score"),
        color_continuous_scale="blues",
        template=template,
        height=500,
    )

    fig.update_xaxes(tickmode="linear", dtick=1)
    fig.update_layout(margin=dict(l=250, t=20, b=50, r=30))
    return fig


# Array de visualizaciones, cada una con su título, subtítulo y función de gráfico
plots = [
    {
        "title": "Traffic Fines: Parallel Comparison of Monetary Amounts by Violation",
        "subtitle": "Each line represents a unique combination of monetary values and its corresponding violation type",
        "graph": graphParallel,
    },
    {
        "title": "Hourly Patterns of Traffic Violations",
        "subtitle": "Z-score by violation type across the day",
        "graph": graphHeatmap,
    },
]
