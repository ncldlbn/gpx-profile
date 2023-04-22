import gpxpy
import pandas as pd
import geopy.distance
from shapely.geometry import LineString
import json

import plotly.io as pio
import plotly.graph_objects as go
pio.renderers.default='browser'

# -----------------------------------------------------------------------------
# FUNZIONI
# -----------------------------------------------------------------------------

def gpx2df(path):
    # apriamo il file GPX
    with open(path, "r") as f:
        gpx = gpxpy.parse(f)
    points = []
    for segment in gpx.tracks[0].segments:
        for p in segment.points:
            points.append({
                'time': p.time,
                'latitude': p.latitude,
                'longitude': p.longitude,
                'elevation': p.elevation,
            })
    df = pd.DataFrame.from_records(points)
    # distanza e distanza cumulata
    coords = [(p.latitude, p.longitude) for p in df.itertuples()]
    df['distance'] = [0] + [geopy.distance.distance(from_, to).m for from_, to in zip(coords[:-1], coords[1:])]
    df['cumulative_distance'] = df.distance.cumsum()
    return df

def semplifica_profilo(df, tolleranza):
    # Per semplificare il profilo altimetrico con l'algoritmo di Douglas-Peucker e la libreria Shapely puoi utilizzare questo codice:
    # creiamo una LineString a partire dai punti del profilo altimetrico
    line = LineString([(x, y) for x, y in zip(df['cumulative_distance'], df['elevation'])])
    # semplifichiamo la LineString con l'algoritmo di Douglas-Peucker
    simplified_line = line.simplify(tolerance=tolleranza)
    # estraiamo i punti semplificati
    simplified = pd.DataFrame(simplified_line.coords._coords)
    simplified.columns = ['distance', 'elevation']
    simplified['length'] = simplified['distance'].diff()
    simplified['slope'] = simplified['elevation'].diff()/simplified['distance'].diff()*100
    return simplified

def hex2rgb(h, alpha):
    # converts color value in hex format to rgba format with alpha transparency
    rgb = tuple([int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)] + [alpha])
    return 'rgba' + str(rgb)

def colors(slope, alpha):
    slope = round(slope)
    if slope < 0:
        colorcode = hex2rgb('#ffffff', 0)
    elif slope >= 20:
        colorcode =  hex2rgb('#000000', alpha)
    else:
        colorcode = cmap.get(str(slope), '#ffffff')
        colorcode = hex2rgb(colorcode, alpha)
    return colorcode

def hoverstring(dataframe, i):
    distanza = str(round(dataframe['distance'][i-1]/1000,1))+ ' km'
    quota = str(round(dataframe['elevation'][i-1]))+ ' m'
    lunghezza = str(round(dataframe['length'][i]/1000,1)) + ' km '
    pendenza = str(round(dataframe['slope'][i])) + '%'
    
    text = 'Distanza: ' + distanza + '<br>' + 'Quota: ' + quota + '<br>' + 'Lungehzza: ' + lunghezza + '<br>' + 'Pendenza: ' + pendenza
    return text

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

palette = 'GBVRB'

climb = 'sellaronda'

# Opening JSON file
with open('../data/colors/' + palette + '.json') as json_file:
    cmap = json.load(json_file)
    
GPXpath = '../data/' + climb + '.gpx'
data = gpx2df(GPXpath)
semplificato = semplifica_profilo(data, 20)

# -----------------------------------------------------------------------------
# PLOT
# -----------------------------------------------------------------------------
fig = go.Figure()
fig.layout.template = 'none'

# riempimento basato su valore pendenza
for i in range(1, len(semplificato)):
    df = semplificato.loc[i-1:i, :]
    fig.add_trace(go.Scatter(x=df['distance'],
                             y=df['elevation'], 
                             fill='tozeroy',
                             fillcolor=colors(slope = df['slope'][i],
                                              alpha = 0.5),
                             mode='lines',
                             line={'color': 'black'},
                             hovertext = hoverstring(df, i),
                             hoverinfo="text"))
    
# etichette luoghi
# fig.add_annotation(x=12100, y=2231,
#             text="Passo Pordoi <br> 2231m",
#             showarrow=False,
#             yshift=20)
# fig.add_annotation(x=25600, y=1880,
#             text="Passo Campolongo <br> 1880m",
#             showarrow=False,
#             yshift=20)
# fig.add_annotation(x=40200, y=2104,
#             text="Passo Gardena <br> 2104m",
#             showarrow=False,
#             yshift=20)
# fig.add_annotation(x=51400, y=2225,
#             text="Passo Sella <br> 2225m",
#             showarrow=False,
#             yshift=20)

# punto di massima pendenza
maxslope = dict(semplificato.iloc[semplificato['slope'].idxmax(), :])
fig.add_annotation(x=maxslope['distance'], y=maxslope['elevation'],
            text=str(round(maxslope['slope'])) + '%',
            showarrow=True,
            yshift=20,
            font=dict(color="#991212"))

# assi
ystart = round(semplificato['elevation'].min(), -2) - 100
yend = round(semplificato['elevation'].max(), -2) + 100
fig.update_xaxes(title_text='Distanza',
                 showline=True, linewidth=1,
                 tick0=0, dtick=1000, ticks="outside", tickformat = "%i")
fig.update_yaxes(title_text='Quota',
                 showline=True, linewidth=1,
                 tick0=100, dtick=100, ticks="outside",
                 range=[ystart, yend])

# hover 
fig.update_xaxes(showspikes=True, spikecolor="white", spikethickness=1)

fig.update_layout(
    hoverlabel=dict(
        bgcolor="white"),
    hoverdistance=1000)


# Titolo e legenda
fig.update_layout(title_text=climb,
                  showlegend=False)

fig.show()






