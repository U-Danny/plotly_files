import dash
from dash import Input, Output, dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from urllib.request import urlopen
import json
import plotly.express as px
import plotly.express as px
import PIL
import cairosvg
import plotly.express as px
import io
import numpy as np
import pandas as pd


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

#Function generate color scale in array svg
def genCategoryColor(matrix,start = 0.33, end = 1, color_rgb=[255,0,0]):
    for x in range(int(round(matrix.shape[0]*start,0)), int(round(matrix.shape[0]*end,0))):
        if (np.any(matrix[x,:,:])):  
            for y in range(matrix.shape[1]): 
                if (np.any(matrix[x][y])):
                    if x>=matrix.shape[0]*start and x < matrix.shape[0]*end:
                        matrix[x][y] = [color_rgb[0],color_rgb[1],color_rgb[2],list(matrix[x][y])[-1]]
                        # x_l.append(x)
                        # y_l.append(y)
                        # color_l.append()
    return matrix

#Function generate annotation in chart
def addAnnotation(fig,shape, start= 0.33, end = 1, text='Annotation'):
     fig.add_annotation(
        x=0,
        y=shape[0]*((start+end)/2),
        text=text,
        showarrow=True,
        xanchor="right",
        ax=-50,
        ay=0,
        arrowsize=0.5,
    )

df = pd.read_csv("https://raw.githubusercontent.com/plotly/Figure-Friday/refs/heads/main/2024/week-46/PDO_wine_data_IT_FR.csv")
df['Max_yield_hl'] = pd.to_numeric(df['Max_yield_hl'], errors='coerce')
df_cleaned = df.dropna(subset=['Max_yield_hl'])  # Remove rows with NaN
countries = {'FR':'FRANCE', 'IT':'ITALY'}
color_discrete_map = {'White': 'rgb(197, 188, 165)', 'Rosé': 'rgb(177, 79, 83)', 'Red': 'rgb(150, 31, 33)'}

def graphViolin():
    fig = px.box(df_cleaned, x='Color', y='Max_yield_hl',color='Color', color_discrete_map=color_discrete_map,
                    facet_col='Country')
    fig.update_layout(            
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0)",
            showlegend=False,
            boxmode = "group", boxgap = 0.5, boxgroupgap = 0
        )
    fig.for_each_annotation(lambda a: a.update(text=countries[a.text.split("=")[-1]]))
    fig.update_xaxes(visible=True, showticklabels=True, showgrid=True, title="")
    return fig


def graphPictorial(country = 'FRANCE'):
    data = {'ITALY':[
                {'value':48.27,'name':'White', 'start':0, 'end': 0.166, 'color':[197, 188, 165]},
                {'value':7.31,'name':'Rosé', 'start':0.166, 'end': 0.188986, 'color':[177, 79, 83]},
                {'value':44.42,'name':'Red', 'start':0.188985, 'end': 0.34, 'color':[150, 31, 33]},
                {'value':0,'name':'Over', 'start':0.34, 'end': 1, 'color':[187, 185, 192]},
            ],
            'FRANCE':[
                {'value':47.08,'name':'White', 'start':0, 'end': 0.160068, 'color':[197, 188, 165]},
                {'value':16.77,'name':'Rosé', 'start':0.160068, 'end': 0.21707, 'color':[177, 79, 83]},
                {'value':36.16,'name':'Red', 'start':0.21707, 'end': 0.34, 'color':[150, 31, 33]},
                {'value':0,'name':'Over', 'start':0.34, 'end': 1, 'color':[187, 185, 192]},
            ]
          }
    df = pd.DataFrame(data[country])
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><!--!Font Awesome Free 6.6.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.--><path d="M256.814,72.75c0-26.898-10.451-52.213-29.43-71.277C226.444,0.529,225.17,0,223.84,0H87.712c-1.329,0-2.604,0.529-3.543,1.473c-18.978,19.064-29.43,44.379-29.43,71.277c0,50.615,37.414,92.654,86.037,99.922v108.88h-21.25c-8.271,0-15,6.729-15,15c0,8.271,6.729,15,15,15h72.5c8.271,0,15-6.729,15-15c0-8.271-6.729-15-15-15h-21.25v-108.88C219.399,165.404,256.814,123.365,256.814,72.75z M106.709,120.879c-1.234,1.083-2.765,1.615-4.285,1.615c-1.807,0-3.604-0.748-4.888-2.212c-13.153-14.986-18.888-34.832-15.733-54.451c0.571-3.543,3.902-5.956,7.45-5.385c3.544,0.57,5.955,3.905,5.386,7.45c-2.538,15.779,2.079,31.747,12.667,43.811C109.674,114.404,109.406,118.511,106.709,120.879z M144.351,136.662c-0.514,3.194-3.274,5.468-6.409,5.468c-0.343,0-0.69-0.027-1.041-0.083c-6.937-1.117-13.6-3.299-19.804-6.488c-3.193-1.641-4.451-5.559-2.811-8.752c1.641-3.194,5.563-4.451,8.752-2.81c4.985,2.562,10.345,4.317,15.929,5.215C142.511,129.782,144.922,133.118,144.351,136.662z"/></svg>'
    im = PIL.Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg))).convert("RGBA")
    matrix = np.array(im)
    for index, row in df.iterrows():
        matrix = genCategoryColor(matrix,row['start'],row['end'],list(row['color']))

    fig = px.imshow(
            matrix,
            y= range(matrix.shape[0]-50),
            x= range(matrix.shape[1]),
            height=500,
            width=400,
            template='none',
            labels=dict(x="X", 
                        y="Y", 
                        color="Color")
            )

    for index, row in df.iterrows():
        if row['name'] != 'Over':
            addAnnotation(fig,matrix.shape,row['start'],row['end'],str(row['value'])+'% '+row['name'])

    fig.update_xaxes(title = 'Time', showticklabels=False, visible = False)
    fig.update_yaxes(visible=False, type='linear', showticklabels=False)
    fig.update_layout(coloraxis_showscale=False,margin=dict(l=20,r=20,b=20,t=20))
    fig.update_layout(coloraxis_colorbar_x=0.8)
    fig.update_layout(
            title_text=country,
            title_x=0.5,
            title_y=0.95,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0)",
        )
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
                html.H3("Wines in Italy and France", className="p-2"),
                html.Span(
                    "STORY Week 46 FF",
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
        html.Div([
            html.Div([
                dcc.Graph(figure=graphPictorial(country = 'ITALY'), config=config)
            ],className='col-sm-6 text-center'),
            html.Div([
                dcc.Graph(figure=graphPictorial(country = 'FRANCE'), config=config)
            ],className='col-sm-6 text-center'),
        ],className='row px-2'),
        html.Div([dcc.Graph(figure=graphViolin(), config=config)]),
    ]
    text = [
        ("Wine production by color", "The color of wine is an essential aspect both from a visual standpoint and in terms of quality and perception."),
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
