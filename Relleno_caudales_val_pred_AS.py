# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.

Author: CCCM

"""

#%% Dependencias

import pandas as pd
import numpy as np
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from itertools import cycle
import geopandas as gpd
import os
import re
import matplotlib.pyplot as plt
import datetime
import pathlib
#Funciones

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

def mejoresCorrelaciones(df, col, Nestaciones):
    ordenados = df.copy().sort_values(by=col, ascending = False)
    # coef. correlacion pearson 0.5
    ordenados = ordenados[ordenados[col] >= 0.75]
    return ordenados.index[:]

def parse_digito_verificador(lista):
    list_return=[]
    for rut in lista:
        rut=str(rut)
        if len(rut)<=7:
            rut='0'+rut
        digito_ver=digito_verificador(rut)
        list_return.append(str(rut)+'-'+str(digito_ver))
    return list_return

# Función rut
def digito_verificador(rut):
    reversed_digits = map(int, reversed(str(rut)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    if (-s) % 11 > 9:
        return 'K'
    else:
        return (-s) % 11

def extenderQ(dfDGA, dfCR2bueno):
    
    dfDGA_aux = dfDGA.copy()
    dfDGA_aux = dfDGA_aux.loc[dfDGA_aux.index <= '01-01-2008']
    
    for columna in dfDGA.columns:
        missing_DGA = dfDGA_aux[columna][dfDGA_aux[columna].isna()]
        dfDGA.loc[missing_DGA.index,columna] = dfCR2bueno.loc[missing_DGA.index,
                                                              columna]
    return dfDGA

# ================================
#     Encontrar puntos cercanos 
# ================================
    
def min_dist(point, gpd2, n_multivariables):
    gpd2['Dist'] = gpd2.apply(lambda row:  point.distance(row.geometry),axis=1)
    gpd2=gpd2[gpd2['Dist']<=5.3e4]
    return gpd2.sort_values(by=['Dist']).loc[gpd2.sort_values(by=['Dist']).index[0:n_multivariables],
                                             gpd2.columns]
# ordenar datos DGA
def ordenarDGA(df,df_DGA):
    """
    

    Parameters
    ----------
    df : Pandas DataFrame
        dataframe de los datos del BNA.
    df_DGA : str
        estacion a ordenar.

    Returns
    -------
    output : TYPE
        DESCRIPTION.

    """
    output = pd.DataFrame([], index = pd.date_range(start='1980-01-01',
end='2020-12-31', closed=None))

    for ind, est in enumerate(df):
        q_est = df_DGA[df_DGA.iloc[:,0] == df[ind]]
        fechas = pd.to_datetime(q_est.iloc[:,2], dayfirst = True)
        caudal = q_est.iloc[:,3]
        flags = q_est.iloc[:,4]
        
        q_est_df = pd.DataFrame(caudal.values, index = fechas, columns = [est])
        flags_est=pd.DataFrame(flags.values,index=fechas,columns=['flags'])
            
        output.loc[output.index,est] = q_est_df[est]
        output.loc[output.index,'flag'] = flags_est['flags']

    return output

def join_path(*args):
    string=os.path.abspath('\\'.join(args))         
    return string

def filter_stations(df,list_reg=['07','08','09']):
    idx_reg=df.index[df.index.str.startswith(tuple(list_reg))]
    df_reg=df.loc[idx_reg]
    return df_reg
    
def parse_att_fisicos(df):
    atts=['mean_elev','mean_slope_perc','_forest','_grass','shrub_frac',
'geol_class_1st_','crop_frac','land_cover_missing','frac_snow']
    atts_fisico=df.columns[df.columns.str.contains('|'.join(atts))]
    atts_fisico=[x for x in atts_fisico if ('frac_snow_tmpa' not in x)]
    return df[atts_fisico]

def geo_to_utm(gdf):
    gdf.set_crs(epsg='4326',inplace=True)
    gdf.to_crs(epsg='32719',inplace=True)
    gdf.index=gdf['rut']
    return gdf

def similitud_fisica(est,df_fisic_norm,df_coord_reg,df_coord_camels):
    '''
    Quevedo et al. (2021)
    1. Se elabora un ranking de similitud con las estaciones vecinas, 
    considerando el set de atributos asociado al criterio de interés y la 
    ecuación 2.1. la fórmula de similitud es Sij=Sum(ai-aj)/IQR(a)
    2. Se calcula el coeficiente de determinación entre los caudales de la cuenca
    objetivo y los caudales de las diez cuencas más similares según el ranking 
    efectuado anteriormente.
    3. De las diez cuencas encontradas, se escoge un máximo de cuatro cuencas 
    candidatas que cuenten con coeficientes de determinación mayor a 0,5.
    4. Se ajusta un modelo lineal entre la estación objetivo y la primera 
    estación candidata, y se rellenan los caudales faltantes con dicho modelo. 
    Se repite el procedimiento con las estaciones candidatas restantes 
    (considerando sólo datos observados) y se estiman los datos que no pudieron
    ser rellenados con estaciones de mejor ranking.
    '''      
    # filtrar primero las estaciones a menos de 200km
    coord_est=df_coord_reg[df_coord_reg['rut']==est]
    est_near=min_dist(coord_est.geometry,df_coord_camels, 200)
    idx_near=est_near.index.intersection(df_fisic_norm.index)
    df_fisic_norm_near=df_fisic_norm.loc[idx_near].copy()
    
    # evaluar la similitud fisica de otras cuencas
    try:
        row=df_fisic_norm_near.loc[est]
        Sij=np.abs(df_fisic_norm_near-row)/(df_fisic_norm_near.quantile(.75)-df_fisic_norm_near.quantile(.25))
        Sij_rms=Sij.apply(lambda x: np.sqrt(np.sum(x**2)),axis=1)
        est_simil=Sij_rms.sort_values(ascending=True)[1:22]
        return est_simil
    except:
        return pd.DataFrame(index=[est])

def day_to_mon(df_day,flags_DGA):
    df_filtered=df_day.copy()
    # flags de la DGA
    for est in df_day.columns:
        serie_est=df_day[est][flags_DGA[est].str.contains('\*',na=False)]
        # si se tienen datos suficientes para calcular desviaciones standard y
        # outliers
        est_notna=df_day[est][df_day[est].notna()]
        if len(est_notna.values)>365*20:
            df_filtered[est]=filter_outliers(serie_est,df_day)
           
    # meses con a lo menos 20 dias de información (CNR (2014))
    # flags_20_dias
    flags_day=df_filtered.copy()
    flags_day=flags_day.where(flags_day.isna(),other=1)
    flags_day.fillna(0,inplace=True)
    flag_qmon=flags_day.resample('MS').sum()
    
    # promedio mensual
    df_filter_mon=df_filtered.resample('MS').mean()
    
    # eliminar meses con menos de 20 dias de informacion
    df_filter_mon=df_filter_mon.where(flag_qmon>=20,other=np.nan)
    
    return df_filter_mon
    
def filter_outliers(serie,df_completo,flag=True):
    # filtrar flags DGA      
    rut=serie.name
    df_est_completo=pd.DataFrame(df_completo[rut]).copy()
    rango=range(1,13)
    for mes in rango:
        df_mon=df_est_completo[df_est_completo.index.month==mes]
        
        # calcular el indice de los outliers
        outliers=np.abs(df_mon-df_mon.mean())/df_mon.std()>30.
        
        # definir outliers dentro de los flags de la DGA que se removerán
        idx = serie.index.intersection(outliers.index)
        if flag:
            df_est_completo.loc[idx,rut]=np.nan
        
    return df_est_completo

def min_years(df_mon,minYr):
   
   data=df_mon.notnull().astype('int')
   data=data.groupby(df_mon.index.year)  
   data_anual=data.aggregate(np.sum)
   data_anual=data_anual/(12*0.8)  
   data_anual = data_anual.apply(lambda x: [y if y < 1 else 1 for y in x])
   data_anual = data_anual.transpose()
  
   data_anual = data_anual.sort_index()
   estaciones_minimas=pd.DataFrame(data_anual.sum(axis=1),columns=['registro'])
   estaciones_minimas=estaciones_minimas[estaciones_minimas['registro']>=minYr]
   
   return estaciones_minimas
  
def merge_columns(df):
    df_merged=pd.DataFrame(index=pd.date_range(df.index.min(),
df.index.max(),freq='1d'),columns=[df.columns[0]])
    
    for col in reversed(range(len(df.columns)-1)): # itera sobre indices de columnas en vez de nombres porque cuando los nombres de columnas son iguales no funciona
        columna=df.iloc[:,col][df.iloc[:,col].notna()]
        df_merged.loc[columna.index,df_merged.columns[0]]=columna.values
    return df_merged

def dms2dd(degrees, minutes, seconds, direction):
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
    if direction == 'E' or direction == 'S':
        dd *= -1
    return dd;

def dd2dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return [d, m, sd]

def parse_dms(dms):
    if not isinstance(dms, (int, float)):
        parts = re.split('[^\d\w]+', dms)
        lat = dms2dd(parts[0], parts[1], parts[2], parts[3])
    else:
        lat=-dms
    return -(lat)
#%%    
    
def main(root,cuenca,yr_ini,path_q_0,path_q_region,path_q_2,ruta_reg,path_shac):
    """
    

    Parameters
    ----------
    root : str
        carpeta de trabajo, ejemplo r'G:\OneDrive - ciren.cl\2022_Nuble_Embalses'
    cuenca : str
        cuenca o region de análisis.
    yr_ini : str o int
        año de inicio desde el cual se realizará el relleno y extensión de data.
    path_q_0 : str
        ruta de la planilla de caudales de region o cuenca al norte del área 
        en estudio. Ejemplo join_path(root,'Datos','Caudales',
                                'CaudalesDGA_Maule_2021_revA.xlsx')
    path_q_region : str
        ruta de la planilla de caudales de region o cuenca en estudio. Ejemplo
  ruta de la planilla de caudales de region o cuenca al norte del área 
  en estudio. Ejemplo join_path(root,'Datos','Caudales',
                           'CaudalesDGA_Nuble_2021_revA.xlsx')
    path_q_2 : str
        ruta de la planilla de caudales de region o cuenca al sur del área 
        en estudio. Ejemplo join_path(root,'Datos','Caudales',
                                'CaudalesDGA_BioBio_2021_revA.xlsx')
    ruta_reg : str
        ruta del shape de la cuenca o región en estudio. Ejemplo
        os.path.join('..','SIG','REGION_NUBLE','region_Nuble.shp')
    path_shac : str
        ruta de los SHACS a nivel nacional. Ejemplo 
