import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
from urllib.request import urlopen
import numpy as np
import plotly.express as px
from wordcloud import WordCloud


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
    "toImageButtonOptions": {
        "format": "png",
        "filename": "I-Digital",
        "height": 500,
        "width": 700,
        "scale": 1,
    },
}

df = pd.read_csv('https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2024/week-47/scrubbed.csv', low_memory=False)
df['year'] = pd.to_datetime(df['date posted']).dt.year
df['datetime'] = pd.to_datetime(df['datetime'], format='%m/%d/%Y %H:%M',  errors='coerce')
df['month'] = df['datetime'].dt.strftime('%B')
df['day'] = df['datetime'].dt.strftime('%A')

df_polarity = pd.read_csv(
    "https://raw.githubusercontent.com/U-Danny/test-dataset/refs/heads/main/polarity_sub.csv",sep=';'
)
df_polarity = df_polarity.sort_values(by=['year'], ascending=True)

df_tf_idf = pd.read_csv("https://raw.githubusercontent.com/U-Danny/test-dataset/refs/heads/main/tf_idf.csv",index_col=0).squeeze()

def graphScatter3d():
    df_3 = df[['year','month','day']]
    df_3 = df_3.groupby(['year','month','day'])['day'].count().reset_index(name='valor')
    months = ['January', 'February', 'March', 'April', 'May', 'June','July', 'August', 'September', 'October', 'November', 'December']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    fig = px.scatter_3d(df_3, x='month', y='day', z='year', size='valor', size_max=40,template='none',
                color='valor', color_continuous_scale='ice_r', height=500,)
    fig.update_scenes(
        xaxis_categoryarray= months,
        yaxis_categoryarray= days,    
    )
    fig.update_traces(
        marker=dict(
            #sizemin=1,
            line=dict(width=0)
        )
    )
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0))
    return fig


def graphWordCloud():
    word_freq = df_tf_idf.to_dict()
    wordcloud = WordCloud(width=800, height=300, background_color='white').generate_from_frequencies(word_freq)
    image_array = np.array(wordcloud.to_array())
    fig = px.imshow(image_array, template='none',height=400)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0))
    return fig

def graphPolarity():    
    fig = px.scatter(df_polarity,x='polaridad', y='subjetividad', color='polaridad', color_continuous_scale='rdbu',
                    animation_frame='year',
                    hover_name="datetime", hover_data=["comments", "polaridad"], template='none')
    return fig


# Create the Dash app
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
                                className="fa-solid fa-circle-arrow-left fa-2xl text-dark",
                            ),
                            className="rounded-pill btn-link px-2 col",
                            outline=True,
                            id="prev",
                            n_clicks=0,
                        ),
                        dbc.Button(
                            html.I(
                                id="icon-next",
                                className="fa-solid fa-circle-arrow-right fa-3x text-dark",
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
                html.H5(id="title-plot", className="px-2 my-0 py-0 text-dark fw-bold"),
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
                html.H3("UFO sightings in north America since the 20th century", className="p-2"),
                html.Span(
                    "STORY Week 47 FF",
                    className="ms-auto",
                    style={"fontSize": "smaller", "color": "gray"},
                ),
            ],
            className="container text-center d-flex",
        ),
        html.Div(
            [slider_plot, carousel, sub_controls, plot], className="bg-light container"
        ),
    ],
    fluid=True,
    className="bg-light vh-100",
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
        html.Div([dcc.Graph(figure=graphScatter3d(), config=config)]),
        html.Div([dcc.Graph(figure=graphWordCloud(), config=config)]),        
        html.Div([dcc.Graph(figure=graphPolarity(), config=config)]),
    ]
    text = [
        ("Wine production by color", "The color of wine is an essential aspect both from a visual standpoint and in terms of quality and perception."),
        ("Hectoliters per hectare", "Max allowed yield of hectoliters per hectare (Italy / France)"),
        ("Hectoliters per hectare", "Max allowed yield of hectoliters per hectare (Italy / France)"),
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
