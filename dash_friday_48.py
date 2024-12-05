import dash
from dash import dcc
from dash import html, Input, Output, ctx, callback
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from urllib.request import urlopen
import json
import numpy as np
import plotly.graph_objects as go
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score


dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
BS = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css'
external_stylesheets=[dbc.themes.BOOTSTRAP,dbc_css,BS,dbc.icons.FONT_AWESOME,dbc.icons.BOOTSTRAP]
config = {'displaylogo': False,'queueLength':0,'responsive': True,
          'modeBarButtonsToRemove': ['pan','select','autoScale','resetScale','lasso2d'],
          'toImageButtonOptions': {'format': 'png','filename': 'I-Digital','height': 500,'width': 700,'scale': 1 }}

with urlopen(
    "https://raw.githubusercontent.com/U-Danny/test-dataset/refs/heads/main/countries.geo.json"
) as response:
    countries = json.load(response)

df = pd.read_csv('https://raw.githubusercontent.com/U-Danny/test-dataset/refs/heads/main/country_resume.csv', sep=';')
df_internet = pd.read_csv('https://raw.githubusercontent.com/U-Danny/test-dataset/refs/heads/main/internet.csv')

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)

def graphMap():
    fig = px.choropleth_mapbox(
        df,
        geojson=countries,
        color="internet_use",
        locations="country_code",
        opacity=1,
        mapbox_style="carto-positron",
        zoom=0,
        custom_data=["country_name", "internet_use",'population'],
        color_continuous_scale="ice",
        height=435
    )    
    fig.update_layout(autosize=True, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.layout.coloraxis.colorbar.title = "\tUse of internet <br>"
    fig.layout.coloraxis.colorbar.ticksuffix = "%"
    fig.layout.coloraxis.colorbar.lenmode = "fraction"
    fig.layout.coloraxis.colorbar.len = 0.9
    fig.layout.coloraxis.colorbar.bgcolor = "rgba(255,255,255,0.85)"
    fig.layout.coloraxis.colorbar.thickness = 5
    fig.layout.coloraxis.colorbar.x = 0.5
    fig.layout.coloraxis.colorbar.y = 0
    fig.layout.coloraxis.colorbar.orientation = "h"
    fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>Percentage: %{customdata[1]}%<br>population: %{customdata[2]}")
    return fig

def graphLine(df):    
    x = np.array(list(map(int, list(df.columns))))
    y = np.array(df.iloc[0].tolist())
    max_degree = 8
    best_degree = 1
    best_score = float('-inf')
    for degree in range(1, max_degree + 1):
        poly = PolynomialFeatures(degree)
        x_poly = poly.fit_transform(x.reshape(-1, 1))
        model = LinearRegression()
        score = cross_val_score(model, x_poly, y, cv=5, scoring='r2').mean()
        if score > best_score:
            best_score = score
            best_degree = degree

    poly = PolynomialFeatures(best_degree)
    x_poly = poly.fit_transform(x.reshape(-1, 1))
    model = LinearRegression()
    model.fit(x_poly, y)
    coefficients = np.append(model.intercept_, model.coef_[1:])
    coeficient = coefficients
    reversed_list = coeficient[::-1]
    adjusted_coefficients = reversed_list.copy()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers', name='Original data',marker=dict(color='#286a79', size=5)))
    target_values = [50, 75, 90, 100]
    target_color = ['red', 'blue', 'green', '#7aff05']
    x_futures = []
    
    index = 0
    if 0 <= max(df.iloc[0].tolist()) < 50.0:
        index = 0
    elif 50.0 <= max(df.iloc[0].tolist()) < 75.0:
        index = 1
    elif 75.0 <= max(df.iloc[0].tolist()) < 90.0:
        index = 2
    elif 90.0 <= max(df.iloc[0].tolist()) < 100.0:
        index = 3
    else:
        index = -1
    if index >= 0:
        y_future = target_values[index]
        adjusted_coefficients[-1] -= target_values[index]
        roots = np.roots(adjusted_coefficients).real
        x_future = roots[roots > max(x)]
        x_futures.append(x_future)
        x_fit = np.linspace(min(x), max(x_future) if x_future.size > 0 else max(x), 200)
        x_fit_poly = poly.transform(x_fit.reshape(-1, 1))
        y_fit = model.predict(x_fit_poly)
        if x_future.size > 0:
            fig.add_trace(go.Scatter(x=[x_future[0]], y=[y_future], mode='markers',
                                    name=f'Prediction: {y_future:.2f}% year:{x_future[0]:.0f}', 
                                    marker=dict(color=target_color[index], size=10)))
        fig.add_trace(go.Scatter(x=x_fit, y=y_fit, mode='lines', name=f'Prediction line (Grade {best_degree})', line=dict(color='#0090b0', width=1)))

    fig.update_layout(legend=dict(x=0.01, y=0.98), template='plotly_white', height=400)
    fig.update_layout(yaxis_range=[0,110],margin={"r":0,"t":20,"l":20,"b":40})
    fig.update_yaxes(title='Percentage',
        tickvals=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100], 
        ticktext=['10 %', '20 %', '30 %', '40 %', '50 %', '60 %', '70 %', '80 %', '90 %', '100 %'] )

    graph = html.Div([
        html.Div([dcc.Graph(figure=fig, config=config)]),
    ])

    return graph

