# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 10:25:23 2020
@author: ccalvo
"""

import requests #librería para hacer consultas https
from time import sleep
import random
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os
import sys
#%% funciones
#Estos son los encabezados del método POST
def headersParam(cookies):
    headers={
				"Accept"
				: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
,
				"Accept-Encoding"
				: "gzip, deflate, br"
,
				"Accept-Language"
				: "en-US,en;q=0.5"
,
				"Connection"
				: "keep-alive"
,
				"Content-Length"
				: "251"
,
				"Content-Type"
				: "application/x-www-form-urlencoded"
,
				"Cookie"
				: cookies
,
				"DNT"
				: "1"
,
				"Host"
				: "snia.mop.gob.cl"
,
				"Origin"
				: "https://snia.mop.gob.cl"
,
				"Referer"
				: "https://snia.mop.gob.cl/dgasat/pages/dgasat_param/dgasat_param.jsp?param=1"
,
				"Sec-Fetch-Dest"
				: "document"
,
				"Sec-Fetch-Mode"
				: "navigate"
,
				"Sec-Fetch-Site"
				: "same-origin"
,
				"Sec-Fetch-User"
				: "?1"
,
				"TE"
				: "trailers"
,
				"Upgrade-Insecure-Requests"
				: "1"
,
				"User-Agent"
				: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}
    return headers

def paramsPOSTdata(estaciones,date): 
    data_param={
	"estacion1": "-1",
	"estacion2": "-1",
	"estacion3": "-1",
	"accion": "refresca",
	"param": "1",
	"tipo": "ANO",
	"fechaFinGrafico": date,
	"hora_fin": "0",
	"tiporep": "I",
	"period": "rango",
	"fechaInicioTabla": date,
	"fechaFinTabla": date,
	"UserID": "nobody",
	"EsDL1": "0",
	"EsDL2": "0",
	"EsDL3": "0"
} 
    
    for ind,est in enumerate(estaciones):
        data_param['estacion'+str(ind+1)]=est
        
    return data_param

def get_headers(cookies):
    headers = {
'Host': 'snia.mop.gob.cl',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
'Accept-Encoding': 'gzip, deflate, br',
'Referer': 'https://snia.mop.gob.cl/dgasat/pages/dgasat_param/dgasat_param_1.jsp',
'Content-Length': '798',
'Origin': 'https://snia.mop.gob.cl',
'Connection': 'keep-alive',
'Cookie': cookies,
'Upgrade-Insecure-Requests': '1',
'Sec-Fetch-Dest': 'empty',
'Sec-Fetch-Mode': 'no-cors',
'Sec-Fetch-Site': 'same-origin',
'Sec-Fetch-User': '?1',
'Content-Type': 'application/x-www-form-urlencoded',
'Pragma': 'no-cache',
'Cache-Control': 'no-cache',
'TE': 'trailers' }
    
    return headers

def headersGET(cookies):
    headers={	"Accept"
				: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
,
				"Accept-Encoding"
				: "gzip, deflate, br"
,
				"Accept-Language"
				: "es-CL,es;q=0.8,en-US;q=0.5,en;q=0.3"
,
				"Cache-Control"
				: "no-cache"
,
				"Connection"
				: "keep-alive"
,
				"Cookie"
				: cookies
,
				"Host"
				: "snia.mop.gob.cl"
,
				"Pragma"
				: "no-cache"
,
				"Referer"
				: "https://snia.mop.gob.cl/dgasat/pages/dgasat_param/dgasat_param_1.jsp"
,
				"Sec-Fetch-Dest"
				: "document"
,
				"Sec-Fetch-Mode"
				: "navigate",
            
				"Sec-Fetch-Site"
				: "same-origin"
,
				"Sec-Fetch-User"
				: "?1"
,
				"TE"
				: "trailers"
,
				"Upgrade-Insecure-Requests"
				: "1"
,
				"User-Agent"
				: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
}
    return headers

def POSTdata(g_recaptcha_response,fechaInicio,fechaFin,parametros,date,stations):
    data={
	"estacion1": "-1",
	"estacion2": "-1",
	"estacion3": "-1",
	"parametros":parametros,
	"accion": "refresca",
	"param": "",
	"tipo": "ANO",
	"g-recaptcha-response": g_recaptcha_response,
	"fechaFinGrafico": date,
	"hora_fin": "0",
	"tiporep": "S",
	"period": "rango",
	"fechaInicioTabla": fechaInicio,
	"fechaFinTabla": fechaFin,
	"UserID": "nobody",
	"EsDL1": "",
	"EsDL2": "",
	"EsDL3": ""
} 
    
    for ind,est in enumerate(stations):
        data['estacion'+str(ind+1)]=est
        
    return data

def parse_params(texto):
    df=pd.read_html(texto)
    max_df=[len(x) for x in df]
    df_yrs=df[max_df.index(max_df)]
    return df_yrs

def parse_tables(texto):

    df_yrs=pd.DataFrame([],index=[datetime.date.today()])
    df=pd.read_html(texto)
    max_df=[len(x) for x in df]
    max_second=max_df.index(sorted(max_df)[-2])
    if max_second>0:
        df_yrs=df[max_second]
        # parsear fechas
        df_yrs.set_index(keys=df_yrs.columns[1],drop=True,inplace=True)
        df_yrs.index=pd.to_datetime(df_yrs.index,format="%d/%m/%Y")
        
    return df_yrs

def parse_rut(sopa):
    # parsear todas las estaciones
    estaciones_all=[element.get_text() for element in sopa.find_all('option')]
    estaciones=estaciones_all[:estaciones_all.index(' - Seleccione Estación 2 - ')]
    
    # ruts
    rut_estacion=[x.split(' ')[0] for x in estaciones]
    
    return rut_estacion

def ordenarDGA(ests,df_DGA,lastYear):
    """
    

    Parameters
    ----------
    df : list
        estaciones a ordenar.
    df_DGA : Pandas DataFrame
        dataframe de los datos del BNA.

    Returns
    -------
    output : TYPE
        DESCRIPTION.

    """
    output=pd.DataFrame([],index=pd.date_range(start=str(lastYear)+'-01-01',
                                               end='2020-12-31',inclusive='right'))
    df_DGA.index = pd.to_datetime(df_DGA.index)
    output_flag=pd.DataFrame([],index=pd.date_range(start=str(lastYear)+'-01-01', 
end='2020-12-31',inclusive='right'))

    for ind,est in enumerate(ests):
        q_est=df_DGA[df_DGA['rut'] == ests[ind]]
        fechas=q_est.index
        caudal=q_est['Q (m3/s)']
        flags=q_est['flag']
        
        q_est_df=pd.DataFrame(caudal.values,index=fechas,columns=[est])
            
        output.loc[q_est_df.index,est]=q_est_df[est].values
        output_flag.loc[flags.index,est]=flags.values

    return output,output_flag  

def date_rut(rut,df_,lastYear):
    date_first=df_[df_['rut']==rut].index
    if len(date_first)>=1:
        idx=date_first[-1]
        return  pd.to_datetime(idx,format='%Y-%m-%d')
    else:
        return pd.to_datetime('01-01-'+str(lastYear),format='%d-%m-%Y')
    
def checkFile(path):
    return os.path.isfile(path)
#%%
def main(cookies,g_recaptcha):
    
    cookies='__uzma=3f5bb002-58ef-4822-97bc-e1701a390727; __uzmb=1731693866; __uzme=5422; __ssds=3; __ssuzjsr3=a9be0cd8e; __uzmaj3=c885041e-ead3-4b02-80ba-bb96493cff81; __uzmbj3=1731693914; _ga=GA1.1.950226115.1731773240; JSESSIONID=0000HYiEUsRPU5MuK6ittdgnaY1:-1; _ga_Y8S34E0V2R=GS1.1.1731787861.2.0.1731787871.50.0.1047810154; __uzmc=903349423712; __uzmd=1731787895; __uzmcj3=914246411504; __uzmdj3=1731787898'
    g_recaptcha='03AFcWeA5Xw1rWuGqWRlgYGnWmI3PIwlFn8cBMl0-G6nA454uPXiA69ejvMrkQ3NIn97uy4sdqKipfPiRpQ6xNkWs3lN69IUUTFyZTZ-_vULyxpKVAUlgxY33wjG1z-NuBiCQ-tBsHKpYXtoWZbbDzBumJqzr1CUnHsllDzbBmuYmawjScyU106uzGsB7n2ZmhnUGKE-W7ayWr3C1wQE0y55atAboONXZMVCuFfdzucIqXr4Es_tl-gT-go8nX89KcFcqkRGU9uQGnAbH6qikJqeKxZRghC4gp_nN0cYuiGBMvnyRi4OBs1c-9Wj0MsV-cRmqFQ3xAnukSkkwOCBMl2MMwAPobcrwrE_1EZBU9ezwr0NPWTjBJ-AN9kthmhiIhLoeS1irEvVtGzxAZrOYUthjirrO3vLbJqajoo4JiWTExU4YUz42bFxQpTKq3C6olm59ADenX7kkwbj6lW0JtIExMuaQwDYUbD5wlbRI7Pb5s10hsI82pE5gPEZoGIjbFde7KPXBw-vNra-HNRz_t__YwLSm3in2MCGyhhAhj-vO_zQte9gczIjpKlCT9AgbfTzwb6fbV1zMK-BzOst3DxGq1JYUTj25Ka9Zdb__tJWJPtSlk4StoiIGuGGme1Tmw145h0QfFrwFpxC0lYigxmOrQhKANRD73sssTVt5DqPqyL9Fg6_IAjl6Jb8BHC3WVQKWkcsyaDu0rZQzbDC3v0sCQ2p7TG_w1Rq1-4B3xAlSmy30izlLgmOhVU72OcRvny5MXep7x5LCfo0LC-ZCGE6zTikHlCosHAOymsaNnjvdt_Lh0ZPx9pjXZ_-2OCmSWvnVkfhqQsFhSsnpvHSEsECNOn3qu7R2pngSYCjXp7MSEBAdxZCatL6c3nOl6qQ3WmuMCOkSKjkQLWedgAww9XJrU6RUCG0ADpE7ZAp5_2DkYM7CRhrJwKQgc30FoqtP4pkzX4FHzFI0adP327Lnn3VkWtPgGkcVIm5lfzxJE1zjxPxKd44m8faB_MQrnZr_d9-GPepO6ZiwetPfMrjpd38PXUcuoG-DDxjlY1cj3E6l5qJ8lmFMoAdcVit60GE6mBPiu_dRa98wC95ZDUqpe_RKpKSbmbI4jT4SoV5klBk-MzVbJVz5UwdS6yODxT9ZEhtAArpfwsTovsyuhQqHGZxEkQ-F_mc6Eb_grGaRzRxciI7JC6nJ5Fa6I53dT4FXk2eiNQN-V9SlaGDZzMA8M8t2PqbqkuoKy_WNyZ0oiE0Q1dGmwNIfZE6Lo8ReclEuTrdgwrPpI7wJfrB6CWlgz7xp59QkMMZV2Yb5wtUAVAURkb8YsAIb3drCZYzfJrAexN7Gcl0X6NFlavono47InTJKY06P0rnKT0yGC41iBpBXkmbEcX6ucYMN4GyzaIL2WHM_uUCLOAnfg1gTa5XWZ05rBB_CAqYaTpVhPNR4V9UDb9LMsYdsLFw4vJpY_t368zqlfs_cw7ERB7OxygmftmJUIAJJ8WwyTQMnQ3h1WkvjvtEQfVvLEfjZ0m6B5wa-pVQX58UqiR_781Dez-XzMz2XQTBSAgPZkYxUx-XaiWO300xFcWzitahOO-4wZtOUcPuNe8fTXUynz622AyWserKnABVFM7IJptkCAdAXKWgFbz0tI2T9tM103hSun-2kEEIQZkC1QVeu5lgaTRGLSw0woHdZl0prJvpZ8twdqR3dBqb_THWbUZdqO54XB3ivrQNEx3_8JAoPsXV_ZgSNcp52PiEt9ncUySNVa91S_sdXpnKcJypWC9wNwLVOmCqxglIjM0r1xFiQ09DO-Mr2Suo50leFJlI3YsMnJ0aPdO_eGpFBFRGCyv1GVwvYT7xQqMQ-uJ0kEN1Bdd-pw7LgN-npsUwYbdrXToOGMKEAjsp6Asxe44j5KeOHWb675tTMuw51va5ssCqMdoIyCLgHa4kK7XSSBJ5njkQ'
    #% invariantes
    today=datetime.date.today()
    
    # enlaces
    URLParam='https://snia.mop.gob.cl/dgasat/pages/dgasat_param/dgasat_param_1.jsp'
    URL='https://snia.mop.gob.cl/dgasat/pages/dgasat_param/dgasat_param_tablas.jsp'
    URL2='https://snia.mop.gob.cl/dgasat/pages/dgasat_param/dgasat_param_tablas_sinoptico.jsp'
    
    # payloads
    session=requests.session()
    
    # crear diccionario con las fechas de inicio
    path_metadata=os.path.join('.','inputs','datesRuts.csv')
    if checkFile(path_metadata):
        df=pd.read_csv(path_metadata,index_col=0)
    else:
        sys.exit('Se necesita archivo de fechas para descargar')
    
    # ruts
    path_ruts=os.path.join('.','inputs','rut_estaciones.csv')
    if checkFile(path_ruts):
        ruts=pd.read_csv(path_ruts)
    else:
        sys.exit('Se necesita archivo de estaciones para descargar')
    
    # leer fecha inicial
    path_last_yr=os.path.join('.','outputs','lastYearMOP.csv')
    if checkFile(path_last_yr):
        lastYear=int(pd.read_csv(path_last_yr).columns[0])
    else:
        lastYear=1972
    date_user=pd.to_datetime('01-01-'+str(lastYear),
                                 format='%d-%m-%Y')    
    # df para guardar los datos q medio, minimo y maximo 
    df_qmean=pd.DataFrame(index=pd.date_range('01-01-'+str(lastYear),today,
                                              freq='1d'))

    df_qmin=pd.DataFrame(index=pd.date_range('01-01-'+str(lastYear),today,
                                             freq='1d'))
    
    df_qmax=pd.DataFrame(index=pd.date_range('01-01-'+str(lastYear),today,
                                             freq='1d'))
        
    # iterar en las estaciones
    for rut in ruts['Rut']:
        
        # get first date
        if df['rut'].str.contains(rut).any():
            date_ini=max(date_rut(rut,df,lastYear),date_user)
        else:
            date_ini=date_user
        # headers
        headerParams=headersParam(cookies)

        # POST data
        data_param=paramsPOSTdata([rut],today.strftime("%d/%m/%Y"))
        
        response=requests.post(URLParam,headers=headerParams,data=data_param,
    stream=True)
        
        # chequear errores del servidor
        while any(x in response.text for x in ['Error 500',
                'Se ha producido un error en el Sistema','502 Bad Gateway',
                '403 Forbidden','permission to access this resource.']):
            print('Error en el servidor, esperando 1 minuto')
            sleep(random.randint(21,60)) #NO CAMBIAR
            response=requests.post(URLParam,headers=headerParams,
                                   data=data_param,stream=True)
            
        soup=BeautifulSoup(response.text, "html.parser")
        parametros=[element['value'].replace(' ','+') for element in soup.find_all('input')
if (any(str(x) in element['value'] for x in [rut]))]
        param_q=[x for x in parametros if 'Caudal+(m3/seg)' in x]
        
        # iterar en los años
        for yr in range(date_ini.year,int(datetime.date.today().year)+1):
                
            date_fin=min(date_ini+pd.offsets.DateOffset(years=1),pd.to_datetime(today))
                    
            # POST request
            sleep(random.randint(1,1)) #NO CAMBIAR
            # PostDATA
            data=POSTdata(g_recaptcha,pd.to_datetime(date_ini).strftime("%d/%m/%Y"),
                          date_fin.strftime("%d/%m/%Y"),param_q[0],
                          today.strftime("%d/%m/%Y"),[rut])
            
            # headers POST
            headers=get_headers(cookies=cookies)
            session.headers.update(headers)
            r=session.post(URL,headers=headers, data=data, stream = True)    
            
            # GET request
            headers2=headersGET(cookies)
            r=requests.get(URL2,headers=headers2)
            
            # parsear tablas con pandas
            df_yrs=parse_tables(r.text)
            
            if len(df_yrs.columns)>1:
                df_qmin.loc[df_yrs.index,rut]=df_yrs.iloc[:,1].values
                df_qmax.loc[df_yrs.index,rut]=df_yrs.iloc[:,2].values
                df_qmean.loc[df_yrs.index,rut]=df_yrs.iloc[:,3].values
            
            date_ini=date_fin
    
    # salidas
    folder=os.path.join('.','outputs')
    try:
        os.makedirs(folder)
    except:
        pass
    df_qmean.to_csv(os.path.join(folder,'qmean_MOP.csv'))
    df_qmax.to_csv(os.path.join(folder,'qmax_MOP.csv'))
    df_qmin.to_csv(os.path.join(folder,'qmin_MOP.csv'))
    
    parse_MOP(df,df_qmean,lastYear)
    
def parse_MOP(df_,df_qmean_,lastYear):
    # obtener estaciones totales
    stations=list(df_['rut'].unique())+list(df_qmean_.columns)
    stations_dr=list(dict.fromkeys(stations))
    
    # crear df para guardar
    df_q=pd.DataFrame(index=pd.date_range(str(lastYear)+'-01-01',
datetime.date.today(),freq='1d'),columns=stations_dr)
    
    # parsear los caudales originales de la DGA de los ultimos 50 años
    # df_q50=df_.loc[df_.index>='1972-01-01']
    # df_parsed,flags_parsed=ordenarDGA(stations_dr,df_q50)
    
    for est in df_qmean_.columns:
        qmean_est=df_qmean_[est].copy()
        
        # remover los nan
        qmean_est_nna=qmean_est[qmean_est.notna()]
        
        # guardar los valores nuevos not nan
        df_q.loc[qmean_est_nna.index,qmean_est_nna.name]=qmean_est_nna.values        
   
    # for est in df_parsed.columns:
    #     qmean_est=df_parsed[est]
        
    #     # remover los nan
    #     qmean_est_nna=qmean_est[qmean_est.notna()]
        
    #     # guardar los valores nuevos not nan
    #     df_q.loc[qmean_est_nna.index,qmean_est_nna.name]=qmean_est_nna.values   
   
    # guardar los caudales del MOP
    df_q.dropna(how='all',axis=1).dropna(how='all',axis=0).to_csv(os.path.join('.',
'outputs','qmean_MOP_'+str(datetime.date.today().year)+'.csv'))
            
# if __name__=='__main__':
#     main()