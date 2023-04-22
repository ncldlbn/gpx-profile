#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 10:51:30 2023

@author: nicola
"""

# esempio di codice Python che utilizza la libreria gpxpy per associare i 
# valori di quota da un DEM ai punti di un file GPX. Si presuppone di avere un 
# file GPX in cui sono presenti dei punti, e un file DEM con i valori di quota 
# per ogni punto:

import gpxpy
import rasterio

# Apri il file DEM
with rasterio.open('file_dem.tif') as src:
    # Prendi i metadati da src
    transform, width, height = src.transform, src.width, src.height
    # Prendi la bounding box del DEM
    bounds = src.bounds

# Apri il file GPX
with open('file_gpx.gpx', 'r') as f:
    gpx = gpxpy.parse(f)

# Per ogni punto nel file GPX, cerca il valore di quota corrispondente nel DEM
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            # Trova il valore di quota corrispondente al punto
            col, row = src.index(point.longitude, point.latitude)
            altitude = src.read(1, window=((row, row+1), (col, col+1)))
            # Aggiungi il valore di quota al punto del file GPX
            point.elevation = altitude

# Salva il file GPX con i valori di quota aggiornati
with open('file_gpx_with_elevations.gpx', 'w') as f:
    f.write(gpx.to_xml())