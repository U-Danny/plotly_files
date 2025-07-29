import geopandas as gpd
from shapely.geometry import Polygon, LineString, MultiPolygon, MultiLineString, Point
from shapely import union_all
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import plotly.graph_objects as go


df = pd.read_csv("fig-friday-data-july-4-2025/model-grid-subsample.csv")
df = df[df.dem_m > df.zkm * 1e3]

df["x"] = df["xkm"] * 1e3
df["y"] = df["ykm"] * 1e3
df["z"] = df["zkm"] * 1e3
df["salinity"] = df["mean_tds"]

spacing = 100
x_range = np.arange(df.x.min(), df.x.max(), spacing)
y_range = np.arange(df.y.min(), df.y.max(), spacing)
z_range = np.arange(df.z.min(), df.z.max(), spacing)
X, Y, Z = np.meshgrid(x_range, y_range, z_range, indexing="ij")
points = df[["x", "y", "z"]].values
values = df["salinity"].values
grid_salinity = griddata(points, values, (X, Y, Z), method="linear")


def get_coordinates(geom):
    if isinstance(geom, Point):
        return [geom.x], [geom.y]
    elif isinstance(geom, (LineString, MultiLineString)):
        x, y = [], []
        geoms = geom.geoms if isinstance(geom, MultiLineString) else [geom]
        for g in geoms:
            xi, yi = g.xy
            x.extend(xi)
            y.extend(yi)
        return x, y
    elif isinstance(geom, (Polygon, MultiPolygon)):
        x, y = [], []
        geoms = geom.geoms if isinstance(geom, MultiPolygon) else [geom]
        for g in geoms:
            xi, yi = g.exterior.coords.xy
            x.extend(xi)
            y.extend(yi)
        return x, y
    else:
        raise ValueError(f"Geometría no soportada: {type(geom)}")


def mainMap():
    gdf1 = gpd.read_file("CA_Boundary/CA_Boundary.shp").to_crs(epsg=4326)
    gdf2 = gpd.read_file(
        "Major_rivers_of_California/Major_rivers_of_California.shp"
    ).to_crs(epsg=4326)

    gdf_pts = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.Longitude, df.Latitude),
        crs="EPSG:4326",
    )
    polygon = union_all(gdf_pts.geometry).convex_hull
    centroid = polygon.centroid
    centroid_lon = float(centroid.x)
    centroid_lat = float(centroid.y)
    fig = go.Figure()
    for idx, row in gdf1.iterrows():
        x, y = get_coordinates(row.geometry)
        fig.add_trace(
            go.Scattermapbox(
                lon=x,
                lat=y,
                mode="lines",
                fill="toself",
                fillcolor="rgba(0,128,0,0.3)",
                line=dict(color="green", width=1),
                name=f"Área {idx+1}",
                showlegend=False,
            )
        )
    for idx, row in gdf2.iterrows():
        x, y = get_coordinates(row.geometry)
        fig.add_trace(
            go.Scattermapbox(
                lon=x,
                lat=y,
                mode="lines",
                line=dict(color="blue", width=2),
                name=f"Río {idx+1}",
                showlegend=False,
            )
        )
    fig.add_trace(
        go.Scattermapbox(
            lon=[centroid_lon],
            lat=[centroid_lat],
            mode="markers+text",
            marker=dict(size=20, color="red", opacity=0.5),
            text=["San Ardo, California, EE. UU."],
            textposition="bottom right",
            textfont=dict(size=14, color="red"),
            name="Zona",
            customdata=["abrir_modal"],
            showlegend=False,
        )
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=5,
        mapbox_center={"lat": centroid_lat, "lon": centroid_lon},
        margin=dict(r=0, t=0, l=0, b=0),
        height=700,
        showlegend=False,
        title={
            "text": ("<b>Geospatial Visualization of the Study Area</b>"),
            "x": 0.01,
            "y": 0.98,
            "font": {"size": 20},
        },
    )
    return fig


