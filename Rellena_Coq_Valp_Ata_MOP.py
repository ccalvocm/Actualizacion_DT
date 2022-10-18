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

#%% Rellena estaciones de Coquimbo, Valparaiso y Atacama con registros MOP adicionales previos a 1972

root='.'

ruta_Archivos=pathlib.PurePath(root,'..','Antecedentes','Caudales')

list_DGA = [] # lista de rutas de archivos de registros DGA completados con MOP desde 1972

for path, subdirs, files in os.walk(ruta_Archivos):
    for name in files:
        if name.startswith("CaudalesDGAyMOP_") and ('Atacama' in name or 'Valpara' in name or 'Coquimbo' in name) and name.endswith("revA.xlsx"):
            list_DGA.append(pathlib.PurePath(path, name))

# lista de rutas de archivos de registros MOP con registros previos a 1972
list_MOP =[pathlib.PurePath(root,'..','Scripts','inputs','q_flags_atacama.xlsx'),
           pathlib.PurePath(root,'..','Scripts','inputs','CaudalesDGA_Coquimbo_diarios_2021.xlsx'),
           pathlib.PurePath(root,'..','Scripts','inputs','q_flags_valparaiso.xlsx')]

for fnD, fnM  in zip(list_DGA, list_MOP): # itera entre los pares de nombres de archivo DGA-MOP
    md_DGA =  pd.read_excel(fnD, sheet_name = 'Ficha_est', index_col=0) # carga metadata estaciones DGA
    f_DGA =  pd.read_excel(fnD, sheet_name = 'Flags') # carga flags registros DGA
    f_DGA.iloc[0,0] = pd.Timestamp('1900-01-01 00:00:00') # corrige valor 0 de fecha
    f_DGA =  f_DGA.set_index(f_DGA.columns[0]) # convierte fechas a indice (DGA)
    f_DGA.index.name = None # remueve Unnamed: 0
    
    q_DGA =  pd.read_excel(fnD, sheet_name = 'Datos', parse_dates=[0]) # carga registros de estaciones DGA
    q_DGA.iloc[0,0] = pd.Timestamp('1900-01-01 00:00:00') # corrige valor 0 de fecha
    q_DGA =  q_DGA.set_index(q_DGA.columns[0]) # convierte fechas a indice (DGA)
    q_DGA.index.name = None # remueve Unnamed: 0 
    
    if 'Coquimbo' in fnD.name:
        md_MOP =  pd.read_excel(fnM, sheet_name = 'Ficha_est', index_col=0) # carga metadata de estaciones MOP
        md_DGA = pd.concat([md_DGA, md_MOP.loc[~md_MOP['rut'].isin(md_DGA['rut'])]], ignore_index=True) # agrega metadata de estaciones faltantes a ficha
        md_DGA.index += 1 # hace que indice parta desde 1  
        
        q_MOP = pd.read_excel(fnM, sheet_name = 'Datos', parse_dates=[0]) # carga registros de estaciones Coquimbo MOP
        q_MOP.iloc[0,0] = pd.Timestamp('1900-01-01 00:00:00') # corrige valor 0 de fecha
        q_MOP =  q_MOP.set_index(q_MOP.columns[0]) # convierte fechas a indice
        q_MOP.index.name = None # remueve Unnamed: 0 
        
        parent, name = fnM.parent, fnM.name # obtiene carpeta y nombre de archivo de registros MOP
        flag_fn = name.replace('Caudales', 'Flags') # crea nombre de archivo de flags de estaciones MOP Coquimbo
        fnM_flag = pathlib.Path(parent).joinpath(flag_fn) # crea ruta de archivo de flags  MOP Coquimbo
        f_MOP = pd.read_excel(fnM_flag, sheet_name = 'Sheet1', parse_dates=[0]) # carga flags registros MOP
        f_MOP =  f_MOP.set_index(f_MOP.columns[0]) # convierte fechas a indice
        f_MOP.index.name = None # remueve Unnamed: 0 
        
    else:            
        f_MOP =  pd.read_excel(fnM, sheet_name = 'Flags', parse_dates=[0]) # carga flags registros MOP
        f_MOP =  f_MOP.set_index(f_MOP.columns[0]) # convierte fechas a indice
        f_MOP.index.name = None # remueve Unnamed: 0 
        q_MOP =  pd.read_excel(fnM, sheet_name = 'Data', parse_dates=[0]) # carga registros de estaciones MOP
        q_MOP =  q_MOP.set_index(q_MOP.columns[0]) # convierte fechas a indice
        q_MOP.index.name = None # remueve Unnamed: 0 


    q_DGAyMOP = merge_dfs(q_DGA,q_MOP) # reemplaza valores NaN de los registros DGA con valores no NaN de los registros MOP correspondientes al dia y agrega estaciones faltantes 

    f_DGAyMOP = merge_dfs(f_DGA,f_MOP) # agrega flags de los registros MOP correspondientes

    parent, name = fnD.parent, fnD.name # obtiene carpeta y nombre de archivo de registros DGA
    proc_fn = name.replace('revA', 'revB') # crea nombre de archivo de registros de estaciones completadas con MOP
    fn_DGAyMOP = pathlib.Path(parent).joinpath(proc_fn) # crea ruta de archivo
    
    writer = pd.ExcelWriter(fn_DGAyMOP, engine='xlsxwriter') # 
    md_DGA.to_excel(writer, sheet_name='Ficha_est')
    q_DGAyMOP.to_excel(writer, sheet_name='Datos')
    f_DGAyMOP.to_excel(writer, sheet_name='Flags')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    writer.close()
    
