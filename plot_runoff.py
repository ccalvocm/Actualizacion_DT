# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 11:48:59 2022

@author: ccalvo
"""

import os
import pandas as pd
import modules_CCC
import matplotlib.pyploy as plt

# =======================================     
def runoff(cuenca):
# ----------------------------------------
# Esta función grafica las CVE, CD y CMA
# de cada cuenca
    
    # diccionario de caudales en cada caso
    dicc_caudales={
'Nuble':[os.path.join('.','outputs','q_relleno_Nuble_1987-2022_monthly.csv'),
os.path.join('.','outputs','Metadata_Q_Nuble.csv')]}

    # df con Estaciones
    df_estaciones=pd.read_csv(dicc_caudales[cuenca][1])
    
    caudales=modules_CCC.CDA(dicc_caudales[cuenca][0])
    df=df_estaciones[df_estaciones['rut'].isin(caudales.columns)]
    # geo_df=gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df['Lon'],
    #                                                        df['Lat']))
    # geo_df=geo_df.set_crs(epsg=4326)
    
    # graciar hidrogramas
    caudales_nam=modules_CCC.get_names(caudales,df_estaciones[['Estacion',
                                                               'rut']])
    caudales_nam.columns=caudales_nam.columns
    caudales_nam.columns=[x.replace('Rio','Río').replace('_',' ').replace('DGA','').replace('nn','ñ').title() for x in caudales_nam.columns]
        
    for i in range(4,len(caudales_nam.columns)+4,4):
        # caudales medios anuales
        modules_CCC.CMA(caudales_nam.iloc[:,i-2:i], 10 ,22, 2, 1)
        
        # # curvas de duración de caudales
        fig, axes=plt.subplots(2,2,figsize=(10, 22))
        modules_CCC.CDQ(caudales_nam.iloc[:,i-4:i], 4, fig,  axes)
        
        # # curvas de variación estacional
        fig, axes=plt.subplots(2,2,figsize=(11, 17))
        axes=axes.reshape(-1)
        modules_CCC.CVE_mon(caudales_nam.iloc[:,i-4:i],fig,axes,4, 
caudales_nam.index.year[0],caudales_nam.index.year[-1])

        # anomalias
        fig, axes=plt.subplots(2,2,figsize=(10, 22))
        axes=axes.reshape(-1)
        modules_CCC.ANOM(caudales_nam.iloc[:,i-4:i], 20, 11, 0.72, 0.02, 110, 'MS', fig, axes)
            