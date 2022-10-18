# -*- coding: utf-8 -*-
"""
"""

import pandas as pd
import os
import numpy as np
import pathlib

#%% define funciones
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

#%% Rellena demas estaciones de con registros previos a 1972

root='.'

ruta_Archivos=pathlib.PurePath(root,'..','Antecedentes','Caudales')

list_DGA = [] # lista de rutas de archivos de registros DGA completados con MOP desde 1972

for path, subdirs, files in os.walk(ruta_Archivos):
    for name in files:
        if name.startswith("CaudalesDGAyMOP_")  and name.endswith("revA.xlsx"):
            list_DGA.append(pathlib.PurePath(path, name))

# lista de rutas de archivo de con registros previos a 1972
ruta_72 = pathlib.PurePath(root,'..','Scripts','inputs','q_Chile_1972.xlsx')
q_72 =  pd.read_excel(ruta_72, sheet_name = 'Sheet1', parse_dates=[0]) # carga registros de estaciones previos a 1972
q_72 =  q_72.set_index(q_72.columns[0]) # convierte fechas a indice (DGA)
q_72.index.name = None # remueve Unnamed: 0


for fnD in list_DGA: # itera entre los archivos de cada region
    md_DGA =  pd.read_excel(fnD, sheet_name = 'Ficha_est', index_col=0) # carga metadata estaciones DGA
    f_DGA =  pd.read_excel(fnD, sheet_name = 'Flags') # carga flags registros DGA
    f_DGA.iloc[0,0] = pd.Timestamp('1900-01-01 00:00:00') # corrige valor 0 de fecha
    f_DGA =  f_DGA.set_index(f_DGA.columns[0]) # convierte fechas a indice (DGA)
    f_DGA.index.name = None # remueve Unnamed: 0
    
    q_DGA =  pd.read_excel(fnD, sheet_name = 'Datos', parse_dates=[0]) # carga registros de estaciones DGA
    q_DGA.iloc[0,0] = pd.Timestamp('1900-01-01 00:00:00') # corrige valor 0 de fecha
    q_DGA =  q_DGA.set_index(q_DGA.columns[0]) # convierte fechas a indice (DGA)
    q_DGA.index.name = None # remueve Unnamed: 0 

    q_ext = merge_dfs(q_DGA,q_72.reindex(columns=q_DGA.columns)) # reemplaza valores NaN de los registros DGA con valores no NaN de los registros previos a 1972

    parent, name = fnD.parent, fnD.name # obtiene carpeta y nombre de archivo de registros DGA
    proc_fn = name.replace('revA', 'revB') # crea nombre de archivo de registros de estaciones extendidas previo a 1972
    fn_ext = pathlib.Path(parent).joinpath(proc_fn) # crea ruta de archivo
    
    writer = pd.ExcelWriter(fn_ext, engine='xlsxwriter') 
    md_DGA.to_excel(writer, sheet_name='Ficha_est')
    q_ext.to_excel(writer, sheet_name='Datos')
    f_DGA.to_excel(writer, sheet_name='Flags')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    writer.close()