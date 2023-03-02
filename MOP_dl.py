# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 10:25:23 2020
@author: ccalvo
"""

import requests #librería para hacer consultas https
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os
import sys
from time import sleep
import random
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

def date_rut(rut,df_,lastYear):
    date_first=df_[df_['rut']==rut].index
    if len(date_first)>=1:
        idx=date_first[-1]
        return  pd.to_datetime(idx,format='%Y-%m-%d')
    else:
        return pd.to_datetime('01-01-'+str(lastYear),format='%d-%m-%Y')
    
def checkFile(path):
    return os.path.isfile(path)

def getStations(sp):
    stations=[element.get_text() for element in sp.find_all('option')]
    listStations=sorted(list(set([x.split(' ')[0] for x in stations])))
    listStations=[x for x in listStations if len(x)>2]
    return listStations

def openFile(path):
    try:
        df=pd.read_csv(path,index_col=0)
        return df
    except:
        sys.exit('Se necesita archivo para descargar')    
        return None
#%%
def main(cookies,g_recaptcha):
    
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
    df=openFile(path_metadata)

    # ruts blacklist
    path_ruts=os.path.join('.','inputs','rut_estaciones.csv')
    rutsBlacklist=openFile(path_ruts)
    
    # leer fecha inicial
    path_last_yr=os.path.join('.','outputs','lastYearMOP.csv')
    try:
        lastYear=int(pd.read_csv(path_last_yr).columns[0])
    except:
        lastYear=1972
    date_user=pd.to_datetime('01-01-'+str(lastYear),
                                 format='%d-%m-%Y')    
     
    # get ruts
    firstRut='01000005-K'
    # get first date
    try:
        date_ini=max(date_rut(firstRut,df,lastYear),date_user)
    except:
        date_ini=date_user
    # headers
    headerParams=headersParam(cookies)

    # POST data
    data_param=paramsPOSTdata([firstRut],today.strftime("%d/%m/%Y"))
    
    response=requests.post(URLParam,headers=headerParams,data=data_param,
stream=True)
    
    # obtener los ruts nuevos y filtrar los que no tienen caudal
    ruts=getStations(BeautifulSoup(response.text))[1:]
    ruts=[x for x in ruts if x not in list(rutsBlacklist['rut'])]
    
    # df para guardar los datos q medio, minimo y maximo 
    df_qmean=pd.DataFrame(index=pd.date_range('01-01-'+str(lastYear),today,
                                              freq='1d'),columns=ruts)

    df_qmin=df_qmean.copy()
    
    df_qmax=df_qmin.copy()
    
    # iterar en las estaciones
    for rut in ruts:
        print(rut)
        
        # get first date
        try:
            date_ini=max(date_rut(rut,df,lastYear),date_user)
        except:
            date_ini=date_user
        # headers
        headerParams=headersParam(cookies)

        # POST data
        data_param=paramsPOSTdata([rut],today.strftime("%d/%m/%Y"))
        
        response=requests.post(URLParam,headers=headerParams,data=data_param,
    stream=True)
        
        # chequear errores del servidor
        while any(x in response.text for x in ['Error 500',
                'Se ha producido un error en el Sistema','502 Bad Gateway']):
            sleep(random.randint(1,3)) #NO CAMBIAR
            response=requests.post(URLParam,headers=headerParams,
                                   data=data_param,stream=True)
                                
        soup=BeautifulSoup(response.text, "html.parser")
        
        parametros=[element['value'].replace(' ','+') for element in soup.find_all('input')
if (any(str(x) in element['value'] for x in [rut]))]
        param_q=[x for x in parametros if 'Caudal+(m3/seg)' in x]
        
        if len(param_q)>0:
            # iterar en los años
            for yr in range(date_ini.year,int(datetime.date.today().year)+1):
                    
                date_fin=min(date_ini+pd.offsets.DateOffset(years=1),
                             pd.to_datetime(today))
                        
                # POST request
                data=POSTdata(g_recaptcha,pd.to_datetime(date_ini).strftime("%d/%m/%Y"),
                              date_fin.strftime("%d/%m/%Y"),param_q,today,[rut])
                
                # headers POST
                headers=get_headers(cookies=cookies)
                session.headers.update(headers)
                
                r=session.post(URL,headers=headers, data=data, stream = True)
                while any(x in response.text for x in ['Error 500',
                        'Se ha producido un error en el Sistema','502 Bad Gateway']):
                    sleep(random.randint(1,3)) #NO CAMBIAR
                    r=session.post(URL,headers=headers, data=data, stream = True)
                
                # GET request
                headers2=headersGET(cookies)
                
                r=requests.get(URL2,headers=headers2)
                
                while any(x in response.text for x in ['Error 500',
                        'Se ha producido un error en el Sistema','502 Bad Gateway']):
                    sleep(random.randint(1,3)) #NO CAMBIAR
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
    
    df_qmean=dropnans(df_qmean)
    df_qmax=dropnans(df_qmax)
    df_qmin=dropnans(df_qmin)
    
    df_qmean.to_csv(os.path.join(folder,'qmean_MOP.csv'))
    df_qmax.to_csv(os.path.join(folder,'qmax_MOP.csv'))
    df_qmin.to_csv(os.path.join(folder,'qmin_MOP.csv'))
    
    parse_MOP(df,df_qmean,lastYear)

def dropnans(df):
    return df.dropna(how='all',axis=1)    

def parse_MOP(df_,df_qmean_,lastYear):
    # obtener estaciones totales
    stations=list(df_['rut'].unique())+list(df_qmean_.columns)
    stations_dr=list(dict.fromkeys(stations))
    
    # crear df para guardar
    df_q=pd.DataFrame(index=pd.date_range(str(lastYear)+'-01-01',
datetime.date.today(),freq='1d'),columns=stations_dr)
        
    for est in df_qmean_.columns:
        qmean_est=df_qmean_[est].copy()
        
        # remover los nan
        qmean_est_nna=qmean_est[qmean_est.notna()]
        
        # guardar los valores nuevos not nan
        df_q.loc[qmean_est_nna.index,qmean_est_nna.name]=qmean_est_nna.values        
   
    # guardar los caudales del MOP
    df_q.dropna(how='all',axis=1).dropna(how='all',axis=0).to_csv(os.path.join('.',
'outputs','qmean_MOP_'+str(datetime.date.today().year)+'.csv'))
            
# if __name__=='__main__':
#     main()