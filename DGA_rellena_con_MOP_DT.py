# -*- coding: utf-8 -*-
"""
"""

import pandas as pd
import geopandas as gpd
import os
import datetime
import calendar
import datetime
import time
import re
import calendar
from functools import reduce
import gc
import numpy as np
import pathlib

#%% define funciones
def dms2dd(degrees, minutes, seconds, direction):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    if direction == 'E' or direction == 'S':
        dd *= -1
    return dd;

def parse_dms(dms):
    parts = re.split('[^\d\w]+', dms)
    lat = dms2dd(parts[0], parts[1], parts[2], parts[3])
    return -(lat)

def merge_dfs(df1,df2):
    min_date=min(df1.index[0],df2.index[0])
    max_date=max(df1.index[-1],df2.index[-1])
    idx=pd.date_range(min_date,max_date,freq='1d')
    cols=list(df1.columns)+[x for x in df2.columns if x not in df1.columns]
    df_merged=pd.DataFrame(index=idx,columns=cols)
    
    for col in df1.columns:
        col_nna=df1[col][df1[col].notna()]
        df_merged.loc[col_nna.index,col]=col_nna.values
        
    for col in df2.columns:
        col_nna=df2[col][df2[col].notna()]
        df_merged.loc[col_nna.index,col]=col_nna.values
    
    return df_merged

#%% Revisar y Rellenar registros de estaciones DGA con registros MOP

# rutas
# os.chdir(r'C:\Users\andre\OneDrive - ciren.cl\2022_CNR_Actualizacion_DT\Scripts')
root=pathlib.PurePath()

ruta_Archivos=pathlib.PurePath(root,'..','Antecedentes','Caudales')
ruta_MOP=pathlib.PurePath(root,'..','Scripts','outputs','qmean_MOP_1972_2022.xlsx')
ruta_fal=pathlib.PurePath(root,'..','Antecedentes','Caudales','metadata_est_MOP_faltantes_en_DGA_v2.xlsx') # ruta metadata de estaciones faltantes MOP en registros DGA
# ruta_Archivos=join_path(root,'..','Antecedentes','Caudales')
list_arc_est = [] # lista de reutas de archivos de registros DGA

for path, subdirs, files in os.walk(ruta_Archivos):
    for name in files:
        if name.startswith("CaudalesDGA_"): list_arc_est.append(pathlib.PurePath(path, name))

# carga archivos MOP
f_MOP =  pd.read_excel(ruta_MOP, sheet_name = 'Flags', parse_dates=[0]) # flags MOP
f_MOP =  f_MOP.set_index(f_MOP.columns[0]) # convierte fechas a indice
f_MOP.index.name = None # remueve Unnamed: 0

q_MOP =  pd.read_excel(ruta_MOP, sheet_name = 'Datos', parse_dates=[0]) # caudales MOP
q_MOP =  q_MOP.set_index(q_MOP.columns[0]) # convierte fechas a indice
q_MOP.index.name = None # remueve Unnamed: 0

md_MOP_f =  pd.read_excel(ruta_fal, sheet_name = 'Ficha_est', index_col=0) # carga metadata de estaciones faltantes MOP

