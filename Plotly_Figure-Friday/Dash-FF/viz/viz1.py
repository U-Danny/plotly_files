import plotly.express as px
from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


project = "Figure Friday 2025 - week 32"
project_title = "Trends of Traffic at U.S. Borders"
date = date(2025, 8, 15)
detail_project = "US-Canada-Mexico: what items cross between the borders? what's the volume of items passing through the borders?"
dataset_url = "https://community.plotly.com/t/figure-friday-2025-week-32/93588"


download_url = "dataset/Border_Crossing_Entry_Data.parquet"


def graphBarPolar(template):
    df = pd.read_parquet(download_url, engine="pyarrow")
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
        template=template,
        labels={"r": "Valor", "theta": "Mes"},
        height=500,
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
        # font=dict(color="white"),
    )
    return fig


def graphBar(template):
    df = pd.read_parquet(download_url, engine="pyarrow")
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
        template=template,
        orientation="h",
    )

    fig.update_layout(
        xaxis_title="Total Traffic",
        yaxis_title="Traffic Measure",
        xaxis_range=x_range,
        legend_title_text="Border",
        # font_color="white",
        xaxis_tickprefix="",
        xaxis_showticklabels=False,
        margin=dict(l=180, r=50, t=30, b=10),
        height=500,
    )

    fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="grey")
    return fig


# Array de visualizaciones, cada una con su título, subtítulo y función de gráfico
plots = [
    {
        "title": "Seasonal Traffic Patterns.",
        "subtitle": "Visualization of how monthly traffic patterns evolve over the years.",
        "graph": graphBarPolar,
    },
    {
        "title": "Cross-Border Traffic Comparison by Year.",
        "subtitle": "Annual traffic volume between the US-Mexico and US-Canada borders, measured by type.",
        "graph": graphBar,
    },
]