os.path.join('..', 'SIG', 'SHACS',
                          'Acuiferos_SHAC_Julio_2022.shp')
    
    Notas: Necesariamente debe existir una carpeta con el dataset de las cuencas 
        CAMELS y debe ubicarse en la siguiente ruta:
    os.path.join('..','Datos','dataset_cuencas','CAMELS_CL_v202201')      


    Returns
    -------
    None.
    
    Outputs
    -------
    Caudales medios mensuales rellenados y extendidos.

    """



#%%    

    #minimo de años con datos, Quevedo et al. (2021)
    minYr = 4

    # rango de fechas de las nuevas normales
    date_start=pd.to_datetime(str(1952)+'-04-01')
    date_end=pd.to_datetime(str(datetime.date.today().year)+'-03-31')
    
    # rutas
    root='.'
    ruta_Archivos=join_path(root,'..','Antecedentes','Caudales')
    list_arc_est = []

    for path, subdirs, files in os.walk(ruta_Archivos):
        for name in files:
            if name.startswith("CaudalesDGAyMOP_"): list_arc_est.append(pathlib.PurePath(path, name))
    
    # ruta de archivos con registros previos a 1972 (revB)
    ruta_Q_0_dga=[x for x in list_arc_est if 'Atacama' in x.name and x.name.endswith('revB.xlsx')][0]
    ruta_Q_1_dga=[x for x in list_arc_est if 'Coquimbo' in x.name and x.name.endswith('revB.xlsx')][0]
    ruta_Q_2_dga=[x for x in list_arc_est if 'Valpara' in x.name and x.name.endswith('revB.xlsx')][0]

    # region y shacs
    ruta_reg=os.path.join('..','SIG','Base','REGIONES_2020.shp')
    path_shac = os.path.join('..', 'SIG', 'SHACS','Acuiferos_SHAC_Julio_2022.shp')   
    
    shacs=gpd.read_file(path_shac)
    reg=gpd.read_file(ruta_reg)
    reg=reg[reg['REGION']=='Coquimbo']
    
    # unir region Nuble y shacs
    reg.set_crs(epsg='5360',inplace=True)
    reg.to_crs(epsg='32719',inplace=True)
    shacs_inter=gpd.overlay(shacs, gpd.GeoDataFrame([],
                                                    geometry=reg.buffer(1e3)))
    #%%
    shacs_reg=shacs[shacs['OBJECTID_1'].isin(shacs_inter['OBJECTID_1'])]
    
    # leer dataset CAMELS
    path_camels=os.path.join('..','Datos','dataset_cuencas','CAMELS_CL_v202201')
    camels=pd.read_csv(os.path.join(path_camels,'catchment_attributes.csv'),
                       index_col=0)
    
    # calcular el digito verificador
    camels.index=parse_digito_verificador(camels.index)
    camels=filter_stations(camels,['03','04','05'])
    
    # atributos fisicos
    camels_fisico=parse_att_fisicos(camels)
        
    # coordenadas camels
    coords_camels=gpd.GeoDataFrame(camels,
    geometry=gpd.points_from_xy(x=camels['gauge_lon'],y=camels['gauge_lat']))
    coords_camels.set_crs(epsg='4326',inplace=True)
    coords_camels.to_crs(epsg='32719',inplace=True)
    
    # normalizar cada columna de los atributos fisicos
    camels_fisic_norm=camels_fisico.apply(lambda x: np.abs((x-x.mean())/x.std()),
                                                           axis=0)
    camels_fisic_norm=camels_fisic_norm.apply(lambda x: x/x.max(),axis=0)
    
    # leer caudales
    # dga
    q_day_0_dga=pd.read_excel(ruta_Q_0_dga,sheet_name='Datos',index_col=0,
                              parse_dates=True,skiprows=[1])
    q_day_1_dga=pd.read_excel(ruta_Q_1_dga,sheet_name='Datos',index_col=0,
                              parse_dates=True,skiprows=[1])
    q_day_2_dga=pd.read_excel(ruta_Q_2_dga,sheet_name='Datos',index_col=0,
                              parse_dates=True,skiprows=[1])
    
    # merge region 1, region 2 y region 3
    q_day=pd.concat([q_day_0_dga,q_day_1_dga,q_day_2_dga])

    #filtrar estaciones que sean canales, vertederos, desagues
    names_blacklist=['canal','desague','vertedero','dren']
    
    # leer metadata dga de region 1, region 2 y region 3
    metadata_0_dga=pd.read_excel(ruta_Q_0_dga,sheet_name='Ficha_est',index_col=0)
    metadata_0_dga[['Lon','Lat']]=metadata_0_dga[['Lon','Lat']].applymap(lambda x:parse_dms(x))
    metadata_1_dga=pd.read_excel(ruta_Q_1_dga,sheet_name='Ficha_est',index_col=0)
    metadata_1_dga[['Lon','Lat']]=metadata_1_dga[['Lon','Lat']].applymap(lambda x:parse_dms(x))    
    metadata_2_dga=pd.read_excel(ruta_Q_2_dga,sheet_name='Ficha_est',index_col=0)
    metadata_2_dga[['Lon','Lat']]=metadata_2_dga[['Lon','Lat']].applymap(lambda x:parse_dms(x))    
    
    # merge metadata    
    metadata=pd.concat([metadata_0_dga,metadata_1_dga,metadata_2_dga],ignore_index=True)
    
    blacklist=metadata['Estacion'].str.lower().str.contains('|'.join(names_blacklist))
    metadata=metadata[~blacklist]
    
    # leer y combinar informacion de estaciones duplicadas
    dupls=metadata['rut'][metadata['rut'].duplicated()]
    
    for dupl in dupls:
        rut_dupl=metadata['rut'][metadata['rut']==dupl]
        q_day[rut_dupl.iloc[0]]=merge_columns(q_day[rut_dupl])
        del q_day[rut_dupl.iloc[-1]]
    
    metadata.drop_duplicates(subset='rut') #eliminar estaciones duplicadas
    
    # gdf de metadata
    gdf_metadata=gpd.GeoDataFrame(metadata,
            geometry=gpd.points_from_xy(x=metadata['Lon'],y=metadata['Lat']))
    gdf_metadata.set_crs(epsg='4326',inplace=True)
    gdf_metadata.to_crs(epsg='32719',inplace=True)
    
    # estaciones en shacs
    est_utm_shac=gpd.overlay(gdf_metadata,shacs_reg)
    
    # filtrar los caudales segun fechas a rellenar
    q_day=q_day.loc[(q_day.index<=date_end) & (q_day.index>=date_start)]

    # leer flags 
    # maule
    flag_DGA_0=pd.read_excel(ruta_Q_0_dga,sheet_name='Flags',index_col=0,
                              parse_dates=True,skiprows=[1])
    flag_DGA_1=pd.read_excel(ruta_Q_1_dga,sheet_name='Flags',index_col=0,
                              parse_dates=True,skiprows=[1])
    flag_DGA_2=pd.read_excel(ruta_Q_2_dga,sheet_name='Flags',index_col=0,
                              parse_dates=True,skiprows=[1])
        
    # merge 
    flags=merge_dfs(flag_DGA_0,flag_DGA_1)
    flags=merge_dfs(flags,flag_DGA_2)
    flags=flags.loc[(flags.index<=date_end) & (flags.index>=date_start)]

    # promediar caudales medios diarios considerando flags y meses con mas
    # de 20 registros
    q_mon=day_to_mon(q_day,flags)
      
    # caudales de rios, esteros, quebradas, etc.
    qmon_white=q_mon.columns[q_mon.columns.isin(metadata[~blacklist]['rut'])]
    qmon=q_mon[qmon_white]    
  #%Crear indice de fechas, convertir años a int y calcular frecuencia de datos

    # seleccionar estaciones con un minimo de 20 years (Quevedo, 2021)
    estaciones_min=min_years(qmon,minYr)
    qmon_filtradas=qmon.copy()[estaciones_min.index]

    #%% Relleno
    
    # inicializacion de variables
    n_multivariables=4 # 4 estaciones de relleno Quevedo, 2021
    
    # z-value
    stdOutliers=3

    # meses
    meses=range(1,13)
    
    # df relleno
    q_mon_MLR=qmon_filtradas.copy()
    q_mon_MLR=q_mon_MLR.astype(float)
    
    # Multivariable
    # rellenar estaciones en shacs
    estaciones=qmon_filtradas.columns.intersection(est_utm_shac['rut'])
    
    df_check=q_mon_MLR[estaciones].copy()
    
    while df_check.isnull().values.any():
        for col in estaciones:
            # print('Rellenando estación '+str(col),metadata[metadata['rut']==col]['Estacion'].iloc[0])
                        
            for mes in meses:
                q_mon_mes=qmon_filtradas.loc[qmon_filtradas.index.month==mes].copy()
                y=q_mon_mes[col]
                           
                if y.count() < 1:
                    continue
                
                # obtener estaciones con similitud fisica
                # pueden haber estaciones fuera de los shacs segun Quevedo, 2021
                est_similares=similitud_fisica(col,camels_fisic_norm,
                                               gdf_metadata,coords_camels).index         
    
                # similitud hidrológica
                correl=q_mon_mes.astype(float).corr()
                coord_est=gdf_metadata[gdf_metadata['rut']==col].geometry
                est_near=min_dist(coord_est.geometry,gdf_metadata, -1)
                idx=q_mon_mes.columns.intersection(list(est_near['rut']))
                est_indep=mejoresCorrelaciones(correl.loc[list(idx)],col, -1)

                if len(est_similares)>1:
                    est_indep=[col]+list(set(est_indep) & set(est_similares))
                # a lo más 4 estaciones para rellenar
                est_indep=list(est_indep[:n_multivariables])+[col]
                est_indep=list(set(est_indep))
                if col in ['04522001-K','04531001-9','04535002-9','04506002-0','04550003-9']:
                    print(metadata[metadata['rut'].isin(est_indep)]['Estacion'].values)
                x=pd.DataFrame(q_mon_mes.loc[q_mon_mes.index.month==mes][est_indep].copy(),
                                                                   dtype=float)
                
                x=x.dropna(how='all',axis=1)
                
                max_value_=x.mean()+stdOutliers*x.std()
                
                imp=IterativeImputer(imputation_order='ascending',random_state=0,
            max_iter=10,min_value=0,max_value=max_value_,sample_posterior=True)
                Y=imp.fit_transform(x)
                Q_monthly_MLR_mes=pd.DataFrame(Y,columns=x.columns,index=x.index)
                Q_monthly_MLR_mes=Q_monthly_MLR_mes.dropna()
    
                q_mon_MLR.loc[Q_monthly_MLR_mes.index,
                              col]=Q_monthly_MLR_mes[col].values
                df_check=q_mon_MLR[estaciones].copy()
                
#%% plots para presentación
    # qmon_filtradas=qmon_filtradas.loc[qmon_filtradas.index>='1982-04-01']
    plt.close('all')
    q_mon_MLR=q_mon_MLR.loc[q_mon_MLR.index>='1982-04-01']
    lista_limari=['04532001-4', '04534001-5', '04533002-8', '04520001-9', 
'04522001-K', '04530001-3','04531001-9', '04531002-7', '04514001-6', '04515002-K', 
'04535002-9', '04535003-7','04537001-1', '04506002-0', '04506003-9', '04550003-9',
 '04540003-4', '04501001-5','04501002-3', '04502001-0', '04503001-6', '04516001-7',
'04523001-5', '04522002-8','04523002-3', '04540001-8', '04556001-5', '04557002-9', 
'04558001-6', '04511002-8','04512001-5', '04513001-0']
    lista_limari=[x for x in lista_limari if x not in ['04535003-7','04506003-9',
                                                       '04540003-4']]
    n=int(np.sqrt(len(lista_limari)))+1
    fig,axes=plt.subplots(1)
    axes=q_mon_MLR[lista_limari].resample('Y').mean().plot(subplots=True,layout=(n,n),rot=45,color='b',
                                      legend=False)
    plt.subplots_adjust(left=0.1,bottom=0.1,right=0.9,top=0.9,wspace=0.37, 
                    hspace=0.12)
    axes=axes.reshape(-1)
    for i,a in enumerate(axes[:-2]):
        try:
            qmon_filtradas[lista_limari[i]].resample('Y').mean().plot(ax=a,rot=45,color='r',legend=False)
            # a.legend(loc='best', prop={'size': 7})
            a.set_ylim(bottom=0)
            a.set_ylabel('$\overline{Q}$mensual ($m^3/s$)', fontsize=9)
            a.tick_params(axis='y', which='major', labelsize=9)
            a.set_title(gdf_metadata.Estacion[gdf_metadata.rut == lista_limari[i]].iloc[0], fontsize=9)
            a.set_xlim(['1982-04-01','2022-03-31'])
        except IndexError as e:
            print(str(e)+'not found')
            

    for i,a in enumerate(axes):
        a.set_ylim(bottom=0)
        if i<int(np.sqrt(len(lista_limari)))*(int(np.sqrt(len(lista_limari)))-1):
            pass
            # a.set_xticks([])
        if i%6!=0:
            a.set_ylabel('')
        
    plt.subplots_adjust(left=0.1,bottom=0.1, 
                right=0.9, 
                top=0.9, 
                wspace=0.14, 
                hspace=0.24)

    plt.savefig(os.path.join('.','outputs','q_mean_yr_complete.png'),
                bbox_inches='tight')
        
    #%% Guardar
    filename='q_relleno_'+str(cuenca)+'_'+str(qmon.index.year.min()+1)+'-'+\
        str(qmon.index.year.max())+'_monthly.xlsx'
        
    path_save=os.path.join('.','outputs',filename)
    with pd.ExcelWriter(path_save) as writer:
        q_mon_MLR[estaciones].to_excel(writer,sheet_name='Data')
        
        est_utm_shac.to_excel(writer,sheet_name='Ficha_est')
    writer.save()
    writer.close()
        