# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 11:48:59 2022

@author: ccalvo
"""

import os
import pandas as pd
import modules_CCC
import matplotlib.pyplot as plt
import pathlib

 
# diccionario de caudales en cada caso
dicc_caudales={'DT-02':os.path.join('.','outputs','q_relleno_DT-02_1950-2022_monthly.xlsx')}

# df con Estaciones
# df_estaciones=pd.read_excel(dicc_caudales[cuenca],sheet_name='Ficha_est')
df_cuenca=pd.read_pickle(r'D:\Documentos\DT\Scripts\dataframes\qmon_MLR_DT-02_1950_2022.pkl') # cargar dataframe estaciones rellenadas
# metadata_cuenca=df_estaciones[(df_estaciones['Cuenca'].str.lower().str.contains('limar')) & (~df_estaciones['Cuenca'].str.lower().str.contains('costeras'))]
metadata_cuenca=pd.read_pickle(r'D:\Documentos\DT\Scripts\dataframes\md_est_DT02.pkl') # cargar metadata de estaciones
# df=pd.read_excel(dicc_caudales[cuenca],sheet_name='Data',index_col=0,parse_dates=True)
# df_cuenca=df[df.columns[df.columns.isin(list(metadata_cuenca['rut']))]]

# caudales=modules_CCC.CDA(df_cuenca)
caudales=df_cuenca

# graciar hidrogramas
caudales_nam=modules_CCC.get_names(caudales,metadata_cuenca[['Estacion',
                                                           'rut']])
caudales_nam=caudales_nam.loc[caudales_nam.index<='2000-03-01']
plt.close('all')

# crear archivo para guardar estaciones
save_path=os.path.join('.','outputs','CVE_1950-2000_caudales_DT-02.xlsx')
writer=pd.ExcelWriter(save_path, engine='xlsxwriter')
cuenca = 'DT-02'


for i in range(2,len(caudales_nam.columns)+2,2):
    # # caudales medios anuales
    modules_CCC.CMA(caudales_nam.iloc[:,i-2:i], 10 ,22, 2, 1, cuenca)
    plt.show()
    
    # # # curvas de duración de caudales
    fig, axes=plt.subplots(2,2,figsize=(10, 22))
    modules_CCC.CDQ(caudales_nam.iloc[:,i-4:i], 4, fig,  axes)
    
    # # curvas de variación estacional
    fig, axes=plt.subplots(2,1,figsize=(11, 17))
    axes=axes.reshape(-1)
    modules_CCC.CVE_mon(caudales_nam.iloc[:,i-2:i],fig,axes,2, 
caudales_nam.index.year[0],caudales_nam.index.year[-1],cuenca,writer)
    plt.show()

    # anomalias
    # fig, axes=plt.subplots(2,2,figsize=(10, 22))
    # axes=axes.reshape(-1)
    # modules_CCC.ANOM(caudales_nam.iloc[:,i-4:i], 20, 11, 0.72, 0.02, 110, 'MS', fig, axes)
    
writer.save()
writer.close()         

