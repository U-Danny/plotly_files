import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from urllib.request import urlopen
import json
import plotly.express as px

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

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2025/week-10/Popularity%20of%20Programming%20Languages%20from%202004%20to%202024.csv"
)
df["Date"] = pd.to_datetime(df["Date"])


def graphCategory():
    language_categories = {
        "JavaScript": "Web & Mobile Development",
        "TypeScript": "Web & Mobile Development",
        "PHP": "Web & Mobile Development",
        "Dart": "Web & Mobile Development",
        "Swift": "Web & Mobile Development",
        "Kotlin": "Web & Mobile Development",
        "Java": "Enterprise & Backend",
        "C#": "Enterprise & Backend",
        "Visual Basic": "Enterprise & Backend",
        "VBA": "Enterprise & Backend",
        "Cobol": "Enterprise & Backend",
        "Delphi/Pascal": "Enterprise & Backend",
        "Abap": "Enterprise & Backend",
        "Python": "Data Science & AI",
        "R": "Data Science & AI",
        "Julia": "Data Science & AI",
        "Matlab": "Data Science & AI",
        "Scala": "Data Science & AI",
        "C/C++": "Systems & Security",
        "Rust": "Systems & Security",
        "Go": "Systems & Security",
        "Ada": "Systems & Security",
        "Objective-C": "Systems & Security",
        "Perl": "Scripting, Automation & Game Development",
        "Lua": "Scripting, Automation & Game Development",
        "Powershell": "Scripting, Automation & Game Development",
        "Haskell": "Scripting, Automation & Game Development",
        "Groovy": "Scripting, Automation & Game Development",
        "Ruby": "Scripting, Automation & Game Development",
    }

    TRENDS = {
        "Mobile": "2010-01-01",
        "Data Science & IA": "2020-01-01",
        "Automation": "2015-01-01",
        "Game Development": "2005-01-01",
    }

    category_colors = {
        "Web & Mobile Development": "#1f77b4",
        "Enterprise & Backend": "#ff7f0e",
        "Data Science & AI": "#2ca02c",
        "Systems & Security": "#d62728",
        "Scripting, Automation & Game Development": "#9467bd",
    }
    df_long = df.melt(id_vars=["Date"], var_name="Language", value_name="Popularity")
    df_long["Category"] = df_long["Language"].map(language_categories)
    df_long = df_long.sort_values(
        by=["Date", "Category", "Popularity"], ascending=[True, True, False]
    )
    df_long["Formatted Date"] = df_long["Date"].dt.strftime("%m/%Y")
    tick_vals = df_long[df_long["Date"].dt.month == 12]["Formatted Date"].unique()
    fig = px.area(
        df_long,
        x="Formatted Date",
        y="Popularity",
        color="Category",
        line_group="Language",
        color_discrete_map=category_colors,
        template="plotly_dark",
        height=600,
    )
    for t in TRENDS:
        fecha = pd.to_datetime(TRENDS[t]).strftime("%m/%Y")
        fig.add_vline(x=fecha, line_width=2, line_dash="dash", line_color="gray")
        fig.add_annotation(
            x=fecha,
            y=1.02,
            xref="x",
            yref="paper",
            text=t,
            showarrow=False,
            font=dict(color="gray", size=12),
            yanchor="bottom",
        )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Popularity (%)",
        xaxis=dict(tickmode="array", tickvals=tick_vals, tickangle=-45, showgrid=False),
        yaxis=dict(range=[0, 100], showgrid=True),
        legend_title="Category",
        showlegend=True,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.05),
    )
    return fig


