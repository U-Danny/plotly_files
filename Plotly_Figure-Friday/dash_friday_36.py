import dash
from dash import dcc
from dash import html, Input, Output, ctx, callback
import plotly.express as px
import pandas as pd
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
BS = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css'
external_stylesheets=[dbc.themes.BOOTSTRAP,dbc_css,BS,dbc.icons.FONT_AWESOME,dbc.icons.BOOTSTRAP]
config = {'displaylogo': False,'queueLength':0,'responsive': True,
          'modeBarButtonsToRemove': ['zoom','pan','select','zoomIn','zoomOut','autoScale','resetScale','lasso2d'],
          'toImageButtonOptions': {'format': 'png','filename': 'I-Digital','height': 500,'width': 700,'scale': 1 }}

url = 'test-dataset/map_density_f36.csv'
df = pd.read_csv(url)

# Create the Dash app
app = dash.Dash(__name__,external_stylesheets=external_stylesheets)

def mapMain():
    fig = px.density_map(df, lat="latitude", lon="longitude", z='index', radius=20,animation_frame="year",
                        zoom=1.2,color_continuous_scale=[
                            [0, '#ACD160'], 
                            [0.02, '#ACD160'], 
                            [0.1, '#F7D55F'], 
                            [0.2, '#F39955'],
                            [0.4, '#ED6669'],
                            [0.76, '#A47DB7'],
                            [1, '#9F7785']],
                            range_color=(0, 230),
                        map_style="carto-positron", height=600, hover_name="location", hover_data={'latitude':False,'longitude':False})

    fig.update_layout(autosize=True,margin={"r":0,"t":0,"l":0,"b":0})
    fig.layout.coloraxis.colorbar.title = 'PM 2.5'
    fig.layout.coloraxis.colorbar.lenmode='fraction'
    fig.layout.coloraxis.colorbar.len=0.9
    fig.layout.coloraxis.colorbar.bgcolor='rgba(255,255,255,0.5)'
    fig.layout.coloraxis.colorbar.thickness=5
    fig.layout.coloraxis.colorbar.x=0.5
    fig.layout.coloraxis.colorbar.y=0
    fig.layout.coloraxis.colorbar.orientation='h'
    return fig

config_pm25 = {
    'Good':                             {'start':0.0,'end':9.0,'color':'#ACD160','detail':'Air quality is satisfactory ...'},
    'Moderate':                         {'start':9.1,'end':35.4,'color':'#F7D55F','detail':'Sensitive individuals should avoid outdoor activity ...'},
    'Unhealthy for sensitive Groups':   {'start':35.5,'end':55.4,'color':'#F39955','detail':'General public and sensitive individual ...'},
    'Unhealthy':                        {'start':55.5,'end':125.4,'color':'#ED6669','detail':'Increased likehood of adverse effects and aggravation ..'},
    'Very Unhealthy':                   {'start':125.5,'end':225.4,'color':'#A47DB7','detail':'General public will be noticeably affected ...'},
    'Hazardous':                        {'start':225.5, 'end':250.0,'color':'#9F7785','detail':'General public at high risk of experiencing strong ...'},
}

def setColor(fig):
    for i in config_pm25:
        fig.add_hrect(
            y0=str(config_pm25[i]['start']), y1=str(config_pm25[i]['end']),
            fillcolor=config_pm25[i]['color'], opacity=0.5,
            layer="below", line_width=0,
        )
        fig.add_annotation(
            x=1850,
            y=config_pm25[i]['end']-5,
            text=i+'<br>('+str(config_pm25[i]['start'])+' - '+str(config_pm25[i]['end'])+')',
            showarrow=False,
            xanchor="right",
            ax=-50,
            ay=0,
        )
        

    return fig
def lineChart(countries):
    fig = px.line(df[df['location'].isin(countries)], x="year", y="index", color='location', height=550)
    fig.update_layout(yaxis_range=[0,230],xaxis_range=[1850,2021],margin={"r":0,"t":20,"l":200,"b":0})
    fig = setColor(fig)
    fig.update_yaxes(visible=False, showticklabels=False, showgrid=False, title='')
    fig.update_xaxes(showgrid=False)
    return fig

title = html.Div([
    html.H4("Air quality  1850 - 2021"),
], className='container-fluid text-center')

menu = html.Div(
    [
        html.Button(
            children=[html.I(className="bi bi-globe-americas"), ' Mapa'], 
            id='btn-nclicks-1', 
            n_clicks=0,
            className='btn btn-sm btn-outline-primary'),
        html.Button(
            children=[html.I(className="bi bi-graph-up-arrow"), ' Gráfico'], 
            id='btn-nclicks-2', 
            n_clicks=0,
            className='btn btn-sm btn-outline-primary mx-2'),
    ],className='py-2'
)

distribution = html.Div([dcc.Loading(id="ls-loading-2",color='#018E99', type="cube", style={'padding-top':'100px'},
    children=[        
        html.Div([dcc.Graph(figure=mapMain(),config=config,clear_on_unhover=True)]),        
    ])])

graph = html.Div([
    dcc.Dropdown(
        list(set(df['location'])),
        [list(set(df['location']))[0]],
        multi=True,
        id='id-drop',
    ),
    html.Div([dcc.Graph(id='graph-main',figure=lineChart([list(set(df['location']))[0]]), config=config)])
    ]
)

main_div = html.Div([distribution],id='main-div')

app.layout = dbc.Container(
    [
        title,
        menu,
        main_div
    ],
    id="main-container",
    fluid=True,
    className="bg-white text-info vh-100",
)


@app.callback(
    Output("main-div", "children"), 
    [Input('btn-nclicks-1', 'n_clicks'),
    Input('btn-nclicks-2', 'n_clicks'),],
    prevent_initial_call=True
)
def displayClick(btn1, btn2):
    if "btn-nclicks-1" == ctx.triggered_id:
        return distribution
    elif "btn-nclicks-2" == ctx.triggered_id:
        return graph

@app.callback(
    Output("graph-main", "figure"),     
    Input('id-drop', 'value'),
    prevent_initial_call=True
)
def displayClick(value):    
    return lineChart(value)




if __name__ == '__main__':
    app.run_server(debug=True)
