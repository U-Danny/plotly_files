from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dash import html, Input, Output
import pandas as pd
from urllib.request import urlopen
import json
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np

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
df['mount'] = df['datetime'].dt.strftime('%B')
df['day'] = df['datetime'].dt.strftime('%A')

def graphHeatmap(year=2014):
    df_sub = df[df['year'] == year]
    df_sub = df_sub[['year','mount','day']]
    df_x = df_sub.groupby(['year','mount','day'])['day'].count().reset_index(name='valor')
    df_x = df_x.pivot(index='day', columns='mount', values='valor')
    mounts = ['January', 'February', 'March', 'April', 'May', 'June','July', 'August', 'September', 'October', 'November', 'December']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    fig = px.imshow(df_x, color_continuous_scale='BuGn',x=[m for m in mounts if m in list(df_x.columns)],y=[d for d in days if d in list(df_x.index)],
                    height=400,template='plotly_dark')
    fig.update_layout(margin=dict(l=10,r=0,t=60,b=100), title='Sightings on days and months.')
    return fig

def graphWord(year=2014):
    df_x = df[df['year'] == year]
    text = ''
    for c in list(df_x['comments']):
        text += str(c)
    wordcloud = WordCloud().generate(text)
    wordcloud = WordCloud(
        height=300,
        width=600,
        background_color='black',
        colormap='viridis'
    ).generate(text)
    image_array = np.array(wordcloud.to_array())
    fig = px.imshow(image_array, template='plotly_dark',height=400)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(margin=dict(l=40,r=40,t=40,b=40), title='Most common words in the comments.')
    return fig

app = Dash(__name__, external_stylesheets=external_stylesheets)

title = html.Div(
    [html.H5("UFO sightings in north America since the 20th century", className="p-2 text-center")]
)
slider = html.Div([
    dcc.Slider(min(df['year']),max(df["year"]), 1,
               value=2014,
               marks={i: str(i) for i in list(set(df["year"]))},
               id='id-slider'
    ),
], className='px-3 pt-3')
body = html.Div([
    html.Div([
        dcc.Graph(
                id="id-Heat", figure= graphHeatmap(2014), config=config, clear_on_unhover=True
            )
    ],className='col-sm-6 mx-0 px-0'),
    html.Div([
        dcc.Graph(
                id="id-Word", figure= graphWord(2014), config=config, clear_on_unhover=True
            )
    ],className='col-sm-6 mx-0 px-0'),
],className='row pt-5')

app.layout = html.Div([title, slider, body], className="bg-dark text-info vh-100")

@app.callback(
    [Output("id-Heat", "figure"),
     Output("id-Word", "figure"),],
    Input("id-slider", "value"),
    prevent_initial_call=True,
)
def displayClick(value):
    return [graphHeatmap(value),graphWord(value)]

if __name__ == "__main__":
    app.run_server(debug=True)