voxel_volume = spacing**3
ranges = [0, 1500, 5000, 9000, np.nanmax(values)]
volume_summary = {}
flat_salinity = grid_salinity.flatten()
valid_mask = ~np.isnan(flat_salinity)
valid_values = flat_salinity[valid_mask]

for i in range(len(ranges) - 1):
    lower = ranges[i]
    upper = ranges[i + 1]
    mask = (valid_values >= lower) & (valid_values < upper)
    n_voxels = np.sum(mask)
    volume_m3 = n_voxels * voxel_volume
    volume_summary[f"{int(lower)}–{int(upper)} mg/L"] = volume_m3

total_volume = sum(volume_summary.values())
volume_description_component = html.Div(
    [
        html.P(
            "Interpolated volume segmented by key salinity ranges in the subsurface:"
        ),
        *[
            html.Div(
                [
                    html.Sup(
                        f" ▸ Range {k}: {v/1e6:.2f} Mm³ ({(v/total_volume)*100:.1f}%)"
                    ),
                    html.Br(),
                ]
            )
            for k, v in volume_summary.items()
        ],
        html.Br(),
        html.B(f"Estimated total visible volume: {total_volume/1e6:.2f} Mm³"),
        html.P(
            "Note: This volume reflects only the portion covered by available data and interpolation — not the total aquifer volume."
        ),
    ]
)


def volumen3D():
    fig = go.Figure(
        data=go.Volume(
            x=X.flatten(),
            y=Y.flatten(),
            z=Z.flatten(),
            value=grid_salinity.flatten(),
            isomin=np.nanmin(values),
            isomax=np.nanmax(values),
            opacity=0.1,
            surface_count=25,
            colorscale="RdYlBu_r",
            caps=dict(x_show=False, y_show=False, z_show=False),
            colorbar=dict(
                title="Salinity (mg/L)",
                orientation="v",
                x=-0.01,
                xanchor="center",
                y=0.5,
                thickness=10,
                len=0.6,
                tickvals=np.linspace(np.nanmin(values), np.nanmax(values), 5),
                tickformat=".0f",
            ),
        )
    )

    fig.update_layout(
        title={
            "text": "Estimated Volumes (Mm³) in Key Salinity Ranges",
            "x": 0.5,
            "y": 0.99,
            "xanchor": "center",
        },
        height=400,
        template="none",
        scene=dict(
            xaxis_title="x (m)",
            yaxis_title="y (m)",
            zaxis_title="Depth value (m)",
            bgcolor="white",
            aspectmode="manual",
            aspectratio=dict(x=1.2, y=1.2, z=0.3),
        ),
        margin=dict(l=10, r=10, b=0, t=10),
    )

    return fig


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    [
        dcc.Graph(id="mapa", figure=mainMap()),
        dbc.Modal(
            id="modal",
            is_open=False,
            size="xl",
            backdrop=True,
            scrollable=True,
            style={"maxWidth": "95vw", "margin": "2vh auto", "minHeight": "85vh"},
            children=[
                dbc.ModalHeader("San Ardo, California, EE. UU."),
                dbc.ModalBody(
                    dbc.Container(
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Graph(
                                        id="grafico-adicional",
                                        figure=volumen3D(),
                                    ),
                                    width=8,
                                ),
                                dbc.Col(
                                    volume_description_component,
                                    width=4,
                                    style={"maxHeight": "700px", "overflowY": "auto"},
                                ),
                            ],
                            className="g-4",
                        ),
                        fluid=True,
                    )
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close-modal", className="ms-auto", n_clicks=0
                    )
                ),
            ],
        ),
    ]
)


@app.callback(
    Output("modal", "is_open"),
    Input("mapa", "clickData"),
    Input("close-modal", "n_clicks"),
    State("modal", "is_open"),
)
def toggle_modal(clickData, n_close, is_open):
    if clickData and clickData["points"][0].get("customdata") == "abrir_modal":
        return True
    if n_close:
        return False
    return is_open


if __name__ == "__main__":
    app.run(debug=True)
