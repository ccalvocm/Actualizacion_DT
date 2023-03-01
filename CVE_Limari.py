# -*- coding: utf-8 -*-
"""
"""
import os
import pandas as pd
import modules_CCC
import matplotlib.pyplot as plt
import pathlib

os.chdir(r'E:\GitHub\Actualizacion_DT')
ruta_ip = pathlib.PurePath('inputs') # ruta inputs
ruta_op = pathlib.PurePath('outputs') # ruta outputs
# df con Estaciones
# df_estaciones=pd.read_excel(dicc_caudales[cuenca],sheet_name='Ficha_est')
df_cuenca=pd.read_pickle(ruta_ip.joinpath('qmon_MLR_DT-02_1950_2022.pkl')) # cargar dataframe estaciones rellenadas
df_cuenca = df_cuenca.reindex(columns=['04501001-5', '04522002-8', '04514001-6', '04513001-0', '04533002-8', '04557002-9'])
# metadata_cuenca=df_estaciones[(df_estaciones['Cuenca'].str.lower().str.contains('limar')) & (~df_estaciones['Cuenca'].str.lower().str.contains('costeras'))]
md_est = pd.read_pickle(ruta_ip.joinpath('md_est_DT02.pkl')) # cargar dataframe de metadata de todas las estaciones
metadata_cuenca=md_est[md_est['rut'].isin(df_cuenca.columns)].copy()
# df=pd.read_excel(dicc_caudales[cuenca],sheet_name='Data',index_col=0,parse_dates=True)
# df_cuenca=df[df.columns[df.columns.isin(list(metadata_cuenca['rut']))]]

# caudales=modules_CCC.CDA(df_cuenca)
caudales=df_cuenca

#---------------------------------1950-2000-----------------------------

caudales_nam=modules_CCC.get_names(caudales,metadata_cuenca[['Estacion','rut']])
plt.close('all')

# crear archivo para guardar estaciones
save_path=ruta_op.joinpath('CVE_1950-2000_caudales_Limari-DT02.xlsx')
writer=pd.ExcelWriter(save_path, engine='xlsxwriter')
cuenca = 'Limari'

for i in range(len(caudales_nam.columns)):
    q_nam = pd.DataFrame(caudales_nam.loc[(caudales_nam.index>='1950-04-01') & (caudales_nam.index<'2001-03-31')][caudales_nam.columns[i]])
    fig, axes=plt.subplots(2,1,figsize=(11, 17))
    axes=axes.reshape(-1)
    modules_CCC.CVE_mon(q_nam,fig,axes,2,q_nam.index.year[0],q_nam.index.year[-1],cuenca,writer)
    plt.show()
    
writer.save()
writer.close()

#---------------------------------1971-2021-----------------------------

caudales_nam=modules_CCC.get_names(caudales,metadata_cuenca[['Estacion','rut']])
plt.close('all')

# crear archivo para guardar estaciones
save_path=ruta_op.joinpath('CVE_1971-2021_caudales_Limari-DT02.xlsx')
writer=pd.ExcelWriter(save_path, engine='xlsxwriter')
cuenca = 'Limari'

for i in range(len(caudales_nam.columns)):
    q_nam = pd.DataFrame(caudales_nam.loc[(caudales_nam.index>='1971-04-01') & (caudales_nam.index<'2022-03-31')][caudales_nam.columns[i]])
    fig, axes=plt.subplots(2,1,figsize=(11, 17))
    axes=axes.reshape(-1)
    modules_CCC.CVE_mon(q_nam,fig,axes,2,q_nam.index.year[0],q_nam.index.year[-1],cuenca,writer)
    plt.show()
    
writer.save()
writer.close()

#---------------------------------1991-2021-----------------------------

caudales_nam=modules_CCC.get_names(caudales,metadata_cuenca[['Estacion','rut']])
plt.close('all')

# crear archivo para guardar estaciones
save_path=ruta_op.joinpath('CVE_1991-2021_caudales_Limari-DT02.xlsx')
writer=pd.ExcelWriter(save_path, engine='xlsxwriter')
cuenca = 'Limari'

for i in range(len(caudales_nam.columns)):
    q_nam = pd.DataFrame(caudales_nam.loc[(caudales_nam.index>='1991-04-01') & (caudales_nam.index<'2022-03-31')][caudales_nam.columns[i]])
    fig, axes=plt.subplots(2,1,figsize=(11, 17))
    axes=axes.reshape(-1)
    modules_CCC.CVE_mon(q_nam,fig,axes,2,q_nam.index.year[0],q_nam.index.year[-1],cuenca,writer)
    plt.show()
    
writer.save()
writer.close()     

#---------------------------------2006-2021-----------------------------

caudales_nam=modules_CCC.get_names(caudales,metadata_cuenca[['Estacion','rut']])
plt.close('all')

# crear archivo para guardar estaciones
save_path=ruta_op.joinpath('CVE_2006-2021_caudales_Limari-DT02.xlsx')
writer=pd.ExcelWriter(save_path, engine='xlsxwriter')
cuenca = 'Limari'

for i in range(len(caudales_nam.columns)):
    q_nam = pd.DataFrame(caudales_nam.loc[(caudales_nam.index>='2006-04-01') & (caudales_nam.index<'2022-03-31')][caudales_nam.columns[i]])
    fig, axes=plt.subplots(2,1,figsize=(11, 17))
    axes=axes.reshape(-1)
    modules_CCC.CVE_mon(q_nam,fig,axes,2,q_nam.index.year[0],q_nam.index.year[-1],cuenca,writer)
    plt.show()
    
writer.save()
writer.close()     