title = html.Div([
    html.H4("Internet Usage by Country and Projection to Achieve High Digital Inclusion."),    
    
], className='container-fluid text-start p-2')

footer = html.Div([
    html.Div([
            html.I(className="bi bi-check-circle-fill me-2"),
                    "In advanced economies, a penetration rate above 90% is considered indicative of a high level of digital inclusion.."
        ],className='py-0 my-0 text-success',style={'fontSize':'smaller'}),
    html.Div([        
        html.I(className="bi bi-exclamation-triangle-fill me-2"),
                "The United Nations and the World Bank support initiatives such as ensuring that at least 75% of the global population has access to the Internet by 2030."
        ],className='py-0 my-0 text-primary',style={'fontSize':'smaller'}),    
    html.Div([
        html.I(className="bi bi-x-octagon-fill me-2"),
                    "In developing countries, an intermediate goal could be to surpass 50% of the population with regular access to the Internet."
        ],className='py-0 my-0 text-danger',style={'fontSize':'smaller'}),
],className='p-3',style={'fontSiza':'smaller'})

main = html.Div([
    html.Div([dcc.Graph(id='id-map', figure=graphMap(), config=config)],className='col-sm-6'),
    html.Div([html.Div([],className='text-center')],id='id-content',className='col-sm-6')

],className='row p-2')
app.layout = dbc.Container(
    [
        title,
        main,
        footer
    ],
    id="main-container",
    fluid=True,
    className="bg-light vh-100",
)

@app.callback(
    Output('id-content', 'children'),
    Input('id-map', 'clickData')
)
def update_hover_output(clickData):
    if clickData is None:
        return "Click over a country to see details."
    percent = float(clickData['points'][0]['customdata'][1])
    all_people = (float(clickData['points'][0]['customdata'][2])*(percent/100))
    not_people = float(clickData['points'][0]['customdata'][2])-all_people
    all_people = "%.2f" % (all_people/1000000)
    not_people = "%.2f" % (not_people/1000000)
    percent = "%.2f" % percent    
    country= str(clickData['points'][0]['customdata'][0])
    df_country = df_internet[df_internet['country_name'] == country]        
    df_country = df_country.iloc[:, 2:]
    df_country = df_country.dropna(axis=1)
    df_country = df_country.loc[:, (df_country > 0).all()]
    
    item = html.Div([
        html.Div([
            html.H4([country],className='col-sm-5'),
            html.Div([
                html.Small([
                    html.I(className="bi bi-router me-2"),percent,html.I(className="bi bi-percent me-1")
                ],className='py-0 my-0 text-secondary',style={'fontSize':'medium'}),
                html.Small([
                    html.I(className="bi bi-person-check-fill me-2"),str(all_people)+'M.',
                ],className='py-0 my-0 text-secondary mx-4',style={'fontSize':'medium'}),
                html.Small([
                    html.I(className="bi bi-person-x-fill me-2"),str(not_people)+'M.',                    
                ],className='py-0 my-0 text-secondary',style={'fontSize':'medium'}),
            ],className='col-sm-7')
        ],className='row'),       
        
        html.Div([graphLine(df_country)])
    ])

    return item

if __name__ == '__main__':
    app.run_server(debug=True)
