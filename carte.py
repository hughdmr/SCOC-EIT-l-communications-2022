# Louis Vauterin, [27/01/2023 09:48]
from dash import Dash, html, dcc, Input, Output, State, ctx
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pyproj
import geopandas as gpd
import shapely
import json
from functools import partial
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

load_figure_template('LUX')

real_lati = []
real_longi = []


def poi_poly(
    df,
    radius,
    poi={"Longitude": 0.06665166467428207, "Latitude": 51.19034957885742},
    lon_col="Longitude",
    lat_col="Latitude",
    include_radius_poly=False,
):

    # generate a geopandas data frame of the POI
    gdfpoi = gpd.GeoDataFrame(
        geometry=[shapely.geometry.Point(poi["Longitude"], poi["Latitude"])],
        crs="EPSG:4326",
    )
    # extend point to radius defined (a polygon).  Use UTM so that distances work, then back to WSG84
    gdfpoi = (
        gdfpoi.to_crs(gdfpoi.estimate_utm_crs())
        .geometry.buffer(radius)
        .to_crs("EPSG:4326")
    )

    # create a geopandas data frame of all the points / markers
    if not df is None:
        gdf = gpd.GeoDataFrame(
            geometry=df.loc[:, ["Longitude", "Latitude"]]
            .dropna()
            .apply(
                lambda r: shapely.geometry.Point(r["Longitude"], r["Latitude"]), axis=1
            )
            .values,
            crs="EPSG:4326",
        )
    else:
        gdf = gpd.GeoDataFrame(geometry=gdfpoi)

    # create a polygon around the edges of the markers that are within POI polygon
    return pd.concat(
        [
            gpd.GeoDataFrame(
                geometry=[
                    gpd.sjoin(
                        gdf, gpd.GeoDataFrame(geometry=gdfpoi), how="inner"
                    ).unary_union.convex_hull
                ]
            ),
            gpd.GeoDataFrame(geometry=gdfpoi if include_radius_poly else None),
        ]
    )


def initialise_map(dataframe):
    real_lati = []
    real_longi = []

    # original projection
    p = pyproj.Proj('epsg:27572')  # 3347
    # resulting projection, WGS84, long, lat
    outProj = pyproj.Proj('epsg:4326')
    points = dataframe[['X lambert', 'Y lambert']].to_numpy()
    lati_modif = []
    longi_modif = []
    count = 0
    for value in points:
        new_coord = pyproj.transform(p, outProj, value[0], value[1])
        if count % 3 == 0:
            lati_modif.append(new_coord[0]+0.0015)
            longi_modif.append(new_coord[1])
            real_lati.append(new_coord[0])
            real_longi.append(new_coord[1])
        elif count % 3 == 1:
            lati_modif.append(new_coord[0])
            longi_modif.append(new_coord[1]+0.0015)
            real_lati.append(new_coord[0])
            real_longi.append(new_coord[1])
        else:
            lati_modif.append(new_coord[0])
            longi_modif.append(new_coord[1]-0.0015)
            real_lati.append(new_coord[0])
            real_longi.append(new_coord[1])
        count += 1
    dataframe['Lat'] = lati_modif
    dataframe['Long'] = longi_modif

    color_scale = [(0, 'yellow'), (1, 'red')]
    figmap = go.Figure()

    figmap.add_trace(go.Scattermapbox(lat=lati_modif,
                                      lon=longi_modif,
                                      customdata=np.stack((dataframe['debit_prevu'], dataframe['secteur'], dataframe['700 MHz'], dataframe['800 MHz'],
                                                          dataframe['1800 MHz'], dataframe['2100 MHz'], dataframe['2600 MHz'], dataframe['3500 MHz']), axis=-1),
                                      mode='markers',
                                      hoverinfo='text',
                                      hovertemplate='<b>Secteur</b>: %{customdata[1]}' +
                                      '<br><b>Trafic</b>: %{customdata[0]}' + ' Mb/s'+'<br>' +
                                      '<b>700 MHz</b>: %{customdata[2]}' +
                                      '<br><b>800 MHz</b>: %{customdata[3]}<br>' +
                                      '<b>1800 MHz</b>: %{customdata[4]}' +
                                      '<br><b>2100 MHz</b>: %{customdata[5]}<br>' +

                                      # Louis Vauterin, [27/01/2023 09:48]
                                      '<b>2600 MHz</b>: %{customdata[6]}' +
                                      '<br><b>3500 MHz</b>: %{customdata[7]}<br>' +
                                      '<extra></extra>',
                                      marker=go.scattermapbox.Marker(
                                          size=15,
                                          color=dataframe["debit_prevu"],
                                          opacity=0.7,
                                          colorscale=color_scale,
                                          colorbar=dict(title='Débit en Mb/s'),
                                          showscale=False
                                      ),))
    figmap.update_layout(
        title='Emplacement des antennes à La Rochelle',
        mapbox={
            "style": "open-street-map",
            "center": {'lat': 46.18, 'lon': -1.17},

            "zoom": 11.2,

        },
        margin={"r": 5, "t": 0, "l": 5, "b": 5}
    )

    return figmap


