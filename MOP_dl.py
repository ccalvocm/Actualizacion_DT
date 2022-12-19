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
import json
import datetime
import os
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
				: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
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
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0',
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
				: "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0"
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

def ordenarDGA(ests,df_DGA):
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
    output = pd.DataFrame([], index = pd.date_range(start='1972-01-01', end='2020-12-31', closed=None))
    df_DGA.index = pd.to_datetime(df_DGA.index)
    output_flag=pd.DataFrame([],index=pd.date_range(start='1972-01-01', 
end='2020-12-31',closed=None))

    for ind,est in enumerate(ests):
        q_est=df_DGA[df_DGA['rut'] == ests[ind]]
        fechas=q_est.index
        caudal=q_est['Q (m3/s)']
        flags=q_est['flag']
        
        q_est_df=pd.DataFrame(caudal.values,index=fechas,columns=[est])
        flags_est=pd.DataFrame(flags.values,index=fechas,columns=['flags'])
            
        output.loc[q_est_df.index,est]=q_est_df[est].values
        output_flag.loc[flags.index,est]=flags.values

    return output,output_flag  

def date_rut(rut,df_):
    date_first=df_[df_['rut']==rut].index
    if len(date_first)>1:
        idx=date_first[-1]
        return idx
    else:
        return pd.to_datetime('1972-01-01')

#%%
def main():
    
    #%% requests
    
    # inputs usuario
    
    # cookies
    cookies="_ga_RJK2LP1D4K=GS1.1.1661345680.23.0.1661345683.0.0.0; _ga=GA1.1.15729720.1657635782; cookiesession1=074E6377BIPZXLUMRRJSUX3FNZPPF043; JSESSIONID=00007iRayYYSaIvqb5_9c1-sW3N:-1"
    cookiesGET=';'.join(cookies.split(';')[-2:]).strip()
    
    # recaptcha key
    g_recaptcha='03ANYolqsaLGYCv69k4KOmooRswqClC1SBshVRRh95fmDc2fF_C_b1Av78seLT9hP4J-Mk5o6ltQV9H8lm7ZPAULwrIb-__a5tAOpqex_2dhp7RBTOjHBGfl5pRgTuvCHLPL8cJ_YsVxpTfJOAYvULkZTqkvzslN-Bsr_KPVYbnw7UXUMzb1HhZ0e2jE3AT9ql8xJc0sDgmE7LH4Ob8zhc8Qpi7EgzvxBvTETlA5tWjHgFTzAwfrdNg_QK1YAzqtR76pn5rOLRmzr8n3MyKxdDzZirK8eCABJB9JGE3WfvmpUiaIqUacTx6xZrJjDn-t08oDmn_uKB-CrcpHs9Y0u6ds16YrjohXBoJJMJtRerRVNEczrjVMPuN2j2-xvSHoT0TGXvaVkLSbbms8w6vErZTtG9NnTXdREsr8WRPl3O-7EohckUGDKIyrNMbmxJMz4TV2MPxCDfW5paWy9fUI86o9mUfTuPJngEOWupka2_NVuQjxD8qAtLXJaEXkAks9yr7vC0NVFaVdVnNS_HxqUnBx5PLw4MTV3DDA'
                
    #%% invariantes
    today=datetime.date.today().strftime("%d/%m/%Y")
    
    # enlaces
    URLParam='https://snia.mop.gob.cl/dgasat/pages/dgasat_param/dgasat_param_1.jsp'
    URL='https://snia.mop.gob.cl/dgasat/pages/dgasat_param/dgasat_param_tablas.jsp'
    URL2='https://snia.mop.gob.cl/dgasat/pages/dgasat_param/dgasat_param_tablas_sinoptico.jsp'
    
    # payloads
    session=requests.session()
    
    # crear diccionario con las fechas de inicio
    path_metadata=os.path.join('.','inputs','BNAT_CaudalDiario.txt')
    df=pd.read_csv(path_metadata,sep =';',index_col=2,parse_dates=True,dayfirst=True,
names=['rut','nombre','Q (m3/s)','flag'])
    
    # ruts
    ruts=pd.read_csv(os.path.join('.','outputs','rut_estaciones.csv'),
                     names=['Rut'])
    
    # df para guardar los datos q medio, minimo y maximo 
    df_qmean=pd.DataFrame(index=pd.date_range('01-01-1972',
datetime.date.today().strftime("%d-%m-%Y"),freq='1d'))

    df_qmin=pd.DataFrame(index=pd.date_range('01-01-1972',
datetime.date.today().strftime("%d-%m-%Y"),freq='1d'))
    
    df_qmax=pd.DataFrame(index=pd.date_range('01-01-1972',
datetime.date.today().strftime("%d-%m-%Y"),freq='1d'))

    # dia inicial si no existen datos de la estacion
    date_first=pd.to_datetime('1972-01-01')
        
    # iterar en las estaciones
    for rut in ruts['Rut']:
        
        # get first date
        if df['rut'].str.contains(rut).any():
            date_ini=max(date_rut(rut,df),date_first)
        
        # headers
        headerParams=headersParam(cookiesGET)

        # POST data
        data_param=paramsPOSTdata([rut],today)
        
        response=requests.post(URLParam,headers=headerParams,data=data_param,
    stream=True)
        
        if 'Error 500' in response.text:
            print('Error 500')
            break
            
        soup = BeautifulSoup(response.text, "html.parser")
        parametros=[element['value'].replace(' ','+') for element in soup.find_all('input')
if (any(str(x) in element['value'] for x in [rut]))]
        param_q=[x for x in parametros if 'Caudal+(m3/seg)' in x]
        
        # iterar en los años
        for yr in range(2020,2023):
                
            date_fin=min(pd.to_datetime(date_ini,format="%d/%m/%Y")+pd.offsets.DateOffset(years=1),
pd.to_datetime(today)).strftime("%d/%m/%Y")
                    
            # POST request
            # sleep(random.randint(60,120)) #NO CAMBIAR
            # PostDATA
            data=POSTdata(g_recaptcha,pd.to_datetime(date_ini).strftime("%d/%m/%Y"),date_fin,
param_q,today,[rut])
            
            # headers POST
            headers=get_headers(cookies=cookies)
            session.headers.update(headers)
            r=session.post(URL,headers=headers, data=data, stream = True)
            
            # GET request
            headers2=headersGET(cookiesGET)
            r=requests.get(URL2,headers=headers2)
            texto = r.text
            
            # parsear tablas con pandas
            df_yrs=parse_tables(r.text)
            
            if len(df_yrs.columns)>1:
                df_qmin.loc[df_yrs.index,rut]=df_yrs.iloc[:,1].values
                df_qmax.loc[df_yrs.index,rut]=df_yrs.iloc[:,2].values
                df_qmean.loc[df_yrs.index,rut]=df_yrs.iloc[:,3].values
            
            date_ini=date_fin
            
    df_qmean.to_csv(os.path.join('.','outputs','qmean_MOP.csv'))
    df_qmax.to_csv(os.path.join('.','outputs','qmax_MOP.csv'))
    df_qmin.to_csv(os.path.join('.','outputs','qmin_MOP.csv'))
    
    parse_MOP(df,df_qmean)
    
