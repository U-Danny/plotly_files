import plotly.express as px
from datetime import date
import plotly.graph_objects as go
import pandas as pd


project = "Figure Friday 2025 - week 34"
project_title = "Primary Causes of Metro Incidents in Montreal"
date = date(2025, 8, 29)
detail_project = "What type of train incidents occur within the Montreal metro system?"
dataset_url = "https://community.plotly.com/t/figure-friday-2025-week-34/93782"

# url_original = "https://drive.google.com/file/d/1hlH3wEzeMCmdPVTIjajrnFpszHzHwG5r/view"
# file_id = url_original.split("/")[-2]
download_url = "dataset/Incidents-du-reseau-du-metro.csv"


def clean_column_names(df):
    cols = df.columns
    cols = cols.str.replace("'", "").str.replace(" ", "_").str.lower()
    cols = (
        cols.str.normalize("NFKD")
        .str.encode("ascii", errors="ignore")
        .str.decode("utf-8")
    )
    cols = cols.str.replace("_+", "_", regex=True).str.strip("_")
    df.columns = cols
    return df


def pad_text(text, length):
    return " " * (length - len(text)) + text


def process_evacuation_status(evacuation_str):
    if evacuation_str == "0" or evacuation_str == "#":
        return "No Evacuation"
    else:
        return "Evacuation"


def graphProgress(template):
    df = pd.read_csv(download_url)

    df = clean_column_names(df)

    df_filtered = df.dropna(subset=["cause_primaire"])

    cause_counts = (
        df_filtered["cause_primaire"].value_counts(normalize=True).mul(100).round(1)
    )

    top_5_causes = cause_counts.head(5)

    if template == "plotly_dark":
        colors = ["#42A5F5", "#66BB6A", "#FFA726", "#26C6DA", "#AB47BC"]
    else:
        colors = ["#1565C0", "#2E7D32", "#EF6C00", "#00838F", "#6A1B9A"]
    kpis = []
    for i, (cause, percentage) in enumerate(top_5_causes.items()):
        kpis.append({"name": cause, "value": percentage, "color": colors[i]})

    fig = go.Figure()

    max_arc = 270
    rotation_start = 0
    direction = "clockwise"
    bg_gray = "rgba(0,0,0,0.2)"
    invisible_color = "rgba(0,0,0,0)"
    center_space = 0.12
    gap = 0.02
    num_kpis = len(kpis)

    if num_kpis > 0:
        max_total_thickness = 0.5 - center_space
        total_gap_space = (num_kpis - 1) * gap
        thickness = (max_total_thickness - total_gap_space) / num_kpis
        if thickness < 0:
            raise ValueError(
                "Not enough radial space for the number of KPIs. Reduce gaps or center_space."
            )
    else:
        thickness = 0

    texts = [f"{kpi['name']} {kpi['value']}%" for kpi in kpis]
    max_len = max(len(t) for t in texts) if texts else 0

    for i, kpi in enumerate(kpis):
        r_inner = center_space + i * (thickness + gap)
        r_outer = r_inner + thickness
        hole_frac = r_inner / r_outer
        progress_deg = kpi["value"] * max_arc / 100.0
        remaining_deg = max_arc - progress_deg
        invisible_deg = 360 - max_arc
        values = [progress_deg, remaining_deg, invisible_deg]
        domain_box = {
            "x": [0.5 - r_outer, 0.5 + r_outer],
            "y": [0.5 - r_outer, 0.5 + r_outer],
        }
        fig.add_trace(
            go.Pie(
                values=values,
                labels=["", "", ""],
                hole=hole_frac,
                marker_colors=[kpi["color"], bg_gray, invisible_color],
                direction=direction,
                rotation=rotation_start,
                sort=False,
                textinfo="none",
                hoverinfo="skip",
                showlegend=False,
                domain=domain_box,
            )
        )
        ann_radius = r_inner + thickness / 2
        ann_y = 0.5 + ann_radius
        padded_text = pad_text(texts[i], max_len)
        fig.add_annotation(
            x=0.4,
            y=ann_y,
            xref="paper",
            yref="paper",
            text=padded_text,
            showarrow=False,
            align="left",
            font=dict(size=12),
        )

    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        text="Cause<br>primaire",
        showarrow=False,
        font=dict(size=20),
        align="center",
    )

    fig.update_layout(height=500, margin=dict(t=50, b=50, l=0, r=0), template=template)

    return fig


def graphSankey(template):
    df = pd.read_csv(download_url)

    df = clean_column_names(df)

    df_sankey = df.dropna(
        subset=["cause_primaire", "cause_secondaire", "evacuation", "annee_civile"]
    ).copy()

    df_sankey.loc[:, "evacuation_status"] = df_sankey["evacuation"].apply(
        process_evacuation_status
    )

    links1 = (
        df_sankey.groupby(["cause_primaire", "cause_secondaire"])
        .size()
        .reset_index(name="value")
    )
    links1.columns = ["source", "target", "value"]

    links2 = (
        df_sankey.groupby(["cause_secondaire", "evacuation_status"])
        .size()
        .reset_index(name="value")
    )
    links2.columns = ["source", "target", "value"]

    links_df = pd.concat([links1, links2], axis=0)

    unique_nodes = pd.unique(links_df[["source", "target"]].values.ravel("K"))
    node_map = {node: i for i, node in enumerate(unique_nodes)}

    source_indices = links_df["source"].map(node_map)
    target_indices = links_df["target"].map(node_map)
    values = links_df["value"]

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=unique_nodes,
                    color="slateblue",
                ),
                link=dict(source=source_indices, target=target_indices, value=values),
            )
        ]
    )

    fig.update_layout(
        template=template,
        height=500,
        margin=dict(t=0, b=0, l=30, r=30),
    )
    return fig


plots = [
    {
        "title": "Incident Flow: From Primary Cause to Evacuation",
        "subtitle": "This Sankey diagram shows the flow of incidents, from their primary and secondary causes to the final outcome: an evacuation or not.",
        "graph": graphSankey,
    },
    {
        "title": "Primary Causes of Metro Incidents",
        "subtitle": "Distribution of the main causes of incidents, showing the percentage of each.",
        "graph": graphProgress,
    },
]