def add_circles(dataframe):
    real_lati = []
    real_longi = []
    lati_modif = []
    longi_modif = []
    # original projection
    p = pyproj.Proj('epsg:27572')  # 3347
    # resulting projection, WGS84, long, lat
    outProj = pyproj.Proj('epsg:4326')
    points = dataframe[['X lambert', 'Y lambert']].to_numpy()
    count = 0
    for value in points:
        new_coord = pyproj.transform(p, outProj, value[0], value[1])
        if count % 3 == 0:
            real_lati.append(new_coord[0])
            real_longi.append(new_coord[1])
            lati_modif.append(new_coord[0]+0.0015)
            longi_modif.append(new_coord[1])
        elif count % 3 == 1:
            real_lati.append(new_coord[0])
            real_longi.append(new_coord[1])
            lati_modif.append(new_coord[0])
            longi_modif.append(new_coord[1]+0.0015)
        else:
            real_lati.append(new_coord[0])
            real_longi.append(new_coord[1])
            lati_modif.append(new_coord[0])
            longi_modif.append(new_coord[1]-0.0015)
        count += 1
    fig = go.Figure()
    #color_scale = [(0, 'yellow'), (1,'red')]

    fig.add_trace(go.Scattermapbox(lat=lati_modif,
                                   lon=longi_modif,
                                   mode='markers',
                                   customdata=np.stack(
                                       (dataframe['secteur'], dataframe['sature']), axis=-1),
                                   hoverinfo='text',
                                   hovertemplate='<b>Secteur</b>: %{customdata[0]}' +
                                   '<br><b>Sature</b>: %{customdata[1]}'+'<br>'
                                   '<extra></extra>',
                                   marker=go.scattermapbox.Marker(
                                       size=15,
                                       color=dataframe["sature"],
                                       opacity=0.7,
                                       colorscale='bluered'
                                   ),))
    fig.update_layout(
        title='Emplacement des antennes à La Rochelle',
        mapbox={
            "style": "open-street-map",
            "center": {'lat': 46.18, 'lon': -1.17},

            "zoom": 11.2,

        },
        margin={"r": 5, "t": 0, "l": 5, "b": 5}
    )

    return fig


app = Dash(external_stylesheets=[dbc.themes.LUX])
'''

app.layout = html.Div(children=[
    dbc.Row(html.H1('Disposition des antennes Bouygues à La Rochelle')),

    dbc.Row(
        dbc.Col(
             dbc.Row(dbc.RadioItems(['Fréquences','Débits','Cercles'],
                        value='Cercles',
                        id='radio-param'
        ),
            dbc.Row(html.Div(dcc.Slider(
                min=1,
                max=5,
                marks={
                    1: '2023',
                    2: '2024',
                    3:'2025',
                    4:'2026',
                    5:'2027',
                    6:'2028'},
                value=0,
                id='slider-annee'
            ))),
        )


        ),
        dbc.Col(dcc.Graph(id='map-disp',figure={})
        )
    )
])


'''
app.layout = html.Div([


    html.Div(children=[
        html.H1('Disposition des antennes Bouygues à La Rochelle'),
        html.Label('Paramètres'),
        dcc.RadioItems(['Fréquences', 'Débits', 'Cercles'],
                       value='Cercles',

                       # Louis Vauterin, [27/01/2023 09:48]
                       id='radio-param'
                       ),

        html.Br(),
        html.Label('Année'),
        dcc.Slider(
            min=1,
            max=5,
            marks={
                1: '2023',
                2: '2024',
                   3: '2025',
                   4: '2026',
                   5: '2027',
                   6: '2028'},
            value=0,
            id='slider-annee'
        ),
        html.Div(id='output-slider'),
        html.Div(dcc.Graph(id='map-disp', figure={}))
    ], style={'padding': 10, 'flex': 1})
], style={'display': 'flex', 'flex-direction': 'row'})
# ,'background-image':'url("/assets/francois.jpeg")'


# action a realiser lorsque changement checkbox

@app.callback(
    Output("map-disp", "figure"),
    Input('radio-param', 'value'),
    Input('slider-annee', 'value'),
    State('radio-param', 'value'),
    prevent_initial_call=True
)
def update_disp(value1, valueslider, valueradio):
    triggered_id = ctx.triggered_id
    if triggered_id == 'radio-param':
        if value1 == 'Débits':
            return initialise_map(pd.read_csv("exports/export_2023.csv"))
        elif value1 == 'Cercles':
            return add_circles(pd.read_csv("exports/export_2023.csv"))

    elif triggered_id == 'slider-annee':
        if valueslider < 2:
            df = pd.read_csv('exports/export_2023.csv')
        elif 2 <= valueslider < 3:
            df = pd.read_csv('exports/export_2024.csv')
        elif 3 <= valueslider < 4:
            df = pd.read_csv('exports/export_2025.csv')
        elif 4 <= valueslider < 5:
            df = pd.read_csv('exports/export_2026.csv')
        elif 5 <= valueslider < 6:
            df = pd.read_csv('exports/export_2027.csv')
        elif valueslider == 6:
            df = pd.read_csv('exports/export_2027.csv')
        if valueradio == 'Débits':
            return initialise_map(df)
        else:
            return add_circles(df)


app.run_server(debug=True)


'''
def add_circles():
    figmap =initialise_map()
    lay = []

    for latitude, longitude in zip(real_lati,real_longi):
        lay.append({
                        "source": json.loads(poi_poly(None, poi={"Latitude":latitude,"Longitude": longitude}, radius=300).to_json()),
                        "below": "traces",
                        "type": "fill",
                        "opacity":0.2,
                        "color": "green",
        })

    figmap.update_layout(
            title='Emplacement des antennes à La Rochelle',
            mapbox={
                "style": "open-street-map",
                "center": {'lat':46.16,'lon':-1.1},
                "zoom": 10,
                "layers": lay,
            },
        )
    print('Done')
    return figmap

'''