def graphTernary():
    df_long = df.melt(id_vars=["Date"], var_name="language", value_name="popularity")
    paradigms = {
        "Abap": ["Imperativo", "Orientado a objetos"],
        "Ada": ["Imperativo", "Orientado a objetos"],
        "C/C++": ["Imperativo", "Procedural", "Orientado a objetos"],
        "C#": ["Imperativo", "Orientado a objetos", "Funcional"],
        "Cobol": ["Imperativo"],
        "Dart": ["Orientado a objetos", "Funcional"],
        "Delphi/Pascal": ["Imperativo", "Orientado a objetos"],
        "Go": ["Imperativo", "Concurrente"],
        "Groovy": ["Orientado a objetos", "Funcional"],
        "Haskell": ["Funcional"],
        "Java": ["Imperativo", "Orientado a objetos", "Funcional"],
        "JavaScript": ["Imperativo", "Orientado a objetos", "Funcional"],
        "Julia": ["Funcional", "Imperativo"],
        "Kotlin": ["Orientado a objetos", "Funcional"],
        "Lua": ["Imperativo", "Funcional"],
        "Matlab": ["Imperativo", "Funcional"],
        "Objective-C": ["Orientado a objetos", "Imperativo"],
        "Perl": ["Imperativo", "Funcional"],
        "PHP": ["Imperativo", "Orientado a objetos"],
        "Powershell": ["Imperativo"],
        "Python": ["Imperativo", "Funcional", "Orientado a objetos"],
        "R": ["Funcional", "Imperativo"],
        "Ruby": ["Orientado a objetos", "Funcional"],
        "Rust": ["Imperativo", "Funcional"],
        "Scala": ["Funcional", "Orientado a objetos"],
        "Swift": ["Imperativo", "Orientado a objetos"],
        "TypeScript": ["Imperativo", "Orientado a objetos", "Funcional"],
        "VBA": ["Imperativo"],
        "Visual Basic": ["Imperativo", "Orientado a objetos"],
    }

    categories = {
        "Abap": ["Enterprise Applications", "Backend"],
        "Ada": ["Systems Programming", "Safety-Critical", "Backend"],
        "C/C++": ["Systems Programming", "Embedded Systems", "Backend"],
        "C#": ["Web", "Desktop", "Mobile", "Backend"],
        "Cobol": ["Enterprise Applications", "Financial", "Backend"],
        "Dart": ["Web", "Mobile", "Frontend"],
        "Delphi/Pascal": ["Desktop", "Embedded Systems", "Backend"],
        "Go": ["Web", "Systems Programming", "Backend"],
        "Groovy": ["Web", "Scripting", "Backend"],
        "Haskell": ["Web", "Functional Programming", "Backend"],
        "Java": ["Web", "Mobile", "Enterprise", "Backend"],
        "JavaScript": ["Web", "Mobile", "Server-Side", "Frontend"],
        "Julia": ["Data Science", "Scientific Computing", "Backend"],
        "Kotlin": ["Mobile", "Web", "Backend"],
        "Lua": ["Game Development", "Embedded Systems", "Backend"],
        "Matlab": ["Data Science", "Scientific Computing", "Backend"],
        "Objective-C": ["Mobile", "Desktop", "Backend"],
        "Perl": ["Web", "Scripting", "Backend"],
        "PHP": ["Web", "Server-Side", "Backend"],
        "Powershell": ["Scripting", "System Administration", "Backend"],
        "Python": ["Web", "Data Science", "Automation", "AI", "Backend"],
        "R": ["Data Science", "Statistics", "Backend"],
        "Ruby": ["Web", "Scripting", "Backend"],
        "Rust": ["Systems Programming", "Web", "Backend"],
        "Scala": ["Web", "Functional Programming", "Backend"],
        "Swift": ["Mobile", "Web", "Frontend"],
        "TypeScript": ["Web", "Mobile", "Frontend"],
        "VBA": ["Automation", "Backend"],
        "Visual Basic": ["Desktop", "Scripting", "Backend"],
    }

    # Fechas de creación de los lenguajes
    creation_dates = {
        "Abap": "1983-01-01",
        "Ada": "1980-01-01",
        "C/C++": "1972-01-01",
        "C#": "2000-01-01",
        "Cobol": "1959-01-01",
        "Dart": "2011-01-01",
        "Delphi/Pascal": "1983-01-01",
        "Go": "2007-01-01",
        "Groovy": "2003-01-01",
        "Haskell": "1990-01-01",
        "Java": "1995-01-01",
        "JavaScript": "1995-01-01",
        "Julia": "2012-01-01",
        "Kotlin": "2011-01-01",
        "Lua": "1993-01-01",
        "Matlab": "1984-01-01",
        "Objective-C": "1984-01-01",
        "Perl": "1987-01-01",
        "PHP": "1995-01-01",
        "Powershell": "2006-01-01",
        "Python": "1991-01-01",
        "R": "1993-01-01",
        "Ruby": "1995-01-01",
        "Rust": "2010-01-01",
        "Scala": "2003-01-01",
        "Swift": "2014-01-01",
        "TypeScript": "2012-01-01",
        "VBA": "1991-01-01",
        "Visual Basic": "1991-01-01",
    }

    # Fechas clave de tendencias
    TRENDS = {
        "Web": "1995-01-01",
        "Mobile": "2010-01-01",
        "AI": "2020-01-01",
        "Data Science": "2020-01-01",
        "Automation": "2015-01-01",
        "Game Development": "2005-01-01",
        "Embedded Systems": "1980-01-01",
        "Systems Programming": "1970-01-01",
        "Scripting": "1990-01-01",
        "Enterprise Applications": "1980-01-01",
    }

    def update_categories(row):
        base_categories = categories.get(row["language"], []).copy()
        date = row["Date"]
        filtered_categories = [
            cat
            for cat in base_categories
            if date >= pd.Timestamp(TRENDS.get(cat, "1970-01-01"))
        ]
        return filtered_categories

    df_long["detailCat"] = df_long.apply(
        lambda row: ", ".join(update_categories(row)), axis=1
    )
    df_long["categories"] = df_long["detailCat"].apply(
        lambda x: len(x.split(", ")) if x else 0
    )
    df_long["paradigm"] = df_long["language"].map(lambda x: len(paradigms.get(x, [])))
    df_long["created"] = df_long["language"].map(
        lambda x: creation_dates.get(x, "Unknown")
    )
    df_long["detailParadigm"] = df_long["language"].map(
        lambda x: ", ".join(paradigms.get(x, []))
    )
    df_long = df_long[
        [
            "Date",
            "language",
            "popularity",
            "paradigm",
            "categories",
            "created",
            "detailCat",
            "detailParadigm",
        ]
    ]
    df_long["Date"] = pd.to_datetime(df_long["Date"])
    df_long["Date"] = df_long["Date"].dt.strftime("%b-%Y")
    fig = px.scatter_ternary(
        df_long,
        a="popularity",
        b="paradigm",
        c="categories",
        animation_frame="Date",
        template="plotly_dark",
        height=600,
        size="popularity",
        size_max=15,
        color="language",
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
                html.H6(id="sub-title-plot", className="px-2 my-0 py-0"),
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
                html.H3("Popular Programming Languages", className="p-2"),
                html.Span(
                    "STORY Week 10 FF 2025",
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
        html.Div([dcc.Graph(figure=graphCategory(), config=config)]),
        html.Div([dcc.Graph(figure=graphTernary(), config=config)]),
    ]
    text = [
        (
            "Popular Programming Languages:Trends",
            "Most widely used languages, their associated categories, and the trends that have influenced their development.",
        ),
        (
            "Programming Languages: Trends and Paradigms",
            "Trends and paradigms influence the popularity of languages..",
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
    app.run_server(debug=True)