# completa registros DGA con MOP y guarda archivos
for fn in list_arc_est:
    md_DGA =  pd.read_excel(fn, sheet_name = 'Ficha_est', index_col=0) # carga metadata estaciones DGA
    f_DGA =  pd.read_excel(fn, sheet_name = 'Flags') # carga flags registros DGA
    f_DGA.iloc[0,0] = pd.Timestamp('1900-01-01 00:00:00') # corrige valor 0 de fecha
    f_DGA =  f_DGA.set_index(f_DGA.columns[0]) # convierte fechas a indice (DGA)
    f_DGA.index.name = None # remueve Unnamed: 0
    
    q_DGA =  pd.read_excel(fn, sheet_name = 'Datos', parse_dates=[0]) # carga registros de estaciones DGA
    q_DGA.iloc[0,0] = pd.Timestamp('1900-01-01 00:00:00') # corrige valor 0 de fecha
    q_DGA =  q_DGA.set_index(q_DGA.columns[0]) # convierte fechas a indice (DGA)
    q_DGA.index.name = None # remueve Unnamed: 0 
  
    if 'Coquimbo' in fn.__str__(): # agrega estaciones MOP faltantes en Coquimbo
        est = list(q_DGA.columns) + list(md_MOP_f.loc[md_MOP_f['REGION'] == 'Coquimbo', 'rut']) # lista de estaciones de la region incluyendo FALTANTES
        #q_DGAyMOP = q_DGA.reindex(columns = list(q_DGA.columns) + list(md_MOP_f.loc[md_MOP_f['REGION'] == 'Coquimbo', 'rut'])) # se crean columnas de las estaciones FALTANTES
        md_DGA = pd.concat([md_DGA, md_MOP_f.loc[md_MOP_f['REGION'] == 'Coquimbo', md_MOP_f.columns != 'REGION']], ignore_index=True) # agrega metadata de estaciones faltantes a ficha
        md_DGA.index += 1 # hace que indice parta desde 1             
    elif 'BioBio' in fn.__str__(): # agrega estaciones MOP faltantes en Bio-Bio
        est = list(q_DGA.columns) + list(md_MOP_f.loc[md_MOP_f['REGION'] == 'Biobío', 'rut']) # lista de estaciones de la region incluyendo FALTANTES
        #q_DGAyMOP = q_DGA.reindex(columns = list(q_DGA.columns) + list(md_MOP_f.loc[md_MOP_f['REGION'] == 'Biobío', 'rut'])) # se crean columnas de las estaciones FALTANTES
        md_DGA = pd.concat([md_DGA, md_MOP_f.loc[md_MOP_f['REGION'] == 'Biobío', md_MOP_f.columns != 'REGION']], ignore_index=True) # agrega metadata de estaciones faltantes a ficha
        md_DGA.index += 1 # hace que indice parta desde 1 
    elif 'Los_Lagos' in fn.__str__(): # agrega estaciones MOP faltantes en Bio-Bio
        est = list(q_DGA.columns) + list(md_MOP_f.loc[md_MOP_f['REGION'] == 'Los Lagos', 'rut']) # lista de estaciones de la region incluyendo FALTANTES
        #q_DGAyMOP = q_DGA.reindex(columns = list(q_DGA.columns) + list(md_MOP_f.loc[md_MOP_f['REGION'] == 'Los Lagos', 'rut'])) # se crean columnas de las estaciones FALTANTES
        md_DGA = pd.concat([md_DGA, md_MOP_f.loc[md_MOP_f['REGION'] == 'Los Lagos', md_MOP_f.columns != 'REGION']], ignore_index=True) # agrega metadata de estaciones faltantes a ficha
        md_DGA.index += 1 # hace que indice parta desde 1 
    else :
        est = q_DGA.columns # lista de estaciones de la region
        #q_DGAyMOP = q_DGA.copy()
    
    q_DGAyMOP = merge_dfs(q_DGA,q_MOP.reindex(columns=est)) # reemplaza valores NaN de los registros DGA con valores no NaN de los registros MOP correspondientes al dia y agrega estaciones faltantes 

    f_DGAyMOP = merge_dfs(f_DGA,f_MOP.reindex(columns=est)) # agrega flags de los registros MOP correspondientes

    parent, name = fn.parent, fn.name # obtiene carpeta y nombre de archivo de registros DGA
    proc_fn = name.replace('CaudalesDGA_', 'CaudalesDGAyMOP_') # crea nombre de archivo de registros de estaciones completadas con MOP
    fn_DGAyMOP = pathlib.Path(parent).joinpath(proc_fn) # crea ruta de archivo
    
    writer = pd.ExcelWriter(fn_DGAyMOP, engine='xlsxwriter') # 
    md_DGA.to_excel(writer, sheet_name='Ficha_est')
    q_DGAyMOP.to_excel(writer, sheet_name='Datos')
    f_DGAyMOP.to_excel(writer, sheet_name='Flags')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    writer.close()