#%% Rellena demas estaciones de con registros previos a 1972

root='.'

ruta_Archivos=pathlib.PurePath(root,'..','Antecedentes','Caudales')

list_DGA = [] # lista de rutas de archivos de registros DGA completados con MOP desde 1972

for path, subdirs, files in os.walk(ruta_Archivos): #se excluyen regiones ya procesadas
    for name in files:
        if name.startswith("CaudalesDGAyMOP_") and  'Atacama' not in name and 'Valpara' not in name and 'Coquimbo' not in name and name.endswith("revA.xlsx"):
            list_DGA.append(pathlib.PurePath(path, name))

# lista de rutas de archivos de registros MOP con registros previos a 1972
ruta_72 = pathlib.PurePath(root,'..','Scripts','inputs','q_Chile_1972.xlsx')

list_MOP =[pathlib.PurePath(root,'..','Scripts','inputs','q_flags_atacama.xlsx'),
           pathlib.PurePath(root,'..','Scripts','inputs','CaudalesDGA_Coquimbo_diarios_2021.xlsx'),
           pathlib.PurePath(root,'..','Scripts','inputs','q_flags_valparaiso.xlsx')]

for fnD, fnM  in zip(list_DGA, list_MOP): # itera entre los pares de nombres de archivo DGA-MOP
    md_DGA =  pd.read_excel(fnD, sheet_name = 'Ficha_est', index_col=0) # carga metadata estaciones DGA
    f_DGA =  pd.read_excel(fnD, sheet_name = 'Flags') # carga flags registros DGA
    f_DGA.iloc[0,0] = pd.Timestamp('1900-01-01 00:00:00') # corrige valor 0 de fecha
    f_DGA =  f_DGA.set_index(f_DGA.columns[0]) # convierte fechas a indice (DGA)
    f_DGA.index.name = None # remueve Unnamed: 0
    
    q_DGA =  pd.read_excel(fnD, sheet_name = 'Datos', parse_dates=[0]) # carga registros de estaciones DGA
    q_DGA.iloc[0,0] = pd.Timestamp('1900-01-01 00:00:00') # corrige valor 0 de fecha
    q_DGA =  q_DGA.set_index(q_DGA.columns[0]) # convierte fechas a indice (DGA)
    q_DGA.index.name = None # remueve Unnamed: 0 
    
    if 'Coquimbo' in fnD.name:
        md_MOP =  pd.read_excel(fnM, sheet_name = 'Ficha_est', index_col=0) # carga metadata de estaciones MOP
        md_DGA = pd.concat([md_DGA, md_MOP.loc[~md_MOP['rut'].isin(md_DGA['rut'])]], ignore_index=True) # agrega metadata de estaciones faltantes a ficha
        md_DGA.index += 1 # hace que indice parta desde 1  
        
        q_MOP = pd.read_excel(fnM, sheet_name = 'Datos', parse_dates=[0]) # carga registros de estaciones Coquimbo MOP
        q_MOP.iloc[0,0] = pd.Timestamp('1900-01-01 00:00:00') # corrige valor 0 de fecha
        q_MOP =  q_MOP.set_index(q_MOP.columns[0]) # convierte fechas a indice
        q_MOP.index.name = None # remueve Unnamed: 0 
        
        parent, name = fnM.parent, fnM.name # obtiene carpeta y nombre de archivo de registros MOP
        flag_fn = name.replace('Caudales', 'Flags') # crea nombre de archivo de flags de estaciones MOP Coquimbo
        fnM_flag = pathlib.Path(parent).joinpath(flag_fn) # crea ruta de archivo de flags  MOP Coquimbo
        f_MOP = pd.read_excel(fnM_flag, sheet_name = 'Sheet1', parse_dates=[0]) # carga flags registros MOP
        f_MOP =  f_MOP.set_index(f_MOP.columns[0]) # convierte fechas a indice
        f_MOP.index.name = None # remueve Unnamed: 0 
        
    else:            
        f_MOP =  pd.read_excel(fnM, sheet_name = 'Flags', parse_dates=[0]) # carga flags registros MOP
        f_MOP =  f_MOP.set_index(f_MOP.columns[0]) # convierte fechas a indice
        f_MOP.index.name = None # remueve Unnamed: 0 
        q_MOP =  pd.read_excel(fnM, sheet_name = 'Data', parse_dates=[0]) # carga registros de estaciones MOP
        q_MOP =  q_MOP.set_index(q_MOP.columns[0]) # convierte fechas a indice
        q_MOP.index.name = None # remueve Unnamed: 0 


    q_DGAyMOP = merge_dfs(q_DGA,q_MOP) # reemplaza valores NaN de los registros DGA con valores no NaN de los registros MOP correspondientes al dia y agrega estaciones faltantes 

    f_DGAyMOP = merge_dfs(f_DGA,f_MOP) # agrega flags de los registros MOP correspondientes

    parent, name = fnD.parent, fnD.name # obtiene carpeta y nombre de archivo de registros DGA
    proc_fn = name.replace('revA', 'revB') # crea nombre de archivo de registros de estaciones completadas con MOP
    fn_DGAyMOP = pathlib.Path(parent).joinpath(proc_fn) # crea ruta de archivo
    
    writer = pd.ExcelWriter(fn_DGAyMOP, engine='xlsxwriter') # 
    md_DGA.to_excel(writer, sheet_name='Ficha_est')
    q_DGAyMOP.to_excel(writer, sheet_name='Datos')
    f_DGAyMOP.to_excel(writer, sheet_name='Flags')

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    writer.close()