def parse_MOP(df_,df_qmean_):
    # obtener estaciones totales
    stations=list(df_['rut'].unique())+list(df_qmean_.columns)
    stations_dr=list(dict.fromkeys(stations))
    
    # crear df para guardar
    df_q=pd.DataFrame(index=pd.date_range('01-01-1972',
datetime.date.today().strftime("%d-%m-%Y"),freq='1d'),columns=stations_dr)
    
    # parsear los caudales originales de la DGA de los ultimos 50 años
    df_q50=df_.loc[df_.index>='1972-01-01']
    df_parsed,flags_parsed=ordenarDGA(stations_dr,df_q50)
    
    for est in df_qmean_.columns:
        qmean_est=df_qmean_[est].copy()
        
        # remover los nan
        qmean_est_nna=qmean_est[qmean_est.notna()]
        
        # guardar los valores nuevos not nan
        df_q.loc[qmean_est_nna.index,qmean_est_nna.name]=qmean_est_nna.values        
   
    for est in df_parsed.columns:
        qmean_est=df_parsed[est]
        
        # remover los nan
        qmean_est_nna=qmean_est[qmean_est.notna()]
        
        # guardar los valores nuevos not nan
        df_q.loc[qmean_est_nna.index,qmean_est_nna.name]=qmean_est_nna.values   
   
    # guardar los caudales del MOP
    df_q.to_csv(os.path.join('.','outputs','qmean_MOP_1972_2022.csv'))
    
def divide_chunks(l, n):
     
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
x = list(divide_chunks(list(q_mop.columns), 20))

fig,ax=plt.subplots(8,8)
axes=ax.reshape(-1)

for ind,ests in enumerate(x):
    q_mop[ests].plot(ax=axes[ind],legend=False)

if __name__=='__main__':
    main()