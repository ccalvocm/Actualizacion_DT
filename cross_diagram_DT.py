# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 12:42:05 2022

"""

from matplotlib import pyplot as plt
import os
import matplotlib
import datetime
import pandas as pd
import geopandas as gpd
import modules_FAA
import numpy as np
import pathlib

#%% compila bases de datos de registros de estaciones

ruta_Archivos = r'D:\Documentos\DT\Antecedentes\Caudales'

# lista de rutas a archivos de estaciones
list_arc_est = []

for path, subdirs, files in os.walk(ruta_Archivos):
    for name in files:
        if name.startswith("CaudalesDGAyMOP"): list_arc_est.append(pathlib.PurePath(path, name))

#dataframe de informacion de estaciones para shape
est = pd.DataFrame()
for fn in list_arc_est:
    est = pd.concat([est,pd.read_excel(fn, sheet_name = 'Datos', parse_dates=[0])], axis="columns")

est.iloc[0,0] = pd.Timestamp('1900-01-01') # corrige fecha de valor 0
aux = est.iloc[:,0] # extrae serie de tiempo
est.drop([est.columns[0]], axis=1, inplace = True) # elimina columna de fechas porque queda multidimensional y no permite reemplazarla
est =  est.set_index(aux) # convierte fechas a indice
est = est.loc[:,~est.columns.duplicated()].copy() # remover columnas duplicadas
est.to_pickle(r'D:\Documentos\DT\Scripts\dataframes\est_data.pkl') # guardar registros consolidados de estaciones
# est = pd.read_pickle(r'D:\Documentos\DT\Scripts\dataframes\est_data.pkl') # cargar dataframe de estaciones consolidados

gdf_DT02 = gpd.read_file(r'D:\Documentos\DT\SIG\Estaciones\Estaciones_DT_02_rut.shp')

list_DT02 = gdf_DT02['rut'].copy() # lista de estaciones DT02
list_DT02[74] = '07336001-3' # reemplaza rut de estacion Rio Niblinto duplicada por Rio Cauquenes en el Arrayan
est_DT02 = est.reindex(columns=gdf_DT02['rut']) # se seleccionan solo los registros de estaciones DT02
est_DT02.to_pickle(r'D:\Documentos\DT\Scripts\dataframes\est_DT02.pkl') # guardar dataframe de estaciones DT02

#%% diagrama de cruces estaciones DT-02
est_DT02 = pd.read_pickle(r'D:\Documentos\DT\Scripts\dataframes\est_DT02.pkl') # cargar dataframe de estaciones DT02
aux = est_DT02.index # extrae fechas Timestamp
aux = aux.to_pydatetime() # convierte fechas Timestamp a datetime
est_DT02 =  est_DT02.set_index(aux) # convierte fechas datetime a indice

fig = plt.figure(figsize=(11, 17))
axes = fig.add_subplot(111)
modules_FAA.plot_diagrama_cruces(est_DT02.iloc[:,0:62],1970,2023, ax = axes)
plt.savefig(r'D:\Documentos\DT\Antecedentes\Caudales\diagrama_cruces_DT02_p1.svg', bbox_inches='tight', dpi = 300)

fig = plt.figure(figsize=(11, 17))
axes = fig.add_subplot(111)
modules_FAA.plot_diagrama_cruces(est_DT02.iloc[:,62:125],1970,2023, ax = axes)
plt.savefig(r'D:\Documentos\DT\Antecedentes\Caudales\diagrama_cruces_DT02_p2.svg', bbox_inches='tight', dpi = 300)

#%% diagrama de cruces estaciones interes limari
lista_limari = ['04532001-4', '04534001-5', '04533002-8', '04520001-9', '04522001-K', '04530001-3', 
                '04531001-9', '04531002-7', '04514001-6', '04515002-K', '04535002-9', '04535003-7',
                '04537001-1', '04506002-0', '04506003-9', '04550003-9', '04540003-4', '04501001-5',
                '04501002-3', '04502001-0', '04503001-6', '04516001-7', '04523001-5', '04522002-8',
                '04523002-3', '04540001-8', '04556001-5', '04557002-9', '04558001-6', '04511002-8',
                '04512001-5', '04513001-0']
est = pd.read_pickle(r'D:\Documentos\DT\Scripts\dataframes\est_data.pkl') # cargar dataframe de estaciones consolidados
est_limari = est.reindex(columns=lista_limari) # se seleccionan solo los registros de estaciones limari

fig = plt.figure(figsize=(11, 17))
axes = fig.add_subplot(111)
modules_FAA.plot_diagrama_cruces(est_limari,1970,2023, ax = axes)
plt.savefig(r'D:\Documentos\DT\Antecedentes\Caudales\diagrama_cruces_limari.svg', bbox_inches='tight', dpi = 300)

list_bad = ['04534001-5', '04522001-K', '04531001-9', '04535002-9', '04535003-7', '04506002-0',
            '04550003-9', '04540003-4', '04501002-3', '04502001-0', '04516001-7', '04523001-5',
            '04540001-8', '04556001-5'] # estaciones con pocos datos
list_good = [x for x in lista_limari if x not in list_bad] # estaciones con datos abundantes

est_lim_good = est_limari.reindex(columns=list_good) # se seleccionan solo los registros de estaciones DT02
fig = plt.figure(figsize=(11, 17))
axes = fig.add_subplot(111)
modules_FAA.plot_diagrama_cruces(est_lim_good,1970,2023, ax = axes)
plt.savefig(r'D:\Documentos\DT\Antecedentes\Caudales\diagrama_cruces_lim_good.svg', bbox_inches='tight', dpi = 300)

est_mdata = pd.read_pickle(r'D:\Documentos\DT\Scripts\dataframes\estaciones.pkl')
est_bad = est_mdata[est_mdata['rut'].isin(list_bad)].copy() # metadata estaciones con pocos datos
est_good = est_mdata[est_mdata['rut'].isin(list_good)].copy() # metadata estaciones con abundantes datos

# geodataframe y shape de estaciones
gdf_est_good = gpd.GeoDataFrame(est_good, geometry=gpd.points_from_xy(x=est_good['Lon'], y=est_good['Lat']))
gdf_est_good.set_crs(epsg=4326, inplace= True)
gdf_est_good.to_crs(epsg=32719, inplace=True)
gdf_est_good.to_file(r'D:\Documentos\DT\SIG\Estaciones\est_limari_good.shp') # guardar shape de estaciones con datos

gdf_est_bad = gpd.GeoDataFrame(est_bad, geometry=gpd.points_from_xy(x=est_bad['Lon'], y=est_bad['Lat']))
gdf_est_bad.set_crs(epsg=4326, inplace= True)
gdf_est_bad.to_crs(epsg=32719, inplace=True)
gdf_est_bad.to_file(r'D:\Documentos\DT\SIG\Estaciones\est_limari_bad.shp') # guardar shape de estaciones con datos

#%% diagrama de cruces faltantes MOP
q_MOP_f = pd.read_pickle(r'D:\Documentos\DT\Scripts\dataframes\q_MOP_falt.pkl') # cargar dataframe de estaciones faltantes MOP
q_MOP_f.index = pd.to_datetime(q_MOP_f.index)

fig = plt.figure(figsize=(11, 17))
axes = fig.add_subplot(111)
modules_FAA.plot_diagrama_cruces(q_MOP_f,1970,2023, ax = axes)
plt.savefig(r'D:\Documentos\DT\Antecedentes\Caudales\diagrama_MOP_f.svg', bbox_inches='tight', dpi = 300)

lista_MOP_util = ['04302001-3','04306001-5','04308001-6','08123002-1','08318001-3','08386001-4','08530001-6','11020005-6']
fig = plt.figure(figsize=(11, 3))
axes = fig.add_subplot(111)
modules_FAA.plot_diagrama_cruces(q_MOP_f[lista_MOP_util],1970,2023, ax = axes)
plt.savefig(r'D:\Documentos\DT\Antecedentes\Caudales\diagrama_cruces_MOP_f_util.svg', bbox_inches='tight', dpi = 300)
 #%%
# 
path = r'D:\Documentos\DT\Antecedentes\Caudales\METROPOLITANA\CaudalesDGAyMOP_Metropolitana_2022_revA.xlsx'
   

df_all = pd.read_excel(path, sheet_name = 'Datos')
df_all.iloc[0,0] = datetime.datetime(1900, 1, 1, 0, 0)
df_all =  df_all.set_index(df_all.columns[0]) # convierte fechas a indice (DGA)
df_all.index.name = None # remueve Unnamed: 0
fig = plt.figure(figsize=(11, 17))
axes = fig.add_subplot(111)
modules_FAA.plot_diagrama_cruces(df_all,1970,2023, ax = axes)
plt.savefig( r'D:\Documentos\DT\Antecedentes\Caudales\METROPOLITANA\diagrama_cruces_DGAyMOP_Metro.svg', bbox_inches='tight', dpi = 300)
