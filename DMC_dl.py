# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 10:25:23 2020

@author: ccalvo
"""

import requests
import zipfile
import os
import random
from time import sleep
import pandas as pd
import random
import numpy as np
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt
import datetime

def bajarDMCAutomaticas(var='Temperatura del Aire Seco'):    
    
    dictURL={'Temperatura del Aire Seco':r'_XXXX_Temperatura_',
             'Agua Caida, Total Diario':r'_XXXX_Agua24Horas_'}
    estaciones = ['320003','320004','320005','320006','320007','320008',
'320009','320010','320011','320012','320013','320014','320015','320016',
'320017','320018','320019','320020','320021','320022','320023','320024',
'320026','320027','320028','320029','320030','320031','320032','320033',
'320034','320035','320036','320037','320039','320040','320041','320043',
'320045','320048','320055','320901','320909','320910','320911','320913',
'320922','320934','330001','330002','330004','330005','330006','330007',
'330008','330009','330010','330011','330012','330013','330014','330015',
'330016','330017','330018']
    
    # felipe magallanes
    # estaciones=['950007','530029','520031','510901','520009','950008','950009','950010','950011','950012','950013','950014','950015','950016','950017','510020','520030','550902','540008','510003','500003','500004','500005','510007','510008','510009','510010','510012','510013','510014','510015','510016','510018','510019','520016','520017','520018','520019','520020','520021','520022','520023','520024','520025','520026','520028','520029','530012','530013','530014','530015','530016','530017','530018','530019','530020','530021','530022','530023','530024','530025','530026','530027','530028','540002','540003','540004','540005','540006','540007','550003','500001','510011','510017','520011','520027','530010','530011','950006','950901','520015','530009','520001','540001','520010','520007','520004','520014','530006','530003','520013','510004','520002','520003','530001','530002','490001','510006','520005','500002','560002','550002','560001','510005','530005','550001','950001','950002','950003','520006','520012','530008','530004']
    
    ruta_GitHub = '.'
    ruta_descargas = os.path.join(ruta_GitHub,'outputs')
    rutaDl=os.path.join(ruta_descargas,'DMC')

    for estacion in estaciones:
        sleep(random.randint(5,10)) #NO CAMBIAR
    

        URLdatos='https://climatologia.meteochile.gob.cl/application/datos/getDatosSaclim/'+estacion+dictURL[var]
        r = requests.get(URLdatos, stream = True)
        textoURL = r.text
        
        if ('encontra' not in textoURL) & ('No hay' not in textoURL):
            with open(rutaDl+"\\Pp"+estacion+".zip","wb") as zipf:
                 for chunk in r.iter_content():
                     zipf.write(chunk)
            zipf.close()
    
    files=os.listdir(rutaDl)
    files=[x for x in files if x.endswith('.zip')]
    for file in files:
        zip_ref = zipfile.ZipFile(os.path.join(rutaDl,file)) # create zipfile object
        zip_ref.extractall(rutaDl) # extract file to dir
        zip_ref.close() # close file
        os.remove(os.path.join(rutaDl,file)) # delete zipped file

    return None

def bajarDMCOtras(estaciones):
    #%%

    ruta = r'G:\OneDrive - ciren.cl\Proyectos_RHidricos_2023\Ficha_07_Valparaiso\Scripts\outputs\DMC'
    ruta=r'G:\OneDrive - ciren.cl\Proyectos_RHidricos_2023\Ficha_07_Valparaiso\Entregas\20231004\Anexo1-2\T'
    # Maule       
    estacionesOtras = ['320012','320024','320019','320045','320046','320048',
    '320055','330006','320005','320006','320007','320010','320015','320018',
    '320039','330005','330009','330007','330030','330031','270001','320027',
    '330066','330088','330002','320013','320023','320004','320009','320014',
    '320017','320020','320021','320022','320025','320029','320030','320031',
    '320032','320033','320034','320035','320036','320037','320042','320050',
    '320049','320043','320047','330008','330004','320044','330014','330001',
    '330028','330045','330043','330067','320051','330044','330003','320040',
    '320056','320028','320041','330089','330090','320026','320901','330120',
    '320016','320008','320003','330914','260007','330982','320067','330139',
    '320069','320076','320073','320065','320066','320077','320071','320074',
    '320070','320075','320068','320072','320078','330123','330124','330125',
    '330126','330127','330128','330129','320063','320911','320909','320922',
    '320934','330055','330053','330048','330049','330161','330059','320091',
    '320097','320096','320095','320094','320093','320092','320102','320101',
    '320100','320099','320087','320080','320086','320081','320082','320083',
    '320084','320085','320089','320088','320090','320098','320119','320120',
    '320117','320118','330189','330191','320103','320104','320105','320106',
    '320107','320108','320109','320110','320111','320112','320113','320114',
    '320115','330185','330186','330187','330188']
    # quitar duplicados
    estaciones = list(dict.fromkeys(estaciones))
    estaciones=list(set(estacionesOtras+estaciones))
    
    # ===========================
    # Variables que deseen bajar
    # ===========================

    variable = 'Agua Caida, Total Diario'
    variable = 'Temperatura del Aire Seco'
#    variable = 'Temperatura Mínima AM'
#    variable = '2da. TempMín (Temp. Mínima PM)'
#    variable = '2da. TempMáx (Temp. Máxima AM)'
#    variable = 'Temperatura Máxima PM'
    # variable = 'Viento a 10 m. de Altura'
               
    producto = {
                'Agua Caida, Total Diario': ['57','125'], #precipitación cada 24 horas
                'Temperatura del Aire Seco' : ['26', '58'],
                'Temperatura Mínima AM' : ['42', '97'],
                '2da. TempMín (Temp. Mínima PM)' : ['43', '98'],
                '2da. TempMáx (Temp. Máxima AM)' : ['44', '100'],
                'Temperatura Máxima PM' : ['45', '102'],
                'Viento a 10 m. de Altura' : ['28','61']
                } 

    url = 'https://climatologia.meteochile.gob.cl/application/informacion/datosMensualesDelElemento'
    user_agent_list = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'
    ]      

    for estacion in estaciones[59:]:
        all_data = pd.DataFrame([])             
        
        direccion_ficha_est = r'https://climatologia.meteochile.gob.cl/application/informacion/fichaDeEstacion'+'/'+estacion
        User_agent =  random.choice(user_agent_list)
        
        sleep(random.randint(5,10)) #NO CAMBIAR
        r = requests.get(direccion_ficha_est, 
        headers = {'User-Agent': User_agent}, stream = True)
        
        if "<h1>404</h1>" in r.text:
            continue
            
        nombre = pd.read_html(r.text)[0]
        coordenadas = pd.read_html(r.text)[1]
        ficha = pd.concat([nombre, coordenadas])
        
        desde_hasta =[x for x in  pd.read_html(r.text) if type(x.columns)==pd.core.indexes.multi.MultiIndex]
        desde_hasta=[x for x in desde_hasta if x.columns.get_level_values(0).str.contains('Información Disponible').any()][0]
        desde_hasta.columns=desde_hasta.columns.get_level_values(1)
        
        if len(desde_hasta)<1:
            continue

        indice=desde_hasta['Nombre'][desde_hasta['Nombre']==variable].dropna().index
        if len(indice) == 0:
            strings=variable.split(' ')
            strings=[x.replace(',','') for x in strings]
            base = r'^{}'
            expr = '(?=.*{})'
            lookup=base.format(''.join(expr.format(w) for w in strings))
            # look for a row in df desde_hasta where the first column contains all of the strings in the list strings
            indice=desde_hasta['Nombre'][desde_hasta['Nombre'].str.contains(lookup)].dropna().index
        
        colDesde=desde_hasta.columns[desde_hasta.columns.str.contains('Desde')]
        desde=desde_hasta[colDesde].values[0][0]
        if (len(indice) > 0) and (desde!= '.'):
            year_i = int(desde)
            colHasta=desde_hasta.columns[desde_hasta.columns.str.contains('Hasta')]
            year_f = int(desde_hasta[colHasta].values[0][0])
            agnos = np.arange(year_i, year_f+1)
            agnos = agnos[agnos > 1990]

            if len(agnos) > 0:
                for agno in agnos:
                    print(agno)
                    for mes in np.arange(1,13,1):
                        direcccion = url+'/'+estacion+'/'+str(agno)+'/'+str(mes)+'/'+producto[variable][0]
                        sleep(random.randint(5,10)) #NO CAMBIAR
                        User_agent =  random.choice(user_agent_list)
    
                        r = requests.get(direcccion, 
                        headers = {'User-Agent': User_agent}, 
                        cookies={'_ga':'GA1.3.1338480043.1657224266',
                        'PHPSESSID':'ct895a4fd264uftun9p8ffup6n'},stream = True)
                        textoURL = pd.read_html(r.text)
                        all_data = all_data.append(textoURL,ignore_index=True)
                
                if (variable == 'Temperatura del Aire Seco') | (variable == 'Viento a 10 m. de Altura'):
                    all_data.index =  pd.to_datetime(all_data['Fecha']+' '+all_data['Hora (UTC)'], dayfirst = True)
                else:
                    cols=all_data.columns[list(all_data.columns).index('Fecha')]
                    all_data.index =  pd.to_datetime(all_data['Fecha'],
                     dayfirst = True)
                    
                all_data.sort_index(inplace=True)
                all_data = all_data.loc[all_data.index.notnull()]
                
                writer = pd.ExcelWriter(ruta+'\\'+variable+'_estacion_'+estacion+'.xlsx', engine='xlsxwriter')
                
                # Write each dataframe to a different worksheet.
                ficha.to_excel(writer, sheet_name='ficha_est')
                all_data.to_excel(writer, sheet_name='Datos')
                
                # Close the Pandas Excel writer and output the Excel file.
                writer.save()
                writer.close()

#%%
def ordenarMOP(ruta = r'C:\Users\ccalvo\OneDrive - ciren.cl\HM\RM\Temperatura\Rio Volcan en Queltehues', file = 'T_rio_Volcan_en_Queltehues.csv'):
        
    os.chdir(ruta)
    all_data = pd.DataFrame([])
    
    for filename in os.listdir(ruta):
        archivo = pd.read_html(ruta+'\\'+filename)[0]
        archivo.index = pd.to_datetime(archivo['Fecha'])
        all_data = all_data.append(archivo,ignore_index=True)
    all_data.index =  pd.to_datetime(all_data['Fecha-Hora de Medicion'], dayfirst = True)
    all_data.sort_index(inplace=True)
    all_data.iloc[:,2:] = all_data.iloc[:,2:]/1000.
    all_data.to_csv(file)

def ordenarDMC(ruta, file):
    
    # ==================
    # Precipitaciones
    # ==================
    

    ruta=r'G:\OneDrive - ciren.cl\2022_Nuble_Embalses\Datos\Precipitacion\DMC'
    ruta=r'G:\OneDrive - ciren.cl\Proyectos_RHidricos_2023\Ficha_07_Valparaiso\Scripts\outputs\DMC'
    ruta=r'G:\OneDrive - ciren.cl\Proyectos_RHidricos_2023\Ficha_07_Valparaiso\Entregas\20231004\Anexo1-2\T'
    all_data = pd.DataFrame([], index = pd.date_range('1900-01-01',
    pd.to_datetime(datetime.date.today()),freq = '1d'))   
    meta_data = pd.DataFrame([], index = ['Codigo','Pseudonimo','Lat','Lon',
                                          'Alt','Zone'])
    
    for filename in os.listdir(ruta):
        if filename.endswith(".xlsx"): 
            estacion = filename[-11:-5]
            df = pd.read_excel(ruta+'\\'+filename, sheet_name = 'Datos', parse_dates = True, index_col = 0)
            df=df.resample('1D').mean()
            metadata = pd.read_excel(ruta+'\\'+filename, sheet_name = 'ficha_est', parse_dates = True, index_col = 0)
            metadata.iloc[8,1] = int(metadata.iloc[8,1].strip(' Mts.'))
            meta_data[estacion] = metadata.iloc[[0,4,6,7,8,11],1].values
            if len(df.dropna(how='all'))==0:
                continue
            col=df.columns[df.columns.str.contains('Ts',na=False)][0]
            all_data.loc[df.index,estacion] = df[col]
   
    all_data = all_data.replace('.',np.nan)
    all_data = all_data.loc[all_data.index > '1989-01-01']
    meta_data = meta_data.transpose()
    
    # QAQC
    gdf_meta=gpd.GeoDataFrame(meta_data,geometry=gpd.points_from_xy(x=meta_data['Lon'],
y=meta_data['Lat']))
    gdf_meta.set_crs(epsg=4326,inplace=True)
    gdf_meta.to_crs('EPSG:32719',inplace=True)
    fig,ax=plt.subplots(1)
    gdf_meta.plot(ax=ax)
    ctx.add_basemap(ax=ax, crs=gdf_meta.crs.to_string(),
                    source=ctx.providers.Esri.WorldImagery, zoom=9, alpha=0.6)
    
    # ===============================
    #           Por cuenca
    # ===============================
    
    region = 'Valparaiso'
    
    # ------Guardar
    
    writer = pd.ExcelWriter(ruta+'\\t_DMC_daily_'+region+'.xlsx', 
                            engine='xlsxwriter')

    # Write each dataframe to a different worksheet.
    meta_data.to_excel(writer, sheet_name='ficha_est')
    all_data.to_excel(writer, sheet_name='Datos')
    
    
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()
    writer.close()

# =============================================================================
def ordenarCNE():
# precipitaciones
# -----------------------------------------------------------------------------    
    
    ruta=r'G:\OneDrive - ciren.cl\2022_Nuble_Embalses\Datos\Precipitacion\CNE'
    path_pp=os.path.join(ruta,'se_precipitaciones.csv')
    
    pp=pd.read_csv(path_pp,sep=';',index_col=0,parse_dates=True,dayfirst=True)
    cols=pp['nombre_embalse'].unique()
    
    df_all=pd.DataFrame(index=pd.date_range('2003-01-01','2022-06-07',freq='1D'),
columns=cols)
    for col in cols:
        data=pp[pp['nombre_embalse']==col]
        cols=data.columns[data.columns.str.contains('agua_',na=False)]
        data_col=data[cols[0]].str.replace(',','.').astype(float)
        df_all.loc[data_col.index,col]=data_col.values

    with pd.ExcelWriter(os.path.join(ruta,'se_precipitaciones.xlsx')) as writer:
        df_all.to_excel(writer,sheet_name='pp_CNE')
    writer.close()